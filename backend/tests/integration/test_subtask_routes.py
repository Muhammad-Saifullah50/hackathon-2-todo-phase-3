"""
Integration tests for subtask API routes.

Tests all subtask endpoints with database integration.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.subtask import Subtask
from src.models.user import User


@pytest.mark.asyncio
async def test_create_subtask_success(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test creating a subtask with valid data."""
    # Create parent task
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/subtasks",
        json={"description": "First subtask"}
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]
    assert data["description"] == "First subtask"
    assert data["task_id"] == str(task.id)
    assert data["is_completed"] is False
    assert data["order_index"] == 0


@pytest.mark.asyncio
async def test_get_subtasks(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test retrieving all subtasks for a task."""
    # Create parent task
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create subtasks
    subtask1 = Subtask(
        task_id=task.id,
        description="First subtask",
        order_index=0
    )
    subtask2 = Subtask(
        task_id=task.id,
        description="Second subtask",
        order_index=1
    )
    test_session.add(subtask1)
    test_session.add(subtask2)
    await test_session.commit()

    response = await auth_client.get(
        f"/api/v1/tasks/{task.id}/subtasks"
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["subtasks"]
    assert len(data) == 2
    assert data[0]["description"] == "First subtask"
    assert data[1]["description"] == "Second subtask"


@pytest.mark.asyncio
async def test_toggle_subtask(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test toggling subtask completion status."""
    # Create parent task and subtask
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    subtask = Subtask(
        task_id=task.id,
        description="Test subtask",
        is_completed=False,
        order_index=0
    )
    test_session.add(subtask)
    await test_session.commit()
    await test_session.refresh(subtask)

    response = await auth_client.patch(
        f"/api/v1/subtasks/{subtask.id}/toggle",
        json={"is_completed": True}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]
    assert data["is_completed"] is True


@pytest.mark.asyncio
async def test_toggle_last_subtask_completes_parent(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test that completing last subtask auto-completes parent task."""
    # Create parent task
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create two subtasks, one completed
    subtask1 = Subtask(
        task_id=task.id,
        description="First",
        is_completed=True,
        order_index=0
    )
    subtask2 = Subtask(
        task_id=task.id,
        description="Second",
        is_completed=False,
        order_index=1
    )
    test_session.add(subtask1)
    test_session.add(subtask2)
    await test_session.commit()
    await test_session.refresh(subtask2)

    # Complete last subtask
    response = await auth_client.patch(
        f"/api/v1/subtasks/{subtask2.id}/toggle",
        json={"is_completed": True}
    )

    assert response.status_code == 200

    # Check parent task is completed
    await test_session.refresh(task)
    assert task.status == "completed"
    assert task.completed_at is not None


@pytest.mark.asyncio
async def test_update_subtask(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test updating subtask description."""
    # Create parent task and subtask
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    subtask = Subtask(
        task_id=task.id,
        description="Original description",
        order_index=0
    )
    test_session.add(subtask)
    await test_session.commit()
    await test_session.refresh(subtask)

    response = await auth_client.patch(
        f"/api/v1/subtasks/{subtask.id}",
        json={"description": "Updated description"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_subtask(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test deleting a subtask."""
    # Create parent task and subtask
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    subtask = Subtask(
        task_id=task.id,
        description="Test subtask",
        order_index=0
    )
    test_session.add(subtask)
    await test_session.commit()
    await test_session.refresh(subtask)
    subtask_id = subtask.id

    response = await auth_client.delete(
        f"/api/v1/subtasks/{subtask_id}"
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True

    # Verify subtask is deleted
    deleted_subtask = await test_session.get(Subtask, subtask_id)
    assert deleted_subtask is None


@pytest.mark.asyncio
async def test_reorder_subtasks(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test reordering subtasks."""
    # Create parent task
    task = Task(
        user_id=test_user.id,
        title="Parent Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create subtasks
    subtask1 = Subtask(
        task_id=task.id,
        description="First",
        order_index=0
    )
    subtask2 = Subtask(
        task_id=task.id,
        description="Second",
        order_index=1
    )
    subtask3 = Subtask(
        task_id=task.id,
        description="Third",
        order_index=2
    )
    test_session.add_all([subtask1, subtask2, subtask3])
    await test_session.commit()
    await test_session.refresh(subtask1)
    await test_session.refresh(subtask2)
    await test_session.refresh(subtask3)

    # Reorder: reverse the order
    response = await auth_client.patch(
        f"/api/v1/tasks/{task.id}/subtasks/reorder",
        json={"subtask_ids": [str(subtask3.id), str(subtask2.id), str(subtask1.id)]}
    )

    assert response.status_code == 200

    # Verify new order
    statement = select(Subtask).where(Subtask.task_id == task.id).order_by(Subtask.order_index)
    result = await test_session.execute(statement)
    subtasks = result.scalars().all()
    assert subtasks[0].id == subtask3.id
    assert subtasks[1].id == subtask2.id
    assert subtasks[2].id == subtask1.id


@pytest.mark.asyncio
async def test_subtask_unauthorized(client: AsyncClient):
    """Test subtask operations without authentication fail."""
    response = await client.post(
        "/api/v1/tasks/1/subtasks",
        json={"description": "Test"}
    )

    assert response.status_code == 401
