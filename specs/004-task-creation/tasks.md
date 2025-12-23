---
description: "Task breakdown for Task Creation feature"
---

# Tasks: Task Creation

**Input**: Design documents from `/specs/004-task-creation/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Included (100% backend coverage target per constitution requirement)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend tests: `backend/tests/`
- Frontend tests: `frontend/__tests__/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of prerequisites

- [ ] T001 Verify backend dependencies installed (FastAPI, SQLModel, Pydantic v2, pytest)
- [ ] T002 [P] Verify frontend dependencies installed (Next.js 16, React 19, React Hook Form, Zod, TanStack Query v5, Shadcn/ui)
- [ ] T003 [P] Verify Task and User models exist in backend/src/models/
- [ ] T004 [P] Verify authentication working (get_current_user dependency exists in backend/src/auth.py)
- [ ] T005 Verify database connection working (Neon PostgreSQL, can run migrations)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create TaskService class skeleton in backend/src/services/task_service.py
- [ ] T007 [P] Create StandardizedResponse usage pattern documentation (verify existing pattern from Feature 2)
- [ ] T008 [P] Install shadcn/ui components: Dialog, Button, Input, Textarea, Select, Label in frontend/src/components/ui/
- [ ] T009 [P] Setup React Query QueryClient in frontend/src/app/layout.tsx (if not already configured)
- [ ] T010 Configure axios interceptor for JWT tokens in frontend/lib/api/client.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create First Task via Web Interface (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create a task with title and optional description through a modal interface

**Independent Test**: Authenticate as user, open task creation modal, enter title "Buy groceries", submit, and verify task appears in task list with correct data (title, status=pending, timestamps)

### Backend Implementation for User Story 1

**Models & Validation**

- [ ] T011 [P] [US1] Add Pydantic validators to TaskCreate schema in backend/src/models/task.py:
  - `@field_validator('title')`: trim whitespace, check not empty, max 100 chars, max 50 words (regex `/\s+/`)
  - `@field_validator('description')`: trim whitespace, empty→null, max 500 chars

**Service Layer**

- [ ] T012 [US1] Implement TaskService.create_task method in backend/src/services/task_service.py:
  - Accept TaskCreate and user_id
  - Create Task instance (status=PENDING, priority=MEDIUM default, user_id from param)
  - session.add(), await commit(), await refresh()
  - Return Task instance

**API Route**

- [ ] T013 [US1] Create POST /api/v1/tasks endpoint in backend/src/api/routes/tasks.py:
  - Accept TaskCreate request body
  - Use get_current_user() dependency for authentication
  - Call TaskService.create_task()
  - Return StandardizedResponse with 201 Created
  - Error handling: 400 validation, 401 unauthorized, 500 server error

- [ ] T014 [US1] Register tasks router in backend/src/main.py (app.include_router)

**Backend Tests**

- [ ] T015 [P] [US1] Write unit tests for TaskCreate validators in backend/tests/unit/test_models.py:
  - test_title_validation_empty
  - test_title_validation_too_long_chars
  - test_title_validation_too_many_words
  - test_description_validation_too_long
  - test_description_trim_and_null

- [ ] T016 [P] [US1] Write unit tests for TaskService.create_task in backend/tests/unit/test_task_service.py:
  - test_create_task_success
  - test_create_task_default_priority
  - test_create_task_sets_pending_status
  - test_create_task_sets_user_id

- [ ] T017 [US1] Write integration tests for POST /api/v1/tasks in backend/tests/integration/test_task_routes.py:
  - test_create_task_success_with_auth
  - test_create_task_validation_error
  - test_create_task_unauthorized
  - test_create_task_minimal_title_only
  - test_create_task_with_description

**Run Backend Tests**

- [ ] T018 [US1] Run backend tests and verify 100% coverage: pytest backend/tests/ --cov=backend/src

### Frontend Implementation for User Story 1

**API Client & Types**

- [ ] T019 [P] [US1] Generate TypeScript types from OpenAPI in frontend/src/types/api.ts:
  - Run: npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts

- [ ] T020 [P] [US1] Create API client for tasks in frontend/lib/api/tasks.ts:
  - Define CreateTaskRequest, Task, ApiResponse interfaces
  - Implement createTask(data: CreateTaskRequest) function with axios

**Validation & Schemas**

- [ ] T021 [P] [US1] Create Zod schema in frontend/lib/schemas/task.ts:
  - createTaskSchema with title (1-100 chars, 1-50 words), description (0-500 chars), priority enum
  - Export CreateTaskForm type

**React Query Hooks**

- [ ] T022 [US1] Create useCreateTask hook in frontend/hooks/useTasks.ts:
  - useMutation with createTask mutationFn
  - Toast notifications on success/error
  - Query invalidation on success

**UI Components**

- [ ] T023 [US1] Create CreateTaskDialog component in frontend/components/tasks/CreateTaskDialog.tsx:
  - Dialog with controlled open state
  - React Hook Form with zodResolver and mode: "onChange"
  - Form fields: title (Input), description (Textarea), priority (Select - hidden for MVP)
  - Submit button with loading state
  - Cancel button
  - Keyboard shortcut: Ctrl/Cmd+N to open modal
  - Unsaved changes warning on close

- [ ] T024 [US1] Add CreateTaskDialog to tasks page in frontend/app/tasks/page.tsx:
  - Import and render CreateTaskDialog component
  - "Add Task" button in page header

**Frontend Tests**

- [ ] T025 [P] [US1] Write component tests for CreateTaskDialog in frontend/__tests__/components/CreateTaskDialog.test.tsx:
  - test_renders_form_fields
  - test_validates_title_required
  - test_validates_title_max_length
  - test_creates_task_on_submit
  - test_closes_on_cancel

**Manual Testing**

- [ ] T026 [US1] Manual test: Create task with title only, verify success
- [ ] T027 [US1] Manual test: Create task with title and description, verify both saved
- [ ] T028 [US1] Manual test: Submit empty form, verify validation error
- [ ] T029 [US1] Manual test: Enter 101-char title, verify validation error

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via modal UI

---

## Phase 4: User Story 2 - Create Task with Validation Feedback (Priority: P1)

**Goal**: Provide real-time validation feedback as users type in the task creation form

**Independent Test**: Open task creation form, enter invalid inputs (too long title, exceeding limits), verify real-time validation messages appear without form submission

### Frontend Enhancements for User Story 2

**Real-Time Validation**

- [ ] T030 [US2] Update CreateTaskDialog to show inline validation errors in frontend/components/tasks/CreateTaskDialog.tsx:
  - Display errors.title.message below title input
  - Display errors.description.message below description textarea
  - Add aria-invalid and aria-describedby attributes
  - Ensure mode: "onChange" is set for instant feedback

**Validation UX Improvements**

- [ ] T031 [US2] Add character count indicators in frontend/components/tasks/CreateTaskDialog.tsx:
  - Show "X/100 characters" below title field
  - Show "X/500 characters" below description field
  - Update color to warning when approaching limits

**Frontend Tests**

- [ ] T032 [P] [US2] Write validation tests in frontend/__tests__/components/CreateTaskDialog.test.tsx:
  - test_shows_title_too_long_error_realtime
  - test_shows_title_too_many_words_error_realtime
  - test_shows_description_too_long_error_realtime
  - test_error_disappears_on_correction

**Manual Testing**

- [ ] T033 [US2] Manual test: Type 101 characters in title, verify instant error
- [ ] T034 [US2] Manual test: Type 51 words in title, verify instant error
- [ ] T035 [US2] Manual test: Correct invalid input, verify error disappears

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users get instant validation feedback

---

## Phase 5: User Story 3 - Create Task with Optimistic UI Updates (Priority: P2)

**Goal**: Provide instant UI feedback by showing tasks immediately upon submission, even before server responds

**Independent Test**: Create a task and observe it appears in the list immediately upon submission, even before the server responds. If network is slow or fails, verify appropriate error handling and rollback.

### Frontend Optimistic Updates for User Story 3

**React Query Optimistic Pattern**

- [ ] T036 [US3] Add optimistic updates to useCreateTask in frontend/hooks/useTasks.ts:
  - Implement onMutate: cancel queries, snapshot previous state, generate temp UUID, add optimistic task to cache
  - Implement onError: rollback to previous state, show error toast
  - Implement onSuccess: invalidate queries to refetch, show success toast

**Frontend Tests**

- [ ] T037 [P] [US3] Write optimistic update tests in frontend/__tests__/hooks/useTasks.test.tsx:
  - test_task_appears_immediately_on_submit
  - test_optimistic_task_replaced_on_success
  - test_optimistic_task_removed_on_error

**Manual Testing**

- [ ] T038 [US3] Manual test: Create task with backend running, verify instant UI update
- [ ] T039 [US3] Manual test: Stop backend, create task, verify optimistic task appears then removed with error
- [ ] T040 [US3] Manual test: Throttle network (browser DevTools), verify task appears before server response

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - users get instant feedback even with network latency

---

## Phase 6: User Story 4 - Create Task with Priority Setting (Priority: P3)

**Goal**: Allow users to optionally set priority (LOW, MEDIUM, HIGH) when creating a task

**Independent Test**: Create tasks with and without priority selection, verify tasks without explicit priority default to MEDIUM, and that selected priorities are saved correctly.

### Frontend Priority Feature for User Story 4

**UI Component Updates**

- [ ] T041 [US4] Show priority Select field in CreateTaskDialog in frontend/components/tasks/CreateTaskDialog.tsx:
  - Add Select with options: Low, Medium, High
  - Show placeholder "Select priority (default: Medium)"
  - Make field optional

**Frontend Tests**

- [ ] T042 [P] [US4] Write priority tests in frontend/__tests__/components/CreateTaskDialog.test.tsx:
  - test_priority_defaults_to_medium
  - test_priority_high_selected
  - test_priority_low_selected

**Manual Testing**

- [ ] T043 [US4] Manual test: Create task without selecting priority, verify defaults to MEDIUM
- [ ] T044 [US4] Manual test: Create task with HIGH priority, verify saved correctly
- [ ] T045 [US4] Manual test: Create task with LOW priority, verify saved correctly

**Checkpoint**: All user stories (1, 2, 3, 4) should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

**Accessibility**

- [ ] T046 [P] Add ARIA labels to all form inputs in frontend/components/tasks/CreateTaskDialog.tsx
- [ ] T047 [P] Add keyboard navigation support (Tab, Escape, Enter) to CreateTaskDialog
- [ ] T048 Test keyboard-only task creation flow (no mouse)

**Mobile Responsiveness**

- [ ] T049 Verify mobile responsiveness (<768px full-screen modal, >=768px centered modal)
- [ ] T050 Test on mobile device or browser DevTools mobile emulation

**Backend Logging & Error Handling**

- [ ] T051 [P] Add INFO logging for successful task creation in backend/src/api/routes/tasks.py (user_id, task_id)
- [ ] T052 [P] Add ERROR logging for failed task creation in backend/src/api/routes/tasks.py (stack trace)

**Documentation**

- [ ] T053 [P] Verify OpenAPI documentation at http://localhost:8000/docs shows POST /api/v1/tasks
- [ ] T054 [P] Add docstrings to TaskService.create_task (Google style)

**Code Quality**

- [ ] T055 Run backend linting and formatting: ruff check backend/src && black backend/src
- [ ] T056 Run backend type checking: mypy backend/src
- [ ] T057 Run frontend linting: cd frontend && npm run lint
- [ ] T058 Run frontend type checking: cd frontend && npm run type-check
- [ ] T059 Run frontend formatting: cd frontend && npm run format

**Performance Verification**

- [ ] T060 Verify API response time <200ms (use backend logs or browser DevTools Network tab)
- [ ] T061 Verify task creation end-to-end <5 seconds

**Quickstart Validation**

- [ ] T062 Follow quickstart.md step-by-step and verify all code examples work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Enhances User Story 1 - Must have US1 complete first (builds on CreateTaskDialog component)
- **User Story 3 (P2)**: Enhances User Story 1 - Must have US1 complete first (adds optimistic updates to useCreateTask hook)
- **User Story 4 (P3)**: Enhances User Story 1 - Must have US1 complete first (adds priority field to CreateTaskDialog)

### Within Each User Story

**User Story 1** (independent components can run in parallel):
- Backend: T011 → T012 → T013 → T014 (sequential)
- Backend Tests: T015, T016 [P] (parallel) → T017 → T018 (sequential after implementation)
- Frontend: T019, T020, T021 [P] (parallel) → T022 → T023 → T024 (sequential)
- Frontend Tests: T025 [P] (parallel with implementation)
- Manual Tests: T026-T029 (after all implementation)

**User Story 2** (builds on US1):
- T030 → T031 (sequential, updates US1 component)
- T032 [P] (parallel)
- T033-T035 (after implementation)

**User Story 3** (builds on US1):
- T036 (updates US1 hook)
- T037 [P] (parallel)
- T038-T040 (after implementation)

**User Story 4** (builds on US1):
- T041 (updates US1 component)
- T042 [P] (parallel)
- T043-T045 (after implementation)

### Parallel Opportunities

- **Setup Phase**: T002, T003, T004 can run in parallel
- **Foundational Phase**: T007, T008, T009 can run in parallel
- **User Story 1 Backend Tests**: T015 and T016 can run in parallel
- **User Story 1 Frontend Setup**: T019, T020, T021 can run in parallel
- **User Story 1 Frontend Tests**: T025 can run in parallel with component implementation
- **User Story 2 Tests**: T032 can run in parallel with implementation
- **User Story 3 Tests**: T037 can run in parallel with implementation
- **User Story 4 Tests**: T042 can run in parallel with implementation
- **Polish Phase**: T046, T047, T051, T052, T053, T054 can run in parallel

---

## Parallel Example: User Story 1 Backend Tests

```bash
# Launch all backend unit tests for User Story 1 together:
Task T015: "Write unit tests for TaskCreate validators"
Task T016: "Write unit tests for TaskService.create_task"

# These test different files/components with no dependencies
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (core creation functionality)
4. Complete Phase 4: User Story 2 (validation feedback)
5. **STOP and VALIDATE**: Test User Stories 1+2 independently
6. Deploy/demo if ready - this is the MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP core functionality
3. Add User Story 2 → Test independently → MVP with validation (ready to deploy/demo!)
4. Add User Story 3 → Test independently → Enhanced UX with optimistic updates
5. Add User Story 4 → Test independently → Complete feature with priority support
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (backend + frontend core)
   - Developer B: Can start User Story 2 planning/tests (must wait for US1 component)
3. After US1 complete:
   - Developer A: User Story 3 (optimistic updates)
   - Developer B: User Story 2 (validation enhancements)
   - Developer C: User Story 4 (priority feature)
4. Stories complete sequentially but can be validated independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Backend tests follow TDD - write tests before implementation where possible
- Frontend tests follow best practices - test user behavior, not implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requirement: 100% backend coverage, 80%+ frontend coverage
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
