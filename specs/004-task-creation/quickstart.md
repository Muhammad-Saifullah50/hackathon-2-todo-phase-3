# Quickstart: Task Creation Feature

**Feature**: 004-task-creation
**Date**: 2025-12-20
**Prerequisites**: Features 1, 2, and 3 must be complete

## Overview

This guide provides step-by-step instructions for implementing the Task Creation feature, including backend API, frontend UI, and testing.

---

## Prerequisites Checklist

Before starting implementation, verify these prerequisites:

- [x] **Feature 1 (Project Setup)**: Docker Compose running, ports 3000 (frontend) and 8000 (backend) accessible
- [x] **Feature 2 (Database Setup)**: Neon PostgreSQL connected, Task and User tables exist, migrations run successfully
- [x] **Feature 3 (Authentication)**: Better Auth configured, JWT tokens working, `get_current_user()` dependency available
- [x] **Development Environment**: Python 3.13+, Node 20+, uv, npm/pnpm installed
- [x] **Code Quality Tools**: ruff, black, mypy (backend), ESLint, Prettier, tsc (frontend)

---

## Phase 1: Backend API Implementation

### Step 1.1: Update Task Model (If Needed)

**File**: `backend/src/models/task.py`

Verify the existing Task model has proper validation:

```python
from sqlmodel import Field

class TaskBase(SQLModel):
    title: str = Field(
        index=True,
        max_length=100,
        min_length=1,
        description="Title or summary of the task"
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Detailed description of the task"
    )
    # ... existing priority and status fields
```

If constraints are missing, update the model and generate a migration:

```bash
cd backend
alembic revision --autogenerate -m "add task field constraints"
alembic upgrade head
```

---

### Step 1.2: Create TaskCreate Schema

**File**: `backend/src/models/task.py`

Update the TaskCreate schema with custom validators:

```python
import re
from pydantic import field_validator

class TaskCreate(SQLModel):
    """Request schema for creating a task."""
    title: str
    description: str | None = None
    priority: TaskPriority | None = None

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

    @field_validator('description')
    @classmethod
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

**Test the validator**:

```bash
pytest backend/tests/unit/test_models.py::test_task_create_validation
```

---

### Step 1.3: Create TaskService

**File**: `backend/src/services/task_service.py` (new file)

```python
from uuid import UUID
from sqlmodel import Session
from src.models.task import Task, TaskCreate, TaskStatus, TaskPriority

class TaskService:
    """Business logic for task operations."""

    def __init__(self, session: Session):
        self.session = session

    async def create_task(
        self,
        task_data: TaskCreate,
        user_id: str
    ) -> Task:
        """Create a new task for the authenticated user.

        Args:
            task_data: Validated task creation data
            user_id: ID of the authenticated user from JWT

        Returns:
            Created Task instance with all fields populated

        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        task = Task(
            title=task_data.title,  # Already validated and trimmed
            description=task_data.description,  # Already validated and trimmed
            status=TaskStatus.PENDING,  # Always pending on creation
            priority=task_data.priority or TaskPriority.MEDIUM,  # Default to MEDIUM
            user_id=user_id,
            # Timestamps are auto-set by database
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task
```

**Test the service**:

```bash
pytest backend/tests/unit/test_task_service.py::test_create_task_success
```

---

### Step 1.4: Create API Route

**File**: `backend/src/api/routes/tasks.py` (new file)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.auth import get_current_user
from src.db.session import get_db
from src.models.task import TaskCreate, TaskResponse
from src.models.user import User
from src.services.task_service import TaskService
from src.schemas.responses import StandardizedResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=StandardizedResponse[TaskResponse]
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title, description, priority)
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        StandardizedResponse containing the created task

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        service = TaskService(session)
        task = await service.create_task(task_data, current_user.id)

        logger.info(f"Task created: id={task.id}, user_id={current_user.id}")

        return StandardizedResponse(
            success=True,
            message="Task created successfully",
            data=TaskResponse.model_validate(task),
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e),
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to create task. Please try again later.",
                },
            }
        )
```

**Register router** in `backend/src/api/__init__.py`:

```python
from .routes import tasks

app.include_router(tasks.router)
```

**Test the route**:

```bash
pytest backend/tests/integration/test_task_routes.py::test_create_task_success
```

---

### Step 1.5: Verify OpenAPI Documentation

Start the backend and check auto-generated API docs:

```bash
cd backend
uvicorn src.main:app --reload
```

Visit: http://localhost:8000/docs

Verify:
- `POST /api/v1/tasks` endpoint appears
- Request schema shows title (required), description (optional), priority (optional)
- Response schema shows all task fields
- "Try it out" button works (requires authentication)

---

## Phase 2: Frontend UI Implementation

### Step 2.1: Generate TypeScript Types from OpenAPI

```bash
cd frontend
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

Verify the generated types:

```typescript
import type { components } from '@/types/api';

type TaskResponse = components['schemas']['TaskResponse'];
type TaskCreateRequest = components['schemas']['TaskCreateRequest'];
```

---

### Step 2.2: Create API Client

**File**: `frontend/lib/api/tasks.ts` (new file)

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

// Add JWT token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: 'pending' | 'completed';
  priority: 'low' | 'medium' | 'high';
  user_id: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  details?: Array<{
    field: string;
    message: string;
  }>;
}

export async function createTask(data: CreateTaskRequest): Promise<ApiResponse<Task>> {
  const response = await apiClient.post<ApiResponse<Task>>('/api/v1/tasks', data);
  return response.data;
}
```

---

### Step 2.3: Create Zod Schema

**File**: `frontend/lib/schemas/task.ts` (new file)

```typescript
import { z } from 'zod';

export const createTaskSchema = z.object({
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

export type CreateTaskForm = z.infer<typeof createTaskSchema>;
```

---

### Step 2.4: Create React Query Hook

**File**: `frontend/hooks/useTasks.ts` (new file)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createTask, CreateTaskRequest } from '@/lib/api/tasks';
import { toast } from 'sonner';

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTask,

    // Optimistic update
    onMutate: async (newTask: CreateTaskRequest) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previousTasks = queryClient.getQueryData(['tasks']);

      const tempId = `temp-${crypto.randomUUID()}`;
      queryClient.setQueryData(['tasks'], (old: any) => ({
        ...old,
        tasks: [
          {
            id: tempId,
            ...newTask,
            status: 'pending',
            priority: newTask.priority || 'medium',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            completed_at: null,
          },
          ...(old?.tasks || []),
        ],
      }));

      return { previousTasks };
    },

    onError: (err, vars, context) => {
      queryClient.setQueryData(['tasks'], context?.previousTasks);
      toast.error("Failed to create task. Please try again.");
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success("Task created successfully");
    },
  });
}
```

---

### Step 2.5: Create UI Component

**File**: `frontend/components/tasks/CreateTaskDialog.tsx` (new file)

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PlusIcon } from 'lucide-react';
import { createTaskSchema, CreateTaskForm } from '@/lib/schemas/task';
import { useCreateTask } from '@/hooks/useTasks';

export function CreateTaskDialog() {
  const [open, setOpen] = useState(false);
  const { mutate: createTask, isPending } = useCreateTask();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
  } = useForm<CreateTaskForm>({
    resolver: zodResolver(createTaskSchema),
    mode: "onChange", // Real-time validation
  });

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

  const onSubmit = (data: CreateTaskForm) => {
    createTask(data, {
      onSuccess: () => {
        setOpen(false);
        reset();
      },
    });
  };

  // Check if user has entered data (for unsaved changes warning)
  const title = watch('title');
  const description = watch('description');
  const hasChanges = Boolean(title || description);

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && hasChanges) {
      if (!window.confirm("Discard changes?")) {
        return;
      }
      reset();
    }
    setOpen(newOpen);
  };

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <PlusIcon className="mr-2 h-4 w-4" />
        Add Task
      </Button>

      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-[500px] max-sm:h-full max-sm:w-full max-sm:max-w-full">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Title field */}
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                {...register('title')}
                placeholder="Enter task title..."
                maxLength={100}
                aria-invalid={errors.title ? 'true' : 'false'}
                aria-describedby={errors.title ? 'title-error' : undefined}
              />
              {errors.title && (
                <p id="title-error" className="text-sm text-destructive mt-1">
                  {errors.title.message}
                </p>
              )}
            </div>

            {/* Description field */}
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                {...register('description')}
                placeholder="Add details (optional)..."
                maxLength={500}
                rows={4}
                aria-invalid={errors.description ? 'true' : 'false'}
                aria-describedby={errors.description ? 'description-error' : undefined}
              />
              {errors.description && (
                <p id="description-error" className="text-sm text-destructive mt-1">
                  {errors.description.message}
                </p>
              )}
            </div>

            {/* Priority field */}
            <div>
              <Label htmlFor="priority">Priority</Label>
              <Select {...register('priority')}>
                <SelectTrigger id="priority">
                  <SelectValue placeholder="Select priority (default: Medium)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="LOW">Low</SelectItem>
                  <SelectItem value="MEDIUM">Medium</SelectItem>
                  <SelectItem value="HIGH">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Form actions */}
            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isPending || isSubmitting || Object.keys(errors).length > 0}
              >
                {isPending ? 'Creating...' : 'Create Task'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

---

### Step 2.6: Add Component to Task List Page

**File**: `frontend/app/tasks/page.tsx`

```typescript
import { CreateTaskDialog } from '@/components/tasks/CreateTaskDialog';

export default function TasksPage() {
  return (
    <div className="container max-w-7xl mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">My Tasks</h1>
        <CreateTaskDialog />
      </div>

      {/* Task list will be implemented in Feature 5 */}
    </div>
  );
}
```

---

## Phase 3: Testing

### Step 3.1: Backend Unit Tests

**File**: `backend/tests/unit/test_task_service.py`

```python
import pytest
from src.services.task_service import TaskService
from src.models.task import TaskCreate, TaskPriority

@pytest.mark.asyncio
async def test_create_task_success(test_session, test_user):
    service = TaskService(test_session)
    task_data = TaskCreate(title="Test Task", description="Test Description")

    task = await service.create_task(task_data, test_user.id)

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == "pending"
    assert task.priority == "medium"  # Default
    assert task.user_id == test_user.id
    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.completed_at is None
```

Run:
```bash
pytest backend/tests/unit/test_task_service.py -v
```

---

### Step 3.2: Backend Integration Tests

**File**: `backend/tests/integration/test_task_routes.py`

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_create_task_success(client: TestClient, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test Task", "description": "Test Description"},
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Task created successfully"
    assert data["data"]["title"] == "Test Task"
```

Run:
```bash
pytest backend/tests/integration/test_task_routes.py -v
```

---

### Step 3.3: Frontend Component Tests

**File**: `frontend/__tests__/components/CreateTaskDialog.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CreateTaskDialog } from '@/components/tasks/CreateTaskDialog';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

describe('CreateTaskDialog', () => {
  it('creates task on form submission', async () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <CreateTaskDialog />
      </QueryClientProvider>
    );

    await userEvent.click(screen.getByText('Add Task'));
    await userEvent.type(screen.getByLabelText('Title *'), 'New Task');
    await userEvent.click(screen.getByText('Create Task'));

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
});
```

Run:
```bash
npm test -- CreateTaskDialog.test.tsx
```

---

## Phase 4: Manual Testing

### Test Scenario 1: Happy Path

1. Start backend: `cd backend && uvicorn src.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Sign in as a user
4. Click "Add Task" button
5. Enter title: "Buy groceries"
6. Enter description: "Milk, eggs, bread"
7. Select priority: "Medium"
8. Click "Create Task"
9. ✅ Toast notification: "Task created successfully"
10. ✅ Task appears in list immediately

### Test Scenario 2: Validation Errors

1. Click "Add Task"
2. Leave title empty, click "Create Task"
3. ✅ Error: "Title is required"
4. Enter 101-character title
5. ✅ Error: "Title must be 100 characters or less"
6. Enter 51-word title
7. ✅ Error: "Title must be 50 words or less"

### Test Scenario 3: Network Error

1. Stop backend server
2. Create a task
3. ✅ Optimistic task appears immediately
4. ✅ Error toast: "Failed to create task"
5. ✅ Optimistic task removed from list

---

## Troubleshooting

### Issue: "Module not found: task_service"

**Solution**: Ensure `backend/src/services/__init__.py` exists

### Issue: "Port 8000 already in use"

**Solution**: Kill existing process: `lsof -ti:8000 | xargs kill -9`

### Issue: "CORS error in browser"

**Solution**: Verify CORS middleware in backend allows frontend origin

### Issue: "JWT token not being sent"

**Solution**: Check token storage in localStorage and axios interceptor

---

## Next Steps

After completing this feature:

1. **Feature 5**: Task viewing and filtering
2. **Feature 6**: Task updates
3. **Feature 7**: Task status toggle
4. **Feature 8**: Task deletion

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Hook Form Documentation](https://react-hook-form.com)
- [TanStack Query Documentation](https://tanstack.com/query)
- [Shadcn/ui Components](https://ui.shadcn.com)
