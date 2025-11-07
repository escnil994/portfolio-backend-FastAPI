from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import secrets

from app.db.session import get_db
from app.db.repositories.subscriber import subscriber_repository
from app.schemas.subscriber import (
    SubscriberCreate,
    SubscriberResponse,
    SubscriberVerify,
    UnsubscribeRequest
)
from app.services.email import email_service
from app.api.deps import get_current_admin
from app.models.user import User

router = APIRouter()


@router.post("/subscribe", response_model=dict, status_code=status.HTTP_201_CREATED)
async def subscribe(
    subscriber_data: SubscriberCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Suscribirse para recibir notificaciones de nuevos blogs y proyectos.
    Requiere verificación por email.
    """
    existing_subscriber = await subscriber_repository.get_by_email(
        db, subscriber_data.email
    )
    
    if existing_subscriber:
        if existing_subscriber.is_verified and existing_subscriber.is_active:
            return {
                "message": "You are already subscribed!",
                "verified": True
            }
        elif existing_subscriber.is_verified and not existing_subscriber.is_active:
            existing_subscriber.is_active = True
            await db.commit()
            return {
                "message": "Your subscription has been reactivated!",
                "verified": True
            }
        else:
            background_tasks.add_task(
                email_service.send_subscription_verification,
                existing_subscriber.email,
                existing_subscriber.verification_token
            )
            return {
                "message": "Verification email resent. Please check your inbox.",
                "verified": False
            }
    
    verification_token = secrets.token_urlsafe(32)
    
    subscriber = await subscriber_repository.create(
        db,
        obj_in=subscriber_data
    )
    
    subscriber.verification_token = verification_token
    await db.commit()
    
    background_tasks.add_task(
        email_service.send_subscription_verification,
        subscriber.email,
        verification_token
    )
    
    return {
        "message": "Subscription created! Please check your email to verify.",
        "verified": False
    }


@router.post("/verify", response_model=dict)
async def verify_subscription(
    verify_data: SubscriberVerify,
    db: AsyncSession = Depends(get_db)
):
    """
    Verificar suscripción mediante token enviado por email
    """
    subscriber = await subscriber_repository.get_by_token(
        db, verify_data.token
    )

    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification token"
        )
    
    if subscriber.is_verified:
        return {
            "message": "Email already verified!",
            "verified": True
        }
    
    await subscriber_repository.verify_subscriber(db, subscriber)
    
    return {
        "message": "Email verified successfully! You'll now receive updates.",
        "verified": True
    }


@router.post("/unsubscribe", response_model=dict)
async def unsubscribe(
    unsubscribe_data: UnsubscribeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Darse de baja de las notificaciones
    """
    subscriber = await subscriber_repository.get_by_email(
        db, unsubscribe_data.email
    )
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found in subscription list"
        )
    
    if not subscriber.is_active:
        return {
            "message": "You are already unsubscribed"
        }
    
    await subscriber_repository.deactivate_subscriber(db, subscriber)
    
    return {
        "message": "You have been unsubscribed successfully. Sorry to see you go!"
    }



@router.get("/admin/all", response_model=List[SubscriberResponse])
async def get_all_subscribers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Obtener todos los suscriptores (solo admin)
    """
    subscribers = await subscriber_repository.get_multi(
        db, skip=skip, limit=limit
    )
    return subscribers


@router.get("/admin/active", response_model=List[SubscriberResponse])
async def get_active_subscribers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Obtener solo suscriptores activos y verificados (solo admin)
    """
    subscribers = await subscriber_repository.get_active_verified(
        db, skip=skip, limit=limit
    )
    return subscribers


@router.delete("/admin/{subscriber_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscriber(
    subscriber_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Eliminar suscriptor permanentemente (solo admin)
    """
    deleted = await subscriber_repository.delete(db, id=subscriber_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found"
        )


@router.get("/admin/stats", response_model=dict)
async def get_subscriber_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Obtener estadísticas de suscriptores (solo admin)
    """
    total = await subscriber_repository.count(db)
    active = await subscriber_repository.count(
        db,
        filters=[subscriber_repository.model.is_active == True]
    )
    verified = await subscriber_repository.count(
        db,
        filters=[subscriber_repository.model.is_verified == True]
    )
    active_verified = await subscriber_repository.count(
        db,
        filters=[
            subscriber_repository.model.is_active == True,
            subscriber_repository.model.is_verified == True
        ]
    )
    
    return {
        "total": total,
        "active": active,
        "verified": verified,
        "active_verified": active_verified
    }