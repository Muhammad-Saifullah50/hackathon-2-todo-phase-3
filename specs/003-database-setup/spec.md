# Feature Specification: Database Setup (Neon PostgreSQL)

**Feature Branch**: `003-database-setup`
**Created**: 2025-12-19
**Status**: Draft
**Input**: User description: "Feature 2: Database Setup (Neon PostgreSQL) - Set up Neon PostgreSQL database connection, SQLModel ORM with async support, Alembic migrations, seed data script, and database health checks for the FastAPI backend"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Database Connection Validation (Priority: P1)

As a developer working on the backend, I need to verify that the application can successfully connect to the Neon PostgreSQL database so that I can confidently proceed with implementing data persistence features.

**Why this priority**: Without a working database connection, no data-related features can be developed or tested. This is the foundational requirement that unblocks all future backend development.

**Independent Test**: Can be fully tested by starting the backend service with valid database credentials and confirming it connects successfully without errors, delivers value by enabling data persistence for all future features.

**Acceptance Scenarios**:

1. **Given** the backend service has valid Neon database credentials configured, **When** the service starts up, **Then** it successfully establishes a connection to the database and logs confirmation
2. **Given** the database connection is established, **When** a health check endpoint is queried, **Then** it returns a successful status indicating database connectivity
3. **Given** the backend service has invalid or missing database credentials, **When** the service attempts to start, **Then** it fails immediately with a clear error message indicating the database connection issue
4. **Given** the application is running in development mode, **When** a database connection error occurs, **Then** the service fails fast without retries and logs detailed error information
5. **Given** the application is running in production mode, **When** a database connection error occurs on startup, **Then** the service retries up to 5 times before failing and logs each attempt

---

### User Story 2 - Database Schema Creation and Migration (Priority: P2)

As a developer, I need to create and manage database schema through migrations so that I can maintain version control of database changes and deploy them consistently across environments.

**Why this priority**: Schema management is essential for maintaining data integrity and enabling team collaboration, but can only be valuable after the basic connection is established.

**Independent Test**: Can be tested by executing migration commands that create the initial User and Task tables, then verifying the tables exist in the database with correct column definitions and constraints.

**Acceptance Scenarios**:

1. **Given** the database is empty and migrations have not been run, **When** the initial migration is applied, **Then** User and Task tables are created with all specified columns, constraints, and indexes
2. **Given** migrations have been successfully applied, **When** querying the migration version table, **Then** the current version matches the latest migration file
3. **Given** a migration has been applied, **When** a rollback command is executed, **Then** the database schema reverts to the previous version and the migration version table updates accordingly
4. **Given** the database schema is out of date, **When** the application starts, **Then** it logs a warning about migration status but continues to start normally
5. **Given** a developer creates a new migration file, **When** the migration is applied via Docker exec command, **Then** the database schema updates successfully and the change is reflected in the migration version table

---

### User Story 3 - Development Environment Seed Data (Priority: P3)

As a developer, I need to populate the database with test data so that I can develop and test features without manually creating data for every test session.

**Why this priority**: Seed data improves development efficiency and testing convenience, but is not strictly required for the database setup to be functional.

**Independent Test**: Can be tested by running the seed script and verifying that a test user account and sample tasks are created in the database with the expected values.

**Acceptance Scenarios**:

1. **Given** the database schema exists but no data has been seeded, **When** the seed script is executed, **Then** a test user with email `test@example.com` is created with hashed password `Test123!@#`
2. **Given** the test user has been created, **When** the seed script creates sample tasks, **Then** 5 tasks are created (2 pending, 3 completed) with varied priorities, due dates, and tags
3. **Given** the seed script has been run once, **When** the seed script is executed again, **Then** it detects existing data and skips creation without errors (idempotent behavior)
4. **Given** sample tasks are created with tags, **When** querying the database, **Then** all tags are stored in normalized lowercase format with proper array structure
5. **Given** sample tasks are created with due dates, **When** checking the data, **Then** all due dates are stored in UTC timezone format

---

### User Story 4 - Database Session Management in API Routes (Priority: P2)

As a backend developer implementing API endpoints, I need a consistent way to obtain database sessions so that I can perform database operations safely with proper transaction management and error handling.

**Why this priority**: Session management patterns must be established before any API endpoints can be implemented, making this critical infrastructure for backend development.

**Independent Test**: Can be tested by creating a simple API endpoint that uses the session dependency to query the database, verifying the session is properly created, committed/rolled back, and disposed.

**Acceptance Scenarios**:

1. **Given** an API endpoint requires database access, **When** the endpoint handler receives a database session via dependency injection, **Then** the session is valid and can execute queries
2. **Given** an API endpoint successfully completes, **When** the response is returned, **Then** the database session is automatically committed and closed
3. **Given** an error occurs during database operations, **When** the exception is raised, **Then** the database session automatically rolls back any uncommitted changes before closing
4. **Given** multiple concurrent requests arrive, **When** each request uses dependency injection for database sessions, **Then** each request receives its own isolated session from the connection pool
5. **Given** the connection pool is exhausted, **When** a new request attempts to obtain a session, **Then** it waits up to 30 seconds before timing out with an appropriate error

---

### Edge Cases

- What happens when the Neon database becomes temporarily unavailable during application runtime?
- How does the system handle connection pool exhaustion when all connections are in use?
- What occurs if a migration file contains syntax errors or invalid SQL?
- How does the system behave when environment variables are missing or malformed?
- What happens when a migration partially succeeds but fails mid-way (e.g., network interruption)?
- How does the seed script handle partial data (e.g., user exists but tasks don't)?
- What occurs when attempting to create a task with a due date in the past?
- How does the system handle tag validation (empty tags, special characters, length limits)?
- What happens when a user is deleted with CASCADE constraints (orphaned tasks)?
- How does the application behave when database credentials expire or are rotated?
- What occurs when Neon enforces connection limits on the free tier?
- How does the system handle timezone conversions for due_date fields?
- What happens when attempting to apply migrations on a database with existing data?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST establish an async database connection to Neon PostgreSQL using asyncpg driver with SSL mode required
- **FR-002**: System MUST use SQLModel as the ORM layer with async session support for all database operations
- **FR-003**: System MUST configure connection pooling with a pool size of 5-10 connections and max overflow of 10-20 connections
- **FR-004**: System MUST enable pool pre-ping to verify connection health before use
- **FR-005**: System MUST recycle connections after 3600 seconds (1 hour) to prevent stale connections
- **FR-006**: System MUST validate required environment variables (DATABASE_URL, ENVIRONMENT) on startup and fail immediately if missing
- **FR-007**: System MUST support two Neon database branches: `dev` (for development and testing) and `main` (for production)
- **FR-008**: System MUST provide a SessionManager class that initializes the database engine and session factory on application startup
- **FR-009**: System MUST provide a `get_db()` dependency function for FastAPI routes that yields database sessions with automatic rollback on errors
- **FR-010**: System MUST configure Alembic for async migrations with proper env.py setup for SQLModel model detection
- **FR-011**: System MUST disable Alembic auto-generation and require all migrations to be hand-written by developers
- **FR-012**: System MUST define User and Task SQLModel models with proper relationships, constraints, and timestamp fields
- **FR-013**: User model MUST include fields: id (UUID), email (unique), password_hash, name (nullable), is_active (boolean), email_verified (boolean), created_at, updated_at
- **FR-014**: Task model MUST include fields: id (UUID), user_id (foreign key), title, description (nullable), status (enum: pending/completed), priority (enum: low/medium/high), due_date (nullable), tags (array, max 20, max 10 chars each, normalized lowercase), created_at, updated_at, completed_at (nullable)
- **FR-015**: System MUST implement CASCADE delete behavior so deleting a user automatically deletes all their tasks
- **FR-016**: System MUST create indexes on frequently queried columns: user_id, status, priority, due_date, created_at
- **FR-017**: System MUST create a GIN index on the tags array column for efficient array containment queries
- **FR-018**: System MUST automatically update `updated_at` timestamp using `onupdate=func.now()` at the ORM level
- **FR-019**: System MUST automatically set `completed_at` when task status changes to "completed"
- **FR-020**: System MUST validate due_date on task creation to prevent past dates, but allow existing tasks to have past due dates (overdue)
- **FR-021**: System MUST validate tags on tasks: maximum 20 tags, maximum 10 characters per tag, normalized to lowercase with trimmed whitespace
- **FR-022**: System MUST not enforce uniqueness on task titles within a user (allow duplicate titles)
- **FR-023**: System MUST provide a seed script (`scripts/seed_dev.py`) that creates a test user (test@example.com / Test123!@#) with bcrypt-hashed password
- **FR-024**: Seed script MUST be idempotent (check if data exists before creating, safe to run multiple times)
- **FR-025**: Seed script MUST create 5 sample tasks for the test user: 2 pending, 3 completed, with varied priorities, some with due dates, some with tags
- **FR-026**: System MUST provide a health check endpoint at `/api/v1/health` that returns database connection status following ADR-0004 response format
- **FR-027**: Health check MUST return simple format: `{"status": "healthy", "database": "connected", "migration": "up-to-date"}` wrapped in ADR-0004 envelope
- **FR-028**: Health check MUST query the `alembic_version` table to determine if migrations are current
- **FR-029**: System MUST log a warning (not crash) on startup if database migrations are out of date
- **FR-030**: System MUST retry database connections in production mode (5 retries with backoff) but fail immediately in development mode
- **FR-031**: System MUST detect environment (development vs production) using ENVIRONMENT environment variable
- **FR-032**: System MUST log all database queries in development mode (DEBUG level) but only errors in production mode (INFO level)
- **FR-033**: System MUST use client-side UUID generation (`uuid.uuid4()`) for all UUID primary keys
- **FR-034**: System MUST store all timestamps in UTC timezone using `TIMESTAMP WITH TIME ZONE` PostgreSQL type
- **FR-035**: System MUST provide clear documentation for running migrations via `docker-compose exec backend alembic upgrade head`
- **FR-036**: System MUST support migration rollback via `docker-compose exec backend alembic downgrade -1`
- **FR-037**: System MUST provide documentation for running seed script via `docker-compose exec backend python scripts/seed_dev.py`
- **FR-038**: System MUST dispose of database engine properly on application shutdown to prevent connection leaks
- **FR-039**: System MUST use `NullPool` for Alembic migrations to avoid connection pool issues during schema changes
- **FR-040**: System MUST import all SQLModel models in Alembic env.py to ensure proper migration detection

### Key Entities

- **User**: Represents an authenticated user of the application. Contains authentication credentials (email, hashed password), profile information (name), account status (is_active, email_verified), and timestamp tracking (created_at, updated_at). Uses UUID as primary key for security. Has a one-to-many relationship with Task (one user owns many tasks).

- **Task**: Represents a todo item belonging to a user. Contains task content (title, description), workflow state (status: pending/completed, completed_at timestamp), organizational metadata (priority: low/medium/high, due_date, tags array), ownership reference (user_id foreign key), and timestamp tracking (created_at, updated_at). Uses UUID as primary key. Belongs to exactly one User via CASCADE delete relationship.

- **Database Connection Pool**: Manages a pool of persistent connections to Neon PostgreSQL. Configuration includes pool size (5-10 connections), max overflow (10-20 additional connections), timeout settings (30 seconds), health checking (pre-ping enabled), and connection recycling (1 hour lifetime). Handles concurrency and connection lifecycle.

- **Migration Version**: Tracks the current database schema version using Alembic's `alembic_version` table. Contains a single row with the revision hash of the most recently applied migration. Used by health check endpoint to verify schema currency.

- **Seed Data**: Development-only test data consisting of a single test user account and 5 sample tasks. Created by idempotent seed script. Includes varied task states, priorities, due dates, and tags for comprehensive testing scenarios.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Database connection is established successfully within 5 seconds of application startup under normal network conditions
- **SC-002**: The initial database migration creates User and Task tables with all columns, constraints, and indexes in under 10 seconds
- **SC-003**: The seed script completes execution and creates test user plus 5 sample tasks in under 5 seconds
- **SC-004**: The health check endpoint responds in under 200 milliseconds and accurately reports database connection status
- **SC-005**: Developers can run migration commands via Docker exec without encountering connection pool errors or timeouts
- **SC-006**: The seed script can be executed multiple times without errors or duplicate data creation (idempotency verified)
- **SC-007**: Database sessions are properly managed with zero connection leaks detected after 100 API requests
- **SC-008**: Migration rollback successfully reverts schema changes and updates migration version table without data loss
- **SC-009**: Connection retry logic in production mode successfully recovers from transient network failures within 30 seconds
- **SC-010**: Development mode immediately fails with clear error messages when database credentials are invalid or missing
- **SC-011**: All database queries in development mode are logged to console for debugging purposes
- **SC-012**: Production mode logs only database errors without exposing sensitive query details
- **SC-013**: The connection pool handles 50 concurrent database requests without exhausting available connections
- **SC-014**: Developers can follow documentation to set up database locally in under 10 minutes
- **SC-015**: Tag validation prevents invalid data (empty tags, oversized tags, excessive tag counts) from being stored in database

### Non-Functional Success Indicators

- **NF-001**: Database schema design follows third normal form (3NF) with no data duplication
- **NF-002**: All database operations use parameterized queries through ORM to prevent SQL injection
- **NF-003**: Documentation clearly explains the two-branch strategy (dev for development/testing, main for production)
- **NF-004**: Error messages provide actionable guidance without exposing sensitive database information
- **NF-005**: Database connection configuration follows Neon best practices for serverless PostgreSQL
- **NF-006**: Migration files follow consistent naming conventions and include descriptive messages

## Out of Scope

The following are explicitly **not** included in this feature and will be addressed in future features:

- User authentication and authorization logic (Feature 3)
- Password hashing implementation for user signup/login (Feature 3)
- API endpoints for task CRUD operations (Features 4-8)
- Frontend integration and API consumption (Features 4+)
- Better Auth integration and JWT token verification (Feature 3)
- Database backup and restore procedures (Feature 10)
- Production deployment configuration (Feature 10)
- Performance optimization and query tuning (Feature 9+)
- Database monitoring and alerting (Feature 10)
- Advanced migration strategies (blue-green, canary) (Feature 10)
- Data seeding for production environments
- Multi-tenancy or data isolation beyond user-level
- Full-text search indexing
- Database replication or read replicas
- Automated database scaling
- Comprehensive error recovery mechanisms beyond connection retry

## Assumptions

- Developers have Docker and Docker Compose installed locally for running migrations and seed scripts
- The project owner will provision the Neon PostgreSQL database manually via the Neon UI before feature implementation
- Database connection string will be provided securely (not committed to repository) via `.env` file
- Python 3.13+ and all required dependencies (asyncpg, SQLModel, Alembic) will be installed in the Docker container
- Neon database uses PostgreSQL 16+ which includes `gen_random_uuid()` function built-in
- The dev branch in Neon is acceptable for both development and automated testing (no separate test branch)
- Developers are working on Unix-like systems (Linux/macOS) or Windows with WSL2 for Docker compatibility
- Internet connectivity is available for connecting to cloud-hosted Neon database
- The backend service will be the only application accessing this database (no external integrations)
- Tag normalization (lowercase) happens at the application layer before database insertion
- Due date validation (no past dates on creation) happens at the API layer, not database constraints
- Connection pool sizing (5-10 connections) is appropriate for initial development workload
- The `ENVIRONMENT` environment variable will be set correctly in both dev and prod configurations
- Database credentials will not expire frequently or will be rotated with appropriate notice
- Neon's free tier connection limits are sufficient for development purposes
- The test user email `test@example.com` and password `Test123!@#` are acceptable for development
- Bcrypt password hashing will match Better Auth's hashing in Feature 3
- All developers working on the project have access to the Neon database credentials
- Migration files will be reviewed manually before application to catch any autogeneration errors
- The seed script is only for development convenience and will never run in production
- Database logs in development mode are acceptable for console output (not persisted to files)
- CASCADE delete behavior for user → tasks is acceptable without additional confirmation

## Dependencies

- **External**: Neon PostgreSQL service (cloud-hosted), Docker, Docker Compose
- **Related Features**:
  - Feature 1 (Project Setup & Architecture) - MUST be complete first (provides Docker Compose, backend structure, .env configuration)
  - Feature 3 (User Authentication) - Depends on this feature (requires User model and database connection)
  - Feature 4+ (Task CRUD) - Depends on this feature (requires Task model and database session management)
- **Blocking**: This feature must be completed before any backend API endpoints or authentication features can be implemented, as it provides the foundational data persistence layer

## Technical Notes for Implementation

*Note: These technical details guide the implementation planning phase but are not part of the business specification.*

### Architecture Alignment

This specification aligns with the following Architecture Decision Records:

- **ADR-0001**: Uses FastAPI backend (separated from Next.js frontend) with async database operations
- **ADR-0003**: Follows environment configuration strategy with service-specific .env files for backend
- **ADR-0004**: Health endpoint follows standardized API response format with status codes in body

### Technology Stack (Implementation Phase)

The following technologies will be used during implementation:

- **Database**: Neon PostgreSQL 16+ (serverless, cloud-hosted)
- **Driver**: asyncpg (async PostgreSQL driver for Python)
- **ORM**: SQLModel 0.0.14+ (built on SQLAlchemy 2.0+ and Pydantic)
- **Migrations**: Alembic 1.13+ (async mode with NullPool)
- **Validation**: Pydantic v2 (field validators for tags, due dates)
- **Password Hashing**: bcrypt (for seed script test user)
- **Session Management**: SQLAlchemy AsyncSession with sessionmaker

### Database Configuration Values

Based on research, the following configuration values will be used:

- **Pool Size**: 5 connections (conservative for serverless)
- **Max Overflow**: 10 additional connections
- **Pool Timeout**: 30 seconds
- **Pool Pre-Ping**: True (health check before use)
- **Pool Recycle**: 3600 seconds (1 hour)
- **Connection Retry**: 5 attempts in production, 0 in development
- **Query Logging**: DEBUG level in dev, INFO level in prod

### Migration Workflow

1. Developer modifies SQLModel models in `backend/src/models/`
2. Developer manually creates migration file using blank template (not autogenerate)
3. Developer writes SQL in migration's `upgrade()` and `downgrade()` functions
4. Developer reviews migration file for correctness
5. Developer runs `docker-compose exec backend alembic upgrade head`
6. Developer verifies schema changes in database
7. Developer restarts backend container to pick up model changes

### Environment Variables Required

**Backend `.env` (Feature 2):**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require&options=project%3Dmy-project%20branch%3Ddev
ENVIRONMENT=development  # or "production"
CORS_ORIGINS=http://localhost:3000  # Optional, defaults to localhost:3000
LOG_LEVEL=DEBUG  # Optional, defaults to INFO
```

### File Structure

```
backend/
├── alembic/
│   ├── versions/          # Migration files (hand-written)
│   ├── env.py             # Alembic async configuration
│   └── script.py.mako     # Migration template
├── scripts/
│   └── seed_dev.py        # Development seed data script
├── src/
│   ├── config/
│   │   └── settings.py    # Pydantic Settings for env var validation
│   ├── db/
│   │   └── session.py     # SessionManager and get_db dependency
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py        # TimestampMixin
│   │   ├── user.py        # User model
│   │   └── task.py        # Task model
│   └── api/
│       └── routes/
│           └── health.py  # Health check endpoint
├── tests/
│   └── test_database.py   # Connection and session tests
├── alembic.ini            # Alembic configuration file
├── .env                   # Environment variables (gitignored)
└── .env.example           # Template with placeholder values
```

### Neon Branch Syntax

**Dev/Test Connection String:**
```
postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db?sslmode=require&options=project%3Dmy-project%20branch%3Ddev
```

**Production Connection String:**
```
postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db?sslmode=require&options=project%3Dmy-project%20branch%3Dmain
```

## Open Questions

None - all architectural and technical decisions have been resolved through thorough clarification sessions and Context7 research.
