from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# src/schemas/contacts.py

class ContactCreate(BaseModel):
    """Schema for creating or updating a contact.

    This schema validates the input data for creating or updating a contact record.
    It ensures that the contact's first and last names, email, phone number, 
    birth date, and optional additional information meet the required criteria.
    """

    first_name: str = Field(..., min_length=1, max_length=100)
    """First name of the contact, must be between 1 and 100 characters."""

    last_name: str = Field(..., min_length=1, max_length=100)
    """Last name of the contact, must be between 1 and 100 characters."""

    email: EmailStr
    """Email address of the contact, validated as an email format."""

    phone_number: str = Field(..., min_length=5, max_length=20)
    """Phone number of the contact, must be between 5 and 20 characters."""

    birth_date: datetime
    """Birth date of the contact, must be a valid datetime object."""

    additional_info: Optional[str] = None
    """Optional field for additional information about the contact, like notes or tags."""

class ContactResponse(ContactCreate):
    """Schema for contact data in API responses.

    This schema is used to structure the data of a contact in API responses.
    It extends the ContactCreate schema by including additional fields such as 
    the contact's unique ID, user ID, and timestamps for creation and last update.
    """

    id: int
    """Unique identifier for the contact record."""

    user_id: int
    """ID of the user who owns the contact record."""

    created_at: datetime
    """Timestamp of when the contact was created."""

    updated_at: datetime
    """Timestamp of the last update to the contact record."""

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        """Allow the model to be populated from attributes rather than just dictionaries."""