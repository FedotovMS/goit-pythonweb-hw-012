from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


class ContactService:
    """Service layer for managing contact operations.

    This service contains business logic and sits between the route handlers and the repository layer. 
    It handles all operations related to contacts such as creation, retrieval, updates, and deletion.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session.

        Args:
            db (AsyncSession): SQLAlchemy asynchronous database session for database interaction.
        """
        self.repository = ContactRepository(db)

    async def search_contacts(self, query: str, user: UserResponse):
        """Search for contacts by name or email.

        Args:
            query (str): The search string (name, email, or part of them).
            user (UserResponse): The currently authenticated user, used to filter contacts.

        Returns:
            list[Contact]: A list of contacts matching the search criteria.
        """
        return await self.repository.search_contacts(query, user)

    async def create_contact(self, contact_data: ContactCreate, user: UserResponse):
        """Create a new contact for the authenticated user.

        Args:
            contact_data (ContactCreate): Data required to create a new contact (name, email, etc.).
            user (UserResponse): The currently authenticated user, used to associate the contact with the user.

        Returns:
            Contact: The created contact instance.
        """
        # Map the contact data to a Contact model and associate it with the current user.
        new_contact = Contact(**contact_data.model_dump(), user_id=user.id)
        return await self.repository.create(new_contact)

    async def get_contacts(self, user: UserResponse):
        """Retrieve all contacts associated with a specific user.

        Args:
            user (UserResponse): The currently authenticated user, used to filter contacts by user ID.

        Returns:
            list[Contact]: A list of contacts associated with the user.
        """
        return await self.repository.get_all(user)

    async def get_contact(self, contact_id: int, user: UserResponse):
        """Retrieve a single contact by its ID.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (UserResponse): The currently authenticated user, used to check ownership of the contact.

        Returns:
            Contact: The contact matching the provided ID, or None if not found or not owned by the user.
        """
        return await self.repository.get_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, updated_data: ContactCreate, user: UserResponse
    ):
        """Update an existing contact.

        Args:
            contact_id (int): The ID of the contact to update.
            updated_data (ContactCreate): The updated contact data (e.g., new email, phone number).
            user (UserResponse): The currently authenticated user, used to ensure the contact belongs to the user.

        Returns:
            Contact: The updated contact instance, or None if the contact was not found or not owned by the user.
        """
        return await self.repository.update(contact_id, updated_data, user)

    async def delete_contact(self, contact_id: int, user: UserResponse):
        """Delete a contact.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (UserResponse): The currently authenticated user, used to ensure the contact belongs to the user.

        Returns:
            Contact: The deleted contact instance, or None if the contact was not found or not owned by the user.
        """
        return await self.repository.delete(contact_id, user)

    async def get_upcoming_birthdays(self, user: UserResponse):
        """Retrieve contacts with upcoming birthdays (within the next 7 days).

        Args:
            user (UserResponse): The currently authenticated user, used to filter contacts.

        Returns:
            list[Contact]: A list of contacts whose birthdays are within the next 7 days.
        """
        return await self.repository.get_upcoming_birthdays(user)