from uuid import UUID

import pytest
from pydantic import ValidationError

from src.models.task import Task, TaskCreate, TaskPriority, TaskStatus
from src.models.user import User


def test_user_model_creation() -> None:
    """Test creating a User model instance."""
    user = User(id="test-user-123", email="test@example.com", name="Test User")
    assert isinstance(user.id, str)
    assert user.id == "test-user-123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.email_verified is False


def test_task_model_creation() -> None:
    """Test creating a Task model instance."""
    user_id = "test-user-123"
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id=user_id,
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
    )
    assert isinstance(task.id, UUID)
    assert task.title == "Test Task"
    assert task.user_id == user_id
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.HIGH
    assert task.completed_at is None


# TaskCreate Validator Tests


def test_title_validation_empty() -> None:
    """Test that empty title raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="   ", description="Test")

    errors = exc_info.value.errors()
    assert any("Title cannot be empty" in str(error["ctx"]["error"]) for error in errors if "ctx" in error)


def test_title_validation_too_long_chars() -> None:
    """Test that title exceeding 100 characters raises validation error."""
    long_title = "a" * 101
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title=long_title)

    errors = exc_info.value.errors()
    assert any("100 characters" in str(error["ctx"]["error"]) for error in errors if "ctx" in error)


def test_title_validation_too_many_words() -> None:
    """Test that title exceeding 50 words raises validation error."""
    # Create a title with 51 words
    words = ["word"] * 51
    long_title = " ".join(words)

    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title=long_title)

    errors = exc_info.value.errors()
    # Now word count is checked BEFORE character limit
    assert any("50 words" in str(error["ctx"]["error"]) for error in errors if "ctx" in error)


def test_title_validation_success() -> None:
    """Test that valid title passes validation."""
    task_data = TaskCreate(title="Buy groceries", description="Milk, eggs, bread")
    assert task_data.title == "Buy groceries"
    assert task_data.description == "Milk, eggs, bread"


def test_title_trim_whitespace() -> None:
    """Test that title whitespace is trimmed."""
    task_data = TaskCreate(title="  Buy groceries  ")
    assert task_data.title == "Buy groceries"


def test_description_validation_too_long() -> None:
    """Test that description exceeding 500 characters raises validation error."""
    long_description = "a" * 501

    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="Test", description=long_description)

    errors = exc_info.value.errors()
    assert any("500 characters" in str(error["ctx"]["error"]) for error in errors if "ctx" in error)


def test_description_trim_and_null() -> None:
    """Test that empty description is converted to None."""
    # Empty string becomes None
    task_data = TaskCreate(title="Test Task", description="   ")
    assert task_data.description is None

    # None stays None
    task_data2 = TaskCreate(title="Test Task", description=None)
    assert task_data2.description is None

    # Actual content is trimmed but kept
    task_data3 = TaskCreate(title="Test Task", description="  Some content  ")
    assert task_data3.description == "Some content"


def test_description_optional() -> None:
    """Test that description is optional."""
    task_data = TaskCreate(title="Test Task")
    assert task_data.description is None


def test_priority_defaults_to_medium() -> None:
    """Test that priority defaults to MEDIUM when not provided."""
    task_data = TaskCreate(title="Test Task")
    assert task_data.priority == TaskPriority.MEDIUM


def test_priority_accepts_valid_values() -> None:
    """Test that priority accepts LOW, MEDIUM, and HIGH."""
    task_low = TaskCreate(title="Test", priority=TaskPriority.LOW)
    assert task_low.priority == TaskPriority.LOW

    task_medium = TaskCreate(title="Test", priority=TaskPriority.MEDIUM)
    assert task_medium.priority == TaskPriority.MEDIUM

    task_high = TaskCreate(title="Test", priority=TaskPriority.HIGH)
    assert task_high.priority == TaskPriority.HIGH


def test_status_defaults_to_pending() -> None:
    """Test that status defaults to PENDING."""
    task_data = TaskCreate(title="Test Task")
    assert task_data.status == TaskStatus.PENDING
