from sqlalchemy.orm import Session
from typing import Optional, List
import random

from app.models import user_models
from app.schemas import user_schemas
from app.core.security import get_password_hash

def get_user_by_username(db: Session, username: str) -> Optional[user_models.User]:
    return db.query(user_models.User).filter(user_models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[user_models.User]:
    return db.query(user_models.User).filter(user_models.User.email == email).first()

def create_user(db: Session, user: user_schemas.UserRegister) -> user_models.User:
    """Creates a new user with a hashed password."""
    hashed_password = get_password_hash(user.password)
    db_user = user_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role="USER",  # Default role
        verified=False # Default verification status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def generate_username_suggestions(db: Session, email: str) -> List[str]:
    """Generates a list of available username suggestions based on an email."""
    base_username = email.split('@')[0].replace('.', '').replace('_', '')
    suggestions = []
    
    # Suggest the base username first
    if not get_user_by_username(db, base_username):
        suggestions.append(base_username)

    # Generate a few more suggestions with random numbers
    for _ in range(5):
        if len(suggestions) >= 3:
            break
        suffix = random.randint(10, 999)
        suggested_name = f"{base_username}{suffix}"
        if not get_user_by_username(db, suggested_name):
            if suggested_name not in suggestions:
                suggestions.append(suggested_name)
    
    return suggestions

def verify_user_email(db: Session, email: str) -> Optional[user_models.User]:
    """Marks a user's email as verified."""
    user = get_user_by_email(db, email)
    if user:
        user.verified = True
        db.commit()
        db.refresh(user)
    return user
