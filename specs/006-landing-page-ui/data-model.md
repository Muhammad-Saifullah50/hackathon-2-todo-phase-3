# Data Model: Landing Page and UI Enhancement Suite

**Feature**: `006-landing-page-ui`
**Date**: 2025-12-20
**Status**: Phase 1 - Design

## Overview

This document defines the extended data model for the Landing Page and UI Enhancement Suite feature. It builds on the existing `Task` and `User` models by adding support for due dates, tags, subtasks, templates, recurring patterns, and user preferences.

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│     User        │
└────────┬────────┘
         │
         │ 1:N
         │
         ├──────────────────────────────────────────────────────────┐
         │                                                          │
         ▼                                                          ▼
┌─────────────────┐                                       ┌──────────────────┐
│     Task        │◄──────────┐                           │ UserPreferences  │
│ (Extended)      │            │                          └──────────────────┘
└────┬────┬───────┘            │
     │    │                    │ N:M
     │    │                    │
     │    │            ┌───────┴────────┐
     │    │            │   TaskTag      │ (Join table)
     │    │            │                │
     │    │            └───────┬────────┘
     │    │                    │
     │    │                    │ N:1
     │    │                    ▼
     │    │            ┌────────────────┐
     │    │            │      Tag       │
     │    │            └────────────────┘
     │    │
     │    │ 1:N
     │    └───────────►┌─────────────────┐
     │                 │    Subtask      │
     │                 └─────────────────┘
     │
     │ 1:1 (nullable)
     └────────────────►┌──────────────────────┐
                       │ RecurrencePattern    │
                       └──────────────────────┘

┌──────────────────┐
│  TaskTemplate    │
└──────────────────┘
         │
         │ N:M
         ▼
┌──────────────────┐
│ TemplateTag      │ (Join table)
└──────────────────┘
         │
         │ N:1
         ▼
┌──────────────────┐
│      Tag         │
└──────────────────┘

┌──────────────────┐
│ ViewPreference   │
└──────────────────┘
```

---

## Entities

### 1. Task (Extended)

**Purpose**: Represents a user's todo item with extended attributes for due dates, tags, notes, and recurrence.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of the task |
| `title` | VARCHAR(200) | NOT NULL, LENGTH(1-200) | Task title |
| `description` | TEXT | NULLABLE | Optional task description |
| `status` | VARCHAR(50) | NOT NULL, CHECK IN ('pending', 'in_progress', 'completed'), DEFAULT 'pending' | Task status |
| `priority` | VARCHAR(50) | NOT NULL, CHECK IN ('low', 'medium', 'high'), DEFAULT 'medium' | Task priority |
| `due_date` | TIMESTAMP WITH TIME ZONE | NULLABLE | When task should be completed (UTC) |
| `notes` | TEXT | NULLABLE | Rich text notes (markdown) |
| `manual_order` | INTEGER | NULLABLE, DEFAULT NULL | User-defined sort order |
| `template_id` | UUID | FOREIGN KEY (task_templates.id), NULLABLE | Template used to create this task |
| `recurrence_pattern_id` | UUID | FOREIGN KEY (recurrence_patterns.id), NULLABLE | Recurrence configuration |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| `completed_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Completion timestamp |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Soft delete timestamp |

**Relationships**:
- `user_id` → `users.id` (N:1) - Each task belongs to one user
- `template_id` → `task_templates.id` (N:1) - Optional template reference
- `recurrence_pattern_id` → `recurrence_patterns.id` (1:1) - Optional recurrence config
- `tags` → `tags` (N:M via `task_tags`) - Multiple tags per task
- `subtasks` → `subtasks` (1:N) - Multiple subtasks per task

**Indexes**:
- `idx_tasks_user_id` ON `(user_id, deleted_at)` WHERE `deleted_at IS NULL`
- `idx_tasks_due_date` ON `(due_date)` WHERE `deleted_at IS NULL AND due_date IS NOT NULL`
- `idx_tasks_status` ON `(status, user_id)` WHERE `deleted_at IS NULL`
- `idx_tasks_manual_order` ON `(user_id, manual_order)` WHERE `manual_order IS NOT NULL`

**State Transitions**:
```
pending → in_progress → completed
   ↑                        ↓
   └────────────────────────┘
   (reopen task)
```

**Business Rules**:
1. When `status` changes to `completed`, set `completed_at` to current timestamp
2. When `status` changes from `completed` to `pending`/`in_progress`, clear `completed_at`
3. If task has `recurrence_pattern_id` and is completed, create new instance with next due date
4. Soft delete: Set `deleted_at` instead of physical deletion (existing pattern)

---

### 2. Tag

**Purpose**: Represents a categorization label created by users to organize tasks.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of the tag |
| `name` | VARCHAR(50) | NOT NULL, LENGTH(1-50) | Tag name |
| `color` | VARCHAR(7) | NOT NULL, PATTERN(#[0-9A-Fa-f]{6}) | Hex color code |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `user_id` → `users.id` (N:1) - Each tag belongs to one user
- `tasks` → `tasks` (N:M via `task_tags`) - Multiple tasks per tag

**Indexes**:
- `idx_tags_user_id` ON `(user_id, name)` - Unique tag names per user
- UNIQUE constraint on `(user_id, name)` - Prevent duplicate tag names for same user

**Business Rules**:
1. Tag names must be unique per user (case-insensitive)
2. When tag is deleted, remove all associations in `task_tags` (cascade)
3. When tag is edited (name or color), changes cascade to all tasks
4. Default colors: Provide palette of 12 distinct colors for user selection

---

### 3. TaskTag (Join Table)

**Purpose**: Many-to-many relationship between tasks and tags.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `task_id` | UUID | FOREIGN KEY (tasks.id), NOT NULL | Task reference |
| `tag_id` | UUID | FOREIGN KEY (tags.id), NOT NULL | Tag reference |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Association timestamp |

**Relationships**:
- `task_id` → `tasks.id` (N:1, CASCADE ON DELETE)
- `tag_id` → `tags.id` (N:1, CASCADE ON DELETE)

**Indexes**:
- PRIMARY KEY `(task_id, tag_id)` - Composite primary key
- `idx_task_tags_tag_id` ON `(tag_id)` - For reverse lookup (all tasks with tag X)

**Business Rules**:
1. Delete association when task or tag is deleted (cascade)
2. Maximum 10 tags per task (enforced at application layer)

---

### 4. Subtask

**Purpose**: Represents a child checklist item belonging to a parent task.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `task_id` | UUID | FOREIGN KEY (tasks.id), NOT NULL | Parent task reference |
| `description` | VARCHAR(200) | NOT NULL, LENGTH(1-200) | Subtask description |
| `is_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `order_index` | INTEGER | NOT NULL | Display order (0-indexed) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `task_id` → `tasks.id` (N:1, CASCADE ON DELETE) - Each subtask belongs to one task

**Indexes**:
- `idx_subtasks_task_id` ON `(task_id, order_index)` - For ordered retrieval

**Business Rules**:
1. When all subtasks for a task are `is_completed=true`, auto-mark parent task as `completed`
2. When subtask is deleted, recalculate parent task progress
3. `order_index` determines display order, supports drag-and-drop reordering
4. Maximum 50 subtasks per task (enforced at application layer)

---

### 5. RecurrencePattern

**Purpose**: Defines how a task repeats (daily, weekly, monthly, custom).

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `task_id` | UUID | FOREIGN KEY (tasks.id), UNIQUE, NOT NULL | Task reference (1:1) |
| `frequency` | VARCHAR(50) | NOT NULL, CHECK IN ('daily', 'weekly', 'monthly', 'custom') | Recurrence type |
| `interval` | INTEGER | NOT NULL, DEFAULT 1, CHECK > 0 | Repeat every N days/weeks/months |
| `days_of_week` | JSON | NULLABLE | For weekly: [0-6] array (0=Sunday) |
| `day_of_month` | INTEGER | NULLABLE, CHECK BETWEEN 1 AND 31 | For monthly: day of month |
| `end_date` | TIMESTAMP WITH TIME ZONE | NULLABLE | Optional end date for recurrence |
| `next_occurrence_date` | TIMESTAMP WITH TIME ZONE | NOT NULL | Next scheduled date |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `task_id` → `tasks.id` (1:1, CASCADE ON DELETE) - One recurrence pattern per task

**Indexes**:
- `idx_recurrence_next_occurrence` ON `(next_occurrence_date)` - For finding due recurrences

**Business Rules**:
1. When parent task is completed, create new task instance and update `next_occurrence_date`
2. If `end_date` is reached, stop creating new instances
3. `days_of_week` is JSON array for weekly (e.g., `[1, 3, 5]` for Mon/Wed/Fri)
4. Calculate `next_occurrence_date` based on `frequency` and `interval`

---

### 6. TaskTemplate

**Purpose**: Represents a reusable task structure to speed up task creation.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of the template |
| `name` | VARCHAR(100) | NOT NULL, LENGTH(1-100) | Template name |
| `title_template` | VARCHAR(200) | NOT NULL | Default title for tasks created from this template |
| `description_template` | TEXT | NULLABLE | Default description |
| `default_priority` | VARCHAR(50) | NOT NULL, CHECK IN ('low', 'medium', 'high'), DEFAULT 'medium' | Default priority |
| `default_subtasks` | JSON | NULLABLE | Array of subtask descriptions |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `user_id` → `users.id` (N:1) - Each template belongs to one user
- `tags` → `tags` (N:M via `template_tags`) - Default tags for template
- `tasks` → `tasks` (1:N via `tasks.template_id`) - Tasks created from this template

**Indexes**:
- `idx_templates_user_id` ON `(user_id, name)` - For listing user's templates

**Business Rules**:
1. Templates are user-specific (not shared between users)
2. When creating task from template, copy all fields but allow modification before save
3. `default_subtasks` is JSON array: `["Subtask 1", "Subtask 2"]`
4. Maximum 50 templates per user (enforced at application layer)

---

### 7. TemplateTag (Join Table)

**Purpose**: Many-to-many relationship between templates and tags (default tags for template).

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `template_id` | UUID | FOREIGN KEY (task_templates.id), NOT NULL | Template reference |
| `tag_id` | UUID | FOREIGN KEY (tags.id), NOT NULL | Tag reference |

**Relationships**:
- `template_id` → `task_templates.id` (N:1, CASCADE ON DELETE)
- `tag_id` → `tags.id` (N:1, CASCADE ON DELETE)

**Indexes**:
- PRIMARY KEY `(template_id, tag_id)` - Composite primary key
- `idx_template_tags_tag_id` ON `(tag_id)` - For reverse lookup

---

### 8. UserPreferences

**Purpose**: Stores user-specific UI preferences and settings.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), UNIQUE, NOT NULL | User reference (1:1) |
| `theme_name` | VARCHAR(50) | NOT NULL, DEFAULT 'system' | Selected theme (Ocean, Sunset, Forest, Monochrome, system) |
| `accent_color` | VARCHAR(7) | NOT NULL, DEFAULT '#3b82f6' | Custom accent color (hex) |
| `default_view` | VARCHAR(50) | NOT NULL, DEFAULT 'list', CHECK IN ('list', 'grid', 'kanban', 'calendar') | Preferred task view |
| `onboarding_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether user finished onboarding tour |
| `keyboard_shortcuts_enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether keyboard shortcuts are active |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `user_id` → `users.id` (1:1) - One preference record per user

**Indexes**:
- UNIQUE constraint on `user_id` - One preference record per user

**Business Rules**:
1. Auto-create preference record when user signs up (default values)
2. Preferences sync across devices (stored in database, not localStorage)
3. `theme_name='system'` respects OS light/dark mode preference

---

### 9. ViewPreference

**Purpose**: Stores saved filter/sort configurations (smart views like "High Priority This Week").

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of the view |
| `view_name` | VARCHAR(100) | NOT NULL, LENGTH(1-100) | Name of saved view |
| `filter_configuration` | JSON | NOT NULL | Filter settings (status, priority, tags, due date range) |
| `sort_configuration` | JSON | NOT NULL | Sort settings (sort_by, sort_order) |
| `is_default` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this is the default view |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relationships**:
- `user_id` → `users.id` (N:1) - Each view belongs to one user

**Indexes**:
- `idx_view_preferences_user_id` ON `(user_id, view_name)` - For listing user's views
- UNIQUE constraint on `(user_id, view_name)` - Prevent duplicate view names

**Business Rules**:
1. Only one view can be `is_default=true` per user
2. When setting new default, unset previous default
3. `filter_configuration` example: `{"status": "pending", "priority": ["high", "medium"], "tags": ["urgent"], "due_date_range": "this_week"}`
4. `sort_configuration` example: `{"sort_by": "due_date", "sort_order": "asc"}`

---

## Schema Changes

### Migration 1: Add Due Date to Tasks

**File**: `backend/alembic/versions/YYYYMMDD_add_due_date.py`

**Changes**:
```sql
ALTER TABLE tasks
ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;

CREATE INDEX idx_tasks_due_date
ON tasks(due_date)
WHERE deleted_at IS NULL AND due_date IS NOT NULL;
```

**Rollback**:
```sql
DROP INDEX idx_tasks_due_date;
ALTER TABLE tasks DROP COLUMN due_date;
```

---

### Migration 2: Add Notes and Manual Order to Tasks

**File**: `backend/alembic/versions/YYYYMMDD_add_notes_manual_order.py`

**Changes**:
```sql
ALTER TABLE tasks
ADD COLUMN notes TEXT,
ADD COLUMN manual_order INTEGER,
ADD COLUMN template_id UUID REFERENCES task_templates(id) ON DELETE SET NULL,
ADD COLUMN recurrence_pattern_id UUID REFERENCES recurrence_patterns(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_manual_order
ON tasks(user_id, manual_order)
WHERE manual_order IS NOT NULL;
```

**Rollback**:
```sql
DROP INDEX idx_tasks_manual_order;
ALTER TABLE tasks
DROP COLUMN notes,
DROP COLUMN manual_order,
DROP COLUMN template_id,
DROP COLUMN recurrence_pattern_id;
```

---

### Migration 3: Create Tags Table

**File**: `backend/alembic/versions/YYYYMMDD_create_tags_table.py`

**Changes**:
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL CHECK (char_length(name) >= 1 AND char_length(name) <= 50),
    color VARCHAR(7) NOT NULL CHECK (color ~ '^#[0-9A-Fa-f]{6}$'),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

CREATE INDEX idx_tags_user_id ON tags(user_id, name);

-- Join table for task-tag relationship
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

**Rollback**:
```sql
DROP TABLE task_tags;
DROP TABLE tags;
```

---

### Migration 4: Create Subtasks Table

**File**: `backend/alembic/versions/YYYYMMDD_create_subtasks_table.py`

**Changes**:
```sql
CREATE TABLE subtasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    description VARCHAR(200) NOT NULL CHECK (char_length(description) >= 1 AND char_length(description) <= 200),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subtasks_task_id ON subtasks(task_id, order_index);
```

**Rollback**:
```sql
DROP TABLE subtasks;
```

---

### Migration 5: Create Recurrence Patterns Table

**File**: `backend/alembic/versions/YYYYMMDD_create_recurrence_patterns_table.py`

**Changes**:
```sql
CREATE TABLE recurrence_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID UNIQUE NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    frequency VARCHAR(50) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'custom')),
    interval INTEGER NOT NULL DEFAULT 1 CHECK (interval > 0),
    days_of_week JSON,
    day_of_month INTEGER CHECK (day_of_month BETWEEN 1 AND 31),
    end_date TIMESTAMP WITH TIME ZONE,
    next_occurrence_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recurrence_next_occurrence ON recurrence_patterns(next_occurrence_date);
```

**Rollback**:
```sql
DROP TABLE recurrence_patterns;
```

---

### Migration 6: Create Task Templates Table

**File**: `backend/alembic/versions/YYYYMMDD_create_task_templates_table.py`

**Changes**:
```sql
CREATE TABLE task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL CHECK (char_length(name) >= 1 AND char_length(name) <= 100),
    title_template VARCHAR(200) NOT NULL,
    description_template TEXT,
    default_priority VARCHAR(50) NOT NULL DEFAULT 'medium' CHECK (default_priority IN ('low', 'medium', 'high')),
    default_subtasks JSON,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

CREATE INDEX idx_task_templates_user_id ON task_templates(user_id, name);

-- Join table for template-tag relationship
CREATE TABLE template_tags (
    template_id UUID NOT NULL REFERENCES task_templates(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (template_id, tag_id)
);

CREATE INDEX idx_template_tags_tag_id ON template_tags(tag_id);
```

**Rollback**:
```sql
DROP TABLE template_tags;
DROP TABLE task_templates;
```

---

### Migration 7: Create User Preferences Table

**File**: `backend/alembic/versions/YYYYMMDD_create_user_preferences_table.py`

**Changes**:
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    theme_name VARCHAR(50) NOT NULL DEFAULT 'system',
    accent_color VARCHAR(7) NOT NULL DEFAULT '#3b82f6' CHECK (accent_color ~ '^#[0-9A-Fa-f]{6}$'),
    default_view VARCHAR(50) NOT NULL DEFAULT 'list' CHECK (default_view IN ('list', 'grid', 'kanban', 'calendar')),
    onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
    keyboard_shortcuts_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

**Rollback**:
```sql
DROP TABLE user_preferences;
```

---

### Migration 8: Create View Preferences Table

**File**: `backend/alembic/versions/YYYYMMDD_create_view_preferences_table.py`

**Changes**:
```sql
CREATE TABLE view_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    view_name VARCHAR(100) NOT NULL CHECK (char_length(view_name) >= 1 AND char_length(view_name) <= 100),
    filter_configuration JSON NOT NULL,
    sort_configuration JSON NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, view_name)
);

CREATE INDEX idx_view_preferences_user_id ON view_preferences(user_id, view_name);
```

**Rollback**:
```sql
DROP TABLE view_preferences;
```

---

## Data Validation Rules

### Task Validation

```python
# Pydantic schema (backend)
from pydantic import BaseModel, Field, validator
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    priority: Literal['low', 'medium', 'high'] = 'medium'
    due_date: datetime | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)
    notes: str | None = None

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.now(timezone.utc):
            # Allow past dates (user may be logging completed tasks retroactively)
            pass
        return v
```

```typescript
// Zod schema (frontend)
import { z } from 'zod';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(500).nullable(),
  priority: z.enum(['low', 'medium', 'high']),
  due_date: z.date().nullable(),
  tags: z.array(z.string()).max(10),
  notes: z.string().nullable()
});
```

### Tag Validation

```python
class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(pattern=r'^#[0-9A-Fa-f]{6}$')

    @validator('name')
    def validate_name(cls, v):
        # Case-insensitive uniqueness enforced at DB level
        return v.strip()
```

### Subtask Validation

```python
class SubtaskCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    order_index: int = Field(ge=0)

    @validator('description')
    def validate_description(cls, v):
        return v.strip()
```

### Recurrence Pattern Validation

```python
class RecurrencePatternCreate(BaseModel):
    frequency: Literal['daily', 'weekly', 'monthly', 'custom']
    interval: int = Field(ge=1, le=365)  # Max 1 year interval
    days_of_week: list[int] | None = Field(None)  # [0-6] for Sunday-Saturday
    day_of_month: int | None = Field(None, ge=1, le=31)
    end_date: datetime | None = None

    @validator('days_of_week')
    def validate_days_of_week(cls, v, values):
        if values.get('frequency') == 'weekly' and not v:
            raise ValueError('days_of_week required for weekly recurrence')
        if v and (min(v) < 0 or max(v) > 6):
            raise ValueError('days_of_week must be 0-6')
        return v

    @validator('day_of_month')
    def validate_day_of_month(cls, v, values):
        if values.get('frequency') == 'monthly' and not v:
            raise ValueError('day_of_month required for monthly recurrence')
        return v
```

---

## Query Patterns

### Get Tasks with Tags and Subtasks

```python
# Service layer (task_service.py)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_tasks_with_relations(
    db: AsyncSession,
    user_id: str,
    filters: TaskFilters
) -> list[Task]:
    # Eager load relationships to avoid N+1 queries
    query = (
        select(Task)
        .where(Task.user_id == user_id, Task.deleted_at.is_(None))
        .options(
            selectinload(Task.tags),
            selectinload(Task.subtasks),
            selectinload(Task.recurrence_pattern)
        )
    )

    # Apply filters
    if filters.status:
        query = query.where(Task.status == filters.status)
    if filters.priority:
        query = query.where(Task.priority == filters.priority)
    if filters.due_date_range == 'today':
        query = query.where(
            func.date(Task.due_date) == func.date(func.now())
        )
    if filters.tag_ids:
        query = query.join(TaskTag).where(TaskTag.tag_id.in_(filters.tag_ids))

    # Apply sorting
    if filters.sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc().nullslast())
    elif filters.sort_by == 'created_at':
        query = query.order_by(Task.created_at.desc())
    elif filters.sort_by == 'manual_order':
        query = query.order_by(Task.manual_order.asc().nullslast())

    # Pagination
    offset = (filters.page - 1) * filters.limit
    query = query.offset(offset).limit(filters.limit)

    result = await db.execute(query)
    return result.scalars().all()
```

### Search Tasks by Text

```python
async def search_tasks(
    db: AsyncSession,
    user_id: str,
    search_query: str
) -> list[Task]:
    # Full-text search across title, description, notes
    query = (
        select(Task)
        .where(
            Task.user_id == user_id,
            Task.deleted_at.is_(None),
            or_(
                Task.title.ilike(f'%{search_query}%'),
                Task.description.ilike(f'%{search_query}%'),
                Task.notes.ilike(f'%{search_query}%')
            )
        )
    )

    result = await db.execute(query)
    return result.scalars().all()
```

### Get Task Statistics

```python
async def get_task_statistics(
    db: AsyncSession,
    user_id: str
) -> TaskStatistics:
    # Aggregate queries for dashboard
    stats = await db.execute(
        select(
            func.count(Task.id).filter(Task.status == 'pending').label('total_pending'),
            func.count(Task.id).filter(Task.status == 'completed').label('total_completed'),
            func.count(Task.id).filter(
                Task.due_date < func.now(),
                Task.status != 'completed'
            ).label('total_overdue'),
            func.count(Task.id).filter(
                func.date(Task.completed_at) == func.date(func.now())
            ).label('completed_today')
        )
        .where(Task.user_id == user_id, Task.deleted_at.is_(None))
    )

    return stats.one()
```

---

## Data Integrity Constraints

### Database-Level Constraints

1. **Foreign Keys**: All references use `ON DELETE CASCADE` or `ON DELETE SET NULL`
2. **Check Constraints**: Enum fields validated at DB level
3. **Unique Constraints**: Prevent duplicate tag names per user, template names per user
4. **Length Constraints**: Enforce max lengths for title, description, etc.
5. **Pattern Constraints**: Validate hex color codes (`^#[0-9A-Fa-f]{6}$`)

### Application-Level Constraints

1. **Tag Limit**: Maximum 10 tags per task (enforced in service layer)
2. **Subtask Limit**: Maximum 50 subtasks per task
3. **Template Limit**: Maximum 50 templates per user
4. **View Limit**: Maximum 20 saved views per user
5. **Search Query**: Maximum 100 characters (prevent abuse)

---

## Performance Considerations

### Database Indexes

**Critical Indexes** (must add):
- `idx_tasks_user_id` - Already exists
- `idx_tasks_due_date` - For date-based filtering
- `idx_tasks_manual_order` - For custom ordering
- `idx_task_tags_tag_id` - For reverse tag lookup
- `idx_subtasks_task_id` - For subtask retrieval

**Composite Indexes**:
- `(user_id, deleted_at)` - For active task queries
- `(user_id, status)` - For status filtering
- `(task_id, order_index)` - For ordered subtasks

### Query Optimization

1. **Eager Loading**: Use `selectinload()` for relationships to avoid N+1 queries
2. **Pagination**: Always paginate lists (default 20 items, max 100)
3. **Caching**: TanStack Query caches API responses (30s stale time)
4. **Debouncing**: Search queries debounced 300ms on frontend

---

## Security Considerations

### Authorization Rules

1. **Resource Ownership**: Users can only access their own tasks, tags, templates, preferences
2. **API Validation**: All endpoints validate `user_id` matches authenticated user
3. **SQL Injection**: ORM (SQLModel) prevents SQL injection via parameterized queries
4. **XSS Prevention**: React escapes by default, sanitize markdown notes if rendered as HTML
5. **Rate Limiting**: Search/filter endpoints limited to 100 requests/min per user

### Data Privacy

1. **Soft Delete**: Tasks remain in database 30 days after deletion (recovery window)
2. **Permanent Delete**: After 30 days, purge soft-deleted tasks (cron job)
3. **User Data Export**: Support GDPR-compliant data export (future)
4. **User Deletion**: Cascade delete all user data when account is deleted

---

## Frontend Type Definitions

### Extended Task Type

```typescript
// frontend/lib/types/task.ts
export type TaskStatus = 'pending' | 'in_progress' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Tag {
  id: string;
  name: string;
  color: string;
  created_at: string;
}

export interface Subtask {
  id: string;
  description: string;
  is_completed: boolean;
  order_index: number;
}

export interface RecurrencePattern {
  id: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  interval: number;
  days_of_week?: number[];
  day_of_month?: number;
  end_date?: string;
  next_occurrence_date: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  notes: string | null;
  manual_order: number | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  deleted_at: string | null;
  tags: Tag[];
  subtasks: Subtask[];
  recurrence_pattern: RecurrencePattern | null;
}
```

---

## Next Steps

✅ **Phase 0 Complete** - All technology decisions documented
✅ **Data Model Defined** - All entities, relationships, migrations specified

➡️ **Next**: Create API contracts (contracts/*.yaml)
