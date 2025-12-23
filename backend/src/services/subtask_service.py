"""Subtask service for business logic operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.subtask import Subtask
from src.models.task import Task, TaskStatus
from src.schemas.subtask_schemas import (
    SubtaskCreate,
    SubtaskListResponse,
    SubtaskResponse,
    SubtaskUpdate,
)


class SubtaskNotFoundError(Exception):
    """Raised when a subtask is not found."""

    pass


class SubtaskService:
    """Service class for subtask-related business logic.

    This service layer handles:
    - CRUD operations for subtasks
    - Auto-completion of parent tasks
    - Order management for subtasks

    Attributes:
        session: The async database session for database operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the SubtaskService.

        Args:
            session: The async database session.
        """
        self.session = session

    async def get_subtasks(self, task_id: UUID, user_id: str) -> SubtaskListResponse:
        """Get all subtasks for a task.

        Args:
            task_id: ID of the parent task.
            user_id: ID of the authenticated user (for authorization).

        Returns:
            SubtaskListResponse with subtasks and statistics.

        Raises:
            SubtaskNotFoundError: If task doesn't exist or user doesn't own it.
        """
        # Verify task exists and belongs to user
        task = await self._get_task_or_raise(task_id, user_id)

        # Get all subtasks ordered by order_index
        query = (
            select(Subtask)
            .where(Subtask.task_id == task_id)
            .order_by(Subtask.order_index.asc())
        )
        result = await self.session.execute(query)
        subtasks = result.scalars().all()

        # Calculate statistics
        total_count = len(subtasks)
        completed_count = sum(1 for s in subtasks if s.is_completed)
        completion_percentage = (
            (completed_count / total_count * 100.0) if total_count > 0 else 0.0
        )

        return SubtaskListResponse(
            subtasks=[SubtaskResponse.model_validate(s) for s in subtasks],
            total_count=total_count,
            completed_count=completed_count,
            completion_percentage=completion_percentage,
        )

    async def create_subtask(
        self, task_id: UUID, subtask_data: SubtaskCreate, user_id: str
    ) -> Subtask:
        """Create a new subtask for a task.

        Args:
            task_id: ID of the parent task.
            subtask_data: Validated subtask creation data.
            user_id: ID of the authenticated user (for authorization).

        Returns:
            Created Subtask instance.

        Raises:
            SubtaskNotFoundError: If task doesn't exist or user doesn't own it.
            ValueError: If validation fails or max subtasks exceeded.
        """
        # Verify task exists and belongs to user
        await self._get_task_or_raise(task_id, user_id)

        # Check subtask limit (50 per task)
        count_query = select(func.count(Subtask.id)).where(Subtask.task_id == task_id)
        result = await self.session.execute(count_query)
        current_count = result.scalar() or 0

        if current_count >= 50:
            raise ValueError("Maximum 50 subtasks per task exceeded")

        # Determine order_index
        if subtask_data.order_index is not None:
            order_index = subtask_data.order_index
        else:
            # Auto-assign: place at end
            max_order_query = select(func.max(Subtask.order_index)).where(
                Subtask.task_id == task_id
            )
            result = await self.session.execute(max_order_query)
            max_order = result.scalar()
            order_index = (max_order + 1) if max_order is not None else 0

        # Create subtask
        subtask = Subtask(
            task_id=task_id,
            description=subtask_data.description,
            is_completed=False,
            order_index=order_index,
        )

        self.session.add(subtask)
        await self.session.commit()
        await self.session.refresh(subtask)

        return subtask

    async def update_subtask(
        self, subtask_id: UUID, subtask_data: SubtaskUpdate, user_id: str
    ) -> Subtask:
        """Update an existing subtask.

        Args:
            subtask_id: ID of the subtask to update.
            subtask_data: Updated subtask data.
            user_id: ID of the authenticated user (for authorization).

        Returns:
            Updated Subtask instance.

        Raises:
            SubtaskNotFoundError: If subtask doesn't exist or user doesn't own parent task.
        """
        # Get subtask and verify ownership
        subtask = await self._get_subtask_with_auth(subtask_id, user_id)

        # Track if completion status changed
        was_completed = subtask.is_completed

        # Update fields
        if subtask_data.description is not None:
            subtask.description = subtask_data.description
        if subtask_data.is_completed is not None:
            subtask.is_completed = subtask_data.is_completed
        if subtask_data.order_index is not None:
            subtask.order_index = subtask_data.order_index

        await self.session.commit()
        await self.session.refresh(subtask)

        # Check if parent task should be auto-completed
        if subtask.is_completed and not was_completed:
            await self._check_parent_task_completion(subtask.task_id)

        return subtask

    async def toggle_subtask(
        self, subtask_id: UUID, is_completed: bool, user_id: str
    ) -> Subtask:
        """Toggle subtask completion status.

        Args:
            subtask_id: ID of the subtask to toggle.
            is_completed: New completion status.
            user_id: ID of the authenticated user (for authorization).

        Returns:
            Updated Subtask instance.

        Raises:
            SubtaskNotFoundError: If subtask doesn't exist or user doesn't own parent task.
        """
        # Get subtask and verify ownership
        subtask = await self._get_subtask_with_auth(subtask_id, user_id)

        # Track if completion status changed
        was_completed = subtask.is_completed

        # Update completion status
        subtask.is_completed = is_completed

        await self.session.commit()
        await self.session.refresh(subtask)

        # Check if parent task should be auto-completed
        if is_completed and not was_completed:
            await self._check_parent_task_completion(subtask.task_id)

        return subtask

    async def delete_subtask(self, subtask_id: UUID, user_id: str) -> None:
        """Delete a subtask.

        Args:
            subtask_id: ID of the subtask to delete.
            user_id: ID of the authenticated user (for authorization).

        Raises:
            SubtaskNotFoundError: If subtask doesn't exist or user doesn't own parent task.
        """
        # Get subtask and verify ownership
        subtask = await self._get_subtask_with_auth(subtask_id, user_id)

        await self.session.delete(subtask)
        await self.session.commit()

    async def reorder_subtasks(
        self, task_id: UUID, subtask_ids: list[UUID], user_id: str
    ) -> list[Subtask]:
        """Reorder subtasks within a task.

        Args:
            task_id: ID of the parent task.
            subtask_ids: List of subtask IDs in desired order.
            user_id: ID of the authenticated user (for authorization).

        Returns:
            List of updated subtasks in new order.

        Raises:
            SubtaskNotFoundError: If task doesn't exist or user doesn't own it.
            ValueError: If subtask_ids don't match task's subtasks.
        """
        # Verify task exists and belongs to user
        await self._get_task_or_raise(task_id, user_id)

        # Get all subtasks for this task
        query = select(Subtask).where(Subtask.task_id == task_id)
        result = await self.session.execute(query)
        subtasks = list(result.scalars().all())

        # Verify all subtask IDs match
        existing_ids = {str(s.id) for s in subtasks}
        provided_ids = {str(sid) for sid in subtask_ids}

        if existing_ids != provided_ids:
            raise ValueError(
                "Provided subtask IDs do not match task's subtasks"
            )

        # Create mapping of subtask_id to subtask
        subtask_map = {str(s.id): s for s in subtasks}

        # Update order_index for each subtask
        reordered_subtasks = []
        for order_index, subtask_id in enumerate(subtask_ids):
            subtask = subtask_map[str(subtask_id)]
            subtask.order_index = order_index
            reordered_subtasks.append(subtask)

        await self.session.commit()

        # Refresh all subtasks
        for subtask in reordered_subtasks:
            await self.session.refresh(subtask)

        return reordered_subtasks

    async def _get_task_or_raise(self, task_id: UUID, user_id: str) -> Task:
        """Get task and verify user owns it.

        Args:
            task_id: ID of the task.
            user_id: ID of the authenticated user.

        Returns:
            Task instance if found and owned by user.

        Raises:
            SubtaskNotFoundError: If task doesn't exist or user doesn't own it.
        """
        query = select(Task).where(
            Task.id == task_id, Task.user_id == user_id, Task.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise SubtaskNotFoundError(
                f"Task {task_id} not found or access denied"
            )

        return task

    async def _get_subtask_with_auth(
        self, subtask_id: UUID, user_id: str
    ) -> Subtask:
        """Get subtask and verify user owns parent task.

        Args:
            subtask_id: ID of the subtask.
            user_id: ID of the authenticated user.

        Returns:
            Subtask instance if found and user owns parent task.

        Raises:
            SubtaskNotFoundError: If subtask doesn't exist or user doesn't own parent task.
        """
        # Get subtask with joined task for authorization
        query = (
            select(Subtask)
            .join(Task, Subtask.task_id == Task.id)
            .where(
                Subtask.id == subtask_id,
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        subtask = result.scalar_one_or_none()

        if not subtask:
            raise SubtaskNotFoundError(
                f"Subtask {subtask_id} not found or access denied"
            )

        return subtask

    async def _check_parent_task_completion(self, task_id: UUID) -> None:
        """Check if all subtasks are completed and auto-complete parent task if so.

        Args:
            task_id: ID of the parent task to check.
        """
        # Get all subtasks for this task
        query = select(Subtask).where(Subtask.task_id == task_id)
        result = await self.session.execute(query)
        subtasks = list(result.scalars().all())

        # If no subtasks, don't auto-complete
        if not subtasks:
            return

        # Check if all subtasks are completed
        all_completed = all(s.is_completed for s in subtasks)

        if all_completed:
            # Auto-complete parent task
            task_query = select(Task).where(Task.id == task_id)
            task_result = await self.session.execute(task_query)
            task = task_result.scalar_one_or_none()

            if task and task.status != TaskStatus.COMPLETED:
                from datetime import datetime, timezone

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc)
                await self.session.commit()
