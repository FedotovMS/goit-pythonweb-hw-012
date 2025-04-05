import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy import select

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse
from src.entity.models import Contact, User


@pytest.mark.asyncio
async def test_create_contact(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact for the user
    contact = Contact(
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        phone_number="0671234567",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    # Use the repository to create the contact
    repo = ContactRepository(override_get_db)
    result = await repo.create(contact)

    assert result is not None
    assert result.first_name == "ivan"
    assert result.last_name == "ivanov"
    assert result.email == "ivan.ivanov@test.com"
    assert result.user_id == user.id


@pytest.mark.asyncio
async def test_get_all_contacts(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create multiple contacts for the user
    contacts = [
        Contact(
            first_name="ivan",
            last_name="ivanov",
            email="ivan.ivanov@test.com",
            phone_number="0671234567",
            birth_date=datetime.now(),
            additional_info="Test contact 1",
            user_id=user.id,
        ),
        Contact(
            first_name="petr",
            last_name="petrov",
            email="petr.petrov@test.com",
            phone_number="0677654321",
            birth_date=datetime.now(),
            additional_info="Test contact 2",
            user_id=user.id,
        ),
    ]

    # Add the contacts to the database
    for contact in contacts:
        override_get_db.add(contact)

    await override_get_db.commit()

    # Use the repository to get all contacts for the user
    repo = ContactRepository(override_get_db)
    results = await repo.get_all(user_response)

    assert results is not None
    assert len(results) == 2
    emails = [c.email for c in results]
    assert "ivan.ivanov@test.com" in emails
    assert "petr.petrov@test.com" in emails


@pytest.mark.asyncio
async def test_get_by_id(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact for the user
    contact = Contact(
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        phone_number="0671234567",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    override_get_db.add(contact)
    await override_get_db.commit()
    await override_get_db.refresh(contact)

    # Use the repository to get the contact by ID
    repo = ContactRepository(override_get_db)
    result = await repo.get_by_id(contact.id, user_response)

    assert result is not None
    assert result.id == contact.id
    assert result.first_name == "ivan"
    assert result.email == "ivan.ivanov@test.com"

    # Test get_by_id with non-existent ID
    non_existent = await repo.get_by_id(9999, user_response)
    assert non_existent is None

    # Test get_by_id with wrong user
    other_user = UserResponse(
        id=user.id + 1, email="other@test.com", created_at=datetime.now()
    )

    other_result = await repo.get_by_id(contact.id, other_user)
    assert other_result is None


@pytest.mark.asyncio
async def test_update_contact(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact for the user
    contact = Contact(
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        phone_number="0671234567",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    override_get_db.add(contact)
    await override_get_db.commit()
    await override_get_db.refresh(contact)

    # Update data for the contact
    updated_data = ContactCreate(
        first_name="ivan-Updated",
        last_name="ivanov-Updated",
        email="updated@test.com",
        phone_number="1111111111",
        birth_date=datetime.now(),
        additional_info="Updated info",
    )

    # Use the repository to update the contact
    repo = ContactRepository(override_get_db)
    result = await repo.update(contact.id, updated_data, user_response)

    assert result is not None
    assert result.first_name == "ivan-Updated"
    assert result.last_name == "ivanov-Updated"
    assert result.email == "updated@test.com"
    assert result.phone_number == "1111111111"

    # Test update with non-existent ID
    non_existent = await repo.update(9999, updated_data, user_response)
    assert non_existent is None

    # Test update with wrong user
    other_user = UserResponse(
        id=user.id + 1, email="other@test.com", created_at=datetime.now()
    )

    other_result = await repo.update(contact.id, updated_data, other_user)
    assert other_result is None


@pytest.mark.asyncio
async def test_delete_contact(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact for the user
    contact = Contact(
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        phone_number="0671234567",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    override_get_db.add(contact)
    await override_get_db.commit()
    await override_get_db.refresh(contact)

    # Use the repository to delete the contact
    repo = ContactRepository(override_get_db)
    result = await repo.delete(contact.id, user_response)

    assert result is not None
    assert result.id == contact.id
    assert result.first_name == "ivan"

    # Verify contact is deleted
    stmt = select(Contact).where(Contact.id == contact.id)
    query_result = await override_get_db.execute(stmt)
    deleted_contact = query_result.scalar_one_or_none()
    assert deleted_contact is None

    # Test delete with non-existent ID
    non_existent = await repo.delete(9999, user_response)
    assert non_existent is None

    # Test delete with wrong user
    # Create another contact for the user
    another_contact = Contact(
        first_name="petr",
        last_name="petrov",
        email="petr.petrov@test.com",
        phone_number="0677654321",
        birth_date=datetime.now(),
        additional_info="Test contact 2",
        user_id=user.id,
    )

    override_get_db.add(another_contact)
    await override_get_db.commit()
    await override_get_db.refresh(another_contact)

    other_user = UserResponse(
        id=user.id + 1, email="other@test.com", created_at=datetime.now()
    )

    other_result = await repo.delete(another_contact.id, other_user)
    assert other_result is None


@pytest.mark.asyncio
async def test_search_contacts(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create multiple contacts for the user with different names
    contacts = [
        Contact(
            first_name="ivan",
            last_name="ivanov",
            email="ivan.ivanov@test.com",
            phone_number="0671234567",
            birth_date=datetime.now(),
            additional_info="Test contact 1",
            user_id=user.id,
        ),
        Contact(
            first_name="petr",
            last_name="petrov",
            email="petr.petrov@test.com",
            phone_number="0677654321",
            birth_date=datetime.now(),
            additional_info="Test contact 2",
            user_id=user.id,
        ),
        Contact(
            first_name="john",
            last_name="smith",
            email="john.smith@test.com",
            phone_number="2222222222",
            birth_date=datetime.now(),
            additional_info="Test contact 3",
            user_id=user.id,
        ),
    ]

    # Add contacts to the database
    for contact in contacts:
        override_get_db.add(contact)

    await override_get_db.commit()

    # Use the repository to search contacts by first name, last name, and email
    repo = ContactRepository(override_get_db)

    # Search by first name
    results_first_name = await repo.search_contacts("ivan", user_response)
    assert len(results_first_name) == 1
    assert results_first_name[0].first_name == "ivan"

    # Search by last name
    results_last_name = await repo.search_contacts("petrov", user_response)
    assert len(results_last_name) == 1
    assert results_last_name[0].last_name == "petrov"

    # Search by email
    results_email = await repo.search_contacts("john", user_response)
    assert len(results_email) == 1
    assert results_email[0].first_name == "john"

    # Search with no results
    no_results = await repo.search_contacts("XYZ", user_response)
    assert len(no_results) == 0

    # Create a contact for another user
    another_user = User(
        email="another@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(another_user)
    await override_get_db.commit()
    await override_get_db.refresh(another_user)

    another_contact = Contact(
        first_name="kate",
        last_name="Mate",
        email="kate.Mate@test.com",
        phone_number="0123456789",
        birth_date=datetime.now(),
        additional_info="Another user's contact",
        user_id=another_user.id,
    )

    override_get_db.add(another_contact)
    await override_get_db.commit()

    # Search should not return another user's contacts
    results_with_other_user = await repo.search_contacts("kate", user_response)
    assert len(results_with_other_user) == 0


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(override_get_db):
    # Create a test user first
    user = User(
        email="test@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Get the current date and other dates for testing
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    last_week = today - timedelta(days=7)

    # Create contacts with different birthdays
    contacts = [
        Contact(
            first_name="Today",
            last_name="Birthday",
            email="today@test.com",
            phone_number="1111111111",
            birth_date=today,
            additional_info="Birthday today",
            user_id=user.id,
        ),
        Contact(
            first_name="Tomorrow",
            last_name="Birthday",
            email="tomorrow@test.com",
            phone_number="2222222222",
            birth_date=tomorrow,
            additional_info="Birthday tomorrow",
            user_id=user.id,
        ),
        Contact(
            first_name="NextWeek",
            last_name="Birthday",
            email="nextweek@test.com",
            phone_number="3333333333",
            birth_date=next_week,
            additional_info="Birthday next week",
            user_id=user.id,
        ),
        Contact(
            first_name="LastWeek",
            last_name="Birthday",
            email="lastweek@test.com",
            phone_number="4444444444",
            birth_date=last_week,
            additional_info="Birthday last week",
            user_id=user.id,
        ),
    ]

    # Add contacts to the database
    for contact in contacts:
        override_get_db.add(contact)

    await override_get_db.commit()

    # Use the repository to get upcoming birthdays
    repo = ContactRepository(override_get_db)
    results = await repo.get_upcoming_birthdays(user_response)

    # Should include today, tomorrow, and next week birthdays
    assert len(results) >= 2  # At least today and tomorrow

    # Create a contact for another user with birthday today
    another_user = User(
        email="another@test.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(another_user)
    await override_get_db.commit()
    await override_get_db.refresh(another_user)

    another_contact = Contact(
        first_name="Another",
        last_name="Birthday",
        email="another@test.com",
        phone_number="1111111111",
        birth_date=today,
        additional_info="Another user's birthday",
        user_id=another_user.id,
    )

    override_get_db.add(another_contact)
    await override_get_db.commit()

    # Results should not include another user's contact
    another_user_response = UserResponse(
        id=another_user.id, email=another_user.email, created_at=another_user.created_at
    )

    results_for_first_user = await repo.get_upcoming_birthdays(user_response)
    results_for_another_user = await repo.get_upcoming_birthdays(another_user_response)

    # The first user should not see another user's birthdays
    assert len(results_for_another_user) == 1
    assert results_for_another_user[0].first_name == "Another"

    # First user's results should not include "Another"
    assert all(contact.first_name != "Another" for contact in results_for_first_user)