import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup mock database url env var before imports
os.environ["DATABASE_URL"] = "sqlite://"

from main import app
from app.database.session import Base, get_db
from app.database.seed import seed_db
from app.models.models import Parent, Child, parent_child_links
from app.api.dependencies import get_current_parent

# Create test engine using in-memory sqlite
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Seed domains and milestones
    db = TestingSessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_parent():
        parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
        if not parent:
            parent = Parent(
                first_name="Test",
                last_name="Parent",
                email="default.test.parent@example.com"
            )
            db.add(parent)
            db.commit()
            db.refresh(parent)
            
        # Ensure all children in the database are linked to this parent during testing
        # only if they don't have any parents associated yet.
        children = db.query(Child).all()
        for child in children:
            if len(child.parents) == 0:
                db.execute(
                    parent_child_links.insert().values(
                        parent_id=parent.id,
                        child_id=child.id,
                        relationship_type="parent"
                    )
                )
        db.commit()
        return parent
            
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_parent] = override_get_current_parent
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
