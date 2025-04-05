from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.contacts import ContactCreate, ContactResponse
from src.schemas.users import UserResponse
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Create a new contact.

    Creates a new contact entry in the database for the authenticated user.

    Args:
        contact (ContactCreate): Contact data to create, such as name, email, and birthday.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user, ensuring contacts are associated with the correct user.

    Returns:
        ContactResponse: The created contact object, including the contact details like name and email.
    """
    service = ContactService(db)
    return await service.create_contact(contact, current_user)


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve all contacts for the current user.

    Fetches and returns all contacts associated with the authenticated user.

    Args:
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        list[ContactResponse]: List of contacts that belong to the authenticated user.
    """
    service = ContactService(db)
    return await service.get_contacts(current_user)


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(
    query: str = Query(..., description="Search by name or email"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Search contacts by name or email.

    This endpoint allows searching for contacts based on a query string, which can match
    either the name or email of the contact.

    Args:
        query (str): Search string that will match against contact name or email.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        list[ContactResponse]: List of contacts whose name or email matches the search query.
    """
    service = ContactService(db)
    return await service.search_contacts(query, current_user)


@router.get("/birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve contacts with upcoming birthdays.

    Fetches contacts who have a birthday within the next 7 days, providing a useful feature
    to keep track of upcoming celebrations.

    Args:
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        list[ContactResponse]: List of contacts with birthdays within the next 7 days.
    """
    service = ContactService(db)
    return await service.get_upcoming_birthdays(current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve a single contact by ID.

    Fetches and returns a single contact entry for the authenticated user, based on the provided
    contact ID. If the contact doesn't exist, a 404 error is raised.

    Args:
        contact_id (int): The unique ID of the contact to retrieve.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        ContactResponse: The requested contact.

    Raises:
        HTTPException: 404 if the contact with the specified ID is not found.
    """
    service = ContactService(db)
    contact = await service.get_contact(contact_id, current_user)

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    updated_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Update an existing contact.

    This endpoint allows the authenticated user to update an existing contact by providing
    the contact ID and the new contact data.

    Args:
        contact_id (int): The ID of the contact to update.
        updated_data (ContactCreate): New contact information (name, email, etc.).
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        ContactResponse: The updated contact object with the new information.

    Raises:
        HTTPException: 404 if the contact to be updated doesn't exist.
    """
    service = ContactService(db)
    contact = await service.update_contact(contact_id, updated_data, current_user)

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Delete a contact.

    This endpoint allows the authenticated user to delete a contact by providing the contact ID.
    If the contact doesn't exist, a 404 error is returned.

    Args:
        contact_id (int): The unique ID of the contact to delete.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        None: No content on success, as the contact is removed from the system.

    Raises:
        HTTPException: 404 if the contact to be deleted doesn't exist.
    """
    service = ContactService(db)
    contact = await service.delete_contact(contact_id, current_user)

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return None