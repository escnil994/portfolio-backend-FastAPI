from azure.communication.email import EmailClient
from app.config import settings
import logging
import asyncio
import secrets
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.connection_string = settings.AZURE_COMMUNICATION_CONNECTION_STRING
        self.sender_email = settings.SENDER_EMAIL
        self.recipient_email = settings.RECIPIENT_EMAIL
        # Configurar cliente con retry policy implícito en el SDK
        self.client = EmailClient.from_connection_string(self.connection_string)

        self.colors = {
            "bg_dark": "#0f172a",       # Fondo oscuro principal
            "bg_card": "#1e293b",       # Fondo de tarjeta
            "text_main": "#e2e8f0",     # Texto claro
            "text_muted": "#94a3b8",    # Texto secundario
            "accent_start": "#3b82f6",  # Azul (gradiente inicio)
            "accent_end": "#06b6d4",    # Cian (gradiente fin)
            "code_bg": "#334155"        # Fondo para bloques de código
        }

    def _get_html_template(self, title: str, body_content: str, button_text: Optional[str] = None, button_url: Optional[str] = None) -> str:
        """
        Genera una plantilla HTML responsive con el branding de Escnil994 (Dark Mode).
        """
        button_html = ""
        if button_text and button_url:
            button_html = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{button_url}" style="
                    background: linear-gradient(90deg, {self.colors['accent_start']}, {self.colors['accent_end']});
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                    display: inline-block;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                ">{button_text}</a>
            </div>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: {self.colors['bg_dark']}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: {self.colors['text_main']};">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td style="padding: 20px 0; text-align: center;">
                <h1 style="margin: 0; font-family: 'Courier New', monospace; color: {self.colors['text_main']}; font-size: 24px;">
                    <span style="color: {self.colors['accent_start']}"></span>Escnil994<span style="color: {self.colors['accent_end']}/>&gt;</span>
                </h1>
            </td>
        </tr>
        <tr>
            <td style="padding: 0 10px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; margin: 0 auto; background-color: {self.colors['bg_card']}; border-radius: 12px; border: 1px solid #334155; overflow: hidden;">
                    <tr>
                        <td height="4" style="background: linear-gradient(90deg, {self.colors['accent_start']}, {self.colors['accent_end']});"></td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="color: white; margin-top: 0; font-size: 22px; border-bottom: 1px solid #334155; padding-bottom: 15px;">{title}</h2>
                            
                            <div style="font-size: 16px; line-height: 1.6; color: {self.colors['text_main']};">
                                {body_content}
                            </div>

                            {button_html}
                            
                            <p style="margin-top: 30px; font-size: 14px; color: {self.colors['text_muted']}; border-top: 1px solid #334155; padding-top: 20px;">
                                Best regards,<br>
                                <strong style="color: white;">Nilson Escobar</strong><br>
                                <span style="font-size: 12px;">Full Stack Developer & DevOps</span>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; text-align: center; font-size: 12px; color: {self.colors['text_muted']};">
                <p>&copy; 2025 Nilson Escobar. All rights reserved.</p>
                <p>El Salvador, Ahuachapán.</p>
            </td>
        </tr>
    </table>
</body>
</html>
        """

    async def _send_async(self, message: dict) -> dict:
        """Helper to run blocking send in a separate thread"""
        loop = asyncio.get_running_loop()
        try:
            poller = await loop.run_in_executor(
                None, 
                lambda: self.client.begin_send(message)
            )
            return await loop.run_in_executor(None, poller.result)
        except Exception as e:
            logger.error(f"Email transmission failed: {e}")
            raise

    # 1. NOTIFICACIÓN AL ADMIN (TÚ)
    async def send_contact_message_notification(self, name: str, email: str, subject: str, message: str) -> bool:
        try:
            html_content = self._get_html_template(
                title="🚀 New Contact Message",
                body_content=f"""
                <p>You have received a new message via your portfolio contact form.</p>
                <div style="background-color: {self.colors['code_bg']}; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Name:</strong> {name}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> <a href="mailto:{email}" style="color: {self.colors['accent_end']};">{email}</a></p>
                    <p style="margin: 5px 0;"><strong>Subject:</strong> {subject}</p>
                    <hr style="border: 0; border-top: 1px solid #475569; margin: 15px 0;">
                    <p style="margin: 5px 0;"><strong>Message:</strong></p>
                    <p style="white-space: pre-wrap; color: #cbd5e1;">{message}</p>
                </div>
                """
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"to": [{"address": self.recipient_email}]},
                "content": {
                    "subject": f"[Portfolio] Contact: {subject}",
                    "plainText": f"Name: {name}\nEmail: {email}\nMessage: {message}",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

    # 2. CONFIRMACIÓN AL USUARIO (Respuesta automática)
    async def send_confirmation_to_user(self, name: str, email: str, subject: str) -> bool:
        try:
            html_content = self._get_html_template(
                title="Message Received!",
                body_content=f"""
                <p>Hi <strong>{name}</strong>,</p>
                <p>Thank you for reaching out via <strong>&lt;Escnil994/&gt;</strong>.</p>
                <p>I have successfully received your message regarding: <em style="color: {self.colors['accent_end']};">{subject}</em>.</p>
                <p>I typically respond within 24-48 hours via LinkedIn or email.</p>
                """
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"to": [{"address": email}]},
                "content": {
                    "subject": "I've received your message - Nilson Escobar",
                    "plainText": f"Hi {name}, thanks for contacting me. I'll get back to you soon regarding '{subject}'.",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

    # 3. NOTIFICACIÓN DE COMENTARIO (ADMIN)
    async def send_comment_notification(self, commenter_name: str, commenter_email: str, comment_content: str, item_type: str, item_title: str) -> bool:
        try:
            html_content = self._get_html_template(
                title="💬 New Comment Pending",
                body_content=f"""
                <p>A new comment has been posted on the <strong>{item_type}</strong>: <em>{item_title}</em></p>
                <div style="background-color: {self.colors['code_bg']}; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <p style="margin: 0 0 10px 0;"><strong>User:</strong> {commenter_name} ({commenter_email})</p>
                    <p style="margin: 0; font-style: italic;">"{comment_content}"</p>
                </div>
                <p>This comment requires approval before it is visible.</p>
                """
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"to": [{"address": self.recipient_email}]},
                "content": {
                    "subject": f"New Comment on {item_title}",
                    "plainText": f"User {commenter_name} commented on {item_title}: {comment_content}",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

    # 4. CÓDIGO 2FA (Estilo Tech)
    async def send_2fa_code(self, email: str, code: str, name: str) -> bool:
        try:
            html_content = self._get_html_template(
                title="🔐 Verification Code",
                body_content=f"""
                <p>Hi {name},</p>
                <p>Someone attempted to log in to your account. Use the code below to complete the authentication:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <span style="
                        background-color: {self.colors['code_bg']};
                        color: {self.colors['accent_end']};
                        font-family: 'Courier New', monospace;
                        font-size: 32px;
                        font-weight: bold;
                        padding: 15px 30px;
                        border-radius: 8px;
                        letter-spacing: 8px;
                        border: 1px solid #475569;
                        display: inline-block;
                    ">{code}</span>
                </div>
                
                <p style="color: #ef4444; font-size: 14px; text-align: center;">This code expires in 10 minutes.</p>
                <p style="font-size: 13px; color: {self.colors['text_muted']};">If you didn't request this, you can safely ignore this email.</p>
                """
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"to": [{"address": email}]},
                "content": {
                    "subject": f"Verification Code: {code}",
                    "plainText": f"Your code is: {code}",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

    # 5. VERIFICACIÓN DE SUSCRIPCIÓN
    async def send_subscription_verification(self, email: str, token: str) -> bool:
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-subscription?token={token}"
            
            html_content = self._get_html_template(
                title="Verify your Subscription",
                body_content=f"""
                <p>Thanks for your interest in my portfolio updates!</p>
                <p>To ensure I have the right email address, please click the button below to confirm your subscription.</p>
                """,
                button_text="Confirm Subscription",
                button_url=verification_url
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"to": [{"address": email}]},
                "content": {
                    "subject": "Action Required: Confirm Subscription",
                    "plainText": f"Please verify your email: {verification_url}",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

    # 6. NEWSLETTER: NUEVO BLOG POST
    async def send_new_blog_notification(self, subscribers: List[str], blog_title: str, blog_slug: str, blog_excerpt: str) -> bool:
        try:
            blog_url = f"{settings.FRONTEND_URL}/blog/{blog_slug}"
            unsubscribe_url = f"{settings.FRONTEND_URL}/unsubscribe"
            
            html_content = self._get_html_template(
                title="📝 New Article Published",
                body_content=f"""
                <h3 style="color: {self.colors['accent_end']}; margin-top: 0;">{blog_title}</h3>
                <p style="font-size: 16px; color: {self.colors['text_muted']};">{blog_excerpt}</p>
                <p>Read the full story to learn more about this topic.</p>
                <p style="font-size: 12px; margin-top: 40px; text-align: center;"><a href="{unsubscribe_url}" style="color: {self.colors['text_muted']};">Unsubscribe</a></p>
                """,
                button_text="Read Full Article",
                button_url=blog_url
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"bcc": [{"address": email} for email in subscribers]},
                "content": {
                    "subject": f"New Post: {blog_title}",
                    "plainText": f"Read my new post: {blog_title} at {blog_url}",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

    # 7. NEWSLETTER: NUEVO PROYECTO
    async def send_new_project_notification(self, subscribers: List[str], project_title: str, project_id: int, project_description: str) -> bool:
        try:
            project_url = f"{settings.FRONTEND_URL}/projects/{project_id}"
            unsubscribe_url = f"{settings.FRONTEND_URL}/unsubscribe"
            
            html_content = self._get_html_template(
                title="🚀 New Project Dropped",
                body_content=f"""
                <h3 style="color: {self.colors['accent_end']}; margin-top: 0;">{project_title}</h3>
                <p style="font-size: 16px; color: {self.colors['text_muted']};">{project_description}</p>
                <p>Check out the tech stack and live demo on my portfolio.</p>
                <p style="font-size: 12px; margin-top: 40px; text-align: center;"><a href="{unsubscribe_url}" style="color: {self.colors['text_muted']};">Unsubscribe</a></p>
                """,
                button_text="View Project",
                button_url=project_url
            )

            email_msg = {
                "senderAddress": self.sender_email,
                "recipients": {"bcc": [{"address": email} for email in subscribers]},
                "content": {
                    "subject": f"Check out my new project: {project_title}",
                    "plainText": f"New project {project_title} available at {project_url}",
                    "html": html_content
                }
            }
            await self._send_async(email_msg)
            return True
        except Exception:
            return False

email_service = EmailService()