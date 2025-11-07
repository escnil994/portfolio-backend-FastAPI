from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class SubscriberBase(BaseModel):
    email: EmailStr


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberResponse(SubscriberBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubscriberVerify(BaseModel):
    token: str


class UnsubscribeRequest(BaseModel):
    email: EmailStr