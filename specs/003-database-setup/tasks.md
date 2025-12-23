# Tasks: Feature 2 - Database Setup (Neon PostgreSQL)

**Input**: Feature Specification from `/specs/003-database-setup/spec.md`
**Prerequisites**: plan.md (required), spec.md (required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User Story identifier (US1-US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create `backend` directory structure if not exists (src/db, src/models, scripts)
- [x] T002 Add database dependencies to `backend/requirements.txt` (sqlmodel, asyncpg, alembic, greenlet)
- [x] T003 Install new dependencies in the virtual environment
- [x] T004 [P] Update `backend/src/config/settings.py` with `DATABASE_URL` and `ENVIRONMENT` fields
- [x] T005 [P] Create `backend/.env` and `backend/.env.example` with Neon connection string placeholders

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Implement `DatabaseSessionManager` in `backend/src/db/session.py` with async engine and pool configuration
- [x] T007 Initialize Alembic (`alembic init -t async backend/alembic`) and configure `alembic.ini`
- [x] T008 Configure `backend/alembic/env.py` to support SQLModel and `NullPool`
- [x] T009 Create `backend/src/models/base.py` with `TimestampMixin` (created_at, updated_at)

**Checkpoint**: Database engine and migration framework ready.

## Phase 3: User Story 1 - Connection Validation (Priority: P1) 🎯 MVP

**Goal**: Verify application can successfully connect to Neon PostgreSQL.

**Independent Test**: Start app, hit health endpoint, verify 200 OK and DB status.

### Implementation for User Story 1

- [x] T010 [US1] Create `backend/src/api/routes/health.py` with database connectivity check
- [x] T011 [US1] Register health router in `backend/src/main.py` (or `app.py`)
- [x] T012 [US1] Add `alembic_version` check to health endpoint response
- [x] T013 [US1] Implement environment-aware connection retry logic (0 retries dev, 5 prod) in `session.py`
- [x] T014 [US1] Verify connection by running the application and checking logs

**Checkpoint**: Application connects to DB and reports health.

## Phase 4: User Story 2 - Schema Creation & Migration (Priority: P2)

**Goal**: Manage database schema via migrations.

**Independent Test**: Run migrations, verify tables exist in Neon console.

### Implementation for User Story 2

- [x] T015 [P] [US2] Implement `User` model in `backend/src/models/user.py` with UUID and constraints
- [x] T016 [P] [US2] Implement `Task` model in `backend/src/models/task.py` with UUID, relationships, and indexes
- [x] T017 [US2] Update `backend/src/models/__init__.py` to export User and Task for Alembic detection
- [x] T018 [US2] Generate initial migration script (`alembic revision`) and manually write upgrade/downgrade logic
- [x] T019 [US2] Apply migration (`alembic upgrade head`) and verify schema creation

**Checkpoint**: Database schema (User/Task tables) exists in Neon.

## Phase 5: User Story 4 - Session Management (Priority: P2)

**Goal**: Safe database access in API routes.

**Independent Test**: Route receives valid session, commits on success, rolls back on error.

### Implementation for User Story 4

- [x] T020 [US4] Implement `get_db` dependency in `backend/src/db/session.py` with yield pattern
- [x] T021 [US4] Add context manager support to `DatabaseSessionManager` for scripts
- [x] T022 [P] [US4] Create integration test `tests/test_database.py` for session lifecycle (commit/rollback)
- [x] T023 [US4] Verify connection pool behavior (size, overflow) under load (manual check or load test)

**Checkpoint**: API routes can request `Session` dependency safely.

## Phase 6: User Story 3 - Seed Data (Priority: P3)

**Goal**: Populate database with development data.

**Independent Test**: Run script, verify data in DB.

### Implementation for User Story 3

- [x] T024 [US3] Create `backend/scripts/seed_dev.py` script structure
- [x] T025 [US3] Implement idempotent user creation (check email `test@example.com`)
- [x] T026 [US3] Implement task creation (5 tasks: 2 pending, 3 completed) with varied tags/dates
- [x] T027 [US3] Add password hashing (bcrypt) for test user
- [x] T028 [US3] Execute seed script and verify data in database

## Phase 7: Polish & Documentation

- [x] T029 Update README with database setup instructions (env vars, migration commands)
- [x] T030 Ensure all sensitive credentials are in `.env` (verify gitignore)
- [x] T031 Review logs for sensitive information leaks (ensure query logging is DEBUG only)

## Dependencies & Execution Order

1.  **Phase 1 & 2** are blocking.
2.  **Phase 3 (US1)** verifies the setup.
3.  **Phase 4 (US2)** builds the schema.
4.  **Phase 5 (US4)** allows using the schema in API.
5.  **Phase 6 (US3)** populates the schema.

All tasks within a Phase marked [P] can run in parallel.
