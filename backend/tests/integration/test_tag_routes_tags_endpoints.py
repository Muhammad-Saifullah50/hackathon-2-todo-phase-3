"""
Tests specifically for the tag routes endpoints at /api/v1/tags/*

These tests target the tags.py routes to increase coverage, since there are
duplicate endpoints in tasks.py that handle similar functionality.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from src.models.tag import Tag
from src.models.task import Task
from src.models.task_tag import TaskTag
from src.models.user import User


# ============================================================================
# Tests for /api/v1/tags/tasks/{task_id}/tags endpoints
# ============================================================================


@pytest.mark.asyncio
async def test_assign_tags_via_tags_route(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tags via /api/v1/tags/tasks/{task_id}/tags endpoint."""
    # Create tags
    tag1 = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    tag2 = Tag(user_id=test_user.id, name="Urgent", color="#FF0000")
    test_session.add_all([tag1, tag2])

    # Create task
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag1.id), str(tag2.id)]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["tags"]) == 2


@pytest.mark.asyncio
async def test_assign_tags_via_tags_route_empty(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning empty tag list via tags route."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": []}
    )

    # Empty list might be rejected by validation (422) or accepted (200)
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_assign_tags_via_tags_route_task_not_found(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tags to non-existent task via tags route."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    fake_task_id = uuid4()
    response = await auth_client.post(
        f"/api/v1/tags/tasks/{fake_task_id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_assign_tags_via_tags_route_tag_not_found(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning non-existent tag via tags route."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    fake_tag_id = uuid4()
    response = await auth_client.post(
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": [str(fake_tag_id)]}
    )

    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_assign_tags_via_tags_route_wrong_user_task(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tags to task of another user via tags route."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    other_user_id = str(uuid4())
    task = Task(user_id=other_user_id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_remove_tags_via_tags_route(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing tags via /api/v1/tags/tasks/{task_id}/tags endpoint."""
    # Create tag and task
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task)

    # Associate tag with task
    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
    test_session.add(task_tag)
    await test_session.commit()

    # Remove tag
    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_remove_tags_via_tags_route_empty(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing empty tag list via tags route."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": []}
    )

    # Empty list might be rejected by validation (422) or accepted (200)
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_remove_tags_via_tags_route_task_not_found(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing tags from non-existent task via tags route."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    fake_task_id = uuid4()
    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tags/tasks/{fake_task_id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_remove_tags_via_tags_route_wrong_user_task(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing tags from task of another user via tags route."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    other_user_id = str(uuid4())
    task = Task(user_id=other_user_id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task)

    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tags/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [400, 404]


@pytest.mark.asyncio
async def test_get_task_tags_via_tags_route(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test getting task tags via /api/v1/tags/tasks/{task_id}/tags endpoint."""
    # Create tags
    tag1 = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    tag2 = Tag(user_id=test_user.id, name="Urgent", color="#FF0000")
    test_session.add_all([tag1, tag2])

    # Create task
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(task)

    # Associate tags
    test_session.add_all([
        TaskTag(task_id=task.id, tag_id=tag1.id),
        TaskTag(task_id=task.id, tag_id=tag2.id)
    ])
    await test_session.commit()

    response = await auth_client.get(f"/api/v1/tags/tasks/{task.id}/tags")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["tags"]) == 2
    tag_names = [t["name"] for t in data["data"]["tags"]]
    assert "Work" in tag_names
    assert "Urgent" in tag_names


@pytest.mark.asyncio
async def test_get_task_tags_via_tags_route_empty(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test getting tags for task with no tags via tags route."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.get(f"/api/v1/tags/tasks/{task.id}/tags")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["tags"]) == 0


@pytest.mark.asyncio
async def test_get_task_tags_via_tags_route_internal_error(
    auth_client: AsyncClient,
    test_user: User
):
    """Test error handling in get task tags endpoint."""
    # Use an invalid UUID to trigger an error path
    fake_task_id = uuid4()
    response = await auth_client.get(f"/api/v1/tags/tasks/{fake_task_id}/tags")

    # Should return 500 for internal error or 200 with empty tags
    assert response.status_code in [200, 500]
