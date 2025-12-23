"""Integration tests for task API routes."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.main import app
from src.models.user import User


@pytest.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user in the database."""
    import uuid
    # Generate unique email for each test to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    user = User(id=f"test-user-{unique_id}", email=f"test-{unique_id}@example.com", name="Test User")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def auth_client(client: AsyncClient, test_user: User) -> AsyncClient:
    """Create an authenticated client by mocking the get_current_user dependency."""

    async def mock_get_current_user() -> User:
        return test_user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_task_success_with_auth(auth_client: AsyncClient, test_user: User) -> None:
    """Test creating a task with valid authentication."""
    response = await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": "medium"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Task created successfully"
    assert data["data"]["title"] == "Buy groceries"
    assert data["data"]["description"] == "Milk, eggs, bread"
    assert data["data"]["status"] == "pending"
    assert data["data"]["priority"] == "medium"
    assert data["data"]["user_id"] == test_user.id
    assert "id" in data["data"]
    assert "created_at" in data["data"]
    assert "updated_at" in data["data"]


@pytest.mark.asyncio
async def test_create_task_minimal_title_only(auth_client: AsyncClient) -> None:
    """Test creating a task with only title (minimal required field)."""
    response = await auth_client.post("/api/v1/tasks/", json={"title": "Minimal Task"})

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Minimal Task"
    assert data["data"]["description"] is None
    assert data["data"]["priority"] == "medium"  # Default
    assert data["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_create_task_with_description(auth_client: AsyncClient) -> None:
    """Test creating a task with title and description."""
    response = await auth_client.post(
        "/api/v1/tasks/", json={"title": "Test Task", "description": "Test Description"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "Test Task"
    assert data["data"]["description"] == "Test Description"


@pytest.mark.asyncio
async def test_create_task_validation_error_empty_title(auth_client: AsyncClient) -> None:
    """Test that empty title returns validation error."""
    response = await auth_client.post("/api/v1/tasks/", json={"title": "   "})

    # FastAPI returns 422 for validation errors from Pydantic validators
    assert response.status_code in [400, 422]
    data = response.json()
    # Response could be FastAPI's default format or our custom format
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_create_task_validation_error_title_too_long(auth_client: AsyncClient) -> None:
    """Test that title exceeding 100 characters returns validation error."""
    long_title = "a" * 101
    response = await auth_client.post("/api/v1/tasks/", json={"title": long_title})

    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_create_task_validation_error_title_too_many_words(auth_client: AsyncClient) -> None:
    """Test that title exceeding 50 words returns validation error."""
    words = ["word"] * 51
    long_title = " ".join(words)
    response = await auth_client.post("/api/v1/tasks/", json={"title": long_title})

    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_create_task_validation_error_description_too_long(auth_client: AsyncClient) -> None:
    """Test that description exceeding 500 characters returns validation error."""
    long_description = "a" * 501
    response = await auth_client.post(
        "/api/v1/tasks/", json={"title": "Test", "description": long_description}
    )

    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_create_task_unauthorized(client: AsyncClient) -> None:
    """Test that creating a task without authentication returns 401."""
    response = await client.post("/api/v1/tasks/", json={"title": "Test Task"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_task_with_high_priority(auth_client: AsyncClient) -> None:
    """Test creating a task with HIGH priority."""
    response = await auth_client.post(
        "/api/v1/tasks/", json={"title": "Urgent Task", "priority": "high"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["priority"] == "high"


@pytest.mark.asyncio
async def test_create_task_with_low_priority(auth_client: AsyncClient) -> None:
    """Test creating a task with LOW priority."""
    response = await auth_client.post(
        "/api/v1/tasks/", json={"title": "Low Priority Task", "priority": "low"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["priority"] == "low"


@pytest.mark.asyncio
async def test_create_task_trims_whitespace(auth_client: AsyncClient) -> None:
    """Test that title and description whitespace is trimmed."""
    response = await auth_client.post(
        "/api/v1/tasks/",
        json={"title": "  Test Task  ", "description": "  Test Description  "},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["title"] == "Test Task"
    assert data["data"]["description"] == "Test Description"


@pytest.mark.asyncio
async def test_create_task_empty_description_becomes_null(auth_client: AsyncClient) -> None:
    """Test that empty description string is converted to null."""
    response = await auth_client.post(
        "/api/v1/tasks/", json={"title": "Test Task", "description": "   "}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["description"] is None
