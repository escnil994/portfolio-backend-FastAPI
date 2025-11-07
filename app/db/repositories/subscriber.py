from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.subscriber import Subscriber
from app.schemas.subscriber import SubscriberCreate


class SubscriberRepository(BaseRepository[Subscriber, SubscriberCreate, dict]):
    
    def __init__(self):
        super().__init__(Subscriber)
    
    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[Subscriber]:
        """Obtener suscriptor por email"""
        return await self.get_by_field(db, "email", email)
    
    async def get_by_token(
        self,
        db: AsyncSession,
        token: str
    ) -> Optional[Subscriber]:
        """Obtener suscriptor por token de verificación"""
        return await self.get_by_field(db, "verification_token", token)
    
    async def get_active_verified(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 1000
    ) -> Sequence[Subscriber]:
        """Obtener todos los suscriptores activos y verificados"""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[
                Subscriber.is_active == True,
                Subscriber.is_verified == True
            ]
        )
    
    async def verify_subscriber(
        self,
        db: AsyncSession,
        subscriber: Subscriber
    ) -> Subscriber:
        """Marcar suscriptor como verificado"""
        subscriber.is_verified = True
        # subscriber.verification_token = None
        await db.commit()
        await db.refresh(subscriber)
        return subscriber
    
    async def deactivate_subscriber(
        self,
        db: AsyncSession,
        subscriber: Subscriber
    ) -> Subscriber:
        """Desactivar suscriptor (unsubscribe)"""
        subscriber.is_active = False
        await db.commit()
        await db.refresh(subscriber)
        return subscriber


subscriber_repository = SubscriberRepository()