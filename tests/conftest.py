from fastapi.testclient import TestClient
import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.database.db import get_db
from src.entity.models import Base
from main import app as app_instance

# Test database URL, specifically for testing
TEST_DB_URL = "postgresql+asyncpg://postgres:mypassword@localhost:5432/contacts_db"


# Fixture to override the default database dependency for testing
@pytest.fixture
def override_get_db():
    """
    Set up and tear down a test database for each test.
    
    This fixture creates a test database engine and session, runs migrations (drops and creates tables),
    and yields a session to be used in the test. It also handles cleaning up the test database
    after each test.
    """
    # Create a test engine with an asyncpg connection
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Set up the database (drop existing tables and create new ones)
    with engine.begin() as conn:
        conn.run_sync(Base.metadata.drop_all)  # Drop all existing tables
        conn.run_sync(Base.metadata.create_all)  # Create fresh tables

    # Create a session and yield it for the test
    with async_session() as session:
        yield session

    # Clean up the test database after the test is done
    with engine.begin() as conn:
        conn.run_sync(Base.metadata.drop_all)  # Drop tables again to clean up
    engine.dispose()  # Dispose of the engine


# Fixture for setting up the FastAPI app for tests
@pytest.fixture
def app():
    """
    Prepare the FastAPI app for testing by overriding the database dependency
    and setting up any necessary environment variables.
    """
    # Override the database dependency in the FastAPI app with the test DB session
    app_instance.dependency_overrides[get_db] = override_get_db

    # Configure Redis environment variables (mock or configure as needed)
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_PASSWORD"] = ""  # Empty password for test Redis

    # Yield the app instance for use in tests
    yield app_instance

    # Clear any dependency overrides after the test to avoid side effects
    app_instance.dependency_overrides.clear()


# Fixture to set up a sync client for testing the FastAPI app
@pytest.fixture
def client(app):
    """
    Set up a synchronous HTTP client to make requests to the FastAPI app.
    """
    # Initialize the test client with the FastAPI app
    with TestClient(app) as client:
        yield client