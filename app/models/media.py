from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class VideoSourceEnum(str, enum.Enum):
    YOUTUBE = "youtube"
    BLOB_STORAGE = "blob_storage"


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    blob_name = Column(String(500), nullable=True)  # Azure blob identifier for deletion
    image_order = Column(Integer, default=0, nullable=True)
    alt_text = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    content_type = Column(String(50), nullable=True)  # MIME type
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('ix_images_entity', 'entity_id', 'entity_type'),
    )


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    source = Column(SQLEnum(VideoSourceEnum), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    blog_post_id = Column(Integer, ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=True)
    
    project = relationship("Project", back_populates="videos")
    blog_post = relationship("BlogPost", back_populates="videos")