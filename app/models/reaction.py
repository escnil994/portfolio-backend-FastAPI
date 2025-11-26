import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class ReactionTypeEnum(str, enum.Enum):
    LIKE = "like"
    LOVE = "love"
    CONGRATULATIONS = "congratulations"

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    reaction_type = Column(Enum(ReactionTypeEnum), nullable=False)
    
    entity_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('email', 'entity_id', 'entity_type', name='uix_reaction_user_entity'),
    )