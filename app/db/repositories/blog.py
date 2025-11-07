# app/db/repositories/blog.py

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from sqlalchemy.orm import selectinload

from app.db.repositories.base import BaseRepository
from app.models.blog import BlogPost
from app.schemas.blog import BlogPostCreate, BlogPostUpdate


class BlogRepository(BaseRepository[BlogPost, BlogPostCreate, BlogPostUpdate]):
    
    def __init__(self):
        super().__init__(BlogPost)
    
    async def get_by_slug(
        self,
        db: AsyncSession,
        slug: str
    ) -> Optional[BlogPost]:
        return await self.get_by_field(db, "slug", slug)
    
    async def get_with_details(
        self,
        db: AsyncSession,
        post_id: int
    ) -> Optional[BlogPost]:
        return await self.get(
            db,
            post_id,
            options=[
                selectinload(BlogPost.comments),
                selectinload(BlogPost.videos)
            ]
        )
    
    async def get_by_slug_with_details(
        self,
        db: AsyncSession,
        slug: str
    ) -> Optional[BlogPost]:
        query = select(BlogPost).options(
            selectinload(BlogPost.comments),
            selectinload(BlogPost.videos)
        ).where(BlogPost.slug == slug)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_published(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ) -> Sequence[BlogPost]:
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[BlogPost.published == True],
            order_by=[desc(BlogPost.created_at)]
        )
    
    async def get_all_ordered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        published: Optional[bool] = None
    ) -> Sequence[BlogPost]:
        filters = []
        if published is not None:
            filters.append(BlogPost.published == published)
        
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters if filters else None,
            order_by=[desc(BlogPost.created_at)]
        )
    
    async def increment_views(
        self,
        db: AsyncSession,
        post_id: int
    ) -> None:
        await db.execute(
            update(BlogPost)
            .where(BlogPost.id == post_id)
            .values(views=BlogPost.views + 1)
        )
        await db.commit()
    
    async def search_by_tag(
        self,
        db: AsyncSession,
        tag: str,
        skip: int = 0,
        limit: int = 10
    ):
        query = select(BlogPost).where(
            BlogPost.tags.contains(tag),
            BlogPost.published == True
        ).order_by(desc(BlogPost.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_popular(
        self,
        db: AsyncSession,
        limit: int = 5
    ):
        return await self.get_multi(
            db,
            skip=0,
            limit=limit,
            filters=[BlogPost.published == True],
            order_by=[desc(BlogPost.views)]
        )


blog_repository = BlogRepository()