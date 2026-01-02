"""Pytest fixtures for Todo API tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

from src.auth import get_current_user
from src.db.session import get_db
from src.main import app
from src.models.user import User

# Import models to ensure they are registered with SQLModel.metadata
from src.models import *  # noqa

# Use in-memory SQLite for tests to avoid external dependencies
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine() -> AsyncGenerator[Any]:
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine: Any) -> AsyncGenerator[AsyncSession]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Create a test client with a database session override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user in the database."""
    import uuid

    # Generate unique email for each test to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        id=f"test-user-{unique_id}", email=f"test-{unique_id}@example.com", name="Test User"
    )
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


@pytest.fixture
async def sample_task(test_session: AsyncSession, test_user: User):
    """Create a sample task for testing."""
    from datetime import datetime, timezone
    from src.models.task import Task, TaskPriority, TaskStatus

    task = Task(
        title="Sample Task",
        description="A sample task for testing",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        user_id=test_user.id,
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task


@pytest.fixture
async def sample_tasks(test_session: AsyncSession, test_user: User):
    """Create multiple sample tasks for testing."""
    from datetime import datetime, timezone, timedelta
    from src.models.task import Task, TaskPriority, TaskStatus

    tasks = []
    now = datetime.now(timezone.utc)

    # Create tasks with different statuses and priorities
    task_data = [
        {
            "title": "High Priority Task",
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.PENDING,
            "due_date": now + timedelta(days=1),
        },
        {
            "title": "Medium Priority Task",
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "due_date": now + timedelta(days=7),
        },
        {
            "title": "Low Priority Task",
            "priority": TaskPriority.LOW,
            "status": TaskStatus.PENDING,
            "due_date": None,
        },
        {
            "title": "Completed Task",
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.COMPLETED,
            "completed_at": now - timedelta(hours=2),
        },
        {
            "title": "Overdue Task",
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.PENDING,
            "due_date": now - timedelta(days=2),
        },
    ]

    for data in task_data:
        task = Task(
            title=data["title"],
            description=f"Description for {data['title']}",
            status=data["status"],
            priority=data["priority"],
            due_date=data.get("due_date"),
            completed_at=data.get("completed_at"),
            user_id=test_user.id,
        )
        test_session.add(task)
        tasks.append(task)

    await test_session.commit()
    for task in tasks:
        await test_session.refresh(task)

    return tasks


@pytest.fixture
async def sample_tag(test_session: AsyncSession, test_user: User):
    """Create a sample tag for testing."""
    from src.models.tag import Tag

    tag = Tag(
        name="Work",
        color="#3B82F6",
        user_id=test_user.id,
    )
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)
    return tag


@pytest.fixture
async def sample_tags(test_session: AsyncSession, test_user: User):
    """Create multiple sample tags for testing."""
    from src.models.tag import Tag

    tag_data = [
        {"name": "Work", "color": "#3B82F6"},
        {"name": "Personal", "color": "#10B981"},
        {"name": "Urgent", "color": "#EF4444"},
    ]

    tags = []
    for data in tag_data:
        tag = Tag(
            name=data["name"],
            color=data["color"],
            user_id=test_user.id,
        )
        test_session.add(tag)
        tags.append(tag)

    await test_session.commit()
    for tag in tags:
        await test_session.refresh(tag)

    return tags


@pytest.fixture
def mock_jwt_token():
    """Generate a mock JWT token for testing."""
    import jwt
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "aud": "todo-api",
        "iss": "todo-auth",
    }

    # For testing, we'll use a simple secret key
    # In actual tests, we'd need to mock the JWT validation
    return jwt.encode(payload, "test-secret-key", algorithm="HS256")
