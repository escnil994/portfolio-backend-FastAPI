from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from sqlalchemy.orm import selectinload

from app.db.repositories.base import BaseRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    
    def __init__(self):
        super().__init__(Project)
    
    async def get_with_details(
        self,
        db: AsyncSession,
        project_id: int
    ) -> Optional[Project]:
        
        query = select(self.model).where(self.model.id == project_id).options(
            selectinload(Project.comments),
            selectinload(Project.videos),
            selectinload(Project.author)
        )
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()
    
    async def get_featured(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ) -> Sequence[Project]:
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[Project.featured == True],
            order_by=[desc(Project.created_at)],
            options=[selectinload(Project.author)]
        )
    
    async def get_all_ordered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        featured: Optional[bool] = None
    ) -> Sequence[Project]:
        filters = []
        if featured is not None:
            filters.append(Project.featured == featured)
        
        options = [selectinload(Project.author)]
        
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters if filters else None,
            order_by=[desc(Project.created_at)],
            options=options
        )
    
    async def search_by_technology(
        self,
        db: AsyncSession,
        technology: str,
        skip: int = 0,
        limit: int = 10
    ):
        query = select(Project).where(
            Project.technologies.contains(technology)
        ).order_by(desc(Project.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def increment_views(
        self,
        db: AsyncSession,
        project_id: int
    ) -> None:
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(views=Project.views + 1)
        )
        await db.commit()

project_repository = ProjectRepository()