import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Neurolens API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres_secure_pass_123@localhost:5432/neurolens_db"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        # Quick fallback/check for postgres URL compatibility
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

# Load settings singleton
settings = Settings()
