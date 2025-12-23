"""Template API routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.template_schemas import (
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
)
from src.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=TemplateListResponse)
async def get_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all templates for the current user."""
    service = TemplateService(db)
    templates, total = await service.get_templates(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )

    return TemplateListResponse(
        templates=templates,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new template."""
    service = TemplateService(db)
    template = await service.create_template(
        user_id=current_user.id,
        template_data=template_data,
    )

    return template


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific template."""
    service = TemplateService(db)
    template = await service.get_template(template_id, current_user.id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a template."""
    service = TemplateService(db)
    template = await service.update_template(
        template_id=template_id,
        user_id=current_user.id,
        template_data=template_data,
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a template."""
    service = TemplateService(db)
    success = await service.delete_template(template_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Template not found")


@router.post("/{template_id}/apply", response_model=dict, status_code=201)
async def apply_template(
    template_id: str,
    due_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task from a template."""
    service = TemplateService(db)
    task = await service.apply_template(
        template_id=template_id,
        user_id=current_user.id,
        due_date=due_date,
    )

    if not task:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"task_id": task.id, "message": "Task created from template successfully"}


@router.post("/tasks/{task_id}/save-as-template", response_model=TemplateResponse, status_code=201)
async def save_task_as_template(
    task_id: str,
    template_name: str = Query(..., min_length=1, max_length=100),
    include_subtasks: bool = Query(True),
    include_tags: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save an existing task as a template."""
    service = TemplateService(db)
    template = await service.save_task_as_template(
        task_id=task_id,
        user_id=current_user.id,
        template_name=template_name,
        include_subtasks=include_subtasks,
        include_tags=include_tags,
    )

    if not template:
        raise HTTPException(status_code=404, detail="Task not found")

    return template
