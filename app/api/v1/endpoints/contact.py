from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.session import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactMessageCreate, MessageResponse
from app.services.email import email_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_contact_message(
    message_data: ContactMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Received contact message from {message_data.name} ({message_data.email})")
    
    try:
        message = ContactMessage(**message_data.model_dump())
        db.add(message)
        await db.commit()
        await db.refresh(message)
        logger.info(f"Message saved to database with ID: {message.id}")
    except Exception as e:
        logger.error(f"Failed to save message to database: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )
    
    background_tasks.add_task(
        email_service.send_contact_message_notification,
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject,
        message=message_data.message
    )
    
    background_tasks.add_task(
        email_service.send_confirmation_to_user,
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject
    )
    
    return MessageResponse(
        message="Message received successfully",
        detail="Thank you for contacting me. I'll get back to you soon!"
    )