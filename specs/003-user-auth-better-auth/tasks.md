---
description: "Task list for User Authentication implementation"
---

# Tasks: User Authentication (Better Auth)

**Input**: Design documents from `/specs/004-user-auth-better-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Install `better-auth` in `frontend/package.json`
- [X] T002 [P] Install `python-jose[cryptography]` in `backend/requirements.txt`
- [X] T003 [P] Add `BETTER_AUTH_SECRET` and `BETTER_AUTH_URL` to `frontend/.env.local`
- [X] T004 [P] Add `BETTER_AUTH_SECRET` to `backend/.env`
- [X] T005 Update `backend/src/config.py` to validate `BETTER_AUTH_SECRET` on startup

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Initialize Better Auth in `frontend/auth.ts` with PostgreSQL adapter and JWT plugin
- [X] T007 Configure Better Auth client in `frontend/lib/auth-client.ts`
- [X] T008 Update `backend/src/models/user.py` to align with Better Auth `user` table (singular table name, specific fields)
- [X] T009 Update `backend/alembic/env.py` to exclude Better Auth tables (`user`, `session`, `account`, `verification`) from migrations
- [X] T010 Implement JWT verification logic in `backend/src/auth.py` using `python-jose`
- [X] T011 Create `get_current_user` FastAPI dependency in `backend/src/auth.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Sign-up and Login (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and log in using email/password.

**Independent Test**: Register a new user on the frontend, verify records appear in DB, and successfully log in to reach the dashboard.

### Implementation for User Story 1

- [X] T012 [P] [US1] Create registration page in `frontend/app/(auth)/sign-up/page.tsx`
- [X] T013 [P] [US1] Create login page in `frontend/app/(auth)/sign-in/page.tsx`
- [X] T014 [US1] Implement signup form logic using `authClient.signUp.email`
- [X] T015 [US1] Implement login form logic using `authClient.signIn.email`
- [X] T016 [US1] Add error handling for duplicate emails and invalid credentials in UI

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - JWT-Authenticated API Access (Priority: P1)

**Goal**: Secure backend endpoints and ensure data isolation using JWTs.

**Independent Test**: Call `/api/v1/users/me` with a valid JWT and receive the correct user profile; call it without a token and receive 401.

### Implementation for User Story 2

- [X] T017 [US2] Update Axios client in `frontend/lib/api.ts` with request interceptor to attach JWT
- [X] T018 [US2] Create User router in `backend/src/api/routes/user.py`
- [X] T019 [US2] Implement `GET /api/v1/users/me` endpoint using `get_current_user` dependency
- [X] T020 [US2] Update `backend/src/main.py` to register the User router
- [ ] T021 [US2] Update `backend/src/api/routes/task.py` (and related services) to use `get_current_user` for all operations
- [ ] T022 [US2] Modify task queries to filter by the authenticated user's ID

**Checkpoint**: At this point, User Story 2 is complete - backend is secured and data is isolated.

---

## Phase 5: User Story 3 - Protected Dashboard & Session Management (Priority: P2)

**Goal**: Protect private routes and maintain user session.

**Independent Test**: Navigate to `/dashboard` while logged out (redirects to landing); remain on `/dashboard` after page refresh while logged in.

### Implementation for User Story 3

- [X] T023 [US3] Create `frontend/middleware.ts` to protect `/dashboard` and other private routes
- [X] T024 [US3] Implement "Logout" button in `frontend/components/navbar.tsx` using `authClient.signOut`
- [X] T025 [US3] Update Navbar to conditionally show "Dashboard" and "Logout" buttons based on session state
- [X] T026 [US3] Handle 401 API responses in `frontend/lib/api.ts` interceptor to trigger client-side logout

**Checkpoint**: At this point, the application has full session management and route protection.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T027 Verify ADR-0004 compliance for all new authentication error responses
- [ ] T028 Add loading states to sign-in/sign-up Sniper forms
- [ ] T029 Ensure all sensitive data (passwords, secrets) is never logged
- [ ] T030 Final verification of all user scenarios defined in `spec.md`

---

## Dependencies & Execution Order

1.  **Phase 1 & 2** are blocking and MUST be completed first.
2.  **User Story 1** provides the UI for creating users needed by other stories.
3.  **User Story 2** depends on User Story 1 (needs a logged-in user to test JWT API calls).
4.  **User Story 3** can be implemented in parallel with User Story 2 implementation once User Story 1 is complete.

## Parallel Execution Examples

- **Setup**: T001, T002, T003, T004 can run in parallel.
- **US1**: T012 and T013 (pages) can be created in parallel.
- **US2**: T018 (router) and T017 (axios interceptor) can start in parallel.

## Implementation Strategy

1.  **MVP Scope**: Complete Phases 1, 2, and 3 (User Story 1). This delivers a functional auth system where users can register and log in.
2.  **Incremental Delivery**: Add User Story 2 to secure the data layer, then User Story 3 for UX and session management.