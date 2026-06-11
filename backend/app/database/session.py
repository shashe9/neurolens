from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine
engine = create_engine(
    settings.sqlalchemy_database_url,
    pool_pre_ping=True,
    echo=False
)

# Create SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative Base
Base = declarative_base()

# Dependency for route request lifecycles
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
