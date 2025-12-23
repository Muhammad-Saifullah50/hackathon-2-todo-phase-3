"""Request and response schemas for search operations."""

from pydantic import BaseModel, Field

from ..models.task import TaskResponse
from .task_schemas import PaginationInfo, TaskMetadata


class SearchResponse(BaseModel):
    """Response schema for search results.

    Attributes:
        tasks: List of tasks matching the search criteria.
        query: The search query that was used.
        total_results: Total number of matching tasks.
        metadata: Task count statistics.
        pagination: Pagination information.
    """

    tasks: list[TaskResponse] = Field(description="List of matching tasks")
    query: str | None = Field(description="The search query used")
    total_results: int = Field(ge=0, description="Total number of matching tasks")
    metadata: TaskMetadata = Field(description="Task count statistics")
    pagination: PaginationInfo = Field(description="Pagination information")


class AutocompleteSuggestion(BaseModel):
    """Single autocomplete suggestion.

    Attributes:
        id: Task ID for the suggestion.
        title: Task title to display.
        status: Task status for visual indicator.
    """

    id: str = Field(description="Task ID")
    title: str = Field(description="Task title")
    status: str = Field(description="Task status")


class AutocompleteResponse(BaseModel):
    """Response schema for autocomplete suggestions.

    Attributes:
        suggestions: List of matching task title suggestions.
    """

    suggestions: list[AutocompleteSuggestion] = Field(
        description="List of autocomplete suggestions"
    )


class QuickFilterOption(BaseModel):
    """Single quick filter option with count.

    Attributes:
        id: Filter identifier (e.g., 'today', 'overdue').
        label: Display label for the filter.
        count: Number of tasks matching this filter.
        filter_params: Query parameters to apply this filter.
    """

    id: str = Field(description="Filter identifier")
    label: str = Field(description="Display label")
    count: int = Field(ge=0, description="Number of matching tasks")
    filter_params: dict = Field(description="Query parameters to apply filter")


class QuickFiltersResponse(BaseModel):
    """Response schema for quick filters with counts.

    Attributes:
        filters: List of available quick filters with counts.
    """

    filters: list[QuickFilterOption] = Field(description="Available quick filters")
