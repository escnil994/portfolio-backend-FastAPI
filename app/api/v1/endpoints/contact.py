# app/api/v1/endpoints/contact.py

from fastapi import APIRouter, Depends, HTTPException, status
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
    
    admin_email_sent = False
    try:
        logger.info("Sending notification to admin...")
        admin_email_sent = await email_service.send_contact_message_notification(
            name=message_data.name,
            email=message_data.email,
            subject=message_data.subject,
            message=message_data.message
        )
        
        if admin_email_sent:
            logger.info("Admin notification sent successfully")
        else:
            logger.warning("Admin notification failed")
            
    except Exception as e:
        logger.error(f"Exception sending admin notification: {type(e).__name__}: {str(e)}")
    
    user_email_sent = False
    try:
        logger.info("Sending confirmation to user...")
        user_email_sent = await email_service.send_confirmation_to_user(
            name=message_data.name,
            email=message_data.email,
            subject=message_data.subject
        )
        
        if user_email_sent:
            logger.info("User confirmation sent successfully")
        else:
            logger.warning("User confirmation failed")
            
    except Exception as e:
        logger.error(f"Exception sending user confirmation: {type(e).__name__}: {str(e)}")
    
    if admin_email_sent and user_email_sent:
        return MessageResponse(
            message="Message sent successfully",
            detail="Thank you for contacting me. I'll get back to you soon!"
        )
    elif admin_email_sent or user_email_sent:
        return MessageResponse(
            message="Message sent with partial success",
            detail="Your message was saved. Some notifications may have failed."
        )
    else:
        return MessageResponse(
            message="Message saved but notifications failed",
            detail="Your message was saved. However, email notifications failed."
        )