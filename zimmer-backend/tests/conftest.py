import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Import app + DB + deps (adjust paths if needed)
from main import app
from database import Base, get_db

# Use a fresh test database with all latest models
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_fresh.db")

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DB_URL, future=True)
    # Create fresh database with all latest models (includes health check columns)
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def client(db_session, monkeypatch):
    # Override DB dependency
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the main database get_db
    app.dependency_overrides[get_db] = _get_db
    
    # Override the users router get_db
    from routers.users import get_db as users_get_db
    app.dependency_overrides[users_get_db] = _get_db
    
    # Override the auth dependency get_db
    from utils.auth_dependency import get_db as auth_get_db
    app.dependency_overrides[auth_get_db] = _get_db

    # Override the auth utils get_db
    from utils.auth import get_db as auth_utils_get_db
    app.dependency_overrides[auth_utils_get_db] = _get_db
    
    # Also override the get_db function that's imported inside utils.auth
    # This is needed because utils.auth has its own local get_db function
    import utils.auth
    utils.auth.get_db = _get_db
    
    # Override the admin automation health router get_db
    from routers.admin_automation_health import get_db as admin_health_get_db
    app.dependency_overrides[admin_health_get_db] = _get_db

    # Override all other get_db functions to be safe
    from routers.knowledge import get_db as knowledge_get_db
    app.dependency_overrides[knowledge_get_db] = _get_db
    
    from routers.fallback import get_db as fallback_get_db
    app.dependency_overrides[fallback_get_db] = _get_db
    
    from routers.ticket_message import get_db as ticket_message_get_db
    app.dependency_overrides[ticket_message_get_db] = _get_db
    
    from routers.telegram import get_db as telegram_get_db
    app.dependency_overrides[telegram_get_db] = _get_db
    
    from routers.ticket import get_db as ticket_get_db
    app.dependency_overrides[ticket_get_db] = _get_db

    # Force sandbox payments (if your code reads this env/config)
    monkeypatch.setenv("PAYMENTS_MODE", "sandbox")

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
