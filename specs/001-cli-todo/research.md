# Research Findings: CLI Todo Application

**Date**: 2025-12-18
**Phase**: 0 (Research)
**Status**: Complete

## Overview

This document consolidates research findings for technical decisions in the CLI Todo Application implementation. Each section presents the decision made, rationale, and alternatives considered.

---

## 1. UUID Generation in Python 3.13

### Decision
Use `uuid.uuid4().hex[:8]` to generate 8-character hexadecimal identifiers with collision detection and regeneration.

### Rationale
- **Standard Library**: `uuid` module is Python stdlib, no external dependencies
- **Collision Probability**: 8 hex characters = 32 bits = 4.3 billion combinations. For <10k tasks, collision probability < 0.01%
- **Simplicity**: Single line of code, no custom logic required
- **Regeneration Pattern**: `while id in existing_ids: id = uuid.uuid4().hex[:8]` ensures uniqueness with expected O(1) iterations

### Implementation Pattern
```python
import uuid
from typing import Set

def generate_unique_id(existing_ids: Set[str]) -> str:
    """Generate unique 8-character hexadecimal ID."""
    task_id = uuid.uuid4().hex[:8]
    while task_id in existing_ids:
        task_id = uuid.uuid4().hex[:8]
    return task_id
```

### Alternatives Considered
- **Sequential IDs (1, 2, 3, ...)**: Not unique across instances, collision risk
- **Full UUID (32 chars)**: Too long for terminal display
- **shortuuid library**: External dependency, overkill for simple use case
- **Base62 encoding**: More complex, 8 chars provides 62^8 = 218 trillion combinations (unnecessary)

### References
- Python uuid docs: https://docs.python.org/3/library/uuid.html
- UUID collision probability calculator: https://zelark.github.io/nano-id-cc/

---

## 2. Atomic File Operations

### Decision
Use "write to temp file + atomic rename" pattern for all JSON file writes.

### Rationale
- **Atomicity**: OS-level `os.replace()` is atomic on POSIX systems (Linux/macOS) and Windows
- **Corruption Prevention**: If write fails mid-operation, original file remains intact
- **Standard Pattern**: Used by git, systemd, and other production systems
- **Python 3.13 Support**: `os.replace()` available in stdlib, works cross-platform

### Implementation Pattern
```python
import os
import json
import tempfile
from pathlib import Path

def atomic_write_json(file_path: Path, data: dict) -> None:
    """Atomically write JSON data to file."""
    # Write to temporary file in same directory (same filesystem for atomic rename)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        suffix=".tmp"
    )

    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())  # Ensure data written to disk

        # Atomic rename (replaces existing file if present)
        os.replace(temp_path, file_path)

        # Set file permissions (user read/write only)
        os.chmod(file_path, 0o600)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
```

### Alternatives Considered
- **Direct write**: Risk of corruption if process crashes mid-write
- **File locking (fcntl)**: Doesn't prevent corruption, only prevents concurrent access (not needed for single-user CLI)
- **Write-Ahead Log (WAL)**: Overkill for simple JSON storage, adds complexity
- **SQLite**: More robust but heavier, planned for future migration

### References
- Python tempfile docs: https://docs.python.org/3/library/tempfile.html
- Atomic file operations: https://danluu.com/file-consistency/

---

## 3. Rich Library Best Practices

### Decision
Use rich `Table` for task lists, `Panel` for messages, `Console` with custom theme for consistent styling.

### Rationale
- **Table**: Built-in column formatting, truncation, alignment, borders
- **Panel**: Boxes for success/error messages with title and border styling
- **Theme**: Centralized color scheme (green=success, yellow=warning, red=error, blue=info)
- **Performance**: rich is optimized for terminal rendering, handles ANSI escapes efficiently

### Implementation Pattern
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.theme import Theme

# Custom theme for consistent colors
custom_theme = Theme({
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "bold blue",
    "pending": "yellow",
    "completed": "green",
})

console = Console(theme=custom_theme)

# Task table
def create_task_table(tasks: list[Task]) -> Table:
    table = Table(
        title="Tasks",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("ID", style="dim", width=8)
    table.add_column("Status", width=8)
    table.add_column("Title", no_wrap=False)
    table.add_column("Description", no_wrap=False, overflow="ellipsis")
    table.add_column("Created", style="dim")

    for task in tasks:
        status_icon = "✓" if task.status == "completed" else "✗"
        status_style = "completed" if task.status == "completed" else "pending"
        table.add_row(
            task.id,
            f"[{status_style}]{status_icon}[/]",
            task.title,
            task.description or "—",
            task.created_at.split()[0],  # Date only
        )
    return table

# Success/error panels
def show_success(message: str) -> None:
    console.print(Panel(message, title="✓ Success", style="success"))

def show_error(message: str) -> None:
    console.print(Panel(message, title="✗ Error", style="error"))
```

### Alternatives Considered
- **tabulate**: Simpler but less feature-rich, no color theming
- **terminaltables**: Deprecated, not actively maintained
- **Manual ANSI codes**: Error-prone, hard to maintain
- **curses**: Too low-level, complex for simple tables

### References
- rich documentation: https://rich.readthedocs.io/
- rich examples: https://github.com/Textualize/rich/tree/master/examples

---

## 4. Questionary Patterns

### Decision
Use questionary for all interactive inputs: `select()` for menus, `text()` for input, `checkbox()` for multi-select, `confirm()` for dangerous operations.

### Rationale
- **Keyboard Navigation**: Arrow keys, Enter, Esc supported out-of-box
- **Validation**: Built-in validation with custom validators
- **Styling**: Integrates with rich for consistent theming
- **Error Handling**: Returns `None` on Ctrl+C, easy to handle gracefully

### Implementation Pattern
```python
import questionary
from questionary import ValidationError, Validator

# Custom validator
class TitleValidator(Validator):
    def validate(self, document):
        words = document.text.strip().split()
        if len(words) == 0:
            raise ValidationError(
                message="Title cannot be empty",
                cursor_position=len(document.text),
            )
        if len(words) > 10:
            raise ValidationError(
                message=f"Title too long ({len(words)} words, max 10)",
                cursor_position=len(document.text),
            )

# Menu selection
def show_main_menu() -> str | None:
    return questionary.select(
        "What would you like to do?",
        choices=[
            "Add new task",
            "View tasks",
            "Update task",
            "Delete task",
            "Mark task as complete/incomplete",
            "Exit",
        ],
    ).ask()

# Text input with validation
def prompt_title() -> str | None:
    return questionary.text(
        "Enter task title (1-10 words):",
        validate=TitleValidator,
    ).ask()

# Multi-select checkbox
def select_tasks_to_delete(tasks: list[Task]) -> list[str] | None:
    choices = [
        questionary.Choice(
            title=f"[{'✓' if t.status == 'completed' else '✗'}] {t.title}",
            value=t.id,
        )
        for t in tasks
    ]
    return questionary.checkbox(
        "Select tasks to delete (Space to select, Enter to confirm):",
        choices=choices,
    ).ask()

# Confirmation
def confirm_delete(count: int) -> bool | None:
    return questionary.confirm(
        f"Delete {count} selected task{'s' if count > 1 else ''}?",
        default=False,
    ).ask()
```

### Alternatives Considered
- **click prompts**: Less interactive, no arrow key navigation
- **inquirer**: Similar but less actively maintained
- **prompt_toolkit**: Lower level, more complex
- **raw input()**: No validation, no keyboard navigation

### References
- questionary docs: https://questionary.readthedocs.io/
- questionary examples: https://github.com/tmbo/questionary/tree/master/examples

---

## 5. Pytest Fixtures for File I/O

### Decision
Use pytest fixtures with `tmp_path` for isolated file tests, `unittest.mock` for mocking storage layer in service tests.

### Rationale
- **Isolation**: Each test gets fresh temporary directory via `tmp_path` fixture
- **No Cleanup**: pytest automatically cleans up temp directories
- **Mock Patterns**: `unittest.mock.Mock` with `spec` ensures type safety
- **Fixture Composition**: Fixtures can depend on other fixtures for DRY test setup

### Implementation Pattern
```python
import pytest
from pathlib import Path
from unittest.mock import Mock
from src.storage.json_storage import JSONStorage
from src.models.task import Task

# Fixture: Temporary storage file
@pytest.fixture
def storage_file(tmp_path: Path) -> Path:
    return tmp_path / "test_tasks.json"

# Fixture: Real storage instance for integration tests
@pytest.fixture
def json_storage(storage_file: Path) -> JSONStorage:
    return JSONStorage(storage_file)

# Fixture: Mock storage for unit tests
@pytest.fixture
def mock_storage() -> Mock:
    storage = Mock(spec=StorageInterface)
    storage.load.return_value = {"tasks": [], "version": "1.0.0"}
    storage.save.return_value = None
    return storage

# Fixture: Sample tasks
@pytest.fixture
def sample_tasks() -> list[Task]:
    return [
        Task(
            id="abc123de",
            title="Buy groceries",
            description="Milk, eggs, bread",
            status="pending",
            created_at="2025-12-18 10:00:00",
            updated_at="2025-12-18 10:00:00",
        ),
        Task(
            id="def456gh",
            title="Write tests",
            description="",
            status="completed",
            created_at="2025-12-18 09:00:00",
            updated_at="2025-12-18 11:00:00",
        ),
    ]

# Usage in test
def test_add_task(json_storage, storage_file):
    task = Task(id="test1234", title="Test task", ...)
    json_storage.save({"tasks": [task.to_dict()], "version": "1.0.0"})

    # Verify file exists and contains task
    assert storage_file.exists()
    data = json.loads(storage_file.read_text())
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Test task"
```

### Alternatives Considered
- **Manual temp file creation**: Error-prone, manual cleanup required
- **monkeypatch**: Works but less explicit than fixtures
- **pytest-mock plugin**: Adds dependency, unittest.mock sufficient
- **Real files in tests/**: Slow, risk of side effects between tests

### References
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- pytest tmp_path: https://docs.pytest.org/en/stable/tmpdir.html
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html

---

## 6. mypy Strict Mode Configuration

### Decision
Enable mypy strict mode with explicit protocol support, no implicit `Any`, and strict optional checking.

### Rationale
- **Early Error Detection**: Catches type errors at development time, not runtime
- **Protocol Support**: `--enable-incomplete-feature=Protocols` for structural subtyping
- **No Implicit Any**: Forces explicit typing, prevents silent type holes
- **Strict Optional**: Catches None-handling bugs early

### Implementation (mypy.ini)
```ini
[mypy]
python_version = 3.13
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
disallow_incomplete_defs = True

# Protocol support
enable_incomplete_feature = Protocols

# Ignore missing imports for third-party libraries without stubs
[mypy-questionary.*]
ignore_missing_imports = True

[mypy-rich.*]
ignore_missing_imports = True
```

### Key Settings Explained
- `strict = True`: Enables all strict checks
- `disallow_untyped_defs`: Functions must have type hints
- `disallow_any_unimported`: Can't use untyped imports
- `no_implicit_optional`: `x: str = None` is error (must be `x: str | None`)
- `enable_incomplete_feature = Protocols`: Structural subtyping for protocols

### Alternatives Considered
- **Non-strict mode**: Misses many type errors, defeats purpose of mypy
- **pyright**: Good alternative, but mypy is industry standard for Python
- **Pyre**: Facebook's type checker, less adoption than mypy
- **Gradual typing**: Start loose and tighten - violates constitution (strict from day 1)

### References
- mypy configuration: https://mypy.readthedocs.io/en/stable/config_file.html
- mypy strict mode: https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict

---

## 7. uv Project Setup

### Decision
Use `uv` for dependency management with `pyproject.toml` for project config and tool configurations.

### Rationale
- **Speed**: 10-100x faster than pip, uses Rust-based resolver
- **Reproducibility**: Lock file (`uv.lock`) ensures consistent installs
- **Modern**: Follows PEP 621 (pyproject.toml standard)
- **Tool Config**: Single file for black, ruff, pytest, mypy configs
- **Virtual Env**: `uv venv` creates isolated environments fast

### Implementation (pyproject.toml)
```toml
[project]
name = "cli-todo"
version = "0.1.0"
description = "Interactive CLI Todo Application"
requires-python = ">=3.13"
dependencies = [
    "questionary>=2.0.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
    "black>=23.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 100
target-version = ["py313"]

[tool.ruff]
line-length = 100
target-version = "py313"
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--cov=src --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "**/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### Workflow Commands
```bash
# Setup (one-time)
uv venv                        # Create virtual environment
source .venv/bin/activate      # Activate (or .venv\Scripts\activate on Windows)
uv pip install -e ".[dev]"     # Install project + dev dependencies

# Development
uv pip install <package>       # Add runtime dependency
uv pip install --dev <package> # Add dev dependency
uv pip compile pyproject.toml  # Generate requirements.txt

# Quality checks
ruff check .                   # Lint
black --check .                # Format check
mypy .                         # Type check
pytest --cov=src tests/        # Test with coverage
```

### Alternatives Considered
- **pip + requirements.txt**: Slower, no lock file, less reproducible
- **poetry**: Heavier, slower resolver, more complex
- **pipenv**: Slower, less active development
- **conda**: Overkill for pure Python project, slow

### References
- uv documentation: https://github.com/astral-sh/uv
- PEP 621 (pyproject.toml): https://peps.python.org/pep-0621/
- uv examples: https://github.com/astral-sh/uv/tree/main/examples

---

## Summary

All research topics resolved with concrete implementation patterns. Key decisions:

1. **UUID**: `uuid.uuid4().hex[:8]` with collision detection
2. **Atomic Writes**: Temp file + `os.replace()` pattern
3. **Rich**: Tables, Panels, custom theme for consistent UI
4. **Questionary**: Select, text, checkbox, confirm for all interactions
5. **Pytest**: Fixtures with `tmp_path`, mocks with `spec`
6. **mypy**: Strict mode with protocol support enabled
7. **uv**: Fast, modern dependency management with pyproject.toml

All patterns align with constitution principles: explicit, testable, type-safe, following Python 3.13 best practices.
