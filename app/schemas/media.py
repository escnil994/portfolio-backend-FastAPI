from pydantic import BaseModel, ConfigDict
from typing import Optional

class MediaBase(BaseModel):
    image_order: Optional[int] = 1
    alt_text: Optional[str] = None

class ImageResponse(MediaBase):
    id: int
    entity_id: int
    entity_type: str
    image_url: str
    blob_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ImageUploadResponse(BaseModel):
    message: str
    image: ImageResponse

class ImageUpdate(MediaBase):
    pass

class VideoBase(BaseModel):
    title: str
    url: str
    source: str
    thumbnail_url: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoResponse(VideoBase):
    id: int
    project_id: Optional[int] = None
    blog_post_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)