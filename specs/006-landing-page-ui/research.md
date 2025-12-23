# Research & Technology Decisions: Landing Page and UI Enhancement Suite

**Feature**: `006-landing-page-ui`
**Date**: 2025-12-20
**Status**: Phase 0 Complete

## Overview

This document consolidates technology research, library selections, best practices, and architectural decisions for implementing a production-ready landing page and comprehensive UI enhancements. All decisions align with the project constitution and existing technology stack.

---

## 1. Animation Library: Framer Motion

### Decision

**Use Framer Motion** for all animations (landing page scroll effects, UI transitions, micro-interactions).

### Rationale

1. **Constitution Alignment**: Already compatible with Next.js 15 + React 19
2. **Production-Ready**: Used by major companies (Linear, Stripe, Vercel)
3. **Declarative API**: Animation variants match React component patterns
4. **Performance**: GPU-accelerated transforms, respects `prefers-reduced-motion`
5. **Scroll Animations**: Built-in `useScroll`, `useTransform`, `useInView` hooks ideal for landing page
6. **Bundle Size**: 37KB gzipped (acceptable for visual impact)

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| React Spring | Physics-based, smaller bundle | Less scroll animation support | ❌ Not ideal for landing page |
| GSAP | Powerful, mature | Proprietary license, larger API surface | ❌ Over-engineering |
| CSS Animations | Zero bundle cost | Imperative, harder to coordinate | ❌ Too limited for complex sequences |

### Implementation Pattern

```typescript
// Scroll-triggered landing page sections
import { motion, useInView } from 'framer-motion';

export function Section({ children }: { children: React.ReactNode }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {children}
    </motion.section>
  );
}

// Task completion confetti
import { motion } from 'framer-motion';

const confettiVariants = {
  hidden: { opacity: 0, scale: 0 },
  visible: {
    opacity: [0, 1, 1, 0],
    scale: [0, 1.2, 1, 0],
    y: [0, -20, -40, -60],
    transition: { duration: 1 }
  }
};
```

### Best Practices

- Use `useInView` with `once: true` to trigger animations once (performance)
- Define reusable animation variants in `lib/animations.ts`
- Respect `prefers-reduced-motion`: Provide `reduce-motion` variants
- Keep animations under 600ms for UI feedback (confetti can be 1s)
- Use GPU-accelerated properties: `transform`, `opacity` (not `width`, `height`)

---

## 2. Charting Library: Recharts

### Decision

**Use Recharts** for dashboard visualizations (7-day completion trend, priority breakdown).

### Rationale

1. **React-Native API**: Declarative components (`<LineChart>`, `<PieChart>`)
2. **Responsive**: Auto-resizes with parent container
3. **TypeScript Support**: Excellent type definitions
4. **Customizable**: Tailwind-compatible styling
5. **Bundle Size**: 96KB gzipped (reasonable for dashboard page)
6. **MIT License**: No licensing concerns

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| Chart.js | Mature, feature-rich | Imperative API, harder to integrate with React | ❌ Not React-idiomatic |
| Victory | React-native, accessible | Larger bundle (150KB+) | ❌ Heavier than needed |
| Tremor | Tailwind-first, beautiful | Opinionated styling, less flexible | ❌ Too opinionated |

### Implementation Pattern

```typescript
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

export function CompletionTrendChart({ data }: { data: CompletionData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis
          dataKey="date"
          tickFormatter={(date) => format(new Date(date), 'MMM d')}
          stroke="hsl(var(--muted-foreground))"
        />
        <YAxis stroke="hsl(var(--muted-foreground))" />
        <Tooltip
          content={<CustomTooltip />}
          cursor={{ stroke: 'hsl(var(--muted))' }}
        />
        <Line
          type="monotone"
          dataKey="completed"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          dot={{ fill: 'hsl(var(--primary))', r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Best Practices

- Use `ResponsiveContainer` for fluid layouts
- Use Tailwind CSS variables for theme consistency (`hsl(var(--primary))`)
- Custom tooltips for better UX
- Lazy load charts with `React.lazy()` (code splitting)
- Limit data points to 30 days max (performance)

---

## 3. Calendar Library: Custom Implementation

### Decision

**Build a custom calendar component** using native `Date` APIs + date-fns.

### Rationale

1. **Full Control**: Custom month/week/day views, drag-and-drop
2. **Bundle Size**: Avoid 100KB+ library for simple calendar grid
3. **Design System**: Match Shadcn/ui aesthetic exactly
4. **Performance**: Only render visible month (30-31 days)
5. **Integration**: Easier to integrate drag-and-drop (dnd-kit)

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| React Big Calendar | Feature-rich, mature | Large bundle (150KB+), opinionated styling | ❌ Over-engineering |
| React Calendar | Lightweight | Limited month-only view, no drag-and-drop | ❌ Missing features |
| FullCalendar | Industry standard | Huge bundle (300KB+), complex API | ❌ Overkill |

### Implementation Pattern

```typescript
import { startOfMonth, endOfMonth, eachDayOfInterval, isSameDay } from 'date-fns';

export function CalendarView({ tasks, onDateChange }: CalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const days = eachDayOfInterval({
    start: startOfMonth(currentMonth),
    end: endOfMonth(currentMonth)
  });

  const getTasksForDay = (day: Date) =>
    tasks.filter(task => task.due_date && isSameDay(new Date(task.due_date), day));

  return (
    <div className="grid grid-cols-7 gap-2">
      {days.map(day => (
        <CalendarDay
          key={day.toISOString()}
          date={day}
          tasks={getTasksForDay(day)}
          onTaskDrop={(taskId) => onDateChange(taskId, day)}
        />
      ))}
    </div>
  );
}
```

### Best Practices

- Use `date-fns` for date manipulation (already in dependencies)
- Lazy load calendar page with `React.lazy()` (not frequently accessed)
- Limit to ±12 months navigation (prevent unbounded rendering)
- Use `<DndContext>` from dnd-kit for drag-and-drop
- Virtual scrolling if user has 1000+ tasks (use `react-window`)

---

## 4. Drag-and-Drop Library: dnd-kit

### Decision

**Use dnd-kit** for kanban board drag-and-drop and task reordering.

### Rationale

1. **Modern**: Built for React 18+, hooks-based API
2. **Accessible**: Built-in keyboard navigation (WCAG compliant)
3. **Performance**: Uses CSS transforms (GPU-accelerated)
4. **Flexible**: Supports sortable lists, droppable zones, sensors
5. **TypeScript**: Excellent type support
6. **Bundle Size**: 45KB gzipped (reasonable)

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| React DnD | Mature, widely used | Older API, less performant | ❌ Legacy library |
| react-beautiful-dnd | Excellent UX | Deprecated (no React 18 support) | ❌ No longer maintained |
| Sortable.js | Vanilla JS, lightweight | Non-React API, harder integration | ❌ Not idiomatic |

### Implementation Pattern

```typescript
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, arrayMove } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Kanban Board: Drag between columns
export function KanbanBoard({ tasks, onStatusChange }: KanbanProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 } // Prevent accidental drags
    })
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      onStatusChange(active.id as string, over.id as TaskStatus);
    }
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-3 gap-4">
        {['pending', 'in_progress', 'completed'].map(status => (
          <KanbanColumn key={status} status={status} tasks={tasks.filter(t => t.status === status)} />
        ))}
      </div>
    </DndContext>
  );
}

// Sortable Task Card
function DraggableTaskCard({ task }: { task: Task }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <TaskCard task={task} />
    </div>
  );
}
```

### Best Practices

- Use `PointerSensor` with `activationConstraint` to prevent accidental drags
- Use `CSS.Transform.toString()` for smooth animations
- Optimistic updates: Update UI immediately, rollback on error
- Mobile: Use `TouchSensor` with `activationConstraint: { delay: 250, tolerance: 5 }`
- Accessibility: Ensure keyboard navigation works (Tab, Space, Arrow keys)

---

## 5. Mobile Gestures: use-gesture

### Decision

**Use @use-gesture/react** for mobile swipe interactions (swipe-to-delete, swipe-to-complete).

### Rationale

1. **React Hooks**: `useSwipe`, `useDrag` hooks API
2. **Touch-Optimized**: Handles touch events, prevents scroll conflicts
3. **Configurable**: Thresholds, velocity, direction
4. **Lightweight**: 12KB gzipped
5. **Framework-Agnostic**: Works with Framer Motion

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| Swiper | Feature-rich carousel | Overkill for swipe gestures | ❌ Too heavy |
| react-swipeable | Simple, lightweight | Less control over physics | ❌ Limited |
| Hammer.js | Mature | Vanilla JS, larger bundle | ❌ Not React-idiomatic |

### Implementation Pattern

```typescript
import { useSwipe } from '@use-gesture/react';
import { useSpring, animated } from '@react-spring/web';

export function SwipeableTaskCard({ task, onDelete, onToggle }: SwipeableProps) {
  const [{ x }, api] = useSpring(() => ({ x: 0 }));

  const bind = useSwipe(
    ({ down, movement: [mx], velocity: [vx], direction: [dx] }) => {
      // Swipe left (delete)
      if (!down && mx < -100 && dx < 0) {
        onDelete(task.id);
        return;
      }
      // Swipe right (toggle)
      if (!down && mx > 100 && dx > 0) {
        onToggle(task.id);
        return;
      }
      // Animate back to center
      api.start({ x: down ? mx : 0, immediate: down });
    },
    { axis: 'x', filterTaps: true, threshold: 10 }
  );

  return (
    <animated.div {...bind()} style={{ x }} className="relative">
      <TaskCard task={task} />
      <div className="absolute inset-y-0 left-0 bg-red-500 text-white flex items-center px-4">
        Delete
      </div>
      <div className="absolute inset-y-0 right-0 bg-green-500 text-white flex items-center px-4">
        Complete
      </div>
    </animated.div>
  );
}
```

### Best Practices

- Use `threshold: 10` to prevent accidental swipes during scrolling
- Use `filterTaps: true` to prevent tap events from triggering swipes
- Animate `x` property only (GPU-accelerated)
- Show action hints (colored backgrounds) during swipe
- Require 100px+ swipe distance for confirmation (prevent accidents)

---

## 6. Command Palette Library: cmdk

### Decision

**Use cmdk** (Command Menu by Paco Coursey) for keyboard shortcuts and command palette.

### Rationale

1. **Vercel-Approved**: Used in Vercel Dashboard, Linear, Raycast
2. **Accessible**: Full keyboard navigation, screen reader support
3. **Lightweight**: 15KB gzipped
4. **Fuzzy Search**: Built-in fuzzy matching
5. **Customizable**: Headless component (style with Tailwind)
6. **Shadcn/ui Integration**: Already used in Shadcn's command component

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| kbar | Feature-rich | Larger bundle (30KB) | ❌ Heavier |
| react-command-palette | Simple | Less maintained | ❌ Outdated |
| Custom | Full control | More work, less battle-tested | ❌ Reinventing wheel |

### Implementation Pattern

```typescript
import { Command } from 'cmdk';

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  return (
    <Command.Dialog open={open} onOpenChange={onOpenChange}>
      <Command.Input placeholder="Type a command or search..." />
      <Command.List>
        <Command.Empty>No results found.</Command.Empty>

        <Command.Group heading="Tasks">
          <Command.Item onSelect={() => createTask()}>
            <Plus className="mr-2 h-4 w-4" />
            Create Task
            <Command.Shortcut>N</Command.Shortcut>
          </Command.Item>
          <Command.Item onSelect={() => toggleFilter('today')}>
            <Calendar className="mr-2 h-4 w-4" />
            Show Today's Tasks
          </Command.Item>
        </Command.Group>

        <Command.Group heading="Views">
          <Command.Item onSelect={() => navigate('/tasks')}>
            List View
          </Command.Item>
          <Command.Item onSelect={() => navigate('/tasks/kanban')}>
            Kanban Board
          </Command.Item>
        </Command.Group>
      </Command.List>
    </Command.Dialog>
  );
}

// Global keyboard handler
export function useKeyboardShortcuts() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(true);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  return { open, setOpen };
}
```

### Best Practices

- Use `Command.Shortcut` to display shortcuts in UI
- Group actions by category (Tasks, Views, Settings)
- Register shortcuts in `lib/keyboard-shortcuts.ts` registry
- Prevent shortcuts when input focused: `if (document.activeElement instanceof HTMLInputElement) return;`
- Fuzzy search: cmdk handles this automatically

---

## 7. State Management: TanStack Query + Zustand

### Decision

**Use TanStack Query for server state** (existing) + **Zustand for client state** (new).

### Rationale

**TanStack Query (Already in Use)**:
- ✅ Handles API data fetching, caching, revalidation
- ✅ Optimistic updates for task mutations
- ✅ Automatic background refetching

**Zustand (New for Client State)**:
- ✅ Lightweight (3KB gzipped)
- ✅ TypeScript-first
- ✅ No boilerplate (simpler than Redux)
- ✅ Ideal for UI state (theme, sidebar open, onboarding progress)

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| Redux Toolkit | Mature, DevTools | Heavy (60KB), verbose | ❌ Over-engineering |
| Jotai | Atomic, React 18 | Less ecosystem | ❌ Less proven |
| Recoil | Facebook-backed | Experimental API | ❌ Not stable |

### Implementation Pattern

```typescript
// Theme preference store (Zustand)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeStore {
  theme: string;
  accentColor: string;
  setTheme: (theme: string) => void;
  setAccentColor: (color: string) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'system',
      accentColor: '#3b82f6',
      setTheme: (theme) => set({ theme }),
      setAccentColor: (accentColor) => set({ accentColor })
    }),
    { name: 'theme-storage' }
  )
);

// Server state (TanStack Query - existing pattern)
export function useTasks(filters: TaskFilters) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => fetchTasks(filters),
    staleTime: 30000 // Cache for 30s
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createTask,
    onMutate: async (newTask) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData(['tasks']);
      queryClient.setQueryData(['tasks'], (old: TaskListResponse) => ({
        ...old,
        tasks: [...old.tasks, { ...newTask, id: 'temp' }]
      }));
      return { previous };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      queryClient.setQueryData(['tasks'], context.previous);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });
}
```

### Best Practices

- **TanStack Query**: Use for all API data (tasks, tags, templates)
- **Zustand**: Use for UI state (theme, sidebar, tour progress)
- Persist theme preferences with `persist` middleware
- Use `queryKey` arrays for cache invalidation
- Optimistic updates: Update immediately, rollback on error

---

## 8. Date Handling: date-fns

### Decision

**Use date-fns** for date formatting, manipulation, and timezone handling.

### Rationale

1. **Modular**: Import only what you need (tree-shakeable)
2. **Functional**: Immutable date operations
3. **TypeScript**: Excellent type support
4. **Bundle Size**: 10-15KB gzipped (only used functions)
5. **Locale Support**: Optional locale imports
6. **Already in Dependencies**: No new dependency

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| Moment.js | Mature | Large (67KB), mutable | ❌ Deprecated |
| Day.js | Lightweight, Moment-like API | Less feature-rich | ❌ date-fns more complete |
| Luxon | Immutable, timezone support | Larger (62KB) | ❌ Overkill |

### Implementation Pattern

```typescript
import { format, formatDistanceToNow, isSameDay, addDays, startOfWeek, endOfWeek } from 'date-fns';

// Due date badge
export function DueDateBadge({ dueDate }: { dueDate: Date }) {
  const now = new Date();
  const isOverdue = dueDate < now && !isSameDay(dueDate, now);
  const isDueSoon = !isOverdue && addDays(now, 1) >= dueDate;

  return (
    <Badge variant={isOverdue ? 'destructive' : isDueSoon ? 'warning' : 'default'}>
      {formatDistanceToNow(dueDate, { addSuffix: true })}
    </Badge>
  );
}

// Smart date filters
export function useDateFilters() {
  const today = new Date();
  return {
    today: (task: Task) => task.due_date && isSameDay(new Date(task.due_date), today),
    thisWeek: (task: Task) =>
      task.due_date &&
      new Date(task.due_date) >= startOfWeek(today) &&
      new Date(task.due_date) <= endOfWeek(today),
    overdue: (task: Task) => task.due_date && new Date(task.due_date) < today
  };
}
```

### Best Practices

- Use `formatDistanceToNow` for relative dates ("2 days ago")
- Use `format(date, 'MMM d, yyyy')` for absolute dates
- Store dates in UTC on server, display in user's timezone
- Use `isSameDay` for "Today" filter (not string comparison)
- Import specific functions to minimize bundle size

---

## 9. Form Validation: React Hook Form + Zod

### Decision

**Continue using React Hook Form + Zod** for all form validation (existing pattern).

### Rationale

1. **Already in Use**: Existing pattern in CreateTaskDialog
2. **Type-Safe**: Zod schemas infer TypeScript types
3. **Performance**: Minimal re-renders
4. **Accessibility**: Built-in error messages, focus management
5. **Integration**: Works seamlessly with Shadcn/ui form components

### Best Practices

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(500).nullable(),
  priority: z.enum(['low', 'medium', 'high']),
  due_date: z.date().nullable(),
  tags: z.array(z.string()).max(10)
});

type TaskFormData = z.infer<typeof taskSchema>;

export function CreateTaskDialog() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      description: null,
      priority: 'medium',
      due_date: null,
      tags: []
    }
  });

  const onSubmit = (data: TaskFormData) => {
    createTask(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {/* Fields */}
      </form>
    </Form>
  );
}
```

---

## 10. Landing Page Best Practices

### Decisions

Based on landing page performance research and conversion optimization:

#### Performance Optimizations

1. **Above-the-Fold Priority**: Critical CSS inline, defer non-critical JS
2. **Image Optimization**: Next.js `<Image>` with `priority` for hero images
3. **Font Loading**: Use `next/font` with `display: swap`
4. **Lazy Loading**: Sections below fold with `IntersectionObserver`
5. **Prefetching**: Prefetch signup page on CTA hover

#### Conversion Best Practices

1. **Hero Section**:
   - Clear value proposition (10 words max)
   - Prominent CTA (above fold, contrasting color)
   - Social proof (testimonial count, star rating)

2. **Features Section**:
   - 6-8 features max
   - Icon + Title + 1-2 sentence description
   - Benefit-focused (not feature-focused)

3. **Demo Section**:
   - Interactive (not static screenshot)
   - Tabbed views (List/Kanban/Calendar/Dashboard)
   - Auto-play demo or click-to-interact

4. **Testimonials**:
   - Real names + roles + avatars (builds trust)
   - Specific outcomes (not vague praise)
   - 3-5 testimonials rotating

5. **Pricing**:
   - 2 tiers max for MVP (Free + Premium)
   - Highlight recommended tier
   - Annual billing option (save 20%)

6. **CTA Strategy**:
   - Repeat CTA every 2-3 sections
   - Action-oriented copy ("Start Building" not "Learn More")
   - Low friction (no credit card for free tier)

---

## Summary of Technology Decisions

| Category | Technology | Bundle Size | Rationale |
|----------|-----------|-------------|-----------|
| **Animations** | Framer Motion | 37KB | Industry standard, excellent DX |
| **Charts** | Recharts | 96KB | React-idiomatic, customizable |
| **Calendar** | Custom | 0KB (date-fns) | Full control, avoid 100KB+ libraries |
| **Drag & Drop** | dnd-kit | 45KB | Modern, accessible, performant |
| **Gestures** | @use-gesture/react | 12KB | Touch-optimized, configurable |
| **Command Palette** | cmdk | 15KB | Vercel-approved, accessible |
| **Client State** | Zustand | 3KB | Lightweight, TypeScript-first |
| **Server State** | TanStack Query | (existing) | Already in use, proven |
| **Dates** | date-fns | 10-15KB | Modular, already in dependencies |
| **Forms** | React Hook Form + Zod | (existing) | Already in use, type-safe |

**Total New Bundle Impact**: ~218KB gzipped (acceptable for visual enhancement scope)

---

## Next Steps

✅ **Phase 0 Complete** - All technology decisions made and justified

➡️ **Phase 1**: Generate data-model.md, API contracts, quickstart.md

