from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class ContactMessageBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)

class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessageUpdate(BaseModel):
    read: bool

class ContactMessageResponse(ContactMessageBase):
    id: int
    created_at: datetime
    read: bool
    
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message: str
    detail: str

class MessageStatsResponse(BaseModel):
    total_messages: int
    unread_count: int