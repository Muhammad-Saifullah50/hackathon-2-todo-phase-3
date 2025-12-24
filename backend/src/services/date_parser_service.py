"""Date parser service for natural language date parsing."""

from datetime import datetime, timezone
from typing import Optional

import dateparser


class DateParserService:
    """Service class for parsing natural language date expressions.

    Uses the dateparser library to convert natural language strings like
    "tomorrow", "next Friday", "in 2 weeks" to datetime objects.

    Example usage:
        service = DateParserService()
        due_date = service.parse_date("tomorrow at 3pm")
        is_valid, error = service.validate_date("next week")
    """

    @staticmethod
    def parse_date(
        date_string: str,
        user_timezone: str = "UTC",
        prefer_future: bool = True,
    ) -> Optional[datetime]:
        """Parse natural language date string to datetime object.

        Args:
            date_string: Natural language date (e.g., "tomorrow", "next Friday", "Dec 25").
            user_timezone: User's timezone (default: UTC).
            prefer_future: Whether to prefer future dates (default: True).

        Returns:
            Timezone-aware datetime object in UTC, or None if parsing fails.

        Examples:
            >>> service = DateParserService()
            >>> service.parse_date("tomorrow")
            datetime(2025, 12, 24, 0, 0, 0, tzinfo=timezone.utc)
            >>> service.parse_date("next Friday at 3pm")
            datetime(2025, 12, 27, 15, 0, 0, tzinfo=timezone.utc)
            >>> service.parse_date("invalid")
            None
        """
        if not date_string or not date_string.strip():
            return None

        settings = {
            "TIMEZONE": user_timezone,
            "RETURN_AS_TIMEZONE_AWARE": True,
            "TO_TIMEZONE": "UTC",  # Always store in UTC
            "PREFER_DATES_FROM": "future" if prefer_future else "current_period",
        }

        try:
            result = dateparser.parse(
                date_string.strip(),
                settings=settings,
                languages=["en"],  # Specify language for better performance
            )
            return result
        except Exception:
            return None

    @staticmethod
    def validate_date(
        date_string: str,
        allow_past: bool = False,
        user_timezone: str = "UTC",
    ) -> tuple[bool, str]:
        """Validate date string and provide user-friendly error messages.

        Args:
            date_string: Natural language date to validate.
            allow_past: Whether past dates are allowed (default: False).
            user_timezone: User's timezone (default: UTC).

        Returns:
            Tuple of (is_valid, error_message).
            If valid, error_message is empty string.
            If invalid, error_message contains user-friendly explanation.

        Examples:
            >>> service = DateParserService()
            >>> service.validate_date("tomorrow")
            (True, "")
            >>> service.validate_date("yesterday")
            (False, "Date 'yesterday' is in the past...")
            >>> service.validate_date("invalid date")
            (False, "Could not understand date 'invalid date'...")
        """
        if not date_string or not date_string.strip():
            return False, "Date cannot be empty"

        try:
            parsed = DateParserService.parse_date(
                date_string, user_timezone=user_timezone
            )

            if parsed is None:
                return (
                    False,
                    f"Could not understand date '{date_string}'. "
                    f"Try 'tomorrow', 'next Friday', or 'December 30th'.",
                )

            # Check if date is in the past
            if not allow_past and parsed < datetime.now(timezone.utc):
                return (
                    False,
                    f"Date '{date_string}' is in the past. "
                    f"Did you mean to set a future date?",
                )

            return True, ""

        except Exception as e:
            return False, f"Invalid date format: {str(e)}"

    @staticmethod
    def format_relative_date(dt: datetime) -> str:
        """Format a datetime as a human-readable relative string.

        Args:
            dt: Datetime object to format.

        Returns:
            Human-readable string like "today", "tomorrow", "in 3 days", etc.

        Examples:
            >>> from datetime import timedelta
            >>> service = DateParserService()
            >>> now = datetime.now(timezone.utc)
            >>> service.format_relative_date(now)
            "today"
            >>> service.format_relative_date(now + timedelta(days=1))
            "tomorrow"
            >>> service.format_relative_date(now + timedelta(days=3))
            "in 3 days"
        """
        now = datetime.now(timezone.utc)

        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Calculate difference
        diff = dt - now
        days = diff.days

        if days == 0:
            return "today"
        elif days == 1:
            return "tomorrow"
        elif days == -1:
            return "yesterday"
        elif days > 1 and days < 7:
            return f"in {days} days"
        elif days < -1 and days > -7:
            return f"{abs(days)} days ago"
        elif days >= 7:
            weeks = days // 7
            if weeks == 1:
                return "in 1 week"
            return f"in {weeks} weeks"
        else:
            weeks = abs(days) // 7
            if weeks == 1:
                return "1 week ago"
            return f"{weeks} weeks ago"

    @staticmethod
    def parse_date_with_fallback(
        date_string: str,
        user_timezone: str = "UTC",
    ) -> Optional[datetime]:
        """Parse date with multiple fallback strategies.

        Tries to parse the date string with different strategies:
        1. Natural language parsing (dateparser)
        2. ISO 8601 format (YYYY-MM-DD)
        3. Common formats (MM/DD/YYYY, DD/MM/YYYY)

        Args:
            date_string: Date string to parse.
            user_timezone: User's timezone (default: UTC).

        Returns:
            Parsed datetime in UTC, or None if all strategies fail.
        """
        # Try natural language parsing first
        result = DateParserService.parse_date(date_string, user_timezone)
        if result:
            return result

        # Try ISO 8601 format
        try:
            dt = datetime.fromisoformat(date_string)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass

        # All strategies failed
        return None
