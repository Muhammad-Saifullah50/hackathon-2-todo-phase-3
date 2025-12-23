"""Query builder utilities for task queries with user filtering and soft delete handling."""

from typing import Any

from sqlalchemy import Select, and_, func, select
from sqlmodel import Session

from ..models.task import Task, TaskStatus


class TaskQueryBuilder:
    """Builder class for constructing task queries with common filters.

    Handles user ownership filtering and soft delete exclusion by default.
    """

    def __init__(self, session: Session, user_id: str):
        """Initialize the query builder.

        Args:
            session: Database session.
            user_id: The user ID for ownership filtering.
        """
        self.session = session
        self.user_id = user_id
        self._query: Select[Any] = select(Task)
        self._filters: list[Any] = []

    def base_query(self, include_deleted: bool = False) -> "TaskQueryBuilder":
        """Set up base query with user filtering.

        Args:
            include_deleted: If False (default), exclude soft-deleted tasks.

        Returns:
            Self for method chaining.
        """
        # Always filter by user ID for security
        self._filters.append(Task.user_id == self.user_id)

        # Exclude soft-deleted tasks by default
        if not include_deleted:
            self._filters.append(Task.deleted_at.is_(None))

        return self

    def filter_by_status(self, status: TaskStatus | None) -> "TaskQueryBuilder":
        """Add status filter to the query.

        Args:
            status: The task status to filter by (optional).

        Returns:
            Self for method chaining.
        """
        if status is not None:
            self._filters.append(Task.status == status)

        return self

    def filter_deleted_only(self) -> "TaskQueryBuilder":
        """Filter to show only soft-deleted tasks (trash view).

        Returns:
            Self for method chaining.
        """
        # Override the base deleted_at filter
        self._filters = [f for f in self._filters if not str(f).startswith("tasks.deleted_at")]
        self._filters.append(Task.deleted_at.isnot(None))

        return self

    def order_by(self, field: str = "created_at", descending: bool = True) -> "TaskQueryBuilder":
        """Add ordering to the query.

        Args:
            field: Field name to order by (default: "created_at").
            descending: If True, order descending (default: True).

        Returns:
            Self for method chaining.
        """
        order_column = getattr(Task, field, Task.created_at)

        if descending:
            self._query = self._query.order_by(order_column.desc())
        else:
            self._query = self._query.order_by(order_column.asc())

        return self

    def paginate(self, page: int = 1, limit: int = 20) -> "TaskQueryBuilder":
        """Add pagination to the query.

        Args:
            page: Page number (1-indexed, default: 1).
            limit: Number of items per page (default: 20).

        Returns:
            Self for method chaining.
        """
        offset = (page - 1) * limit
        self._query = self._query.offset(offset).limit(limit)

        return self

    def build(self) -> Select[Any]:
        """Build and return the final query with all filters applied.

        Returns:
            SQLAlchemy Select query ready for execution.
        """
        if self._filters:
            self._query = self._query.where(and_(*self._filters))

        return self._query

    def count(self) -> int:
        """Execute a count query with the current filters.

        Returns:
            Total number of tasks matching the filters.
        """
        count_query = select(func.count()).select_from(Task)

        if self._filters:
            count_query = count_query.where(and_(*self._filters))

        result = self.session.exec(count_query).one()
        return result

    def get_metadata(self) -> dict[str, int]:
        """Get task count metadata for the current user.

        Returns:
            Dictionary with count statistics:
                - total_pending: Number of pending tasks
                - total_completed: Number of completed tasks
                - total_active: Number of active (non-deleted) tasks
                - total_deleted: Number of soft-deleted tasks
        """
        # Active tasks count
        active_count = (
            self.session.exec(
                select(func.count())
                .select_from(Task)
                .where(
                    and_(
                        Task.user_id == self.user_id,
                        Task.deleted_at.is_(None),
                    )
                )
            )
            .one()
        )

        # Pending tasks count
        pending_count = (
            self.session.exec(
                select(func.count())
                .select_from(Task)
                .where(
                    and_(
                        Task.user_id == self.user_id,
                        Task.deleted_at.is_(None),
                        Task.status == TaskStatus.PENDING,
                    )
                )
            )
            .one()
        )

        # Completed tasks count
        completed_count = (
            self.session.exec(
                select(func.count())
                .select_from(Task)
                .where(
                    and_(
                        Task.user_id == self.user_id,
                        Task.deleted_at.is_(None),
                        Task.status == TaskStatus.COMPLETED,
                    )
                )
            )
            .one()
        )

        # Deleted tasks count
        deleted_count = (
            self.session.exec(
                select(func.count())
                .select_from(Task)
                .where(
                    and_(
                        Task.user_id == self.user_id,
                        Task.deleted_at.isnot(None),
                    )
                )
            )
            .one()
        )

        return {
            "total_pending": pending_count,
            "total_completed": completed_count,
            "total_active": active_count,
            "total_deleted": deleted_count,
        }
