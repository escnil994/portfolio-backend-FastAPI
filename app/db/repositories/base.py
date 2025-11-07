# app/db/repositories/base.py

from typing import Generic, TypeVar, Type, Optional, List, Any, Sequence
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel


ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(
        self,
        db: AsyncSession,
        id: Any,
        *,
        options: Optional[List] = None
    ) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        
        if options:
            for option in options:
                query = query.options(option)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    # app/db/repositories/base.py

    async def get_multi(
    self,
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[List] = None,
    order_by: Optional[List] = None,
    options: Optional[List] = None
    ) -> Sequence[ModelType]:
        query = select(self.model)
        
        if filters:
            query = query.where(and_(*filters))
        
        if order_by:
            for order_expr in order_by:
                query = query.order_by(order_expr)
        else:
            query = query.order_by(self.model.id)
        
        if options:
            for option in options:
                query = query.options(option)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        field_value: Any,
        *,
        options: Optional[List] = None
    ) -> Optional[ModelType]:
        query = select(self.model).where(
            getattr(self.model, field_name) == field_value
        )
        
        if options:
            for option in options:
                query = query.options(option)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        commit: bool = True
    ) -> ModelType:
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_data)
        
        db.add(db_obj)
        
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        commit: bool = True
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj
    
    
    
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        id: Any,
        commit: bool = True
    ) -> bool:
        db_obj = await self.get(db, id)
        if not db_obj:
            return False
        
        await db.delete(db_obj)
        
        if commit:
            await db.commit()
        
        return True
    
    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Optional[List] = None
    ) -> int:
        query = select(func.count(self.model.id))
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        return result.scalar_one()
    
    async def exists(
        self,
        db: AsyncSession,
        *,
        filters: List
    ) -> bool:
        count = await self.count(db, filters=filters)
        return count > 0