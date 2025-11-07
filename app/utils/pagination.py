# app/utils/pagination.py

from typing import TypeVar, Generic, List, Sequence
from pydantic import BaseModel, Field
from math import ceil
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        
        return cls(
            items=list(items),
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


async def paginate(
    db: AsyncSession,
    query: select,
    page: int = 1,
    page_size: int = 10
) -> tuple[List, int]:
    count_query = select(func.count()).select_from(query.alias())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    skip = (page - 1) * page_size
    items_query = query.offset(skip).limit(page_size)
    result = await db.execute(items_query)
    items = list(result.scalars().all())
    
    return items, total