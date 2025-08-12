from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Portfolio API"
    DEBUG: bool = False
    API_URL: str = "http://localhost:8000"

    # --- Database Components ---
    DB_USER: str
    DB_PASSWORD: str
    DB_SERVER: str
    DB_PORT: int = 1433
    DB_NAME: str
    USE_DOCKER_DB: bool = False
    DATABASE_URL: str = ""

    # --- JWT Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # --- CORS Settings ---
    ALLOWED_ORIGINS: str = ""

    # --- Azure Communication Services ---
    AZURE_COMM_CONN_STRING: str = ""
    AZURE_COMM_SENDER_ADDRESS: str = ""

    @model_validator(mode='after')
    def assemble_db_connection(self) -> 'Settings':
        driver = "ODBC+Driver+18+for+SQL+Server"
        connection_string = (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?"
            f"driver={driver}"
        )
        if self.USE_DOCKER_DB:
            connection_string += "&TrustServerCertificate=yes"
        self.DATABASE_URL = connection_string
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
