from cryptography.fernet import Fernet
import os


ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY", b'g_s7_D5vR9FqQ_1hM2x3k4L5p6O7i8U9y0T1r2E3w4Q=')

cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encripta datos sensibles antes de guardar en DB"""
    if not data:
        return None
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    """Desencripta datos de la DB para usarlos en memoria"""
    if not token:
        return None
    try:
        return cipher.decrypt(token.encode()).decode()
    except Exception:
        return None