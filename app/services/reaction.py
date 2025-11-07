# app/services/reaction.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from typing import Optional, Tuple
import logging

from app.models.reaction import Reaction, ReactionTypeEnum
from app.models.blog import BlogPost
from app.models.project import Project

logger = logging.getLogger(__name__)


class ReactionService:
    
    async def upsert_reaction(
        self,
        db: AsyncSession,
        email: str,
        name: str,
        reaction_type: ReactionTypeEnum,
        entity_id: int,
        entity_type: str,
        ip_address: Optional[str] = None
    ) -> Tuple[Reaction, str]:
        result = await db.execute(
            select(Reaction).where(
                and_(
                    Reaction.email == email,
                    Reaction.entity_id == entity_id,
                    Reaction.entity_type == entity_type
                )
            )
        )
        existing_reaction = result.scalar_one_or_none()
        
        if existing_reaction:
            old_type = existing_reaction.reaction_type
            existing_reaction.reaction_type = reaction_type
            existing_reaction.name = name
            
            await db.commit()
            await db.refresh(existing_reaction)
            
            logger.info(
                f"Reaction updated: {email} changed from {old_type} to {reaction_type} "
                f"on {entity_type}:{entity_id}"
            )
            
            return existing_reaction, "updated"
        else:
            new_reaction = Reaction(
                email=email,
                name=name,
                reaction_type=reaction_type,
                entity_id=entity_id,
                entity_type=entity_type,
                ip_address=ip_address
            )
            
            db.add(new_reaction)
            await db.commit()
            await db.refresh(new_reaction)
            
            logger.info(
                f"New reaction: {email} reacted with {reaction_type} "
                f"on {entity_type}:{entity_id}"
            )
            
            return new_reaction, "created"
    
    async def delete_reaction(
        self,
        db: AsyncSession,
        email: str,
        entity_id: int,
        entity_type: str
    ) -> bool:
        result = await db.execute(
            delete(Reaction).where(
                and_(
                    Reaction.email == email,
                    Reaction.entity_id == entity_id,
                    Reaction.entity_type == entity_type
                )
            )
        )
        await db.commit()
        
        deleted = result.rowcount > 0
        
        if deleted:
            logger.info(f"Reaction deleted: {email} on {entity_type}:{entity_id}")
        
        return deleted
    
    async def get_reaction_summary(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str,
        user_email: Optional[str] = None
    ) -> dict:
        result = await db.execute(
            select(
                Reaction.reaction_type,
                func.count(Reaction.id).label('count')
            ).where(
                and_(
                    Reaction.entity_id == entity_id,
                    Reaction.entity_type == entity_type
                )
            ).group_by(Reaction.reaction_type)
        )
        
        counts = result.all()
        
        like_count = 0
        love_count = 0
        congratulations_count = 0
        
        for reaction_type, count in counts:
            if reaction_type == ReactionTypeEnum.LIKE:
                like_count = count
            elif reaction_type == ReactionTypeEnum.LOVE:
                love_count = count
            elif reaction_type == ReactionTypeEnum.CONGRATULATIONS:
                congratulations_count = count
        
        total = like_count + love_count + congratulations_count
        
        user_reaction = None
        if user_email:
            result = await db.execute(
                select(Reaction.reaction_type).where(
                    and_(
                        Reaction.email == user_email,
                        Reaction.entity_id == entity_id,
                        Reaction.entity_type == entity_type
                    )
                )
            )
            user_reaction_row = result.scalar_one_or_none()
            if user_reaction_row:
                user_reaction = user_reaction_row
        
        return {
            "total_reactions": total,
            "like_count": like_count,
            "love_count": love_count,
            "congratulations_count": congratulations_count,
            "user_reaction": user_reaction
        }
    
    async def verify_entity_exists(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str
    ) -> bool:
        if entity_type == 'blog_post':
            result = await db.execute(
                select(BlogPost.id).where(BlogPost.id == entity_id)
            )
            return result.scalar_one_or_none() is not None
        
        elif entity_type == 'project':
            result = await db.execute(
                select(Project.id).where(Project.id == entity_id)
            )
            return result.scalar_one_or_none() is not None
        
        return False
    
    async def get_user_reaction(
        self,
        db: AsyncSession,
        email: str,
        entity_id: int,
        entity_type: str
    ) -> Optional[Reaction]:
        result = await db.execute(
            select(Reaction).where(
                and_(
                    Reaction.email == email,
                    Reaction.entity_id == entity_id,
                    Reaction.entity_type == entity_type
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_reactions(
        self,
        db: AsyncSession,
        entity_id: int,
        entity_type: str,
        limit: int = 100,
        offset: int = 0
    ):
        result = await db.execute(
            select(Reaction)
            .where(
                and_(
                    Reaction.entity_id == entity_id,
                    Reaction.entity_type == entity_type
                )
            )
            .order_by(Reaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


reaction_service = ReactionService()