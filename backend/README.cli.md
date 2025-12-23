# 📋 CLI Todo Application

A beautiful, interactive command-line task management application built with Python. Features a modern UI with full-width menus, colorful highlights, and intuitive navigation.

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-76%20passing-brightgreen)

## ✨ Features

- **📝 Add Tasks** - Create tasks with titles and optional descriptions
- **👀 View Tasks** - Filter by status (all, pending, completed) with pagination
- **✏️ Update Tasks** - Modify task titles and descriptions
- **✅ Toggle Status** - Mark tasks as complete or pending (bulk operations supported)
- **🗑️ Delete Tasks** - Remove tasks individually or in bulk
- **💾 Persistent Storage** - Tasks saved to JSON file automatically
- **🎨 Beautiful UI** - Full-width menus with colors, emojis, and visual borders
- **⌨️ Keyboard Navigation** - Arrow keys for menu navigation, intuitive controls

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Muhammad-Saifullah50/hackathon-2-todo-phase-1.git
cd hackathon-2-todo-phase-1
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

### Running the Application

```bash
todo
```

Or run directly with Python:
```bash
python -m src.main
```

For narrow terminals (less than 80 columns), use simple mode:
```bash
todo --simple
```

## 📖 Usage

### Main Menu

When you launch the application, you'll see a beautiful welcome banner and main menu:

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║                    📋  TODO CLI APPLICATION  📋                        ║
║                                                                        ║
║               Beautiful Task Management in Terminal                   ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

✨ Features: Add • View • Update • Toggle • Delete ✨
💡 Tip: Use arrow keys to navigate, Ctrl+C to exit
```

### Navigation

- Use **↑/↓ arrow keys** to navigate menus
- Press **Enter** to select an option
- Press **Space** to select/deselect items in checkboxes
- Press **Ctrl+C** or **Esc** to exit or go back

### Adding a Task

1. Select "📝 Add task" from the main menu
2. Enter a task title (required)
3. Optionally add a description
4. Task is automatically saved!

### Viewing Tasks

1. Select "👀 View all tasks"
2. Choose a filter:
   - 📋 All tasks
   - ⏳ Pending tasks
   - ✅ Completed tasks
3. Navigate through pages if you have many tasks

### Updating a Task

1. Select "✏️ Update task"
2. Choose the task to update
3. Select what to update:
   - 📝 Title only
   - 📄 Description only
   - 📝📄 Both title and description
4. Enter new values

### Toggling Task Status

1. Select "✅ Toggle task status"
2. Choose action:
   - Mark tasks as complete
   - Mark tasks as incomplete
3. Select tasks using checkbox (Space to toggle)
4. Confirm your action

### Deleting Tasks

1. Select "🗑️ Delete tasks"
2. Select tasks to delete (Space to toggle)
3. Confirm deletion (⚠️ This cannot be undone!)

## 🏗️ Project Structure

```
hackathon-2-todo-phase-1/
├── src/
│   ├── cli/                    # CLI interface layer
│   │   ├── commands/           # Command implementations
│   │   │   ├── add.py         # Add task command
│   │   │   ├── view.py        # View tasks command
│   │   │   ├── update.py      # Update task command
│   │   │   ├── toggle.py      # Toggle status command
│   │   │   └── delete.py      # Delete tasks command
│   │   ├── display/           # Display formatting
│   │   │   ├── formatters.py # Rich formatting utilities
│   │   │   └── messages.py   # User-facing messages
│   │   ├── utils/             # CLI utilities
│   │   │   ├── styles.py     # Full-width menu wrappers
│   │   │   └── terminal.py   # Terminal utilities
│   │   └── app.py             # Main application loop
│   ├── models/                # Data models
│   │   └── task.py           # Task model
│   ├── services/              # Business logic
│   │   ├── task_service.py   # Task service implementation
│   │   ├── interface.py      # Service interface
│   │   └── validators.py     # Input validation
│   ├── storage/               # Data persistence
│   │   ├── json_storage.py   # JSON storage implementation
│   │   └── interface.py      # Storage interface
│   ├── exceptions.py          # Custom exceptions
│   └── main.py               # Entry point
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── contract/             # Contract tests
├── specs/                     # Specifications and planning
│   └── 001-cli-todo/
│       ├── spec.md           # Feature specification
│       ├── plan.md           # Implementation plan
│       └── tasks.md          # Task breakdown
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── CLAUDE.md                 # Claude Code guidelines
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_task_service.py

# Run tests verbosely
pytest -v
```

Current test coverage: **76 passing tests**

## 🛠️ Development

### Setting up Development Environment

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run code quality checks:
```bash
# Format code with black
black src tests

# Lint with ruff
ruff check src tests

# Type check with mypy
mypy src
```

### Project Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Use type hints for better code clarity
- Keep functions focused and small
- Document public APIs with docstrings

## 📦 Dependencies

### Core Dependencies
- **questionary** (>=2.0.0) - Interactive prompts and menus
- **rich** (>=13.7.0) - Beautiful terminal formatting

### Development Dependencies
- **pytest** (>=7.4.0) - Testing framework
- **pytest-cov** (>=4.1.0) - Coverage reporting
- **mypy** (>=1.7.0) - Static type checking
- **ruff** (>=0.1.0) - Fast Python linter
- **black** (>=23.0.0) - Code formatter

## 🎨 UI Features

### Full-Width Menus
All interactive prompts use full-width boxes with visual borders for a unified look:
- Cyan horizontal borders (─) above and below each menu
- Adapts to terminal width automatically
- Consistent styling across all commands

### Color Scheme
- **Bright Blue** - Question marks and prompts
- **Bright Green** - Highlighted selections and answers
- **Dark Gray** - Background for highlighted items
- **Yellow** - Pending task status
- **Green** - Completed task status
- **Red** - Error messages
- **Cyan** - Info messages and borders

### Emoji Icons
- 📝 Add task
- 👀 View tasks
- ✏️ Update task
- ✅ Complete/Toggle status
- 🗑️ Delete tasks
- 🚪 Exit
- 📋 All tasks
- ⏳ Pending tasks

## 💾 Data Storage

Tasks are stored in `tasks.json` in the current working directory with the following structure:

```json
{
  "tasks": [
    {
      "id": "a1b2c3d4",
      "title": "Complete project documentation",
      "description": "Write README and setup guide",
      "status": "pending",
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:30:00"
    }
  ]
}
```

### Backup
The application creates automatic backups before modifications with timestamps:
- Format: `tasks_backup_YYYYMMDD_HHMMSS.json`

## 🔧 Configuration

### Terminal Width
Minimum terminal width: **80 columns**

For narrow terminals, use simple mode:
```bash
todo --simple
```

### Pagination
- Default page size: **10 tasks per page**
- Automatic pagination for task lists

## 🐛 Troubleshooting

### Terminal Too Narrow
**Error:** `Terminal too narrow (minimum 80 columns required)`

**Solution:**
- Resize your terminal window
- Or use simple mode: `todo --simple`

### JSON File Corrupted
**Error:** `Error loading tasks: Invalid JSON`

**Solution:**
- Check `tasks.json` for syntax errors
- Restore from backup file in the same directory
- Or delete `tasks.json` to start fresh

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'questionary'`

**Solution:**
```bash
pip install -e .
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

**Saifullah**
- GitHub: [@Muhammad-Saifullah50](https://github.com/Muhammad-Saifullah50)

## 🙏 Acknowledgments

- Built with [questionary](https://github.com/tmbo/questionary) for beautiful prompts
- Styled with [rich](https://github.com/Textualize/rich) for terminal formatting
- Developed with assistance from Claude Code

---

**Built with ❤️ using Python and Claude Code**
