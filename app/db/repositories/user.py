# app/db/repositories/user.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(
        self, 
        db: AsyncSession, 
        email: str
    ) -> Optional[User]:
        return await self.get_by_field(db, "email", email)
    
    async def get_by_username(
        self, 
        db: AsyncSession, 
        username: str
    ) -> Optional[User]:
        return await self.get_by_field(db, "username", username)
    
    async def is_email_taken(
        self, 
        db: AsyncSession, 
        email: str
    ) -> bool:
        return await self.exists(db, filters=[User.email == email])
    
    async def is_username_taken(
        self, 
        db: AsyncSession, 
        username: str
    ) -> bool:
        return await self.exists(db, filters=[User.username == username])
    
    async def get_active_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ):
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[User.is_active == True]
        )
    
    async def get_superusers(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ):
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[User.is_superuser == True]
        )


user_repository = UserRepository()