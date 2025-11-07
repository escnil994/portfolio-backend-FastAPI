from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.models.media import VideoSourceEnum


class ImageBase(BaseModel):
    image_url: str
    image_order: int = 0
    alt_text: Optional[str] = None


class ImageCreate(BaseModel):
    """Schema for creating image with file upload"""
    image_order: int = Field(default=1, ge=1)
    alt_text: Optional[str] = None


class ImageUpdate(BaseModel):
    """Schema for updating image metadata"""
    image_order: Optional[int] = Field(default=None, ge=1)
    alt_text: Optional[str] = None


class ImageResponse(BaseModel):
    """Schema for image response"""
    id: int
    entity_id: int
    entity_type: str
    image_url: str
    blob_name: Optional[str] = None
    image_order: int
    alt_text: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ImageUploadResponse(BaseModel):
    """Response after successful image upload"""
    message: str
    image: ImageResponse


class VideoBase(BaseModel):
    title: str
    url: str
    source: VideoSourceEnum
    thumbnail_url: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class VideoResponse(VideoBase):
    id: int
    created_at: datetime
    project_id: Optional[int] = None
    blog_post_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)