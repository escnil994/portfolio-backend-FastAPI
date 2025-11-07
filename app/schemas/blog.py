from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.media import ImageResponse, VideoResponse
from app.schemas.project import CommentResponse


class BlogPostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: str
    author: str = Field(..., min_length=1, max_length=255)
    tags: Optional[str] = None
    published: bool = True


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    tags: Optional[str] = None
    published: Optional[bool] = None


class BlogPostResponse(BlogPostBase):
    id: int
    views: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class BlogPostWithDetails(BlogPostResponse):
    comments: List[CommentResponse] = []
    videos: List[VideoResponse] = []