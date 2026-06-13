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
    
    # JWT Auth Settings
    JWT_SECRET_KEY: str = "dev_secret_key_for_neurolens_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours

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

# Runtime security check for production environments
if settings.ENVIRONMENT == "production" or os.getenv("ENVIRONMENT") == "production":
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key or secret_key == "dev_secret_key_for_neurolens_2026":
        raise RuntimeError("PRODUCTION RUNTIME ERROR: JWT_SECRET_KEY environment variable must be configured in production!")

