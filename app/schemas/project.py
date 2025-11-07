# app/schemas/project.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.media import ImageResponse, VideoResponse


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    content: Optional[str] = None
    technologies: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    featured: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    technologies: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    featured: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    approved: bool
    created_at: datetime
    project_id: Optional[int] = None
    blog_post_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProjectWithDetails(ProjectResponse):
    comments: List[CommentResponse] = []
    videos: List[VideoResponse] = []