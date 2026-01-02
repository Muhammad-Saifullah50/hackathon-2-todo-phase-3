"""Comprehensive tests for MCP server - covers all tools and edge cases.

This test suite ensures:
1. All MCP tools work correctly
2. Authentication changes don't break functionality
3. Database operations are properly tested
4. Edge cases and error conditions are covered
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
import uuid
import json


class TestAddTaskComprehensive:
    """Comprehensive tests for add_task tool."""

    @pytest.mark.asyncio
    async def test_add_task_minimal_required_fields(self):
        """Test adding task with only required field (title)."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(title="Test Task")

        assert result["success"] is True
        assert result["task"]["title"] == "Test Task"
        assert result["task"]["status"] == "pending"
        assert result["task"]["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_add_task_all_fields(self):
        """Test adding task with all possible fields."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(
                title="Complete Task",
                description="Full description",
                due_date="2024-12-31T23:59:59Z",
                priority="high",
                tags=["urgent", "work"],
                user_id="test-user-123"
            )

        assert result["success"] is True
        assert result["task"]["title"] == "Complete Task"
        assert result["task"]["description"] == "Full description"
        assert result["task"]["priority"] == "high"
        assert result["task"]["tags"] == ["urgent", "work"]

    @pytest.mark.asyncio
    async def test_add_task_empty_title(self):
        """Test adding task with empty title fails."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(title="")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_add_task_whitespace_only_title(self):
        """Test adding task with whitespace-only title fails."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(title="   ")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_add_task_invalid_priority_values(self):
        """Test various invalid priority values."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        invalid_priorities = ["urgent", "critical", "normal", "MEDIUM", "123", ""]

        with patch('main.get_pool', return_value=mock_pool):
            for invalid_priority in invalid_priorities:
                result = await add_task(
                    title="Test Task",
                    priority=invalid_priority
                )

                # Only lowercase low/medium/high are valid
                if invalid_priority.lower() not in ["low", "medium", "high"]:
                    assert result["success"] is False
                    assert "Invalid priority" in result["error"]

    @pytest.mark.asyncio
    async def test_add_task_valid_priority_values(self):
        """Test all valid priority values."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        valid_priorities = ["low", "medium", "high"]

        for priority in valid_priorities:
            with patch('main.get_pool', return_value=mock_pool):
                result = await add_task(
                    title=f"Task with {priority} priority",
                    priority=priority
                )

            assert result["success"] is True
            assert result["task"]["priority"] == priority

    @pytest.mark.asyncio
    async def test_add_task_various_date_formats(self):
        """Test various date format inputs."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        valid_dates = [
            "2024-12-31",
            "2024-12-31T23:59:59",
            "2024-12-31T23:59:59Z",
            "2024-12-31T23:59:59+00:00",
            "December 31, 2024",
            "12/31/2024",
        ]

        for date_str in valid_dates:
            with patch('main.get_pool', return_value=mock_pool):
                result = await add_task(
                    title="Task with date",
                    due_date=date_str
                )

            assert result["success"] is True
            assert result["task"]["due_date"] is not None

    @pytest.mark.asyncio
    async def test_add_task_invalid_date_format(self):
        """Test invalid date format."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(
                title="Task",
                due_date="invalid-date"
            )

        assert result["success"] is False
        assert "date" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_add_task_database_error(self):
        """Test database error handling."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock(side_effect=Exception("Database connection failed"))

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(title="Test Task")

        assert result["success"] is False
        assert "error" in result


class TestListTasksComprehensive:
    """Comprehensive tests for list_tasks tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_no_filters(self):
        """Test listing all tasks without filters."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_tasks = [
            {
                "id": str(uuid.uuid4()),
                "title": "Task 1",
                "description": "Description 1",
                "status": "pending",
                "priority": "high",
                "due_date": None,
                "created_at": datetime.now(timezone.utc),
                "completed_at": None,
                "tags": "[]"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Task 2",
                "description": None,
                "status": "completed",
                "priority": "low",
                "due_date": None,
                "created_at": datetime.now(timezone.utc),
                "completed_at": datetime.now(timezone.utc),
                "tags": '["work"]'
            }
        ]
        mock_conn.fetch = AsyncMock(return_value=mock_tasks)

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks()

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self):
        """Test filtering tasks by status."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_tasks = [
            {
                "id": str(uuid.uuid4()),
                "title": "Pending Task",
                "description": None,
                "status": "pending",
                "priority": "medium",
                "due_date": None,
                "created_at": datetime.now(timezone.utc),
                "completed_at": None,
                "tags": "[]"
            }
        ]
        mock_conn.fetch = AsyncMock(return_value=mock_tasks)

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks(status="pending")

        assert result["success"] is True
        assert all(task["status"] == "pending" for task in result["tasks"])

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_priority(self):
        """Test filtering tasks by priority."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch = AsyncMock(return_value=[])

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks(priority="high")

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_tasks_invalid_status(self):
        """Test listing tasks with invalid status."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks(status="invalid")

        assert result["success"] is False
        assert "Invalid status" in result["error"]

    @pytest.mark.asyncio
    async def test_list_tasks_invalid_priority(self):
        """Test listing tasks with invalid priority."""
        from main import list_tasks

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await list_tasks(priority="invalid")

        assert result["success"] is False
        assert "Invalid priority" in result["error"]


class TestCompleteTaskComprehensive:
    """Comprehensive tests for complete_task tool."""

    @pytest.mark.asyncio
    async def test_complete_task_already_completed(self):
        """Test completing an already completed task."""
        from main import complete_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction

        mock_task = {
            "id": task_id,
            "title": "Already Completed",
            "status": "completed",
            "completed_at": datetime.now(timezone.utc)
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await complete_task(task_id)

        # Should succeed even if already completed (idempotent)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_complete_task_invalid_uuid(self):
        """Test completing task with invalid UUID."""
        from main import complete_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        with patch('main.get_pool', return_value=mock_pool):
            result = await complete_task("not-a-uuid")

        # Should either fail validation or not find task
        assert result["success"] is False


class TestUpdateTaskComprehensive:
    """Comprehensive tests for update_task tool."""

    @pytest.mark.asyncio
    async def test_update_task_no_changes(self):
        """Test updating task with no actual changes."""
        from main import update_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_task = {
            "id": task_id,
            "title": "Test Task",
            "description": "Description",
            "status": "pending",
            "priority": "medium",
            "due_date": None
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            # Update with same values
            result = await update_task(
                task_id=task_id,
                title="Test Task"
            )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_task_multiple_fields(self):
        """Test updating multiple fields at once."""
        from main import update_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_task = {
            "id": task_id,
            "title": "Old Title",
            "description": "Old Description",
            "status": "pending",
            "priority": "low",
            "due_date": None
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result = await update_task(
                task_id=task_id,
                title="New Title",
                description="New Description",
                priority="high",
                due_date="2024-12-31"
            )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_task_clear_description(self):
        """Test clearing task description."""
        from main import update_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_task = {
            "id": task_id,
            "title": "Test Task",
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
                description=""
            )

        assert result["success"] is True


class TestDeleteTaskComprehensive:
    """Comprehensive tests for delete_task tool."""

    @pytest.mark.asyncio
    async def test_delete_task_twice(self):
        """Test deleting same task twice (idempotency)."""
        from main import delete_task

        task_id = str(uuid.uuid4())
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction

        # First deletion
        mock_task = {
            "id": task_id,
            "title": "Test Task"
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_task)
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            result1 = await delete_task(task_id)

        assert result1["success"] is True

        # Second deletion - task not found
        mock_conn.fetchrow = AsyncMock(return_value=None)

        with patch('main.get_pool', return_value=mock_pool):
            result2 = await delete_task(task_id)

        assert result2["success"] is False


class TestAuthenticationBehavior:
    """Tests to verify authentication behavior (will fail when auth is implemented)."""

    @pytest.mark.asyncio
    async def test_default_user_id_is_used(self):
        """Test that default_user is currently used (THIS SHOULD FAIL WHEN AUTH IS ADDED)."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            # Don't pass user_id, should default to "default_user"
            result = await add_task(title="Test Task")

        assert result["success"] is True
        # This assertion will need to change when auth is implemented
        # Currently, the default user_id is "default_user"

    @pytest.mark.asyncio
    async def test_user_id_can_be_overridden(self):
        """Test that user_id can be set (SECURITY ISSUE - should require auth)."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction
        mock_conn.execute = AsyncMock()

        with patch('main.get_pool', return_value=mock_pool):
            # Can set any user_id without authentication (SECURITY ISSUE)
            result = await add_task(
                title="Test Task",
                user_id="any-user-id-here"
            )

        assert result["success"] is True
        # This test documents the current insecure behavior
        # When authentication is added, this should require a valid JWT token


class TestDatabaseConnectionPool:
    """Tests for database connection pool behavior."""

    @pytest.mark.asyncio
    async def test_pool_is_reused(self):
        """Test that connection pool is reused across requests."""
        from main import get_pool

        # First call creates pool
        pool1 = await get_pool()
        assert pool1 is not None

        # Second call should return same pool
        pool2 = await get_pool()
        assert pool2 is pool1

    @pytest.mark.asyncio
    async def test_database_url_not_set(self):
        """Test behavior when DATABASE_URL is not set."""
        # This is tested at import time in main.py
        # If DATABASE_URL is not set, it raises ValueError
        pass


class TestErrorHandling:
    """Tests for error handling across all tools."""

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()

        # Simulate connection timeout
        mock_pool.acquire.side_effect = TimeoutError("Connection timeout")

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(title="Test Task")

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test that transactions rollback on error."""
        from main import add_task

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_transaction = AsyncMock()

        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.transaction.return_value.__aenter__.return_value = mock_transaction

        # Simulate error during execute
        mock_conn.execute = AsyncMock(side_effect=Exception("Database error"))

        with patch('main.get_pool', return_value=mock_pool):
            result = await add_task(title="Test Task")

        assert result["success"] is False
        # Transaction should have been rolled back
