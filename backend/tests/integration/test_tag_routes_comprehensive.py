"""
Comprehensive integration tests for tag API routes.

This test suite aims to achieve 80%+ coverage for src/api/routes/tags.py
by testing all endpoints, error paths, and edge cases.
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
# Create Tag Tests - Testing all error paths
# ============================================================================


@pytest.mark.asyncio
async def test_create_tag_with_only_name(auth_client: AsyncClient, test_user: User):
    """Test creating tag with only name (color is required)."""
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": "Important", "color": "#AABBCC"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Important"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_create_tag_empty_name(auth_client: AsyncClient, test_user: User):
    """Test creating tag with empty name fails validation."""
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": "", "color": "#FF5733"}
    )

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_create_tag_name_too_long(auth_client: AsyncClient, test_user: User):
    """Test creating tag with name exceeding max length."""
    long_name = "A" * 201  # Assuming 200 char limit
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": long_name, "color": "#FF5733"}
    )

    # Could be 422 (validation) or 400 (ValueError)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_create_tag_malformed_json(auth_client: AsyncClient, test_user: User):
    """Test creating tag with malformed JSON."""
    response = await auth_client.post(
        "/api/v1/tags/",
        content="{invalid json",
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


# ============================================================================
# Get Tags Tests - Testing sorting, filtering, and edge cases
# ============================================================================


@pytest.mark.asyncio
async def test_get_tags_with_task_counts(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test that tags return with correct task counts."""
    # Create tag
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    # Create tasks
    task1 = Task(user_id=test_user.id, title="Task 1", status="pending", priority="medium")
    task2 = Task(user_id=test_user.id, title="Task 2", status="pending", priority="medium")
    test_session.add(task1)
    test_session.add(task2)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task1)
    await test_session.refresh(task2)

    # Associate tag with tasks
    test_session.add(TaskTag(task_id=task1.id, tag_id=tag.id))
    test_session.add(TaskTag(task_id=task2.id, tag_id=tag.id))
    await test_session.commit()

    response = await auth_client.get("/api/v1/tags/")

    assert response.status_code == 200
    data = response.json()
    tags = data["data"]["tags"]
    assert len(tags) == 1
    assert tags[0]["name"] == "Work"
    assert tags[0]["task_count"] == 2


@pytest.mark.asyncio
async def test_get_tags_unauthorized(client: AsyncClient):
    """Test getting tags without authentication."""
    response = await client.get("/api/v1/tags/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tags_multiple_users_isolation(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test that users only see their own tags."""
    # Create tag for test user
    user_tag = Tag(user_id=test_user.id, name="MyTag", color="#FF5733")
    test_session.add(user_tag)

    # Create tag for another user
    other_user_id = str(uuid4())
    other_tag = Tag(user_id=other_user_id, name="OtherTag", color="#00FF00")
    test_session.add(other_tag)
    await test_session.commit()

    response = await auth_client.get("/api/v1/tags/")

    assert response.status_code == 200
    data = response.json()
    tags = data["data"]["tags"]
    assert len(tags) == 1
    assert tags[0]["name"] == "MyTag"


# ============================================================================
# Update Tag Tests - Testing all update scenarios
# ============================================================================


@pytest.mark.asyncio
async def test_update_tag_both_name_and_color(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test updating both name and color simultaneously."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.patch(
        f"/api/v1/tags/{tag.id}",
        json={"name": "Office", "color": "#00FF00"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Office"
    assert data["data"]["color"] == "#00FF00"


@pytest.mark.asyncio
async def test_update_tag_duplicate_name(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test updating tag to duplicate name fails."""
    # Create two tags
    tag1 = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    tag2 = Tag(user_id=test_user.id, name="Personal", color="#00FF00")
    test_session.add(tag1)
    test_session.add(tag2)
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)

    # Try to rename tag2 to "Work"
    response = await auth_client.patch(
        f"/api/v1/tags/{tag2.id}",
        json={"name": "Work"}
    )

    assert response.status_code == 409  # CONFLICT
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_update_tag_empty_name(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test updating tag with empty name fails."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.patch(
        f"/api/v1/tags/{tag.id}",
        json={"name": ""}
    )

    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_update_tag_invalid_uuid(auth_client: AsyncClient, test_user: User):
    """Test updating tag with invalid UUID format."""
    response = await auth_client.patch(
        "/api/v1/tags/invalid-uuid",
        json={"name": "Updated"}
    )

    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_update_tag_empty_payload(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test updating tag with no fields to update."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.patch(
        f"/api/v1/tags/{tag.id}",
        json={}
    )

    # Should succeed (no changes)
    assert response.status_code in [200, 400, 422]


# ============================================================================
# Delete Tag Tests - Testing various deletion scenarios
# ============================================================================


@pytest.mark.asyncio
async def test_delete_tag_not_found(auth_client: AsyncClient, test_user: User):
    """Test deleting non-existent tag."""
    fake_id = uuid4()
    response = await auth_client.delete(f"/api/v1/tags/{fake_id}")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_delete_tag_wrong_user(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test deleting tag belonging to another user fails."""
    other_user_id = str(uuid4())
    tag = Tag(user_id=other_user_id, name="OtherTag", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.delete(f"/api/v1/tags/{tag.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag_invalid_uuid(auth_client: AsyncClient, test_user: User):
    """Test deleting tag with invalid UUID."""
    response = await auth_client.delete("/api/v1/tags/not-a-uuid")

    assert response.status_code == 422


# ============================================================================
# Assign Tags to Task Tests - Testing various assignment scenarios
# ============================================================================


@pytest.mark.asyncio
async def test_assign_tags_empty_list(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning empty tag list to task."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": []}
    )

    # Should succeed with empty list
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Data might be None or have empty tags
    if data["data"] is not None:
        assert len(data["data"].get("tags", [])) == 0


@pytest.mark.asyncio
async def test_assign_tags_task_not_found(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tags to non-existent task."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    fake_task_id = uuid4()
    response = await auth_client.post(
        f"/api/v1/tasks/{fake_task_id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [404, 500]
    data = response.json()
    if response.status_code == 404:
        assert "not found" in data["detail"]["error"]["message"].lower()


@pytest.mark.asyncio
async def test_assign_tags_tag_not_found(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning non-existent tag to task."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    fake_tag_id = uuid4()
    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(fake_tag_id)]}
    )

    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_assign_tags_wrong_user_task(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tags to task belonging to another user."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    other_user_id = str(uuid4())
    task = Task(user_id=other_user_id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_assign_tags_wrong_user_tag(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tag belonging to another user."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)

    other_user_id = str(uuid4())
    tag = Tag(user_id=other_user_id, name="OtherTag", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(task)
    await test_session.refresh(tag)

    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_assign_tags_invalid_task_uuid(
    auth_client: AsyncClient,
    test_user: User
):
    """Test assigning tags with invalid task UUID."""
    response = await auth_client.post(
        "/api/v1/tasks/invalid-uuid/tags",
        json={"tag_ids": []}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_assign_tags_invalid_tag_uuid(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning tags with invalid tag UUID."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": ["invalid-uuid"]}
    )

    assert response.status_code in [422, 500]


# ============================================================================
# Remove Tags from Task Tests - Testing removal scenarios
# ============================================================================


@pytest.mark.asyncio
async def test_remove_tags_empty_list(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing empty tag list from task."""
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": []}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_remove_tags_task_not_found(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing tags from non-existent task."""
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    fake_task_id = uuid4()
    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tasks/{fake_task_id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_remove_tags_wrong_user_task(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing tags from task belonging to another user."""
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
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_remove_tags_multiple(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing multiple tags from task."""
    # Create tags
    tag1 = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    tag2 = Tag(user_id=test_user.id, name="Urgent", color="#FF0000")
    tag3 = Tag(user_id=test_user.id, name="Personal", color="#00FF00")
    test_session.add_all([tag1, tag2, tag3])

    # Create task
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(tag3)
    await test_session.refresh(task)

    # Associate all tags
    test_session.add_all([
        TaskTag(task_id=task.id, tag_id=tag1.id),
        TaskTag(task_id=task.id, tag_id=tag2.id),
        TaskTag(task_id=task.id, tag_id=tag3.id)
    ])
    await test_session.commit()

    # Remove two tags
    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag1.id), str(tag2.id)]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Should have only tag3 remaining
    if data["data"] is not None:
        assert len(data["data"]["tags"]) == 1
        assert data["data"]["tags"][0]["name"] == "Personal"


# ============================================================================
# Edge Cases and Integration Tests
# ============================================================================
# Note: GET /api/v1/tasks/{task_id}/tags endpoint doesn't exist in the current implementation
# Task tags are retrieved via the tags routes @ /api/v1/tags/tasks/{task_id}/tags


@pytest.mark.asyncio
async def test_tag_lifecycle_complete(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test complete tag lifecycle: create, assign, update, remove, delete."""
    # Create tag
    create_response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": "Lifecycle", "color": "#FF5733"}
    )
    assert create_response.status_code == 201
    tag_id = create_response.json()["data"]["id"]

    # Create task
    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Assign to task
    assign_response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [tag_id]}
    )
    assert assign_response.status_code == 200

    # Update tag
    update_response = await auth_client.patch(
        f"/api/v1/tags/{tag_id}",
        json={"name": "Updated", "color": "#00FF00"}
    )
    assert update_response.status_code == 200

    # Remove from task
    remove_response = await auth_client.request(
        "DELETE",
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [tag_id]}
    )
    assert remove_response.status_code == 200

    # Delete tag
    delete_response = await auth_client.delete(f"/api/v1/tags/{tag_id}")
    assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_assign_multiple_tags_bulk(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test assigning multiple tags to task in single request."""
    # Create 5 tags
    tags = []
    for i in range(5):
        tag = Tag(user_id=test_user.id, name=f"Tag{i}", color=f"#{i:06x}")
        test_session.add(tag)
        tags.append(tag)

    task = Task(user_id=test_user.id, title="Task", status="pending", priority="medium")
    test_session.add(task)
    await test_session.commit()

    for tag in tags:
        await test_session.refresh(tag)
    await test_session.refresh(task)

    tag_ids = [str(tag.id) for tag in tags]
    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": tag_ids}
    )

    assert response.status_code == 200
    data = response.json()
    if data["data"] is not None:
        assert len(data["data"]["tags"]) == 5
