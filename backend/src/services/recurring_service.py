"""Service for managing task recurrence patterns."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.recurrence_pattern import RecurrencePattern
from src.models.task import Task
from src.schemas.recurring_schemas import (
    RecurrencePatternCreate,
    RecurrencePatternUpdate,
    RecurrencePreviewResponse,
)


class RecurringService:
    """Service for managing task recurrence patterns."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session.

        Args:
            db: SQLModel async database session
        """
        self.db = db

    async def create_recurrence_pattern(
        self,
        task_id: UUID,
        pattern_data: RecurrencePatternCreate,
        start_date: Optional[datetime] = None
    ) -> RecurrencePattern:
        """Create a new recurrence pattern for a task.

        Args:
            task_id: ID of the task to make recurring
            pattern_data: Recurrence pattern configuration
            start_date: Starting date for recurrence (defaults to now)

        Returns:
            Created RecurrencePattern

        Raises:
            ValueError: If task already has a recurrence pattern or task not found
        """
        # Check if task exists
        task = await self.db.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Check if pattern already exists
        result = await self.db.execute(
            select(RecurrencePattern).where(RecurrencePattern.task_id == task_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Task {task_id} already has a recurrence pattern")

        # Calculate next occurrence
        if start_date is None:
            start_date = datetime.now(timezone.utc)

        next_occurrence = self._calculate_next_occurrence(
            start_date,
            pattern_data.frequency,
            pattern_data.interval,
            pattern_data.days_of_week,
            pattern_data.day_of_month
        )

        # Create pattern
        pattern = RecurrencePattern(
            task_id=task_id,
            frequency=pattern_data.frequency,
            interval=pattern_data.interval,
            days_of_week=pattern_data.days_of_week,
            day_of_month=pattern_data.day_of_month,
            end_date=pattern_data.end_date,
            next_occurrence_date=next_occurrence
        )

        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(pattern)

        return pattern

    async def get_recurrence_pattern(self, task_id: UUID) -> Optional[RecurrencePattern]:
        """Get recurrence pattern for a task.

        Args:
            task_id: ID of the task

        Returns:
            RecurrencePattern if exists, None otherwise
        """
        result = await self.db.execute(
            select(RecurrencePattern).where(RecurrencePattern.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def update_recurrence_pattern(
        self,
        task_id: UUID,
        pattern_data: RecurrencePatternUpdate
    ) -> RecurrencePattern:
        """Update an existing recurrence pattern.

        Args:
            task_id: ID of the task
            pattern_data: Updated pattern configuration

        Returns:
            Updated RecurrencePattern

        Raises:
            ValueError: If pattern not found
        """
        pattern = await self.get_recurrence_pattern(task_id)
        if not pattern:
            raise ValueError(f"No recurrence pattern found for task {task_id}")

        # Update fields
        update_data = pattern_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pattern, key, value)

        # Recalculate next occurrence if frequency/interval changed
        if any(k in update_data for k in ["frequency", "interval", "days_of_week", "day_of_month"]):
            pattern.next_occurrence_date = self._calculate_next_occurrence(
                datetime.now(timezone.utc),
                pattern.frequency,
                pattern.interval,
                pattern.days_of_week,
                pattern.day_of_month
            )

        pattern.updated_at = datetime.now(timezone.utc)

        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(pattern)

        return pattern

    async def delete_recurrence_pattern(self, task_id: UUID) -> bool:
        """Delete a recurrence pattern.

        Args:
            task_id: ID of the task

        Returns:
            True if deleted, False if not found
        """
        pattern = await self.get_recurrence_pattern(task_id)
        if not pattern:
            return False

        await self.db.delete(pattern)
        await self.db.commit()

        return True

    async def preview_occurrences(
        self,
        task_id: UUID,
        count: int = 5
    ) -> RecurrencePreviewResponse:
        """Preview the next N occurrences of a recurring task.

        Args:
            task_id: ID of the task
            count: Number of occurrences to preview (default 5, max 20)

        Returns:
            RecurrencePreviewResponse with upcoming dates

        Raises:
            ValueError: If pattern not found
        """
        pattern = await self.get_recurrence_pattern(task_id)
        if not pattern:
            raise ValueError(f"No recurrence pattern found for task {task_id}")

        count = min(count, 20)  # Cap at 20
        dates: List[datetime] = []
        current_date = pattern.next_occurrence_date

        for _ in range(count):
            if pattern.end_date and current_date > pattern.end_date:
                break

            dates.append(current_date)
            current_date = self._calculate_next_occurrence(
                current_date,
                pattern.frequency,
                pattern.interval,
                pattern.days_of_week,
                pattern.day_of_month
            )

        return RecurrencePreviewResponse(dates=dates, count=len(dates))

    async def generate_next_instance(self, task_id: UUID) -> Optional[Task]:
        """Generate the next instance of a recurring task.

        Args:
            task_id: ID of the completed recurring task

        Returns:
            New task instance if recurrence continues, None if ended

        Raises:
            ValueError: If pattern not found or task not found
        """
        # Get pattern
        pattern = await self.get_recurrence_pattern(task_id)
        if not pattern:
            raise ValueError(f"No recurrence pattern found for task {task_id}")

        # Get original task
        original_task = await self.db.get(Task, task_id)
        if not original_task:
            raise ValueError(f"Task {task_id} not found")

        # Check if recurrence has ended
        if pattern.end_date and pattern.next_occurrence_date > pattern.end_date:
            return None

        # Create new task instance
        new_task = Task(
            user_id=original_task.user_id,
            title=original_task.title,
            description=original_task.description,
            status="pending",
            priority=original_task.priority,
            due_date=pattern.next_occurrence_date,
            notes=original_task.notes,
            template_id=original_task.template_id,
            recurrence_pattern_id=pattern.id
        )

        self.db.add(new_task)

        # Update pattern with next occurrence
        pattern.next_occurrence_date = self._calculate_next_occurrence(
            pattern.next_occurrence_date,
            pattern.frequency,
            pattern.interval,
            pattern.days_of_week,
            pattern.day_of_month
        )
        pattern.updated_at = datetime.now(timezone.utc)

        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(new_task)

        return new_task

    def _calculate_next_occurrence(
        self,
        from_date: datetime,
        frequency: str,
        interval: int,
        days_of_week: Optional[List[int]] = None,
        day_of_month: Optional[int] = None
    ) -> datetime:
        """Calculate the next occurrence date based on recurrence rules.

        Args:
            from_date: Starting date for calculation
            frequency: 'daily', 'weekly', or 'monthly'
            interval: Recurrence interval
            days_of_week: Specific days for weekly recurrence
            day_of_month: Specific day for monthly recurrence

        Returns:
            Next occurrence datetime
        """
        if frequency == "daily":
            return from_date + timedelta(days=interval)

        elif frequency == "weekly":
            if not days_of_week:
                # Default to same day of week
                return from_date + timedelta(weeks=interval)

            # Find next matching day of week
            current_weekday = from_date.weekday()
            days_of_week_sorted = sorted(days_of_week)

            # Find next day in current week
            for day in days_of_week_sorted:
                if day > current_weekday:
                    days_ahead = day - current_weekday
                    return from_date + timedelta(days=days_ahead)

            # If no day found this week, go to first day of next occurrence
            first_day = days_of_week_sorted[0]
            days_until_next_week = 7 - current_weekday + first_day
            return from_date + timedelta(days=days_until_next_week, weeks=interval - 1)

        elif frequency == "monthly":
            target_day = day_of_month if day_of_month else from_date.day

            # Move to next month(s)
            year = from_date.year
            month = from_date.month + interval

            while month > 12:
                month -= 12
                year += 1

            # Handle day overflow (e.g., day 31 in February)
            while True:
                try:
                    return from_date.replace(year=year, month=month, day=target_day)
                except ValueError:
                    # Day doesn't exist in this month, try last day
                    target_day -= 1
                    if target_day < 1:
                        # Shouldn't happen, but fallback to day 1
                        target_day = 1
                        break

        return from_date + timedelta(days=1)  # Fallback
