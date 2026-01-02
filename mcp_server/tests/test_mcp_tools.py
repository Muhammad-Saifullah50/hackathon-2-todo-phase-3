"""Unit tests for MCP server tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
import uuid


class TestAddTask:
    """Test cases for add_task MCP tool."""

    @pytest.mark.asyncio
    async def test_add_task_success(self):
        """Test successful task creation."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(
                title="Test Task",
                description="Test Description",
                priority="medium",
                user_id="test-user"
            )

        assert result["success"] is True
        assert result["task"]["title"] == "Test Task"
        assert result["task"]["status"] == "pending"
        assert result["task"]["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_add_task_with_due_date(self):
        """Test adding task with due date."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(
                title="Task with Due Date",
                due_date="2024-12-31",
                user_id="test-user"
            )

        assert result["success"] is True
        assert result["task"]["due_date"] is not None

    @pytest.mark.asyncio
    async def test_add_task_invalid_priority(self):
        """Test adding task with invalid priority."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(
                title="Test Task",
                priority="invalid",
                user_id="test-user"
            )

        assert result["success"] is False
        assert "Invalid priority" in result["error"]

    @pytest.mark.asyncio
    async def test_add_task_with_tags(self):
        """Test adding task with tags."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)  # Tag doesn't exist

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(
                title="Task with Tags",
                tags=["work", "urgent"],
                user_id="test-user"
            )

        assert result["success"] is True
        assert result["task"]["tags"] == ["work", "urgent"]


class TestListTasks:
    """Test cases for list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self):
        """Test listing tasks when none exist."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch = AsyncMock(return_value=[])

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks(user_id="test-user")

        assert result["success"] is True
        assert result["count"] == 0
        assert result["tasks"] == []

    @pytest.mark.asyncio
    async def test_list_tasks_with_status_filter(self):
        """Test listing tasks with status filter."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock task row
        mock_row = {
            "id": str(uuid.uuid4()),
            "title": "Test Task",
            "description": "Description",
            "status": "pending",
            "priority": "medium",
            "due_date": None,
            "created_at": datetime.now(timezone.utc),
            "completed_at": None,
            "tags": "[]"
        }
        mock_conn.fetch = AsyncMock(return_value=[mock_row])

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks(status="pending", user_id="test-user")

        assert result["success"] is True
        assert result["count"] >= 0


class TestCompleteTask:
    """Test cases for complete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Test completing a task."""
        from main import complete_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction

        # Mock task exists and is not completed
        mock_task = {
            "id": task_id,
            "title": "Test Task",
            "status": "pending"
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await complete_task(task_id, user_id="test-user")

        assert result["success"] is True
        assert result["task"]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self):
        """Test completing non-existent task."""
        from main import complete_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.fetchrow = AsyncMock(return_value=None)

        with patch('main.get_pool', return_value=mock_pool):
            result = await complete_task(task_id, user_id="test-user")

        assert result["success"] is False
        assert "not found" in result["error"]


class TestUpdateTask:
    """Test cases for update_task MCP tool."""

    @pytest.mark.asyncio
    async def test_update_task_success(self):
        """Test updating a task."""
        from main import update_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock task exists
        mock_task = {
            "id": task_id,
            "title": "Old Title",
            "description": "Old Description",
            "status": "pending",
            "priority": "medium",
            "due_date": None
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await update_task(
                task_id=task_id,
                title="New Title",
                user_id="test-user"
            )

        assert result["success"] is True
        assert result["task"]["title"] == "New Title"

    @pytest.mark.asyncio
    async def test_update_task_invalid_priority(self):
        """Test updating task with invalid priority."""
        from main import update_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_task = {
            "id": task_id,
            "title": "Test Task",
            "status": "pending",
            "priority": "medium"
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)

        with patch('main.get_pool', return_value=mock_pool):
            result = await update_task(
                task_id=task_id,
                priority="invalid",
                user_id="test-user"
            )

        assert result["success"] is False
        assert "Invalid priority" in result["error"]


class TestDeleteTask:
    """Test cases for delete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self):
        """Test deleting a task (soft delete)."""
        from main import delete_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction

        mock_task = {
            "id": task_id,
            "title": "Test Task"
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await delete_task(task_id, user_id="test-user")

        assert result["success"] is True
        assert result["task"]["status"] == "deleted"

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self):
        """Test deleting non-existent task."""
        from main import delete_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.fetchrow = AsyncMock(return_value=None)

        with patch('main.get_pool', return_value=mock_pool):
            result = await delete_task(task_id, user_id="test-user")

        assert result["success"] is False
        assert "not found" in result["error"]
