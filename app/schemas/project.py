from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.media import ImageResponse, VideoResponse
from app.schemas.comment import CommentResponse, CommentCreate
from app.schemas.user import UserResponse

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    description: str
    content: Optional[str] = None
    technologies: Optional[str] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    featured: bool = False
    published: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    technologies: Optional[str] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    featured: Optional[bool] = None
    published: Optional[bool] = None

class ProjectResponse(ProjectBase):
    id: int
    views: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    author: Optional[UserResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProjectWithDetails(ProjectResponse):
    comments: List[CommentResponse] = []
    videos: List[VideoResponse] = []
    
    model_config = ConfigDict(from_attributes=True)