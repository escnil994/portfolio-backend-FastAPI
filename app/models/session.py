from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from datetime import datetime

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Seguridad: Guardamos el HASH del token, no el token real.
    # Si roban la DB, estos hashes son inútiles sin el token original del usuario.
    refresh_token_hash = Column(String(255), unique=True, index=True, nullable=False)
    
    # Huella digital
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relación inversa (asegúrate que tu modelo User acepte esto o usa backref aquí)
    user = relationship("User", backref="sessions")