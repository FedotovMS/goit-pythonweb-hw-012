from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError

from src.entity.models import User
from src.schemas.users import UserCreate
from src.conf.config import settings
from src.utils.security import get_password_hash, verify_password  # Import security functions


class UserRepository:
    """Repository class for managing user data operations.

    Provides methods to interact with the user database, such as retrieving,
    creating, authenticating, and updating user data.
    """

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str):
        """Retrieve a user from the database by their email.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
            email (str): The email of the user to retrieve.

        Returns:
            User: The user object if found, or None if not found.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate):
        """Create a new user in the database.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
            user_data (UserCreate): The user data (email and password) for the new user.

        Returns:
            User: The created user object.
        """
        hashed_password = get_password_hash(user_data.password)  # Hash the user's password
        user = User(email=user_data.email, hashed_password=hashed_password)
        db.add(user)
        await db.commit()  # Commit the new user to the database
        await db.refresh(user)  # Refresh the user to get the latest state from the DB
        return user

    @staticmethod
    async def verify_token(db: AsyncSession, token: str):
        """Verify a JWT token and update the user's verification status if valid.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
            token (str): The JWT token to verify.

        Returns:
            User: The user object if the token is valid and user is updated, or None if invalid.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")  # Extract email from token
            if email is None:
                return None  # Return None if email is not found in the token
        except JWTError:
            return None  # Return None if the token is invalid

        # Retrieve the user by email and update their verification status
        user = await UserRepository.get_by_email(db, email)
        if user and not user.is_verified:  # Only update if user exists and is not already verified
            user.is_verified = True
            await db.commit()  # Commit the changes to the database
            await db.refresh(user)  # Refresh the user to get the latest state from the DB
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        """Authenticate a user by checking their email and password.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            User: The authenticated user if credentials are valid, or None if invalid.
        """
        user = await UserRepository.get_by_email(db, email)  # Get user by email
        if not user:
            return None  # Return None if the user does not exist

        if not verify_password(password, user.hashed_password):  # Verify the user's password
            return None  # Return None if the password is incorrect

        return user  # Return the authenticated user if everything is valid

    @staticmethod
    async def update_avatar(db: AsyncSession, user: User, avatar_url: str) -> User:
        """Update the avatar URL of a user.

        Args:
            db (AsyncSession): The SQLAlchemy async session.
            user (User): The user whose avatar is to be updated.
            avatar_url (str): The new avatar URL.

        Returns:
            User: The updated user object with the new avatar URL.
        """
        user.avatar_url = avatar_url  # Update the user's avatar URL
        db.add(user)  # Add the updated user to the session
        await db.commit()  # Commit the changes to the database
        await db.refresh(user)  # Refresh the user to get the latest state from the DB
        return user