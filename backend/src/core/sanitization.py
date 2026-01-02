"""Input sanitization utilities for XSS prevention."""

from typing import Any

import bleach


def sanitize_html(text: str | None) -> str | None:
    """Sanitize HTML/text input to prevent XSS attacks.

    Removes dangerous HTML tags and attributes while preserving safe formatting.
    Allows basic text formatting tags commonly used in markdown/rich text.

    Args:
        text: The text to sanitize (can be None).

    Returns:
        Sanitized text with dangerous content removed, or None if input is None.

    Examples:
        >>> sanitize_html("<script>alert('XSS')</script>Hello")
        'Hello'
        >>> sanitize_html("<b>Bold text</b>")
        '<b>Bold text</b>'
        >>> sanitize_html(None)
        None
    """
    if text is None:
        return None

    # Strip whitespace first
    text = text.strip()
    if not text:
        return text

    # Define allowed tags for safe formatting
    # These are commonly used in markdown and rich text editors
    allowed_tags = [
        "b",
        "i",
        "u",
        "em",
        "strong",
        "a",
        "p",
        "br",
        "ul",
        "ol",
        "li",
        "code",
        "pre",
        "blockquote",
    ]

    # Define allowed attributes for specific tags
    allowed_attributes = {
        "a": ["href", "title"],  # Links can have href and title
        "code": ["class"],  # Code blocks can have language class
    }

    # Clean the text using bleach
    sanitized = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,  # Strip disallowed tags instead of escaping
    )

    return sanitized


def sanitize_text(text: str | None, max_length: int | None = None) -> str | None:
    """Sanitize plain text input by removing HTML and limiting length.

    For fields that should only contain plain text (no formatting).

    Args:
        text: The text to sanitize (can be None).
        max_length: Optional maximum length to enforce.

    Returns:
        Sanitized plain text, or None if input is None.

    Examples:
        >>> sanitize_text("<b>Hello</b>")
        'Hello'
        >>> sanitize_text("Hello World", max_length=5)
        'Hello'
    """
    if text is None:
        return None

    # Strip whitespace
    text = text.strip()
    if not text:
        return text

    # Remove all HTML tags
    sanitized = bleach.clean(text, tags=[], strip=True)

    # Enforce max length if specified
    if max_length is not None and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def sanitize_url(url: str | None) -> str | None:
    """Sanitize URL to prevent javascript: and data: URL attacks.

    Args:
        url: The URL to sanitize (can be None).

    Returns:
        Sanitized URL or None if unsafe/invalid.

    Examples:
        >>> sanitize_url("https://example.com")
        'https://example.com'
        >>> sanitize_url("javascript:alert('XSS')")
        None
        >>> sanitize_url("data:text/html,<script>alert('XSS')</script>")
        None
    """
    if url is None:
        return None

    url = url.strip()
    if not url:
        return None

    # Check for dangerous protocols
    dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
    url_lower = url.lower()

    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return None

    # Only allow http, https, and relative URLs
    if not (
        url_lower.startswith("http://")
        or url_lower.startswith("https://")
        or url_lower.startswith("/")
        or url_lower.startswith("./")
        or url_lower.startswith("../")
    ):
        return None

    return url


def sanitize_dict(
    data: dict[str, Any], text_fields: list[str], html_fields: list[str] | None = None
) -> dict[str, Any]:
    """Sanitize multiple fields in a dictionary.

    Args:
        data: The dictionary to sanitize.
        text_fields: List of field names to sanitize as plain text.
        html_fields: Optional list of field names to sanitize as HTML.

    Returns:
        Dictionary with sanitized fields.

    Examples:
        >>> sanitize_dict(
        ...     {"title": "<b>Task</b>", "description": "Details"},
        ...     text_fields=["title"],
        ...     html_fields=["description"]
        ... )
        {'title': 'Task', 'description': 'Details'}
    """
    sanitized = data.copy()

    # Sanitize plain text fields
    for field in text_fields:
        if field in sanitized and isinstance(sanitized[field], str):
            sanitized[field] = sanitize_text(sanitized[field])

    # Sanitize HTML fields
    if html_fields:
        for field in html_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = sanitize_html(sanitized[field])

    return sanitized
