"""Unit tests for TaskService business logic."""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID

from src.services.task_service import TaskService
from src.models.task import TaskCreate, TaskStatus, TaskPriority


class TestTaskServiceCreate:
    """Test cases for TaskService.create_task method."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, test_session, test_user):
        """Test successful task creation."""
        service = TaskService(test_session)
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH,
        )

        task = await service.create_task(task_data, test_user.id)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
        assert task.user_id == test_user.id
        assert task.created_at is not None
        assert task.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(self, test_session, test_user):
        """Test creating task with due date."""
        service = TaskService(test_session)
        due_date = datetime.now(timezone.utc) + timedelta(days=7)
        task_data = TaskCreate(
            title="Task with Due Date",
            due_date=due_date,
        )

        task = await service.create_task(task_data, test_user.id)

        # SQLite stores naive datetimes, so compare without timezone if needed
        if task.due_date and task.due_date.tzinfo is None:
            assert task.due_date == due_date.replace(tzinfo=None)
        else:
            assert task.due_date == due_date

    @pytest.mark.asyncio
    async def test_create_task_minimal_data(self, test_session, test_user):
        """Test creating task with minimal data."""
        service = TaskService(test_session)
        task_data = TaskCreate(title="Minimal Task")

        task = await service.create_task(task_data, test_user.id)

        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.priority == TaskPriority.MEDIUM
        assert task.status == TaskStatus.PENDING


class TestTaskServiceGetTasks:
    """Test cases for TaskService.get_tasks method."""

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, test_session, test_user):
        """Test getting tasks when none exist."""
        service = TaskService(test_session)

        result = await service.get_tasks(test_user.id)

        assert result.pagination.total_items == 0
        assert len(result.tasks) == 0

    @pytest.mark.asyncio
    async def test_get_tasks_filters_by_user(self, test_session, test_user):
        """Test that get_tasks only returns current user's tasks."""
        from src.models.user import User
        from src.models.task import Task

        # Create another user with a task
        other_user = User(id="other-user", email="other@example.com", name="Other User")
        test_session.add(other_user)

        other_task = Task(
            title="Other User's Task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=other_user.id,
        )
        test_session.add(other_task)

        # Create task for test user
        user_task = Task(
            title="Test User's Task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
        )
        test_session.add(user_task)
        await test_session.commit()

        service = TaskService(test_session)
        result = await service.get_tasks(test_user.id)

        assert result.pagination.total_items == 1
        assert result.tasks[0].title == "Test User's Task"

    @pytest.mark.asyncio
    async def test_get_tasks_excludes_soft_deleted(self, test_session, test_user, sample_task):
        """Test that soft-deleted tasks are excluded."""
        # Soft delete the task
        sample_task.deleted_at = datetime.now(timezone.utc)
        await test_session.commit()

        service = TaskService(test_session)
        result = await service.get_tasks(test_user.id)

        assert result.pagination.total_items == 0

    @pytest.mark.asyncio
    async def test_get_tasks_status_filter(self, test_session, test_user, sample_tasks):
        """Test filtering tasks by status."""
        service = TaskService(test_session)

        # Filter by pending
        pending_result = await service.get_tasks(test_user.id, status=TaskStatus.PENDING)
        assert all(task.status == TaskStatus.PENDING for task in pending_result.tasks)

        # Filter by completed
        completed_result = await service.get_tasks(test_user.id, status=TaskStatus.COMPLETED)
        assert all(task.status == TaskStatus.COMPLETED for task in completed_result.tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_priority_filter(self, test_session, test_user, sample_tasks):
        """Test filtering tasks by priority."""
        service = TaskService(test_session)

        high_priority_result = await service.get_tasks(test_user.id, priority=TaskPriority.HIGH)
        assert all(task.priority == TaskPriority.HIGH for task in high_priority_result.tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_pagination(self, test_session, test_user, sample_tasks):
        """Test task pagination."""
        service = TaskService(test_session)

        # Get first page with limit of 2
        page1 = await service.get_tasks(test_user.id, page=1, limit=2)
        assert len(page1.tasks) == 2
        assert page1.pagination.page == 1
        assert page1.pagination.has_next

        # Get second page
        page2 = await service.get_tasks(test_user.id, page=2, limit=2)
        assert len(page2.tasks) == 2
        assert page2.pagination.page == 2

    @pytest.mark.asyncio
    async def test_get_tasks_search(self, test_session, test_user, sample_tasks):
        """Test search functionality."""
        service = TaskService(test_session)

        result = await service.get_tasks(test_user.id, search="High Priority")
        assert len(result.tasks) >= 1
        assert any("High Priority" in task.title for task in result.tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_page(self, test_session, test_user):
        """Test that invalid page number raises ValueError."""
        service = TaskService(test_session)

        with pytest.raises(ValueError, match="Page must be >= 1"):
            await service.get_tasks(test_user.id, page=0)

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_limit(self, test_session, test_user):
        """Test that invalid limit raises ValueError."""
        service = TaskService(test_session)

        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            await service.get_tasks(test_user.id, limit=0)

        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            await service.get_tasks(test_user.id, limit=101)


class TestTaskServiceUpdateTask:
    """Test cases for TaskService.update_task method."""

    @pytest.mark.asyncio
    async def test_update_task_title(self, test_session, test_user, sample_task):
        """Test updating task title."""
        service = TaskService(test_session)

        updated_task = await service.update_task(
            str(sample_task.id),
            test_user.id,
            title="Updated Title"
        )

        assert updated_task.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_multiple_fields(self, test_session, test_user, sample_task):
        """Test updating multiple fields at once."""
        service = TaskService(test_session)

        updated_task = await service.update_task(
            str(sample_task.id),
            test_user.id,
            title="New Title",
            description="New Description",
            priority=TaskPriority.HIGH
        )

        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"
        assert updated_task.priority == TaskPriority.HIGH

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, test_session, test_user):
        """Test updating non-existent task raises ValueError."""
        service = TaskService(test_session)
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(ValueError, match="not found"):
            await service.update_task(fake_id, test_user.id, title="New Title")

    @pytest.mark.asyncio
    async def test_update_task_wrong_user(self, test_session, test_user, sample_task):
        """Test updating task owned by different user raises PermissionError."""
        service = TaskService(test_session)

        with pytest.raises(PermissionError):
            await service.update_task(
                str(sample_task.id),
                "different-user-id",
                title="New Title"
            )

    @pytest.mark.asyncio
    async def test_update_task_no_changes(self, test_session, test_user, sample_task):
        """Test updating task with identical values raises ValueError."""
        service = TaskService(test_session)

        with pytest.raises(ValueError, match="No changes detected"):
            await service.update_task(
                str(sample_task.id),
                test_user.id,
                title=sample_task.title
            )

    @pytest.mark.asyncio
    async def test_update_task_no_fields_provided(self, test_session, test_user, sample_task):
        """Test updating with no fields raises ValueError."""
        service = TaskService(test_session)

        with pytest.raises(ValueError, match="At least one field must be provided"):
            await service.update_task(str(sample_task.id), test_user.id)


class TestTaskServiceToggleStatus:
    """Test cases for TaskService.toggle_task_status method."""

    @pytest.mark.asyncio
    async def test_toggle_pending_to_completed(self, test_session, test_user, sample_task):
        """Test toggling task from pending to completed."""
        service = TaskService(test_session)

        toggled_task = await service.toggle_task_status(str(sample_task.id), test_user.id)

        assert toggled_task.status == TaskStatus.COMPLETED
        assert toggled_task.completed_at is not None

    @pytest.mark.asyncio
    async def test_toggle_completed_to_pending(self, test_session, test_user):
        """Test toggling task from completed to pending."""
        from src.models.task import Task

        completed_task = Task(
            title="Completed Task",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            user_id=test_user.id,
            completed_at=datetime.now(timezone.utc),
        )
        test_session.add(completed_task)
        await test_session.commit()
        await test_session.refresh(completed_task)

        service = TaskService(test_session)
        toggled_task = await service.toggle_task_status(str(completed_task.id), test_user.id)

        assert toggled_task.status == TaskStatus.PENDING
        assert toggled_task.completed_at is None

    @pytest.mark.asyncio
    async def test_toggle_task_not_found(self, test_session, test_user):
        """Test toggling non-existent task raises ValueError."""
        service = TaskService(test_session)
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(ValueError, match="not found"):
            await service.toggle_task_status(fake_id, test_user.id)


class TestTaskServiceDeleteTask:
    """Test cases for TaskService soft delete methods."""

    @pytest.mark.asyncio
    async def test_soft_delete_task(self, test_session, test_user, sample_task):
        """Test soft deleting a task."""
        service = TaskService(test_session)

        deleted_task = await service.soft_delete_task(str(sample_task.id), test_user.id)

        assert deleted_task.deleted_at is not None

        # Verify task is excluded from get_tasks
        result = await service.get_tasks(test_user.id)
        assert result.pagination.total_items == 0

    @pytest.mark.asyncio
    async def test_bulk_delete_tasks(self, test_session, test_user, sample_tasks):
        """Test bulk soft delete."""
        service = TaskService(test_session)
        task_ids = [str(task.id) for task in sample_tasks[:3]]

        deleted_tasks = await service.bulk_delete_tasks(task_ids, test_user.id)

        assert len(deleted_tasks) == 3
        assert all(task.deleted_at is not None for task in deleted_tasks)

    @pytest.mark.asyncio
    async def test_restore_task(self, test_session, test_user, sample_task):
        """Test restoring a soft-deleted task."""
        service = TaskService(test_session)

        # Soft delete
        await service.soft_delete_task(str(sample_task.id), test_user.id)

        # Restore
        restored_task = await service.restore_task(str(sample_task.id), test_user.id)

        assert restored_task.deleted_at is None

    @pytest.mark.asyncio
    async def test_permanent_delete(self, test_session, test_user, sample_task):
        """Test permanently deleting a task."""
        service = TaskService(test_session)

        # Soft delete first
        await service.soft_delete_task(str(sample_task.id), test_user.id)

        # Permanent delete
        await service.permanent_delete(str(sample_task.id), test_user.id)

        # Task should not exist at all
        trash = await service.get_trash(test_user.id)
        assert trash.pagination.total_items == 0


class TestTaskServiceBulkOperations:
    """Test cases for bulk operations."""

    @pytest.mark.asyncio
    async def test_bulk_toggle_status(self, test_session, test_user, sample_tasks):
        """Test bulk status toggle."""
        service = TaskService(test_session)
        pending_tasks = [t for t in sample_tasks if t.status == TaskStatus.PENDING]
        task_ids = [str(task.id) for task in pending_tasks]

        toggled_tasks = await service.bulk_toggle_status(
            task_ids,
            TaskStatus.COMPLETED,
            test_user.id
        )

        assert len(toggled_tasks) == len(task_ids)
        assert all(task.status == TaskStatus.COMPLETED for task in toggled_tasks)

    @pytest.mark.asyncio
    async def test_bulk_toggle_max_limit(self, test_session, test_user):
        """Test bulk toggle respects maximum limit."""
        service = TaskService(test_session)
        # Try to toggle 51 tasks (max is 50)
        fake_ids = [f"00000000-0000-0000-0000-00000000{i:04d}" for i in range(51)]

        with pytest.raises(ValueError, match="Maximum 50 tasks"):
            await service.bulk_toggle_status(fake_ids, TaskStatus.COMPLETED, test_user.id)

    @pytest.mark.asyncio
    async def test_reorder_tasks(self, test_session, test_user, sample_tasks):
        """Test reordering tasks."""
        service = TaskService(test_session)
        task_ids = [str(task.id) for task in sample_tasks[:3]]

        # Reverse the order
        reversed_ids = list(reversed(task_ids))
        reordered_tasks = await service.reorder_tasks(reversed_ids, test_user.id)

        assert len(reordered_tasks) == 3
        for i, task in enumerate(reordered_tasks):
            assert task.manual_order == i
