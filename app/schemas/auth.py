# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class Token(BaseModel):
    access_token: str
    token_type: str
    requires_2fa: bool = False
    temp_token: Optional[str] = None


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Verify2FARequest(BaseModel):
    temp_token: str
    code: str


class EnableTOTPRequest(BaseModel):
    password: str


class EnableTOTPResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]


class VerifyTOTPRequest(BaseModel):
    code: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)