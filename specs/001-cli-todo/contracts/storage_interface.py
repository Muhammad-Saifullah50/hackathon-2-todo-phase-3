"""Storage layer interface contract.

This module defines the protocol for storage implementations. Any storage backend
(JSON file, SQLite, PostgreSQL, etc.) must implement this interface.
"""

from pathlib import Path
from typing import Protocol


class StorageInterface(Protocol):
    """Protocol defining the storage layer contract.

    This protocol uses structural subtyping (PEP 544) to define the interface
    that all storage implementations must follow. Implementations don't need to
    explicitly inherit from this protocol.

    The storage layer is responsible for:
    - Loading task data from persistent storage
    - Saving task data to persistent storage atomically
    - Creating backups before destructive operations
    - Handling file I/O errors gracefully
    """

    def load(self) -> dict[str, any]:
        """Load task data from storage.

        Returns:
            Dictionary with structure:
            {
                "version": "1.0.0",
                "tasks": [
                    {
                        "id": "abc123de",
                        "title": "Task title",
                        "description": "Task description",
                        "status": "pending",
                        "created_at": "2025-12-18 10:00:00",
                        "updated_at": "2025-12-18 10:00:00"
                    },
                    ...
                ]
            }

        Raises:
            StorageError: If storage file cannot be read
            FileCorruptionError: If JSON is malformed or schema is invalid
            FilePermissionError: If file permissions deny read access

        Notes:
            - If file doesn't exist, should auto-create with empty state
            - If file is corrupted, should create backup and reset to empty
            - Should validate schema version and structure
        """
        ...

    def save(self, data: dict[str, any]) -> None:
        """Save task data to storage atomically.

        Args:
            data: Dictionary with same structure as load() returns

        Raises:
            StorageError: If storage file cannot be written
            FilePermissionError: If file permissions deny write access

        Notes:
            - MUST use atomic write pattern (temp file + rename)
            - MUST set user-only file permissions (0o600 on Unix)
            - MUST validate data structure before writing
            - Should fsync to ensure data hits disk
        """
        ...

    def create_backup(self) -> Path | None:
        """Create backup of current storage file.

        Returns:
            Path to backup file if successful, None if no file to backup

        Raises:
            StorageError: If backup creation fails

        Notes:
            - Backup filename: {original}.backup (e.g., tasks.json.backup)
            - Should overwrite existing backup
            - Only called before potentially destructive operations
        """
        ...

    @property
    def file_path(self) -> Path:
        """Get the path to the storage file.

        Returns:
            Absolute path to storage file

        Notes:
            - Used for error messages and debugging
            - Should be absolute path, not relative
        """
        ...


# Type alias for easier imports
Storage = StorageInterface
