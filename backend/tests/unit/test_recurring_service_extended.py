"""
Extended unit tests for RecurringService to increase coverage to 80%+.

Focuses on edge cases, error conditions, and complex date calculations.
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


class TestCreateRecurrencePatternEdgeCases:
    """Tests for create_recurrence_pattern edge cases."""

    @pytest.mark.asyncio
    async def test_create_recurrence_pattern_task_not_found(
        self,
        recurring_service,
        mock_db_session
    ):
        """Test creating recurrence pattern when task doesn't exist."""
        # Mock task not found
        mock_db_session.get = AsyncMock(return_value=None)

        pattern_data = RecurrencePatternCreate(
            frequency="daily",
            interval=1
        )
        task_id = uuid4()

        with pytest.raises(ValueError, match="not found"):
            await recurring_service.create_recurrence_pattern(
                task_id=task_id,
                pattern_data=pattern_data
            )


class TestUpdateRecurrencePatternEdgeCases:
    """Tests for update_recurrence_pattern edge cases."""

    @pytest.mark.asyncio
    async def test_update_recurrence_pattern_not_found(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test updating non-existent recurrence pattern."""
        # Mock pattern not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        pattern_update = RecurrencePatternUpdate(frequency="weekly")

        with pytest.raises(ValueError, match="No recurrence pattern found"):
            await recurring_service.update_recurrence_pattern(
                task_id=sample_task.id,
                pattern_data=pattern_update
            )


class TestPreviewOccurrences:
    """Tests for preview_occurrences method."""

    @pytest.mark.asyncio
    async def test_preview_occurrences_pattern_not_found(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test previewing occurrences when pattern doesn't exist."""
        # Mock pattern not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="No recurrence pattern found"):
            await recurring_service.preview_occurrences(task_id=sample_task.id)

    @pytest.mark.asyncio
    async def test_preview_occurrences_daily(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test previewing daily occurrences."""
        next_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=next_date
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await recurring_service.preview_occurrences(
            task_id=sample_task.id,
            count=5
        )

        assert result.count == 5
        assert len(result.dates) == 5
        # Verify dates are sequential
        for i in range(len(result.dates) - 1):
            diff = (result.dates[i + 1] - result.dates[i]).days
            assert diff == 1

    @pytest.mark.asyncio
    async def test_preview_occurrences_with_end_date(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test previewing occurrences stops at end date."""
        next_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 2, 9, 0, tzinfo=timezone.utc)  # Should include Jan 1, 2 but not 3
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=next_date,
            end_date=end_date
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await recurring_service.preview_occurrences(
            task_id=sample_task.id,
            count=5  # Request 5 but should only get 2
        )

        # Should stop at end_date (only 2 occurrences: Jan 1, Jan 2)
        assert result.count == 2
        assert len(result.dates) == 2

    @pytest.mark.asyncio
    async def test_preview_occurrences_caps_at_20(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test preview caps at 20 occurrences maximum."""
        next_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=next_date
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await recurring_service.preview_occurrences(
            task_id=sample_task.id,
            count=100  # Request 100 but should cap at 20
        )

        assert result.count == 20
        assert len(result.dates) == 20


class TestGenerateNextInstanceEdgeCases:
    """Tests for generate_next_instance edge cases."""

    @pytest.mark.asyncio
    async def test_generate_next_instance_pattern_not_found(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test generating instance when pattern doesn't exist."""
        # Mock pattern not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="No recurrence pattern found"):
            await recurring_service.generate_next_instance(task_id=sample_task.id)

    @pytest.mark.asyncio
    async def test_generate_next_instance_task_not_found(
        self,
        recurring_service,
        mock_db_session,
        sample_task
    ):
        """Test generating instance when original task doesn't exist."""
        pattern = RecurrencePattern(
            id=uuid4(),
            task_id=sample_task.id,
            frequency="daily",
            interval=1,
            next_occurrence_date=datetime.now(timezone.utc) + timedelta(days=1)
        )

        # Mock get pattern
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=pattern)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Mock task not found
        mock_db_session.get = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Task .* not found"):
            await recurring_service.generate_next_instance(task_id=sample_task.id)


class TestCalculateNextOccurrenceEdgeCases:
    """Tests for _calculate_next_occurrence edge cases."""

    def test_calculate_weekly_with_specific_days(self, recurring_service):
        """Test weekly recurrence with specific days of week."""
        # Start on Monday (day 0), want next Thursday (day 3)
        start_date = datetime(2025, 1, 6, 9, 0, tzinfo=timezone.utc)  # Monday
        frequency = "weekly"
        interval = 1
        days_of_week = [3, 5]  # Thursday, Saturday

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            days_of_week=days_of_week
        )

        # Should return Thursday (3 days ahead)
        expected = datetime(2025, 1, 9, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_weekly_wraps_to_next_week(self, recurring_service):
        """Test weekly recurrence wraps to next week when no more days this week."""
        # Start on Friday (day 4), want Monday (day 0) next week
        start_date = datetime(2025, 1, 10, 9, 0, tzinfo=timezone.utc)  # Friday
        frequency = "weekly"
        interval = 1
        days_of_week = [0, 2]  # Monday, Wednesday

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            days_of_week=days_of_week
        )

        # Should return Monday next week
        expected = datetime(2025, 1, 13, 9, 0, tzinfo=timezone.utc)  # Monday
        assert result == expected

    def test_calculate_monthly_day_31_in_february(self, recurring_service):
        """Test monthly recurrence handles day 31 in February (adjusts to last day)."""
        # Start on Jan 31, next occurrence should be Feb 28 (or 29 in leap year)
        start_date = datetime(2025, 1, 31, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 1
        day_of_month = 31

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=day_of_month
        )

        # Should return Feb 28 (2025 is not a leap year)
        expected = datetime(2025, 2, 28, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_monthly_crosses_year_boundary(self, recurring_service):
        """Test monthly recurrence crosses year boundary."""
        start_date = datetime(2025, 11, 15, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 3  # 3 months later = February 2026

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=15
        )

        expected = datetime(2026, 2, 15, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_invalid_frequency_fallback(self, recurring_service):
        """Test invalid frequency falls back to adding 1 day."""
        start_date = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        frequency = "invalid_frequency"
        interval = 1

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval
        )

        # Should fallback to +1 day
        expected = datetime(2025, 1, 2, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_monthly_without_day_of_month(self, recurring_service):
        """Test monthly recurrence uses from_date day when day_of_month not specified."""
        start_date = datetime(2025, 1, 15, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 1

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=None  # Should use day 15 from start_date
        )

        expected = datetime(2025, 2, 15, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_weekly_with_multi_week_interval(self, recurring_service):
        """Test weekly recurrence with multi-week interval and specific days."""
        # Start on Monday (day 0), want next occurrence in 2 weeks on Monday
        start_date = datetime(2025, 1, 6, 9, 0, tzinfo=timezone.utc)  # Monday
        frequency = "weekly"
        interval = 2
        days_of_week = [0]  # Only Mondays

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            days_of_week=days_of_week
        )

        # Should return Monday in 2 weeks
        expected = datetime(2025, 1, 20, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_monthly_february_29_in_non_leap_year(self, recurring_service):
        """Test monthly recurrence handles Feb 29 in non-leap year (adjusts to Feb 28)."""
        # Start on Jan 29, target Feb 29 (but 2025 is not a leap year)
        start_date = datetime(2025, 1, 29, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 1
        day_of_month = 29

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=day_of_month
        )

        # Should return Feb 28 (2025 is not a leap year, Feb has only 28 days)
        expected = datetime(2025, 2, 28, 9, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_calculate_monthly_day_30_in_february(self, recurring_service):
        """Test monthly recurrence handles day 30 in February (adjusts to last day)."""
        # Start on Jan 30, target Feb 30 (doesn't exist)
        start_date = datetime(2025, 1, 30, 9, 0, tzinfo=timezone.utc)
        frequency = "monthly"
        interval = 1
        day_of_month = 30

        result = recurring_service._calculate_next_occurrence(
            from_date=start_date,
            frequency=frequency,
            interval=interval,
            day_of_month=day_of_month
        )

        # Should return Feb 28 (2025 is not a leap year)
        expected = datetime(2025, 2, 28, 9, 0, tzinfo=timezone.utc)
        assert result == expected
