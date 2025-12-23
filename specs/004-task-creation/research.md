# Research: Task Creation Feature

**Feature**: 004-task-creation
**Date**: 2025-12-20
**Purpose**: Resolve technical unknowns and establish implementation patterns

## Research Topics

### 1. Pydantic v2 Validation Patterns for Title Word Count

**Decision**: Use custom validator with regex pattern for word counting

**Rationale**:
- Pydantic v2 provides `@field_validator` decorator for custom validation logic
- Word count requirement: max 50 words using `/\s+/` regex split
- Both character (100) and word (50) limits must be enforced

**Implementation Pattern**:
```python
from pydantic import BaseModel, field_validator
import re

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        # Trim whitespace
        v = v.strip()

        # Check not empty
        if not v:
            raise ValueError('Title cannot be empty')

        # Check character limit
        if len(v) > 100:
            raise ValueError('Title must be 100 characters or less')

        # Check word count
        words = re.split(r'\s+', v)
        if len(words) > 50:
            raise ValueError('Title must be 50 words or less')

        return v
```

**Alternatives Considered**:
- Database-level CHECK constraints: Rejected - PostgreSQL doesn't support word count checks
- Frontend-only validation: Rejected - security risk, backend must validate independently

**References**:
- Pydantic v2 Validators: https://docs.pydantic.dev/latest/concepts/validators/

---

### 2. React Hook Form + Zod Integration for Real-Time Validation

**Decision**: Use React Hook Form with Zod schema and `mode: "onChange"` for instant feedback

**Rationale**:
- React Hook Form provides performant form state management
- Zod enables type-safe schema validation matching backend
- `mode: "onChange"` triggers validation on every keystroke for immediate feedback

**Implementation Pattern**:
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

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

type CreateTaskForm = z.infer<typeof createTaskSchema>;

export function CreateTaskDialog() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateTaskForm>({
    resolver: zodResolver(createTaskSchema),
    mode: "onChange", // Real-time validation
  });

  // ...
}
```

**Alternatives Considered**:
- Formik: Rejected - more verbose API, less TypeScript-friendly
- Manual validation: Rejected - error-prone, difficult to maintain
- `mode: "onBlur"`: Rejected - less immediate feedback than `onChange`

**References**:
- React Hook Form: https://react-hook-form.com/get-started
- Zod: https://zod.dev/
- @hookform/resolvers: https://github.com/react-hook-form/resolvers

---

### 3. TanStack Query Optimistic Updates Pattern

**Decision**: Use `onMutate` with temporary ID and `onError` rollback strategy

**Rationale**:
- Optimistic updates improve perceived performance (instant UI feedback)
- TanStack Query v5 provides first-class optimistic update support
- Temporary client-side UUID prevents ID conflicts during optimistic state

**Implementation Pattern**:
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createTask, CreateTaskRequest } from '@/lib/api/tasks';

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTask,

    // Optimistic update
    onMutate: async (newTask: CreateTaskRequest) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(['tasks']);

      // Generate temporary ID
      const tempId = `temp-${crypto.randomUUID()}`;

      // Optimistically update cache
      queryClient.setQueryData(['tasks'], (old: any) => ({
        ...old,
        tasks: [
          {
            id: tempId,
            ...newTask,
            status: 'PENDING',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            completed_at: null,
          },
          ...(old?.tasks || []),
        ],
      }));

      return { previousTasks };
    },

    // Rollback on error
    onError: (err, newTask, context) => {
      queryClient.setQueryData(['tasks'], context?.previousTasks);
      toast.error("Failed to create task. Please try again.");
    },

    // Refetch on success
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success("Task created successfully");
    },
  });
}
```

**Alternatives Considered**:
- No optimistic updates: Rejected - poor user experience with network latency
- Manual cache management: Rejected - error-prone, TanStack Query handles it better
- Server-side rendering only: Rejected - doesn't provide instant feedback

**References**:
- TanStack Query Optimistic Updates: https://tanstack.com/query/latest/docs/react/guides/optimistic-updates
- TanStack Query v5 Migration: https://tanstack.com/query/latest/docs/react/guides/migrating-to-v5

---

### 4. FastAPI Service Layer Pattern

**Decision**: Implement separate TaskService class with dependency injection

**Rationale**:
- Service layer isolates business logic from HTTP layer (testable without FastAPI)
- Matches existing project architecture from Feature 2 (Database Setup)
- Enables easier testing (mock dependencies) and code reuse

**Implementation Pattern**:
```python
# backend/src/services/task_service.py
from uuid import UUID
from sqlmodel import Session, select
from src.models.task import Task, TaskCreate
from src.models.user import User

class TaskService:
    def __init__(self, session: Session):
        self.session = session

    async def create_task(
        self,
        task_data: TaskCreate,
        user_id: str
    ) -> Task:
        """Create a new task for the authenticated user."""
        task = Task(
            title=task_data.title.strip(),
            description=task_data.description.strip() if task_data.description else None,
            status=TaskStatus.PENDING,
            priority=task_data.priority or TaskPriority.MEDIUM,
            user_id=user_id,
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

# backend/src/api/routes/tasks.py
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from src.auth import get_current_user
from src.db.session import get_db
from src.models.task import TaskCreate, TaskResponse
from src.models.user import User
from src.services.task_service import TaskService
from src.schemas.responses import StandardizedResponse

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Create a new task for the authenticated user."""
    service = TaskService(session)
    task = await service.create_task(task_data, current_user.id)

    return StandardizedResponse(
        success=True,
        message="Task created successfully",
        data=TaskResponse.model_validate(task),
    )
```

**Alternatives Considered**:
- Logic in route handler: Rejected - violates separation of concerns, hard to test
- Repository pattern: Rejected - SQLModel ORM provides sufficient abstraction
- Domain-driven design layers: Rejected - over-engineering for current scope

**References**:
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- SQLModel Async: https://sqlmodel.tiangolo.com/tutorial/

---

### 5. Shadcn/ui Dialog Component for Modal

**Decision**: Use Shadcn Dialog with controlled open state and keyboard shortcuts

**Rationale**:
- Shadcn Dialog provides accessible, WAI-ARIA compliant modal
- Built on Radix UI primitives (battle-tested accessibility)
- Supports keyboard navigation (Escape to close) out of the box

**Implementation Pattern**:
```typescript
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

export function CreateTaskDialog() {
  const [open, setOpen] = useState(false);
  const { mutate: createTask, isPending } = useCreateTask();

  // Keyboard shortcut: Ctrl/Cmd + N
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        setOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (data: CreateTaskForm) => {
    createTask(data, {
      onSuccess: () => {
        setOpen(false);
        reset(); // React Hook Form reset
      },
    });
  };

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <PlusIcon className="mr-2 h-4 w-4" />
        Add Task
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmit)}>
            {/* Form fields */}
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

**Alternatives Considered**:
- Inline form at top of page: Rejected - takes up constant screen space
- Full-page route: Rejected - breaks flow, requires navigation
- Bottom sheet (mobile): Considered for future enhancement, modal works on mobile

**References**:
- Shadcn Dialog: https://ui.shadcn.com/docs/components/dialog
- Radix UI Dialog: https://www.radix-ui.com/primitives/docs/components/dialog

---

### 6. Error Response Format Consistency

**Decision**: Use existing StandardizedResponse with nested error details array

**Rationale**:
- Project already uses StandardizedResponse pattern (from Feature 2)
- Pydantic ValidationError provides detailed field errors
- Frontend expects consistent error structure

**Implementation Pattern**:
```python
# backend/src/schemas/responses.py (already exists)
from pydantic import BaseModel
from typing import Any

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    # For validation errors with multiple fields
    details: list[dict[str, Any]] | None = None

# Error handling in route
from fastapi import HTTPException, status
from pydantic import ValidationError

@router.post("/")
async def create_task(task_data: TaskCreate, ...):
    try:
        # ... logic
    except ValidationError as e:
        errors = []
        for err in e.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
            })

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                },
                "details": errors,
            }
        )
```

**Alternatives Considered**:
- Flat error array: Rejected - doesn't match existing StandardizedResponse pattern
- Error codes per field: Rejected - over-engineering, message is sufficient

**References**:
- FastAPI Exception Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
- Pydantic Validation Errors: https://docs.pydantic.dev/latest/errors/errors/

---

### 7. Database Constraints vs Application Validation

**Decision**: Use both database constraints (max_length) and application validation

**Rationale**:
- Database constraints provide last line of defense (prevent data corruption)
- Application validation provides user-friendly error messages
- Defense in depth: validation at all layers (frontend, backend, database)

**Implementation Pattern**:
```python
# backend/src/models/task.py (update existing)
from sqlmodel import Field

class TaskBase(SQLModel):
    title: str = Field(
        index=True,
        max_length=100,  # DB constraint
        min_length=1,    # DB constraint
        description="Title or summary of the task"
    )
    description: str | None = Field(
        default=None,
        max_length=500,  # DB constraint
        description="Detailed description of the task"
    )
```

**Alternatives Considered**:
- Application-only validation: Rejected - risk of data corruption if validation bypassed
- Database CHECK constraints for word count: Rejected - PostgreSQL doesn't support regex in CHECK
- No constraints: Rejected - violates constitution principle of defense in depth

**References**:
- SQLModel Field Constraints: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/

---

### 8. Mobile Responsiveness Strategy

**Decision**: Full-screen modal on mobile (<768px), centered modal on desktop (>=768px)

**Rationale**:
- Tailwind breakpoints (sm: 640px, md: 768px, lg: 1024px) are industry standard
- Full-screen on mobile provides more space for form inputs
- Centered modal on desktop preserves context (user can see task list behind)

**Implementation Pattern**:
```typescript
<DialogContent className="sm:max-w-[500px] max-sm:h-full max-sm:w-full max-sm:max-w-full">
  {/*
    Mobile (<640px): Full screen (h-full w-full)
    Desktop (>=640px): Centered modal with max-width 500px
  */}
</DialogContent>

// Form fields with responsive padding
<div className="space-y-4 px-4 py-6 sm:px-6">
  {/* More padding on desktop */}
</div>
```

**Alternatives Considered**:
- Same modal size on all devices: Rejected - poor mobile UX (cramped)
- Bottom sheet on mobile: Deferred - nice-to-have, full-screen works fine
- Separate mobile/desktop components: Rejected - unnecessary code duplication

**References**:
- Tailwind Responsive Design: https://tailwindcss.com/docs/responsive-design
- Shadcn Dialog Responsive: https://ui.shadcn.com/docs/components/dialog

---

## Summary

All technical unknowns have been resolved with clear implementation patterns:

1. ✅ Pydantic v2 custom validators for word count validation
2. ✅ React Hook Form + Zod with `mode: "onChange"` for real-time feedback
3. ✅ TanStack Query optimistic updates with temporary IDs
4. ✅ FastAPI service layer pattern with dependency injection
5. ✅ Shadcn Dialog with keyboard shortcuts for modal UI
6. ✅ StandardizedResponse error format with details array
7. ✅ Database constraints + application validation (defense in depth)
8. ✅ Responsive design: full-screen mobile, centered desktop modal

All patterns align with constitution principles and existing codebase architecture.

**Next Phase**: Proceed to Phase 1 (Data Model & Contracts)
