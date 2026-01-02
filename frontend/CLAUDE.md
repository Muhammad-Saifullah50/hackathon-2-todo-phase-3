# TodoMore Frontend - Next.js Development Guidelines

This file contains project-specific guidelines for Claude Code when working on the TodoMore frontend application.

## Project Overview

**TodoMore Frontend** - A modern Next.js 15 frontend for the TodoMore task management application, featuring React 19, TypeScript, Shadcn/ui, and comprehensive task management capabilities.

**Tech Stack:**
- Next.js 15 (App Router) for React framework
- TypeScript 5.7+ for type safety
- React 19 for UI library
- Tailwind CSS for styling
- Shadcn/ui for component library (Radix UI primitives)
- TanStack Query v5 for data fetching and state management
- Framer Motion for animations
- Recharts for data visualization
- @dnd-kit for drag-and-drop functionality
- cmdk for command palette
- @use-gesture/react for mobile gestures
- date-fns for date handling
- Zustand for client state
- Vitest + React Testing Library + Playwright for testing

**Architecture:**
- Next.js App Router with server and client components
- Component-based architecture with reusable UI components
- Custom hooks for data fetching and business logic
- Optimistic UI updates with TanStack Query
- Responsive design with mobile-first approach
- Accessible components following WCAG 2.1 AA

## Core Principles

### 1. Code Quality Standards

- **TypeScript Strict Mode:** All type errors must be resolved
- **Type Hints:** All function signatures and component props must include types
- **Component Structure:** Prefer functional components with hooks
- **Naming:**
  - Components: PascalCase (e.g., `TaskCard.tsx`)
  - Hooks: camelCase with `use` prefix (e.g., `useTasks.ts`)
  - Utilities: camelCase (e.g., `formatDate.ts`)
- **File Organization:** Co-locate related files when possible

### 2. Testing Requirements

- **Unit Tests:** Test components and hooks in isolation
- **Integration Tests:** Test user flows with React Testing Library
- **E2E Tests:** Critical user journeys with Playwright
- **Test Location:** All tests in `tests/` directory
- **Run Before Commit:** Always run tests before committing changes

### 3. Component Design

- **Server Components as Default:** Only use "use client" when necessary
- **Component Composition:** Build components from smaller reusable pieces
- **Props Interface:** Define clear props interfaces with TypeScript
- **Accessibility:** Ensure all components are keyboard navigable and screen reader friendly

### 4. State Management

- **Server State:** Use TanStack Query for API data
- **Client State:** Use React useState/useContext for local component state
- **Global State:** Use Zustand for cross-component state when needed
- **Form State:** Use React Hook Form with Zod validation

## File Organization

### Directory Structure

```
frontend/
├── app/                          # Next.js App Router pages
│   ├── (root)/                  # Authenticated routes
│   │   └── tasks/               # Task management pages
│   ├── layout.tsx               # Root layout with providers
│   └── page.tsx                 # Landing page
├── components/                   # React components
│   ├── calendar/                # Calendar view components
│   ├── dashboard/               # Dashboard analytics components
│   ├── kanban/                  # Kanban board components
│   ├── landing/                 # Landing page sections
│   ├── mobile/                  # Mobile-specific components
│   ├── onboarding/              # Onboarding tour components
│   ├── sidebar/                 # Navigation sidebar
│   ├── tasks/                   # Task management components
│   └── ui/                      # Reusable UI components (Shadcn)
├── hooks/                       # Custom React hooks
│   ├── useTasks.ts              # Task CRUD operations
│   ├── useTags.ts               # Tags management
│   ├── useSubtasks.ts           # Subtasks operations
│   ├── useTemplates.ts          # Templates management
│   ├── useRecurring.ts          # Recurring tasks
│   ├── useAnalytics.ts          # Dashboard analytics
│   └── useSearch.ts             # Search functionality
├── lib/                         # Utility functions
│   ├── api/                     # API client functions
│   ├── types/                   # TypeScript type definitions
│   ├── animations.ts            # Framer Motion variants
│   ├── date-utils.ts            # Date formatting utilities
│   ├── onboarding-steps.ts      # Tour configuration
│   └── utils.ts                 # General utilities
├── public/                      # Static assets
│   └── illustrations/           # Empty state SVG illustrations
└── tests/                       # Test files
```

### When Adding New Features

1. **Types** (`lib/types/`):
   - Define TypeScript interfaces for data structures
   - Export types for reusability

2. **API Functions** (`lib/api/`):
   - Create typed API functions
   - Handle errors gracefully

3. **Custom Hooks** (`hooks/`):
   - Create reusable hooks for data fetching
   - Use TanStack Query for server state
   - Return data, loading, error states

4. **Components** (`components/`):
   - Create reusable components
   - Use Shadcn/ui components when possible
   - Add TypeScript prop types

5. **Pages** (`app/`):
   - Create route pages
   - Keep business logic in hooks/services
   - Display data from hooks

### When Modifying Existing Code

1. **Read Before Modifying:**
   - Always read the entire file before making changes
   - Understand existing patterns and conventions
   - Maintain consistency with existing code

2. **Preserve Functionality:**
   - Don't break existing tests
   - Run tests after changes
   - Update tests if behavior changes intentionally

3. **Respect Architecture:**
   - Keep business logic in hooks/services
   - Don't fetch data directly in components
   - Use proper state management

## Specific Module Guidelines

### Components (`components/`)

**Purpose:** Reusable UI components

**Rules:**
- Use TypeScript for all component props
- Add descriptive prop interfaces
- Use Shadcn/ui components as building blocks
- Keep components focused (single responsibility)
- Add accessibility attributes

**Example:**
```typescript
"use client";

interface TaskCardProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Task>) => void;
}

export function TaskCard({ task, onToggle, onDelete, onUpdate }: TaskCardProps) {
  return (
    <Card className="task-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <Checkbox
            checked={task.status === "completed"}
            onCheckedChange={() => onToggle(task.id)}
            aria-label={`Toggle task ${task.title}`}
          />
          <CardTitle>{task.title}</CardTitle>
        </div>
      </CardHeader>
    </Card>
  );
}
```

### Custom Hooks (`hooks/`)

**Purpose:** Reusable stateful logic

**Rules:**
- Return consistent shape: `{ data, isLoading, error }`
- Use TanStack Query for server state
- Handle loading and error states
- Provide optimistic updates for mutations
- Type all return values

**Example:**
```typescript
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function useTasks() {
  const queryClient = useQueryClient();

  // Fetch tasks
  const { data, isLoading, error } = useQuery({
    queryKey: ["tasks"],
    queryFn: fetchTasks,
  });

  // Toggle task status with optimistic update
  const toggleMutation = useMutation({
    mutationFn: toggleTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const previousTasks = queryClient.getQueryData<Task[]>(["tasks"]);

      queryClient.setQueryData<Task[]>(["tasks"], (old) =>
        old?.map((t) =>
          t.id === taskId
            ? { ...t, status: t.status === "pending" ? "completed" : "pending" }
            : t
        )
      );

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(["tasks"], context.previousTasks);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  return {
    tasks: data || [],
    isLoading,
    error,
    toggleTask: toggleMutation.mutate,
  };
}
```

### API Functions (`lib/api/`)

**Purpose:** Typed API calls

**Rules:**
- Use typed return values
- Handle errors gracefully
- Use fetch or axios for HTTP requests
- Return typed responses

**Example:**
```typescript
export async function fetchTasks(): Promise<Task[]> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`);
  if (!response.ok) {
    throw new Error("Failed to fetch tasks");
  }
  return response.json();
}

export async function createTask(task: TaskCreate): Promise<Task> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  if (!response.ok) {
    throw new Error("Failed to create task");
  }
  return response.json();
}
```

### Utility Functions (`lib/`)

**Purpose:** Pure functions for data transformation

**Rules:**
- Keep functions pure (no side effects)
- Type all parameters and return values
- Add JSDoc comments for complex logic
- Export functions for reusability

**Example:**
```typescript
/**
 * Format a date string to a localized format
 * @param date - Date to format
 * @param format - Output format (default: 'short')
 * @returns Formatted date string
 */
export function formatDate(date: Date | string, format: "short" | "long" = "short"): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;

  if (format === "long") {
    return dateObj.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  return dateObj.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}
```

## Common Patterns

### Server vs Client Components

**Server Component (Default):**
```typescript
// No "use client" directive
// Can fetch data directly, no hooks
export default function TasksPage() {
  const tasks = await fetchTasks(); // Direct fetch

  return (
    <div>
      <h1>My Tasks</h1>
      <TaskList tasks={tasks} /> {/* Client Component */}
    </div>
  );
}
```

**Client Component:**
```typescript
"use client"; // Required for hooks and interactivity
import { useState } from "react";

export function TaskList({ tasks }: { tasks: Task[] }) {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  return (
    <div>
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} onSelect={setSelectedTask} />
      ))}
    </div>
  );
}
```

### Form Validation with Zod + React Hook Form

```typescript
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title too long"),
  description: z.string().max(2000).nullable(),
  priority: z.enum(["low", "medium", "high"]),
});

type TaskFormData = z.infer<typeof taskSchema>;

export function TaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: { title: "", description: null, priority: "medium" },
  });

  const onSubmit = (data: TaskFormData) => {
    createTask(data);
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register("title")} />
      {form.formState.errors.title && (
        <span className="text-red-500">{form.formState.errors.title.message}</span>
      )}
      <Button type="submit">Create Task</Button>
    </form>
  );
}
```

### Optimistic UI Updates

```typescript
const toggleMutation = useMutation({
  mutationFn: toggleTask,
  onMutate: async (taskId) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries({ queryKey: ["tasks"] });

    // Snapshot previous state
    const previousTasks = queryClient.getQueryData<Task[]>(["tasks"]);

    // Optimistically update
    queryClient.setQueryData<Task[]>(["tasks"], (old) =>
      old?.map((t) =>
        t.id === taskId
          ? { ...t, status: t.status === "pending" ? "completed" : "pending" }
          : t
      )
    );

    return { previousTasks };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(["tasks"], context.previousTasks);
    toast.error("Failed to update task");
  },
  onSuccess: () => {
    // Refresh to ensure consistency
    queryClient.invalidateQueries({ queryKey: ["tasks"] });
    toast.success("Task updated");
  },
});
```

### Accessibility Best Practices

```typescript
// Use semantic HTML
<button
  aria-label="Delete task"
  onClick={handleDelete}
  className="p-2 hover:bg-red-100 rounded"
>
  <Trash2 className="h-4 w-4" aria-hidden="true" />
</button>

// Add aria-live regions for dynamic updates
<div
  className="sr-only"
  aria-live="polite"
  aria-atomic="true"
>
  {`${pendingCount} pending tasks, ${completedCount} completed tasks`}
</div>

// Use role attributes
<Card
  role="article"
  aria-label={`Task: ${task.title}, status: ${task.status}`}
>
  {/* Card content */}
</Card>

// Keyboard navigation
<div
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      handleSelect();
    }
  }}
  role="button"
>
  Task item
</div>
```

## Testing Guidelines

### Unit Tests (Vitest + React Testing Library)

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { TaskCard } from "../TaskCard";

describe("TaskCard", () => {
  it("renders task title", () => {
    const task = { id: "1", title: "Test Task", status: "pending" };
    render(<TaskCard task={task} onToggle={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("calls onToggle when checkbox is clicked", async () => {
    const onToggle = vi.fn();
    const task = { id: "1", title: "Test Task", status: "pending" };

    render(<TaskCard task={task} onToggle={onToggle} onDelete={vi.fn()} />);

    const checkbox = screen.getByRole("checkbox");
    fireEvent.click(checkbox);

    expect(onToggle).toHaveBeenCalledWith("1");
  });
});
```

### Hook Tests

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { useTasks } from "../useTasks";

describe("useTasks", () => {
  it("fetches tasks on mount", async () => {
    const { result } = renderHook(() => useTasks());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.tasks).toBeDefined();
  });
});
```

## Common Mistakes to Avoid

### ❌ Don't Do This

```typescript
// 1. Fetching data directly in component
export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    fetch("/api/tasks").then(res => res.json()).then(setTasks);  // ❌ Manual fetch
  }, []);

  return <div>{tasks.map(...)}</div>;
}

// 2. Using .optional() instead of .nullable() for forms
const schema = z.object({
  description: z.string().optional()  // ❌ Type issues with React Hook Form
});

// 3. Not handling loading/error states
export function TaskList() {
  const { data } = useTasks();  // ❌ No loading/error handling

  return <div>{data.map(...)}</div>;
}

// 4. Using useState for server state
export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);  // ❌ Use TanStack Query instead

  return <div>{tasks.map(...)}</div>;
}
```

### ✅ Do This Instead

```typescript
// 1. Use custom hooks for data fetching
export function TaskList() {
  const { tasks, isLoading, error } = useTasks();  // ✓ Use custom hook

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorMessage message={error.message} />;

  return <div>{tasks.map(...)}</div>;
}

// 2. Use .nullable() for optional form fields
const schema = z.object({
  description: z.string().nullable()  // ✓ Correct with React Hook Form
});

// 3. Always handle loading/error states
export function TaskList() {
  const { tasks, isLoading, error } = useTasks();  // ✓ Handle all states

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorMessage message={error.message} />;

  return <div>{tasks.map(...)}</div>;
}

// 4. Use TanStack Query for server state
export function TaskList() {
  const { data: tasks } = useTasks();  // ✓ TanStack Query handles caching
  return <div>{tasks?.map(...)}</div>;
}
```

## Performance Considerations

- **Code Splitting:** Use Next.js dynamic imports for heavy components
- **Image Optimization:** Use Next.js Image component
- **Query Caching:** Configure TanStack Query stale-time and cache-time
- **Debouncing:** Debounce search inputs to reduce API calls
- **Virtualization:** Use react-virtual for long lists
- **Lazy Loading:** Load components on demand with React.lazy
- **Memoization:** Use React.memo for expensive renders

## Accessibility Considerations

- **Semantic HTML:** Use proper HTML elements (button, input, nav, etc.)
- **ARIA Labels:** Add aria-label to icon-only buttons
- **Keyboard Navigation:** Ensure all interactive elements are keyboard accessible
- **Focus Management:** Manage focus in modals and dialogs
- **Screen Reader Support:** Use aria-live for dynamic content updates
- **Color Contrast:** Ensure text meets WCAG AA standards (4.5:1)
- **Touch Targets:** Minimum 44x44px for mobile

## Quick Reference

### Run Development Server
```bash
npm run dev              # Start dev server on port 3000
npm run build           # Build for production
npm run start           # Start production server
```

### Code Quality
```bash
npm run lint            # Run ESLint
npm run format          # Format with Prettier
npm run type-check      # Run TypeScript type checking
```

### Testing
```bash
npm test                # Run unit tests with Vitest
npm run test:cov        # Run tests with coverage
npm run test:watch      # Run tests in watch mode
npm run test:e2e        # Run E2E tests with Playwright
```

### Shadcn UI Components
```bash
npx shadcn@latest add <component-name>  # Add a component
```

---

**Remember:** The goal is to maintain a clean, accessible, and performant codebase. When in doubt, follow existing patterns and ask for clarification.

## Active Technologies
- Next.js 15 (App Router)
- React 19
- TypeScript 5.7+
- Tailwind CSS
- Shadcn/ui (Radix UI)
- TanStack Query v5
- Framer Motion
- Recharts
- @dnd-kit
- cmdk
- @use-gesture/react
- date-fns
- Zustand
- Vitest + React Testing Library + Playwright

## Recent Changes
- Phase 3: Enhanced AI integration with MCP support
- 006-landing-page-ui: Added multiple views, animations, gestures, onboarding
- 007-ai-chatbot: Added AI chatbot integration
