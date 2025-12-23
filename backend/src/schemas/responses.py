from typing import Any

from pydantic import BaseModel


class StandardizedResponse[T](BaseModel):
    """Standard API response wrapper.

    Attributes:
        success: Boolean indicating operation success.
        message: Human-readable message.
        data: Payload data (optional).
        meta: Pagination or other metadata (optional).
    """

    success: bool = True
    message: str = "Operation completed successfully"
    data: T | None = None
    meta: dict[str, Any] | None = None


class ErrorDetail(BaseModel):
    """Detailed error information.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable error message.
        field: Field name if validation error (optional).
    """

    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response structure.

    Attributes:
        success: Always False for errors.
        error: Error details object.
    """

    success: bool = False
    error: ErrorDetail


class PaginationMeta(BaseModel):
    """Metadata for paginated responses.

    Attributes:
        total: Total number of items.
        page: Current page number.
        limit: Items per page.
        pages: Total number of pages.
    """

    total: int
    page: int
    limit: int
    pages: int
