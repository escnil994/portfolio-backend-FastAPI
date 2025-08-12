from app.core.config import settings
from azure.communication.email import EmailClient

def send_verification_email(email_to: str, username: str, verification_url: str):
    """
    Sends an account verification email.
    NOTE: This is a MOCK function. It prints to the console instead of sending a real email.
    """
    subject = f"¡Verifica tu cuenta para {settings.PROJECT_NAME}!"
    html_content = f"""
    <html>
        <body>
            <h2>¡Hola {username}!</h2>
            <p>Gracias por registrarte. Por favor, haz clic en el siguiente enlace para verificar tu correo electrónico:</p>
            <a href="{verification_url}">Verificar mi cuenta</a>
            <p>Si no te registraste, por favor ignora este mensaje.</p>
        </body>
    </html>
    """
    
    print("---- INICIO DE CORREO DE VERIFICACIÓN (SIMULADO) ----")
    print(f"Para: {email_to}")
    print(f"Asunto: {subject}")
    print("Contenido:")
    print(html_content.strip())
    print("---- FIN DE CORREO DE VERIFICACIÓN (SIMULADO) ----")

    # IMPLEMENTATION WITH AZURE ---
    try:
        client = EmailClient.from_connection_string(settings.AZURE_COMM_CONN_STRING)
        message = {
            "content": {
                "subject": subject,
                "html": html_content,
            },
            "recipients": {"to": [{"address": email_to}]},
            "senderAddress": settings.AZURE_COMM_SENDER_ADDRESS,
        }
        poller = client.begin_send(message)
        result = poller.result()
        print(f"Email sent successfully: {result}")
    except Exception as ex:
        print(f"Error sending email: {ex}")
