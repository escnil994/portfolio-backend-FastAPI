# app/services/auth.py

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import pyotp
import qrcode
import io
import base64
import secrets
import string

from app.config import settings
from app.models.user import User, TwoFactorCode, LoginAttempt


class AuthService:
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def get_password_hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_temp_token(self, user_id: int) -> str:
        expires_delta = timedelta(minutes=10)
        to_encode = {
            "user_id": user_id,
            "type": "temp_2fa",
            "exp": datetime.utcnow() + expires_delta
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def create_user(
        self, 
        db: AsyncSession, 
        email: str, 
        username: str, 
        password: str,
        full_name: Optional[str] = None, 
        is_superuser: bool = False
    ) -> User:
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
            email_2fa_enabled=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    def generate_2fa_code(self) -> str:
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    async def create_2fa_code(self, db: AsyncSession, user_id: int) -> str:
        code = self.generate_2fa_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        two_fa_code = TwoFactorCode(
            user_id=user_id,
            code=code,
            expires_at=expires_at
        )
        db.add(two_fa_code)
        await db.commit()
        return code
    
    async def verify_2fa_code(self, db: AsyncSession, user_id: int, code: str) -> bool:
        result = await db.execute(
            select(TwoFactorCode).where(
                and_(
                    TwoFactorCode.user_id == user_id,
                    TwoFactorCode.code == code,
                    TwoFactorCode.used == False,
                    TwoFactorCode.expires_at > datetime.utcnow()
                )
            )
        )
        two_fa_code = result.scalar_one_or_none()
        
        if not two_fa_code:
            return False
        
        two_fa_code.used = True
        await db.commit()
        return True
    
    def generate_totp_secret(self) -> str:
        return pyotp.random_base32()
    
    def generate_totp_uri(self, secret: str, email: str) -> str:
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=settings.APP_NAME
        )
    
    def generate_qr_code(self, uri: str) -> str:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp(self, secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes
    
    def hash_backup_codes(self, codes: List[str]) -> str:
        hashed_codes = [self.get_password_hash(code) for code in codes]
        return '|'.join(hashed_codes)
    
    def verify_backup_code(self, hashed_codes: str, code: str) -> bool:
        if not hashed_codes:
            return False
        
        codes = hashed_codes.split('|')
        for hashed_code in codes:
            if self.verify_password(code, hashed_code):
                return True
        return False
    
    async def log_login_attempt(
        self, 
        db: AsyncSession, 
        email: str, 
        success: bool,
        ip_address: Optional[str] = None
    ):
        attempt = LoginAttempt(
            email=email,
            success=success,
            ip_address=ip_address
        )
        db.add(attempt)
        await db.commit()
    
    async def check_login_attempts(
        self, 
        db: AsyncSession, 
        email: str, 
        minutes: int = 15,
        max_attempts: int = 5
    ) -> bool:
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        result = await db.execute(
            select(LoginAttempt).where(
                and_(
                    LoginAttempt.email == email,
                    LoginAttempt.success == False,
                    LoginAttempt.created_at > time_threshold
                )
            )
        )
        attempts = result.scalars().all()
        return len(attempts) >= max_attempts
    
    async def update_last_login(self, db: AsyncSession, user_id: int):
        user = await self.get_user_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            await db.commit()


auth_service = AuthService()