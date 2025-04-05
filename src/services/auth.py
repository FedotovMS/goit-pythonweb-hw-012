from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.redis import user_cache
from src.database.db import get_db
from src.schemas.users import UserResponse, UserRole
from src.repository.users import UserRepository
from src.conf.config import settings

# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# JWT token configuration
SECRET_KEY = settings.SECRET_KEY  # The secret key loaded from environment settings (.env file)
ALGORITHM = "HS256"  # Algorithm used for signing the JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password (str): Plain text password.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password (str): Plain text password to verify.
        hashed_password (str): Hashed password from the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data (dict): Token payload data (e.g., user information).
        expires_delta (Optional[timedelta], optional): Custom expiration time for the token. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})  # Set expiration time
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get the current authenticated user from the JWT token.

    This function first attempts to retrieve the user from the Redis cache, 
    and if not found, it falls back to querying the database.

    Args:
        token (str, optional): JWT token obtained from the Authorization header.
        db (AsyncSession, optional): Database session.

    Returns:
        UserResponse: The current authenticated user.

    Raises:
        HTTPException: 401 if the token is invalid or if the user cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token to extract payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type", "access")  # Default to "access" token type

        if email is None:
            raise credentials_exception  # Raise exception if the email is not found in the token

        # Ensure we're not using a password reset token for authentication
        if token_type == "password_reset":
            raise credentials_exception

    except JWTError:
        raise credentials_exception  # Raise exception if JWT decoding fails

    # Try to get the user from Redis cache
    cached_user = await user_cache.get_user_data(email)

    if cached_user:
        # Return cached user data as a UserResponse model
        return UserResponse(**cached_user)

    # If user is not in cache, fetch from the database
    user = await UserRepository.get_by_email(db, email)
    if user is None:
        raise credentials_exception  # Raise exception if user is not found in the database

    # Cache the user data for future requests
    user_data = {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "avatar_url": user.avatar_url,
        "role": user.role,
    }
    await user_cache.set_user_data(email, user_data)  # Store user data in cache

    return user


# Function to check user roles and enforce access control
def RoleChecker(allowed_roles: list[UserRole]):
    """Generate a dependency function that checks if the current user has an allowed role.

    Args:
        allowed_roles (list[UserRole]): List of roles allowed to access a particular resource.

    Returns:
        check_role: A function that checks the current user's role.
    """
    async def check_role(
        current_user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:
        # Check if the user's role is in the list of allowed roles
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",  # If the role is not allowed, raise an error
            )
        return current_user

    return check_role


# Predefined role check for admin users only
admin_only = RoleChecker([UserRole.ADMIN])  # Restrict access to admin users