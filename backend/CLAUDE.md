# Claude Code Guidelines - CLI Todo Application

This file contains project-specific guidelines for Claude Code when working on this CLI Todo application.

## Project Overview

**CLI Todo Application** - A beautiful, interactive command-line task management application built with Python 3.13+, featuring full-width menus, colorful UI, and persistent JSON storage.

**Tech Stack:**
- Python 3.13+
- questionary (interactive prompts)
- rich (terminal formatting)
- pytest (testing)

**Architecture:**
- Clean layered architecture (CLI → Services → Storage)
- Interface-based design for testability
- Separation of concerns across modules

## Core Principles

### 1. Code Quality Standards

- **Type Hints:** All function signatures must include type hints
- **Docstrings:** All public functions and classes require docstrings
- **Line Length:** Maximum 100 characters (configured in pyproject.toml)
- **Naming:** Use descriptive names (no single-letter variables except in comprehensions)
- **Imports:** Organize imports (standard library → third-party → local)

### 2. Testing Requirements

- **Coverage:** Maintain existing test coverage (76+ passing tests)
- **Test Structure:** Follow AAA pattern (Arrange, Act, Assert)
- **Test Location:**
  - Unit tests: `tests/unit/`
  - Integration tests: `tests/integration/`
  - Contract tests: `tests/contract/`
- **Run Before Commit:** Always run `pytest` before committing changes

### 3. UI Consistency

All interactive prompts MUST use the full-width wrappers from `src/cli/utils/styles.py`:

```python
from src.cli.utils.styles import (
    select_fullwidth,      # For select menus
    checkbox_fullwidth,    # For checkboxes
    text_fullwidth,        # For text inputs
    confirm_fullwidth,     # For confirmations
)
```

**Do NOT use questionary directly** - always use the wrapper functions to maintain UI consistency.

### 4. Error Handling

- Use custom exceptions from `src/exceptions.py`
- Always provide user-friendly error messages
- Use `show_error()` for displaying errors to users
- Handle KeyboardInterrupt gracefully (let main app handle it)

Example:
```python
try:
    # operation
except TaskNotFoundError as e:
    show_error(f"❌ Task not found: {str(e)}")
except KeyboardInterrupt:
    raise  # Let main app handle
except Exception as e:
    show_error(f"Unexpected error: {str(e)}", exception=e)
```

## File Organization

### When Adding New Features

1. **Commands** (`src/cli/commands/`):
   - One file per command (e.g., `export.py` for export feature)
   - Follow existing command structure
   - Use full-width menu wrappers
   - Handle errors consistently

2. **Models** (`src/models/`):
   - Keep Task model focused and simple
   - Add new models only if needed
   - Include validation in model methods

3. **Services** (`src/services/`):
   - Business logic goes here, not in CLI layer
   - Follow interface pattern (interface.py + implementation)
   - Keep methods focused and testable

4. **Storage** (`src/storage/`):
   - Abstract storage operations
   - Support atomic writes
   - Maintain backup functionality

### When Modifying Existing Code

1. **Read Before Modifying:**
   - Always read the entire file before making changes
   - Understand existing patterns and conventions
   - Maintain consistency with existing code

2. **Preserve Functionality:**
   - Don't break existing tests
   - Run tests after changes
   - Update tests if behavior changes intentionally

3. **Respect Architecture:**
   - Don't add business logic to CLI layer
   - Don't access storage directly from commands
   - Use service layer as intermediary

## Specific Module Guidelines

### CLI Layer (`src/cli/`)

**Purpose:** User interaction and display only

**Rules:**
- No business logic calculations
- No direct storage access
- Use services for all operations
- Use formatters for all output
- Use full-width wrappers for all prompts

**Example:**
```python
# ✅ Good - delegates to service
def add_task_interactive(service: TaskService) -> None:
    title = text_fullwidth("Enter task title:")
    task = service.add_task(title=title)
    show_success("Task added!", task=task)

# ❌ Bad - contains business logic
def add_task_interactive(storage: Storage) -> None:
    title = input("Title: ")
    task_id = str(uuid.uuid4())[:8]  # Logic in CLI!
    task = Task(id=task_id, title=title, ...)
    storage.save(...)
```

### Service Layer (`src/services/`)

**Purpose:** Business logic and orchestration

**Rules:**
- Validate all inputs using `validators.py`
- Don't print or display messages
- Raise custom exceptions for errors
- Keep methods focused (single responsibility)
- Document complex logic

**Example:**
```python
def add_task(self, title: str, description: str = "") -> Task:
    """Add a new task with validation.

    Args:
        title: Task title (required)
        description: Optional task description

    Returns:
        Created Task object

    Raises:
        TaskValidationError: If validation fails
    """
    validate_title(title)
    validate_description(description)
    # ... implementation
```

### Storage Layer (`src/storage/`)

**Purpose:** Data persistence only

**Rules:**
- No business logic
- Use atomic writes
- Create backups before modifications
- Handle file I/O errors gracefully
- Keep storage format simple (JSON)

### Models (`src/models/`)

**Purpose:** Data structures and validation

**Rules:**
- Immutable where possible (use methods to create new instances)
- Include validation in constructors
- Provide `to_dict()` and `from_dict()` methods
- Keep models focused (single responsibility)

## UI/UX Guidelines

### Menu Design

1. **Use Emojis Consistently:**
   - 📝 for creation/input
   - 👀 for viewing
   - ✏️ for editing
   - ✅ for completion/confirmation
   - 🗑️ for deletion
   - 🚪 for exit
   - ← for back navigation

2. **Provide Back Options:**
   - Always include "← Back to main menu" or "← Cancel"
   - Place back option last in the list

3. **Confirm Destructive Actions:**
   - Always confirm deletions
   - Use ⚠️ emoji for warnings
   - Mention if action is irreversible

### Formatting

1. **Use Rich Formatters:**
   ```python
   from src.cli.display.formatters import (
       show_success,  # Green success messages
       show_error,    # Red error messages
       show_info,     # Blue info messages
       show_warning,  # Yellow warnings
   )
   ```

2. **Table Display:**
   - Use `create_task_table()` for task lists
   - Truncate long descriptions
   - Show status with icons (⏳ pending, ✅ completed)

3. **Spacing:**
   - Add blank lines before/after menus: `console.print()`
   - Let full-width wrappers handle borders

## Common Patterns

### Adding a New Command

1. Create file in `src/cli/commands/new_command.py`
2. Follow this template:

```python
"""New command description."""

from src.cli.display.formatters import show_error, show_success
from src.cli.utils.styles import select_fullwidth
from src.exceptions import TaskNotFoundError
from src.services.task_service import TaskService


def new_command_interactive(service: TaskService) -> None:
    """Interactive command description.

    Args:
        service: TaskService instance
    """
    try:
        # Show menu
        choice = select_fullwidth(
            "What would you like to do?",
            choices=["Option 1", "Option 2", "← Back to main menu"],
        )

        if choice is None or choice == "← Back to main menu":
            return

        # Perform operation
        result = service.some_operation()

        # Show result
        show_success("Operation successful!", task=result)

    except TaskNotFoundError as e:
        show_error(f"❌ Error: {str(e)}")
    except KeyboardInterrupt:
        raise
    except Exception as e:
        show_error(f"Unexpected error: {str(e)}", exception=e)
```

3. Add to main menu in `src/cli/app.py`
4. Write tests in `tests/unit/test_new_command.py`

### Adding a New Service Method

1. Add method to interface in `src/services/interface.py`
2. Implement in `src/services/task_service.py`
3. Follow this pattern:

```python
def new_method(self, param: str) -> Task:
    """Method description.

    Args:
        param: Parameter description

    Returns:
        Result description

    Raises:
        CustomException: When this happens
    """
    # Validate inputs
    validate_param(param)

    # Load data
    data = self.storage.load()

    # Business logic here
    result = self._process(data, param)

    # Save if needed
    self.storage.save(data)

    return result
```

4. Write tests covering happy path and error cases

## Testing Guidelines

### Unit Tests

- Test one unit of code in isolation
- Mock external dependencies
- Cover happy path and error cases
- Use descriptive test names: `test_add_task_generates_unique_id`

### Integration Tests

- Test multiple components together
- Use real storage (temp files)
- Verify end-to-end workflows
- Keep tests independent

### Contract Tests

- Verify interface implementations
- Test storage contract compliance
- Ensure backward compatibility

### Test Structure

```python
def test_descriptive_name(self):
    """Test description in plain English."""
    # Arrange
    service = TaskService(mock_storage)

    # Act
    result = service.add_task("Test task")

    # Assert
    assert result.title == "Test task"
    assert result.status == "pending"
```

## Common Mistakes to Avoid

### ❌ Don't Do This

```python
# 1. Using questionary directly
import questionary
choice = questionary.select("Menu", choices=[...]).ask()

# 2. Business logic in CLI
def add_task_interactive(service):
    if len(title) < 3:  # Validation in CLI!
        print("Error")

# 3. Printing in service layer
def add_task(self, title):
    print("Adding task...")  # No printing in services!

# 4. Direct storage access in commands
def view_tasks(storage):
    tasks = storage.load()["tasks"]  # Skip service layer!
```

### ✅ Do This Instead

```python
# 1. Use full-width wrappers
from src.cli.utils.styles import select_fullwidth
choice = select_fullwidth("Menu", choices=[...])

# 2. Delegate validation to service
def add_task_interactive(service):
    title = text_fullwidth("Title:")
    service.add_task(title)  # Let service validate

# 3. Return data, let CLI handle display
def add_task(self, title):
    validate_title(title)
    # ... logic ...
    return task

# 4. Always use service layer
def view_tasks_interactive(service):
    tasks = service.get_all_tasks()
```

## Performance Considerations

- **Pagination:** Always paginate large lists (default: 10 items)
- **File I/O:** Use atomic writes, create backups before modifications
- **Validation:** Validate early, fail fast
- **Caching:** Store loaded data in service instance when appropriate

## Security Considerations

- **Input Validation:** Validate all user inputs
- **File Paths:** Use pathlib, avoid shell injection
- **Errors:** Don't expose internal paths in error messages
- **Backups:** Create backups before destructive operations

## When to Ask for Clarification

Always ask the user before:
- Making breaking changes to the API
- Changing data storage format
- Modifying existing behavior significantly
- Adding new dependencies
- Removing features

## Resources

- **Project Specs:** `specs/001-cli-todo/`
- **Test Examples:** `tests/unit/` and `tests/integration/`
- **Code Contracts:** `specs/001-cli-todo/contracts/`
- **Data Model:** `specs/001-cli-todo/data-model.md`

## Quick Reference

### Run Tests
```bash
pytest                    # Run all tests
pytest -v                # Verbose output
pytest --cov=src         # With coverage
```

### Code Quality
```bash
black src tests          # Format code
ruff check src tests     # Lint code
mypy src                 # Type check
```

### Run Application
```bash
todo                     # Normal mode
todo --simple           # Simple mode
python -m src.main      # Direct execution
```

---

**Remember:** The goal is to maintain a clean, testable, and user-friendly codebase. When in doubt, follow existing patterns and ask for clarification.

## Active Technologies
- Neon PostgreSQL 16+ (serverless cloud database with automatic scaling) (002-project-setup)

## Recent Changes
- 002-project-setup: Added Neon PostgreSQL 16+ (serverless cloud database with automatic scaling)
