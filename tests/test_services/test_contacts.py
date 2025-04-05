import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.contacts import ContactService
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


@pytest.mark.asyncio
async def test_create_contact(override_get_db):
    """
    Test the creation of a new contact.
    Ensures that the service correctly creates a contact, and the repository method is called once.
    """
    # Create a mock repository and simulate contact creation
    mock_repo = AsyncMock()
    mock_repo.create.return_value = MagicMock(
        id=1,
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Data to create a contact
        contact_data = ContactCreate(
            first_name="ivan",
            last_name="ivanov",
            email="ivan.ivanov@test.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Test contact",
        )

        # Create the contact
        result = await service.create_contact(contact_data, user)

    # Assertions to verify that the result matches expectations
    assert result is not None
    assert result.first_name == "ivan"
    assert result.last_name == "ivanov"
    assert result.email == "ivan.ivanov@test.com"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_contacts(override_get_db):
    """
    Test retrieving a list of contacts for a user.
    Ensures that the service returns the correct contacts and calls the repository's get_all method.
    """
    # Mock list of contacts
    mock_contacts = [
        MagicMock(
            id=1,
            first_name="ivan",
            last_name="ivanov",
            email="ivan.ivanov@test.com",
            phone_number="0671234567",
            birth_date=datetime.now(),
            additional_info="Test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        MagicMock(
            id=2,
            first_name="petr",
            last_name="petrov",
            email="petr.petrov@test.com",
            phone_number="0677654321",
            birth_date=datetime.now(),
            additional_info="Another test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    # Create a mock repository and simulate fetching contacts
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = mock_contacts

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Get all contacts
        result = await service.get_contacts(user)

    # Assertions to verify the correct contacts are returned
    assert result is not None
    assert len(result) == 2
    assert result[0].first_name == "ivan"
    assert result[1].first_name == "petr"
    mock_repo.get_all.assert_called_once_with(user)


@pytest.mark.asyncio
async def test_get_contact(override_get_db):
    """
    Test retrieving a single contact by ID.
    Ensures that the service returns the correct contact based on the given ID and calls the repository's get_by_id method.
    """
    # Mock a single contact
    mock_contact = MagicMock(
        id=1,
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create a mock repository and simulate fetching a contact by ID
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = mock_contact

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Get the contact by ID
        result = await service.get_contact(1, user)

    # Assertions to verify the result matches the expected contact
    assert result is not None
    assert result.id == 1
    assert result.first_name == "ivan"
    assert result.email == "ivan.ivanov@test.com"
    mock_repo.get_by_id.assert_called_once_with(1, user)


@pytest.mark.asyncio
async def test_update_contact(override_get_db):
    """
    Test updating a contact.
    Ensures that the service correctly updates the contact and calls the repository's update method.
    """
    # Mock updated contact data
    mock_updated_contact = MagicMock(
        id=1,
        first_name="ivan-Updated",
        last_name="ivanov-Updated",
        email="ivan.updated@test.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Updated test contact",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create a mock repository and simulate updating a contact
    mock_repo = AsyncMock()
    mock_repo.update.return_value = mock_updated_contact

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Data to update the contact
        updated_data = ContactCreate(
            first_name="ivan-Updated",
            last_name="ivanov-Updated",
            email="ivan.updated@test.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Updated test contact",
        )

        # Update the contact
        result = await service.update_contact(1, updated_data, user)

    # Assertions to verify the updated contact
    assert result is not None
    assert result.first_name == "ivan-Updated"
    assert result.last_name == "ivanov-Updated"
    assert result.email == "ivan.updated@test.com"
    mock_repo.update.assert_called_once_with(1, updated_data, user)


@pytest.mark.asyncio
async def test_delete_contact(override_get_db):
    """
    Test deleting a contact.
    Ensures that the service correctly deletes the contact and calls the repository's delete method.
    """
    # Mock the contact to delete
    mock_deleted_contact = MagicMock(
        id=1,
        first_name="ivan",
        last_name="ivanov",
        email="ivan.ivanov@test.com",
        user_id=1,
    )

    # Create a mock repository and simulate deleting a contact
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = mock_deleted_contact

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Delete the contact by ID
        result = await service.delete_contact(1, user)

    # Assertions to verify the deleted contact
    assert result is not None
    assert result.id == 1
    assert result.first_name == "ivan"
    mock_repo.delete.assert_called_once_with(1, user)


@pytest.mark.asyncio
async def test_search_contacts(override_get_db):
    """
    Test searching for contacts by a query string.
    Ensures that the service correctly filters and returns contacts that match the search term.
    """
    # Create mock search results
    mock_results = [
        MagicMock(
            id=1,
            first_name="ivan",
            last_name="ivanov",
            email="ivan.ivanov@test.com",
            phone_number="0671234567",
            birth_date=datetime.now(),
            additional_info="Test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    ]

    # Create a mock repository and simulate search results
    mock_repo = AsyncMock()
    mock_repo.search_contacts.return_value = mock_results

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Search for contacts with the term "ivanov"
        result = await service.search_contacts("ivanov", user)

    # Assertions to verify the search results
    assert result is not None
    assert len(result) == 1
    assert result[0].last_name == "ivanov"
    mock_repo.search_contacts.assert_called_once_with("ivanov", user)


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(override_get_db):
    """
    Test retrieving contacts with upcoming birthdays.
    Ensures that the service returns contacts whose birthdays are soon and calls the repository's get_upcoming_birthdays method.
    """
    # Create mock upcoming birthdays
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    mock_birthdays = [
        MagicMock(
            id=1,
            first_name="ivan",
            last_name="ivanov",
            email="ivan.ivanov@test.com",
            phone_number="0671234567",
            birth_date=today,
            additional_info="Test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        MagicMock(
            id=2,
            first_name="petr",
            last_name="petrov",
            email="petr.petrov@test.com",
            phone_number="0677654321",
            birth_date=tomorrow,
            additional_info="Another test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    # Create a mock repository and simulate fetching upcoming birthdays
    mock_repo = AsyncMock()
    mock_repo.get_upcoming_birthdays.return_value = mock_birthdays

    # Mock user data
    user = UserResponse(
        id=1, email="test@test.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repository
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Get upcoming birthdays
        result = await service.get_upcoming_birthdays(user)

    # Assertions to verify upcoming birthdays
    assert result is not None
    assert len(result) == 2
    assert result[0].first_name == "ivan"
    assert result[1].first_name == "petr"
    mock_repo.get_upcoming_birthdays.assert_called_once_with(user)