from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.repositories.subscriber import subscriber_repository
from app.services.email import email_service

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para gestionar notificaciones a suscriptores"""
    
    async def notify_new_blog_post(
        self,
        db: AsyncSession,
        blog_title: str,
        blog_slug: str,
        blog_excerpt: str
    ) -> bool:
        """
        Notificar a todos los suscriptores activos sobre un nuevo blog post
        """
        try:
            # Obtener todos los suscriptores activos y verificados
            subscribers = await subscriber_repository.get_active_verified(db)
            
            if not subscribers:
                logger.info("No active subscribers to notify")
                return True
            
            # Extraer emails
            subscriber_emails = [sub.email for sub in subscribers]
            
            # Enviar notificación en lotes de 50 para evitar límites de email
            batch_size = 50
            for i in range(0, len(subscriber_emails), batch_size):
                batch = subscriber_emails[i:i + batch_size]
                
                success = await email_service.send_new_blog_notification(
                    subscribers=batch,
                    blog_title=blog_title,
                    blog_slug=blog_slug,
                    blog_excerpt=blog_excerpt or "Check out my latest blog post!"
                )
                
                if not success:
                    logger.error(f"Failed to send notification to batch {i//batch_size + 1}")
            
            logger.info(f"Blog notifications sent to {len(subscriber_emails)} subscribers")
            return True
            
        except Exception as e:
            logger.error(f"Error notifying subscribers about new blog: {str(e)}")
            return False
    
    async def notify_new_project(
        self,
        db: AsyncSession,
        project_title: str,
        project_id: int,
        project_description: str
    ) -> bool:
        """
        Notificar a todos los suscriptores activos sobre un nuevo proyecto
        """
        try:
            # Obtener todos los suscriptores activos y verificados
            subscribers = await subscriber_repository.get_active_verified(db)
            
            if not subscribers:
                logger.info("No active subscribers to notify")
                return True
            
            # Extraer emails
            subscriber_emails = [sub.email for sub in subscribers]
            
            # Enviar notificación en lotes de 50
            batch_size = 50
            for i in range(0, len(subscriber_emails), batch_size):
                batch = subscriber_emails[i:i + batch_size]
                
                success = await email_service.send_new_project_notification(
                    subscribers=batch,
                    project_title=project_title,
                    project_id=project_id,
                    project_description=project_description
                )
                
                if not success:
                    logger.error(f"Failed to send notification to batch {i//batch_size + 1}")
            
            logger.info(f"Project notifications sent to {len(subscriber_emails)} subscribers")
            return True
            
        except Exception as e:
            logger.error(f"Error notifying subscribers about new project: {str(e)}")
            return False


notification_service = NotificationService()