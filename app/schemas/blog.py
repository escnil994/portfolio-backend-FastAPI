from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.media import ImageResponse, VideoResponse
from app.schemas.comment import CommentResponse, CommentCreate
from app.schemas.user import UserResponse

class BlogPostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    excerpt: Optional[str] = None
    content: str
    tags: Optional[str] = None
    published: bool = True

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    published: Optional[bool] = None

class BlogPostResponse(BlogPostBase):
    id: int
    views: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserResponse] = None
    images: List[ImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class BlogPostWithDetails(BlogPostResponse):
    comments: List[CommentResponse] = []
    videos: List[VideoResponse] = []
    
    model_config = ConfigDict(from_attributes=True)