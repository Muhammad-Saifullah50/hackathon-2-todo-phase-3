# Implementation Plan: Task Management Operations

**Branch**: `005-task-management` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)

## Summary

This feature implements comprehensive task management operations including viewing with pagination/filtering, editing title/description, status toggling (individual + bulk), and soft deletion with trash/restore capabilities. The implementation follows established patterns from Feature 4 (task creation), extends the existing Task model with soft delete support, and provides a production-ready UI with optimistic updates and proper error handling.

**Key Technical Approach:**
- Add `deleted_at` nullable timestamp field to tasks table via Alembic migration
- Implement 9 new API endpoints following RESTful conventions
- Build reusable React components with TanStack Query for optimistic UI
- Use query parameter-based filtering/pagination (offset-based, 20 items default)
- Implement bulk operations with 50-task limit enforced at API layer
- Follow existing service layer pattern for business logic separation

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.7+ (frontend)
**Primary Dependencies**: FastAPI 0.100+, SQLModel, PostgreSQL 16+ (Neon), Next.js 15, React 19, TanStack Query v5, Shadcn/ui
**Storage**: PostgreSQL with SQLModel ORM, Alembic migrations for schema versioning
**Testing**: pytest (backend unit/integration), Vitest + React Testing Library (frontend), Playwright (E2E)
**Target Platform**: Web application (backend: Linux server, frontend: browser/Vercel Edge)
**Project Type**: Web (full-stack with backend/ and frontend/ directories)
**Performance Goals**: Task list load <2s, status toggle <1s, pagination <1s, optimistic UI instant with 2s confirmation
**Constraints**: Bulk max 50 tasks, pagination max 100 items, API <200ms p95, user isolation enforced
**Scale/Scope**: 500-1000 tasks/user, 1000+ concurrent users, 9 API endpoints, 6+ components, 1 migration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Evaluation: PASS ✅

All 20 constitution principles satisfied:

**Part I - Inherited Principles (I-X):** PASS
- Architecture separation (API → Service → Database)
- Type safety (Python mypy strict, TypeScript strict)
- TDD with test pyramid (70% unit, 20% integration, 10% E2E)
- Single source of truth (PostgreSQL)
- Structured error handling
- Performance optimization (indexes, async, caching)

**Part II - Web Principles (XI-XX):** PASS
- Next.js 15 + React 19 with Shadcn/ui
- RESTful API design with OpenAPI
- JWT authentication + authorization
- Database migrations (Alembic)
- OWASP Top 10 compliance
- WCAG 2.1 AA accessibility
- Responsive mobile-first design
- Type-safe contracts (Pydantic ↔ TypeScript)

No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/005-task-management/
├── plan.md              # This file
├── research.md          # Phase 0: pagination, soft delete, optimistic UI patterns
├── data-model.md        # Phase 1: Task + deleted_at, ViewPreference model
├── quickstart.md        # Phase 1: setup, API examples
├── contracts/           # Phase 1: OpenAPI specs for 9 endpoints
│   ├── get-tasks.yaml
│   ├── update-task.yaml
│   ├── toggle-task.yaml
│   ├── bulk-toggle.yaml
│   ├── delete-task.yaml
│   ├── bulk-delete.yaml
│   ├── get-trash.yaml
│   ├── restore-task.yaml
│   └── permanent-delete.yaml
└── tasks.md             # Phase 2: /sp.tasks output (not created yet)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # [MODIFY] Add deleted_at field
│   │   └── view_preference.py   # [NEW] User layout preference
│   ├── services/
│   │   └── task_service.py      # [EXTEND] Add 9 service methods
│   ├── api/routes/
│   │   └── tasks.py             # [EXTEND] Add 9 endpoints
│   └── schemas/
│       └── task_schemas.py      # [NEW] Request/response schemas
├── migrations/versions/
│   └── {timestamp}_add_deleted_at.py  # [NEW] Migration
└── tests/
    ├── unit/services/
    │   └── test_task_service.py
    └── integration/api/
        └── test_tasks_api.py

frontend/
├── app/tasks/
│   ├── page.tsx                 # [MODIFY] Add TaskList
│   └── trash/page.tsx           # [NEW] Trash view
├── components/tasks/
│   ├── TaskList.tsx             # [NEW] Main list
│   ├── TaskCard.tsx             # [NEW] Card component
│   ├── TaskFilters.tsx          # [NEW] Filter controls
│   ├── EditTaskDialog.tsx       # [NEW] Edit modal
│   ├── DeleteConfirmDialog.tsx  # [NEW] Delete confirmation
│   └── BulkActions.tsx          # [NEW] Bulk toolbar
├── hooks/
│   └── useTasks.ts              # [EXTEND] Add mutation hooks
└── tests/
    ├── components/tasks/
    └── e2e/task-management.spec.ts
```

**Structure Decision**: Web application (Option 2). Backend: API + services + models. Frontend: Next.js pages + components. Matches existing Features 3 & 4 pattern.

## Phase 0: Research

### Key Technical Decisions

1. **Pagination Strategy**: Offset-based using `?page=1&limit=20`
   - **Rationale**: Simpler than cursor-based, adequate for <1000 tasks/user, allows direct page access
   - **Implementation**: `OFFSET (page-1)*limit LIMIT limit`

2. **Soft Delete**: Nullable `deleted_at` timestamp
   - **Rationale**: Audit trail, enables "days in trash" feature, standard pattern
   - **Query**: `WHERE deleted_at IS NULL` for active, `IS NOT NULL` for trash

3. **Optimistic UI**: TanStack Query `useMutation` with `onMutate`/`onError`
   - **Rationale**: Better UX (instant feedback), standard React Query pattern
   - **Rollback**: Restore previous data from snapshot on error

4. **Bulk Operations**: Dedicated server endpoints accepting task ID arrays
   - **Rationale**: Atomic transactions, better error handling, prevents race conditions
   - **Limit**: 50 tasks max per request

5. **View Preference**: Database persistence (ViewPreference model)
   - **Rationale**: Syncs across devices, enables future personalization

6. **Filter State**: URL query params via Next.js searchParams
   - **Rationale**: Shareable URLs, browser navigation support, preserves state

## Phase 1: Design

### Database Schema Changes

**Migration: add_deleted_at_to_tasks**

```sql
ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;
CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at);
CREATE INDEX idx_tasks_user_deleted ON tasks(user_id, deleted_at) WHERE deleted_at IS NULL;
```

**Updated Task Model:**

```python
class Task(TaskBase, TimestampMixin, table=True):
    __tablename__ = "tasks"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    completed_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)  # NEW
    user: "User" = Relationship(back_populates="tasks")
```

**New Model: ViewPreference**

```python
class ViewPreference(SQLModel, table=True):
    __tablename__ = "view_preferences"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    preference_key: str = Field(index=True)
    preference_value: str
    created_at: datetime
    updated_at: datetime
    __table_args__ = (UniqueConstraint("user_id", "preference_key"),)
```

### API Endpoints Summary

All endpoints require JWT Bearer authentication and enforce user ownership.

1. **GET /api/v1/tasks** - List tasks with pagination, filtering, sorting
   - Query params: page, limit, status, sort_by, sort_order
   - Returns: TaskListResponse with tasks, metadata, pagination

2. **PUT /api/v1/tasks/{id}** - Update task title/description
   - Body: {title?, description?} (at least one required, must differ from current)
   - Returns: Updated TaskResponse

3. **PATCH /api/v1/tasks/{id}/toggle** - Toggle status (pending ↔ completed)
   - No body, auto-determines new status
   - Returns: Updated TaskResponse with new status and completed_at

4. **POST /api/v1/tasks/bulk-toggle** - Bulk status change
   - Body: {task_ids: UUID[], target_status: "pending"|"completed"}
   - Max 50 tasks, returns: {updated_count, tasks[]}

5. **DELETE /api/v1/tasks/{id}** - Soft delete (set deleted_at)
   - Returns: TaskResponse with deleted_at timestamp

6. **POST /api/v1/tasks/bulk-delete** - Bulk soft delete
   - Body: {task_ids: UUID[]} (max 50)
   - Returns: {deleted_count, tasks[]}

7. **GET /api/v1/tasks/trash** - View deleted tasks with pagination
   - Query params: page, limit
   - Returns: TaskListResponse filtered by deleted_at IS NOT NULL

8. **POST /api/v1/tasks/{id}/restore** - Restore from trash (clear deleted_at)
   - Returns: Restored TaskResponse

9. **DELETE /api/v1/tasks/{id}/permanent** - Hard delete from database
   - Irreversible, returns: success message

### Response Schemas

**TaskListResponse:**

```python
class TaskMetadata(BaseModel):
    total_pending: int
    total_completed: int
    total_active: int
    total_deleted: int

class PaginationInfo(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    metadata: TaskMetadata
    pagination: PaginationInfo
```

**BulkToggleRequest:**

```python
class BulkToggleRequest(BaseModel):
    task_ids: list[UUID] = Field(min_length=1, max_length=50)
    target_status: TaskStatus

    @field_validator('task_ids')
    @classmethod
    def validate_task_ids(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 tasks per bulk operation")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate task IDs not allowed")
        return v
```

## Implementation Strategy

### Backend Implementation Order (Days 1-5)

**Day 1: Database Layer**
- Create Alembic migration for deleted_at column
- Add ViewPreference model
- Run migration, verify schema

**Day 2: Models & Schemas**
- Update Task model with deleted_at
- Create request schemas (TaskUpdateRequest, BulkToggleRequest, BulkDeleteRequest)
- Create response schemas (TaskListResponse, TaskMetadata, PaginationInfo)

**Day 3: Service Layer**
- Implement 9 service methods in TaskService:
  - get_tasks() - pagination, filtering, sorting
  - update_task() - validation, ownership check
  - toggle_task_status() - status flip, completed_at handling
  - bulk_toggle_status() - batch update with transaction
  - soft_delete_task() - set deleted_at
  - bulk_delete_tasks() - batch soft delete
  - get_trash() - query deleted tasks
  - restore_task() - clear deleted_at
  - permanent_delete() - hard delete

**Day 4: API Routes**
- Implement 9 endpoints in /api/routes/tasks.py
- Add authentication dependency (get_current_user)
- Standardized error handling
- OpenAPI documentation

**Day 5: Testing**
- Unit tests for service methods
- Integration tests for API endpoints
- Edge cases (ownership, not found, bulk limits)

### Frontend Implementation Order (Days 1-5)

**Day 1: API Hooks**
- useTasks() - GET /tasks with TanStack Query
- useUpdateTask() - mutation with optimistic updates
- useToggleTask(), useBulkToggle() - status mutations
- useDeleteTask(), useBulkDelete() - delete mutations
- useTrash(), useRestoreTask() - trash operations

**Day 2-3: Core Components**
- TaskCard - display single task
- TaskList - render list/grid of cards
- TaskFilters - status dropdown, sort controls
- Pagination - page navigation

**Day 3-4: Action Components**
- EditTaskDialog - modal with form validation
- DeleteConfirmDialog - confirmation modal
- BulkActions - toolbar for bulk operations

**Day 4: Pages**
- Update /tasks page with TaskList
- Create /tasks/trash page

**Day 5: Testing**
- Component tests (Vitest + RTL)
- E2E test (Playwright full workflow)

## Key Technical Patterns

### Optimistic UI Pattern

```tsx
const { mutate: toggleTask } = useMutation({
  mutationFn: (taskId: string) => api.patch(`/tasks/${taskId}/toggle`),
  onMutate: async (taskId) => {
    await queryClient.cancelQueries({ queryKey: ['tasks'] });
    const previousTasks = queryClient.getQueryData(['tasks']);
    queryClient.setQueryData(['tasks'], (old) => ({
      ...old,
      tasks: old.tasks.map(t =>
        t.id === taskId
          ? { ...t, status: t.status === 'pending' ? 'completed' : 'pending' }
          : t
      )
    }));
    return { previousTasks };
  },
  onError: (err, variables, context) => {
    queryClient.setQueryData(['tasks'], context.previousTasks);
    toast.error('Failed to update task');
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
  },
});
```

### Soft Delete Query Pattern

```python
# Active tasks (default)
query = select(Task).where(
    Task.user_id == user_id,
    Task.deleted_at.is_(None)
)

# Trash view
query = select(Task).where(
    Task.user_id == user_id,
    Task.deleted_at.isnot(None)
)
```

### Pagination State Management

- Use Next.js searchParams for URL-based state
- TanStack Query caches each page separately
- Enables shareable URLs and browser navigation

## Critical Implementation Files

**Backend:**
- `backend/src/models/task.py` - Add deleted_at field
- `backend/src/services/task_service.py` - Implement 9 service methods
- `backend/src/api/routes/tasks.py` - Add 9 route handlers
- `backend/migrations/versions/{timestamp}_add_deleted_at.py` - Migration

**Frontend:**
- `frontend/app/tasks/page.tsx` - Integrate TaskList component
- `frontend/components/tasks/TaskList.tsx` - Main list component
- `frontend/hooks/useTasks.ts` - Add mutation hooks
- `frontend/app/tasks/trash/page.tsx` - Trash view page

## Next Steps

This plan is ready for task generation via `/sp.tasks`.

---

**Planning Complete**: 2025-12-20
**Ready for**: Task generation and implementation
