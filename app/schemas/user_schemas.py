from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List

# Schema for user registration input
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

# Schema for displaying user information (without password)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    verified: bool
    
    model_config = ConfigDict(from_attributes=True)

# Schema for username suggestion request
class SuggestUsernameRequest(BaseModel):
    email: EmailStr

# Schema for username suggestion response
class SuggestUsernameResponse(BaseModel):
    suggestions: List[str]