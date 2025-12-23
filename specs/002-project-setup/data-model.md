# Data Model: Project Setup & Architecture

**Feature**: Project Setup & Architecture
**Branch**: `002-project-setup`
**Created**: 2025-12-19

## Overview

This document defines the database schema for the Todo application, including User and Task entities. The schema is designed to support future authentication (Feature 3) and task management features (Features 4-8).

---

## Design Principles

1. **UUID Primary Keys**: Use UUIDs instead of auto-incrementing integers to prevent enumeration attacks and enable distributed systems
2. **Timestamps**: Track `created_at` and `updated_at` for all entities for auditing and debugging
3. **Soft Deletes**: Consider future implementation (not in initial schema)
4. **Foreign Key Constraints**: Enforce referential integrity at database level
5. **Check Constraints**: Validate data at database level (status values, string lengths)
6. **Indexes**: Add indexes on frequently queried columns (user_id, status, created_at)
7. **Normalization**: Follow 3NF (Third Normal Form) to avoid data duplication

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│             users                   │
├─────────────────────────────────────┤
│ id               UUID (PK)          │
│ email            VARCHAR(255) UNIQUE│
│ name             VARCHAR(255)       │
│ email_verified   BOOLEAN            │
│ image            VARCHAR(500) NULL  │
│ created_at       TIMESTAMPTZ        │
│ updated_at       TIMESTAMPTZ        │
└─────────────────────────────────────┘
           │
           │ 1
           │
           │ has many
           │
           │ N
           ▼
┌─────────────────────────────────────┐
│             tasks                   │
├─────────────────────────────────────┤
│ id               UUID (PK)          │
│ user_id          UUID (FK)          │
│ title            VARCHAR(200)       │
│ description      TEXT NULL          │
│ status           VARCHAR(50)        │
│ priority         VARCHAR(50)        │
│ created_at       TIMESTAMPTZ        │
│ updated_at       TIMESTAMPTZ        │
│ completed_at     TIMESTAMPTZ NULL   │
└─────────────────────────────────────┘
```

---

## Entity Definitions

### 1. User Entity

Represents an authenticated user of the application. This schema is designed to be compatible with Better Auth (to be integrated in Feature 3).

**Table Name**: `users`

| Column         | Type             | Constraints                          | Description                                      |
|----------------|------------------|--------------------------------------|--------------------------------------------------|
| id             | UUID             | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the user                   |
| email          | VARCHAR(255)     | UNIQUE NOT NULL                      | User's email address (used for login)            |
| name           | VARCHAR(255)     | NOT NULL                             | User's display name                              |
| email_verified | BOOLEAN          | NOT NULL DEFAULT FALSE               | Whether email has been verified                  |
| image          | VARCHAR(500)     | NULL                                 | URL to user's profile image (for OAuth)          |
| created_at     | TIMESTAMPTZ      | NOT NULL DEFAULT NOW()               | When the user account was created                |
| updated_at     | TIMESTAMPTZ      | NOT NULL DEFAULT NOW()               | When the user account was last updated           |

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `email` (automatic with UNIQUE constraint)

**Notes**:
- The `image` field is nullable to support users without profile pictures
- `email_verified` will be used by Better Auth for email verification flow
- This schema is a minimal subset compatible with Better Auth; additional fields (password hash, OAuth tokens, sessions) will be added in Feature 3
- Passwords will NOT be stored in this table; Better Auth manages authentication data separately

**Future Extensions (Feature 3)**:
- Better Auth will add additional tables: `sessions`, `accounts`, `verification_tokens`
- Password hashing will be handled by Better Auth's internal schema

---

### 2. Task Entity

Represents a todo item belonging to a user. This is the core domain entity of the application.

**Table Name**: `tasks`

| Column       | Type         | Constraints                                    | Description                                 |
|--------------|--------------|------------------------------------------------|---------------------------------------------|
| id           | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid()         | Unique identifier for the task              |
| user_id      | UUID         | NOT NULL REFERENCES users(id) ON DELETE CASCADE | Owner of the task (foreign key)             |
| title        | VARCHAR(200) | NOT NULL CHECK (char_length(title) >= 1)       | Task title (required, 1-200 characters)     |
| description  | TEXT         | NULL                                           | Optional detailed description               |
| status       | VARCHAR(50)  | NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')) | Task completion status |
| priority     | VARCHAR(50)  | NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')) | Task priority level |
| created_at   | TIMESTAMPTZ  | NOT NULL DEFAULT NOW()                         | When the task was created                   |
| updated_at   | TIMESTAMPTZ  | NOT NULL DEFAULT NOW()                         | When the task was last updated              |
| completed_at | TIMESTAMPTZ  | NULL                                           | When the task was marked completed          |

**Indexes**:
- Primary key index on `id` (automatic)
- Index on `user_id` for fast user task lookups: `CREATE INDEX idx_tasks_user_id ON tasks(user_id)`
- Composite index on `user_id` and `status` for filtered queries: `CREATE INDEX idx_tasks_user_status ON tasks(user_id, status)`
- Index on `created_at` for sorting: `CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC)`

**Constraints**:
- Foreign key constraint on `user_id` with `ON DELETE CASCADE` (deleting a user deletes all their tasks)
- Check constraint on `status` to allow only 'pending' or 'completed'
- Check constraint on `priority` to allow only 'low', 'medium', or 'high'
- Check constraint on `title` to prevent empty strings

**Notes**:
- `description` is optional (NULL allowed) to support quick task entry
- `completed_at` is set when `status` changes to 'completed' (enforced at application level)
- Priority field is included for future features (filtering, sorting) but not used in initial setup
- UUIDs are generated at database level with `gen_random_uuid()` (PostgreSQL 13+)

**Future Extensions**:
- Feature 4: Add task creation via API
- Feature 5: Add task listing with filtering (by status, priority)
- Feature 6: Add task update functionality
- Feature 7: Add task deletion
- Feature 8: Add task completion toggle

---

## Database Schema (SQL)

### PostgreSQL Schema Definition

```sql
-- Enable UUID generation (PostgreSQL 13+)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    image VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL CHECK (char_length(title) >= 1),
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    priority VARCHAR(50) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for tasks table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Trigger to update updated_at timestamp (optional but recommended)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## SQLModel Definitions (Python)

### User Model

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class UserBase(SQLModel):
    """Base user schema (shared fields)"""
    email: str = Field(max_length=255, sa_column_kwargs={"unique": True})
    name: str = Field(max_length=255)
    email_verified: bool = Field(default=False)
    image: Optional[str] = Field(default=None, max_length=500)

class User(UserBase, table=True):
    """Database model for users table"""
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (defined when implementing task relationships)
    # tasks: list["Task"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    """Schema for creating a user (API request)"""
    pass

class UserResponse(UserBase):
    """Schema for user response (API response)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Task Model

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Literal

StatusType = Literal["pending", "completed"]
PriorityType = Literal["low", "medium", "high"]

class TaskBase(SQLModel):
    """Base task schema (shared fields)"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    status: StatusType = Field(default="pending")
    priority: PriorityType = Field(default="medium")

class Task(TaskBase, table=True):
    """Database model for tasks table"""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    # user: User = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    """Schema for creating a task (API request)"""
    # user_id will be extracted from authentication context
    pass

class TaskUpdate(SQLModel):
    """Schema for updating a task (API request)"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    status: Optional[StatusType] = Field(default=None)
    priority: Optional[PriorityType] = Field(default=None)

class TaskResponse(TaskBase):
    """Schema for task response (API response)"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
```

---

## TypeScript Types (Frontend)

These types will be auto-generated from the OpenAPI spec, but here's the expected structure:

```typescript
// Generated from OpenAPI spec
export interface User {
  id: string; // UUID as string
  email: string;
  name: string;
  email_verified: boolean;
  image: string | null;
  created_at: string; // ISO 8601 datetime
  updated_at: string;
}

export interface Task {
  id: string; // UUID as string
  user_id: string;
  title: string;
  description: string | null;
  status: 'pending' | 'completed';
  priority: 'low' | 'medium' | 'high';
  created_at: string; // ISO 8601 datetime
  updated_at: string;
  completed_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high';
}
```

---

## Alembic Migration Strategy

### Initial Migration

The initial Alembic migration will create both `users` and `tasks` tables:

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial schema: users and tasks tables"

# Review generated migration file in alembic/versions/
# Edit if necessary (add indexes, triggers)

# Apply migration
alembic upgrade head
```

### Example Migration File

```python
"""Initial schema: users and tasks tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('image', sa.String(500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(50), nullable=False, server_default='medium'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("char_length(title) >= 1", name='check_title_length'),
        sa.CheckConstraint("status IN ('pending', 'completed')", name='check_status_values'),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high')", name='check_priority_values'),
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_status', 'tasks', ['user_id', 'status'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], postgresql_ops={'created_at': 'DESC'})


def downgrade() -> None:
    # Drop tasks table (will also drop its indexes)
    op.drop_table('tasks')

    # Drop users table (will also drop its indexes)
    op.drop_table('users')
```

---

## Data Validation Rules

### User Validation

| Field          | Validation Rules                                                  |
|----------------|-------------------------------------------------------------------|
| email          | Must be valid email format (RFC 5322), max 255 chars             |
| name           | Required, 1-255 characters                                        |
| email_verified | Boolean (true/false)                                              |
| image          | Optional, must be valid URL if provided, max 500 chars           |

### Task Validation

| Field       | Validation Rules                                                   |
|-------------|--------------------------------------------------------------------|
| title       | Required, 1-200 characters, no leading/trailing whitespace         |
| description | Optional, no max length (TEXT field)                               |
| status      | Must be 'pending' or 'completed'                                   |
| priority    | Must be 'low', 'medium', or 'high'                                 |
| user_id     | Must reference existing user (foreign key constraint)              |

**Validation Layers**:
1. **Frontend**: React Hook Form + Zod for immediate user feedback
2. **API**: Pydantic schemas for request validation (FastAPI does this automatically)
3. **Database**: Check constraints, foreign keys, NOT NULL constraints

---

## Sample Data (for Testing)

### Seed Data SQL

```sql
-- Insert sample user
INSERT INTO users (id, email, name, email_verified, image) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'alice@example.com', 'Alice Smith', true, 'https://example.com/avatars/alice.jpg'),
('550e8400-e29b-41d4-a716-446655440001', 'bob@example.com', 'Bob Johnson', true, NULL);

-- Insert sample tasks for Alice
INSERT INTO tasks (id, user_id, title, description, status, priority) VALUES
('650e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Milk, eggs, bread, cheese', 'pending', 'high'),
('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Finish project report', NULL, 'pending', 'high'),
('650e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'Call dentist', 'Schedule cleaning appointment', 'completed', 'medium');

-- Insert sample tasks for Bob
INSERT INTO tasks (id, user_id, title, description, status, priority) VALUES
('650e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'Read book', 'The Pragmatic Programmer', 'pending', 'low');

-- Update completed task
UPDATE tasks SET completed_at = NOW() WHERE status = 'completed';
```

---

## Migration Checklist

When applying this schema to Neon PostgreSQL:

- [ ] Create `.env` file with Neon DATABASE_URL
- [ ] Verify PostgreSQL version supports `gen_random_uuid()` (PostgreSQL 13+)
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` with async engine and SQLModel metadata
- [ ] Generate initial migration: `alembic revision --autogenerate -m "Initial schema"`
- [ ] Review generated migration file, add missing indexes/triggers
- [ ] Apply migration: `alembic upgrade head`
- [ ] Verify tables created: `psql $DATABASE_URL -c "\dt"`
- [ ] Verify indexes created: `psql $DATABASE_URL -c "\di"`
- [ ] Insert seed data for testing (optional)
- [ ] Test foreign key constraints (try to insert task with invalid user_id)
- [ ] Test check constraints (try to insert task with invalid status)

---

## Future Considerations

### Potential Schema Extensions (Out of Scope for Feature 2)

1. **Soft Deletes**: Add `deleted_at` column for soft delete functionality
2. **Tags**: Add `tags` table with many-to-many relationship to tasks
3. **Categories**: Add `categories` table with one-to-many relationship to tasks
4. **Attachments**: Add `attachments` table to store file references
5. **Comments**: Add `comments` table for task notes/discussion
6. **Subtasks**: Add self-referential foreign key `parent_task_id` to tasks table
7. **Due Dates**: Add `due_date` column to tasks table
8. **Recurrence**: Add recurrence rules (daily, weekly, monthly)
9. **Sharing**: Add `task_shares` table for collaborative tasks
10. **Audit Log**: Add `audit_log` table to track all changes

These extensions will be evaluated in future features based on user needs.

---

## Summary

This data model provides:

- **User entity**: Compatible with Better Auth, supports profile information
- **Task entity**: Core domain model with status, priority, timestamps
- **UUID primary keys**: Security best practice
- **Foreign key constraints**: Data integrity enforcement
- **Check constraints**: Database-level validation
- **Indexes**: Query performance optimization
- **Timestamps**: Full audit trail
- **Migration strategy**: Alembic-based schema versioning

The schema is designed for extensibility while maintaining simplicity for the initial setup phase.
