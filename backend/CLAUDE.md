# TodoMore Backend - FastAPI Development Guidelines

This file contains project-specific guidelines for Claude Code when working on the TodoMore backend application.

## Project Overview

**TodoMore Backend** - A modern FastAPI backend for the TodoMore task management application, featuring PostgreSQL database, SQLAlchemy ORM, and RESTful API design.

**Tech Stack:**
- Python 3.13+
- FastAPI 0.100+ for API framework
- SQLModel (SQLAlchemy + Pydantic) for ORM and validation
- Alembic for database migrations
- Neon PostgreSQL 16+ for database (serverless)
- Pytest for testing
- Pydantic v2 for data validation

**Architecture:**
- Layered architecture (API → Services → Models/Database)
- RESTful API design
- Async/await support
- Dependency injection pattern
- Soft delete pattern

## Core Principles

### 1. Code Quality Standards

- **Type Hints:** All function signatures must include type hints
- **Docstrings:** All public functions and classes require docstrings
- **Line Length:** Maximum 100 characters (configured in ruff.toml)
- **Naming:** Use descriptive names following PEP 8
- **Imports:** Organize imports (standard library → third-party → local)

### 2. Testing Requirements

- **Coverage:** Maintain high test coverage
- **Test Structure:** Follow AAA pattern (Arrange, Act, Assert)
- **Test Location:** All tests in `tests/` directory
- **Run Before Commit:** Always run `uv run pytest` before committing changes

### 3. API Design

- Follow RESTful conventions
- Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Use semantic status codes (200, 201, 400, 404, 500)
- Provide clear error messages
- Use Pydantic for request/response validation

### 4. Error Handling

- Use FastAPI's HTTPException for errors
- Provide user-friendly error messages
- Log errors appropriately
- Handle database errors gracefully

Example:
```python
from fastapi import HTTPException, status

try:
    result = service.get_task(task_id)
except TaskNotFoundError:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )
```

## File Organization

### Directory Structure

```
backend/
├── alembic/              # Database migrations
├── src/
│   ├── api/              # API route handlers
│   ├── core/             # Core utilities (security, config)
│   ├── db/               # Database utilities
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas (request/response)
│   ├── services/         # Business logic layer
│   └── validators/      # Custom validators
├── tests/                # Test files
├── alembic.ini
└── pyproject.toml
```

### When Adding New Features

1. **Models** (`src/models/`):
   - Add SQLModel classes for database tables
   - Include proper field types and constraints
   - Add soft delete support (deleted_at field)

2. **Schemas** (`src/schemas/`):
   - Create request schemas for input validation
   - Create response schemas for output formatting
   - Use appropriate field types (e.g., EmailStr, HttpUrl)

3. **Services** (`src/services/`):
   - Implement business logic in service classes
   - Keep methods focused and testable
   - Raise appropriate exceptions

4. **API Routes** (`src/api/`):
   - Create route handlers (routers)
   - Use dependency injection
   - Validate inputs with Pydantic
   - Return proper status codes

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
   - Keep business logic in services
   - Don't access database directly from routes
   - Use validators for input validation

## Specific Module Guidelines

### API Layer (`src/api/`)

**Purpose:** HTTP request/response handling only

**Rules:**
- Route handlers should be thin
- Delegate business logic to services
- Use dependency injection for database, auth, etc.
- Validate inputs with Pydantic
- Return appropriate HTTP status codes

**Example:**
```python
# ✅ Good - delegates to service
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task for the current user."""
    created_task = task_service.create_task(db, task, current_user.id)
    return created_task

# ❌ Bad - contains business logic
@router.post("/tasks")
async def create_task(task: TaskCreate):
    task_id = uuid.uuid4()  # Logic in route!
    db.execute(...)
    return task
```

### Service Layer (`src/services/`)

**Purpose:** Business logic and orchestration

**Rules:**
- Implement all business logic
- Don't use FastAPI-specific types (Request, Response)
- Raise domain-specific exceptions
- Keep methods focused (single responsibility)
- Document complex logic

**Example:**
```python
def create_task(
    self,
    db: Session,
    task_data: TaskCreate,
    user_id: str
) -> Task:
    """Create a new task for a user.

    Args:
        db: Database session
        task_data: Task creation data
        user_id: ID of the user creating the task

    Returns:
        Created Task object

    Raises:
        TaskValidationError: If validation fails
    """
    # Validate input
    validate_task_title(task_data.title)

    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=user_id,
        status=TaskStatus.PENDING
    )

    # Save to database
    db.add(task)
    db.commit()
    db.refresh(task)

    return task
```

### Models (`src/models/`)

**Purpose:** Database schema definition

**Rules:**
- Use SQLModel for table definition
- Include proper field types and constraints
- Add indexes for commonly queried fields
- Implement soft delete pattern
- Define relationships between models

**Example:**
```python
class Task(SQLModel, table=True):
    """Task model representing a task in the database."""
    __tablename__ = "tasks"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={"onupdate": utcnow})
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    subtasks: List["Subtask"] = Relationship(back_populates="task")
```

### Schemas (`src/schemas/`)

**Purpose:** Request/response validation and serialization

**Rules:**
- Use Pydantic models for validation
- Separate request and response schemas
- Use appropriate field types (EmailStr, HttpUrl, etc.)
- Make optional fields nullable, not optional
- Use enums for fixed sets of values

**Example:**
```python
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Validators (`src/validators/`)

**Purpose:** Business validation logic

**Rules:**
- Implement custom validation rules
- Raise ValidationError or domain-specific exceptions
- Keep validators focused and reusable
- Use descriptive error messages

**Example:**
```python
def validate_task_title(title: str) -> None:
    """Validate task title.

    Args:
        title: Task title to validate

    Raises:
        ValidationError: If title is invalid
    """
    if not title or not title.strip():
        raise ValidationError("Task title cannot be empty")
    if len(title) > 200:
        raise ValidationError("Task title cannot exceed 200 characters")
```

## Database Operations

### Soft Delete Pattern

Always use soft deletes instead of hard deletes:

```python
# Filter out deleted records
query = select(Task).where(Task.deleted_at.is_(None))

# Soft delete
task.deleted_at = datetime.now(timezone.utc)
db.commit()

# Restore
task.deleted_at = None
db.commit()
```

### Pagination

Implement pagination for list endpoints:

```python
def get_tasks(
    db: Session,
    user_id: str,
    page: int = 1,
    limit: int = 10
) -> PaginatedTasksResponse:
    """Get paginated tasks for a user."""
    offset = (page - 1) * limit

    # Get total count
    total = db.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.deleted_at.is_(None)
        )
    ).one()

    # Get paginated results
    tasks = db.exec(
        select(Task)
        .where(Task.user_id == user_id, Task.deleted_at.is_(None))
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    total_pages = (total + limit - 1) // limit

    return PaginatedTasksResponse(
        tasks=tasks,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )
```

## Common Patterns

### Creating a New API Endpoint

1. **Create schema** in `src/schemas/`:
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
```

2. **Create service method** in `src/services/`:
```python
def create_task(self, db: Session, task_data: TaskCreate, user_id: str) -> Task:
    validate_task_title(task_data.title)
    task = Task(**task_data.model_dump(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

3. **Create route handler** in `src/api/`:
```python
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return task_service.create_task(db, task, current_user.id)
```

### Creating a Database Migration

```bash
# Generate migration
cd backend && uv run alembic revision --autogenerate -m "Add task priority field"

# Review the generated migration file
# Edit if necessary

# Apply migration
cd backend && uv run alembic upgrade head
```

## Testing Guidelines

### Unit Tests

```python
def test_create_task(db_session):
    """Test creating a task."""
    # Arrange
    user = User(id="user1", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    task_data = TaskCreate(title="Test Task", description="Test description")

    # Act
    result = task_service.create_task(db_session, task_data, user.id)

    # Assert
    assert result.title == "Test Task"
    assert result.user_id == user.id
    assert result.status == TaskStatus.PENDING
```

### Integration Tests

```python
def test_create_task_endpoint(client, auth_headers):
    """Test creating a task via API."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test description"},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
```

## Common Mistakes to Avoid

### ❌ Don't Do This

```python
# 1. Business logic in routes
@router.post("/tasks")
async def create_task(task: TaskCreate):
    if len(task.title) < 3:  # Validation in route!
        raise HTTPException(400, "Title too short")
    # ... logic ...

# 2. Hard deletes
db.delete(task)  # ❌ Hard delete

# 3. SQL injection vulnerabilities
db.execute(f"SELECT * FROM tasks WHERE id = '{task_id}'")  # ❌ SQL injection

# 4. Not using dependency injection
db = Session(engine)  # ❌ Manual session management
```

### ✅ Do This Instead

```python
# 1. Use service layer
@router.post("/tasks")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(db, task, user_id)  # Delegate to service

# 2. Use soft deletes
task.deleted_at = datetime.now(timezone.utc)  # ✓ Soft delete

# 3. Use parameterized queries
db.execute(select(Task).where(Task.id == task_id))  # ✓ Safe query

# 4. Use dependency injection
db: Session = Depends(get_db)  # ✓ Dependency injection
```

## Performance Considerations

- **Indexes:** Add indexes to frequently queried fields
- **Pagination:** Always paginate large lists
- **N+1 Queries:** Use eager loading for relationships
- **Connection Pooling:** Configure appropriate pool size
- **Lazy Loading:** Be aware of lazy loading behavior

## Security Considerations

- **Input Validation:** Always validate user inputs
- **SQL Injection:** Use SQLAlchemy ORM, not raw SQL
- **XSS:** Sanitize user-generated content
- **Rate Limiting:** Implement rate limiting for public endpoints
- **CORS:** Configure CORS properly
- **Environment Variables:** Never commit secrets

## Quick Reference

### Run Tests
```bash
uv run pytest                    # Run all tests
uv run pytest -v                # Verbose output
uv run pytest --cov=src         # With coverage
```

### Code Quality
```bash
uv run ruff check src tests     # Lint code
uv run black src tests          # Format code
uv run mypy src tests           # Type check
```

### Database Operations
```bash
uv run alembic upgrade head     # Apply migrations
uv run alembic revision --autogenerate -m "message"  # Create migration
uv run alembic current          # Check current version
uv run alembic history          # View migration history
```

### Run Server
```bash
uvicorn src.main:app --reload   # Development server
uvicorn src.main:app            # Production server
```

---

**Remember:** The goal is to maintain a clean, testable, and maintainable codebase. When in doubt, follow existing patterns and ask for clarification.

## Active Technologies
- Neon PostgreSQL 16+ (serverless cloud database with automatic scaling)
- MCP (Model Context Protocol) for AI integration

## Recent Changes
- Phase 3: Added MCP (Model Context Protocol) server for AI integration
- 007-ai-chatbot: Added AI chatbot functionality with conversations and messages
