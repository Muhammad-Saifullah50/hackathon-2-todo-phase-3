# Quickstart Guide: CLI Todo Application

**Date**: 2025-12-18
**Phase**: 1 (Design)
**Status**: Complete

## Overview

This guide provides step-by-step instructions for setting up the development environment, running the application, executing tests, and following the TDD workflow.

---

## Prerequisites

- **Python 3.13+** installed and available in PATH
- **Git** for version control
- **Terminal emulator** supporting ANSI colors and UTF-8 encoding (80+ column width recommended)
- **uv** package manager (installation instructions below)

---

## Installation

### 1. Install uv Package Manager

**Linux/macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```bash
uv --version
```

### 2. Clone Repository and Switch to Feature Branch

```bash
# Clone repository (replace with actual repo URL)
git clone <repo-url>
cd hackathon-2-todo-phase-1

# Switch to feature branch
git checkout 001-cli-todo
```

### 3. Create Virtual Environment

```bash
# Create virtual environment in .venv/
uv venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

You should see `(.venv)` prefix in your shell prompt.

### 4. Install Dependencies

```bash
# Install project dependencies + development tools
uv pip install -e ".[dev]"
```

This installs:
- **Runtime**: questionary, rich
- **Development**: pytest, pytest-cov, mypy, ruff, black

### 5. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.13+

# Check installed packages
uv pip list
```

---

## Running the Application

### First Run

```bash
# Run from project root
python src/main.py
```

On first run:
- `tasks.json` file is auto-created in project root
- Empty state message displayed
- Main menu appears

### Normal Usage

The application uses interactive menus:
1. Navigate with arrow keys (↑/↓)
2. Select with Enter
3. Cancel/back with Esc
4. Exit with Ctrl+C (graceful goodbye message)

### Command-Line Flags

```bash
# Simple mode (no colors, plain text)
python src/main.py --simple

# Help
python src/main.py --help
```

---

## Running Tests

### Run All Tests

```bash
# Run full test suite with coverage
pytest --cov=src tests/
```

Output shows:
- Test results (pass/fail)
- Coverage percentage
- Coverage report

### Run Specific Test Files

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Single test file
pytest tests/unit/test_task_model.py

# Single test function
pytest tests/unit/test_task_model.py::test_task_creation
```

### Run Tests in Watch Mode

```bash
# Install pytest-watch (optional)
uv pip install pytest-watch

# Run tests on file changes
ptw -- --cov=src tests/
```

### Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/

# Open report in browser
# Linux:
xdg-open htmlcov/index.html

# macOS:
open htmlcov/index.html

# Windows:
start htmlcov/index.html
```

---

## Development Workflow (TDD)

### Step 1: Write Test FIRST (RED)

Before writing any implementation code, write a failing test:

```python
# tests/unit/test_task_service.py
def test_add_task_creates_task_with_valid_title(mock_storage):
    service = TaskService(mock_storage)

    task = service.add_task(title="Buy groceries", description="Milk, eggs")

    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs"
    assert task.status == "pending"
    assert len(task.id) == 8
```

Run test to verify it **fails**:
```bash
pytest tests/unit/test_task_service.py::test_add_task_creates_task_with_valid_title
```

Expected output: `FAILED` (because implementation doesn't exist yet)

### Step 2: Write Minimal Code (GREEN)

Write just enough code to make the test pass:

```python
# src/services/task_service.py
def add_task(self, title: str, description: str = "") -> Task:
    task_id = self._generate_unique_id()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    task = Task(
        id=task_id,
        title=title,
        description=description,
        status="pending",
        created_at=now,
        updated_at=now,
    )

    self._save_task(task)
    return task
```

Run test again:
```bash
pytest tests/unit/test_task_service.py::test_add_task_creates_task_with_valid_title
```

Expected output: `PASSED` ✅

### Step 3: Refactor (while keeping tests GREEN)

Clean up code without changing behavior:

```python
# Extract timestamp generation to helper
def _current_timestamp(self) -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_task(self, title: str, description: str = "") -> Task:
    task = Task(
        id=self._generate_unique_id(),
        title=title,
        description=description,
        status="pending",
        created_at=self._current_timestamp(),
        updated_at=self._current_timestamp(),
    )

    self._save_task(task)
    return task
```

Run tests to verify refactor didn't break anything:
```bash
pytest tests/unit/test_task_service.py
```

All tests should still **PASS** ✅

### Repeat RED-GREEN-REFACTOR

Continue this cycle for each feature:
1. Write failing test (RED)
2. Make it pass (GREEN)
3. Clean up code (REFACTOR)
4. Commit when feature is complete

---

## Quality Checks (Pre-Commit)

Before committing code, run all quality checks:

### 1. Linting

```bash
# Check for linting errors
ruff check .

# Auto-fix linting errors
ruff check --fix .
```

### 2. Formatting

```bash
# Check if code is formatted
black --check .

# Auto-format code
black .
```

### 3. Type Checking

```bash
# Run mypy strict mode
mypy .
```

### 4. Tests

```bash
# Run full test suite
pytest --cov=src tests/
```

### All-in-One Pre-Commit Script

Create a script to run all checks:

```bash
#!/bin/bash
# scripts/pre-commit.sh

set -e  # Exit on first error

echo "Running quality checks..."

echo "1. Linting (ruff)..."
ruff check .

echo "2. Formatting (black)..."
black --check .

echo "3. Type checking (mypy)..."
mypy .

echo "4. Tests (pytest)..."
pytest --cov=src tests/

echo "✅ All checks passed!"
```

Make it executable:
```bash
chmod +x scripts/pre-commit.sh
```

Run before commit:
```bash
./scripts/pre-commit.sh
```

---

## Common Tasks

### Add a New Dependency

```bash
# Add runtime dependency
uv pip install <package-name>

# Update pyproject.toml manually:
# [project]
# dependencies = [
#     "questionary>=2.0.0",
#     "rich>=13.7.0",
#     "new-package>=1.0.0",  # <-- Add here
# ]

# Regenerate requirements.txt
uv pip compile pyproject.toml --output-file requirements.txt
```

### Add a New Development Tool

```bash
# Add dev dependency
uv pip install --dev <package-name>

# Update pyproject.toml manually:
# [project.optional-dependencies]
# dev = [
#     "pytest>=7.4.0",
#     "new-tool>=1.0.0",  # <-- Add here
# ]
```

### Update All Dependencies

```bash
# Update all packages to latest versions
uv pip install --upgrade -e ".[dev]"
```

### View Test Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing tests/

# See which lines are not covered
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

### Debug Failing Tests

```bash
# Run with verbose output
pytest -v tests/

# Run with print statements visible
pytest -s tests/

# Stop on first failure
pytest -x tests/

# Enter debugger on failure (requires pdb++)
pytest --pdb tests/
```

### Clean Build Artifacts

```bash
# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove coverage files
rm -rf .coverage htmlcov/

# Remove virtual environment
rm -rf .venv/
```

---

## Project Structure Quick Reference

```
hackathon-2-todo-phase-1/
├── src/                    # Source code
│   ├── models/            # Data models (Task)
│   ├── storage/           # Persistence layer (JSON)
│   ├── services/          # Business logic layer
│   ├── cli/               # CLI interface layer
│   ├── exceptions.py      # Custom exceptions
│   └── main.py            # Entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── contract/         # Contract tests
│   └── conftest.py       # Pytest fixtures
├── specs/001-cli-todo/   # Feature documentation
│   ├── spec.md           # Requirements
│   ├── plan.md           # Architecture
│   ├── data-model.md     # Data design
│   ├── research.md       # Tech decisions
│   ├── contracts/        # Interface specs
│   └── quickstart.md     # This file
├── pyproject.toml        # Project config
├── mypy.ini              # Type checking config
├── .ruff.toml            # Linting config
└── tasks.json            # Runtime data (gitignored)
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
uv pip install -e ".[dev]"
```

### "Permission denied" on tasks.json

```bash
# Check file permissions
ls -la tasks.json

# Fix permissions (user read/write only)
chmod 600 tasks.json
```

### Tests fail with "fixture not found"

```bash
# Ensure conftest.py exists in tests/
ls tests/conftest.py

# Check fixture is defined correctly
cat tests/conftest.py
```

### Type checking fails

```bash
# Check mypy.ini configuration
cat mypy.ini

# Run mypy with verbose output
mypy --verbose .
```

### Terminal too narrow warning

```bash
# Resize terminal to at least 80 columns
# Check current width
tput cols

# Or use simple mode
python src/main.py --simple
```

---

## Next Steps

1. Read [spec.md](./spec.md) for full requirements
2. Read [plan.md](./plan.md) for architecture overview
3. Read [data-model.md](./data-model.md) for data structures
4. Review [contracts/](./contracts/) for interface specifications
5. Start implementing following TDD workflow (RED-GREEN-REFACTOR)

---

## Getting Help

- **Constitution**: See `.specify/memory/constitution.md` for project principles
- **Templates**: See `.specify/templates/` for spec/plan/task templates
- **Slash Commands**: Run `/help` in Claude Code for workflow commands
- **Issues**: Report bugs or ask questions in GitHub issues

---

**Ready to code!** Start with the first task in [tasks.md](./tasks.md) (generated by `/sp.tasks` command).
