"""View preference model for storing user UI preferences."""

from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, UniqueConstraint

from .base import TimestampMixin


class ViewPreference(TimestampMixin, table=True):
    """Database model for storing user view preferences.

    Stores key-value pairs for user preferences like layout (list/grid).

    Attributes:
        id: Unique UUID identifier for the preference.
        user_id: Foreign key to the User who owns this preference.
        preference_key: The preference identifier (e.g., 'tasks_layout').
        preference_value: The preference value (e.g., 'list' or 'grid').
        created_at: Timestamp when preference was created (from TimestampMixin).
        updated_at: Timestamp when preference was last modified (from TimestampMixin).
    """

    __tablename__ = "view_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "preference_key", name="uq_user_preference_key"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the preference",
    )
    user_id: str = Field(
        foreign_key="user.id", index=True, description="ID of the user who owns this preference"
    )
    preference_key: str = Field(
        index=True, max_length=100, description="The preference identifier"
    )
    preference_value: str = Field(max_length=500, description="The preference value")


class ViewPreferenceCreate(SQLModel):
    """Schema for creating a new view preference.

    Attributes:
        preference_key: The preference identifier (required).
        preference_value: The preference value (required).
    """

    preference_key: str = Field(max_length=100, description="The preference identifier")
    preference_value: str = Field(max_length=500, description="The preference value")


class ViewPreferenceUpdate(SQLModel):
    """Schema for updating an existing view preference.

    Attributes:
        preference_value: The new preference value (required).
    """

    preference_value: str = Field(max_length=500, description="The new preference value")


class ViewPreferenceResponse(SQLModel):
    """Schema for view preference response payloads.

    Includes all fields from the database model.
    """

    id: UUID
    user_id: str
    preference_key: str
    preference_value: str
