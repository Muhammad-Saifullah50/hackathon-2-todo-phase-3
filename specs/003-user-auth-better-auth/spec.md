# Feature Specification: User Authentication (Better Auth)

**Feature Branch**: `004-user-auth-better-auth`
**Created**: 2025-12-19
**Status**: Draft
**Input**: User description: "Implement User Authentication using Better Auth in Next.js and FastAPI. Requirements: Email/Password, JWT tokens for FastAPI, Shared Secret, Shared DB, and Dashboard protection. Note: Email verification and password recovery are currently out of scope."

## Clarifications

### Session 2025-12-19
- Q: What is the preferred JWT token expiration duration? → A: 7 days
- Q: Should explicit `iss` (issuer) and `aud` (audience) claims be defined and validated? → A: Yes, `iss`: "todo-auth", `aud`: "todo-api"
- Q: How should the JWT token be attached to frontend API requests? → A: Use an Axios request interceptor in `lib/api.ts`
- Q: How should the application behave if the `BETTER_AUTH_SECRET` is missing? → A: Fail immediately with a clear error message
- Q: Should user display names be unique across the system? → A: No, allow duplicates (email is the unique identifier)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Sign-up and Login (Priority: P1)

As a new user, I want to create an account and log in so that I can access my private dashboard and manage my tasks.

**Why this priority**: Foundational requirement for any user to enter the system and establish identity.

**Independent Test**: Can be tested by signing up with a new email and password, then logging in with those credentials to reach the dashboard.

**Acceptance Scenarios**:

1. **Given** a new user on the signup page, **When** they submit a valid email and password, **Then** an account is created in the shared database and they are redirected to the login page.
2. **Given** a registered user on the login page, **When** they enter correct credentials, **Then** they are granted access to the dashboard.
3. **Given** invalid credentials on the login page, **When** the user attempts to sign in, **Then** an appropriate error message is displayed and access is denied.

---

### User Story 2 - JWT-Authenticated API Access (Priority: P1)

As an authenticated user, I want my frontend to automatically include a JWT token in API requests so that the FastAPI backend can identify me and return only my data.

**Why this priority**: Essential for secure data isolation in the full-stack architecture. Connects the frontend security context to the backend service.

**Independent Test**: Can be tested by logging in, making a request to `/api/v1/tasks`, and verifying via network inspector that the `Authorization: Bearer <token>` header is present and the backend returns the correct user's data.

**Acceptance Scenarios**:

1. **Given** a valid JWT token in the request header, **When** calling a protected FastAPI endpoint, **Then** the backend extracts the user identity and processes the request.
2. **Given** a request without a token or with an expired token, **When** calling any protected endpoint, **Then** the backend returns a 401 Unauthorized response following ADR-0004.
3. **Given** an authenticated request, **When** the backend queries for data, **Then** it automatically filters all results to only include those belonging to the identified user.

---

### User Story 3 - Protected Dashboard & Session Management (Priority: P2)

As a user, I want my session to remain active across page reloads and my dashboard to be protected from unauthorized access.

**Why this priority**: Core requirement for a professional web application experience and basic privacy.

**Independent Test**: Can be tested by navigating directly to `/dashboard` while logged out (redirects to landing) and refreshing the dashboard while logged in (remains on page).

**Acceptance Scenarios**:

1. **Given** an unauthenticated state, **When** attempting to access `/dashboard`, **Then** the system redirects the user to the landing or login page.
2. **Given** an active session, **When** the user visits the landing page, **Then** a "Dashboard" link/button is visible in the navigation.
3. **Given** a user is logged in, **When** they click "Logout", **Then** the session is destroyed and all subsequent protected API calls fail until a new login occurs.

---

### Edge Cases

- **Token Expiry**: How does the frontend handle a 401 mid-session? (Trigger logout/redirect).
- **Secret Key Change**: What happens if the `BETTER_AUTH_SECRET` is rotated? (All active JWTs become invalid).
- **Duplicate Sign-up**: How does the system handle an attempt to register with an email that already exists?
- **Invalid Token Format**: How does the backend handle malformed or "garbage" Authorization headers?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: **Better Auth Integration**: The system MUST implement Better Auth in the Next.js frontend using the PostgreSQL adapter for the shared database.
- **FR-002**: **JWT Plugin**: Better Auth MUST be configured with the JWT plugin to issue tokens compatible with the FastAPI backend.
- **FR-003**: **Shared Secret**: Both Next.js and FastAPI MUST use the same `BETTER_AUTH_SECRET` for token signing and verification using the HS256 algorithm.
- **FR-004**: **FastAPI Security Dependency**: The backend MUST implement a reusable dependency to verify JWT signatures and extract the user ID (`sub` claim).
- **FR-005**: **User-Based Filtering**: All backend services MUST use the authenticated user ID to filter database queries for tasks.
- **FR-006**: **Frontend API Client**: The Axios client in `frontend/lib/api.ts` MUST implement a request interceptor to automatically attach the JWT token to the `Authorization` header.
- **FR-007**: **Route Protection**: The `/dashboard` route MUST be protected using Next.js Middleware to prevent unauthenticated access.
- **FR-008**: **User Profile Endpoint**: The backend MUST provide a `GET /api/v1/users/me` endpoint that returns the authenticated user's information.
- **FR-009**: **Shadow Model Support**: The FastAPI `User` model MUST be synchronized with the Better Auth table structure but excluded from Alembic migrations.
- **FR-010**: **Startup Validation**: Both frontend and backend MUST validate the presence of `BETTER_AUTH_SECRET` on startup and fail immediately if it is missing.

### Key Entities

- **User**: The identity entity managed by Better Auth, containing `id`, `email` (unique identifier), and `name` (non-unique).
- **Session**: A Better Auth entity representing an active web session.
- **JWT**: A signed token issued by the frontend containing the user's unique identifier and basic metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Protected API endpoints reject unauthorized requests with a 401 Unauthorized status in < 100ms.
- **SC-002**: 100% of tasks returned by the API belong to the user identified in the JWT.
- **SC-003**: Next.js Middleware redirects unauthenticated users from `/dashboard` in < 500ms.
- **SC-004**: The backend can verify a JWT issued by the frontend using only the shared secret (no network call to frontend).

## Out of Scope

- Email verification (deferred).
- Password recovery/reset (deferred).
- Google/Social OAuth (deferred).
- Multi-factor authentication (MFA).
- Admin/Management roles.

## Assumptions

- **Database**: Next.js and FastAPI share the same Neon PostgreSQL instance.
- **Algorithm**: JWTs will use the `HS256` symmetric signing algorithm.
- **Persistence**: Better Auth will handle its own schema creation in the database.
