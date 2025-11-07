# app/services/email.py

from azure.communication.email import EmailClient
from app.config import settings
import logging
import asyncio
import secrets
from typing import List

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.connection_string = settings.AZURE_COMMUNICATION_CONNECTION_STRING
        self.sender_email = settings.SENDER_EMAIL
        self.recipient_email = settings.RECIPIENT_EMAIL
        self.client = EmailClient.from_connection_string(self.connection_string)
    
    async def send_contact_message_notification(
        self, 
        name: str, 
        email: str, 
        subject: str, 
        message: str
    ) -> bool:
        try:
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": self.recipient_email}]
                },
                "content": {
                    "subject": f"New Contact Message: {subject}",
                    "plainText": f"""
New contact message received from your portfolio:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This is an automated notification from your portfolio contact form.
                    """,
                    "html": f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
        <h2 style="color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 10px;">
            New Contact Message
        </h2>
        
        <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
            <p><strong>Subject:</strong> {subject}</p>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #0078D4;">
                <strong>Message:</strong>
                <p style="margin-top: 10px; white-space: pre-wrap;">{message}</p>
            </div>
        </div>
        
        <p style="color: #666; font-size: 12px; text-align: center; margin-top: 20px;">
            This is an automated notification from your portfolio contact form.
        </p>
    </div>
</body>
</html>
                    """
                }
            }
            
            poller = self.client.begin_send(email_message)
            result = poller.result()
            logger.info(f"Email sent successfully. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def send_confirmation_to_user(
        self,
        name: str,
        email: str,
        subject: str
    ) -> bool:
        try:
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": email}]
                },
                "content": {
                    "subject": "Thank you for contacting me!",
                    "plainText": f"""
Hi {name},

Thank you for reaching out through my portfolio!

I've received your message about: {subject}

I'll get back to you as soon as possible.

Best regards,
Portfolio Team
                    """,
                    "html": f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
        <h2 style="color: #0078D4;">Thank you for contacting me!</h2>
        
        <p>Hi <strong>{name}</strong>,</p>
        
        <p>Thank you for reaching out through my portfolio!</p>
        
        <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p>I've received your message about: <strong>{subject}</strong></p>
        </div>
        
        <p>I'll get back to you as soon as possible.</p>
        
        <p style="margin-top: 30px;">
            Best regards,<br>
            <strong>Portfolio Team</strong>
        </p>
    </div>
</body>
</html>
                    """
                }
            }
            
            poller = self.client.begin_send(email_message)
            result = poller.result()
            logger.info(f"Confirmation email sent to {email}. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}")
            return False
    
    async def send_comment_notification(
        self,
        commenter_name: str,
        commenter_email: str,
        comment_content: str,
        item_type: str,
        item_title: str
    ) -> bool:
        try:
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": self.recipient_email}]
                },
                "content": {
                    "subject": f"New Comment on {item_type}: {item_title}",
                    "plainText": f"""
New comment received on your {item_type}: {item_title}

From: {commenter_name} ({commenter_email})

Comment:
{comment_content}

---
This comment is awaiting approval.
                    """,
                    "html": f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
        <h2 style="color: #0078D4;">New Comment Received</h2>
        
        <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <p><strong>{item_type}:</strong> {item_title}</p>
            <p><strong>From:</strong> {commenter_name} ({commenter_email})</p>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #0078D4;">
                <strong>Comment:</strong>
                <p style="margin-top: 10px; white-space: pre-wrap;">{comment_content}</p>
            </div>
        </div>
        
        <p style="color: #666; font-size: 12px; text-align: center;">
            This comment is awaiting approval.
        </p>
    </div>
</body>
</html>
                    """
                }
            }
            
            poller = self.client.begin_send(email_message)
            result = poller.result()
            logger.info(f"Comment notification sent. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send comment notification: {str(e)}")
            return False
    
    async def send_2fa_code(
        self,
        email: str,
        code: str,
        name: str
    ) -> bool:
        try:
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": email}]
                },
                "content": {
                    "subject": "Your Login Verification Code",
                    "plainText": f"""
Hi {name},

Your verification code is: {code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
{settings.APP_NAME}
                    """,
                    "html": f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
        <h2 style="color: #0078D4; text-align: center;">Login Verification</h2>
        
        <p>Hi <strong>{name}</strong>,</p>
        
        <p>Your verification code is:</p>
        
        <div style="background-color: white; padding: 30px; border-radius: 5px; margin: 20px 0; text-align: center;">
            <span style="font-size: 32px; font-weight: bold; color: #0078D4; letter-spacing: 8px;">{code}</span>
        </div>
        
        <p style="color: #d9534f; text-align: center;">This code will expire in 10 minutes.</p>
        
        <p style="color: #666; font-size: 12px; text-align: center; margin-top: 30px;">
            If you didn't request this code, please ignore this email.
        </p>
    </div>
</body>
</html>
                    """
                }
            }
            
            poller = self.client.begin_send(email_message)
            result = poller.result()
            logger.info(f"2FA code sent to {email}. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send 2FA code: {str(e)}")
            return False

    async def send_subscription_verification(
        self,
        email: str,
        token: str
    ) -> bool:
        """Enviar email de verificación de suscripción"""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-subscription?token={token}"
            
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": email}]
                },
                "content": {
                    "subject": "Confirm your subscription",
                    "plainText": f"""
    Hi!

    Thanks for subscribing to receive updates from my portfolio!

    Please confirm your subscription by clicking the link below:
    {verification_url}

    If you didn't request this subscription, you can safely ignore this email.

    Best regards,
    Portfolio Team
                    """,
                    "html": f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
            <h2 style="color: #0078D4; text-align: center;">Confirm Your Subscription</h2>
            
            <p>Hi!</p>
            
            <p>Thanks for subscribing to receive updates from my portfolio!</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                style="background-color: #0078D4; 
                        color: white; 
                        padding: 15px 30px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        display: inline-block;
                        font-weight: bold;">
                    Confirm Subscription
                </a>
            </div>
            
            <p style="color: #666; font-size: 12px; text-align: center;">
                If you didn't request this subscription, you can safely ignore this email.
            </p>
        </div>
    </body>
    </html>
                    """
                }
            }
            
            # Ejecutar en thread para no bloquear
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.begin_send(email_message).result()
            )
            
            logger.info(f"Verification email sent to {email}. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False


    async def send_new_blog_notification(
        self,
        subscribers: List[str],
        blog_title: str,
        blog_slug: str,
        blog_excerpt: str
    ) -> bool:
        """Enviar notificación de nuevo blog post a suscriptores"""
        try:
            blog_url = f"{settings.FRONTEND_URL}/blog/{blog_slug}"
            unsubscribe_url = f"{settings.FRONTEND_URL}/unsubscribe"
            
            # Enviar en BCC para privacidad
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "bcc": [{"address": email} for email in subscribers]
                },
                "content": {
                    "subject": f"New Blog Post: {blog_title}",
                    "plainText": f"""
    Hi!

    I just published a new blog post that might interest you:

    {blog_title}

    {blog_excerpt}

    Read more: {blog_url}

    ---
    You're receiving this because you subscribed to updates from my portfolio.
    Unsubscribe: {unsubscribe_url}
                    """,
                    "html": f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
            <h2 style="color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 10px;">
                📝 New Blog Post
            </h2>
            
            <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">{blog_title}</h3>
                <p style="color: #666;">{blog_excerpt}</p>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{blog_url}" 
                    style="background-color: #0078D4; 
                            color: white; 
                            padding: 12px 25px; 
                            text-decoration: none; 
                            border-radius: 5px; 
                            display: inline-block;">
                        Read Full Post
                    </a>
                </div>
            </div>
            
            <p style="color: #666; font-size: 11px; text-align: center; margin-top: 20px;">
                You're receiving this because you subscribed to updates from my portfolio.<br>
                <a href="{unsubscribe_url}" style="color: #0078D4;">Unsubscribe</a>
            </p>
        </div>
    </body>
    </html>
                    """
                }
            }
            
            # Ejecutar en thread para no bloquear
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.begin_send(email_message).result()
            )
            
            logger.info(f"Blog notification sent to {len(subscribers)} subscribers. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send blog notification: {str(e)}")
            return False


    async def send_new_project_notification(
        self,
        subscribers: List[str],
        project_title: str,
        project_id: int,
        project_description: str
    ) -> bool:
        """Enviar notificación de nuevo proyecto a suscriptores"""
        try:
            project_url = f"{settings.FRONTEND_URL}/projects/{project_id}"
            unsubscribe_url = f"{settings.FRONTEND_URL}/unsubscribe"
            
            # Enviar en BCC para privacidad
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "bcc": [{"address": email} for email in subscribers]
                },
                "content": {
                    "subject": f"New Project: {project_title}",
                    "plainText": f"""
    Hi!

    I just added a new project to my portfolio:

    {project_title}

    {project_description}

    Check it out: {project_url}

    ---
    You're receiving this because you subscribed to updates from my portfolio.
    Unsubscribe: {unsubscribe_url}
                    """,
                    "html": f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
            <h2 style="color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 10px;">
                🚀 New Project
            </h2>
            
            <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">{project_title}</h3>
                <p style="color: #666;">{project_description}</p>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{project_url}" 
                    style="background-color: #0078D4; 
                            color: white; 
                            padding: 12px 25px; 
                            text-decoration: none; 
                            border-radius: 5px; 
                            display: inline-block;">
                        View Project
                    </a>
                </div>
            </div>
            
            <p style="color: #666; font-size: 11px; text-align: center; margin-top: 20px;">
                You're receiving this because you subscribed to updates from my portfolio.<br>
                <a href="{unsubscribe_url}" style="color: #0078D4;">Unsubscribe</a>
            </p>
        </div>
    </body>
    </html>
                    """
                }
            }
            
            # Ejecutar en thread para no bloquear
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.begin_send(email_message).result()
            )
            
            logger.info(f"Project notification sent to {len(subscribers)} subscribers. Message ID: {result['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send project notification: {str(e)}")
            return False


    # Función helper para generar tokens
    def generate_verification_token() -> str:
        """Generar token de verificación único"""
        return secrets.token_urlsafe(32)




email_service = EmailService()