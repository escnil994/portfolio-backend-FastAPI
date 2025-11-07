# app/db/repositories/project.py

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
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
        return await self.get(
            db,
            project_id,
            options=[
                selectinload(Project.comments),
                selectinload(Project.videos)
            ]
        )
    
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
            order_by=[desc(Project.created_at)]
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
        
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters if filters else None,
            order_by=[desc(Project.created_at)]
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


project_repository = ProjectRepository()