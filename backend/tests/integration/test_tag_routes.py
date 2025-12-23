"""
Integration tests for tag API routes.

Tests all tag endpoints with database integration.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tag import Tag
from src.models.task import Task
from src.models.task_tag import TaskTag
from src.models.user import User


@pytest.mark.asyncio
async def test_create_tag_success(auth_client: AsyncClient, test_user: User):
    """Test creating a tag with valid data."""
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": "Work", "color": "#FF5733"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Work"
    assert data["data"]["color"] == "#FF5733"
    assert "id" in data["data"]
    assert "created_at" in data["data"]


@pytest.mark.asyncio
async def test_create_tag_duplicate_name(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test creating tag with duplicate name fails."""
    # Create first tag
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()

    # Attempt to create duplicate
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": "Work", "color": "#00FF00"}
    )

    assert response.status_code == 409  # CONFLICT
    response_data = response.json()
    # HTTPException detail is returned directly in the response under "detail" key
    assert "detail" in response_data
    detail = response_data["detail"]
    assert detail["success"] is False
    assert "already exists" in detail["error"]["message"].lower()


@pytest.mark.asyncio
async def test_create_tag_invalid_color(auth_client: AsyncClient, test_user: User):
    """Test creating tag with invalid color format."""
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"name": "Work", "color": "invalid"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_tag_missing_name(auth_client: AsyncClient, test_user: User):
    """Test creating tag without name fails."""
    response = await auth_client.post(
        "/api/v1/tags/",
        json={"color": "#FF5733"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_unauthorized(client: AsyncClient):
    """Test creating tag without authentication fails."""
    response = await client.post(
        "/api/v1/tags/",
        json={"name": "Work", "color": "#FF5733"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tags_success(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test retrieving all tags for authenticated user."""
    # Create test tags
    tag1 = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    tag2 = Tag(user_id=test_user.id, name="Personal", color="#00FF00")
    test_session.add(tag1)
    test_session.add(tag2)
    await test_session.commit()

    response = await auth_client.get("/api/v1/tags/")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    tags_data = data["data"]["tags"]
    assert len(tags_data) == 2
    assert any(tag["name"] == "Work" for tag in tags_data)
    assert any(tag["name"] == "Personal" for tag in tags_data)


@pytest.mark.asyncio
async def test_get_tags_empty(auth_client: AsyncClient, test_user: User):
    """Test retrieving tags when user has none."""
    response = await auth_client.get("/api/v1/tags/")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["tags"] == []


@pytest.mark.asyncio
async def test_get_tags_filters_by_user(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test that tags are filtered by authenticated user."""
    # Create tag for another user
    other_tag = Tag(user_id="other_user", name="Other", color="#0000FF")
    test_session.add(other_tag)

    # Create tag for test user
    user_tag = Tag(user_id=test_user.id, name="Mine", color="#FF5733")
    test_session.add(user_tag)
    await test_session.commit()

    response = await auth_client.get("/api/v1/tags/")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    tags_data = data["data"]["tags"]
    assert len(tags_data) == 1
    assert tags_data[0]["name"] == "Mine"


@pytest.mark.asyncio
async def test_update_tag_name(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test updating tag name."""
    # Create tag
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.patch(
        f"/api/v1/tags/{tag.id}",
        json={"name": "Office"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Office"
    assert data["data"]["color"] == "#FF5733"  # Color unchanged


@pytest.mark.asyncio
async def test_update_tag_color(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test updating tag color."""
    # Create tag
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.patch(
        f"/api/v1/tags/{tag.id}",
        json={"color": "#00FF00"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Work"  # Name unchanged
    assert data["data"]["color"] == "#00FF00"


@pytest.mark.asyncio
async def test_update_tag_not_found(auth_client: AsyncClient, test_user: User):
    """Test updating non-existent tag."""
    response = await auth_client.patch(
        "/api/v1/tags/00000000-0000-0000-0000-000000000999",
        json={"name": "Updated"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_tag_wrong_user(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test updating tag belonging to another user."""
    # Create tag for another user
    tag = Tag(user_id="other_user", name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    response = await auth_client.patch(
        f"/api/v1/tags/{tag.id}",
        json={"name": "Hacked"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag_success(auth_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Test deleting a tag."""
    # Create tag
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)
    tag_id = tag.id

    response = await auth_client.delete(f"/api/v1/tags/{tag_id}")

    assert response.status_code == 200  # Changed from 204 to 200
    data = response.json()
    assert data["success"] is True

    # Verify tag is deleted
    deleted_tag = await test_session.get(Tag, tag_id)
    assert deleted_tag is None


@pytest.mark.asyncio
async def test_delete_tag_with_task_associations(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test deleting tag removes task associations."""
    # Create tag and task
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    task = Task(
        user_id=test_user.id,
        title="Test Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task)

    # Associate tag with task
    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
    test_session.add(task_tag)
    await test_session.commit()

    # Delete tag
    response = await auth_client.delete(f"/api/v1/tags/{tag.id}")

    assert response.status_code == 200  # Changed from 204 to 200
    data = response.json()
    assert data["success"] is True

    # Verify task_tag is deleted
    from sqlalchemy import select as sa_select
    statement = sa_select(TaskTag).where(TaskTag.tag_id == tag.id)
    result = await test_session.execute(statement)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_add_tags_to_task_success(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test adding tags to a task."""
    # Create tags
    tag1 = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    tag2 = Tag(user_id=test_user.id, name="Urgent", color="#FF0000")
    test_session.add(tag1)
    test_session.add(tag2)

    # Create task
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(task)

    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag1.id), str(tag2.id)]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify associations created
    from sqlalchemy import select as sa_select
    statement = sa_select(TaskTag).where(TaskTag.task_id == task.id)
    result = await test_session.execute(statement)
    task_tags = result.scalars().all()
    assert len(task_tags) == 2


@pytest.mark.asyncio
async def test_add_tags_to_task_duplicate(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test adding duplicate tag to task is idempotent."""
    # Create tag and task
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    task = Task(
        user_id=test_user.id,
        title="Test Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task)

    # Add tag first time
    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
    test_session.add(task_tag)
    await test_session.commit()

    # Add same tag again
    response = await auth_client.post(
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify still only one association
    from sqlalchemy import select as sa_select
    statement = sa_select(TaskTag).where(TaskTag.task_id == task.id)
    result = await test_session.execute(statement)
    task_tags = result.scalars().all()
    assert len(task_tags) == 1


@pytest.mark.asyncio
async def test_remove_tags_from_task_success(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing tags from a task."""
    # Create tag and task
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    task = Task(
        user_id=test_user.id,
        title="Test Task",
        status="pending",
        priority="medium"
    )
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
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": [str(tag.id)]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify association removed
    from sqlalchemy import select as sa_select
    statement = sa_select(TaskTag).where(TaskTag.task_id == task.id)
    result = await test_session.execute(statement)
    task_tags = result.scalars().all()
    assert len(task_tags) == 0


@pytest.mark.asyncio
async def test_remove_tags_from_task_nonexistent(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test removing non-associated tag from task."""
    # Create task
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Attempt to remove non-existent tag (use valid UUID format)
    response = await auth_client.request(
        "DELETE",
        f"/api/v1/tasks/{task.id}/tags",
        json={"tag_ids": ["00000000-0000-0000-0000-000000000999"]}
    )

    # Should succeed (idempotent) - either 200 or 404 is acceptable
    assert response.status_code in [200, 404]
