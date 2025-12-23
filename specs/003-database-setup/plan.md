# Implementation Plan - Feature 2: Database Setup (Neon PostgreSQL)

**Feature Branch**: `003-database-setup`
**Date**: 2025-12-19
**Spec**: [specs/003-database-setup/spec.md](spec.md)

## Summary

This feature implements the persistence layer for the backend application using Neon PostgreSQL. It transitions the application from local JSON storage to a cloud-native relational database. Key components include setting up the `asyncpg` driver, `SQLModel` ORM, `Alembic` for async migrations, and connection pooling logic. It also includes a health check endpoint to verify connectivity and a seed script for development data.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- `fastapi` (Web Framework)
- `sqlmodel` (ORM)
- `asyncpg` (Async PostgreSQL Driver)
- `alembic` (Database Migrations)
- `pydantic-settings` (Configuration)
**Storage**: Neon PostgreSQL (Serverless)
**Testing**: `pytest` with `pytest-asyncio`
**Target Platform**: Linux (Docker containerized)
**Project Type**: Backend API (Part of Full Stack Web App)

## Constitution Check

- **Architecture**: Compliant with ADR-0001 (Full-Stack) and ADR-0002 (API Design).
- **Separation of Concerns**: Database logic isolated in `src/db/` and `src/models/`.
- **Environment Config**: Uses `.env` for credentials per ADR-0003.
- **Testing**: Includes unit and integration tests for database connections.

## Project Structure

### Documentation

```text
specs/003-database-setup/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # Task breakdown (to be created)
```

### Source Code

This feature assumes the `backend/` directory structure from Feature 1.

```text
backend/
├── alembic.ini                  # [NEW] Alembic config
├── alembic/                     # [NEW] Migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── requirements.txt             # [UPDATE] Add db dependencies
├── scripts/
│   └── seed_dev.py              # [NEW] Development seed script
└── src/
    ├── config/
    │   └── settings.py          # [UPDATE] Add DB settings
    ├── db/                      # [NEW] Database core
    │   ├── __init__.py
    │   └── session.py           # Engine & SessionManager
    ├── models/                  # [NEW] SQLModel entities
    │   ├── __init__.py
    │   ├── base.py              # Common mixins (Timestamp)
    │   ├── user.py              # User model
    │   └── task.py              # Task model
    └── api/
        └── routes/
            └── health.py        # [UPDATE] Add DB health check
```

## Implementation Steps

### Phase 1: Infrastructure & Configuration

1.  **Dependency Management**:
    - Add `sqlmodel`, `asyncpg`, `alembic`, `greenlet` to `requirements.txt`.
    - Install dependencies.

2.  **Configuration**:
    - Update `src/config/settings.py` to include `DATABASE_URL` and `ENVIRONMENT`.
    - Create `.env` and `.env.example` with Neon connection strings.

3.  **Database Session Manager**:
    - Create `src/db/session.py`.
    - Implement `DatabaseSessionManager` class with `create_async_engine`.
    - Configure connection pooling (size: 5, overflow: 10, recycle: 3600).
    - Implement `get_db` dependency for FastAPI.

### Phase 2: Models & Migrations

4.  **Base Models**:
    - Create `src/models/base.py` with `TimestampMixin` (created_at, updated_at).
    - Ensure `updated_at` uses `sa.func.now()` and `onupdate`.

5.  **Domain Models**:
    - Implement `User` model in `src/models/user.py` (UUID PK).
    - Implement `Task` model in `src/models/task.py` (UUID PK, FK to User).
    - Define relationships and indexes (tags GIN index, status/priority B-Tree).

6.  **Alembic Setup**:
    - Initialize alembic: `alembic init -t async alembic`.
    - Configure `alembic.ini` and `alembic/env.py`.
    - **Crucial**: Import SQLModel models in `env.py` for autogenerate detection (even if using manual migrations, it helps validation).
    - Configure `NullPool` for migrations.

7.  **Initial Migration**:
    - Generate initial migration script: `alembic revision -m "initial_schema"`.
    - Manually define `upgrade` and `downgrade` logic for Users and Tasks tables.
    - Apply migration: `alembic upgrade head`.

### Phase 3: Features & Verification

8.  **Health Check**:
    - Update `src/api/routes/health.py`.
    - Implement database ping logic.
    - Check `alembic_version` table.
    - Return status following ADR-0004.

9.  **Seed Script**:
    - Create `scripts/seed_dev.py`.
    - Implement idempotent logic (check if test user exists).
    - Create test user (`test@example.com`) and 5 sample tasks.
    - Ensure tasks cover edge cases (overdue, tags, priorities).

10. **Integration Testing**:
    - Write tests in `tests/test_database.py`.
    - Verify connection pooling, model constraints, and cascade deletes.

## Complexity Tracking

| Complexity | Justification | Mitigation |
|------------|---------------|------------|
| **Async SQLModel** | Required for high-performance non-blocking API. | Use `DatabaseSessionManager` pattern to abstract complexity. |
| **Manual Migrations** | `spec.md` forbids autogeneration to ensure schema control. | Strict review process for migration files. |
| **UUIDs** | Security requirement to avoid enumeration. | Use `uuid.uuid4()` client-side generation. |

## Verification Plan

### Automated Tests
- Run `pytest tests/test_database.py` to verify connection and CRUD basics.
- Run `scripts/seed_dev.py` to verify data seeding.

### Manual Verification
1.  **Connection**: Start app, check logs for "Database connection established".
2.  **Migrations**: Run `alembic upgrade head`, check Neon dashboard for tables.
3.  **Seed**: Run seed script, query tables to verify data.
4.  **Health**: `curl http://localhost:8000/api/v1/health` -> returns 200 OK with DB status.
5.  **Failure**: Stop DB, verify app handles connection errors gracefully (retry/fail based on env).