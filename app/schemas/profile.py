# app/schemas/profile.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.media import ImageResponse


class ProfileBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    bio: Optional[str] = None
    email: EmailStr
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    skills: Optional[str] = None
    resume_url: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    skills: Optional[str] = None
    resume_url: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)