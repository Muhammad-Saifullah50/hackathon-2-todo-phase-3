# Gemini CLI Rules - Todo Backend

Guidelines for working on the FastAPI backend of the Todo application.

## Tech Stack
- **Framework:** FastAPI
- **ORM/Models:** SQLModel (SQLAlchemy + Pydantic)
- **Migrations:** Alembic
- **Database:** PostgreSQL (asyncpg)
- **Testing:** Pytest, HTTPX (for async testing)
- **Task Runner:** PoeThePoet

## Development Guidelines

### 1. Code Quality
- **Type Hints:** Required for all function signatures.
- **Async:** Use `async/await` for all DB and I/O operations.
- **Validation:** Use Pydantic models (SQLModel) for request/response schemas.
- **Naming:** Snake_case for variables/functions, PascalCase for classes.

### 2. Architecture (Clean Layered)
- **API (`src/api/`):** Routers and dependency injection.
- **Models (`src/models/`):** SQLModel definitions.
- **Services (`src/services/`):** Business logic and DB orchestration.
- **Schemas (`src/schemas/`):** Non-DB response/request models.

### 3. Database & Migrations
- **Alembic:** All schema changes MUST have a migration.
- **Command:** `alembic revision --autogenerate -m "description"` followed by `alembic upgrade head`.

### 4. Testing Requirements
- **Location:** `tests/` (unit, integration, contract).
- **Commands:**
  - `poe test`: Run all tests.
  - `poe test-cov`: Run with coverage.
- **Mocking:** Use `pytest-asyncio` and mock external services.

### 5. Tooling
- **Linting:** `poe lint` (Ruff).
- **Formatting:** `poe format` (Black).
- **Type Checking:** `poe type-check` (Mypy).

## Common Patterns

### FastAPI Router
```python
@router.post("/", response_model=TaskRead)
async def create_task(
    *, session: AsyncSession = Depends(get_session), task: TaskCreate
):
    return await task_service.create(session, task)
```

### SQLModel Definition
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
```

## Error Handling
- Use custom exceptions in `src/exceptions.py`.
- Let FastAPI handle standard HTTP exceptions via dependencies or middleware.
- Always return descriptive error messages in JSON format.

## Security
- Use `bcrypt` for password hashing.
- Follow OAuth2 with Password flow (JWT) if implementing auth.
- Never expose sensitive data in response models.