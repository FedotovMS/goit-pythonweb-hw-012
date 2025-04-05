from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from src.entity.models import Contact
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


class ContactRepository:
    """Repository class for managing contact data.

    Provides CRUD operations and additional methods for searching
    and filtering contacts based on user needs.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a given database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for DB operations.
        """
        self.db = session

    async def create(self, contact: Contact):
        """Create and save a new contact to the database.

        Args:
            contact (Contact): Contact model instance to be created.

        Returns:
            Contact: The created contact with assigned ID and timestamps.
        """
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_all(self, user: UserResponse):
        """Retrieve all contacts belonging to a specific user.

        Args:
            user (UserResponse): The user for whom contacts are to be fetched.

        Returns:
            list[Contact]: A list of contacts associated with the given user.
        """
        result = await self.db.execute(
            select(Contact).where(Contact.user_id == user.id)
        )
        return result.scalars().all()

    async def get_by_id(self, contact_id: int, user: UserResponse):
        """Retrieve a specific contact by its ID for a given user.

        Args:
            contact_id (int): ID of the contact to fetch.
            user (UserResponse): The user who owns the contact.

        Returns:
            Contact: The contact object if found, or None if not found.
        """
        result = await self.db.execute(
            select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
        )
        return result.scalar_one_or_none()

    async def update(
        self, contact_id: int, updated_data: ContactCreate, user: UserResponse
    ):
        """Update an existing contact with new data.

        Args:
            contact_id (int): ID of the contact to update.
            updated_data (ContactCreate): New data to update the contact with.
            user (UserResponse): The user who owns the contact.

        Returns:
            Contact: The updated contact object or None if not found.
        """
        contact = await self.get_by_id(contact_id, user)
        if not contact:
            return None  # Return None if the contact doesn't exist

        # Update the contact fields with the provided data
        for key, value in updated_data.dict().items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int, user: UserResponse):
        """Delete a specific contact for a user.

        Args:
            contact_id (int): ID of the contact to delete.
            user (UserResponse): The user who owns the contact.

        Returns:
            Contact: The deleted contact if found, or None if not found.
        """
        contact = await self.get_by_id(contact_id, user)
        if not contact:
            return None  # Return None if the contact doesn't exist

        await self.db.delete(contact)
        await self.db.commit()
        return contact

    async def search_contacts(self, query: str, user: UserResponse):
        """Search for contacts by matching name or email.

        Args:
            query (str): Search term to match against contact first name,
                         last name, or email.
            user (UserResponse): The user who owns the contacts.

        Returns:
            list[Contact]: A list of contacts matching the search criteria.
        """
        stmt = select(Contact).where(
            Contact.user_id == user.id,
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            ),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_birthdays(self, user: UserResponse):
        """Get a list of contacts with birthdays within the next 7 days.

        Args:
            user (UserResponse): The user who owns the contacts.

        Returns:
            list[Contact]: A list of contacts whose birthdays are within the
                           next week.
        """
        today = datetime.today().date()  # Get the current date
        next_week = today + timedelta(days=7)  # Get the date 7 days from today

        stmt = select(Contact).where(
            Contact.user_id == user.id,
            and_(Contact.birth_date >= today, Contact.birth_date <= next_week),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()