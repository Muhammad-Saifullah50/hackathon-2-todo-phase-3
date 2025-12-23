# Feature Specification: Task Creation

**Feature Branch**: `004-task-creation`
**Created**: 2025-12-20
**Status**: Draft
**Input**: User description: "Feature 4: Task Creation - Enable authenticated users to create new tasks with title and optional description through web API and UI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create First Task via Web Interface (Priority: P1)

As a new user who has just signed in, I want to quickly create my first task through an intuitive interface so I can start organizing my work immediately.

**Why this priority**: This is the foundational user journey for the entire application. Without the ability to create tasks, no other task management functionality has value. This represents the absolute minimum viable product for the web application.

**Independent Test**: Can be fully tested by authenticating as a user, opening the task creation interface, entering a title, and verifying the task appears in the task list with correct data (title, status, timestamps).

**Acceptance Scenarios**:

1. **Given** I am authenticated and viewing the task list, **When** I click the "Add Task" button, **Then** I see a task creation modal with title and description input fields
2. **Given** the task creation modal is open, **When** I enter a title "Buy groceries" and click "Create Task", **Then** I see a success message and the new task appears at the top of my task list with status "Pending"
3. **Given** I am creating a task, **When** I enter both title "Finish project" and description "Complete the frontend implementation", **Then** the task is created with both fields saved correctly
4. **Given** the modal is open with no input, **When** I try to submit the form, **Then** I see a validation error "Title is required" and the form is not submitted

---

### User Story 2 - Create Task with Validation Feedback (Priority: P1)

As a user creating tasks, I want immediate feedback on input validation so I know my task data meets requirements before submitting.

**Why this priority**: Validation feedback is critical for good user experience during the core task creation flow. Users need to understand constraints to successfully create tasks on their first attempt.

**Independent Test**: Can be tested by opening the task creation form and entering various invalid inputs (too long title, exceeding character limits), verifying real-time validation messages appear without form submission.

**Acceptance Scenarios**:

1. **Given** I am entering a task title, **When** I type more than 100 characters, **Then** I see an error message "Title must be 100 characters or less" displayed immediately
2. **Given** I am entering a task title, **When** I type more than 50 words, **Then** I see an error message "Title must be 50 words or less" displayed immediately
3. **Given** I am entering a description, **When** I type more than 500 characters, **Then** I see an error message "Description must be 500 characters or less" and cannot type further
4. **Given** I have validation errors showing, **When** I correct the input to meet requirements, **Then** the error messages disappear and the submit button becomes enabled

---

### User Story 3 - Create Task with Optimistic UI Updates (Priority: P2)

As a user creating tasks, I want the interface to respond instantly when I submit a task so the application feels fast and responsive even with network delays.

**Why this priority**: Optimistic updates significantly improve perceived performance and user satisfaction, but the basic creation functionality (P1) must work first. This enhances the experience but is not blocking for core functionality.

**Independent Test**: Can be tested by creating a task and observing that it appears in the list immediately upon submission, even before the server responds. If the network is slow or fails, verify appropriate error handling and rollback.

**Acceptance Scenarios**:

1. **Given** I submit a valid task, **When** I click "Create Task", **Then** the task appears in my list immediately before the server response arrives
2. **Given** the server successfully creates the task, **When** the response is received, **Then** the temporary task is replaced with the server task including the real UUID
3. **Given** the server fails to create the task, **When** the error response is received, **Then** the optimistic task is removed from the list and I see an error message "Failed to create task. Please try again."
4. **Given** I create a task with optimistic updates enabled, **When** I navigate away before the server responds, **Then** the task creation completes in the background and appears when I return to the task list

---

### User Story 4 - Create Task with Priority Setting (Priority: P3)

As a power user managing multiple tasks, I want to optionally set a priority level when creating a task so I can organize my work by importance from the start.

**Why this priority**: Priority is a nice-to-have feature that enhances task organization but is not essential for the core task creation flow. Most users can effectively create and manage tasks without setting priorities initially.

**Independent Test**: Can be tested by creating tasks with and without priority selection, verifying that tasks without explicit priority default to MEDIUM, and that selected priorities are saved correctly.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I leave the priority dropdown unselected, **Then** the task is created with priority "MEDIUM" by default
2. **Given** I am creating a task, **When** I select priority "HIGH" from the dropdown, **Then** the task is created with priority "HIGH"
3. **Given** I have created tasks with different priorities, **When** I view my task list, **Then** I can see the priority indicator for each task
4. **Given** the priority dropdown is visible, **When** I view the options, **Then** I see "Low", "Medium", and "High" as available choices

---

### Edge Cases

- **Empty title submission**: When user tries to submit a task with only whitespace in the title, system shows "Title is required" error and prevents submission
- **Maximum title length (100 chars)**: When user enters exactly 100 characters, system accepts the input; at 101 characters, system shows validation error
- **Maximum title words (50 words)**: When user enters exactly 50 words, system accepts; at 51 words, system shows "Title must be 50 words or less"
- **Maximum description length (500 chars)**: When user enters 500 characters, system accepts; attempting 501 characters shows error or prevents further typing
- **Network failure during creation**: When task creation API call fails due to network error, system removes optimistic task from list and shows user-friendly error message
- **Authentication token expired**: When user's JWT token expires while creating a task, system shows "Session expired. Please sign in again." and redirects to sign-in page
- **Concurrent task creation**: When user rapidly clicks "Create Task" multiple times, system prevents duplicate submissions through form disabling or debouncing
- **Modal close with unsaved data**: When user has entered data in the form and tries to close the modal, system shows confirmation "Discard changes?" before closing
- **Server validation mismatch**: When backend validation differs from frontend (edge case bug), system displays server validation errors and prevents submission
- **Special characters in input**: When user enters emojis, newlines, or special characters in title/description, system accepts and displays them correctly
- **Keyboard shortcuts conflict**: When user presses Ctrl/Cmd+N while already in the creation modal, system ignores the duplicate command
- **API returns 500 error**: When server encounters an internal error during creation, system shows "Something went wrong. Please try again later." and logs the error for investigation

## Requirements *(mandatory)*

### Functional Requirements

#### API Endpoint Requirements

- **FR-001**: System MUST provide a POST endpoint at `/api/v1/tasks` that accepts authenticated requests with JWT Bearer token
- **FR-002**: System MUST accept request body containing title (required string) and description (optional nullable string) fields only
- **FR-003**: System MUST NOT accept user_id in the request body; it MUST be extracted automatically from the authenticated user's JWT token
- **FR-004**: System MUST NOT accept status in the request body; all new tasks MUST default to PENDING status
- **FR-005**: System MUST accept optional priority field in request body with valid values: LOW, MEDIUM, or HIGH
- **FR-006**: System MUST return HTTP 201 Created status code with standardized response format on successful creation
- **FR-007**: System MUST return HTTP 400 Bad Request with validation error details when input fails validation
- **FR-008**: System MUST return HTTP 401 Unauthorized when JWT token is missing, invalid, or expired
- **FR-009**: System MUST return HTTP 500 Internal Server Error with generic error message when server-side failure occurs

#### Validation Requirements

- **FR-010**: System MUST validate title is not empty after trimming whitespace
- **FR-011**: System MUST validate title does not exceed 100 characters in length
- **FR-012**: System MUST validate title does not exceed 50 words (split by whitespace using `/\s+/` pattern)
- **FR-013**: System MUST validate description does not exceed 500 characters when provided
- **FR-014**: System MUST treat empty string description as null (no description)
- **FR-015**: System MUST trim leading and trailing whitespace from title and description before saving
- **FR-016**: System MUST allow HTML, markdown, emojis, special characters, and international characters in description field
- **FR-017**: System MUST validate priority is one of LOW, MEDIUM, or HIGH when provided; reject invalid values
- **FR-018**: System MUST apply validation rules on both backend (security layer) and frontend (user experience layer)

#### Data Persistence Requirements

- **FR-019**: System MUST generate a UUID for each new task using uuid4 algorithm
- **FR-020**: System MUST automatically set created_at timestamp to current UTC time when task is created
- **FR-021**: System MUST automatically set updated_at timestamp to current UTC time when task is created
- **FR-022**: System MUST set completed_at field to null for newly created tasks with PENDING status
- **FR-023**: System MUST default priority to MEDIUM when not provided in request
- **FR-024**: System MUST associate each task with the authenticated user's ID from the JWT token
- **FR-025**: System MUST persist task data to the database using SQLModel ORM with implicit transaction management
- **FR-026**: System MUST add database-level constraints: title max_length=100, description max_length=500

#### Response Format Requirements

- **FR-027**: System MUST return success response in StandardizedResponse format with fields: success (true), message, data
- **FR-028**: System MUST include HTTP status code in response body (status: 201)
- **FR-029**: System MUST set message field to "Task created successfully" on successful creation
- **FR-030**: System MUST include complete task object in data field with all attributes: id, title, description, status, priority, user_id, created_at, updated_at, completed_at
- **FR-031**: System MUST return error response in ErrorResponse format with fields: success (false), error (with code, message, and optional field details)
- **FR-032**: System MUST use error codes: VALIDATION_ERROR (validation failures), UNAUTHORIZED (auth issues), INTERNAL_ERROR (server failures)
- **FR-033**: System MUST return array of field-specific errors in error.details for validation failures, each containing field name and message

#### Frontend Interface Requirements

- **FR-034**: System MUST provide a modal dialog interface for task creation, triggered by "Add Task" button or Ctrl/Cmd+N keyboard shortcut
- **FR-035**: System MUST display form fields: title (text input, required), description (textarea, optional), priority (dropdown, optional)
- **FR-036**: System MUST show real-time validation errors as users type, without requiring form submission
- **FR-037**: System MUST disable submit button when validation errors exist or when form is submitting
- **FR-038**: System MUST show loading state with "Creating..." text on submit button during API request
- **FR-039**: System MUST close modal automatically after successful task creation
- **FR-040**: System MUST display success toast notification "Task created successfully" after successful creation
- **FR-041**: System MUST display error toast notification with specific error message when creation fails
- **FR-042**: System MUST support keyboard shortcuts: Ctrl/Cmd+N (open modal), Escape (close modal), Ctrl/Cmd+Enter (submit form)
- **FR-043**: System MUST implement mobile-first responsive design: full-screen modal on mobile (<768px), centered modal on desktop (>=768px)

#### Optimistic Update Requirements

- **FR-044**: System MUST add newly created task to the UI immediately upon form submission, before server response
- **FR-045**: System MUST generate temporary client-side UUID for optimistic task using crypto.randomUUID()
- **FR-046**: System MUST mark optimistic task with pending state in React Query cache
- **FR-047**: System MUST replace optimistic task with server task (real UUID) when API response succeeds
- **FR-048**: System MUST remove optimistic task from UI and show error message when API response fails
- **FR-049**: System MUST invalidate tasks query cache after successful creation to refetch complete task list

#### Service Layer Requirements

- **FR-050**: System MUST implement TaskService class to handle business logic and validation, separating concerns from route handlers
- **FR-051**: System MUST keep route handlers thin, delegating validation and creation logic to TaskService
- **FR-052**: System MUST catch and handle SQLAlchemy exceptions in service layer, returning user-friendly error messages
- **FR-053**: System MUST log successful task creation at INFO level with user_id and task_id
- **FR-054**: System MUST log failed task creation at ERROR level with stack trace for debugging

### Key Entities

- **Task**: Represents a todo item owned by a user. Core domain entity for the application. Contains:
  - id: UUID primary key, generated automatically
  - title: Short summary (1-100 characters, 1-50 words, required)
  - description: Detailed information (0-500 characters, optional, nullable)
  - status: Completion state (PENDING or COMPLETED enum, defaults to PENDING)
  - priority: Importance level (LOW, MEDIUM, or HIGH enum, defaults to MEDIUM)
  - user_id: Foreign key reference to owning user (string, matches Better Auth user.id)
  - created_at: Timestamp when task was created (datetime with timezone, auto-set)
  - updated_at: Timestamp when task was last modified (datetime with timezone, auto-set)
  - completed_at: Timestamp when task was marked complete (datetime with timezone, nullable, null for new tasks)

- **TaskCreate**: Request schema for creating a task. Contains only user-provided fields:
  - title: Task summary (string, required, validated)
  - description: Task details (string, optional, nullable, validated)
  - priority: Importance level (TaskPriority enum, optional, defaults to MEDIUM)
  - Note: status and user_id are NOT accepted; id and timestamps are system-generated

- **TaskResponse**: Response schema representing a created task. Contains all Task fields for client consumption, including system-generated values (id, user_id, timestamps)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new task and see it appear in their task list in under 5 seconds from clicking "Add Task" to seeing confirmation
- **SC-002**: Users successfully create tasks on their first attempt in at least 90% of cases without encountering validation errors
- **SC-003**: Task creation interface responds to user input with validation feedback within 100 milliseconds of typing
- **SC-004**: System handles task creation requests from 100 concurrent users without performance degradation or errors
- **SC-005**: Task creation success rate is 99.9% or higher (excluding user-caused validation errors and network failures)
- **SC-006**: Users can create tasks on mobile devices with the same ease as desktop, measured by equal task creation completion rates across devices
- **SC-007**: Zero data loss occurs during task creation under normal operation (successful creation always persists task to database)
- **SC-008**: All validation errors provide clear, actionable guidance that users can understand without technical knowledge in 100% of cases
- **SC-009**: Users can create and submit a task using only keyboard navigation without requiring mouse interaction
- **SC-010**: Task creation form loads and becomes interactive within 1 second on standard broadband connections

### Non-Functional Success Indicators

- **NF-001**: Developer onboarding - new developers can implement a similar feature by following this pattern within 2 hours
- **NF-002**: Code maintainability - service layer logic is testable in isolation with 100% code coverage achieved
- **NF-003**: API reliability - task creation endpoint maintains 99.9% uptime during normal operation
- **NF-004**: User satisfaction - users report task creation is intuitive and straightforward in user testing sessions

## Assumptions

The following assumptions are made in this specification:

### Validation Assumptions
1. **Word count definition**: A "word" is defined as any sequence of characters separated by whitespace (space, tab, newline), using the `/\s+/` regex pattern for splitting
2. **Character limit precedence**: Both character count (100) and word count (50) limits must be satisfied; if title is 80 characters but 60 words, it fails validation
3. **Whitespace handling**: Leading and trailing whitespace is automatically trimmed; consecutive internal whitespace is preserved as typed
4. **Special character support**: All Unicode characters including emojis, international characters, and special symbols are allowed in title and description

### Priority Assumptions
5. **Priority default**: When priority is not provided in the request, it defaults to MEDIUM (not null) to simplify UI display and sorting logic
6. **Priority optionality**: Priority field is optional on task creation; frontend may choose to hide or show it based on UX requirements

### Authentication Assumptions
7. **JWT structure**: JWT token contains `sub` (user ID), `email`, `name`, and `email_verified` claims as defined in Feature 3 (Better Auth integration)
8. **Token extraction**: User ID is always extracted from JWT token's `sub` claim; any user_id in request body is rejected to prevent privilege escalation
9. **Session management**: Token expiration and refresh are handled by Better Auth (Feature 3); this feature only validates token presence and extracts user data

### Data Persistence Assumptions
10. **Database transactions**: SQLModel's session provides implicit transaction management (auto-commit on success, auto-rollback on exception)
11. **UUID generation**: Python's uuid4 algorithm provides sufficient uniqueness guarantees without collision checking
12. **Timestamp precision**: All timestamps are stored in UTC with timezone information; frontend is responsible for displaying in user's local timezone

### API Response Assumptions
13. **Response format**: All endpoints follow ADR-0004 standardized response format with status code in body matching HTTP status code
14. **Error detail level**: Validation errors include field-specific details; server errors return generic messages without stack traces or internal details
15. **Success message**: Generic "Task created successfully" message is sufficient; task title is not included to avoid truncation complexity

### Frontend Assumptions
16. **UI pattern**: Modal dialog is the chosen pattern for task creation; alternative patterns (inline form, dedicated page) are out of scope
17. **Optimistic updates**: Enabled by default to improve perceived performance; users see tasks immediately even with slow network
18. **Mobile-first breakpoints**: Using Tailwind's default breakpoints (mobile <768px, tablet/desktop >=768px)
19. **Browser support**: Modern browsers with ES6+ support; legacy IE11 support is out of scope

### Integration Assumptions
20. **Feature dependencies**: Feature 1 (Project Setup), Feature 2 (Database), and Feature 3 (Authentication) are fully complete and functional
21. **Database schema**: Task and User tables exist with proper relationships and constraints as defined in Feature 2
22. **CORS configuration**: Backend CORS middleware allows requests from frontend origin as configured in Feature 1

### Testing Assumptions
23. **Test coverage**: 100% code coverage target applies to service layer and route handlers; UI components follow best-effort testing
24. **Test database**: Integration tests use separate test database instance (local PostgreSQL or separate Neon database)
25. **Test independence**: Each test is independent and can run in isolation without affecting other tests

## Out of Scope (Phase 1)

The following are explicitly **not** included in this feature:

- Task editing/updating functionality (covered in Feature 6)
- Task deletion functionality (covered in Feature 8)
- Task status toggling (covered in Feature 7)
- Task filtering and searching (covered in Feature 5)
- Task due dates and reminders
- Task tags or categories
- Task attachments or file uploads
- Bulk task creation (import multiple tasks)
- Task templates or recurring tasks
- Collaborative task assignment (sharing tasks with other users)
- Task comments or activity history
- Rich text editing for descriptions
- Drag-and-drop task creation
- Voice input for task creation
- Offline task creation with sync
- Task creation via email or API integrations
- Custom task fields or metadata
- Task color coding or icons

## Dependencies

This feature depends on the following being complete:

- **Feature 1 (Project Setup)**: Frontend and backend infrastructure, Docker setup, development environment
- **Feature 2 (Database Setup)**: Neon PostgreSQL provisioned, SQLModel ORM configured, Task and User tables created with migrations
- **Feature 3 (Authentication)**: Better Auth integration complete, JWT token generation/verification working, user authentication flow functional

The following libraries and frameworks are assumed to be configured:

- **Backend**: FastAPI, SQLModel, Alembic, python-jose (JWT), Pydantic (validation)
- **Frontend**: Next.js 16, React Hook Form, Zod (validation), TanStack Query (React Query), Tailwind CSS, shadcn/ui components
- **Database**: Neon PostgreSQL with Task and User tables
- **Authentication**: Better Auth with JWT tokens

## Non-Functional Requirements

- **Testability**: 100% test coverage required for backend service layer and route handlers; minimum 80% coverage for frontend components
- **Type Safety**: All code must include type hints (Python) and TypeScript types; must pass mypy (backend) and tsc (frontend) with no errors
- **Code Quality**: Must pass ruff linting and black formatting (backend); must pass ESLint and Prettier (frontend)
- **Performance**: Task creation API endpoint must respond in under 200 milliseconds for 95th percentile requests
- **Usability**: All operations must be completable with keyboard only; mobile interface must be touch-friendly with appropriate tap targets (minimum 44px)
- **Accessibility**: Form inputs must have proper labels, ARIA attributes, and error announcements for screen readers
- **Error Recovery**: All error states must be recoverable without data loss or requiring page refresh
- **Data Integrity**: All database writes must be atomic; partial task creation must not leave orphaned data
- **Security**: Input validation on both frontend and backend; no SQL injection, XSS, or CSRF vulnerabilities
- **Documentation**: All public functions must have docstrings (Google style); API endpoint must appear in auto-generated OpenAPI documentation at `/docs`
