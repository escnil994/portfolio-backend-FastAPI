from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    content: str = Field(..., min_length=5, max_length=1000)

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    approved: bool
    created_at: datetime
    project_id: Optional[int] = None
    blog_post_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)