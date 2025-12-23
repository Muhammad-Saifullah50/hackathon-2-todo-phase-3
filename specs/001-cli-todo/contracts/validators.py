"""Input validation contract specifications.

This module defines the validation functions that must be implemented to ensure
data integrity at system boundaries (CLI input and persistence layer).
"""

import re
from datetime import datetime
from typing import Final

# Validation constants
MAX_TITLE_WORDS: Final[int] = 10
MAX_DESCRIPTION_CHARS: Final[int] = 500
ID_LENGTH: Final[int] = 8
ID_PATTERN: Final[re.Pattern] = re.compile(r"^[0-9a-f]{8}$")
ALLOWED_STATUSES: Final[set[str]] = {"pending", "completed"}
TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
MIN_TERMINAL_WIDTH: Final[int] = 80


def validate_title(title: str) -> None:
    """Validate task title.

    Rules:
    - Not empty after stripping whitespace
    - 1-10 words (space-separated)
    - Leading/trailing whitespace is stripped

    Args:
        title: Task title to validate

    Raises:
        TaskValidationError: If title is invalid with specific error message:
            - "Title cannot be empty (min 1 character required)"
            - "Title too long (X words, max 10 words allowed)"

    Examples:
        >>> validate_title("Buy groceries")  # OK
        >>> validate_title("  ")  # Raises: Title cannot be empty
        >>> validate_title("One two three four five six seven eight nine ten eleven")
        # Raises: Title too long (11 words, max 10 words allowed)
    """
    ...


def validate_description(description: str) -> None:
    """Validate task description.

    Rules:
    - 0-500 characters
    - Empty string is valid (optional field)
    - Multiline allowed

    Args:
        description: Task description to validate

    Raises:
        TaskValidationError: If description is invalid with specific error message:
            - "Description too long (X characters, max 500 characters allowed)"

    Examples:
        >>> validate_description("")  # OK (empty allowed)
        >>> validate_description("Short description")  # OK
        >>> validate_description("a" * 501)  # Raises: Description too long
    """
    ...


def validate_id(task_id: str) -> None:
    """Validate task ID format.

    Rules:
    - Exactly 8 characters
    - Lowercase hexadecimal (0-9, a-f only)

    Args:
        task_id: Task ID to validate

    Raises:
        TaskValidationError: If ID is invalid with specific error message:
            - "Invalid ID format: 'X' (must be 8 hex characters)"

    Examples:
        >>> validate_id("abc123de")  # OK
        >>> validate_id("ABC123DE")  # Raises: Invalid ID format (uppercase)
        >>> validate_id("abc123")    # Raises: Invalid ID format (too short)
        >>> validate_id("xyz123de")  # Raises: Invalid ID format (invalid chars)
    """
    ...


def validate_status(status: str) -> None:
    """Validate task status.

    Rules:
    - Must be exactly "pending" or "completed"
    - Case-sensitive

    Args:
        status: Task status to validate

    Raises:
        TaskValidationError: If status is invalid with specific error message:
            - "Invalid status: 'X' (must be 'pending' or 'completed')"

    Examples:
        >>> validate_status("pending")    # OK
        >>> validate_status("completed")  # OK
        >>> validate_status("Pending")    # Raises: Invalid status (case mismatch)
        >>> validate_status("done")       # Raises: Invalid status (wrong value)
    """
    ...


def validate_timestamp(timestamp: str) -> None:
    """Validate ISO 8601 timestamp format.

    Rules:
    - Format: YYYY-MM-DD HH:MM:SS
    - Must be parseable as datetime
    - No timezone suffix

    Args:
        timestamp: Timestamp string to validate

    Raises:
        TaskValidationError: If timestamp is invalid with specific error message:
            - "Invalid timestamp format: 'X' (expected YYYY-MM-DD HH:MM:SS)"

    Examples:
        >>> validate_timestamp("2025-12-18 10:30:45")  # OK
        >>> validate_timestamp("2025-12-18")           # Raises: Invalid format
        >>> validate_timestamp("12/18/2025 10:30")     # Raises: Invalid format
        >>> validate_timestamp("invalid")              # Raises: Invalid format
    """
    ...


def validate_terminal_width(width: int) -> None:
    """Validate terminal width meets minimum requirement.

    Rules:
    - Width must be >= 80 columns

    Args:
        width: Terminal width in columns

    Raises:
        TerminalError: If terminal is too narrow with specific error message:
            - "⚠️ Terminal too narrow. Please resize to at least 80 columns."

    Examples:
        >>> validate_terminal_width(80)   # OK
        >>> validate_terminal_width(100)  # OK
        >>> validate_terminal_width(79)   # Raises: Terminal too narrow
    """
    ...


def validate_page_number(page: int, max_page: int) -> None:
    """Validate pagination page number.

    Rules:
    - Page must be >= 0 (zero-indexed)
    - Page must be < max_page (if max_page > 0)

    Args:
        page: Zero-indexed page number
        max_page: Maximum valid page number (exclusive)

    Raises:
        PaginationError: If page is invalid with specific error message:
            - "Invalid page number: X (must be 0-Y)"

    Examples:
        >>> validate_page_number(0, 5)   # OK (page 0 of 5 total pages)
        >>> validate_page_number(4, 5)   # OK (last valid page)
        >>> validate_page_number(-1, 5)  # Raises: Invalid page number
        >>> validate_page_number(5, 5)   # Raises: Invalid page number (out of range)
    """
    ...


def validate_non_empty_selection(selected_ids: list[str]) -> None:
    """Validate that at least one item is selected.

    Rules:
    - List must not be empty
    - Used for bulk operations (delete, mark complete)

    Args:
        selected_ids: List of selected task IDs

    Raises:
        ValidationError: If selection is empty with specific error message:
            - "❌ No tasks selected. Please select at least one task."

    Examples:
        >>> validate_non_empty_selection(["abc123de"])  # OK
        >>> validate_non_empty_selection([])            # Raises: No tasks selected
    """
    ...


# Validation helper functions

def is_valid_id(task_id: str) -> bool:
    """Check if task ID format is valid (non-raising).

    Args:
        task_id: Task ID to check

    Returns:
        True if ID format is valid, False otherwise

    Examples:
        >>> is_valid_id("abc123de")  # True
        >>> is_valid_id("invalid")   # False
    """
    return bool(ID_PATTERN.match(task_id))


def is_valid_status(status: str) -> bool:
    """Check if status value is valid (non-raising).

    Args:
        status: Status to check

    Returns:
        True if status is valid, False otherwise

    Examples:
        >>> is_valid_status("pending")    # True
        >>> is_valid_status("completed")  # True
        >>> is_valid_status("done")       # False
    """
    return status in ALLOWED_STATUSES


def is_valid_timestamp(timestamp: str) -> bool:
    """Check if timestamp format is valid (non-raising).

    Args:
        timestamp: Timestamp to check

    Returns:
        True if timestamp is parseable, False otherwise

    Examples:
        >>> is_valid_timestamp("2025-12-18 10:30:45")  # True
        >>> is_valid_timestamp("invalid")              # False
    """
    try:
        datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        return True
    except ValueError:
        return False


def count_words(text: str) -> int:
    """Count words in text (space-separated).

    Args:
        text: Text to count words in

    Returns:
        Number of words (after stripping whitespace)

    Examples:
        >>> count_words("Buy groceries")      # 2
        >>> count_words("  spaced   out  ")   # 2
        >>> count_words("")                   # 0
    """
    return len(text.strip().split())


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated (default: "...")

    Returns:
        Truncated text with suffix if needed

    Examples:
        >>> truncate_text("Short", 10)                    # "Short"
        >>> truncate_text("Very long text here", 10)      # "Very lo..."
        >>> truncate_text("Exactly ten", 10)              # "Exactly ten"
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
