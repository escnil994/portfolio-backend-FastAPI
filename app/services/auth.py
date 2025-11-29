from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update
from sqlalchemy.orm import selectinload
import pyotp
import qrcode
import io
import base64
import secrets
import string
import hashlib

from app.config import settings
from app.models.user import User, TwoFactorCode, LoginAttempt
from app.models.session import UserSession 
from app.core.security_fields import encrypt_data, decrypt_data 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_temp_token(self, user_id: int) -> str:
        expires_delta = timedelta(minutes=10)
        to_encode = {"user_id": user_id, "type": "temp_2fa", "exp": datetime.utcnow() + expires_delta}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except PyJWTError:
            return None

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).options(selectinload(User.profile)).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).options(selectinload(User.profile)).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).options(selectinload(User.profile)).where(User.username == username))
        return result.scalar_one_or_none()
        
    async def get_user_by_identifier(self, db: AsyncSession, identifier: str) -> Optional[User]:
        result = await db.execute(
            select(User).options(selectinload(User.profile))
            .where(or_(User.email == identifier, User.username == identifier))
        )
        return result.scalar_one_or_none()

    async def authenticate_user(self, db: AsyncSession, identifier: str, password: str) -> Optional[User]:
        user = await self.get_user_by_identifier(db, identifier)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, db: AsyncSession, email: str, username: str, password: str, full_name: Optional[str] = None, is_superuser: bool = False) -> User:
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email, username=username, hashed_password=hashed_password,
            full_name=full_name, is_superuser=is_superuser, email_2fa_enabled=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def create_secure_session(
        self, db: AsyncSession, user_id: int, user_email: str, ip_address: str, user_agent: str
    ) -> Tuple[str, str]:
        """Crea access token y refresh token, y registra la sesión en DB"""
        access_token = self.create_access_token({"user_id": user_id, "email": user_email})
        refresh_token = self.create_refresh_token({"user_id": user_id, "email": user_email})
        
        rt_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        new_session = UserSession(
            user_id=user_id,
            refresh_token_hash=rt_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=7),
            is_active=True
        )
        db.add(new_session)
        await db.commit()
        
        return access_token, refresh_token

    async def rotate_refresh_token(
        self, db: AsyncSession, incoming_refresh_token: str, ip_address: str, user_agent: str
    ) -> Tuple[str, str, User]:
        """Rota el token, detecta robos y retorna nuevos tokens"""
        
        payload = self.verify_token(incoming_refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise Exception("Token inválido")

        user_id = payload.get("user_id")
        
        rt_hash = hashlib.sha256(incoming_refresh_token.encode()).hexdigest()
        result = await db.execute(select(UserSession).where(UserSession.refresh_token_hash == rt_hash))
        session = result.scalar_one_or_none()

        if session and not session.is_active:
            await self.revoke_all_user_sessions(db, user_id)
            raise Exception("Security Alert: Token reuse detected")

        if not session:
            raise Exception("Session not found")
            
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            await db.commit()
            raise Exception("Session expired")

        if session.user_agent != user_agent:
            pass 

        session.is_active = False
        session.revoked_at = datetime.utcnow()
        
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise Exception("User not found")
            
        new_access, new_refresh = await self.create_secure_session(
            db, user.id, user.email, ip_address, user_agent
        )
        
        return new_access, new_refresh, user

    async def revoke_all_user_sessions(self, db: AsyncSession, user_id: int):
        """Botón de pánico: Cierra todas las sesiones"""
        await db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(is_active=False, revoked_at=datetime.utcnow())
        )
        await db.commit()

    def generate_2fa_code(self) -> str:
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    async def create_2fa_code(self, db: AsyncSession, user_id: int) -> str:
        code = self.generate_2fa_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        two_fa_code = TwoFactorCode(user_id=user_id, code=code, expires_at=expires_at)
        db.add(two_fa_code)
        await db.commit()
        return code
    
    async def verify_2fa_code(self, db: AsyncSession, user_id: int, code: str) -> bool:
        result = await db.execute(
            select(TwoFactorCode).where(
                and_(TwoFactorCode.user_id == user_id, TwoFactorCode.code == code, 
                     TwoFactorCode.used == False, TwoFactorCode.expires_at > datetime.utcnow())
            )
        )
        two_fa_code = result.scalar_one_or_none()
        if not two_fa_code: return False
        two_fa_code.used = True
        await db.commit()
        return True
    
    def generate_totp_secret(self) -> str:
        return pyotp.random_base32()
    
    def generate_totp_uri(self, secret: str, email: str) -> str:
        return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=settings.APP_NAME)
    
    def generate_qr_code(self, uri: str) -> str:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buffer.read()).decode()}"
    
    def verify_totp(self, encrypted_secret: str, code: str) -> bool:
        secret = decrypt_data(encrypted_secret)
        if not secret: return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(f"{code[:4]}-{code[4:]}")
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> str:
        hashed_codes = [self.get_password_hash(code) for code in codes]
        return '|'.join(hashed_codes)
    
    def verify_backup_code(self, hashed_codes: str, code: str) -> Tuple[bool, Optional[str]]:
        if not hashed_codes: return False, None
        codes = hashed_codes.split('|')
        for i, hashed_code in enumerate(codes):
            if self.verify_password(code, hashed_code):
                codes.pop(i) 
                return True, '|'.join(codes)
        return False, None

    async def log_login_attempt(self, db: AsyncSession, identifier: str, success: bool, ip_address: Optional[str] = None):
        attempt = LoginAttempt(email=identifier, success=success, ip_address=ip_address)
        db.add(attempt)
        await db.commit()
    
    async def check_login_attempts(self, db: AsyncSession, identifier: str, minutes: int = 15, max_attempts: int = 5) -> bool:
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        result = await db.execute(
            select(LoginAttempt).where(and_(LoginAttempt.email == identifier, LoginAttempt.success == False, LoginAttempt.created_at > time_threshold))
        )
        return len(result.scalars().all()) >= max_attempts
    
    async def update_last_login(self, db: AsyncSession, user_id: int):
        user = await self.get_user_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            await db.commit()

auth_service = AuthService()