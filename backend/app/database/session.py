from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine options
connect_args = {}
if settings.sqlalchemy_database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.sqlalchemy_database_url,
    pool_pre_ping=True,
    echo=False,
    connect_args=connect_args
)

# Create SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create engine options for admin/seeding tasks (uses settings.admin_database_url to bypass pooling issues)
admin_connect_args = {}
if settings.admin_database_url.startswith("sqlite"):
    admin_connect_args = {"check_same_thread": False}

admin_engine = create_engine(
    settings.admin_database_url,
    pool_pre_ping=True,
    echo=False,
    connect_args=admin_connect_args
)

AdminSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=admin_engine
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
