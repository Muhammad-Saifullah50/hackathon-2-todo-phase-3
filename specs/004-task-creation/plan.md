# Implementation Plan: Task Creation

**Branch**: `004-task-creation` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-task-creation/spec.md`

## Summary

**Primary Requirement**: Enable authenticated users to create new tasks with title and optional description through a web API (POST /api/v1/tasks) and responsive modal-based UI interface.

**Technical Approach**:
- **Backend**: FastAPI route with service layer pattern, Pydantic v2 validation with custom word count validator, SQLModel ORM for database persistence
- **Frontend**: Next.js modal dialog using Shadcn UI, React Hook Form + Zod for real-time validation, TanStack Query for optimistic updates
- **Validation**: Triple-layer defense (frontend Zod, backend Pydantic, database constraints) with word count (50 max) and character limits (title 100, description 500)
- **Authentication**: JWT token extraction via existing `get_current_user()` dependency, user_id auto-set (never accepted in request)
- **Response Format**: Existing StandardizedResponse pattern with 201 Created status

---

## Technical Context

**Language/Version**:
- Backend: Python 3.13+
- Frontend: TypeScript 5.7+, Node 20+

**Primary Dependencies**:
- Backend: FastAPI 0.100+, SQLModel 0.0.8+, Pydantic v2, python-jose (JWT), uvicorn
- Frontend: Next.js 16, React 19, React Hook Form, Zod, TanStack Query v5, Shadcn/ui, Tailwind CSS, Axios

**Storage**:
- PostgreSQL 16+ (Neon, already provisioned in Feature 2)
- Existing Task and User tables (no schema migration needed)

**Testing**:
- Backend: pytest, pytest-asyncio, httpx (API tests), pytest-cov (coverage)
- Frontend: Vitest, React Testing Library, Playwright (E2E, deferred)

**Target Platform**:
- Backend: Linux server (containerized, port 8000)
- Frontend: Web (Next.js SSR, port 3000), responsive (mobile + desktop)

**Project Type**: Web application (separate frontend + backend)

**Performance Goals**:
- API response time: <200ms (p95)
- Task creation end-to-end: <5 seconds
- Frontend validation feedback: <100ms
- Bundle size: <200KB gzipped

**Constraints**:
- 100% test coverage (backend service + routes)
- WCAG 2.1 AA accessibility compliance
- Mobile-first responsive design (breakpoint: 768px)
- Keyboard-only navigation support

**Scale/Scope**:
- Initial target: 100 concurrent users
- Database: Supports 1000+ tasks per user efficiently
- Single API endpoint (POST)
- Single frontend modal component

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ **I. Architecture & Design - Separation of Concerns**
- **Status**: PASS
- Frontend (React) ↔ API (FastAPI) ↔ Service Layer (TaskService) ↔ Database (PostgreSQL)
- Clear contracts: OpenAPI schema, TypeScript types, Pydantic models
- Service layer is testable without HTTP (dependency injection)

### ✅ **II. Code Quality - Explicit & Self-Documenting**
- **Status**: PASS
- TypeScript strict mode + Python mypy strict mode enforced
- Type hints on all functions
- Explicit validation logic (no magic)

### ✅ **III. Testing - Test-Driven Development**
- **Status**: PASS
- Unit tests: TaskService validation logic, Pydantic validators
- Integration tests: API endpoint with test database
- Component tests: React Hook Form submission
- Target: 100% backend coverage, 80% frontend coverage

### ✅ **IV. Data Management - Single Source of Truth**
- **Status**: PASS
- PostgreSQL is canonical data store
- Triple-layer validation (frontend, backend, database)
- Atomic writes via SQLModel session
- Migration-based schema evolution (Alembic)

### ✅ **V. Error Handling - Clear & User-Friendly**
- **Status**: PASS
- Structured error responses (StandardizedResponse pattern)
- Field-specific validation errors
- Toast notifications for user feedback
- Backend logging with context (user_id, task_id)

### ✅ **VI. User Experience - Beautiful & Intuitive Web UI**
- **Status**: PASS
- Shadcn Dialog with Radix UI primitives (accessible)
- Real-time validation feedback (mode: "onChange")
- Loading states ("Creating..." button text)
- Success/error toast notifications
- Keyboard shortcuts (Ctrl/Cmd+N to open)

### ✅ **VII. Performance & Scalability - Efficient by Design**
- **Status**: PASS
- Optimistic UI updates (instant feedback)
- Code splitting (dynamic imports)
- Database indexes on user_id, status, created_at
- Async I/O (FastAPI async endpoints)

### ✅ **VIII. Security & Safety - Secure by Default**
- **Status**: PASS
- JWT authentication required
- user_id extracted from token (prevents privilege escalation)
- Input validation at all layers
- No SQL injection risk (SQLModel ORM)
- XSS prevention (React escapes by default)

### ✅ **IX. Python Standards - Modern & Professional**
- **Status**: PASS
- PEP 8 compliance (black formatter)
- Type hints (mypy strict)
- Dependency management (uv)

### ✅ **X. Development Workflow - Spec-Driven & Systematic**
- **Status**: PASS
- Spec → Plan → Tasks workflow followed
- Atomic commits
- Branch: 004-task-creation

### ✅ **XI. Frontend Architecture - Professional UI Generation**
- **Status**: PASS
- Next.js 16 (App Router), React 19
- Tailwind CSS + Shadcn/ui
- React Hook Form + Zod (type-safe validation)
- TanStack Query v5 (server state)
- TypeScript strict mode

### ✅ **XII. API Design & Backend Architecture**
- **Status**: PASS
- RESTful: POST /api/v1/tasks
- Service layer pattern (TaskService)
- OpenAPI 3.1 documentation (auto-generated)
- Pydantic v2 schemas
- Thin route handlers

### ✅ **XIII. Authentication & Authorization**
- **Status**: PASS (inherited from Feature 3)
- JWT Bearer authentication
- `get_current_user()` dependency
- Resource ownership enforced (user_id from token)

### ✅ **XIV. Database Architecture & Migration**
- **Status**: PASS
- PostgreSQL 16+ with UUID primary keys
- SQLModel ORM with async support
- Alembic migrations (no schema change needed)
- Proper indexes and constraints

### ✅ **XV. Web Security - OWASP Top 10 Compliance**
- **Status**: PASS
- Input validation (all layers)
- No user_id in request body (prevents forging)
- HTTPS in production (deployment concern)
- CORS configured (Feature 1)

### ✅ **XVI. Accessibility & Responsive Design**
- **Status**: PASS
- ARIA labels on form inputs
- Error descriptions via aria-describedby
- Keyboard navigation (Tab, Escape, Enter)
- Mobile-first (full-screen modal <768px, centered >=768px)
- Touch targets >=44px

### ✅ **XVII. Deployment & Infrastructure**
- **Status**: PASS (inherited from Feature 1)
- Containerized (Docker Compose)
- CI/CD ready

### ✅ **XVIII. Monitoring & Observability**
- **Status**: PASS
- Structured logging (INFO on success, ERROR on failure)
- Error tracking ready (Sentry integration TBD)

### ✅ **XIX. Performance Optimization**
- **Status**: PASS
- Optimistic updates (no wait for server)
- Lazy loading (modal not loaded until opened)
- Database query optimization (single INSERT)

### ✅ **XX. Type Safety & API Contracts**
- **Status**: PASS
- OpenAPI spec auto-generated from Pydantic
- TypeScript types generated from OpenAPI
- End-to-end type safety

**Overall Constitution Compliance**: ✅ **100% PASS** - No violations, no complexity justification needed

---

## Project Structure

### Documentation (this feature)

```text
specs/004-task-creation/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technical research and patterns
├── data-model.md        # Phase 1: Entity schemas and validation rules
├── quickstart.md        # Phase 1: Step-by-step implementation guide
├── contracts/
│   └── openapi.yaml     # Phase 1: API contract specification
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── tasks.md             # Phase 2: Generated by /sp.tasks (not yet created)
```

### Source Code (repository root)

**Structure Decision**: Web application pattern with separate frontend and backend directories

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py (existing)
│   │       ├── user.py (existing)
│   │       └── tasks.py (NEW - this feature)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py (existing)
│   │   ├── user.py (existing)
│   │   └── task.py (MODIFIED - add validators)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py (NEW - this feature)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── responses.py (existing)
│   ├── auth.py (existing - provides get_current_user)
│   ├── db/
│   │   └── session.py (existing)
│   └── main.py (MODIFIED - register tasks router)
└── tests/
    ├── unit/
    │   ├── test_models.py (MODIFIED - add validation tests)
    │   └── test_task_service.py (NEW - service layer tests)
    ├── integration/
    │   └── test_task_routes.py (NEW - API endpoint tests)
    └── conftest.py (existing - test fixtures)

frontend/
├── src/
│   ├── app/
│   │   ├── tasks/
│   │   │   └── page.tsx (MODIFIED - add CreateTaskDialog)
│   │   └── layout.tsx (existing)
│   ├── components/
│   │   ├── ui/ (Shadcn components - existing)
│   │   └── tasks/
│   │       └── CreateTaskDialog.tsx (NEW - main UI component)
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts (existing)
│   │   │   └── tasks.ts (NEW - API client functions)
│   │   └── schemas/
│   │       └── task.ts (NEW - Zod validation schemas)
│   ├── hooks/
│   │   └── useTasks.ts (NEW - React Query hooks)
│   └── types/
│       └── api.ts (GENERATED - from OpenAPI spec)
└── __tests__/
    └── components/
        └── CreateTaskDialog.test.tsx (NEW - component tests)
```

---

## Complexity Tracking

**No complexity violations detected.** This feature follows all constitution principles without exceptions.

---

## Implementation Phases (Completed by /sp.plan)

### ✅ Phase 0: Research & Technical Unknowns (Completed)

**Output**: `research.md`

**Resolved Topics**:
1. Pydantic v2 validation patterns for word count → Custom `@field_validator` with regex
2. React Hook Form + Zod integration → `mode: "onChange"` for real-time feedback
3. TanStack Query optimistic updates → `onMutate` with temporary IDs, `onError` rollback
4. FastAPI service layer pattern → TaskService class with dependency injection
5. Shadcn Dialog component usage → Controlled state with keyboard shortcuts
6. Error response format → Existing StandardizedResponse with details array
7. Database constraints strategy → Both DB constraints and application validation
8. Mobile responsiveness → Full-screen <768px, centered modal >=768px

**Key Decisions**:
- Word count: `/\s+/` regex split, both char (100) and word (50) limits enforced
- Priority default: MEDIUM (not null) for simpler UI
- Status: NOT accepted in request, always PENDING
- Optimistic updates: Enabled by default for better UX

---

### ✅ Phase 1: Design & Contracts (Completed)

**Output**: `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

#### Data Model

**Entities**:
- **Task** (modified): Added Pydantic validators for title/description
- **User** (read-only): Accessed via JWT token

**Request Schema** (TaskCreate):
```python
- title: str (required, 1-100 chars, 1-50 words)
- description: str | None (optional, 0-500 chars)
- priority: TaskPriority | None (optional, defaults to MEDIUM)
# status and user_id NOT accepted
```

**Response Schema** (TaskResponse):
```python
- id: UUID
- title, description, status, priority
- user_id, created_at, updated_at, completed_at
```

**Validation Logic**:
- Trim whitespace on title and description
- Empty description → null
- Title: 1-100 chars AND 1-50 words (both must pass)
- Priority: Defaults to MEDIUM if not provided

#### API Contract

**Endpoint**: `POST /api/v1/tasks`

**Request**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "MEDIUM"
}
```

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": "uuid",
    "title": "Buy groceries",
    "status": "pending",
    ...
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data"
  },
  "details": [
    {"field": "title", "message": "Title must be 50 words or less"}
  ]
}
```

#### Quickstart Guide

**Backend Implementation**:
1. Update TaskCreate schema with validators
2. Create TaskService class
3. Create tasks.py route with POST endpoint
4. Register router in main.py
5. Write unit + integration tests

**Frontend Implementation**:
1. Generate TypeScript types from OpenAPI
2. Create API client (tasks.ts)
3. Create Zod schema (task.ts)
4. Create React Query hook (useTasks.ts)
5. Create CreateTaskDialog component
6. Add component to tasks page
7. Write component tests

**Testing Strategy**:
- Backend: pytest unit (validators, service) + integration (API)
- Frontend: Vitest component tests + manual testing
- E2E: Playwright (deferred to Feature 9)

---

## Next Steps

**After /sp.plan completion**:

1. **✅ Phase 0 (Research) - Completed**
   - ✅ Technical patterns identified
   - ✅ All unknowns resolved
   - ✅ research.md created

2. **✅ Phase 1 (Design) - Completed**
   - ✅ Data model documented
   - ✅ API contract specified
   - ✅ Quickstart guide written

3. **⏭️ Phase 2 (Tasks) - Next**
   - Run `/sp.tasks` to generate tasks.md
   - Break down implementation into atomic, testable tasks
   - Follow RED-GREEN-REFACTOR TDD cycle

4. **⏭️ Phase 3 (Implementation) - After Tasks**
   - Execute tasks from tasks.md
   - Run `/sp.implement` (optional, for guided execution)
   - Commit after each task completion

5. **⏭️ Phase 4 (Validation) - Before Merge**
   - All tests pass (100% backend, 80%+ frontend)
   - Code quality checks pass (ruff, black, mypy, ESLint, Prettier, tsc)
   - Manual testing complete
   - Code review approved

---

## Dependencies & Prerequisites

**Must Be Complete Before Starting**:
- ✅ Feature 1 (Project Setup): Docker Compose, Next.js + FastAPI infrastructure
- ✅ Feature 2 (Database Setup): Neon PostgreSQL, Task/User tables, SQLModel ORM
- ✅ Feature 3 (Authentication): Better Auth, JWT tokens, `get_current_user()` dependency

**External Dependencies**:
- Backend: FastAPI, SQLModel, Pydantic v2, python-jose, uvicorn
- Frontend: Next.js 16, React 19, React Hook Form, Zod, TanStack Query v5, Shadcn/ui, Tailwind
- Database: PostgreSQL 16+ (Neon)
- Auth: Better Auth (JWT tokens)

**Development Tools**:
- Backend: Python 3.13+, uv, ruff, black, mypy, pytest
- Frontend: Node 20+, npm/pnpm, ESLint, Prettier, TypeScript, Vitest

---

## Risk Assessment

### Low Risk
- ✅ Task model already exists (no schema migration)
- ✅ StandardizedResponse pattern already established
- ✅ Authentication already working
- ✅ All unknowns resolved in research phase

### Medium Risk
- ⚠️ Word count validation complexity (regex pattern) - **Mitigation**: Thoroughly tested in research phase
- ⚠️ Optimistic updates rollback logic - **Mitigation**: Well-documented pattern from TanStack Query

### Mitigated Risks
- ~~CORS issues~~ → Already configured in Feature 1
- ~~Database connection~~ → Already working in Feature 2
- ~~JWT authentication~~ → Already working in Feature 3

---

## Success Criteria (From Spec)

All success criteria from spec.md are addressed by this plan:

- **SC-001**: Users create task in <5s → Optimistic updates provide instant feedback
- **SC-002**: 90% first-attempt success → Real-time validation prevents errors
- **SC-003**: Validation feedback <100ms → `mode: "onChange"` provides instant feedback
- **SC-004**: 100 concurrent users → Async FastAPI + database connection pooling
- **SC-005**: 99.9% success rate → Error handling, logging, atomic transactions
- **SC-006**: Mobile = desktop UX → Responsive design (full-screen mobile, centered desktop)
- **SC-007**: Zero data loss → SQLModel transactions, atomic writes
- **SC-008**: Clear error messages → Field-specific validation errors
- **SC-009**: Keyboard-only navigation → Shadcn Dialog supports Tab, Escape, Enter
- **SC-010**: Form loads <1s → Lazy loading (modal not rendered until opened)

---

## Open Questions

**None.** All technical unknowns resolved in research phase. Ready to proceed to `/sp.tasks`.

---

**Plan Status**: ✅ **COMPLETE**

**Ready for**: `/sp.tasks` (task generation and breakdown)

**Constitution Compliance**: ✅ 100% PASS

**Phase 0 (Research)**: ✅ Complete
**Phase 1 (Design)**: ✅ Complete
**Phase 2 (Tasks)**: ⏭️ Next Step
