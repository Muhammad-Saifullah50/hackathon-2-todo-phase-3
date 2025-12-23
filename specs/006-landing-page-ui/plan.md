# Implementation Plan: Landing Page and UI Enhancement Suite

**Branch**: `006-landing-page-ui` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-landing-page-ui/spec.md`

## Summary

This feature transforms the task management application into a production-ready, visually stunning full-stack web application with a professional landing page and comprehensive UI enhancements. The implementation encompasses:

1. **Landing Page**: Animated hero section, features showcase, interactive product demos, testimonials, pricing, and CTAs designed to convert visitors to users
2. **Foundation Features** (P1): Due dates with visual indicators, tags system with color coding, animations and visual polish, global search and filters
3. **Advanced Views** (P2): Dashboard with statistics and charts, Kanban board with drag-and-drop, Calendar view with date visualization
4. **Power Features** (P3): Keyboard shortcuts with command palette, subtasks with progress tracking, task notes, recurring tasks, task templates, drag-and-drop reordering
5. **Mobile & Polish** (P3): Swipe gestures, bottom navigation, floating action button, theme picker with multiple palettes, enhanced empty states, onboarding tour

**Technical Approach**: Leverages Next.js 15 with React 19 for frontend, extends existing FastAPI backend with new endpoints and data models, adds Framer Motion for animations, implements comprehensive state management with TanStack Query, and ensures WCAG AA accessibility compliance throughout.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.7+ (strict mode)
- Backend: Python 3.13+

**Primary Dependencies**:
- Frontend Core: Next.js 15+ (App Router), React 19+, TypeScript 5.7+
- Styling: Tailwind CSS 4+, Shadcn/ui components, Lucide React icons
- Animations: Framer Motion (landing page scroll effects, UI transitions)
- Forms: React Hook Form + Zod validation
- State Management: TanStack Query v5 (server state), Zustand (client state)
- Backend Core: FastAPI 0.100+, SQLModel/SQLAlchemy 2.0+, Pydantic v2
- Charts: Recharts or Chart.js (dashboard visualizations)
- Calendar: React Big Calendar or custom implementation
- Drag & Drop: dnd-kit or React DnD
- Gestures: use-gesture (mobile swipe interactions)
- Command Palette: cmdk library
- Testing: Vitest + React Testing Library (frontend), pytest (backend), Playwright (E2E)

**Storage**:
- Database: PostgreSQL 16+ (Neon hosted)
- Migrations: Alembic for schema versioning
- Extended schema: New tables for tags, subtasks, templates, recurrence patterns, user preferences

**Testing**:
- Frontend: Vitest (unit), React Testing Library (component), Playwright (E2E)
- Backend: pytest with pytest-cov (≥80% coverage target)
- E2E: Playwright for critical user flows (landing page → signup → task creation → views)

**Target Platform**:
- Web application (responsive: desktop 1920px+, tablet 768px-1024px, mobile 320px-767px)
- Browsers: Chrome 90+, Safari 14+, Firefox 90+, Edge 90+ (last 2 versions)

**Project Type**: Web application (frontend + backend + database)

**Performance Goals**:
- Landing page: Lighthouse score 90+ (performance, accessibility, SEO)
- Landing page: Load <3s on 3G connections
- Search: Results <300ms after last keystroke
- Animations: Maintain 60fps on devices with 4GB+ RAM (2020+)
- Tag filtering: Results <200ms for lists with up to 1000 tasks
- Dashboard: Load stats/charts <2s for users with up to 1000 tasks
- Kanban drag-and-drop: Status update <500ms
- API response: p95 latency <200ms

**Constraints**:
- WCAG 2.1 AA accessibility compliance (mandatory)
- No hard limit on tags per user (recommend <30 for UX)
- Subtasks: Single-level only (no nested subtasks within subtasks)
- Calendar navigation: ±12 months from current month
- Animation performance: Respect `prefers-reduced-motion` media query
- Search: Client-side for MVP (server-side full-text search if performance degrades)
- Browser support: Modern browsers only (no IE11 polyfills)

**Scale/Scope**:
- 18 user stories across 4 priority phases
- 123 functional requirements
- 78 success criteria
- Extended data model: 10+ new entity types
- 30+ new API endpoints
- 50+ new React components
- Landing page: 8 major sections (hero, features, demo, details, testimonials, pricing, CTA, footer)
- Views: 4 task visualization modes (list, grid, kanban, calendar)
- Multiple frontend pages: Landing, Dashboard, Tasks (multiple views), Trash, Settings

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Architecture & Design - Separation of Concerns (PASS)

**Requirement**: Frontend ↔ API ↔ Business Logic ↔ Data Layer must be independent layers

**Assessment**:
- ✅ Landing page will be server component at root route (/) consuming existing auth API
- ✅ New API endpoints will extend existing FastAPI structure (thin routes → service layer)
- ✅ Business logic for tags, due dates, recurring tasks will live in service layer
- ✅ Data layer extensions will use SQLModel ORM with Alembic migrations
- ✅ All new features will use dependency injection pattern (FastAPI Depends)
- ✅ Frontend components will communicate via TanStack Query (no direct DB access)

**Evidence**: Existing codebase already follows this pattern (task_service.py, API routes in api/routes/, SQLModel models)

### ✅ Testing - Test-Driven Development (PASS)

**Requirement**: RED-GREEN-REFACTOR cycle, test pyramid (70% unit, 20% integration, 10% E2E), 80% backend coverage, 70% frontend coverage

**Assessment**:
- ✅ All new features will be implemented following TDD
- ✅ Backend: pytest with pytest-cov for services, API endpoints
- ✅ Frontend: Vitest for components, hooks, utilities
- ✅ E2E: Playwright for critical flows (landing page interaction, due date creation, tag filtering, kanban drag)
- ✅ Test pyramid will be maintained across new features

**Evidence**: Existing test infrastructure in place (backend/tests/, frontend/tests/)

### ✅ Data Management - Single Source of Truth (PASS)

**Requirement**: PostgreSQL with schema versioning, validation at all boundaries, atomic operations

**Assessment**:
- ✅ All new data (tags, due dates, subtasks, templates, preferences) will use PostgreSQL
- ✅ Alembic migrations will version all schema changes
- ✅ Validation at 3 layers: Frontend (React Hook Form + Zod), API (Pydantic), Database (constraints, foreign keys)
- ✅ Atomic operations via database transactions (SQLAlchemy session management)
- ✅ UUIDs for primary keys (existing pattern, prevents enumeration)
- ✅ Foreign keys enforce referential integrity

**Evidence**: Existing database setup with Neon PostgreSQL, Alembic migrations directory

### ✅ Error Handling - Clear & User-Friendly (PASS)

**Requirement**: Structured API errors, user-friendly frontend messages, detailed backend logs

**Assessment**:
- ✅ API errors will use existing FastAPI HTTPException pattern with structured responses
- ✅ Frontend will display errors via toast notifications (Shadcn/ui toast component)
- ✅ Form validation errors will show inline with clear messages
- ✅ Backend will log errors with context (request ID, user ID, stack trace)
- ✅ Graceful degradation for network failures (TanStack Query retry logic)

**Evidence**: Existing error handling in API routes, toast notification system already in use

### ✅ User Experience - Beautiful & Intuitive Web UI (PASS)

**Requirement**: Shadcn/ui + Tailwind design system, consistent visual hierarchy, interactive states, empty/error/loading states

**Assessment**:
- ✅ All components will use existing Shadcn/ui + Tailwind design system
- ✅ Landing page will follow design system with custom animations via Framer Motion
- ✅ All interactive elements will implement hover/focus/active/disabled states
- ✅ Empty states with illustrations for zero tasks, no search results, empty trash
- ✅ Loading states with skeleton loaders (already implemented in TaskListSkeleton)
- ✅ Success feedback via toast notifications and optimistic UI updates (TanStack Query)

**Evidence**: Existing Shadcn/ui components, Tailwind config, TaskList with loading/empty states

### ✅ Performance & Scalability - Efficient by Design (PASS)

**Requirement**: Code splitting, bundle size <200KB, image optimization, database indexes, caching, async I/O

**Assessment**:
- ✅ Next.js automatic code splitting for heavy components (charts, calendar)
- ✅ Image optimization via Next.js `<Image>` component for landing page assets
- ✅ Database indexes on user_id, status, due_date, tag relationships (will be added in migrations)
- ✅ TanStack Query provides built-in caching for API responses
- ✅ FastAPI async endpoints for I/O-bound operations
- ✅ Lazy loading for below-the-fold landing page sections

**Evidence**: Next.js 15 in use, existing async FastAPI endpoints

### ✅ Security & Safety - Secure by Default (PASS with Extensions)

**Requirement**: Input validation, authentication, HTTPS, CORS, CSRF, XSS prevention, rate limiting

**Assessment**:
- ✅ Input validation: All new forms will use React Hook Form + Zod (frontend) and Pydantic (backend)
- ✅ Authentication: Existing Better Auth system will protect all task management features
- ✅ Landing page: Publicly accessible (no auth required)
- ✅ Authorization: Users can only modify their own tasks/tags/preferences (existing pattern)
- ✅ XSS prevention: React escapes by default, Shadcn/ui components are safe
- ✅ CORS: Already configured in FastAPI middleware
- ✅ Rate limiting: Will be added for search and filter operations (new requirement)

**Evidence**: Existing Better Auth integration, CORS middleware in main.py

### ✅ Frontend Architecture - Professional UI Generation (PASS)

**Requirement**: Next.js 15 App Router, TypeScript strict, Shadcn/ui, TanStack Query, design system consistency

**Assessment**:
- ✅ Next.js 15 with App Router already in use
- ✅ TypeScript 5.7+ in strict mode
- ✅ Shadcn/ui components for all UI primitives
- ✅ TanStack Query v5 for server state (already in use for task fetching)
- ✅ Zustand for client state (will be added for theme preferences, UI state)
- ✅ Server Components by default, Client Components only when needed ("use client" directive)

**Evidence**: Existing Next.js setup, Shadcn/ui components, TanStack Query hooks (useTasks)

### ✅ API Design & Backend Architecture (PASS)

**Requirement**: RESTful principles, resource-oriented URLs, explicit schemas, thin routes, testable services

**Assessment**:
- ✅ New endpoints will follow existing REST pattern: `/api/v1/tags`, `/api/v1/tasks/{id}/subtasks`
- ✅ HTTP methods: GET (read), POST (create), PATCH (update), DELETE (delete)
- ✅ Pydantic schemas for all request/response types
- ✅ Pagination for large lists (existing pattern: page/limit query params)
- ✅ Filtering via query params (existing: status, sort_by)
- ✅ API routes will be thin (validation → service → response)
- ✅ OpenAPI documentation auto-generated by FastAPI

**Evidence**: Existing API structure in backend/src/api/routes/tasks.py

### ✅ Authentication & Authorization (PASS)

**Requirement**: Secure authentication, role-based access control, resource ownership checks

**Assessment**:
- ✅ Better Auth provides secure session management
- ✅ All API endpoints will use existing authentication dependency
- ✅ Resource ownership: Users can only access/modify their own tasks/tags/preferences (existing pattern in task_service.py)
- ✅ Landing page: No authentication required (publicly accessible marketing page)

**Evidence**: Existing Better Auth setup, get_current_user dependency in use

### ✅ Database Architecture & Migration (PASS with Extensions)

**Requirement**: PostgreSQL 16+, 3NF schema, UUIDs, foreign keys, migration tooling

**Assessment**:
- ✅ PostgreSQL 16+ via Neon (existing)
- ✅ Alembic for schema versioning (existing)
- ✅ New tables will use UUIDs (existing pattern in Task model)
- ✅ Foreign keys for referential integrity (user_id references, task_id references)
- ✅ Indexes on frequently queried columns (user_id, due_date, tag relationships)
- ✅ Check constraints for data validation (status enum, priority enum)
- ✅ Timestamps (created_at, updated_at) on all entities

**Evidence**: Existing SQLModel models with UUID primary keys, Alembic migrations directory

### ✅ Web Security - OWASP Top 10 Compliance (PASS)

**Requirement**: Input validation, XSS prevention, CSRF, CORS, rate limiting, HTTPS

**Assessment**:
- ✅ Input validation at all layers (React Hook Form + Zod, Pydantic, DB constraints)
- ✅ XSS prevention: React escapes by default, will sanitize user-generated content in task notes (DOMPurify if markdown support added)
- ✅ CSRF: Better Auth handles CSRF tokens
- ✅ CORS: Already configured with whitelist (no wildcard)
- ✅ Rate limiting: Will add for search/filter operations (new)
- ✅ HTTPS: Enforced in production (Vercel/Neon)
- ✅ No secrets in code (environment variables via .env)

**Evidence**: Existing security setup, CORS middleware, Better Auth CSRF handling

### ✅ Accessibility & Responsive Design (PASS)

**Requirement**: WCAG 2.1 AA compliance, keyboard navigation, semantic HTML, responsive breakpoints, mobile-first

**Assessment**:
- ✅ Semantic HTML: Existing components use proper elements (button, main, header)
- ✅ ARIA labels: Shadcn/ui components have built-in ARIA support
- ✅ Keyboard navigation: All interactive elements will be keyboard accessible
- ✅ Focus states: Tailwind `focus-visible:ring-2` pattern (existing)
- ✅ Color contrast: Design system maintains 4.5:1 ratio for text (existing)
- ✅ Screen readers: Proper heading hierarchy, live regions for dynamic updates
- ✅ Responsive: Tailwind breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
- ✅ Mobile-first: Default styles for mobile, layer on desktop (existing pattern)
- ✅ Touch targets: Minimum 44x44px on mobile (Shadcn/ui default)

**Evidence**: Existing responsive design, Shadcn/ui accessible components, aria-labels in TaskCard

### ✅ Deployment & Infrastructure (PASS)

**Requirement**: Docker, CI/CD, environment variables, production deployment strategy

**Assessment**:
- ✅ Docker: Can be added (optional for Vercel + Neon deployment)
- ✅ CI/CD: GitHub Actions will run tests, lint, type check on PR
- ✅ Environment variables: .env for local, Vercel environment variables for production
- ✅ Deployment: Vercel (frontend), existing backend deployment strategy
- ✅ Database: Neon PostgreSQL (already in use)

**Evidence**: Existing .env setup, Vercel-compatible Next.js project

### ✅ Monitoring & Observability (PASS)

**Requirement**: Structured logging, error tracking, performance monitoring, health checks

**Assessment**:
- ✅ Structured logging: Can add via FastAPI middleware (new)
- ✅ Error tracking: Can add Sentry integration (optional, future)
- ✅ Performance monitoring: Vercel Analytics for frontend (optional)
- ✅ Health checks: Can add `/health` endpoint (recommended)
- ✅ Core Web Vitals: Next.js automatically reports (existing)

**Evidence**: Next.js built-in performance monitoring, FastAPI logging capabilities

### ✅ Performance Optimization (PASS)

**Requirement**: Code splitting, bundle size, image optimization, database indexes, caching, async I/O

**Assessment**:
- ✅ Code splitting: Next.js automatic + React.lazy() for heavy components
- ✅ Bundle size: Next.js automatic tree-shaking and code splitting
- ✅ Image optimization: Next.js `<Image>` for landing page (new)
- ✅ Database indexes: Will add on user_id, due_date, tag relationships
- ✅ Caching: TanStack Query built-in cache, Redis optional for future
- ✅ Async I/O: FastAPI async endpoints (existing pattern)

**Evidence**: Next.js 15 optimizations, existing async FastAPI routes

### ✅ Type Safety & API Contracts (PASS)

**Requirement**: Pydantic schemas, OpenAPI spec, TypeScript types from OpenAPI, end-to-end type safety

**Assessment**:
- ✅ Backend schemas: Pydantic models for all request/response types
- ✅ OpenAPI spec: Auto-generated by FastAPI at `/openapi.json`
- ✅ Frontend types: Can generate TypeScript types from OpenAPI (optional, recommended)
- ✅ Zod schemas: Frontend validation mirrors backend Pydantic schemas
- ✅ Type safety: TypeScript strict mode (existing)

**Evidence**: Existing Pydantic schemas in backend/src/schemas/, TypeScript strict in frontend

### 📋 Constitution Check Summary

**Overall Status**: ✅ **PASS** - All constitutional requirements are met

**Justification**: This feature builds on an existing, well-architected full-stack application that already follows all constitutional principles. The new features extend existing patterns rather than introducing architectural changes. No violations or exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/006-landing-page-ui/
├── plan.md              # This file
├── research.md          # Technology decisions and best practices
├── data-model.md        # Extended schema and entity relationships
├── quickstart.md        # Developer onboarding guide
├── contracts/           # API endpoint specifications
│   ├── tags.yaml        # Tag CRUD endpoints
│   ├── due-dates.yaml   # Due date filtering endpoints
│   ├── subtasks.yaml    # Subtask management endpoints
│   ├── templates.yaml   # Task template endpoints
│   ├── recurring.yaml   # Recurring task endpoints
│   ├── preferences.yaml # User preference endpoints
│   └── search.yaml      # Search and filter endpoints
└── tasks.md             # Generated by /sp.tasks (not yet created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py                      # Extended with due_date, tags, notes, etc.
│   │   ├── tag.py                       # NEW: Tag model
│   │   ├── subtask.py                   # NEW: Subtask model
│   │   ├── task_template.py             # NEW: Task template model
│   │   ├── recurrence_pattern.py        # NEW: Recurrence pattern model
│   │   ├── user_preferences.py          # NEW: User preferences model
│   │   └── view_preference.py           # NEW: Saved filter configurations
│   ├── services/
│   │   ├── task_service.py              # Extended with due date, tag operations
│   │   ├── tag_service.py               # NEW: Tag CRUD and filtering
│   │   ├── subtask_service.py           # NEW: Subtask management
│   │   ├── template_service.py          # NEW: Template operations
│   │   ├── recurring_task_service.py    # NEW: Recurring task logic
│   │   ├── search_service.py            # NEW: Search and filter logic
│   │   └── preference_service.py        # NEW: User preference management
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py                 # Extended with subtasks, notes endpoints
│   │   │   ├── tags.py                  # NEW: Tag endpoints
│   │   │   ├── templates.py             # NEW: Template endpoints
│   │   │   ├── recurring.py             # NEW: Recurring task endpoints
│   │   │   ├── search.py                # NEW: Search endpoints
│   │   │   └── preferences.py           # NEW: Preference endpoints
│   │   └── dependencies.py              # Shared API dependencies
│   └── schemas/
│       ├── task_schemas.py              # Extended with due_date, tags, notes
│       ├── tag_schemas.py               # NEW: Tag request/response schemas
│       ├── subtask_schemas.py           # NEW: Subtask schemas
│       ├── template_schemas.py          # NEW: Template schemas
│       ├── recurring_schemas.py         # NEW: Recurring pattern schemas
│       └── preference_schemas.py        # NEW: Preference schemas
└── alembic/
    └── versions/
        ├── YYYYMMDD_add_due_dates.py           # NEW: Add due_date to tasks
        ├── YYYYMMDD_create_tags_table.py       # NEW: Tags table
        ├── YYYYMMDD_create_subtasks_table.py   # NEW: Subtasks table
        ├── YYYYMMDD_create_templates_table.py  # NEW: Templates table
        ├── YYYYMMDD_create_recurrence_table.py # NEW: Recurrence patterns table
        └── YYYYMMDD_create_preferences_table.py # NEW: User preferences table

frontend/
├── app/
│   ├── page.tsx                          # NEW: Landing page (root route)
│   ├── (landing)/
│   │   └── sections/
│   │       ├── Hero.tsx                  # NEW: Hero section component
│   │       ├── Features.tsx              # NEW: Features showcase
│   │       ├── ProductDemo.tsx           # NEW: Interactive demo tabs
│   │       ├── DelightfulDetails.tsx     # NEW: Micro-interactions showcase
│   │       ├── Testimonials.tsx          # NEW: User testimonials
│   │       ├── Pricing.tsx               # NEW: Pricing tiers
│   │       ├── CTA.tsx                   # NEW: Final call-to-action
│   │       └── Footer.tsx                # NEW: Footer with links
│   ├── dashboard/
│   │   └── page.tsx                      # NEW: Dashboard with stats/charts
│   ├── tasks/
│   │   ├── page.tsx                      # Existing: Task list
│   │   ├── layout.tsx                    # NEW: Task views layout
│   │   ├── kanban/
│   │   │   └── page.tsx                  # NEW: Kanban board view
│   │   ├── calendar/
│   │   │   └── page.tsx                  # NEW: Calendar view
│   │   └── trash/
│   │       └── page.tsx                  # Existing: Trash view
│   └── settings/
│       └── page.tsx                      # NEW: Settings (themes, preferences)
├── components/
│   ├── landing/
│   │   ├── AnimatedBackground.tsx        # NEW: Gradient animation
│   │   ├── FloatingTaskCard.tsx          # NEW: Parallax cards
│   │   └── InteractiveDemoWidget.tsx     # NEW: Live demo preview
│   ├── tasks/
│   │   ├── TaskList.tsx                  # Extended: Search bar
│   │   ├── TaskCard.tsx                  # Extended: Due date badge, tag badges
│   │   ├── TaskFilters.tsx               # Extended: Due date filters, tag filters
│   │   ├── CreateTaskDialog.tsx          # Extended: Due date picker, tag selector
│   │   ├── EditTaskDialog.tsx            # Extended: All new fields
│   │   ├── DueDatePicker.tsx             # NEW: Date picker component
│   │   ├── TagSelector.tsx               # NEW: Tag multi-select with create
│   │   ├── SubtaskList.tsx               # NEW: Subtask checklist
│   │   ├── TaskNotes.tsx                 # NEW: Expandable notes section
│   │   ├── RecurringTaskConfig.tsx       # NEW: Recurrence pattern selector
│   │   ├── TemplateSelector.tsx          # NEW: Template library
│   │   └── SearchBar.tsx                 # NEW: Global search with highlighting
│   ├── dashboard/
│   │   ├── StatCards.tsx                 # NEW: Pending/completed/overdue cards
│   │   ├── CompletionTrendChart.tsx      # NEW: 7-day line chart
│   │   ├── PriorityBreakdownChart.tsx    # NEW: Pie/donut chart
│   │   └── QuickAccessLinks.tsx          # NEW: Smart view shortcuts
│   ├── kanban/
│   │   ├── KanbanBoard.tsx               # NEW: Board layout
│   │   ├── KanbanColumn.tsx              # NEW: Column with count
│   │   └── DraggableTaskCard.tsx         # NEW: Drag handle + card
│   ├── calendar/
│   │   ├── CalendarView.tsx              # NEW: Month/week/day toggle
│   │   ├── CalendarDay.tsx               # NEW: Day cell with tasks
│   │   └── DayPanel.tsx                  # NEW: Task list for selected day
│   ├── commands/
│   │   ├── CommandPalette.tsx            # NEW: Cmd+K modal
│   │   └── KeyboardShortcutsHelp.tsx     # NEW: Shortcuts reference
│   ├── onboarding/
│   │   ├── OnboardingTour.tsx            # NEW: Spotlight tour
│   │   └── TourStep.tsx                  # NEW: Step with tooltip
│   ├── themes/
│   │   ├── ThemePicker.tsx               # NEW: Theme selection grid
│   │   └── AccentColorPicker.tsx         # NEW: Color picker
│   ├── mobile/
│   │   ├── BottomNav.tsx                 # NEW: Fixed bottom navigation
│   │   ├── FloatingActionButton.tsx      # NEW: FAB for task creation
│   │   └── SwipeableTaskCard.tsx         # NEW: Swipe gesture wrapper
│   └── ui/
│       ├── [existing Shadcn components]  # button, card, dialog, etc.
│       ├── date-picker.tsx               # NEW: Shadcn date picker
│       ├── command.tsx                   # NEW: Shadcn command (cmdk)
│       └── calendar.tsx                  # NEW: Shadcn calendar
├── hooks/
│   ├── useTasks.ts                       # Extended: Search, filter params
│   ├── useTags.ts                        # NEW: Tag CRUD hooks
│   ├── useSubtasks.ts                    # NEW: Subtask management
│   ├── useTemplates.ts                   # NEW: Template operations
│   ├── useRecurringTasks.ts              # NEW: Recurring task hooks
│   ├── useSearch.ts                      # NEW: Debounced search hook
│   ├── useKeyboardShortcuts.ts           # NEW: Global keyboard handler
│   ├── useTheme.ts                       # NEW: Theme preference hook
│   └── useOnboarding.ts                  # NEW: Tour state management
├── lib/
│   ├── api-client.ts                     # Extended: New endpoint helpers
│   ├── animations.ts                     # NEW: Framer Motion variants
│   └── keyboard-shortcuts.ts             # NEW: Shortcut registry
└── tests/
    ├── e2e/
    │   ├── landing-page.spec.ts          # NEW: Landing page E2E
    │   ├── due-dates.spec.ts             # NEW: Due date workflow
    │   ├── tags.spec.ts                  # NEW: Tag management
    │   ├── kanban.spec.ts                # NEW: Drag-and-drop
    │   └── calendar.spec.ts              # NEW: Calendar interactions
    ├── components/
    │   ├── landing/                      # NEW: Landing component tests
    │   ├── tasks/                        # Extended: New component tests
    │   ├── dashboard/                    # NEW: Dashboard tests
    │   ├── kanban/                       # NEW: Kanban tests
    │   └── calendar/                     # NEW: Calendar tests
    └── hooks/
        ├── useTags.test.ts               # NEW: Tag hook tests
        ├── useSubtasks.test.ts           # NEW: Subtask hook tests
        └── useSearch.test.ts             # NEW: Search hook tests
```

**Structure Decision**: This is a **Web Application** project with separate frontend and backend codebases. The existing structure already follows this pattern with `backend/` (FastAPI + SQLModel) and `frontend/` (Next.js + React). This plan extends both codebases with new routes, components, services, and models while maintaining the established separation of concerns.

## Complexity Tracking

> **Not required** - All constitution checks pass with no violations. This feature extends existing patterns without introducing architectural complexity.

---

*Next: Phase 0 - Research & Technology Decisions*
