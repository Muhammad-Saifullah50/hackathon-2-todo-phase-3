# Todo API Backend

FastAPI-based REST API backend for the Todo Application with comprehensive task management, authentication, and analytics.

## Tech Stack

- **Framework**: FastAPI 0.100+
- **Language**: Python 3.13+
- **Database**: PostgreSQL 16+ (Neon serverless)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Migrations**: Alembic
- **Authentication**: JWT with Better Auth integration
- **Package Manager**: uv
- **Testing**: pytest with async support

## Features

### Core Task Management
- ✅ CRUD operations for tasks
- ✅ Task status tracking (pending, completed)
- ✅ Priority levels (low, medium, high)
- ✅ Due dates with timezone support
- ✅ Rich text notes
- ✅ Soft delete with trash management
- ✅ Bulk operations (toggle, delete)
- ✅ Manual task reordering

### Advanced Features
- 🏷️ **Tags System**: Create, assign, and filter by color-coded tags
- 🔍 **Global Search**: Full-text search across titles, descriptions, and notes
- ⚡ **Quick Filters**: Pre-built filters for common queries
- 🔢 **Subtasks**: Nested checklists with auto-completion
- 🔄 **Recurring Tasks**: Daily, weekly, monthly schedules with auto-generation
- 📝 **Task Templates**: Save and reuse task structures with tags and subtasks
- 📊 **Analytics**: Completion trends, priority breakdowns, and statistics
- 🔐 **Authentication**: JWT-based auth with Better Auth integration

### API Features
- 📚 **Auto-generated Documentation**: Swagger UI and ReDoc
- 🛡️ **Input Validation**: Pydantic schemas with detailed error messages
- 🔄 **Standardized Responses**: Consistent response format across all endpoints
- 🗄️ **Database Connection Pooling**: Optimized for serverless environments
- ⚡ **Performance Optimizations**: Composite indexes for common queries
- 🔧 **CORS Support**: Configurable cross-origin resource sharing
- 📝 **Comprehensive Logging**: Structured logging for debugging

## Setup

### Prerequisites

- Python 3.13+
- uv (recommended) or pip
- PostgreSQL 16+ (or Neon connection string)

### Local Development

1. **Install dependencies**:
   ```bash
   uv sync
   # OR
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Configure the following variables:
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@host/database

   # Auth
   JWT_SECRET=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS
   BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001

   # Environment
   ENVIRONMENT=development
   ```

3. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Start the development server**:
   ```bash
   # Using uv
   uv run uvicorn src.main:app --reload

   # OR directly
   uvicorn src.main:app --reload
   ```

   The API will be available at:
   - **API**: http://localhost:8000
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & Status
- `GET /health` - Health check with database connectivity status

### Authentication
- `GET /api/v1/user/me` - Get current authenticated user

### Tasks
- `GET /api/v1/tasks` - List tasks with pagination, filtering, sorting
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{task_id}` - Get task by ID
- `PATCH /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Soft delete task
- `PATCH /api/v1/tasks/{task_id}/toggle` - Toggle task completion status
- `PATCH /api/v1/tasks/bulk/toggle` - Bulk toggle tasks
- `DELETE /api/v1/tasks/bulk` - Bulk delete tasks
- `PATCH /api/v1/tasks/reorder` - Reorder tasks manually

### Due Dates
- `GET /api/v1/tasks/due` - Get tasks filtered by due date
- `PATCH /api/v1/tasks/{task_id}/due-date` - Set/update due date
- `GET /api/v1/tasks/due/stats` - Get due date statistics

### Trash Management
- `GET /api/v1/tasks/trash` - List deleted tasks
- `PATCH /api/v1/tasks/{task_id}/restore` - Restore deleted task
- `DELETE /api/v1/tasks/{task_id}/permanent` - Permanently delete task

### Tags
- `GET /api/v1/tags` - List all tags for user
- `POST /api/v1/tags` - Create new tag
- `PATCH /api/v1/tags/{tag_id}` - Update tag
- `DELETE /api/v1/tags/{tag_id}` - Delete tag
- `POST /api/v1/tasks/{task_id}/tags` - Assign tags to task
- `DELETE /api/v1/tasks/{task_id}/tags` - Remove tags from task

### Subtasks
- `GET /api/v1/tasks/{task_id}/subtasks` - List subtasks for task
- `POST /api/v1/tasks/{task_id}/subtasks` - Create subtask
- `PATCH /api/v1/subtasks/{subtask_id}` - Update subtask
- `PATCH /api/v1/subtasks/{subtask_id}/toggle` - Toggle subtask completion
- `DELETE /api/v1/subtasks/{subtask_id}` - Delete subtask
- `PATCH /api/v1/tasks/{task_id}/subtasks/reorder` - Reorder subtasks

### Recurring Tasks
- `GET /api/v1/tasks/{task_id}/recurrence` - Get recurrence pattern
- `POST /api/v1/tasks/{task_id}/recurrence` - Set recurrence pattern
- `PATCH /api/v1/tasks/{task_id}/recurrence` - Update recurrence pattern
- `DELETE /api/v1/tasks/{task_id}/recurrence` - Stop recurrence
- `GET /api/v1/tasks/{task_id}/recurrence/preview` - Preview next occurrences

### Templates
- `GET /api/v1/templates` - List all templates
- `POST /api/v1/templates` - Create template
- `PATCH /api/v1/templates/{template_id}` - Update template
- `DELETE /api/v1/templates/{template_id}` - Delete template
- `POST /api/v1/templates/{template_id}/apply` - Create task from template
- `POST /api/v1/tasks/{task_id}/save-as-template` - Save task as template

### Search
- `GET /api/v1/tasks/search` - Search tasks with filters
- `GET /api/v1/tasks/autocomplete` - Get search suggestions
- `GET /api/v1/tasks/quick-filters` - Get quick filter options with counts

### Analytics
- `GET /api/v1/tasks/analytics/stats` - Get task statistics
- `GET /api/v1/tasks/analytics/completion-trend` - Get completion trend data
- `GET /api/v1/tasks/analytics/priority-breakdown` - Get priority distribution

## Database

### Migrations

This project uses Alembic for database migrations:

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show current migration version
uv run alembic current

# Show migration history
uv run alembic history

# Generate a new migration (after modifying models)
uv run alembic revision --autogenerate -m "description"
```

### Models

- **User**: User accounts with authentication
- **Task**: Core task entity with all fields
- **Tag**: Color-coded labels for categorization
- **TaskTag**: Many-to-many relationship between tasks and tags
- **Subtask**: Nested checklists within tasks
- **RecurrencePattern**: Recurring task schedules
- **TaskTemplate**: Reusable task structures
- **TemplateTag**: Tags associated with templates
- **ViewPreference**: User UI preferences

### Indexes

Performance-optimized composite indexes:
- `idx_tasks_user_deleted` - (user_id, deleted_at) for active tasks
- `idx_tasks_user_due_date` - (user_id, due_date) for due date queries
- `idx_tasks_user_status` - (user_id, status) for status filtering
- Additional indexes on foreign keys and frequently queried fields

## Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/integration/test_tasks.py

# Run with verbose output
uv run pytest -v

# Run in watch mode (requires pytest-watch)
uv run ptw
```

### Test Structure

```
tests/
├── integration/        # Integration tests with database
│   ├── test_task_routes.py
│   ├── test_database.py
│   └── test_health.py
└── unit/              # Unit tests for services and models
    ├── test_models.py
    ├── test_schemas.py
    └── test_task_service.py
```

### Current Test Coverage

- **Total Tests**: 48 passing
- **Coverage**: 35.91% (core functionality well-tested, new features need coverage)
- **Integration Tests**: Database operations, API endpoints
- **Unit Tests**: Models, schemas, service layer logic

## Code Quality

### Linting & Formatting

```bash
# Check code with ruff
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Format code with black
uv run black src/ tests/

# Type checking with mypy
uv run mypy src/ tests/
```

### Code Standards

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes
- Write tests for new features
- Use snake_case for variables and functions
- Use PascalCase for class names

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── src/
│   ├── api/                    # API layer
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── routes/             # API endpoints
│   │   │   ├── health.py
│   │   │   ├── tasks.py
│   │   │   ├── tags.py
│   │   │   ├── subtasks.py
│   │   │   ├── recurring.py
│   │   │   ├── templates.py
│   │   │   ├── search.py
│   │   │   └── user.py
│   │   └── utils/              # API utilities
│   ├── models/                 # SQLModel database models
│   │   ├── task.py
│   │   ├── tag.py
│   │   ├── subtask.py
│   │   ├── recurrence_pattern.py
│   │   └── task_template.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── task_schemas.py
│   │   ├── tag_schemas.py
│   │   ├── subtask_schemas.py
│   │   ├── recurring_schemas.py
│   │   └── template_schemas.py
│   ├── services/               # Business logic layer
│   │   ├── task_service.py
│   │   ├── tag_service.py
│   │   ├── subtask_service.py
│   │   ├── recurring_service.py
│   │   └── template_service.py
│   ├── auth.py                 # Authentication logic
│   ├── config.py               # Application configuration
│   ├── database.py             # Database connection
│   └── main.py                 # FastAPI application entry point
├── tests/                      # Test suite
└── scripts/                    # Utility scripts
```

## Authentication

The API uses JWT bearer tokens for authentication:

```python
# Protected endpoint example
@router.get("/tasks")
async def get_tasks(
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically injected
    return await task_service.get_tasks(current_user.id)
```

### Token Format

```
Authorization: Bearer <jwt_token>
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "data": null,
  "error": {
    "message": "Task not found",
    "code": "TASK_NOT_FOUND"
  }
}
```

### Common HTTP Status Codes

- `200 OK` - Successful GET/PATCH requests
- `201 Created` - Successful POST requests
- `204 No Content` - Successful DELETE requests
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server errors

## Performance Optimizations

- **Connection Pooling**: Optimized for serverless environments
- **Composite Indexes**: Fast queries for common patterns
- **Pagination**: All list endpoints support pagination
- **Query Optimization**: Eager loading with selectinload for relationships
- **Caching**: Future: Response caching for static data

## Deployment

### Environment Variables

Required for production:

```env
DATABASE_URL=postgresql://...
JWT_SECRET=<strong-random-secret>
ENVIRONMENT=production
BACKEND_CORS_ORIGINS=https://yourdomain.com
```

### Docker

Build and run with Docker:

```bash
docker build -t todo-backend .
docker run -p 8000:8000 todo-backend
```

Or use Docker Compose from the root directory:

```bash
docker-compose up backend
```

### Health Checks

The `/health` endpoint provides detailed health status:

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-23T12:00:00Z"
}
```

## Troubleshooting

### Database Connection Issues

```bash
# Test database connectivity
uv run python -c "from src.database import test_connection; test_connection()"

# Check migration status
uv run alembic current

# Reset database (development only!)
uv run alembic downgrade base
uv run alembic upgrade head
```

### Migration Conflicts

```bash
# View migration history
uv run alembic history

# Resolve conflicts by merging branches
uv run alembic merge heads
```

### Import Errors

```bash
# Reinstall dependencies
uv sync --reinstall
```

## Contributing

1. Follow the existing code structure
2. Write tests for new features (aim for 80%+ coverage)
3. Use type hints everywhere
4. Add docstrings to public functions
5. Run linting and tests before committing
6. Create migrations for schema changes
7. Update API documentation in docstrings

## License

MIT
