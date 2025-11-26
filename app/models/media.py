
from sqlalchemy import Column, Integer, String, Float, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.base import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    blob_name = Column(String(255), nullable=True)
    image_order = Column(Integer, default=1)
    alt_text = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    blog_post_id = Column(Integer, nullable=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    source = Column(String(50), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())