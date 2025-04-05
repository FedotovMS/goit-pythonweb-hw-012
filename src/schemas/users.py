from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRole(str, Enum):
    """User role enumeration.

    This enumeration defines the possible roles a user can have in the system.
    Each role determines the user's access level and permissions within the system.
    """

    USER = "user"  # Regular user with standard permissions
    ADMIN = "admin"  # Administrator with elevated permissions


class UserCreate(BaseModel):
    """Schema for user registration and creation.

    This schema is used to validate data when creating a new user account.
    It includes the user's email, password, and role, with a default role set to "USER".

    Attributes:
        email (str): User's email address, used for authentication.
        password (str): User's plaintext password (will be hashed before storage).
        role (UserRole): User's role in the system. Defaults to "USER".
    """

    email: str
    """User's email address, required for registration and login."""

    password: str
    """User's plaintext password, which will be securely hashed before storage."""

    role: UserRole = UserRole.USER
    """User's role within the system. Default is "USER", which provides regular access."""


class UserResponse(BaseModel):
    """Schema for user data in API responses.

    This schema represents the user data that will be returned to clients after authentication.
    It includes essential information but excludes sensitive details such as the password.

    Attributes:
        id (int): Unique identifier for the user.
        email (str): User's email address.
        created_at (datetime): The timestamp when the user account was created.
        avatar_url (Optional[str]): URL to the user's profile image, if available.
        role (UserRole): The role assigned to the user (e.g., "USER" or "ADMIN").
    """

    id: int
    """Unique identifier for the user, typically used in internal systems."""

    email: str
    """User's email address, used for login and identification."""

    created_at: datetime
    """Timestamp of when the user account was created."""

    avatar_url: Optional[str] = None
    """URL to the user's avatar or profile image, if any."""

    role: UserRole
    """The role assigned to the user, which controls access to system features."""

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        """Allows the model to be populated from attributes, allowing more flexibility in data handling."""


class Token(BaseModel):
    """Schema for authentication token response.

    This schema is used when returning JWT tokens after successful user authentication.

    Attributes:
        access_token (str): The JWT access token, which is used for subsequent authentication requests.
        token_type (str): The type of token, typically "bearer".
    """

    access_token: str
    """The JWT access token used for authenticating API requests."""

    token_type: str
    """The type of token, typically "bearer" for authentication headers."""


class PasswordResetRequest(BaseModel):
    """Schema for password reset request.

    This schema is used when a user requests a password reset email by providing their registered email address.

    Attributes:
        email (EmailStr): The email address of the account to reset the password for.
    """

    email: EmailStr
    """The email address to which the password reset link will be sent."""


class PasswordReset(BaseModel):
    """Schema for password reset confirmation.

    This schema is used when a user submits a new password along with a reset token.
    It validates the token and the new password to update the account.

    Attributes:
        token (str): The password reset token received via email, used to authenticate the reset request.
        new_password (str): The new password to set for the account, must be at least 8 characters long.
    """

    token: str
    """The reset token that verifies the user's request to change their password."""

    new_password: str = Field(..., min_length=8)
    """The new password to set for the account, which must be at least 8 characters long."""