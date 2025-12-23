# Todo App Frontend

A beautiful, feature-rich Next.js frontend for the Todo Application with comprehensive task management capabilities.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.7+
- **UI Library**: React 19
- **Styling**: Tailwind CSS
- **Components**: Shadcn/ui
- **State/Data Fetching**: TanStack Query v5
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Drag & Drop**: @dnd-kit
- **Command Palette**: cmdk
- **Mobile Gestures**: @use-gesture/react
- **Testing**: Vitest + React Testing Library + Playwright

## Features

### Core Task Management
- ✅ Create, read, update, delete tasks
- ✅ Task status tracking (pending, completed)
- ✅ Priority levels (low, medium, high)
- ✅ Due dates with timezone support
- ✅ Rich text notes for detailed task information
- ✅ Bulk operations (select multiple tasks)
- ✅ Soft delete with trash/restore functionality

### Organization & Filtering
- 🏷️ **Tags System**: Color-coded tags for categorization
- 🔍 **Global Search**: Instant search across titles, descriptions, and notes with highlighting
- ⚡ **Quick Filters**: One-click filters (Today, This Week, High Priority, Overdue)
- 📊 **Advanced Filters**: Status, priority, tags, due date ranges
- 🔢 **Subtasks**: Break down tasks into checklists with progress tracking

### Multiple Views
- 📋 **List View**: Classic list with expandable details
- 🎴 **Grid View**: Card-based layout for visual organization
- 📊 **Kanban Board**: Drag tasks between To Do, In Progress, Done columns
- 📅 **Calendar View**: Visualize tasks by due date with drag-to-reschedule
- 📈 **Dashboard**: Analytics with completion trends and priority breakdown charts

### Advanced Features
- 🔄 **Recurring Tasks**: Daily, weekly, monthly schedules with auto-generation
- 📝 **Task Templates**: Save and reuse task structures
- ⌨️ **Keyboard Shortcuts**: Command palette (Cmd/Ctrl+K) and navigation shortcuts
- 🎨 **Theme Picker**: Multiple color themes with dark mode support
- 📱 **Mobile Optimized**: Swipe gestures, bottom navigation, responsive design
- 🎓 **Onboarding Tour**: Guided tour for new users with spotlight highlights
- ✨ **Animations**: Smooth transitions respecting prefers-reduced-motion

### UI/UX Polish
- 💀 **Empty States**: Illustrated placeholders with contextual CTAs
- ⏳ **Loading Skeletons**: Smooth loading experiences
- 🎯 **Optimistic Updates**: Instant UI feedback with rollback on error
- ♿ **Accessibility**: ARIA labels, keyboard navigation, screen reader support

## Setup

### Prerequisites

- Node.js 22+
- npm or pnpm

### Local Development

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env.local`:

   ```bash
   cp .env.example .env.local
   ```

   Configure the following variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run the development server**:

   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:3000.

## Available Scripts

### Development
- `npm run dev` - Start development server on port 3000
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Testing
- `npm test` - Run unit tests with Vitest
- `npm run test:cov` - Run tests with coverage report
- `npm run test:watch` - Run tests in watch mode
- `npm run test:e2e` - Run E2E tests with Playwright
- `npm run type-check` - Run TypeScript type checking

### Code Quality
- **Linting**: `npm run lint` - Check for code issues
- **Formatting**: `npm run format` - Auto-format code
- **Type Checking**: `npm run type-check` - Verify TypeScript types

## Project Structure

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
└── styles/                      # Global styles
```

## Key Features Implementation

### Optimistic UI Updates
All mutations use TanStack Query's optimistic updates for instant feedback:

```typescript
const { mutate } = useMutation({
  mutationFn: toggleTask,
  onMutate: async (taskId) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries({ queryKey: ['tasks'] });

    // Snapshot previous state
    const previousTasks = queryClient.getQueryData(['tasks']);

    // Optimistically update UI
    queryClient.setQueryData(['tasks'], (old) => ({
      ...old,
      tasks: old.tasks.map(t =>
        t.id === taskId ? { ...t, status: 'completed' } : t
      )
    }));

    return { previousTasks };
  },
  onError: (err, variables, context) => {
    // Rollback on error
    queryClient.setQueryData(['tasks'], context.previousTasks);
  }
});
```

### Keyboard Shortcuts
- `Cmd/Ctrl + K` - Open command palette
- `N` - Create new task
- `E` - Edit selected task
- `Delete` - Delete selected task
- `Arrow Up/Down` - Navigate tasks
- `ESC` - Close dialogs/skip tour

### Drag and Drop
Uses @dnd-kit for accessible drag-and-drop:
- Drag tasks to reorder (when no filters active)
- Drag between Kanban columns to update status
- Drag calendar tasks to reschedule
- Long-press on mobile to activate drag

### Mobile Gestures
Uses @use-gesture/react for touch interactions:
- Swipe left to reveal delete action
- Swipe right to mark task complete
- Bottom navigation for easy access
- Floating action button for quick task creation

## Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Heavy components loaded on demand
- **Image Optimization**: Next.js Image component with lazy loading
- **Query Caching**: TanStack Query with stale-time configuration
- **Debounced Search**: 300ms debounce to reduce API calls
- **Optimistic Updates**: Instant UI feedback
- **Skeleton Loading**: Progressive content loading

## Accessibility Features

- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Screen reader announcements (aria-live regions)
- Focus management in dialogs
- prefers-reduced-motion support
- Minimum 44x44px tap targets on mobile
- Color contrast compliance (WCAG 2.1 AA)

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile Safari (iOS 15+)
- Chrome Mobile (Android 10+)

## Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_ONBOARDING=true
```

## Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Docker

Build and run with Docker:

```bash
docker build -t todo-frontend .
docker run -p 3000:3000 todo-frontend
```

Or use Docker Compose from the root directory:

```bash
docker-compose up frontend
```

## Troubleshooting

### Module Not Found Errors
```bash
rm -rf node_modules package-lock.json .next
npm install
```

### Type Errors
```bash
npm run type-check
```

### Port Already in Use
Change the port in package.json:
```json
"dev": "next dev -p 3001"
```

## Contributing

1. Follow the existing code structure
2. Use TypeScript strict mode
3. Add tests for new features
4. Run linting and type checking before committing
5. Follow the component naming conventions
6. Document complex logic with comments

## License

MIT
