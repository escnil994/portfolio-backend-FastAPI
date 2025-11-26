from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await self.get_by_field(db, "email", email)
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        return await self.get_by_field(db, "username", username)
    
    async def get_by_email_or_username(self, db: AsyncSession, identifier: str) -> Optional[User]:
        query = select(self.model).where(
            or_(
                self.model.email == identifier,
                self.model.username == identifier
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

user_repository = UserRepository()