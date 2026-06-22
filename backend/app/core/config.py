import os
import json
from typing import Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_current_file = Path(__file__).resolve()
BACKEND_DIR = _current_file.parents[2] # backend/
_repo_root_dir = _current_file.parents[3] # repo root

_backend_env = BACKEND_DIR / ".env"
_repo_env = _repo_root_dir / ".env"

if _backend_env.exists():
    RESOLVED_BACKEND_ENV_FILE = str(_backend_env)
else:
    RESOLVED_BACKEND_ENV_FILE = str(_repo_env)


def normalized_database_url(url: str, strip_pgbouncer: bool = False) -> str:
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if strip_pgbouncer and not url.startswith("sqlite") and "pgbouncer" in url.lower():
        from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
        try:
            parsed = urlparse(url)
            queries = parse_qsl(parsed.query)
            filtered_queries = [(k, v) for k, v in queries if k.lower() != 'pgbouncer']
            new_query = urlencode(filtered_queries)
            new_parsed = parsed._replace(query=new_query)
            url = urlunparse(new_parsed)
        except Exception:
            if "?pgbouncer=true" in url:
                url = url.replace("?pgbouncer=true", "")
            elif "&pgbouncer=true" in url:
                url = url.replace("&pgbouncer=true", "")
    return url


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Neurolens API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Debug info
    resolved_backend_env_file: str = RESOLVED_BACKEND_ENV_FILE
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres_secure_pass_123@localhost:5432/neurolens_db"

    DIRECT_URL: Optional[str] = None
    
    # JWT Auth Settings
    JWT_SECRET_KEY: str = "dev_secret_key_for_neurolens_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Frontend settings
    FRONTEND_URL: Optional[str] = None
    
    # Seeding behaviour
    SEED_ON_STARTUP: bool = False

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: any) -> List[str]:
        if isinstance(v, str):
            if not v:
                return []
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            # Split comma separated string
            return [i.strip() for i in v_stripped.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return [str(i) for i in v]
        return []
    
    # Determine backend directory path relative to config.py
    # backend/app/core/config.py -> 3 levels up is backend/
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    

    

    model_config = SettingsConfigDict(
        env_file=RESOLVED_BACKEND_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalized_database_url(self.DATABASE_URL, strip_pgbouncer=True)

    @property
    def alembic_database_url(self) -> str:
        url = self.DIRECT_URL or self.DATABASE_URL
        return normalized_database_url(url, strip_pgbouncer=True)

    @property
    def admin_database_url(self) -> str:
        url = self.DIRECT_URL or self.DATABASE_URL
        return normalized_database_url(url, strip_pgbouncer=True)

# Load settings singleton
settings = Settings()

# Runtime security check for production environments
if settings.ENVIRONMENT == "production":
    secret_key = settings.JWT_SECRET_KEY
    if not secret_key or secret_key == "dev_secret_key_for_neurolens_2026":
        raise RuntimeError("PRODUCTION RUNTIME ERROR: JWT_SECRET_KEY environment variable must be configured in production!")


