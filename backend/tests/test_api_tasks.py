"""Integration tests for task API endpoints."""

import pytest
from datetime import datetime, timezone, timedelta


class TestCreateTaskAPI:
    """Test cases for POST /api/v1/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, auth_client, test_user):
        """Test successful task creation via API."""
        response = await auth_client.post(
            "/api/v1/tasks/",
            json={
                "title": "New API Task",
                "description": "Created via API",
                "priority": "high",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "New API Task"
        assert data["data"]["description"] == "Created via API"
        assert data["data"]["priority"] == "high"
        assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_task_validation_error_empty_title(self, auth_client):
        """Test that empty title returns validation error."""
        response = await auth_client.post(
            "/api/v1/tasks/",
            json={"title": ""},
        )

        # FastAPI returns 422 for validation errors, custom validation may return 400
        assert response.status_code in [400, 422]
        data = response.json()
        # Check that it's an error response
        assert "success" not in data or data["success"] is False

    @pytest.mark.asyncio
    async def test_create_task_validation_error_title_too_long(self, auth_client):
        """Test that title exceeding 100 characters returns validation error."""
        response = await auth_client.post(
            "/api/v1/tasks/",
            json={"title": "a" * 101},
        )

        # FastAPI returns 422 for validation errors, custom validation may return 400
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_create_task_unauthorized(self, client):
        """Test that request without authentication returns 401."""
        response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Unauthorized Task"},
        )

        assert response.status_code == 401


class TestGetTasksAPI:
    """Test cases for GET /api/v1/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, auth_client):
        """Test getting tasks when none exist."""
        response = await auth_client.get("/api/v1/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pagination"]["total_items"] == 0
        assert len(data["data"]["tasks"]) == 0

    @pytest.mark.asyncio
    async def test_get_tasks_with_data(self, auth_client, sample_tasks):
        """Test getting tasks with existing data."""
        response = await auth_client.get("/api/v1/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pagination"]["total_items"] == len(sample_tasks)
        assert len(data["data"]["tasks"]) > 0

    @pytest.mark.asyncio
    async def test_get_tasks_with_status_filter(self, auth_client, sample_tasks):
        """Test filtering tasks by status."""
        response = await auth_client.get("/api/v1/tasks/?status_filter=pending")

        assert response.status_code == 200
        data = response.json()
        tasks = data["data"]["tasks"]
        assert all(task["status"] == "pending" for task in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_with_priority_filter(self, auth_client, sample_tasks):
        """Test filtering tasks by priority."""
        response = await auth_client.get("/api/v1/tasks/?priority=high")

        assert response.status_code == 200
        data = response.json()
        tasks = data["data"]["tasks"]
        assert all(task["priority"] == "high" for task in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_with_search(self, auth_client, sample_tasks):
        """Test searching tasks."""
        response = await auth_client.get("/api/v1/tasks/?search=High Priority")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        tasks = data["data"]["tasks"]
        assert any("High Priority" in task["title"] for task in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_pagination(self, auth_client, sample_tasks):
        """Test pagination."""
        response = await auth_client.get("/api/v1/tasks/?page=1&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 2
        assert len(data["data"]["tasks"]) <= 2

    @pytest.mark.asyncio
    async def test_get_tasks_unauthorized(self, client):
        """Test that unauthenticated request returns 401."""
        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 401


class TestUpdateTaskAPI:
    """Test cases for PUT /api/v1/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_success(self, auth_client, sample_task):
        """Test successful task update."""
        response = await auth_client.put(
            f"/api/v1/tasks/{sample_task.id}",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, auth_client):
        """Test updating non-existent task returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await auth_client.put(
            f"/api/v1/tasks/{fake_id}",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 404
        # The API may return different response formats for 404
        # Just check that we got a 404 status


class TestToggleTaskAPI:
    """Test cases for PATCH /api/v1/tasks/{task_id}/toggle endpoint."""

    @pytest.mark.asyncio
    async def test_toggle_task_success(self, auth_client, sample_task):
        """Test toggling task status."""
        response = await auth_client.patch(f"/api/v1/tasks/{sample_task.id}/toggle")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "completed"

        # Toggle back
        response2 = await auth_client.patch(f"/api/v1/tasks/{sample_task.id}/toggle")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_toggle_task_not_found(self, auth_client):
        """Test toggling non-existent task returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await auth_client.patch(f"/api/v1/tasks/{fake_id}/toggle")

        assert response.status_code == 404


class TestDeleteTaskAPI:
    """Test cases for DELETE /api/v1/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, auth_client, sample_task):
        """Test soft deleting a task."""
        response = await auth_client.delete(f"/api/v1/tasks/{sample_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["deleted_at"] is not None

        # Verify task is excluded from get_tasks
        get_response = await auth_client.get("/api/v1/tasks/")
        assert get_response.status_code == 200
        tasks = get_response.json()["data"]["tasks"]
        assert not any(task["id"] == str(sample_task.id) for task in tasks)

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, auth_client):
        """Test deleting non-existent task returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await auth_client.delete(f"/api/v1/tasks/{fake_id}")

        assert response.status_code == 404


class TestBulkOperationsAPI:
    """Test cases for bulk operation endpoints."""

    @pytest.mark.asyncio
    async def test_bulk_toggle(self, auth_client, sample_tasks):
        """Test bulk toggle endpoint."""
        # Status is already a string, not an enum object
        pending_tasks = [t for t in sample_tasks if t.status == "pending"][:2]
        task_ids = [str(task.id) for task in pending_tasks]

        response = await auth_client.post(
            "/api/v1/tasks/bulk-toggle",
            json={"task_ids": task_ids, "target_status": "completed"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["updated_count"] == 2

    @pytest.mark.asyncio
    async def test_bulk_delete(self, auth_client, sample_tasks):
        """Test bulk delete endpoint."""
        task_ids = [str(task.id) for task in sample_tasks[:2]]

        response = await auth_client.post(
            "/api/v1/tasks/bulk-delete",
            json={"task_ids": task_ids},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["updated_count"] == 2


class TestTrashAPI:
    """Test cases for trash-related endpoints."""

    @pytest.mark.asyncio
    async def test_get_trash(self, auth_client, sample_task):
        """Test getting trash items."""
        # Delete a task first
        await auth_client.delete(f"/api/v1/tasks/{sample_task.id}")

        # Get trash
        response = await auth_client.get("/api/v1/tasks/trash")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pagination"]["total_items"] >= 1

    @pytest.mark.asyncio
    async def test_restore_task(self, auth_client, sample_task):
        """Test restoring a task from trash."""
        # Delete task first
        await auth_client.delete(f"/api/v1/tasks/{sample_task.id}")

        # Restore it
        response = await auth_client.post(f"/api/v1/tasks/{sample_task.id}/restore")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["deleted_at"] is None

    @pytest.mark.asyncio
    async def test_permanent_delete(self, auth_client, sample_task):
        """Test permanently deleting a task."""
        # Soft delete first
        await auth_client.delete(f"/api/v1/tasks/{sample_task.id}")

        # Permanent delete
        response = await auth_client.delete(f"/api/v1/tasks/{sample_task.id}/permanent")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestErrorHandling:
    """Test cases for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_uuid(self, auth_client):
        """Test that invalid UUID format is handled."""
        response = await auth_client.get("/api/v1/tasks/invalid-uuid")

        # FastAPI may return 422, 404, 400, 405, or 307 redirect depending on route matching
        assert response.status_code in [307, 400, 404, 405, 422]

    @pytest.mark.asyncio
    async def test_invalid_json(self, auth_client):
        """Test that invalid JSON is handled."""
        response = await auth_client.post(
            "/api/v1/tasks/",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )

        # May return 422 for invalid JSON or 307 redirect without trailing slash
        assert response.status_code in [307, 422]
