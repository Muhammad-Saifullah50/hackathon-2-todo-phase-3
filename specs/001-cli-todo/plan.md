# Implementation Plan: CLI Todo Application

**Branch**: `001-cli-todo` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cli-todo/spec.md`

## Summary

Build an interactive CLI todo application with beautiful terminal UI using Python 3.13+, questionary for interactive menus, and rich for formatted tables. The application follows strict TDD discipline with separation of concerns architecture (CLI/Business Logic/Data Persistence layers), supports full CRUD operations on tasks with status tracking (pending/completed), and provides comprehensive error handling with atomic JSON file storage.

**Key Features**: Add, view (filtered/paginated), update, delete, and mark tasks complete/incomplete with validation (1-10 word titles, 0-500 char descriptions), 8-character UUID generation, ISO 8601 timestamps, terminal width detection (80+ columns), file corruption recovery with backups, and graceful keyboard interrupt handling.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: questionary (interactive prompts), rich (terminal formatting), pytest (testing), pytest-cov (coverage), mypy (type checking), ruff (linting), black (formatting), uv (dependency management)
**Storage**: JSON file (`tasks.json` in project root) with atomic writes (temp file + rename), auto-creation if missing, backup before corruption reset
**Testing**: pytest with pytest-cov, TDD with RED-GREEN-REFACTOR cycle, 100% test pass rate required, minimum 80% code coverage (targeting 100%)
**Target Platform**: Linux/macOS/Windows desktop CLI environments with Python 3.13+, standard terminal emulator with ANSI color and UTF-8 support
**Project Type**: Single CLI application (not web/mobile) with modular architecture
**Performance Goals**: Add task < 10s, full workflow < 2min, table render < 1s for 1000 tasks, support thousands of tasks without degradation
**Constraints**: < 1s table rendering for 1000 tasks, 80+ column terminal width, atomic file operations (zero data loss), keyboard-only navigation, no mouse required
**Scale/Scope**: Single-user local storage, 1000+ task capacity, 5 core user stories, 38 functional requirements, 11 edge cases, Phase 1 MVP scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Architecture & Design - Separation of Concerns
- **Status**: PASS
- **Implementation**: Three-layer architecture planned:
  - **CLI Layer** (`src/cli/`): Command handlers, menu controllers, display formatters
  - **Business Logic Layer** (`src/services/`): Task operations, validation, filtering, pagination
  - **Data Persistence Layer** (`src/storage/`): JSON file I/O, atomic writes, backup/recovery
- **Contracts**: Python protocols for `StorageInterface`, `TaskService`, dependency injection throughout
- **Command Pattern**: Each CLI command (add, view, update, delete, mark complete) as independent, testable unit

### ✅ II. Code Quality - Explicit & Self-Documenting
- **Status**: PASS
- **Type Hints**: All functions, classes, methods use type hints; mypy strict mode enforced
- **Validation**: Input validation at system boundaries (CLI input, storage layer)
- **No Magic**: Explicit constants for limits (MAX_TITLE_WORDS=10, MAX_DESC_CHARS=500, MIN_TERMINAL_WIDTH=80)
- **DRY/YAGNI**: Extract validation, formatting, error handling utilities without premature abstraction

### ✅ III. Testing - Test-Driven Development (NON-NEGOTIABLE)
- **Status**: PASS
- **TDD Discipline**: RED-GREEN-REFACTOR cycle mandatory, tests written before implementation
- **Coverage**: 100% test pass rate required, targeting 100% code coverage (minimum 80%)
- **Test Pyramid**: Unit tests (models, validators, storage, services), integration tests (full workflows), contract tests (layer boundaries)
- **Independence**: All tests independent, no shared state, mocked file I/O for unit tests
- **Acceptance**: Each functional requirement maps to testable acceptance criteria

### ✅ IV. Data Management - Single Source of Truth
- **Status**: PASS
- **Storage**: Single `tasks.json` file in project root, atomic writes (write to temp + rename)
- **Schema Version**: v1.0.0 embedded in JSON, plan for future evolution with migration support
- **Atomicity**: All read-modify-write operations use atomic file operations
- **Validation**: Input validation at CLI layer, schema validation at storage layer
- **Backwards Compatibility**: Schema versioning planned for future migrations without data loss

### ✅ V. Error Handling - Clear & User-Friendly
- **Status**: PASS
- **Custom Exceptions**: `TaskValidationError`, `StorageError`, `TaskNotFoundError`, `FilePermissionError`, `FileCorruptionError`
- **User Messages**: All errors show actionable guidance (what went wrong, how to fix), no stack traces in production
- **Graceful Degradation**: File corruption → backup + reset, missing file → auto-create, permission error → exit with clear message
- **Logging**: Structured logging (DEBUG for development, ERROR for production) with full context, separate from user output

### ✅ VI. User Experience - Beautiful & Intuitive CLI (NON-NEGOTIABLE)
- **Status**: PASS
- **Visual Hierarchy**: rich tables for task lists, panels for success/error messages, consistent color scheme (green=success/complete, yellow=pending, red=error, blue=prompts)
- **Interactive Menus**: questionary.select() for navigation, questionary.text() for input, questionary.checkbox() for multi-select, questionary.confirm() for dangerous operations
- **Immediate Feedback**: Every action shows confirmation with appropriate visual treatment
- **Accessibility**: --simple flag for plain text output (no colors, no formatting) for screen readers and scripting
- **Empty States**: Beautiful messages when no tasks exist, not blank output

### ✅ VII. Performance & Scalability - Efficient by Design
- **Status**: PASS
- **Scale Target**: Handle 1000+ tasks efficiently, table rendering < 1s for 1000 tasks
- **Lazy Loading**: Pagination (10 tasks/page) reduces rendering overhead
- **Efficient Lookups**: Task dictionary indexed by ID for O(1) lookups during updates/deletes
- **Pluggable Storage**: Storage layer uses protocol interface, allows future swap to SQLite/database without business logic changes
- **No Premature Optimization**: Profile hot paths only after basic implementation works

### ✅ VIII. Security & Safety - Secure by Default
- **Status**: PASS
- **Input Validation**: All user input validated (title word count, description length, empty checks)
- **File Permissions**: Set user-only read/write (600) on tasks.json, check permissions on startup
- **Path Safety**: No user-provided paths, fixed location (project root), prevent traversal attacks
- **Safe Defaults**: Delete/exit require confirmation, update allows cancel on empty input
- **No Secrets**: No hardcoded paths, credentials, or sensitive data in code

### ✅ IX. Python Standards - Modern & Professional
- **Status**: PASS
- **Python Version**: 3.13+ with modern features (pattern matching for menu routing, improved type hints, PEP 695 type aliases)
- **Tooling**: uv (dependency management), ruff (linting), black (formatting), mypy strict (type checking), pytest + pytest-cov (testing)
- **Standards**: PEP 8 compliance enforced, conventional commits (feat:, fix:, docs:, test:, refactor:)
- **Pre-commit Gates**: All commits pass ruff, black, mypy, pytest before merge

### ✅ X. Development Workflow - Spec-Driven & Systematic
- **Status**: PASS
- **Process**: Spec → Plan (this doc) → Tasks → RED-GREEN-REFACTOR implementation
- **Commits**: Small, atomic commits with conventional commit messages
- **Documentation**: PHRs for user interactions, ADRs for architectural decisions (e.g., JSON vs SQLite storage choice)
- **Traceability**: Each task links to functional requirements, each test links to acceptance criteria

### Summary
**All constitution gates: PASS** ✅ No complexity violations to justify. Architecture follows all 10 core principles without exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-todo/
├── spec.md              # Feature specification (✅ complete)
├── plan.md              # This file (✅ complete)
├── research.md          # Phase 0 output (see below)
├── data-model.md        # Phase 1 output (see below)
├── quickstart.md        # Phase 1 output (see below)
├── contracts/           # Phase 1 output (see below)
│   ├── storage_interface.py
│   ├── task_service_interface.py
│   └── validators.py
├── checklists/
│   └── requirements.md  # Spec quality checklist (✅ complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
# Single project structure (CLI application)
src/
├── __init__.py
├── main.py              # Entry point: python src/main.py
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass with validation
├── storage/
│   ├── __init__.py
│   ├── interface.py     # StorageInterface protocol
│   └── json_storage.py  # JSON file storage implementation
├── services/
│   ├── __init__.py
│   ├── interface.py     # TaskServiceInterface protocol
│   ├── task_service.py  # Business logic: CRUD, filtering, pagination
│   └── validators.py    # Input validation utilities
├── cli/
│   ├── __init__.py
│   ├── app.py           # Main CLI controller
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── add.py       # Add task command
│   │   ├── view.py      # View/filter/paginate tasks command
│   │   ├── update.py    # Update task command
│   │   ├── delete.py    # Delete task(s) command
│   │   └── complete.py  # Mark complete/incomplete command
│   ├── display/
│   │   ├── __init__.py
│   │   ├── formatters.py # Rich table/panel formatters
│   │   └── messages.py   # Success/error message constants
│   └── utils/
│       ├── __init__.py
│       ├── terminal.py   # Terminal width detection
│       └── interrupts.py # Keyboard interrupt handling
└── exceptions.py        # Custom exception classes

tests/
├── __init__.py
├── conftest.py          # Pytest fixtures (mock storage, sample tasks)
├── unit/
│   ├── __init__.py
│   ├── test_task_model.py
│   ├── test_validators.py
│   ├── test_json_storage.py
│   ├── test_task_service.py
│   └── test_formatters.py
├── integration/
│   ├── __init__.py
│   ├── test_add_workflow.py
│   ├── test_view_workflow.py
│   ├── test_update_workflow.py
│   ├── test_delete_workflow.py
│   └── test_complete_workflow.py
└── contract/
    ├── __init__.py
    ├── test_storage_contract.py
    └── test_service_contract.py

# Root files
pyproject.toml           # uv project configuration, dependencies, tool configs
requirements.txt         # Generated by uv (for compatibility)
.python-version          # Python 3.13
mypy.ini                 # Mypy strict mode configuration
.ruff.toml               # Ruff linting configuration
tasks.json               # Runtime data file (gitignored, created on first run)
tasks.json.backup        # Backup file (gitignored, created on corruption)
```

**Structure Decision**: Single project structure selected because this is a standalone CLI application with no web frontend, mobile app, or separate API service. The three-layer architecture (CLI/Services/Storage) is implemented via separate packages within a single `src/` directory. This provides clear separation of concerns while maintaining simplicity for a single-binary CLI tool.

## Complexity Tracking

> No violations - all constitution gates pass without exceptions.

---

## Phase 0: Research

### Research Topics

1. **UUID Generation in Python 3.13**: Best practices for generating short, collision-resistant identifiers
2. **Atomic File Operations**: Pattern for atomic writes (temp + rename) on Linux/macOS/Windows
3. **Rich Library Best Practices**: Table formatting, panel styling, color schemes for terminal UIs
4. **Questionary Patterns**: Menu navigation, input validation, checkbox multi-select, error handling
5. **Pytest Fixtures for File I/O**: Mock patterns for JSON storage, temporary file fixtures
6. **mypy Strict Mode**: Configuration for protocols, type guards, no implicit Any
7. **uv Project Setup**: pyproject.toml structure, dependency management, virtual environment workflow

### Research Findings

See [research.md](./research.md) for detailed findings with decisions, rationales, and alternatives considered.

---

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions, field specifications, validation rules, state transitions, and JSON schema.

### API Contracts

See [contracts/](./contracts/) directory for:
- `storage_interface.py`: StorageInterface protocol (load, save, create_backup)
- `task_service_interface.py`: TaskServiceInterface protocol (add, update, delete, mark_complete, filter, paginate)
- `validators.py`: Input validation contracts (validate_title, validate_description, validate_uuid)

### Quickstart Guide

See [quickstart.md](./quickstart.md) for:
- Installation instructions (uv setup, dependencies)
- Running the application (`python src/main.py`)
- Running tests (`pytest --cov=src tests/`)
- Development workflow (TDD cycle, pre-commit checks)

---

## Architecture Decisions

### ADR-001: JSON File Storage for Phase 1

**Context**: Need persistent storage for tasks with requirements for atomic writes, backup/recovery, and future database migration path.

**Decision**: Use JSON file storage (`tasks.json` in project root) with atomic write pattern (temp file + rename).

**Rationale**:
- **Simplicity**: No database setup, no migrations, easy debugging (human-readable)
- **Atomic Writes**: OS-level rename operation is atomic on POSIX systems
- **Backup/Recovery**: Easy to backup (copy file), easy to inspect (cat tasks.json)
- **Future Migration**: Storage layer uses protocol interface, swap to SQLite later without business logic changes

**Alternatives Considered**:
- **SQLite**: More robust, but overkill for single-user CLI, adds complexity
- **pickle**: Not human-readable, not version-control friendly, security risks
- **YAML**: Slower parsing, more dependencies, JSON is Python stdlib

**Consequences**:
- ✅ Fast implementation, easy testing, no external dependencies
- ✅ Human-readable for debugging
- ⚠️ Concurrent access not handled (documented limitation)
- ⚠️ Large datasets (10k+ tasks) may have performance issues (acceptable for Phase 1)

### ADR-002: 8-Character UUID Slicing

**Context**: UUIDs are 32 hex characters (128 bits), but spec requires 8-character IDs for display brevity.

**Decision**: Generate full UUID4, take first 8 characters, regenerate on collision.

**Rationale**:
- **Collision Probability**: With 8 hex chars (32 bits), collision probability is ~1 in 4 billion. For <10k tasks, probability < 0.01%.
- **Regeneration Strategy**: If collision detected (ID exists), regenerate until unique (expected iterations: ~1)
- **Simplicity**: No custom ID generation logic, leverage stdlib `uuid.uuid4()`

**Alternatives Considered**:
- **Full UUID Storage**: 32 chars too long for terminal display
- **Sequential IDs**: Not universally unique, collision risk with concurrent instances
- **Base62 Encoding**: More complex, 8 chars still provides 62^8 = 218 trillion combinations (overkill)

**Consequences**:
- ✅ Simple implementation using stdlib
- ✅ Collision risk negligible for expected scale
- ⚠️ Theoretical collision risk (mitigated by regeneration)

### ADR-003: Three-Layer Architecture with Protocols

**Context**: Constitution requires separation of concerns, testability, and pluggable storage.

**Decision**: Three layers (CLI/Services/Storage) with Python protocols for interfaces.

**Rationale**:
- **Testability**: Each layer testable in isolation with mocked dependencies
- **Flexibility**: Storage layer replaceable (JSON → SQLite) without changing business logic
- **Type Safety**: Protocols provide compile-time type checking via mypy
- **Dependency Injection**: No global state, all dependencies passed explicitly

**Alternatives Considered**:
- **Two-Layer** (CLI + Storage): Business logic would leak into CLI, harder to test
- **Abstract Base Classes**: Protocols are more Pythonic (structural subtyping), lighter weight
- **Monolithic**: Violates constitution, untestable, inflexible

**Consequences**:
- ✅ Clear boundaries, easy to test, future-proof
- ✅ Aligns with constitution principles
- ⚠️ Slightly more initial boilerplate (acceptable tradeoff)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Run research tasks and consolidate findings
2. ✅ **Phase 1 Complete**: Generate data-model.md, contracts/, quickstart.md
3. **Phase 2 (Next Command)**: Run `/sp.tasks` to generate tasks.md with testable, dependency-ordered implementation tasks
4. **Implementation**: Follow TDD cycle (RED-GREEN-REFACTOR) for each task
5. **Validation**: All tests pass, all quality gates pass before merge

**Command to proceed**: `/sp.tasks`
