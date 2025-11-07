# app/schemas/contact.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ContactMessageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    subject: Optional[str] = Field(None, max_length=255)
    message: str = Field(..., min_length=1)


class ContactMessageCreate(ContactMessageBase):
    pass


class ContactMessageResponse(ContactMessageBase):
    id: int
    read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None