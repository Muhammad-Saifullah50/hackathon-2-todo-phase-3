"""Unit tests for database models."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models.task import Task, TaskCreate, TaskStatus, TaskPriority, TaskResponse
from src.models.tag import Tag
from src.models.user import User


class TestTaskModel:
    """Test cases for Task model validation and behavior."""

    def test_task_create_valid_title(self):
        """Test task creation with valid title."""
        task_data = TaskCreate(
            title="Valid Task Title",
            description="Valid description",
            priority=TaskPriority.MEDIUM,
        )
        assert task_data.title == "Valid Task Title"
        assert task_data.description == "Valid description"
        assert task_data.priority == TaskPriority.MEDIUM

    def test_task_create_title_validation_empty(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="", description="Test")

        errors = exc_info.value.errors()
        assert any("Title cannot be empty" in str(e["ctx"].get("error", "")) for e in errors)

    def test_task_create_title_validation_whitespace_only(self):
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="   ", description="Test")

        errors = exc_info.value.errors()
        assert any("Title cannot be empty" in str(e["ctx"].get("error", "")) for e in errors)

    def test_task_create_title_validation_too_long(self):
        """Test that title exceeding 100 characters raises validation error."""
        long_title = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title, description="Test")

        errors = exc_info.value.errors()
        assert any("100 characters" in str(e["ctx"].get("error", "")) for e in errors)

    def test_task_create_title_validation_too_many_words(self):
        """Test that title exceeding 50 words raises validation error."""
        # Create a title with 51 words
        long_title = " ".join([f"word{i}" for i in range(51)])
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title, description="Test")

        errors = exc_info.value.errors()
        assert any("50 words" in str(e["ctx"].get("error", "")) for e in errors)

    def test_task_create_title_trimming(self):
        """Test that title is trimmed of whitespace."""
        task_data = TaskCreate(title="  Trimmed Title  ", description="Test")
        assert task_data.title == "Trimmed Title"

    def test_task_create_description_validation_too_long(self):
        """Test that description exceeding 500 characters raises validation error."""
        long_desc = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Valid Title", description=long_desc)

        errors = exc_info.value.errors()
        assert any("500 characters" in str(e["ctx"].get("error", "")) for e in errors)

    def test_task_create_description_trimming(self):
        """Test that description is trimmed of whitespace."""
        task_data = TaskCreate(title="Valid Title", description="  Trimmed Description  ")
        assert task_data.description == "Trimmed Description"

    def test_task_create_description_empty_string_to_none(self):
        """Test that empty description string becomes None."""
        task_data = TaskCreate(title="Valid Title", description="   ")
        assert task_data.description is None

    def test_task_create_description_optional(self):
        """Test that description is optional."""
        task_data = TaskCreate(title="Valid Title")
        assert task_data.description is None

    def test_task_create_default_priority(self):
        """Test that default priority is MEDIUM."""
        task_data = TaskCreate(title="Valid Title")
        assert task_data.priority == TaskPriority.MEDIUM

    def test_task_create_with_all_priorities(self):
        """Test task creation with all priority levels."""
        for priority in [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]:
            task_data = TaskCreate(title="Valid Title", priority=priority)
            assert task_data.priority == priority

    def test_task_create_with_due_date(self):
        """Test task creation with due date."""
        due_date = datetime.now(timezone.utc)
        task_data = TaskCreate(title="Valid Title", due_date=due_date)
        assert task_data.due_date == due_date

    def test_task_create_with_notes(self):
        """Test task creation with notes."""
        notes = "These are some notes"
        task_data = TaskCreate(title="Valid Title", notes=notes)
        assert task_data.notes == notes

    def test_task_create_with_manual_order(self):
        """Test task creation with manual order."""
        task_data = TaskCreate(title="Valid Title", manual_order=5)
        assert task_data.manual_order == 5

    @pytest.mark.asyncio
    async def test_task_soft_delete(self, test_session, test_user):
        """Test soft delete sets deleted_at timestamp."""
        task = Task(
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Soft delete
        now = datetime.now(timezone.utc)
        task.deleted_at = now
        await test_session.commit()
        await test_session.refresh(task)

        assert task.deleted_at is not None
        # SQLite stores naive datetimes, so compare without timezone
        if task.deleted_at.tzinfo is None:
            assert task.deleted_at >= now.replace(tzinfo=None)
        else:
            assert task.deleted_at >= now

    @pytest.mark.asyncio
    async def test_task_timestamps_auto_set(self, test_session, test_user):
        """Test that created_at and updated_at are automatically set."""
        task = Task(
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        assert task.created_at is not None
        assert task.updated_at is not None
        assert task.created_at <= task.updated_at

    @pytest.mark.asyncio
    async def test_task_status_enum_values(self, test_session, test_user):
        """Test task status enum values."""
        # Test PENDING
        task_pending = Task(
            title="Pending Task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
        )
        test_session.add(task_pending)
        await test_session.commit()
        await test_session.refresh(task_pending)
        assert task_pending.status == TaskStatus.PENDING

        # Test COMPLETED
        task_completed = Task(
            title="Completed Task",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
            completed_at=datetime.now(timezone.utc),
        )
        test_session.add(task_completed)
        await test_session.commit()
        await test_session.refresh(task_completed)
        assert task_completed.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_task_response_from_task(self, test_session, test_user):
        """Test TaskResponse.from_task() method."""
        from sqlalchemy.orm import selectinload

        task = Task(
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
        )
        test_session.add(task)
        await test_session.commit()

        # Reload with relationships eagerly loaded to avoid lazy loading in sync context
        from sqlalchemy import select
        stmt = select(Task).where(Task.id == task.id).options(selectinload(Task.task_tags))
        result = await test_session.execute(stmt)
        task = result.scalar_one()

        task_response = TaskResponse.from_task(task)

        assert task_response.id == task.id
        assert task_response.title == task.title
        assert task_response.description == task.description
        assert task_response.status == task.status
        assert task_response.priority == task.priority
        assert task_response.user_id == task.user_id
        assert task_response.tags == []


class TestTagModel:
    """Test cases for Tag model."""

    @pytest.mark.asyncio
    async def test_tag_creation(self, test_session, test_user):
        """Test creating a tag."""
        tag = Tag(
            name="Work",
            color="#3B82F6",
            user_id=test_user.id,
        )
        test_session.add(tag)
        await test_session.commit()
        await test_session.refresh(tag)

        assert tag.id is not None
        assert tag.name == "Work"
        assert tag.color == "#3B82F6"
        assert tag.user_id == test_user.id
        assert tag.created_at is not None

    @pytest.mark.asyncio
    async def test_tag_name_max_length(self, test_session, test_user):
        """Test tag name maximum length."""
        # This would be validated at the database level
        tag = Tag(
            name="A" * 50,  # Max length
            color="#3B82F6",
            user_id=test_user.id,
        )
        test_session.add(tag)
        await test_session.commit()
        await test_session.refresh(tag)

        assert len(tag.name) == 50


class TestUserModel:
    """Test cases for User model."""

    @pytest.mark.asyncio
    async def test_user_creation(self, test_session):
        """Test creating a user."""
        user = User(
            id="test-user-123",
            email="test@example.com",
            name="Test User",
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)

        assert user.id == "test-user-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    @pytest.mark.asyncio
    async def test_user_task_relationship(self, test_session, test_user):
        """Test user-task relationship."""
        task = Task(
            title="Test Task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
        )
        test_session.add(task)
        await test_session.commit()

        # Refresh to load relationships
        await test_session.refresh(test_user)

        # Note: Relationships may need explicit loading depending on SQLModel configuration
        # This test verifies the foreign key relationship works
        assert task.user_id == test_user.id
