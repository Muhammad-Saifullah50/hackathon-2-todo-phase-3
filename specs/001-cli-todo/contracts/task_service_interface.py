"""Task service interface contract.

This module defines the protocol for the business logic layer. The service layer
sits between the CLI and storage, handling all task operations, validation, and
business rules.
"""

from typing import Protocol

from src.models.task import Task


class TaskServiceInterface(Protocol):
    """Protocol defining the task service contract.

    This protocol uses structural subtyping (PEP 544) to define the interface
    for the business logic layer. Implementations don't need to explicitly
    inherit from this protocol.

    The service layer is responsible for:
    - CRUD operations on tasks
    - Input validation before persistence
    - Filtering and pagination logic
    - ID generation and collision handling
    - Business rule enforcement
    """

    def add_task(self, title: str, description: str = "") -> Task:
        """Create and add a new task.

        Args:
            title: Task title (will be validated for 1-10 words)
            description: Optional task description (will be validated for 0-500 chars)

        Returns:
            Created Task object with generated ID and timestamps

        Raises:
            TaskValidationError: If title or description fails validation

        Notes:
            - Generates unique 8-character ID (collision detection)
            - Sets status to "pending" by default
            - Sets created_at and updated_at to current timestamp
            - Saves to storage after creation
        """
        ...

    def get_task(self, task_id: str) -> Task | None:
        """Get a single task by ID.

        Args:
            task_id: 8-character task ID

        Returns:
            Task object if found, None if not found

        Notes:
            - O(1) lookup using in-memory index
            - Does not raise exception if task not found
        """
        ...

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks, sorted by creation date (newest first).

        Returns:
            List of all Task objects, sorted descending by created_at

        Notes:
            - Returns empty list if no tasks exist
            - Always sorted: newest tasks first
        """
        ...

    def filter_by_status(self, status: str) -> list[Task]:
        """Get tasks filtered by status.

        Args:
            status: "pending" or "completed"

        Returns:
            List of Task objects matching status, sorted descending by created_at

        Raises:
            TaskValidationError: If status is not "pending" or "completed"

        Notes:
            - Returns empty list if no tasks match
            - Always sorted: newest tasks first
        """
        ...

    def paginate(self, tasks: list[Task], page: int = 0, page_size: int = 10) -> list[Task]:
        """Paginate a list of tasks.

        Args:
            tasks: List of Task objects to paginate
            page: Zero-indexed page number (default: 0)
            page_size: Number of tasks per page (default: 10)

        Returns:
            Slice of tasks for the requested page

        Notes:
            - Page 0 returns tasks[0:10], page 1 returns tasks[10:20], etc.
            - Returns empty list if page exceeds available tasks
            - Does not modify input task list
        """
        ...

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update a task's title and/or description.

        Args:
            task_id: 8-character task ID
            title: New title (None to keep current), will be validated
            description: New description (None to keep current), will be validated

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If task ID doesn't exist
            TaskValidationError: If title or description fails validation

        Notes:
            - At least one of title/description must be provided (not both None)
            - Updates updated_at timestamp automatically
            - Saves to storage after update
        """
        ...

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID.

        Args:
            task_id: 8-character task ID

        Returns:
            True if task was deleted, False if task didn't exist

        Notes:
            - Does not raise exception if task not found
            - Saves to storage after deletion
        """
        ...

    def delete_tasks(self, task_ids: list[str]) -> int:
        """Delete multiple tasks by ID (bulk operation).

        Args:
            task_ids: List of 8-character task IDs

        Returns:
            Number of tasks actually deleted (may be less than len(task_ids)
            if some IDs don't exist)

        Notes:
            - Skips IDs that don't exist (no error raised)
            - Saves to storage once after all deletions
            - More efficient than multiple delete_task() calls
        """
        ...

    def mark_completed(self, task_id: str) -> Task:
        """Mark a task as completed.

        Args:
            task_id: 8-character task ID

        Returns:
            Updated Task object with status="completed"

        Raises:
            TaskNotFoundError: If task ID doesn't exist

        Notes:
            - Changes status from "pending" to "completed"
            - Updates updated_at timestamp automatically
            - Idempotent: marking already-completed task is no-op
            - Saves to storage after update
        """
        ...

    def mark_pending(self, task_id: str) -> Task:
        """Mark a task as pending (incomplete).

        Args:
            task_id: 8-character task ID

        Returns:
            Updated Task object with status="pending"

        Raises:
            TaskNotFoundError: If task ID doesn't exist

        Notes:
            - Changes status from "completed" to "pending"
            - Updates updated_at timestamp automatically
            - Idempotent: marking already-pending task is no-op
            - Saves to storage after update
        """
        ...

    def mark_tasks_completed(self, task_ids: list[str]) -> int:
        """Mark multiple tasks as completed (bulk operation).

        Args:
            task_ids: List of 8-character task IDs

        Returns:
            Number of tasks actually marked completed

        Raises:
            TaskNotFoundError: If any task ID doesn't exist

        Notes:
            - All-or-nothing: if any ID is invalid, raises error before modifying
            - More efficient than multiple mark_completed() calls
            - Saves to storage once after all updates
        """
        ...

    def mark_tasks_pending(self, task_ids: list[str]) -> int:
        """Mark multiple tasks as pending (bulk operation).

        Args:
            task_ids: List of 8-character task IDs

        Returns:
            Number of tasks actually marked pending

        Raises:
            TaskNotFoundError: If any task ID doesn't exist

        Notes:
            - All-or-nothing: if any ID is invalid, raises error before modifying
            - More efficient than multiple mark_pending() calls
            - Saves to storage once after all updates
        """
        ...

    def count_tasks(self) -> dict[str, int]:
        """Get task count statistics.

        Returns:
            Dictionary with keys:
            - "total": Total number of tasks
            - "pending": Number of pending tasks
            - "completed": Number of completed tasks

        Notes:
            - Useful for pagination calculations
            - O(n) operation (iterates all tasks)
        """
        ...


# Type alias for easier imports
TaskService = TaskServiceInterface
