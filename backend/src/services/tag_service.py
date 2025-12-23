"""Tag service for business logic operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.tag import Tag, TagCreate, TagUpdate
from src.models.task_tag import TaskTag


class TagService:
    """Service class for tag-related business logic.

    This service layer separates business logic from the HTTP layer,
    making the code more testable and maintainable.

    Attributes:
        session: The async database session for database operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the TagService.

        Args:
            session: The async database session.
        """
        self.session = session

    async def create_tag(self, tag_data: TagCreate, user_id: str) -> Tag:
        """Create a new tag for the authenticated user.

        Args:
            tag_data: Validated tag creation data from request.
            user_id: ID of the authenticated user from JWT token.

        Returns:
            Created Tag instance with all fields populated.

        Raises:
            ValueError: If validation fails or tag name already exists.
        """
        # Check if tag with same name already exists for this user (case-insensitive)
        existing_query = select(Tag).where(
            and_(
                Tag.user_id == user_id,
                func.lower(Tag.name) == tag_data.name.lower(),
            )
        )
        result = await self.session.execute(existing_query)
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            raise ValueError(f"Tag with name '{tag_data.name}' already exists")

        # Create Tag instance
        tag = Tag(
            name=tag_data.name,
            color=tag_data.color,
            user_id=user_id,
        )

        # Add to session and commit
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)

        return tag

    async def get_tags(self, user_id: str) -> list[Tag]:
        """Get all tags for the authenticated user.

        Args:
            user_id: ID of the authenticated user.

        Returns:
            List of Tag instances sorted by name.
        """
        query = (
            select(Tag)
            .where(Tag.user_id == user_id)
            .order_by(Tag.name.asc())
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tag_by_id(self, tag_id: str, user_id: str) -> Tag | None:
        """Get a specific tag by ID.

        Args:
            tag_id: UUID of the tag.
            user_id: ID of the authenticated user.

        Returns:
            Tag instance if found and owned by user, None otherwise.
        """
        query = select(Tag).where(
            and_(Tag.id == UUID(tag_id), Tag.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_tag(
        self, tag_id: str, user_id: str, tag_data: TagUpdate
    ) -> Tag:
        """Update a tag's fields.

        Args:
            tag_id: UUID of the tag to update.
            user_id: ID of the authenticated user.
            tag_data: Tag update data (name and/or color).

        Returns:
            Updated Tag instance.

        Raises:
            ValueError: If tag not found or no changes provided.
            PermissionError: If user doesn't own the tag.
        """
        # Fetch the tag
        tag = await self.get_tag_by_id(tag_id, user_id)

        if not tag:
            raise ValueError(f"Tag with ID {tag_id} not found")

        # Check if at least one field is provided
        if tag_data.name is None and tag_data.color is None:
            raise ValueError("At least one field (name or color) must be provided")

        # Check for name conflicts if updating name
        if tag_data.name is not None and tag_data.name.lower() != tag.name.lower():
            existing_query = select(Tag).where(
                and_(
                    Tag.user_id == user_id,
                    func.lower(Tag.name) == tag_data.name.lower(),
                    Tag.id != UUID(tag_id),
                )
            )
            result = await self.session.execute(existing_query)
            existing_tag = result.scalar_one_or_none()

            if existing_tag:
                raise ValueError(f"Tag with name '{tag_data.name}' already exists")

        # Track changes
        has_changes = False

        if tag_data.name is not None and tag_data.name != tag.name:
            tag.name = tag_data.name
            has_changes = True

        if tag_data.color is not None and tag_data.color != tag.color:
            tag.color = tag_data.color
            has_changes = True

        if not has_changes:
            raise ValueError("No changes detected")

        # Update timestamp
        tag.updated_at = datetime.now(timezone.utc)

        # Commit changes
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)

        return tag

    async def delete_tag(self, tag_id: str, user_id: str) -> None:
        """Delete a tag and all its task associations.

        Args:
            tag_id: UUID of the tag to delete.
            user_id: ID of the authenticated user.

        Raises:
            ValueError: If tag not found.
            PermissionError: If user doesn't own the tag.
        """
        # Fetch the tag
        tag = await self.get_tag_by_id(tag_id, user_id)

        if not tag:
            raise ValueError(f"Tag with ID {tag_id} not found")

        # Delete tag (cascades to task_tags via foreign key)
        await self.session.delete(tag)
        await self.session.commit()

    async def add_tags_to_task(
        self, task_id: str, tag_ids: list[str], user_id: str
    ) -> list[Tag]:
        """Add tags to a task.

        Args:
            task_id: UUID of the task.
            tag_ids: List of tag UUIDs to add.
            user_id: ID of the authenticated user.

        Returns:
            List of tags now associated with the task.

        Raises:
            ValueError: If any tag not found or task doesn't exist.
            PermissionError: If user doesn't own the tags/task.
        """
        from src.models.task import Task

        # Validate task exists and belongs to user
        task_query = select(Task).where(
            and_(
                Task.id == UUID(task_id),
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
            )
        )
        task_result = await self.session.execute(task_query)
        task = task_result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Validate all tags exist and belong to user
        tag_uuids = [UUID(tag_id) for tag_id in tag_ids]
        tags_query = select(Tag).where(
            and_(Tag.id.in_(tag_uuids), Tag.user_id == user_id)
        )
        tags_result = await self.session.execute(tags_query)
        tags = list(tags_result.scalars().all())

        if len(tags) != len(tag_ids):
            raise ValueError("One or more tags not found")

        # Get existing tag associations
        existing_query = select(TaskTag.tag_id).where(TaskTag.task_id == UUID(task_id))
        existing_result = await self.session.execute(existing_query)
        existing_tag_ids = {row[0] for row in existing_result.all()}

        # Add only new associations
        for tag in tags:
            if tag.id not in existing_tag_ids:
                task_tag = TaskTag(task_id=UUID(task_id), tag_id=tag.id)
                self.session.add(task_tag)

        await self.session.commit()

        # Return all tags for the task
        return await self.get_task_tags(task_id, user_id)

    async def remove_tags_from_task(
        self, task_id: str, tag_ids: list[str], user_id: str
    ) -> list[Tag]:
        """Remove tags from a task.

        Args:
            task_id: UUID of the task.
            tag_ids: List of tag UUIDs to remove.
            user_id: ID of the authenticated user.

        Returns:
            List of remaining tags associated with the task.

        Raises:
            ValueError: If task doesn't exist.
            PermissionError: If user doesn't own the task.
        """
        from src.models.task import Task

        # Validate task exists and belongs to user
        task_query = select(Task).where(
            and_(
                Task.id == UUID(task_id),
                Task.user_id == user_id,
                Task.deleted_at.is_(None),
            )
        )
        task_result = await self.session.execute(task_query)
        task = task_result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Delete the associations
        tag_uuids = [UUID(tag_id) for tag_id in tag_ids]
        delete_query = select(TaskTag).where(
            and_(
                TaskTag.task_id == UUID(task_id),
                TaskTag.tag_id.in_(tag_uuids),
            )
        )
        result = await self.session.execute(delete_query)
        associations = result.scalars().all()

        for assoc in associations:
            await self.session.delete(assoc)

        await self.session.commit()

        # Return remaining tags for the task
        return await self.get_task_tags(task_id, user_id)

    async def get_task_tags(self, task_id: str, user_id: str) -> list[Tag]:
        """Get all tags for a specific task.

        Args:
            task_id: UUID of the task.
            user_id: ID of the authenticated user.

        Returns:
            List of Tag instances associated with the task.
        """
        query = (
            select(Tag)
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .where(TaskTag.task_id == UUID(task_id))
            .order_by(Tag.name.asc())
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tag_usage_count(self, tag_id: str, user_id: str) -> int:
        """Get the number of tasks using a specific tag.

        Args:
            tag_id: UUID of the tag.
            user_id: ID of the authenticated user.

        Returns:
            Count of tasks using this tag.
        """
        # First verify the tag belongs to user
        tag = await self.get_tag_by_id(tag_id, user_id)
        if not tag:
            raise ValueError(f"Tag with ID {tag_id} not found")

        # Count active tasks using this tag
        from src.models.task import Task

        count_query = (
            select(func.count())
            .select_from(TaskTag)
            .join(Task, TaskTag.task_id == Task.id)
            .where(
                and_(
                    TaskTag.tag_id == UUID(tag_id),
                    Task.deleted_at.is_(None),
                )
            )
        )
        result = await self.session.execute(count_query)
        return result.scalar_one()
