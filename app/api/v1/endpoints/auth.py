from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.schemas.auth import (
    Token,
    LoginRequest,
    Verify2FARequest,
    RefreshTokenRequest,
    EnableTOTPRequest,
    EnableTOTPResponse,
    VerifyTOTPRequest,
    PasswordChangeRequest,
    UserWithProfile
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import auth_service
from app.services.email import email_service
from app.api.deps import get_current_user, get_current_admin, get_client_ip_from_request
from app.models.user import User
from app.core.security_fields import encrypt_data

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    existing_user = await auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await auth_service.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    user = await auth_service.create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        is_superuser=False
    )
    
    return user

def format_user_response(user: User) -> UserWithProfile:
    return UserWithProfile.model_validate(user)

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    ip_address = get_client_ip_from_request(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    is_blocked = await auth_service.check_login_attempts(db, login_data.identifier)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )
    
    user = await auth_service.authenticate_user(db, login_data.identifier, login_data.password)
    
    if not user:
        await auth_service.log_login_attempt(db, login_data.identifier, False, ip_address)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    if user.email_2fa_enabled or user.totp_enabled:
        temp_token = auth_service.create_temp_token(user.id)
        
        if user.email_2fa_enabled:
            code = await auth_service.create_2fa_code(db, user.id)
            background_tasks.add_task(
                email_service.send_2fa_code,
                email=user.email,
                code=code,
                name=user.full_name or user.username
            )
        
        await auth_service.log_login_attempt(db, login_data.identifier, True, ip_address)
        
        return Token(
            access_token="",
            refresh_token="",
            token_type="bearer",
            requires_2fa=True,
            temp_token=temp_token
        )
    
    access_token, refresh_token = await auth_service.create_secure_session(
        db, user.id, user.email, ip_address, user_agent
    )
    
    await auth_service.update_last_login(db, user.id)
    await auth_service.log_login_attempt(db, login_data.identifier, True, ip_address)
    await db.refresh(user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=format_user_response(user)
    )

@router.post("/verify-2fa", response_model=Token)
async def verify_2fa(
    request: Request,
    verify_data: Verify2FARequest,
    db: AsyncSession = Depends(get_db)
):
    payload = auth_service.verify_token(verify_data.temp_token)
    if not payload or payload.get("type") != "temp_2fa":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id")
    user = await auth_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    is_valid = False
    
    if user.email_2fa_enabled:
        is_valid = await auth_service.verify_2fa_code(db, user_id, verify_data.code)
    
    if not is_valid and user.totp_enabled and user.totp_secret:
        is_valid = auth_service.verify_totp(user.totp_secret, verify_data.code)
    
    if not is_valid and user.backup_codes:
        is_valid, new_backup_codes = auth_service.verify_backup_code(user.backup_codes, verify_data.code)
        if is_valid:
            user.backup_codes = new_backup_codes
            await db.commit()
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    ip_address = get_client_ip_from_request(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    access_token, refresh_token = await auth_service.create_secure_session(
        db, user.id, user.email, ip_address, user_agent
    )
    
    await auth_service.update_last_login(db, user.id)
    await db.refresh(user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=format_user_response(user)
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    token_req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        ip_address = get_client_ip_from_request(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        new_access, new_refresh, user = await auth_service.rotate_refresh_token(
            db, token_req.refresh_token, ip_address, user_agent
        )
        
        return Token(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            user=format_user_response(user)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

@router.get("/me", response_model=UserWithProfile)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await db.refresh(current_user)
    return format_user_response(current_user)

@router.post("/enable-totp", response_model=EnableTOTPResponse)
async def enable_totp(
    request: EnableTOTPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not auth_service.verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    secret = auth_service.generate_totp_secret()
    encrypted_secret = encrypt_data(secret)
    
    uri = auth_service.generate_totp_uri(secret, current_user.email)
    qr_code = auth_service.generate_qr_code(uri)
    
    backup_codes = auth_service.generate_backup_codes()
    hashed_backup_codes = auth_service.hash_backup_codes(backup_codes)
    
    current_user.totp_secret = encrypted_secret
    current_user.backup_codes = hashed_backup_codes
    await db.commit()
    
    return EnableTOTPResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )

@router.post("/verify-totp")
async def verify_totp_setup(
    request: VerifyTOTPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP not initialized"
        )
    
    is_valid = auth_service.verify_totp(current_user.totp_secret, request.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code"
        )
    
    current_user.totp_enabled = True
    await db.commit()
    
    return {"message": "TOTP enabled successfully"}

@router.post("/disable-totp")
async def disable_totp(
    request: EnableTOTPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not auth_service.verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    current_user.totp_enabled = False
    current_user.totp_secret = None
    current_user.backup_codes = None
    await db.commit()
    
    return {"message": "TOTP disabled successfully"}

@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not auth_service.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = auth_service.get_password_hash(request.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}