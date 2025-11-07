# app/db/repositories/reaction.py

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc

from app.db.repositories.base import BaseRepository
from app.models.reaction import Reaction, ReactionTypeEnum
from app.schemas.reaction import ReactionCreate, ReactionUpdate


class ReactionRepository(BaseRepository[Reaction, ReactionCreate, ReactionUpdate]):
    
    def __init__(self):
        super().__init__(Reaction)
    
    async def get_by_email_and_entity(
        self,
        db: AsyncSession,
        email: str,
        entity_id: int,
        entity_type: str
    ) -> Optional[Reaction]:
        query = select(Reaction).where(
            and_(
                Reaction.email == email,
                Reaction.entity_id == entity_id,
                Reaction.entity_type == entity_type
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_entity(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Reaction]:
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[
                Reaction.entity_id == entity_id,
                Reaction.entity_type == entity_type
            ],
            order_by=[desc(Reaction.created_at)]
        )
    
    async def count_by_entity(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str
    ) -> int:
        return await self.count(
            db,
            filters=[
                Reaction.entity_id == entity_id,
                Reaction.entity_type == entity_type
            ]
        )
    
    async def count_by_type(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str,
        reaction_type: ReactionTypeEnum
    ) -> int:
        return await self.count(
            db,
            filters=[
                Reaction.entity_id == entity_id,
                Reaction.entity_type == entity_type,
                Reaction.reaction_type == reaction_type
            ]
        )
    
    async def delete_by_email_and_entity(
        self,
        db: AsyncSession,
        email: str,
        entity_id: int,
        entity_type: str
    ) -> bool:
        reaction = await self.get_by_email_and_entity(
            db, email, entity_id, entity_type
        )
        
        if not reaction:
            return False
        
        await db.delete(reaction)
        await db.commit()
        return True
    
    async def get_reaction_counts(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str
    ) -> dict:
        query = select(
            Reaction.reaction_type,
            func.count(Reaction.id).label('count')
        ).where(
            and_(
                Reaction.entity_id == entity_id,
                Reaction.entity_type == entity_type
            )
        ).group_by(Reaction.reaction_type)
        
        result = await db.execute(query)
        counts = result.all()
        
        return {
            reaction_type.value: count 
            for reaction_type, count in counts
        }


reaction_repository = ReactionRepository()