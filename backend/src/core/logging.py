"""Structured JSON logging configuration with request_id tracking.

This module sets up structured logging for the application with:
- JSON format for machine-readable logs
- Request ID tracking for distributed tracing
- Standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Integration with FastAPI middleware
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from pythonjsonlogger import jsonlogger

# Context variable for request ID (thread-safe)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    """Add request_id to all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to log record.

        Args:
            record: Log record to augment.

        Returns:
            Always True to pass the record through.
        """
        record.request_id = request_id_var.get("")
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with timestamp and structured fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to JSON log record.

        Args:
            log_record: Dictionary to add fields to.
            record: Original log record.
            message_dict: Message dictionary.
        """
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO 8601 format with UTC timezone
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Add log level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add request_id if available
        if hasattr(record, "request_id") and record.request_id:
            log_record["request_id"] = record.request_id

        # Add file and line information
        log_record["file"] = record.pathname
        log_record["line"] = record.lineno
        log_record["function"] = record.funcName


def setup_logging(
    level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_logs: Whether to use JSON format (True) or plain text (False).
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set log level
    root_logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Set formatter based on json_logs flag
    if json_logs:
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)

    # Add request ID filter
    request_id_filter = RequestIdFilter()
    console_handler.addFilter(request_id_filter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_request_id() -> str:
    """Get current request ID from context.

    Returns:
        Current request ID or empty string if not set.
    """
    return request_id_var.get("")


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID in context.

    Args:
        request_id: Request ID to set (generates new UUID if None).

    Returns:
        The request ID that was set.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())

    request_id_var.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_var.set("")


def log_tool_invocation(
    tool_name: str,
    args: dict[str, Any],
    result: Any = None,
    error: Exception | None = None,
) -> None:
    """Log tool invocation with structured data.

    Args:
        tool_name: Name of the tool that was invoked.
        args: Arguments passed to the tool.
        result: Result returned by the tool (optional).
        error: Exception raised by the tool (optional).
    """
    logger = logging.getLogger(__name__)

    log_data = {
        "tool_name": tool_name,
        "args": args,
        "request_id": get_request_id(),
    }

    if error:
        log_data["error"] = str(error)
        log_data["error_type"] = type(error).__name__
        logger.error(f"Tool invocation failed: {tool_name}", extra=log_data)
    else:
        if result is not None:
            # Truncate large results for logging
            result_str = str(result)
            if len(result_str) > 500:
                result_str = result_str[:500] + "... (truncated)"
            log_data["result"] = result_str

        logger.info(f"Tool invocation: {tool_name}", extra=log_data)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
