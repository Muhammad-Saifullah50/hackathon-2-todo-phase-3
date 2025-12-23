"""RecurrencePattern model for task recurrence patterns."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, SQLModel


class RecurrencePattern(SQLModel, table=True):
    """Model for task recurrence patterns.

    Defines how a task should recur (daily, weekly, monthly) with configurable
    parameters like interval, specific days, and end conditions.
    """

    __tablename__ = "recurrence_patterns"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", unique=True, index=True)

    # Recurrence configuration
    frequency: str = Field(max_length=50)  # 'daily', 'weekly', 'monthly'
    interval: int = Field(ge=1)  # Every N days/weeks/months
    days_of_week: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))  # [0-6] for weekly
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)  # Day of month for monthly

    # End conditions
    end_date: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))

    # Next occurrence tracking
    next_occurrence_date: datetime = Field(index=True, sa_type=DateTime(timezone=True))

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "frequency": "weekly",
                "interval": 1,
                "days_of_week": [1, 3, 5],  # Monday, Wednesday, Friday
                "next_occurrence_date": "2025-12-25T10:00:00Z"
            }
        }
