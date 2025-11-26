from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from app.schemas.user import UserResponse
from app.schemas.profile import ProfileResponse

class LoginRequest(BaseModel):
    identifier: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_2fa: bool = False
    temp_token: Optional[str] = None
    user: Optional['UserWithProfile'] = None

class TokenData(BaseModel):
    user_id: Optional[int] = None
    type: Optional[str] = None

class Verify2FARequest(BaseModel):
    temp_token: str
    code: str

class EnableTOTPRequest(BaseModel):
    password: str

class EnableTOTPResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]

class VerifyTOTPRequest(BaseModel):
    code: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserWithProfile(UserResponse):
    profile: Optional[ProfileResponse] = None
    
    model_config = ConfigDict(from_attributes=True)