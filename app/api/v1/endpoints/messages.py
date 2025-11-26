from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional

from app.db.session import get_db
from app.models.contact import ContactMessage
from app.models.user import User
from app.schemas.contact import ContactMessageResponse, ContactMessageUpdate, MessageStatsResponse
from app.api.deps import get_current_admin

router = APIRouter()

@router.get("/", response_model=List[ContactMessageResponse])
async def get_contact_messages(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    read: Optional[bool] = None
):
    query = select(ContactMessage)
    
    if read is not None:
        query = query.where(ContactMessage.read == read)
        
    query = query.order_by(desc(ContactMessage.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    return messages

@router.get("/stats", response_model=MessageStatsResponse)
async def get_message_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    total_query = select(func.count(ContactMessage.id))
    unread_query = select(func.count(ContactMessage.id)).where(ContactMessage.read == False)
    
    total_messages_result = await db.execute(total_query)
    unread_count_result = await db.execute(unread_query)
    
    total_messages = total_messages_result.scalar() or 0
    unread_count = unread_count_result.scalar() or 0
    
    return MessageStatsResponse(
        total_messages=total_messages,
        unread_count=unread_count
    )

@router.patch("/{message_id}", response_model=ContactMessageResponse)
async def update_message_status(
    message_id: int,
    message_update: ContactMessageUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    result = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        
    message.read = message_update.read
    await db.commit()
    await db.refresh(message)
    
    return message

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    result = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        
    await db.delete(message)
    await db.commit()