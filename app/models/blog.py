from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)
    
    published = Column(Boolean, default=True, index=True)
    views = Column(Integer, default=0)
    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    author = relationship("User", back_populates="blog_posts")
    comments = relationship("Comment", back_populates="blog_post", cascade="all, delete-orphan")
    videos = relationship("Video", foreign_keys="Video.blog_post_id", primaryjoin="Video.blog_post_id==BlogPost.id", cascade="all, delete-orphan")