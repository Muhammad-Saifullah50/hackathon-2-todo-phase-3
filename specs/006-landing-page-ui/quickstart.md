# Landing Page & UI Enhancement Suite - Developer Quickstart

**Feature**: Landing Page and UI Enhancement Suite
**Branch**: `006-landing-page-ui`
**Specification**: [spec.md](./spec.md)
**Implementation Plan**: [plan.md](./plan.md)

## Overview

This feature adds a comprehensive landing page and UI enhancement suite to the task management application, including:
- **Landing Page**: Marketing-focused public page with hero, features, demo, testimonials
- **Phase 1 (P1)**: Due dates, tags, animations, search/filters
- **Phase 2 (P2)**: Dashboard analytics, kanban board, calendar view
- **Phase 3 (P3)**: Keyboard shortcuts, subtasks, notes, recurring tasks, templates, drag-and-drop
- **Phase 4 (P3)**: Mobile optimizations, themes, empty states, onboarding tour

## Prerequisites

Before starting implementation, ensure you have:
- ✅ Read [spec.md](./spec.md) completely
- ✅ Read [plan.md](./plan.md) completely
- ✅ Read [research.md](./research.md) for technology decisions
- ✅ Reviewed [data-model.md](./data-model.md) for database changes
- ✅ Examined API contracts in [contracts/](./contracts/)
- ✅ Verified project constitution compliance in plan.md

## Tech Stack Summary

### New Frontend Dependencies
```bash
cd frontend
npm install framer-motion recharts @dnd-kit/core @dnd-kit/sortable @use-gesture/react cmdk date-fns
```

### Backend Dependencies
```bash
cd backend
uv add sqlalchemy[asyncio] alembic
# No new external dependencies - using existing FastAPI + SQLModel
```

## Database Setup

### Run Migrations (8 new migrations)
```bash
cd backend

# Create migrations from data-model.md specifications
alembic revision --autogenerate -m "add due_date to tasks"
alembic revision --autogenerate -m "add notes and manual_order to tasks"
alembic revision --autogenerate -m "create tags table"
alembic revision --autogenerate -m "create task_tags join table"
alembic revision --autogenerate -m "create subtasks table"
alembic revision --autogenerate -m "create recurrence_patterns table"
alembic revision --autogenerate -m "create task_templates table"
alembic revision --autogenerate -m "create user_preferences and view_preferences tables"

# Apply migrations
alembic upgrade head

# Verify migrations
alembic current
```

**Important**: Review each auto-generated migration file and verify it matches the schemas in [data-model.md](./data-model.md) before running `alembic upgrade head`.

## Project Structure

### Backend Structure
```
backend/src/
├── models/
│   ├── task.py (EXTEND with due_date, notes, manual_order)
│   ├── tag.py (NEW)
│   ├── task_tag.py (NEW)
│   ├── subtask.py (NEW)
│   ├── recurrence_pattern.py (NEW)
│   ├── task_template.py (NEW)
│   ├── user_preferences.py (NEW)
│   └── view_preference.py (NEW)
├── schemas/
│   ├── task_schemas.py (EXTEND)
│   ├── tag_schemas.py (NEW)
│   ├── subtask_schemas.py (NEW)
│   ├── template_schemas.py (NEW)
│   ├── recurring_schemas.py (NEW)
│   └── preferences_schemas.py (NEW)
├── services/
│   ├── task_service.py (EXTEND with search, filters, due dates)
│   ├── tag_service.py (NEW)
│   ├── subtask_service.py (NEW)
│   ├── template_service.py (NEW)
│   ├── recurring_service.py (NEW)
│   └── preferences_service.py (NEW)
└── api/routes/
    ├── tasks.py (EXTEND)
    ├── tags.py (NEW)
    ├── subtasks.py (NEW)
    ├── templates.py (NEW)
    ├── recurring.py (NEW)
    ├── preferences.py (NEW)
    └── search.py (NEW)
```

### Frontend Structure
```
frontend/
├── app/
│   ├── page.tsx (NEW - Landing page)
│   ├── tasks/
│   │   ├── page.tsx (EXTEND with filters, search)
│   │   ├── layout.tsx (NEW - Tabs for views)
│   │   ├── dashboard/page.tsx (NEW)
│   │   ├── kanban/page.tsx (NEW)
│   │   └── calendar/page.tsx (NEW)
│   └── layout.tsx (EXTEND with theme provider)
├── components/
│   ├── landing/
│   │   ├── Hero.tsx (NEW)
│   │   ├── Features.tsx (NEW)
│   │   ├── Demo.tsx (NEW)
│   │   ├── Testimonials.tsx (NEW)
│   │   └── Pricing.tsx (NEW)
│   ├── tasks/
│   │   ├── TaskCard.tsx (EXTEND with tags, due date)
│   │   ├── TaskFilters.tsx (NEW)
│   │   ├── SearchBar.tsx (NEW)
│   │   ├── TagPicker.tsx (NEW)
│   │   ├── SubtaskList.tsx (NEW)
│   │   └── DueDatePicker.tsx (NEW)
│   ├── dashboard/
│   │   ├── StatsCards.tsx (NEW)
│   │   ├── CompletionChart.tsx (NEW)
│   │   └── PriorityBreakdown.tsx (NEW)
│   ├── kanban/
│   │   ├── KanbanBoard.tsx (NEW)
│   │   ├── KanbanColumn.tsx (NEW)
│   │   └── DraggableTaskCard.tsx (NEW)
│   ├── calendar/
│   │   ├── CalendarView.tsx (NEW)
│   │   └── CalendarTaskCard.tsx (NEW)
│   └── ui/
│       ├── command.tsx (NEW - cmdk component)
│       ├── theme-picker.tsx (NEW)
│       └── onboarding-tour.tsx (NEW)
├── hooks/
│   ├── useTasks.ts (EXTEND with filters)
│   ├── useTags.ts (NEW)
│   ├── useSubtasks.ts (NEW)
│   ├── useTemplates.ts (NEW)
│   ├── usePreferences.ts (NEW)
│   └── useKeyboardShortcuts.ts (NEW)
└── lib/
    ├── animations.ts (NEW - Framer Motion variants)
    └── theme-store.ts (NEW - Zustand store)
```

## Implementation Phases

### Phase 1: Foundation (Priority P1)
**Goal**: Due dates, tags, animations, search/filters

**Backend Tasks**:
1. Extend Task model with `due_date`, `notes`, `manual_order`
2. Create Tag, TaskTag, Subtask models
3. Create tag_service.py with CRUD operations
4. Add search and filter endpoints to tasks.py
5. Write tests for new endpoints (≥80% coverage)

**Frontend Tasks**:
1. Install dependencies: `framer-motion`, `date-fns`, `cmdk`
2. Create TagPicker, DueDatePicker components
3. Add TaskFilters component with status, priority, tag filters
4. Implement search bar with debouncing
5. Add animations to TaskCard (fade-in, slide-in)
6. Write E2E tests for filtering and search

**Landing Page**:
1. Create app/page.tsx with Hero, Features, Demo sections
2. Add scroll-triggered animations with Framer Motion
3. Implement responsive design (mobile-first)
4. Add testimonials and pricing sections
5. Write E2E tests for landing page navigation

### Phase 2: Advanced Views (Priority P2)
**Goal**: Dashboard analytics, kanban board, calendar view

**Backend Tasks**:
1. Add analytics endpoint for dashboard stats
2. Extend search endpoint with date range filtering
3. Write tests for analytics calculations

**Frontend Tasks**:
1. Install `recharts` for charts
2. Create Dashboard page with StatsCards, CompletionChart
3. Create KanbanBoard with @dnd-kit for drag-and-drop
4. Create CalendarView with custom implementation
5. Add tab navigation in tasks/layout.tsx
6. Write E2E tests for each view

### Phase 3: Power Features (Priority P3)
**Goal**: Keyboard shortcuts, subtasks, notes, recurring tasks, templates

**Backend Tasks**:
1. Create Subtask, RecurrencePattern, TaskTemplate models
2. Implement subtask_service.py with auto-completion logic
3. Implement recurring_service.py with cron-like scheduling
4. Implement template_service.py with apply/save operations
5. Write tests for business logic (≥80% coverage)

**Frontend Tasks**:
1. Create SubtaskList component with toggle and add
2. Add notes textarea to task detail modal
3. Implement command palette (Cmd/Ctrl+K) with cmdk
4. Create RecurringTaskDialog for pattern configuration
5. Create TemplateDialog for save/apply operations
6. Add drag-and-drop reordering for tasks
7. Write E2E tests for keyboard shortcuts and power features

### Phase 4: Mobile & Polish (Priority P3)
**Goal**: Mobile optimizations, themes, empty states, onboarding

**Backend Tasks**:
1. Create UserPreferences, ViewPreference models
2. Implement preferences_service.py for theme/view state
3. Write tests for preferences endpoints

**Frontend Tasks**:
1. Install `@use-gesture/react` for swipe gestures
2. Add SwipeableTaskCard for mobile (left=delete, right=complete)
3. Create ThemePicker with 4+ themes and custom accent colors
4. Implement Zustand store for theme state
5. Add empty state illustrations
6. Create OnboardingTour with spotlight overlays
7. Write E2E tests for mobile interactions and onboarding

## Key Development Patterns

### Backend: Soft Delete Pattern
```python
# All queries must filter out soft-deleted records
query = select(Task).where(Task.user_id == user_id, Task.deleted_at.is_(None))

# Soft delete by setting timestamp
task.deleted_at = datetime.now(timezone.utc)
```

### Backend: Service Layer Pattern
```python
# All business logic goes in service classes
class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tag(self, user_id: str, tag_data: TagCreate) -> Tag:
        # Validate uniqueness, create tag, return
        pass
```

### Frontend: Optimistic UI Updates
```typescript
const { mutate } = useMutation({
  mutationFn: (taskId: string) => api.patch(`/tasks/${taskId}/toggle`),
  onMutate: async (taskId) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries({ queryKey: ['tasks'] });

    // Snapshot previous state
    const previousTasks = queryClient.getQueryData(['tasks']);

    // Optimistically update cache
    queryClient.setQueryData(['tasks'], (old) => ({...}));

    return { previousTasks };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['tasks'], context.previousTasks);
  }
});
```

### Frontend: Server vs Client Components
```typescript
// Server Component (default) - No "use client"
export default function TasksPage() {
  return <div><TaskList /></div>;
}

// Client Component - Add "use client" directive
"use client";
export function TaskList() {
  const [page, setPage] = useState(1);
  const { data } = useTasks({ page });
  // ...
}
```

### Frontend: Animations with Framer Motion
```typescript
import { motion } from 'framer-motion';

export function TaskCard({ task }: { task: Task }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.3 }}
    >
      {/* Card content */}
    </motion.div>
  );
}
```

## Testing Requirements

### Backend Tests (≥80% coverage)
```bash
cd backend
pytest --cov=src tests/

# Target coverage:
# - models/: 90%+
# - services/: 85%+
# - api/routes/: 80%+
```

### Frontend Tests
```bash
cd frontend

# Unit tests with Vitest
npm test

# E2E tests with Playwright
npm run test:e2e

# Test critical flows:
# - Task creation with tags and due date
# - Search and filtering
# - Kanban drag-and-drop
# - Keyboard shortcuts
# - Mobile swipe gestures
# - Onboarding tour
```

## Performance Targets

- **Landing Page**: Lighthouse score 90+ (performance, accessibility, SEO)
- **Landing Page Load**: <3s on 3G connections
- **Search Results**: <300ms after last keystroke (debounced)
- **Animations**: Maintain 60fps on 2020+ devices (4GB+ RAM)
- **Tag Filtering**: <200ms for lists with up to 1000 tasks
- **Dashboard Load**: <500ms for analytics calculation

## Accessibility Requirements (WCAG 2.1 AA)

- All interactive elements must have proper ARIA labels
- Keyboard navigation must work for all features
- Color contrast ratios must meet WCAG 2.1 AA standards
- Screen reader support for all dynamic updates
- Focus management for modals and dialogs

## Security Considerations

- All API endpoints must validate JWT tokens
- Input validation with Pydantic (backend) and Zod (frontend)
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via React's automatic escaping
- CSRF protection for state-changing operations
- Rate limiting on search endpoints (300 req/min per user)

## Common Pitfalls

### Backend
- ❌ Forgetting to filter `deleted_at IS NULL` in queries
- ❌ Not using async/await consistently
- ❌ Missing transaction management for multi-table operations
- ❌ Not validating user ownership before updates/deletes

### Frontend
- ❌ Using "use client" unnecessarily (kills Server Components)
- ❌ Not implementing optimistic UI updates
- ❌ Forgetting to debounce search inputs
- ❌ Not handling loading and error states
- ❌ Missing accessibility attributes (aria-label, role)

## Development Workflow

1. **Start with Backend**:
   - Create database models and migrations
   - Implement service layer with business logic
   - Add API endpoints
   - Write tests (TDD: RED-GREEN-REFACTOR)

2. **Then Frontend**:
   - Create UI components (use Shadcn/ui as base)
   - Implement hooks for API integration
   - Add animations and interactions
   - Write E2E tests

3. **Iterate**:
   - Test integration between backend and frontend
   - Refine UX based on usability
   - Optimize performance
   - Review constitution compliance

## Resources

- **API Contracts**: [contracts/](./contracts/) - OpenAPI 3.1 specs for all endpoints
- **Data Model**: [data-model.md](./data-model.md) - Complete database schema
- **Research**: [research.md](./research.md) - Technology decisions and rationale
- **Specification**: [spec.md](./spec.md) - Complete feature requirements
- **Plan**: [plan.md](./plan.md) - Implementation strategy and architecture

## Getting Help

- Review the constitution at `.specify/memory/constitution.md`
- Check existing task management implementation in `005-task-management`
- Refer to CLAUDE.md for project-wide patterns
- Search codebase for similar patterns (e.g., existing form validation)

## Next Steps After Quickstart

1. Read all linked documentation files
2. Run `/sp.tasks` to generate detailed implementation tasks
3. Start with Phase 1 backend models and migrations
4. Follow TDD approach (write tests first)
5. Implement features incrementally per the phased plan

---

**Ready to start?** Run `/sp.tasks` to break down this plan into actionable implementation tasks.
