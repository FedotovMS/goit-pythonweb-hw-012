import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_contact(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Send a POST request to create a new contact
        response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )

    # Check the status code and response data
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert data["last_name"] == test_contact["last_name"]
    assert data["email"] == test_contact["email"]
    assert data["user_id"] == 1


@pytest.mark.asyncio
async def test_get_contacts(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        await async_client.post("/contacts/", json=test_contact, headers=headers)

        # Send a GET request to fetch all contacts
        response = await async_client.get("/contacts/", headers=headers)

    # Check the status code and response data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Ensure the response is a list
    assert len(data) == 1  # Only one contact should exist
    assert data[0]["email"] == test_contact["email"]


@pytest.mark.asyncio
async def test_get_contact(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        create_response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )
        contact_id = create_response.json()["id"]

        # Send a GET request to fetch the created contact by ID
        response = await async_client.get(f"/contacts/{contact_id}", headers=headers)

    # Check the status code and response data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contact_id  # Ensure the returned contact ID matches
    assert data["email"] == test_contact["email"]


@pytest.mark.asyncio
async def test_update_contact(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        create_response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )
        contact_id = create_response.json()["id"]

        # Prepare updated contact data
        updated_data = test_contact.copy()
        updated_data["first_name"] = "Updated"

        # Send a PUT request to update the contact
        response = await async_client.put(
            f"/contacts/{contact_id}", json=updated_data, headers=headers
        )

    # Check the status code and response data
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"  # Ensure the first name was updated


@pytest.mark.asyncio
async def test_delete_contact(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        create_response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )
        contact_id = create_response.json()["id"]

        # Send a DELETE request to delete the contact by ID
        response = await async_client.delete(f"/contacts/{contact_id}", headers=headers)

    # Check that the contact was deleted successfully
    assert response.status_code == 204  # No content returned after successful deletion


@pytest.mark.asyncio
async def test_search_contacts(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        await async_client.post("/contacts/", json=test_contact, headers=headers)

        # Send a GET request to search contacts based on query string (e.g., last name "Doe")
        response = await async_client.get("/contacts/search?query=Doe", headers=headers)

    # Check the status code and response data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Ensure the response is a list
    assert len(data) > 0  # Ensure at least one contact is returned
    assert data[0]["last_name"] == "Doe"  # Ensure the contact's last name matches the search query


@pytest.mark.asyncio
async def test_upcoming_birthdays(async_client, test_contact, mock_jwt):
    # Set the Authorization header with a mock JWT token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock the get_current_user function to return a mock user object
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        # Create a mock user object
        mock_user.return_value = User(
            id=1,
            email="test@test.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact with today's birthday
        today_contact = test_contact.copy()
        today_contact["birth_date"] = datetime.now().isoformat()
        await async_client.post("/contacts/", json=today_contact, headers=headers)

        # Send a GET request to fetch upcoming birthdays
        response = await async_client.get("/contacts/birthdays", headers=headers)

    # Check the status code and response data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Ensure the response is a list
    assert len(data) > 0  # Ensure there is at least one upcoming birthday