# Data Model: Task Creation

**Feature**: 004-task-creation
**Date**: 2025-12-20
**Source**: Extracted from spec.md requirements and existing database schema

## Entity Overview

This feature interacts with two existing entities:
1. **Task** (primary entity - modified)
2. **User** (existing, read-only for this feature)

---

## Entities

### Task

**Description**: Represents a todo item owned by a user. This is the core domain entity modified by this feature.

**Table**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, DEFAULT gen_random_uuid() | Unique identifier |
| `title` | VARCHAR(100) | NOT NULL, LENGTH >= 1 | Task summary (1-100 chars, 1-50 words) |
| `description` | VARCHAR(500) | NULLABLE | Detailed information (0-500 chars) |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'pending', CHECK IN ('pending', 'completed') | Completion state |
| `priority` | VARCHAR(50) | NOT NULL, DEFAULT 'medium', CHECK IN ('low', 'medium', 'high') | Importance level |
| `user_id` | VARCHAR | NOT NULL, FOREIGN KEY → users(id), INDEX | Owner reference (Better Auth user ID) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp (UTC) |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Last modification timestamp (UTC) |
| `completed_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Completion timestamp (UTC, null for pending tasks) |

**Indexes**:
- `PRIMARY KEY (id)` - Primary key index
- `INDEX idx_tasks_user_id (user_id)` - Query tasks by user
- `INDEX idx_tasks_status (status)` - Filter by status
- `INDEX idx_tasks_created_at DESC (created_at)` - Sort by creation date

**Relationships**:
- **Many-to-One with User**: Each task belongs to exactly one user
  - Foreign key: `task.user_id → user.id`
  - On delete: CASCADE (when user is deleted, all their tasks are deleted)

**Constraints**:
- Title cannot be empty (min_length=1)
- Title max 100 characters
- Description max 500 characters when provided
- Status must be 'pending' or 'completed'
- Priority must be 'low', 'medium', or 'high'
- user_id must reference existing user

**State Transitions**:
- Created → status='pending', completed_at=null
- (Not handled in this feature: pending ↔ completed via Feature 7)

**Validation Rules** (Application Layer):
- Title: 1-100 characters AND 1-50 words (split by whitespace)
- Description: 0-500 characters (optional)
- Priority: LOW | MEDIUM | HIGH (defaults to MEDIUM if not provided)
- Status: NOT accepted in create request (always PENDING)
- Leading/trailing whitespace is trimmed before saving
- Empty description strings are converted to null

---

### User

**Description**: Represents an authenticated user. Managed by Better Auth (Feature 3). Read-only for this feature.

**Table**: `user`

**Fields Used by This Feature**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | VARCHAR | Primary key, user identifier from Better Auth |
| `email` | VARCHAR(255) | User's email address |
| `name` | VARCHAR | User's display name (optional) |

**Relationship to Task**:
- **One-to-Many**: A user can have many tasks
  - Referenced by `task.user_id`

**Access Pattern**:
- Read user ID from JWT token via `get_current_user()` dependency
- User ID is automatically set on task creation (never accepted from request)

---

## Request/Response Schemas

### TaskCreate (Request Schema)

**Purpose**: Validates and parses task creation requests

**Fields**:

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| `title` | string | Yes | 1-100 chars, 1-50 words, trimmed | N/A |
| `description` | string \| null | No | 0-500 chars, trimmed, empty→null | null |
| `priority` | "LOW" \| "MEDIUM" \| "HIGH" | No | Enum validation | "MEDIUM" |

**Validation Logic**:
```python
@field_validator('title')
def validate_title(cls, v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError('Title cannot be empty')
    if len(v) > 100:
        raise ValueError('Title must be 100 characters or less')
    words = re.split(r'\s+', v)
    if len(words) > 50:
        raise ValueError('Title must be 50 words or less')
    return v

@field_validator('description')
def validate_description(cls, v: str | None) -> str | None:
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None
    if len(v) > 500:
        raise ValueError('Description must be 500 characters or less')
    return v
```

**TypeScript Equivalent** (Frontend):
```typescript
const createTaskSchema = z.object({
  title: z.string()
    .min(1, "Title is required")
    .max(100, "Title must be 100 characters or less")
    .refine(
      (val) => val.trim().split(/\s+/).length <= 50,
      "Title must be 50 words or less"
    ),
  description: z.string()
    .max(500, "Description must be 500 characters or less")
    .optional()
    .nullable(),
  priority: z.enum(["LOW", "MEDIUM", "HIGH"]).optional(),
});
```

**Notes**:
- `status` is NOT included (always PENDING)
- `user_id` is NOT included (extracted from JWT)
- `id` and timestamps are NOT included (system-generated)

---

### TaskResponse (Response Schema)

**Purpose**: Returns complete task data to client

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (string) | Task identifier |
| `title` | string | Task title |
| `description` | string \| null | Task description (nullable) |
| `status` | "pending" \| "completed" | Completion state |
| `priority` | "low" \| "medium" \| "high" | Importance level |
| `user_id` | string | Owner user ID |
| `created_at` | string (ISO 8601) | Creation timestamp |
| `updated_at` | string (ISO 8601) | Last modification timestamp |
| `completed_at` | string (ISO 8601) \| null | Completion timestamp (null for pending) |

**Example**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "priority": "medium",
  "user_id": "user_abc123",
  "created_at": "2025-12-20T10:30:00Z",
  "updated_at": "2025-12-20T10:30:00Z",
  "completed_at": null
}
```

**TypeScript Type** (Generated from OpenAPI):
```typescript
export interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  status: "pending" | "completed";
  priority: "low" | "medium" | "high";
  user_id: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}
```

---

## API Response Envelope

All responses use StandardizedResponse wrapper (existing pattern from Feature 2):

### Success Response (201 Created)

```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": "...",
    "title": "...",
    ...
  }
}
```

### Error Response (400 Bad Request - Validation)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data"
  },
  "details": [
    {
      "field": "title",
      "message": "Title must be 50 words or less"
    }
  ]
}
```

### Error Response (401 Unauthorized)

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

### Error Response (500 Internal Server Error)

```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Failed to create task. Please try again later."
  }
}
```

---

## Database Migration

**Migration Required**: No schema changes (Task table already exists from Feature 2)

**Validation**: Confirm existing Task model matches requirements:
- ✅ `title` field: VARCHAR(100) with min_length=1
- ✅ `description` field: VARCHAR(500), nullable
- ✅ `priority` field: VARCHAR(50) with default='medium'
- ✅ `status` field: VARCHAR(50) with default='pending'
- ✅ All timestamp fields exist with proper defaults

**If Schema Mismatch Exists**: Generate Alembic migration to add missing constraints

---

## Entity Lifecycle (This Feature)

```
1. User submits task creation form
   ↓
2. Frontend validates (Zod schema)
   ↓
3. POST /api/v1/tasks with { title, description?, priority? }
   ↓
4. Backend validates (Pydantic TaskCreate)
   ↓
5. Extract user_id from JWT token
   ↓
6. Create Task instance:
   - id: auto-generated UUID
   - title: trimmed input
   - description: trimmed input or null
   - status: 'pending' (forced)
   - priority: input or 'medium' (default)
   - user_id: from JWT
   - created_at: NOW()
   - updated_at: NOW()
   - completed_at: null
   ↓
7. Insert to database (single transaction)
   ↓
8. Refresh from database (get generated fields)
   ↓
9. Return TaskResponse wrapped in StandardizedResponse
   ↓
10. Frontend updates cache (optimistic update or refetch)
```

---

## Data Access Patterns

### Create Task

**SQL (Simplified)**:
```sql
INSERT INTO tasks (
    id, title, description, status, priority, user_id, created_at, updated_at, completed_at
) VALUES (
    gen_random_uuid(), 'Buy groceries', 'Milk, eggs, bread', 'pending', 'medium', 'user_abc123', NOW(), NOW(), NULL
)
RETURNING *;
```

**SQLModel (Actual Implementation)**:
```python
task = Task(
    title=task_data.title,
    description=task_data.description,
    status=TaskStatus.PENDING,
    priority=task_data.priority or TaskPriority.MEDIUM,
    user_id=user_id,
)
session.add(task)
await session.commit()
await session.refresh(task)
return task
```

**Performance Considerations**:
- Single INSERT statement (O(1) operation)
- No joins required for creation
- Indexes not used during insert (only for queries)
- Expected latency: <50ms (database write + network)

---

## Security Considerations

### Authorization

- **User Isolation**: user_id is ALWAYS set from authenticated JWT token
- **No Cross-User Access**: Users cannot create tasks for other users
- **Input Sanitization**: All inputs are validated and trimmed before database insertion

### Data Integrity

- **Atomic Operations**: Task creation is a single database transaction
- **Foreign Key Enforcement**: user_id must reference existing user (database constraint)
- **Default Values**: status and priority have safe defaults (prevents null issues)

### Validation Layers

1. **Frontend** (Zod): User-friendly error messages, prevents unnecessary API calls
2. **Backend** (Pydantic): Security layer, prevents malicious requests
3. **Database** (Constraints): Last line of defense, prevents data corruption

---

## Notes

- Task entity already exists from Feature 2 (Database Setup)
- This feature only implements CREATE operation (POST endpoint)
- Other operations (read, update, delete, toggle status) are separate features (5, 6, 7, 8)
- No changes to User entity (read-only access via JWT)
- All timestamps use UTC with timezone information
- Frontend is responsible for displaying timestamps in user's local timezone
