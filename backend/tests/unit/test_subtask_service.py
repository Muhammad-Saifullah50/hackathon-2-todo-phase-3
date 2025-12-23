"""
Unit tests for SubtaskService.

Tests subtask CRUD operations, auto-completion logic, and reordering.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.services.subtask_service import SubtaskService, SubtaskNotFoundError
from src.models.subtask import Subtask
from src.models.task import Task, TaskStatus
from src.schemas.subtask_schemas import SubtaskCreate, SubtaskUpdate


@pytest.fixture
def mock_db_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.get = AsyncMock()
    return session


@pytest.fixture
def subtask_service(mock_db_session):
    """Create SubtaskService instance with mock session."""
    return SubtaskService(session=mock_db_session)


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        id=uuid4(),
        user_id="user123",
        title="Parent Task",
        status=TaskStatus.PENDING,
        priority="medium",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_subtask():
    """Create a sample subtask for testing."""
    task_id = uuid4()
    return Subtask(
        id=uuid4(),
        task_id=task_id,
        description="Test subtask",
        is_completed=False,
        order_index=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestCreateSubtask:
    """Tests for create_subtask method."""

    @pytest.mark.asyncio
    async def test_create_subtask_success(self, subtask_service, mock_db_session, sample_task):
        """Test successful subtask creation."""
        # Mock task check
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = sample_task

        # Mock subtask count check
        count_result = MagicMock()
        count_result.scalar.return_value = 0

        # Mock max order check
        max_result = MagicMock()
        max_result.scalar.return_value = None

        mock_db_session.execute.side_effect = [task_result, count_result, max_result]

        subtask_data = SubtaskCreate(description="New subtask")
        task_id = sample_task.id

        # Execute
        result = await subtask_service.create_subtask(
            task_id=task_id,
            subtask_data=subtask_data,
            user_id="user123"
        )

        # Assert
        assert result.description == "New subtask"
        assert result.task_id == task_id
        assert result.is_completed is False
        assert result.order_index == 0
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_subtask_task_not_found(self, subtask_service, mock_db_session):
        """Test creating subtask for non-existent task."""
        # Mock task not found
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = task_result

        subtask_data = SubtaskCreate(description="New subtask")
        task_id = uuid4()

        # Execute and assert
        with pytest.raises(SubtaskNotFoundError):
            await subtask_service.create_subtask(
                task_id=task_id,
                subtask_data=subtask_data,
                user_id="user123"
            )


class TestGetSubtasks:
    """Tests for get_subtasks method."""

    @pytest.mark.asyncio
    async def test_get_subtasks_success(self, subtask_service, mock_db_session, sample_task):
        """Test retrieving all subtasks for a task."""
        # Mock task check
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = sample_task

        # Mock subtasks query
        subtask1 = Subtask(
            id=uuid4(),
            task_id=sample_task.id,
            description="First",
            is_completed=False,
            order_index=0
        )
        subtask2 = Subtask(
            id=uuid4(),
            task_id=sample_task.id,
            description="Second",
            is_completed=True,
            order_index=1
        )

        subtasks_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [subtask1, subtask2]
        subtasks_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [task_result, subtasks_result]

        # Execute
        result = await subtask_service.get_subtasks(task_id=sample_task.id, user_id="user123")

        # Assert
        assert result.total_count == 2
        assert result.completed_count == 1
        assert result.completion_percentage == 50.0
        assert len(result.subtasks) == 2


class TestToggleSubtask:
    """Tests for toggle_subtask method."""

    @pytest.mark.asyncio
    async def test_toggle_subtask_complete(self, subtask_service, mock_db_session, sample_subtask):
        """Test toggling subtask from incomplete to complete."""
        sample_subtask.is_completed = False

        # Mock get subtask with auth
        subtask_result = MagicMock()
        subtask_result.scalar_one_or_none.return_value = sample_subtask

        # Mock get all subtasks for parent check
        all_subtasks_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_subtask]
        all_subtasks_result.scalars.return_value = mock_scalars

        # Mock get task
        task_result = MagicMock()
        task = Task(
            id=sample_subtask.task_id,
            user_id="user123",
            title="Test",
            status=TaskStatus.PENDING,
            priority="medium"
        )
        task_result.scalar_one_or_none.return_value = task

        mock_db_session.execute.side_effect = [
            subtask_result,
            all_subtasks_result,
            task_result
        ]

        # Execute
        result = await subtask_service.toggle_subtask(
            subtask_id=sample_subtask.id,
            is_completed=True,
            user_id="user123"
        )

        # Assert
        assert result.is_completed is True
        mock_db_session.commit.assert_called()


class TestUpdateSubtask:
    """Tests for update_subtask method."""

    @pytest.mark.asyncio
    async def test_update_subtask_description(
        self,
        subtask_service,
        mock_db_session,
        sample_subtask
    ):
        """Test updating subtask description."""
        # Mock get subtask with auth
        subtask_result = MagicMock()
        subtask_result.scalar_one_or_none.return_value = sample_subtask

        # Mock get all subtasks (for auto-complete check)
        all_subtasks_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_subtask]
        all_subtasks_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [subtask_result, all_subtasks_result]

        subtask_update = SubtaskUpdate(description="Updated description")

        # Execute
        result = await subtask_service.update_subtask(
            subtask_id=sample_subtask.id,
            subtask_data=subtask_update,
            user_id="user123"
        )

        # Assert
        assert result.description == "Updated description"
        mock_db_session.commit.assert_called()


class TestDeleteSubtask:
    """Tests for delete_subtask method."""

    @pytest.mark.asyncio
    async def test_delete_subtask_success(
        self,
        subtask_service,
        mock_db_session,
        sample_subtask
    ):
        """Test successful subtask deletion."""
        # Mock get subtask with auth
        subtask_result = MagicMock()
        subtask_result.scalar_one_or_none.return_value = sample_subtask
        mock_db_session.execute.return_value = subtask_result

        # Execute
        await subtask_service.delete_subtask(
            subtask_id=sample_subtask.id,
            user_id="user123"
        )

        # Assert
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_subtask_not_found(self, subtask_service, mock_db_session):
        """Test deleting non-existent subtask."""
        # Mock subtask not found
        subtask_result = MagicMock()
        subtask_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = subtask_result

        subtask_id = uuid4()

        # Execute and assert
        with pytest.raises(SubtaskNotFoundError):
            await subtask_service.delete_subtask(subtask_id=subtask_id, user_id="user123")


class TestReorderSubtasks:
    """Tests for reorder_subtasks method."""

    @pytest.mark.asyncio
    async def test_reorder_subtasks_success(
        self,
        subtask_service,
        mock_db_session,
        sample_task
    ):
        """Test reordering subtasks."""
        # Mock task check
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = sample_task

        # Create subtasks
        subtask1 = Subtask(id=uuid4(), task_id=sample_task.id, description="First", order_index=0)
        subtask2 = Subtask(id=uuid4(), task_id=sample_task.id, description="Second", order_index=1)
        subtask3 = Subtask(id=uuid4(), task_id=sample_task.id, description="Third", order_index=2)

        # Mock get all subtasks
        subtasks_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [subtask1, subtask2, subtask3]
        subtasks_result.scalars.return_value = mock_scalars

        mock_db_session.execute.side_effect = [task_result, subtasks_result]

        new_order = [subtask3.id, subtask1.id, subtask2.id]  # Reverse order

        # Execute
        await subtask_service.reorder_subtasks(
            task_id=sample_task.id,
            subtask_ids=new_order,
            user_id="user123"
        )

        # Assert - order_index should be updated
        assert subtask3.order_index == 0
        assert subtask1.order_index == 1
        assert subtask2.order_index == 2
        mock_db_session.commit.assert_called()
