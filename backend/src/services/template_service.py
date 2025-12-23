"""Template service for managing task templates."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.tag import Tag
from src.models.task import Task
from src.models.task_template import TaskTemplate
from src.models.template_tag import TemplateTag
from src.schemas.template_schemas import TemplateCreate, TemplateUpdate


class TemplateService:
    """Service for managing task templates."""

    def __init__(self, db: AsyncSession):
        """Initialize the service."""
        self.db = db

    async def get_templates(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[TaskTemplate], int]:
        """Get all templates for a user with pagination."""
        offset = (page - 1) * page_size

        # Get templates with tags
        query = (
            select(TaskTemplate)
            .where(TaskTemplate.user_id == user_id)
            .options(selectinload(TaskTemplate.tags))
            .offset(offset)
            .limit(page_size)
            .order_by(TaskTemplate.created_at.desc())
        )

        result = await self.db.execute(query)
        templates = result.scalars().all()

        # Get total count
        count_query = select(TaskTemplate).where(TaskTemplate.user_id == user_id)
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())

        return list(templates), total

    async def get_template(self, template_id: str, user_id: str) -> Optional[TaskTemplate]:
        """Get a specific template by ID."""
        query = (
            select(TaskTemplate)
            .where(TaskTemplate.id == template_id, TaskTemplate.user_id == user_id)
            .options(selectinload(TaskTemplate.tags))
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_template(
        self,
        user_id: str,
        template_data: TemplateCreate,
    ) -> TaskTemplate:
        """Create a new template."""
        # Convert subtasks to dict format
        subtasks_dict = None
        if template_data.subtasks_template:
            subtasks_dict = [item.model_dump() for item in template_data.subtasks_template]

        # Create template
        template = TaskTemplate(
            id=str(uuid4()),
            user_id=user_id,
            name=template_data.name,
            title=template_data.title,
            description=template_data.description,
            priority=template_data.priority,
            subtasks_template=subtasks_dict,
        )

        self.db.add(template)
        await self.db.flush()

        # Add tags if provided
        if template_data.tag_ids:
            await self._assign_tags_to_template(template.id, template_data.tag_ids, user_id)

        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def update_template(
        self,
        template_id: str,
        user_id: str,
        template_data: TemplateUpdate,
    ) -> Optional[TaskTemplate]:
        """Update an existing template."""
        template = await self.get_template(template_id, user_id)
        if not template:
            return None

        # Update fields
        if template_data.name is not None:
            template.name = template_data.name
        if template_data.title is not None:
            template.title = template_data.title
        if template_data.description is not None:
            template.description = template_data.description
        if template_data.priority is not None:
            template.priority = template_data.priority
        if template_data.subtasks_template is not None:
            template.subtasks_template = [
                item.model_dump() for item in template_data.subtasks_template
            ]

        template.updated_at = datetime.now(timezone.utc)

        # Update tags if provided
        if template_data.tag_ids is not None:
            await self._reassign_tags_to_template(template_id, template_data.tag_ids, user_id)

        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def delete_template(self, template_id: str, user_id: str) -> bool:
        """Delete a template."""
        template = await self.get_template(template_id, user_id)
        if not template:
            return False

        await self.db.delete(template)
        await self.db.commit()

        return True

    async def apply_template(
        self,
        template_id: str,
        user_id: str,
        due_date: Optional[datetime] = None,
    ) -> Optional[Task]:
        """Create a new task from a template."""
        template = await self.get_template(template_id, user_id)
        if not template:
            return None

        # Create task from template
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=template.title,
            description=template.description,
            priority=template.priority,
            status="pending",
            due_date=due_date,
            template_id=template_id,
        )

        self.db.add(task)
        await self.db.flush()

        # Copy subtasks if template has them
        if template.subtasks_template:
            from src.models.subtask import Subtask

            for index, subtask_data in enumerate(template.subtasks_template):
                subtask = Subtask(
                    id=str(uuid4()),
                    task_id=task.id,
                    description=subtask_data["description"],
                    is_completed=False,
                    order_index=index,
                )
                self.db.add(subtask)

        # Copy tags if template has them
        if template.tags:
            from src.models.task_tag import TaskTag

            for tag in template.tags:
                task_tag = TaskTag(
                    task_id=task.id,
                    tag_id=tag.id,
                )
                self.db.add(task_tag)

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def save_task_as_template(
        self,
        task_id: str,
        user_id: str,
        template_name: str,
        include_subtasks: bool = True,
        include_tags: bool = True,
    ) -> Optional[TaskTemplate]:
        """Save an existing task as a template."""
        # Get task with relationships
        from src.services.task_service import TaskService

        task_service = TaskService(self.db)
        task = await task_service.get_task(task_id, user_id)

        if not task:
            return None

        # Prepare subtasks data
        subtasks_dict = None
        if include_subtasks and task.subtasks:
            subtasks_dict = [
                {"description": subtask.description} for subtask in task.subtasks
            ]

        # Create template
        template = TaskTemplate(
            id=str(uuid4()),
            user_id=user_id,
            name=template_name,
            title=task.title,
            description=task.description,
            priority=task.priority,
            subtasks_template=subtasks_dict,
        )

        self.db.add(template)
        await self.db.flush()

        # Copy tags if requested
        if include_tags and task.tags:
            for tag in task.tags:
                template_tag = TemplateTag(
                    template_id=template.id,
                    tag_id=tag.id,
                )
                self.db.add(template_tag)

        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def _assign_tags_to_template(
        self,
        template_id: str,
        tag_ids: list[str],
        user_id: str,
    ) -> None:
        """Assign tags to a template."""
        # Verify tags belong to user
        query = select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        result = await self.db.execute(query)
        valid_tags = result.scalars().all()

        for tag in valid_tags:
            template_tag = TemplateTag(
                template_id=template_id,
                tag_id=tag.id,
            )
            self.db.add(template_tag)

    async def _reassign_tags_to_template(
        self,
        template_id: str,
        tag_ids: list[str],
        user_id: str,
    ) -> None:
        """Reassign tags to a template (remove old, add new)."""
        # Remove existing tags
        delete_query = select(TemplateTag).where(TemplateTag.template_id == template_id)
        result = await self.db.execute(delete_query)
        existing_tags = result.scalars().all()

        for template_tag in existing_tags:
            await self.db.delete(template_tag)

        # Add new tags
        await self._assign_tags_to_template(template_id, tag_ids, user_id)
