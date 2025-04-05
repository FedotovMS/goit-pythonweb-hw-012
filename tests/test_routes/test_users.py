import pytest
from unittest.mock import AsyncMock, patch
from jose import jwt
from datetime import datetime


@pytest.mark.asyncio
async def test_register_user(async_client, test_user):
    """
    Test user registration. Ensures that:
    - A user is successfully registered.
    - A verification email is sent.
    """
    # Mock email sending to avoid actual email dispatch
    with patch(
        "src.conf.email.send_verification_email", new_callable=AsyncMock
    ) as mock_send_email:
        # Send a POST request to register the user
        response = await async_client.post("/users/register", json=test_user)

    # Check if the registration was successful
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "password" not in data  # Ensure password is not returned in the response
    mock_send_email.assert_called_once()  # Ensure the email verification was sent


@pytest.mark.asyncio
async def test_register_existing_user(async_client, test_user):
    """
    Test attempting to register an already existing user. Ensures:
    - The system responds with a conflict (409) when trying to register a user that already exists.
    """
    # Register a user
    await async_client.post("/users/register", json=test_user)

    # Try to register the same user again and check for conflict
    response = await async_client.post("/users/register", json=test_user)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_user(async_client, test_user):
    """
    Test user login. Ensures:
    - User can log in after successful registration and verification.
    - A valid access token is returned.
    """
    # Register and verify a user
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Mock verify_token to return a verified user
    with patch(
        "src.repository.users.UserRepository.verify_token", new_callable=AsyncMock
    ) as mock_verify:
        from src.entity.models import User

        # Mock a verified user
        user_mock = User(
            id=1,
            email=test_user["email"],
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )
        mock_verify.return_value = user_mock

        # Simulate user verification
        await async_client.get("/users/verify?token=test_token")

    # Test login with the registered user
    response = await async_client.post("/users/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data  # Ensure access token is included in the response
    assert data["token_type"] == "bearer"  # Ensure the token type is 'bearer'


@pytest.mark.asyncio
async def test_login_unverified_user(async_client, test_user):
    """
    Test login attempt by an unverified user. Ensures:
    - The system responds with a 403 Forbidden error if the user is not verified.
    """
    # Register a user without verifying the email
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Try to login without verification
    response = await async_client.post("/users/login", json=test_user)
    assert response.status_code == 403  # Forbidden due to unverified email


@pytest.mark.asyncio
async def test_get_current_user(async_client, mock_jwt, mock_redis_cache):
    """
    Test fetching the current authenticated user. Ensures:
    - The correct user data is returned when a valid JWT is provided in the authorization header.
    """
    # Set auth header with mock token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Send a GET request to fetch current user info
    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"  # Ensure correct email is returned


@pytest.mark.asyncio
async def test_password_reset_request(async_client, test_user):
    """
    Test the password reset request. Ensures:
    - A password reset email is sent when a valid email is provided.
    """
    # Register a user
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Mock password reset email sending
    with patch(
        "src.conf.email.send_password_reset_email", new_callable=AsyncMock
    ) as mock_send:
        # Send a POST request to request password reset
        response = await async_client.post(
            "/users/password-reset-request", json={"email": test_user["email"]}
        )

    # Check if the request was successful and the email was sent
    assert response.status_code == 200
    assert "message" in response.json()  # Ensure the response contains a message
    mock_send.assert_called_once()  # Ensure the password reset email was sent


@pytest.mark.asyncio
async def test_reset_password(async_client, test_user):
    """
    Test password reset functionality. Ensures:
    - The user's password is reset successfully when a valid token and new password are provided.
    """
    # Register a user
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Mock reset_password to return a user with a new password
    with patch(
        "src.repository.users.UserRepository.reset_password", new_callable=AsyncMock
    ) as mock_reset:
        from src.entity.models import User

        # Simulate resetting the password
        mock_reset.return_value = User(
            id=1,
            email=test_user["email"],
            hashed_password="new_hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Send a POST request to reset the password
        response = await async_client.post(
            "/users/reset-password",
            json={"token": "test_token", "new_password": "new_password123"},
        )

    # Check if the password reset was successful
    assert response.status_code == 200
    assert "message" in response.json()  # Ensure the response contains a success message