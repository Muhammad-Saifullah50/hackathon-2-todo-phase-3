"""
Unit tests for TagService.

Tests tag CRUD operations, validation, and business logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.services.tag_service import TagService
from src.models.tag import Tag, TagCreate, TagUpdate
from src.models.task_tag import TaskTag


@pytest.fixture
def mock_db_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def tag_service(mock_db_session):
    """Create TagService instance with mock session."""
    return TagService(session=mock_db_session)


@pytest.fixture
def sample_tag():
    """Create a sample tag for testing."""
    return Tag(
        id=uuid4(),
        user_id="user123",
        name="Work",
        color="#FF5733",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestCreateTag:
    """Tests for create_tag method."""

    @pytest.mark.asyncio
    async def test_create_tag_success(self, tag_service, mock_db_session):
        """Test successful tag creation."""
        # Mock no existing tag
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute.return_value = mock_result

        tag_data = TagCreate(name="Work", color="#FF5733")
        user_id = "user123"

        # Execute
        result = await tag_service.create_tag(tag_data=tag_data, user_id=user_id)

        # Assert
        assert result.name == "Work"
        assert result.color == "#FF5733"
        assert result.user_id == user_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tag_duplicate_name(self, tag_service, mock_db_session, sample_tag):
        """Test creating tag with duplicate name for same user."""
        # Mock existing tag
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_tag)
        mock_db_session.execute.return_value = mock_result

        tag_data = TagCreate(name="Work", color="#FF5733")
        user_id = "user123"

        # Execute and assert
        with pytest.raises(ValueError, match="Tag with name 'Work' already exists"):
            await tag_service.create_tag(tag_data=tag_data, user_id=user_id)


class TestGetTags:
    """Tests for get_tags method."""

    @pytest.mark.asyncio
    async def test_get_tags_success(self, tag_service, mock_db_session, sample_tag):
        """Test retrieving all tags for a user."""
        # Mock query result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tag]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        user_id = "user123"

        # Execute
        tags = await tag_service.get_tags(user_id=user_id)

        # Assert
        assert len(tags) == 1
        assert tags[0].name == "Work"
        assert tags[0].user_id == user_id

    @pytest.mark.asyncio
    async def test_get_tags_empty(self, tag_service, mock_db_session):
        """Test retrieving tags when user has none."""
        # Mock empty result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db_session.execute.return_value = mock_result

        user_id = "user123"

        # Execute
        tags = await tag_service.get_tags(user_id=user_id)

        # Assert
        assert len(tags) == 0


class TestGetTagById:
    """Tests for get_tag_by_id method."""

    @pytest.mark.asyncio
    async def test_get_tag_by_id_success(self, tag_service, mock_db_session, sample_tag):
        """Test retrieving tag by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tag
        mock_db_session.execute.return_value = mock_result

        tag_id = str(sample_tag.id)
        user_id = "user123"

        # Execute
        tag = await tag_service.get_tag_by_id(tag_id=tag_id, user_id=user_id)

        # Assert
        assert tag.id == sample_tag.id
        assert tag.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_tag_by_id_not_found(self, tag_service, mock_db_session):
        """Test retrieving non-existent tag."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        tag_id = str(uuid4())
        user_id = "user123"

        # Execute - returns None when not found
        tag = await tag_service.get_tag_by_id(tag_id=tag_id, user_id=user_id)
        assert tag is None


class TestUpdateTag:
    """Tests for update_tag method."""

    @pytest.mark.asyncio
    async def test_update_tag_name(self, tag_service, mock_db_session, sample_tag):
        """Test updating tag name."""
        # Mock get_tag_by_id (two execute calls: get, and check for name conflicts)
        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = sample_tag

        check_result = MagicMock()
        check_result.scalar_one_or_none.return_value = None

        mock_db_session.execute.side_effect = [get_result, check_result]

        tag_id = str(sample_tag.id)
        user_id = "user123"
        tag_update = TagUpdate(name="Personal")

        # Execute
        updated_tag = await tag_service.update_tag(
            tag_id=tag_id,
            user_id=user_id,
            tag_data=tag_update
        )

        # Assert
        assert updated_tag.name == "Personal"
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()


class TestDeleteTag:
    """Tests for delete_tag method."""

    @pytest.mark.asyncio
    async def test_delete_tag_success(self, tag_service, mock_db_session, sample_tag):
        """Test successful tag deletion."""
        # Mock get_tag_by_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tag
        mock_db_session.execute.return_value = mock_result

        tag_id = str(sample_tag.id)
        user_id = "user123"

        # Execute
        await tag_service.delete_tag(tag_id=tag_id, user_id=user_id)

        # Assert
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestAddTagsToTask:
    """Tests for add_tags_to_task method."""

    @pytest.mark.asyncio
    async def test_add_single_tag_to_task(self, tag_service, mock_db_session, sample_tag):
        """Test adding a single tag to a task."""
        from src.models.task import Task

        task_id = str(uuid4())
        tag_ids = [str(sample_tag.id)]
        user_id = "user123"

        # Mock task check
        task = Task(id=task_id, user_id=user_id, title="Test", status="pending", priority="medium")
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = task

        # Mock tags check
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tag]
        tags_result = MagicMock()
        tags_result.scalars.return_value = mock_scalars

        # Mock existing associations (empty)
        existing_result = MagicMock()
        existing_result.all.return_value = []

        # Mock get_task_tags
        final_scalars = MagicMock()
        final_scalars.all.return_value = [sample_tag]
        final_result = MagicMock()
        final_result.scalars.return_value = final_scalars

        mock_db_session.execute.side_effect = [
            task_result,
            tags_result,
            existing_result,
            final_result
        ]

        # Execute
        result = await tag_service.add_tags_to_task(
            task_id=task_id,
            tag_ids=tag_ids,
            user_id=user_id
        )

        # Assert
        assert len(result) == 1
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()


class TestRemoveTagsFromTask:
    """Tests for remove_tags_from_task method."""

    @pytest.mark.asyncio
    async def test_remove_single_tag_from_task(self, tag_service, mock_db_session, sample_tag):
        """Test removing a single tag from a task."""
        from src.models.task import Task

        task_id = str(uuid4())
        tag_ids = [str(sample_tag.id)]
        user_id = "user123"

        # Mock task check
        task = Task(id=task_id, user_id=user_id, title="Test", status="pending", priority="medium")
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = task

        # Mock associations to delete
        task_tag = TaskTag(task_id=task_id, tag_id=sample_tag.id)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [task_tag]
        assoc_result = MagicMock()
        assoc_result.scalars.return_value = mock_scalars

        # Mock get_task_tags (after deletion)
        final_scalars = MagicMock()
        final_scalars.all.return_value = []
        final_result = MagicMock()
        final_result.scalars.return_value = final_scalars

        mock_db_session.execute.side_effect = [
            task_result,
            assoc_result,
            final_result
        ]

        # Execute
        result = await tag_service.remove_tags_from_task(
            task_id=task_id,
            tag_ids=tag_ids,
            user_id=user_id
        )

        # Assert
        assert len(result) == 0
        mock_db_session.delete.assert_called()
        mock_db_session.commit.assert_called()
