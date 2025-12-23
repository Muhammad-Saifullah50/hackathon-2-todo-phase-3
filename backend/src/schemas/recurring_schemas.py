"""Schemas for recurrence pattern operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RecurrencePatternCreate(BaseModel):
    """Schema for creating a recurrence pattern."""

    frequency: str = Field(..., description="Recurrence frequency: 'daily', 'weekly', or 'monthly'")
    interval: int = Field(ge=1, le=365, description="Recurrence interval (e.g., every N days/weeks/months)")
    days_of_week: Optional[List[int]] = Field(
        default=None,
        description="Days of week for weekly recurrence (0=Monday, 6=Sunday)"
    )
    day_of_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="Day of month for monthly recurrence"
    )
    end_date: Optional[datetime] = Field(default=None, description="Optional end date for recurrence")

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        """Validate frequency is one of the allowed values."""
        allowed = ["daily", "weekly", "monthly"]
        if v.lower() not in allowed:
            raise ValueError(f"Frequency must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate days of week are in valid range."""
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
            if len(v) == 0:
                raise ValueError("Days of week cannot be empty if provided")
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "frequency": "weekly",
                "interval": 1,
                "days_of_week": [1, 3, 5],
                "end_date": "2026-12-31T23:59:59Z"
            }
        }


class RecurrencePatternUpdate(BaseModel):
    """Schema for updating a recurrence pattern."""

    frequency: Optional[str] = Field(None, description="Recurrence frequency")
    interval: Optional[int] = Field(None, ge=1, le=365, description="Recurrence interval")
    days_of_week: Optional[List[int]] = Field(None, description="Days of week for weekly recurrence")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month for monthly recurrence")
    end_date: Optional[datetime] = Field(None, description="End date for recurrence")

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate frequency is one of the allowed values."""
        if v is not None:
            allowed = ["daily", "weekly", "monthly"]
            if v.lower() not in allowed:
                raise ValueError(f"Frequency must be one of: {', '.join(allowed)}")
            return v.lower()
        return v

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate days of week are in valid range."""
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
            if len(v) == 0:
                raise ValueError("Days of week cannot be empty if provided")
        return v


class RecurrencePatternResponse(BaseModel):
    """Schema for recurrence pattern response."""

    id: UUID
    task_id: UUID
    frequency: str
    interval: int
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    end_date: Optional[datetime] = None
    next_occurrence_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "task_id": "123e4567-e89b-12d3-a456-426614174001",
                "frequency": "weekly",
                "interval": 2,
                "days_of_week": [1, 3, 5],
                "day_of_month": None,
                "end_date": None,
                "next_occurrence_date": "2025-12-25T10:00:00Z",
                "created_at": "2025-12-20T10:00:00Z",
                "updated_at": "2025-12-20T10:00:00Z"
            }
        }


class RecurrencePreviewResponse(BaseModel):
    """Schema for previewing upcoming recurrence dates."""

    dates: List[datetime] = Field(..., description="List of upcoming occurrence dates")
    count: int = Field(..., description="Number of dates returned")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "dates": [
                    "2025-12-25T10:00:00Z",
                    "2026-01-01T10:00:00Z",
                    "2026-01-08T10:00:00Z",
                    "2026-01-15T10:00:00Z",
                    "2026-01-22T10:00:00Z"
                ],
                "count": 5
            }
        }
