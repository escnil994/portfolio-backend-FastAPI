from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    technologies = Column(String(500), nullable=True)
    
    demo_url = Column(String(500), nullable=True)
    repo_url = Column(String(500), nullable=True)
    
    featured = Column(Boolean, default=False, index=True)
    published = Column(Boolean, default=True, index=True)
    views = Column(Integer, default=0)
    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    author = relationship("User", back_populates="projects")
    comments = relationship("Comment", back_populates="project", cascade="all, delete-orphan")
    videos = relationship("Video", foreign_keys="Video.project_id", primaryjoin="Video.project_id==Project.id", cascade="all, delete-orphan")