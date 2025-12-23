"""
Integration tests for search API routes.

Tests search functionality with filters, autocomplete, and quick filters.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from src.models.user import User


@pytest.mark.asyncio
async def test_search_tasks_by_title(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test searching tasks by title."""
    # Create tasks with different titles
    task1 = Task(
        user_id=test_user.id,
        title="Buy groceries",
        status="pending",
        priority="medium"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Buy flowers",
        status="pending",
        priority="low"
    )
    task3 = Task(
        user_id=test_user.id,
        title="Write report",
        status="pending",
        priority="high"
    )
    test_session.add_all([task1, task2, task3])
    await test_session.commit()

    # Search for "buy"
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "buy"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) >= 2  # Should find "Buy groceries" and "Buy flowers"
    titles = [task["title"] for task in data]
    assert "Buy groceries" in titles
    assert "Buy flowers" in titles
    assert "Write report" not in titles


@pytest.mark.asyncio
async def test_search_tasks_by_description(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test searching tasks by description."""
    task1 = Task(
        user_id=test_user.id,
        title="Task 1",
        description="Important meeting notes",
        status="pending",
        priority="medium"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Task 2",
        description="Random stuff",
        status="pending",
        priority="low"
    )
    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search for "meeting"
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "meeting"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["description"] == "Important meeting notes"


@pytest.mark.asyncio
async def test_search_with_status_filter(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test searching with status filter."""
    task1 = Task(
        user_id=test_user.id,
        title="Buy groceries",
        status="pending",
        priority="medium"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Buy flowers",
        status="completed",
        priority="low",
        completed_at=datetime.now(timezone.utc)
    )
    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search for "buy" with status=pending
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "buy", "status": "pending"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["title"] == "Buy groceries"
    assert data[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_search_with_priority_filter(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test searching with priority filter."""
    task1 = Task(
        user_id=test_user.id,
        title="Important task",
        status="pending",
        priority="high"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Important meeting",
        status="pending",
        priority="low"
    )
    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search for "important" with priority=high
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "important", "priority": "high"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["priority"] == "high"


@pytest.mark.asyncio
async def test_search_with_tag_filter(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test searching with tag filter."""
    # Create tag
    tag = Tag(user_id=test_user.id, name="Work", color="#FF5733")
    test_session.add(tag)

    # Create tasks
    task1 = Task(
        user_id=test_user.id,
        title="Work task",
        status="pending",
        priority="medium"
    )
    task2 = Task(
        user_id=test_user.id,
        title="Work meeting",
        status="pending",
        priority="high"
    )
    test_session.add_all([task1, task2])
    await test_session.commit()
    await test_session.refresh(tag)
    await test_session.refresh(task1)

    # Associate tag with first task only
    task_tag = TaskTag(task_id=task1.id, tag_id=tag.id)
    test_session.add(task_tag)
    await test_session.commit()

    # Search for "work" with tag filter
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "work", "tags": str(tag.id)}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["id"] == str(task1.id)


@pytest.mark.asyncio
async def test_search_with_due_date_filter(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test searching with due date range filter."""
    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)

    task1 = Task(
        user_id=test_user.id,
        title="Due today",
        status="pending",
        priority="medium",
        due_date=datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    )
    task2 = Task(
        user_id=test_user.id,
        title="Due next week",
        status="pending",
        priority="medium",
        due_date=datetime.combine(today + timedelta(days=7), datetime.min.time(), tzinfo=timezone.utc)
    )
    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search with due date from today to tomorrow
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={
            "due_date_from": today.isoformat(),
            "due_date_to": tomorrow.isoformat()
        }
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["title"] == "Due today"


@pytest.mark.asyncio
async def test_search_case_insensitive(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test that search is case-insensitive."""
    task = Task(
        user_id=test_user.id,
        title="IMPORTANT TASK",
        status="pending",
        priority="high"
    )
    test_session.add(task)
    await test_session.commit()

    # Search with lowercase
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "important"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["title"] == "IMPORTANT TASK"


@pytest.mark.asyncio
async def test_search_partial_match(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test that search matches partial words."""
    task = Task(
        user_id=test_user.id,
        title="Understanding Python",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()

    # Search for partial word
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "under"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["title"] == "Understanding Python"


@pytest.mark.asyncio
async def test_search_with_pagination(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test search with pagination."""
    # Create 25 tasks with "test" in title
    tasks = [
        Task(
            user_id=test_user.id,
            title=f"Test task {i}",
            status="pending",
            priority="medium"
        )
        for i in range(25)
    ]
    test_session.add_all(tasks)
    await test_session.commit()

    # Search with pagination
    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "test", "page": 1, "limit": 10}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) <= 10


@pytest.mark.asyncio
async def test_search_autocomplete(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test search autocomplete suggestions."""
    tasks = [
        Task(user_id=test_user.id, title="Buy groceries", status="pending", priority="medium"),
        Task(user_id=test_user.id, title="Buy flowers", status="pending", priority="low"),
        Task(user_id=test_user.id, title="Write report", status="pending", priority="high"),
    ]
    test_session.add_all(tasks)
    await test_session.commit()

    response = await auth_client.get(
        "/api/v1/tasks/autocomplete",
        params={"q": "bu"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["suggestions"]
    assert len(data) >= 2
    suggestions = [item["title"] for item in data]
    assert "Buy groceries" in suggestions
    assert "Buy flowers" in suggestions


@pytest.mark.asyncio
async def test_quick_filters_endpoint(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test quick filters endpoint returns filter options with counts."""
    today = datetime.now(timezone.utc).date()

    # Create tasks with different statuses and due dates
    tasks = [
        Task(user_id=test_user.id, title="Task 1", status="pending", priority="high",
             due_date=datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)),
        Task(user_id=test_user.id, title="Task 2", status="pending", priority="high"),
        Task(user_id=test_user.id, title="Task 3", status="completed", priority="medium",
             completed_at=datetime.now(timezone.utc)),
        Task(user_id=test_user.id, title="Task 4", status="pending", priority="low",
             due_date=datetime.combine(today - timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)),
    ]
    test_session.add_all(tasks)
    await test_session.commit()

    response = await auth_client.get(
        "/api/v1/tasks/quick-filters"
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    filters = response_data["data"]["filters"]

    # Convert list of filters to dict for easier testing
    filter_dict = {f["id"]: f["count"] for f in filters}

    # Should return counts for different quick filters
    assert "today" in filter_dict
    assert "this_week" in filter_dict
    assert "high_priority" in filter_dict
    assert "overdue" in filter_dict

    assert filter_dict["today"] == 1  # One task due today
    assert filter_dict["high_priority"] == 2  # Two high priority tasks
    assert filter_dict["overdue"] == 1  # One task overdue


@pytest.mark.asyncio
async def test_search_empty_query(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test search with empty query returns all tasks."""
    tasks = [
        Task(user_id=test_user.id, title="Task 1", status="pending", priority="medium"),
        Task(user_id=test_user.id, title="Task 2", status="pending", priority="low"),
    ]
    test_session.add_all(tasks)
    await test_session.commit()

    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": ""}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 2


@pytest.mark.asyncio
async def test_search_no_results(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test search with no matching results."""
    task = Task(
        user_id=test_user.id,
        title="Buy groceries",
        status="pending",
        priority="medium"
    )
    test_session.add(task)
    await test_session.commit()

    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "nonexistent"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 0


@pytest.mark.asyncio
async def test_search_filters_by_user(
    auth_client: AsyncClient,
    test_user: User,
    test_session: AsyncSession
):
    """Test that search only returns current user's tasks."""
    # Create tasks for different users
    task1 = Task(user_id=test_user.id, title="My task", status="pending", priority="medium")
    task2 = Task(user_id="other_user", title="My task", status="pending", priority="medium")
    test_session.add_all([task1, task2])
    await test_session.commit()

    response = await auth_client.get(
        "/api/v1/tasks/search",
        params={"q": "my"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] is True
    data = response_data["data"]["tasks"]
    assert len(data) == 1
    assert data[0]["user_id"] == test_user.id
