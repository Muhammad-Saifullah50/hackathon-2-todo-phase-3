# hackathon-2-todo-phase-3 Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-02

## Active Technologies
- Python 3.13+ (backend), TypeScript 5.7+ (frontend) + FastAPI 0.100+, SQLModel, PostgreSQL 16+ (Neon), Next.js 15, React 19, TanStack Query v5, Shadcn/ui (005-task-management)
- PostgreSQL with SQLModel ORM, Alembic migrations for schema versioning (005-task-management)
- Framer Motion for animations, Recharts for charts, dnd-kit for drag-and-drop, cmdk for command palette, @use-gesture/react for mobile gestures, date-fns for dates, Zustand for client state (006-landing-page-ui)
- PostgreSQL 16+ (Neon) for tasks, users, conversations, messages, templates, tags (007-ai-chatbot)
- MCP (Model Context Protocol) server for AI integration

## Project Structure

```text
backend/          # FastAPI backend
  src/
    api/          # API endpoints
    core/         # Core utilities
    models/       # Database models
    schemas/      # Pydantic schemas
    services/     # Business logic
    db/           # Database utilities
frontend/         # Next.js frontend
  app/            # App Router pages
  components/     # React components
  hooks/          # Custom hooks
  lib/            # Utilities
mcp_server/       # MCP server for AI integration
tests/            # Test files
```

## Commands

### Backend
```bash
# Start development server
cd backend && uvicorn src.main:app --reload

# Run migrations
cd backend && alembic upgrade head

# Create new migration
cd backend && alembic revision --autogenerate -m "description"

# Run tests with coverage
cd backend && uv run pytest --cov=src tests/

# Access API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Frontend
```bash
# Install dependencies
cd frontend && npm install

# Start development server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run type checking
cd frontend && npm run type-check

# Run linting
cd frontend && npm run lint

# Run tests
cd frontend && npm test
```

### MCP Server
```bash
# Start MCP server
cd mcp_server && python main.py

# Install dependencies
cd mcp_server && pip install -r requirements.txt
```

## Code Style

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Use snake_case for variables, functions, and file names
- Use PascalCase for class names
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

### Frontend (TypeScript)
- Follow TypeScript strict mode conventions
- Use camelCase for variables and functions
- Use PascalCase for components and types
- Prefer functional components with hooks over class components
- Use "use client" directive only when necessary (interactivity, hooks)
- Keep Server Components as default when possible

## Implementation Patterns

### Backend Patterns

#### Service Layer Pattern
```python
# All business logic goes in service classes
class TaskService:
    def __init__(self, db: Session):
        self.db = db

    async def get_tasks(self, user_id: str, filters: TaskFilters) -> TaskListResponse:
        # Implement pagination, filtering, sorting
        query = select(Task).where(Task.user_id == user_id, Task.deleted_at.is_(None))
        # Apply filters and return
```

#### Soft Delete Pattern
```python
# Add deleted_at column to models
deleted_at: datetime | None = Field(default=None)

# Filter out soft-deleted records
query = select(Task).where(Task.deleted_at.is_(None))

# Soft delete by setting timestamp
task.deleted_at = datetime.now(timezone.utc)

# Restore by clearing timestamp
task.deleted_at = None
```

#### Authentication Dependency
```python
# Use dependency injection for authentication
async def get_current_user(
    authorization: str = Header(None)
) -> User:
    # Validate JWT token and return user
    pass

# Use in route handlers
@router.get("/tasks")
async def get_tasks(
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically injected
```

### Frontend Patterns

#### Optimistic UI Updates with TanStack Query
```typescript
const { mutate } = useMutation({
  mutationFn: (taskId: string) => api.patch(`/tasks/${taskId}/toggle`),

  // Optimistic update
  onMutate: async (taskId) => {
    await queryClient.cancelQueries({ queryKey: ['tasks'] });
    const previousTasks = queryClient.getQueryData(['tasks']);

    // Update cache immediately
    queryClient.setQueryData(['tasks'], (old) => ({
      ...old,
      tasks: old.tasks.map(t =>
        t.id === taskId ? { ...t, status: t.status === 'pending' ? 'completed' : 'pending' } : t
      )
    }));

    return { previousTasks };
  },

  // Rollback on error
  onError: (err, variables, context) => {
    queryClient.setQueryData(['tasks'], context.previousTasks);
    toast.error('Failed to update task');
  },

  // Confirm success
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
  }
});
```

#### Server vs Client Components
```typescript
// Server Component (default) - No "use client"
// Can fetch data directly, no hooks
export default function TasksPage() {
  return (
    <div>
      <h1>My Tasks</h1>
      <TaskList /> {/* Client Component */}
    </div>
  );
}

// Client Component - Add "use client" directive
// Can use hooks, event handlers, state
"use client";
export function TaskList() {
  const [page, setPage] = useState(1);
  const { data } = useTasks({ page });
  // ...
}
```

#### Form Validation with Zod + React Hook Form
```typescript
const schema = z.object({
  title: z.string().min(1).max(100),
  description: z.string().max(500).nullable(),
});

const form = useForm({
  resolver: zodResolver(schema),
  defaultValues: { title: "", description: "" }
});

const onSubmit = (data) => {
  // data is type-safe and validated
  createTask(data);
};
```

#### Accessibility Best Practices
```typescript
// Use semantic HTML
<button aria-label="Delete task" onClick={handleDelete}>
  <Trash2 className="h-4 w-4" />
</button>

// Add aria-live regions for dynamic updates
<div className="sr-only" aria-live="polite" aria-atomic="true">
  {`${pendingCount} pending tasks, ${completedCount} completed tasks`}
</div>

// Use role attributes
<Card role="article" aria-label={`Task: ${task.title}`}>
  {/* Card content */}
</Card>
```

### Database Patterns

#### Composite Indexes for Performance
```sql
-- Index for filtering active tasks by user
CREATE INDEX idx_tasks_user_deleted ON tasks(user_id, deleted_at)
WHERE deleted_at IS NULL;

-- Improves query: SELECT * FROM tasks WHERE user_id = ? AND deleted_at IS NULL
```

#### Pagination with Offset
```python
# Calculate pagination
offset = (page - 1) * limit
total_pages = (total_count + limit - 1) // limit

# Query with limit and offset
query = query.offset(offset).limit(limit)
```

### Error Handling Patterns

#### Backend Error Responses
```python
from fastapi import HTTPException

# Standard error format
raise HTTPException(
    status_code=404,
    detail="Task not found"
)

# With custom error structure
raise HTTPException(
    status_code=400,
    detail={
        "message": "Validation failed",
        "errors": ["Title is required", "Description too long"]
    }
)
```

#### Frontend Error Boundary
```typescript
class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

## Common Troubleshooting

### Backend Issues

**Migration Errors**
```bash
# Reset database (development only!)
cd backend && alembic downgrade base
cd backend && alembic upgrade head

# Check current migration version
cd backend && alembic current

# View migration history
cd backend && alembic history
```

**CORS Errors**
```python
# Ensure CORS middleware is configured in main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Issues

**Module Not Found Errors**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

**Type Errors with Zod Schemas**
```typescript
// Use .nullable() not .optional() for form fields
description: z.string().nullable()  // ✓ Correct
description: z.string().optional()  // ✗ May cause type issues
```

**Shadcn UI Component Missing**
```bash
# Install missing component
npx shadcn@latest add alert-dialog

# Or create manually in components/ui/
```

### MCP Server Issues

**Connection Errors**
```bash
# Check environment variables
cd mcp_server
cat .env

# Verify the MCP server is running
python main.py
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.13+
```

## Recent Changes
- Phase 3: Added MCP (Model Context Protocol) server for AI integration
- 007-ai-chatbot: Added AI chatbot functionality with conversations and messages
- 006-landing-page-ui: Added Framer Motion for animations, Recharts for charts, dnd-kit for drag-and-drop, cmdk for command palette, @use-gesture/react for mobile gestures, date-fns for dates, Zustand for client state
- 006-landing-page-ui: Implemented landing page with scroll animations, due dates with timezone handling, tags system with color coding, subtasks with auto-completion, recurring tasks, task templates, keyboard shortcuts (Cmd/Ctrl+K), multiple views (List/Grid/Kanban/Calendar/Dashboard), theme picker, mobile swipe gestures, onboarding tour


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
