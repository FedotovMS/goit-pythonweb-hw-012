import asyncio
import os
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.database.db import get_db
from src.entity.models import Base
from src.conf.config import settings
from main import app as app_instance

# Test database URL, specifically for testing
TEST_DB_URL = "postgresql+asyncpg://postgres:mypassword@localhost:5432/test_contacts_db"


# Fixture to override the default database dependency for testing
@pytest_asyncio.fixture
async def override_get_db():
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop all existing tables
        await conn.run_sync(Base.metadata.create_all)  # Create fresh tables

    # Create a session and yield it for the test
    async with async_session() as session:
        yield session

    # Clean up the test database after the test is done
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop tables again to clean up
    await engine.dispose()  # Dispose of the engine


# Fixture for setting up the FastAPI app for tests
@pytest_asyncio.fixture
async def app():
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

    # Optionally mock external services (e.g., email, SMS) here if necessary
    # ...

    # Yield the app instance for use in tests
    yield app_instance

    # Clear any dependency overrides after the test to avoid side effects
    app_instance.dependency_overrides.clear()


# Fixture to set up an async client for testing the FastAPI app
@pytest_asyncio.fixture
async def async_client(app):
    """
    Set up an asynchronous HTTP client to make requests to the FastAPI app.
    """
    # Initialize the async client with the FastAPI app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Mock user data fixture for testing user-related functionality
@pytest.fixture
def test_user():
    """
    Provide a mock user object for testing purposes.
    """
    return {"email": "test@example.com", "password": "password123"}


# Mock contact data fixture for testing contact-related functionality
@pytest.fixture
def test_contact():
    """
    Provide a mock contact object for testing purposes.
    """
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "birth_date": "2000-01-01T00:00:00Z",
        "additional_info": "Test contact",
    }


# Mock admin user data fixture for testing admin-related functionality
@pytest.fixture
def test_admin():
    """
    Provide a mock admin user object for testing purposes.
    """
    return {"email": "admin@example.com", "password": "adminpassword", "role": "admin"}


# Fixture to mock JWT token decoding for authentication tests
@pytest.fixture
def mock_jwt(monkeypatch):
    """
    Mock the JWT decoding function to simulate authentication without needing actual tokens.
    """
    def mock_decode(*args, **kwargs):
        # Mock the decoded JWT payload
        return {"sub": "test@example.com", "type": "access"}

    # Patch the 'decode' method from the JWT library with our mock function
    monkeypatch.setattr("jose.jwt.decode", mock_decode)

    # Return a mocked token for use in tests
    return "test_token"


# Mock Redis fixture to simulate interactions with a Redis cache
@pytest_asyncio.fixture
async def mock_redis_cache(monkeypatch):
    """
    Mock Redis cache interactions for testing purposes without requiring a real Redis instance.
    """
    class MockRedisCache:
        async def get_user_data(self, email):
            # Return mock user data based on the email
            if email == "test@example.com":
                return {
                    "id": 1,
                    "email": "test@example.com",
                    "created_at": "2023-01-01T00:00:00",
                    "avatar_url": None,
                    "role": "user",
                }
            return None

        async def set_user_data(self, email, data, expiry=None):
            # Simulate storing data in the cache (returns True for success)
            return True

        async def invalidate_user_data(self, email):
            # Simulate invalidating cache data for the user
            return True

    # Patch the Redis cache with our mock class
    monkeypatch.setattr("src.conf.redis.user_cache", MockRedisCache())