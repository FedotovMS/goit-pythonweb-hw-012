import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from src.repository.users import UserRepository
from src.schemas.users import UserCreate
from src.entity.models import User


@pytest.mark.asyncio
async def test_get_by_email(override_get_db):
    # Create a user via the repository
    user_data = UserCreate(email="test@test.com", password="test445566")

    # Mock password hashing function during user creation
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Verify the created user's email
    assert created_user.email == "test@test.com"

    # Retrieve the user by email
    user = await UserRepository.get_by_email(override_get_db, "test@test.com")
    assert user is not None  # Ensure the user was found
    assert user.email == "test@test.com"

    # Attempt to retrieve a non-existent user
    non_user = await UserRepository.get_by_email(
        override_get_db, "nonexistent@test.com"
    )
    assert non_user is None  # No user should be returned


@pytest.mark.asyncio
async def test_create_user(override_get_db):
    # User data to create a new user
    user_data = UserCreate(email="test@test.com", password="test445566")

    # Mock password hashing during user creation
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        user = await UserRepository.create(override_get_db, user_data)

    # Verify the user was created and the password was hashed
    assert user is not None
    assert user.email == "test@test.com"
    assert user.hashed_password == "hashed_password"
    assert not user.is_verified  # By default, the user is not verified


@pytest.mark.asyncio
async def test_verify_token(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@test.com", password="test445566")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Mock token verification and simulate a valid token
    with patch("jose.jwt.decode", return_value={"sub": "test@test.com"}):
        user = await UserRepository.verify_token(override_get_db, "test_token")

    # Verify the user is returned and marked as verified
    assert user is not None
    assert user.email == "test@test.com"
    assert user.is_verified  # User should be marked as verified

    # Simulate an invalid token and verify that no user is returned
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        user = await UserRepository.verify_token(override_get_db, "invalid_token")

    assert user is None  # No user should be returned for an invalid token


@pytest.mark.asyncio
async def test_authenticate_user(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@test.com", password="test445566")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Verify the user (needed for authentication)
    with patch("jose.jwt.decode", return_value={"sub": "test@test.com"}):
        await UserRepository.verify_token(override_get_db, "test_token")

    # Mock password verification and simulate a successful authentication
    with patch("src.services.auth.verify_password", return_value=True):
        user = await UserRepository.authenticate_user(
            override_get_db, "test@test.com", "test445566"
        )

    assert user is not None
    assert user.email == "test@test.com"

    # Simulate incorrect password during authentication
    with patch("src.services.auth.verify_password", return_value=False):
        user = await UserRepository.authenticate_user(
            override_get_db, "test@test.com", "wrong_password"
        )

    assert user is None  # Should not authenticate with incorrect password

    # Attempt to authenticate a non-existent user
    user = await UserRepository.authenticate_user(
        override_get_db, "nonexistent@test.com", "test445566"
    )
    assert user is None  # No user should be returned for non-existent email


@pytest.mark.asyncio
async def test_update_avatar(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@test.com", password="test445566")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Update the user's avatar URL
    updated_user = await UserRepository.update_avatar(
        override_get_db, created_user, "https://test.com/avatar.jpg"
    )

    # Verify the avatar URL was updated correctly
    assert updated_user is not None
    assert updated_user.avatar_url == "https://test.com/avatar.jpg"


@pytest.mark.asyncio
async def test_create_password_reset_token(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@test.com", password="test445566")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Mock password reset token creation
    with patch("src.services.auth.create_access_token", return_value="reset_token"):
        token = await UserRepository.create_password_reset_token(
            override_get_db, "test@test.com"
        )

    assert token == "reset_token"  # Ensure the reset token was generated

    # Attempt to generate a reset token for a non-existent user
    token = await UserRepository.create_password_reset_token(
        override_get_db, "nonexistent@test.com"
    )
    assert token is None  # No token should be generated for a non-existent user


@pytest.mark.asyncio
async def test_reset_password(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@test.com", password="test445566")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Mock JWT decoding for a password reset token
    with patch(
        "jose.jwt.decode",
        return_value={"sub": "test@test.com", "type": "password_reset"},
    ):
        # Mock new password hashing during password reset
        with patch(
            "src.services.auth.get_password_hash", return_value="new_hashed_password"
        ):
            user = await UserRepository.reset_password(
                override_get_db, "reset_token", "new_password"
            )

    assert user is not None
    assert user.hashed_password == "new_hashed_password"  # New password should be hashed

    # Simulate an invalid token during password reset
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        user = await UserRepository.reset_password(
            override_get_db, "invalid_token", "new_password"
        )

    assert user is None  # Should not reset password with invalid token

    # Simulate a wrong token type (e.g., access token instead of password reset)
    with patch(
        "jose.jwt.decode", return_value={"sub": "test@test.com", "type": "access"}
    ):
        user = await UserRepository.reset_password(
            override_get_db, "wrong_type_token", "new_password"
        )

    assert user is None  # Should not reset password with wrong token type