from typing import List
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DB_URL: str = "postgresql+asyncpg://usuario:senhadopostgres@localhost:5432/faculdade"
    DBBaseModel = declarative_base()

    JWT_SECRET: str = "8X0EzuMh7W0h1sKB-9gJ7XFbjP_4gjYkh8X11AI9n0c"
    """
    import secrets

    token: str = secrets.token_urlsafe(32)
    """


    ALGORITHM: str = "HS256"

    """60 minutos x 24 horas x 7 dias = Válido por 1 semana"""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 
    
    class Config:
        case_sensitive = True


settings: Settings = Settings()
