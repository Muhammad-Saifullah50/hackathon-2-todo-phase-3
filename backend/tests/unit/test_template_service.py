"""
Unit tests for TemplateService.

Tests template CRUD operations and apply template logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.services.template_service import TemplateService
from src.models.task_template import TaskTemplate
from src.models.task import Task
from src.schemas.template_schemas import TemplateCreate, TemplateUpdate


@pytest.fixture
def mock_db_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.get = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def template_service(mock_db_session):
    """Create TemplateService instance with mock session."""
    return TemplateService(db=mock_db_session)


@pytest.fixture
def sample_template():
    """Create a sample template for testing."""
    return TaskTemplate(
        id=str(uuid4()),
        user_id="user123",
        name="Weekly Report Template",
        title="Weekly Report",
        description="Create weekly status report",
        priority="high",
        subtasks_template=[
            {"description": "Review metrics"},
            {"description": "Write summary"},
            {"description": "Send to team"}
        ],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestCreateTemplate:
    """Tests for create_template method."""

    @pytest.mark.asyncio
    async def test_create_template_success(self, template_service, mock_db_session):
        """Test successful template creation."""
        from src.schemas.template_schemas import SubtaskTemplateItem

        template_data = TemplateCreate(
            name="Weekly Report",
            title="Weekly Report",
            description="Create report",
            priority="high",
            subtasks_template=[
                SubtaskTemplateItem(description="Step 1"),
                SubtaskTemplateItem(description="Step 2")
            ]
        )
        user_id = "user123"

        result = await template_service.create_template(
            user_id=user_id,
            template_data=template_data
        )

        assert result.name == "Weekly Report"
        assert result.title == "Weekly Report"
        assert result.priority == "high"
        assert len(result.subtasks_template) == 2
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_template_minimal(self, template_service, mock_db_session):
        """Test creating template with minimal fields."""
        template_data = TemplateCreate(
            name="Simple Template",
            title="Simple Task",
            priority="medium"
        )
        user_id = "user123"

        result = await template_service.create_template(
            user_id=user_id,
            template_data=template_data
        )

        assert result.name == "Simple Template"
        assert result.description is None


class TestGetTemplates:
    """Tests for get_templates method."""

    @pytest.mark.asyncio
    async def test_get_templates_success(
        self,
        template_service,
        mock_db_session,
        sample_template
    ):
        """Test retrieving all templates for a user."""
        # Mock templates query
        templates_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_template]
        templates_result.scalars.return_value = mock_scalars

        # Mock count query
        count_result = MagicMock()
        count_scalars = MagicMock()
        count_scalars.all.return_value = [sample_template]
        count_result.scalars.return_value = count_scalars

        mock_db_session.execute.side_effect = [templates_result, count_result]

        user_id = "user123"

        templates, total = await template_service.get_templates(user_id=user_id)

        assert len(templates) == 1
        assert total == 1
        assert templates[0].name == "Weekly Report Template"

    @pytest.mark.asyncio
    async def test_get_templates_empty(self, template_service, mock_db_session):
        """Test retrieving templates when user has none."""
        # Mock empty templates query
        templates_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        templates_result.scalars.return_value = mock_scalars

        # Mock empty count query
        count_result = MagicMock()
        count_scalars = MagicMock()
        count_scalars.all.return_value = []
        count_result.scalars.return_value = count_scalars

        mock_db_session.execute.side_effect = [templates_result, count_result]

        user_id = "user123"

        templates, total = await template_service.get_templates(user_id=user_id)

        assert len(templates) == 0
        assert total == 0


class TestGetTemplate:
    """Tests for get_template method."""

    @pytest.mark.asyncio
    async def test_get_template_success(
        self,
        template_service,
        mock_db_session,
        sample_template
    ):
        """Test retrieving a single template."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_template)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        template_id = sample_template.id
        user_id = "user123"

        result = await template_service.get_template(
            template_id=template_id,
            user_id=user_id
        )

        assert result is not None
        assert result.id == sample_template.id
        assert result.name == "Weekly Report Template"


class TestApplyTemplate:
    """Tests for apply_template method."""

    @pytest.mark.asyncio
    async def test_apply_template_creates_task(
        self,
        template_service,
        mock_db_session,
        sample_template
    ):
        """Test applying template creates a task with template data."""
        # Mock get_template
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_template)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        template_id = sample_template.id
        user_id = "user123"

        result = await template_service.apply_template(
            template_id=template_id,
            user_id=user_id
        )

        # Should create task with template fields
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_apply_template_not_found(
        self,
        template_service,
        mock_db_session
    ):
        """Test applying non-existent template."""
        # Mock template not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        template_id = str(uuid4())
        user_id = "user123"

        result = await template_service.apply_template(
            template_id=template_id,
            user_id=user_id
        )

        assert result is None


class TestUpdateTemplate:
    """Tests for update_template method."""

    @pytest.mark.asyncio
    async def test_update_template_name(
        self,
        template_service,
        mock_db_session,
        sample_template
    ):
        """Test updating template name."""
        # Mock get_template
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_template)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        template_id = sample_template.id
        user_id = "user123"
        template_update = TemplateUpdate(name="Updated Name")

        result = await template_service.update_template(
            template_id=template_id,
            user_id=user_id,
            template_data=template_update
        )

        assert result.name == "Updated Name"
        mock_db_session.commit.assert_called_once()


class TestDeleteTemplate:
    """Tests for delete_template method."""

    @pytest.mark.asyncio
    async def test_delete_template_success(
        self,
        template_service,
        mock_db_session,
        sample_template
    ):
        """Test successful template deletion."""
        # Mock get_template
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_template)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        template_id = sample_template.id
        user_id = "user123"

        result = await template_service.delete_template(
            template_id=template_id,
            user_id=user_id
        )

        assert result is True
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestSaveTaskAsTemplate:
    """Tests for save_task_as_template method."""

    @pytest.mark.asyncio
    async def test_save_task_as_template(
        self,
        template_service,
        mock_db_session
    ):
        """Test saving a task as a template."""
        # Create a task
        task = Task(
            id=str(uuid4()),
            user_id="user123",
            title="Task to Save",
            description="Description",
            priority="high",
            status="pending"
        )

        # Mock TaskService.get_task
        from unittest.mock import patch
        with patch('src.services.task_service.TaskService') as MockTaskService:
            mock_task_service = MockTaskService.return_value
            mock_task_service.get_task = AsyncMock(return_value=task)

            task_id = task.id
            template_name = "New Template"
            user_id = "user123"

            result = await template_service.save_task_as_template(
                task_id=task_id,
                template_name=template_name,
                user_id=user_id,
                include_subtasks=False,
                include_tags=False
            )

            # Should create template
            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_called()
