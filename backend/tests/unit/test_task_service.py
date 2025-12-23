"""Unit tests for TaskService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import TaskCreate, TaskPriority, TaskStatus
from src.models.user import User
from src.services.task_service import TaskService


@pytest.mark.asyncio
async def test_create_task_success(test_session: AsyncSession) -> None:
    """Test creating a task successfully."""
    # Create a test user first
    user = User(id="test-user-service-1", email="test-service-1@example.com", name="Test User")
    test_session.add(user)
    await test_session.commit()

    # Create task service
    service = TaskService(test_session)

    # Create task data
    task_data = TaskCreate(title="Buy groceries", description="Milk, eggs, bread")

    # Create task
    task = await service.create_task(task_data, user.id)

    # Assertions
    assert task.id is not None
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.MEDIUM  # Default
    assert task.user_id == user.id
    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.completed_at is None


@pytest.mark.asyncio
async def test_create_task_default_priority(test_session: AsyncSession) -> None:
    """Test that task defaults to MEDIUM priority when not specified."""
    # Create a test user
    user = User(id="test-user-service-2", email="test-service-2@example.com")
    test_session.add(user)
    await test_session.commit()

    # Create service
    service = TaskService(test_session)

    # Create task without priority
    task_data = TaskCreate(title="Test Task")
    task = await service.create_task(task_data, user.id)

    # Assert default priority
    assert task.priority == TaskPriority.MEDIUM


@pytest.mark.asyncio
async def test_create_task_sets_pending_status(test_session: AsyncSession) -> None:
    """Test that task is always created with PENDING status."""
    # Create a test user
    user = User(id="test-user-service-3", email="test-service-3@example.com")
    test_session.add(user)
    await test_session.commit()

    # Create service
    service = TaskService(test_session)

    # Create task
    task_data = TaskCreate(title="Test Task", priority=TaskPriority.HIGH)
    task = await service.create_task(task_data, user.id)

    # Assert status is PENDING
    assert task.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_create_task_sets_user_id(test_session: AsyncSession) -> None:
    """Test that task is created with the correct user_id from JWT."""
    # Create a test user
    user = User(id="test-user-service-4", email="test-service-4@example.com")
    test_session.add(user)
    await test_session.commit()

    # Create service
    service = TaskService(test_session)

    # Create task
    task_data = TaskCreate(title="Test Task")
    task = await service.create_task(task_data, user.id)

    # Assert user_id matches
    assert task.user_id == "test-user-service-4"


@pytest.mark.asyncio
async def test_create_task_with_all_fields(test_session: AsyncSession) -> None:
    """Test creating a task with all optional fields specified."""
    # Create a test user
    user = User(id="test-user-service-5", email="test-service-5@example.com")
    test_session.add(user)
    await test_session.commit()

    # Create service
    service = TaskService(test_session)

    # Create task with all fields
    task_data = TaskCreate(
        title="Complete project",
        description="Finish the backend API implementation",
        priority=TaskPriority.HIGH,
    )
    task = await service.create_task(task_data, user.id)

    # Assertions
    assert task.title == "Complete project"
    assert task.description == "Finish the backend API implementation"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.PENDING
    assert task.user_id == user.id


@pytest.mark.asyncio
async def test_create_task_minimal_title_only(test_session: AsyncSession) -> None:
    """Test creating a task with only title (minimal required field)."""
    # Create a test user
    user = User(id="test-user-service-6", email="test-service-6@example.com")
    test_session.add(user)
    await test_session.commit()

    # Create service
    service = TaskService(test_session)

    # Create task with only title
    task_data = TaskCreate(title="Minimal Task")
    task = await service.create_task(task_data, user.id)

    # Assertions
    assert task.title == "Minimal Task"
    assert task.description is None
    assert task.priority == TaskPriority.MEDIUM
    assert task.status == TaskStatus.PENDING
