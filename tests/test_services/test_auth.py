import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from src.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)


def test_get_password_hash():
    """
    Test that password hashing works correctly.
    Ensures that the password is hashed and does not match the original string.
    """
    hashed = get_password_hash("password123")
    # Ensure the hashed password is different from the original password
    assert hashed != "password123"
    # Ensure the hash is a string
    assert isinstance(hashed, str)
    # Check that the hash length is greater than 20 characters (bcrypt hashes are typically long)
    assert len(hashed) > 20


def test_verify_password():
    """
    Test the password verification process.
    Ensures that the correct password can be verified and an incorrect one cannot.
    """
    hashed = get_password_hash("password123")
    # Verify correct password
    assert verify_password("password123", hashed)
    # Verify incorrect password
    assert not verify_password("wrong_password", hashed)


def test_create_access_token():
    """
    Test creation of access tokens.
    Ensures that tokens are created properly and supports expiry times.
    """
    token = create_access_token({"sub": "test@test.com"})
    # Check if token is a string
    assert isinstance(token, str)

    # Test token creation with a custom expiry time
    token = create_access_token({"sub": "test@test.com"}, timedelta(minutes=30))
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_get_current_user(override_get_db, mock_jwt, mock_redis_cache):
    """
    Test the retrieval of the current user based on a JWT token.
    Ensures that:
    - A valid token returns the correct user.
    - Invalid tokens, missing subjects, or incorrect token types raise errors.
    - A non-existent user raises a 401 error.
    """
    # Mock jwt.decode to return a valid payload for a user
    with patch(
        "jose.jwt.decode", return_value={"sub": "test@test.com", "type": "access"}
    ):
        # Create a user mock to return from the database
        from src.entity.models import User

        user = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Mock UserRepository.get_by_email to return the mock user
        with patch(
            "src.repository.users.UserRepository.get_by_email", return_value=user
        ):
            current_user = await get_current_user(mock_jwt, override_get_db)

    # Ensure the returned user is not None and email matches
    assert current_user is not None
    assert current_user.email == "test@test.com"

    # Test with invalid token, should raise HTTP 401 error
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", override_get_db)

    # Ensure the error status code is 401
    assert exc_info.value.status_code == 401

    # Test with missing subject in the decoded token, should raise HTTP 401 error
    with patch("jose.jwt.decode", return_value={"type": "access"}):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_jwt, override_get_db)

    assert exc_info.value.status_code == 401

    # Test with incorrect token type (e.g., "password_reset" instead of "access"), should raise HTTP 401 error
    with patch(
        "jose.jwt.decode",
        return_value={"sub": "test@test.com", "type": "password_reset"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_jwt, override_get_db)

    assert exc_info.value.status_code == 401

    # Test with a non-existent user, should raise HTTP 401 error
    with patch(
        "jose.jwt.decode", return_value={"sub": "test@test.com", "type": "access"}
    ):
        with patch(
            "src.repository.users.UserRepository.get_by_email", return_value=None
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_jwt, override_get_db)

    assert exc_info.value.status_code == 401