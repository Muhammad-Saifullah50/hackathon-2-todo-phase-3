"""Standardized error and success response helpers for API endpoints."""

from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Create a standardized error response.

    Args:
        message: Human-readable error message.
        status_code: HTTP status code (default: 400).
        details: Optional additional error details.

    Returns:
        JSONResponse with standardized error format.
    """
    content = {
        "status": "error",
        "message": message,
    }

    if details:
        content["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def success_response(
    data: Any,
    message: str | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Create a standardized success response.

    Args:
        data: Response data payload.
        message: Optional success message.
        status_code: HTTP status code (default: 200).

    Returns:
        JSONResponse with standardized success format.
    """
    content = {
        "status": "success",
        "data": data,
    }

    if message:
        content["message"] = message

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def raise_not_found(resource: str, identifier: str | None = None) -> None:
    """Raise a standardized 404 Not Found exception.

    Args:
        resource: The type of resource not found (e.g., "Task", "User").
        identifier: Optional identifier of the resource.

    Raises:
        HTTPException with 404 status code.
    """
    if identifier:
        message = f"{resource} with ID '{identifier}' not found"
    else:
        message = f"{resource} not found"

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message,
    )


def raise_forbidden(message: str = "You do not have permission to access this resource") -> None:
    """Raise a standardized 403 Forbidden exception.

    Args:
        message: Custom forbidden message.

    Raises:
        HTTPException with 403 status code.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


def raise_bad_request(message: str, details: dict[str, Any] | None = None) -> None:
    """Raise a standardized 400 Bad Request exception.

    Args:
        message: Error message describing the bad request.
        details: Optional additional error details.

    Raises:
        HTTPException with 400 status code.
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"message": message, "details": details} if details else message,
    )
