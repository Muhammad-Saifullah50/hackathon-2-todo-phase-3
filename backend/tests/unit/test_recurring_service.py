"""
Unit tests for RecurringService.

Tests recurrence pattern creation, next occurrence calculation, and instance generation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.services.recurring_service import RecurringService
from src.models.recurrence_pattern import RecurrencePattern
from src.models.task import Task
from src.schemas.recurring_schemas import RecurrencePatternCreate, RecurrencePatternUpdate


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
    return session


@pytest.fixture
def recurring_service(mock_db_session):
    """Create RecurringService instance with mock session."""
    return RecurringService(db=mock_db_session)


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        id=uuid4(),
        user_id="user123",
        title="Recurring Task",
        status="pending",
        priority="medium",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestCalculateNextOccurrence:
    """Tests for _calculate_next_occurrence method."""

    def test_calculate_daily_recurrence(self, recurring_service):
        """Test calculating next occurrence for daily recurrence."""
        start_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        frequency = "daily"
        interval = 1

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval
        )

        expected = datetime(2025, 1, 2, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_daily_recurrence_with_interval(self, recurring_service):
        """Test calculating next occurrence for daily recurrence with interval."""
        start_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        frequency = "daily"
        interval = 3

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval
        )

        expected = datetime(2025, 1, 4, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_weekly_recurrence(self, recurring_service):
        """Test calculating next occurrence for weekly recurrence."""
        start_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)  # Wednesday
        frequency = "weekly"
        interval = 1

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval
        )

        expected = datetime(2025, 1, 8, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_monthly_recurrence(self, recurring_service):
        """Test calculating next occurrence for monthly recurrence."""
        start_date = datetime(2025, 1, 15, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 1

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=15
        )

        expected = datetime(2025, 2, 15, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_monthly_recurrence_with_interval(self, recurring_service):
        """Test calculating next occurrence for monthly recurrence with interval."""
        start_date = datetime(2025, 1, 15, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 3

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=15
        )

        expected = datetime(2025, 4, 15, 9, 0, tzinfo=timezone.utc)
        assert result == expected


class TestCreateRecurrencePattern:
    """Tests for create_recurrence_pattern method."""

    @pytest.mark.asyncio
    async def test_create_daily_recurrence(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test creating daily recurrence pattern."""
        # Mock task get
        mock_db_session.get = AsyncMock(return_value=sample_task)

        # Mock no existing pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        pattern_data = RecurrencePatternCreate(
            frequency="daily",
            interval=1
        )
        task_id = sample_task.id

        result = await recurring_service.create_recurrence_pattern(
            task_id=task_id,
            pattern_data=pattern_data
        )

        assert result.frequency == "daily"
        assert result.interval == 1
        assert result.task_id == task_id
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_weekly_recurrence_with_days(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test creating weekly recurrence with specific days of week."""
        # Mock task get
        mock_db_session.get = AsyncMock(return_value=sample_task)

        # Mock no existing pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        pattern_data = RecurrencePatternCreate(
            frequency="weekly",
            interval=1,
            days_of_week=[1, 3, 5]  # Monday, Wednesday, Friday
        )
        task_id = sample_task.id

        result = await recurring_service.create_recurrence_pattern(
            task_id=task_id,
            pattern_data=pattern_data
        )

        assert result.frequency == "weekly"
        assert result.days_of_week == [1, 3, 5]
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_recurrence_with_end_date(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test creating recurrence pattern with end date."""
        # Mock task get
        mock_db_session.get = AsyncMock(return_value=sample_task)

        # Mock no existing pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        end_date = datetime.now(timezone.utc) + timedelta(days=30)
        pattern_data = RecurrencePatternCreate(
            frequency="daily",
            interval=1,
            end_date=end_date
        )
        task_id = sample_task.id

        result = await recurring_service.create_recurrence_pattern(
            task_id=task_id,
            pattern_data=pattern_data
        )

        assert result.end_date == end_date

    @pytest.mark.asyncio
    async def test_create_recurrence_pattern_already_exists(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test creating recurrence pattern when one already exists."""
        # Mock task get
        mock_db_session.get = AsyncMock(return_value=sample_task)

        # Mock existing pattern
        existing_pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        pattern_data = RecurrencePatternCreate(
            frequency="weekly",
            interval=1
        )
        task_id = sample_task.id

        with pytest.raises(ValueError, match="already has a recurrence pattern"):
            await recurring_service.create_recurrence_pattern(
                task_id=task_id,
                pattern_data=pattern_data
            )


class TestGetRecurrencePattern:
    """Tests for get_recurrence_pattern method."""

    @pytest.mark.asyncio
    async def test_get_recurrence_pattern_success(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test retrieving recurrence pattern."""
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc) + timedelta(days=1)
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await recurring_service.get_recurrence_pattern(task_id=sample_task.id)

        assert result is not None
        assert result.task_id == sample_task.id
        assert result.frequency == "daily"


class TestUpdateRecurrencePattern:
    """Tests for update_recurrence_pattern method."""

    @pytest.mark.asyncio
    async def test_update_recurrence_frequency(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test updating recurrence frequency."""
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc)
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        pattern_update = RecurrencePatternUpdate(frequency="weekly")

        result = await recurring_service.update_recurrence_pattern(
            task_id=sample_task.id,
            pattern_data=pattern_update
        )

        assert result.frequency == "weekly"
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_recurrence_interval(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test updating recurrence interval."""
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc)
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        pattern_update = RecurrencePatternUpdate(interval=3)

        result = await recurring_service.update_recurrence_pattern(
            task_id=sample_task.id,
            pattern_data=pattern_update
        )

        assert result.interval == 3


class TestDeleteRecurrencePattern:
    """Tests for delete_recurrence_pattern method."""

    @pytest.mark.asyncio
    async def test_delete_recurrence_pattern(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test deleting recurrence pattern."""
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc)
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await recurring_service.delete_recurrence_pattern(task_id=sample_task.id)

        assert result is True
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_recurrence_pattern_not_found(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test deleting non-existent pattern."""
        # Mock pattern not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await recurring_service.delete_recurrence_pattern(task_id=sample_task.id)

        assert result is False


class TestGenerateNextInstance:
    """Tests for generate_next_instance method."""

    @pytest.mark.asyncio
    async def test_generate_next_instance(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test generating next recurring task instance."""
        # Create recurrence pattern
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc) + timedelta(days=1)
        )

        # Mock get pattern
        pattern_result = MagicMock()
        pattern_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=pattern_result)

        # Mock get task
        mock_db_session.get = AsyncMock(return_value=sample_task)

        result = await recurring_service.generate_next_instance(task_id=sample_task.id)

        # Should create new task and update pattern
        assert mock_db_session.add.call_count == 2  # new task + updated pattern
        assert mock_db_session.commit.called

    @pytest.mark.asyncio
    async def test_generate_next_instance_past_end_date(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test generating instance when past end date."""
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc) + timedelta(days=1),
            end_date=datetime.now(timezone.utc) - timedelta(days=1)  # Past end date
        )

        # Mock get pattern
        pattern_result = MagicMock()
        pattern_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=pattern_result)

        # Mock get task
        mock_db_session.get = AsyncMock(return_value=sample_task)

        result = await recurring_service.generate_next_instance(task_id=sample_task.id)

        # Should not create new instance
        assert result is None
