# Data Model: CLI Todo Application

**Date**: 2025-12-18
**Phase**: 1 (Design)
**Status**: Complete

## Overview

This document defines the complete data model for the CLI Todo Application, including entity definitions, field specifications, validation rules, state transitions, and JSON storage schema.

---

## Entity: Task

### Description
Represents a single todo item with title, optional description, completion status, and timestamps.

### Fields

| Field | Type | Required | Constraints | Default | Description |
|-------|------|----------|-------------|---------|-------------|
| `id` | string | Yes | 8 hex characters, unique | Generated | Unique identifier (first 8 chars of UUID4) |
| `title` | string | Yes | 1-10 words | - | Short task description |
| `description` | string | No | 0-500 characters | Empty string | Detailed task information |
| `status` | string | Yes | "pending" or "completed" | "pending" | Task completion status |
| `created_at` | string | Yes | ISO 8601 format | Current timestamp | When task was created |
| `updated_at` | string | Yes | ISO 8601 format | Current timestamp | When task was last modified |

### Field Details

#### `id` (Unique Identifier)
- **Format**: 8 lowercase hexadecimal characters (0-9, a-f)
- **Generation**: `uuid.uuid4().hex[:8]`
- **Uniqueness**: Collision detection with regeneration loop
- **Example**: `"a3f5b8c2"`, `"7d2e9f14"`
- **Validation**: Regex `^[0-9a-f]{8}$`

#### `title` (Task Title)
- **Format**: Plain text string
- **Length**: 1 to 10 words (space-separated)
- **Validation**:
  - Must not be empty (min 1 character after strip)
  - Word count: `len(title.strip().split()) <= 10`
  - Leading/trailing whitespace stripped
- **Examples**:
  - Valid: `"Buy groceries"`, `"Call mom tomorrow"`
  - Invalid: `""` (empty), `"One two three four five six seven eight nine ten eleven"` (11 words)
- **Special Characters**: Allows emojis, punctuation, Unicode

#### `description` (Task Description)
- **Format**: Plain text string, multiline allowed
- **Length**: 0 to 500 characters
- **Validation**:
  - Optional (empty string if not provided)
  - Character count: `len(description) <= 500`
- **Examples**:
  - Valid: `""` (empty), `"Milk, eggs, bread"`, `"Line 1\nLine 2"`
  - Invalid: (501+ character string)
- **Special Characters**: Allows emojis, newlines (`\n`), tabs, Unicode

#### `status` (Completion Status)
- **Format**: String enum
- **Values**: `"pending"` | `"completed"`
- **Validation**: Must be exactly one of the two allowed values
- **Default**: `"pending"` for new tasks
- **Display**: Rendered as ✗ (pending) or ✓ (completed) in UI

#### `created_at` (Creation Timestamp)
- **Format**: ISO 8601 datetime string (YYYY-MM-DD HH:MM:SS)
- **Timezone**: Local timezone (no timezone suffix)
- **Generation**: `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
- **Immutability**: Never changes after task creation
- **Example**: `"2025-12-18 10:30:45"`

#### `updated_at` (Last Modified Timestamp)
- **Format**: ISO 8601 datetime string (YYYY-MM-DD HH:MM:SS)
- **Timezone**: Local timezone (no timezone suffix)
- **Generation**: `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
- **Update Trigger**: Updated on every modification (title, description, status change)
- **Example**: `"2025-12-18 14:22:10"`

### Python Data Class

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """Represents a todo task.

    Attributes:
        id: Unique 8-character hexadecimal identifier
        title: Short task description (1-10 words)
        description: Detailed task information (0-500 chars, optional)
        status: Completion status ("pending" or "completed")
        created_at: ISO 8601 timestamp when task was created
        updated_at: ISO 8601 timestamp when task was last modified
    """

    id: str
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate all task fields.

        Raises:
            TaskValidationError: If any field fails validation
        """
        from src.services.validators import (
            validate_id,
            validate_title,
            validate_description,
            validate_status,
            validate_timestamp,
        )

        validate_id(self.id)
        validate_title(self.title)
        validate_description(self.description)
        validate_status(self.status)
        validate_timestamp(self.created_at)
        validate_timestamp(self.updated_at)

    def to_dict(self) -> dict[str, str]:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Task":
        """Create task from dictionary (JSON deserialization)."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def mark_completed(self) -> None:
        """Mark task as completed and update timestamp."""
        self.status = "completed"
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def mark_pending(self) -> None:
        """Mark task as pending and update timestamp."""
        self.status = "pending"
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_title(self, new_title: str) -> None:
        """Update task title and timestamp.

        Args:
            new_title: New title (will be validated)

        Raises:
            TaskValidationError: If new title is invalid
        """
        from src.services.validators import validate_title

        validate_title(new_title)
        self.title = new_title
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_description(self, new_description: str) -> None:
        """Update task description and timestamp.

        Args:
            new_description: New description (will be validated)

        Raises:
            TaskValidationError: If new description is invalid
        """
        from src.services.validators import validate_description

        validate_description(new_description)
        self.description = new_description
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

---

## State Transitions

### Status Lifecycle

```
┌─────────┐
│ pending │ ◄───────────────┐
└────┬────┘                 │
     │                      │
     │ mark_completed()     │ mark_pending()
     │                      │
     ▼                      │
┌───────────┐               │
│ completed │───────────────┘
└───────────┘
```

### Allowed Transitions

| From State | Action | To State | Updated Fields |
|-----------|--------|----------|----------------|
| pending | mark_completed() | completed | status, updated_at |
| completed | mark_pending() | pending | status, updated_at |
| pending | update_title() | pending | title, updated_at |
| completed | update_title() | completed | title, updated_at |
| pending | update_description() | pending | description, updated_at |
| completed | update_description() | completed | description, updated_at |
| * (any) | delete() | (removed) | N/A |

### Invariants

1. **Status Validity**: `status` must always be exactly `"pending"` or `"completed"` (no other values)
2. **Timestamp Order**: `created_at <= updated_at` (updated_at never earlier than created_at)
3. **ID Uniqueness**: No two tasks can have the same `id` value in storage
4. **Immutable Creation**: `created_at` never changes after initial creation
5. **Non-Empty Title**: `title` can never be empty string or whitespace-only

---

## JSON Storage Schema

### File Format

**Location**: `tasks.json` in project root directory
**Encoding**: UTF-8
**Indentation**: 2 spaces
**Format**: JSON with top-level object containing version and task array

### Schema Definition

```json
{
  "version": "1.0.0",
  "tasks": [
    {
      "id": "a3f5b8c2",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "created_at": "2025-12-18 10:30:45",
      "updated_at": "2025-12-18 10:30:45"
    },
    {
      "id": "7d2e9f14",
      "title": "Write tests",
      "description": "",
      "status": "completed",
      "created_at": "2025-12-18 09:00:00",
      "updated_at": "2025-12-18 11:15:22"
    }
  ]
}
```

### Schema Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Schema version (semantic versioning) |
| `tasks` | array | Yes | Array of task objects |

### Empty State

When no tasks exist, file contains:

```json
{
  "version": "1.0.0",
  "tasks": []
}
```

### Schema Versioning

**Current Version**: `1.0.0`

**Version Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Incompatible schema changes (breaking migrations required)
- **MINOR**: Backward-compatible additions (new optional fields)
- **PATCH**: Documentation or clarification changes (no schema impact)

**Future Migration Path**:
- Version embedded in JSON allows detection of schema changes
- Migration code will check `version` field and upgrade schema as needed
- Backward compatibility maintained (never break existing user data)

### File Permissions

**Linux/macOS**: `0o600` (user read/write only, no group/other access)
**Windows**: User-only read/write via file system ACLs

---

## Validation Rules

### Title Validation

```python
def validate_title(title: str) -> None:
    """Validate task title.

    Rules:
    - Not empty after stripping whitespace
    - 1-10 words (space-separated)

    Raises:
        TaskValidationError: If title is invalid
    """
    title = title.strip()

    if not title:
        raise TaskValidationError("Title cannot be empty (min 1 character required)")

    word_count = len(title.split())
    if word_count > 10:
        raise TaskValidationError(
            f"Title too long ({word_count} words, max 10 words allowed)"
        )
```

### Description Validation

```python
def validate_description(description: str) -> None:
    """Validate task description.

    Rules:
    - 0-500 characters
    - Empty string allowed (optional field)

    Raises:
        TaskValidationError: If description is invalid
    """
    if len(description) > 500:
        raise TaskValidationError(
            f"Description too long ({len(description)} chars, max 500 characters allowed)"
        )
```

### ID Validation

```python
import re

ID_PATTERN = re.compile(r"^[0-9a-f]{8}$")

def validate_id(task_id: str) -> None:
    """Validate task ID.

    Rules:
    - Exactly 8 characters
    - Lowercase hexadecimal (0-9, a-f)

    Raises:
        TaskValidationError: If ID is invalid
    """
    if not ID_PATTERN.match(task_id):
        raise TaskValidationError(
            f"Invalid ID format: '{task_id}' (must be 8 hex characters)"
        )
```

### Status Validation

```python
ALLOWED_STATUSES = {"pending", "completed"}

def validate_status(status: str) -> None:
    """Validate task status.

    Rules:
    - Must be "pending" or "completed"

    Raises:
        TaskValidationError: If status is invalid
    """
    if status not in ALLOWED_STATUSES:
        raise TaskValidationError(
            f"Invalid status: '{status}' (must be 'pending' or 'completed')"
        )
```

### Timestamp Validation

```python
from datetime import datetime

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

def validate_timestamp(timestamp: str) -> None:
    """Validate ISO 8601 timestamp.

    Rules:
    - Format: YYYY-MM-DD HH:MM:SS
    - Must be parseable as datetime

    Raises:
        TaskValidationError: If timestamp is invalid
    """
    try:
        datetime.strptime(timestamp, TIMESTAMP_FORMAT)
    except ValueError as e:
        raise TaskValidationError(
            f"Invalid timestamp format: '{timestamp}' (expected YYYY-MM-DD HH:MM:SS)"
        ) from e
```

---

## Indexing Strategy

### In-Memory Index

For efficient lookups during runtime, tasks are stored in a dictionary indexed by ID:

```python
from typing import Dict

# In-memory index for O(1) lookups
tasks_by_id: Dict[str, Task] = {
    task.id: task for task in loaded_tasks
}

# Lookup by ID (O(1))
task = tasks_by_id.get(task_id)

# Get all IDs (O(1) set creation)
existing_ids = set(tasks_by_id.keys())
```

### Filtering and Sorting

**Filter by Status** (O(n)):
```python
pending_tasks = [t for t in tasks if t.status == "pending"]
completed_tasks = [t for t in tasks if t.status == "completed"]
```

**Sort by Creation Date** (O(n log n)):
```python
sorted_tasks = sorted(
    tasks,
    key=lambda t: t.created_at,
    reverse=True  # Newest first
)
```

**Pagination** (O(1) after sort/filter):
```python
page_size = 10
page_num = 0  # Zero-indexed
start = page_num * page_size
end = start + page_size
page_tasks = sorted_tasks[start:end]
```

---

## Summary

### Key Design Decisions

1. **Simple Data Class**: Dataclass with validation in `__post_init__`
2. **String-Based Storage**: All fields stored as strings in JSON (no complex types)
3. **Explicit Validation**: Validators separated from model for reusability
4. **Atomic Operations**: State changes update `updated_at` automatically
5. **Schema Versioning**: Version field enables future migrations without data loss

### Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| 8-char UUID | Short display, good enough uniqueness | Theoretical collision risk (mitigated) |
| String timestamps | Simple JSON serialization | No timezone info (acceptable for local CLI) |
| In-memory index | Fast O(1) lookups | Memory usage (negligible for <10k tasks) |
| Separate validators | Reusable, testable | Slightly more code |
| Schema version | Future-proof migrations | Extra field in JSON |

All decisions align with constitution principles: simple, explicit, testable, type-safe.
