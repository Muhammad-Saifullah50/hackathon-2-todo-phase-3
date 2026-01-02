"""Global exception handlers for standardized error responses."""

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.schemas.responses import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with standardized error response format.

    Args:
        request: The incoming request.
        exc: The HTTPException raised.

    Returns:
        JSONResponse with standardized error format.
    """
    # Extract error details from exception
    detail = exc.detail
    error_message = str(detail)
    error_code = "HTTP_ERROR"

    # Handle structured error details
    if isinstance(detail, dict):
        error_message = detail.get("message", str(detail))
        error_code = detail.get("code", f"HTTP_{exc.status_code}")
    else:
        error_code = f"HTTP_{exc.status_code}"

    # Log error for debugging (but not sensitive data)
    logger.warning(
        f"HTTP {exc.status_code} error: {error_code}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )

    # Create standardized error response
    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code=error_code,
            message=error_message,
        ),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with standardized format.

    Args:
        request: The incoming request.
        exc: The validation error raised.

    Returns:
        JSONResponse with standardized error format.
    """
    # Extract validation errors
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        message = error["msg"]
        error_messages.append(f"{field}: {message}" if field else message)

    # Combine all error messages
    combined_message = "; ".join(error_messages)

    logger.warning(
        f"Validation error: {combined_message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_count": len(errors),
        },
    )

    # Create standardized error response
    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message=f"Invalid request data: {combined_message}",
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with standardized error response.

    Args:
        request: The incoming request.
        exc: The exception raised.

    Returns:
        JSONResponse with standardized error format.
    """
    # Log full exception details for debugging
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    # Create standardized error response (don't expose internal details)
    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )
