# Feature Specification: CLI Todo Application

**Feature Branch**: `001-cli-todo`
**Created**: 2025-12-18
**Status**: Draft
**Input**: User description: "Interactive CLI Todo Application with beautiful UX using Python 3.13+, questionary, and rich libraries for task management (add, view, update, delete, mark complete)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add and View First Task (Priority: P1)

As a new user, I want to quickly add my first task and see it displayed beautifully in a table so I can start organizing my work immediately.

**Why this priority**: This is the foundational user journey. Without the ability to create and view tasks, no other functionality has value. This represents the absolute minimum viable product.

**Independent Test**: Can be fully tested by launching the app, adding a single task with title and description, and verifying it appears in a formatted table with correct status, timestamps, and navigation options.

**Acceptance Scenarios**:

1. **Given** I launch the app with no existing tasks, **When** I select "Add new task" and enter a title "Buy groceries", **Then** I see success message with the newly created task details including 8-char ID, title, pending status, and creation timestamp
2. **Given** I have added a task, **When** I select "View tasks" → "View all tasks", **Then** I see a formatted table with my task showing ID, status icon (✗), full title, truncated description, and creation date
3. **Given** I am viewing the tasks table, **When** I select "Back to main menu", **Then** I return to the main menu with all options available

---

### User Story 2 - Update Task Details (Priority: P2)

As a user managing tasks, I want to update task titles and descriptions so I can keep my task list accurate as requirements change.

**Why this priority**: After creating tasks (P1), the ability to modify them is critical for maintaining an accurate task list. Users often need to refine or correct task details after creation.

**Independent Test**: Can be tested by creating a task, selecting "Update task", choosing what to update (title/description/both), entering new values, and verifying the updated task displays with new values and updated timestamp.

**Acceptance Scenarios**:

1. **Given** I have existing tasks, **When** I select "Update task", **Then** I see a selectable list of tasks with status, full title, and truncated description
2. **Given** I select a task to update, **When** I choose "Title only" and enter a new title within 10 words, **Then** I see success message and the updated task with new title and updated timestamp
3. **Given** I am updating a task, **When** I choose "Both title and description" and provide new values, **Then** both fields are updated and I see the updated task details
4. **Given** I am updating a title, **When** I enter an empty string, **Then** I see error "Update cancelled. Title cannot be empty" and return to task view with original values unchanged

---

### User Story 3 - Mark Tasks Complete/Incomplete (Priority: P2)

As a user completing work, I want to mark tasks as complete or incomplete so I can track my progress and focus on pending work.

**Why this priority**: Task status tracking is core to any todo application. This enables users to measure progress and filter their task list by completion status.

**Independent Test**: Can be tested by creating tasks, marking them as complete, verifying status icon changes to (✓), marking complete tasks as incomplete, and verifying status reverts to (✗).

**Acceptance Scenarios**:

1. **Given** I have pending tasks, **When** I select "Mark task as complete/incomplete" → "Mark as complete", **Then** I see only pending tasks (✗) in the selection list
2. **Given** I select tasks to mark complete using checkboxes, **When** I confirm the selection, **Then** I see "Mark N tasks as complete?" confirmation showing the count
3. **Given** I confirm marking tasks complete, **When** the operation completes, **Then** I see success message and all tasks view showing the newly completed tasks with (✓) status icon
4. **Given** I have completed tasks, **When** I select "Mark as incomplete", **Then** I see only completed tasks (✓) and can toggle them back to pending

---

### User Story 4 - Delete Unwanted Tasks (Priority: P3)

As a user maintaining my task list, I want to delete tasks I no longer need so my list stays focused and manageable.

**Why this priority**: While important for list maintenance, deletion is lower priority than creation, viewing, updating, and status tracking. Users can work effectively with a growing list before needing deletion.

**Independent Test**: Can be tested by creating tasks, selecting "Delete task", choosing tasks via checkbox, confirming deletion with count displayed, and verifying tasks are removed from all views.

**Acceptance Scenarios**:

1. **Given** I have existing tasks, **When** I select "Delete task", **Then** I see all tasks in a checkbox list with status icons
2. **Given** I select multiple tasks to delete, **When** I confirm, **Then** I see "Delete N selected tasks?" with the count displayed
3. **Given** I confirm deletion, **When** the operation completes, **Then** I see success message and all tasks view without the deleted tasks
4. **Given** I select no tasks in the checkbox, **When** I try to proceed, **Then** I see error "No tasks selected. Please select at least one task" and return to selection

---

### User Story 5 - Filter and Navigate Task Lists (Priority: P3)

As a user with many tasks, I want to filter by status (all/pending/completed) and navigate paginated results so I can focus on relevant tasks without being overwhelmed.

**Why this priority**: This enhances usability for power users with large task lists but isn't critical for initial adoption. Users with fewer than 10 tasks don't need pagination or filtering.

**Independent Test**: Can be tested by creating 15+ tasks with mixed statuses, selecting view filters (all/pending/completed), verifying pagination controls appear, and navigating between pages.

**Acceptance Scenarios**:

1. **Given** I have tasks with mixed statuses, **When** I select "View pending tasks", **Then** I see only tasks with (✗) status in the table
2. **Given** I have more than 10 tasks, **When** I view any task list, **Then** I see "Showing tasks 1-10 of N" with pagination options
3. **Given** I am on page 1 of results, **When** I view pagination options, **Then** I see "Next page" and "Back to menu" but not "Previous page"
4. **Given** I am viewing a filtered task table, **When** I select "Select a task", **Then** I see submenu with "Update", "Delete", "Toggle status", "Back" options

---

### Edge Cases

- **Empty task list on operation**: When user selects Update/Delete/Mark Complete but no tasks exist, system shows "⚠️ No tasks exist yet. Create your first task!" and returns to main menu
- **Title validation**: When user enters title exceeding 10 words, system shows "❌ Error: Title too long (max 10 words allowed)" and re-prompts
- **Description validation**: When user enters description exceeding 500 characters, system shows "❌ Error: Description too long (max 500 characters allowed)" and re-prompts
- **Empty title input**: When user enters empty title during add/update, system shows "❌ Error: Title cannot be empty (min 1 character required)" and re-prompts or cancels update
- **File corruption**: When tasks.json is corrupted, system saves backup as tasks.json.backup, shows "❌ Data file corrupted. Backup saved to tasks.json.backup. Starting fresh.", and resets to empty state
- **File permission error**: When tasks.json cannot be accessed on startup, system shows "❌ Error: Cannot access tasks.json. Check file permissions." and exits gracefully
- **Terminal too narrow**: When terminal width is less than 80 columns, system shows "⚠️ Terminal too narrow. Please resize to at least 80 columns." before displaying tables
- **UUID collision**: When generated 8-char UUID already exists, system regenerates until unique ID is found
- **Keyboard interrupt (Ctrl+C)**: When user presses Ctrl+C at any point, system catches KeyboardInterrupt and shows "👋 Thanks for using Todo CLI! Goodbye." before exiting
- **Last task deletion**: When user deletes the last remaining task, system shows "✓ Task deleted successfully!" followed by "⚠️ No tasks exist yet. Create your first task!" and returns to main menu
- **Concurrent access**: Multiple instances can access tasks.json simultaneously with last-write-wins behavior (documented limitation for Phase 1)

## Requirements *(mandatory)*

### Functional Requirements

#### Task Management

- **FR-001**: System MUST allow users to add tasks with a title (1-10 words) and optional description (0-500 characters)
- **FR-002**: System MUST generate a unique 8-character UUID for each task, regenerating if collision detected
- **FR-003**: System MUST store both created_at and updated_at timestamps in ISO 8601 format (YYYY-MM-DD HH:MM:SS)
- **FR-004**: System MUST allow users to update task title, description, or both through a selection menu
- **FR-005**: System MUST allow users to mark tasks as complete or incomplete through separate filtered menus
- **FR-006**: System MUST allow users to delete single or multiple tasks with confirmation showing count
- **FR-007**: System MUST display task status using visual indicators: (✗) for pending, (✓) for complete

#### User Interface

- **FR-008**: System MUST provide interactive menu navigation using questionary.select()
- **FR-009**: System MUST display tasks in formatted tables using rich library with columns: ID, Status, Title, Description (truncated to terminal width), Created
- **FR-010**: System MUST implement pagination showing 10 tasks per page with Next/Previous/Back navigation
- **FR-011**: System MUST provide filter options: View all tasks, View pending tasks, View completed tasks
- **FR-012**: System MUST use consistent color scheme: Green for completed/success, Yellow for pending, Red for errors, Blue for prompts
- **FR-013**: System MUST show confirmation messages after all operations with appropriate visual treatment
- **FR-014**: System MUST provide Back/Cancel options in all submenus and Exit (with confirmation) in main menu

#### Text Input and Validation

- **FR-015**: System MUST use questionary.text() for title and description input
- **FR-016**: System MUST use questionary.confirm() for delete and exit confirmations
- **FR-017**: System MUST use questionary.checkbox() for bulk operations (multi-select delete/complete)
- **FR-018**: System MUST validate title has 1-10 words (split by whitespace)
- **FR-019**: System MUST validate description has 0-500 characters
- **FR-020**: System MUST treat empty input as cancel and show "Task addition/update aborted" message
- **FR-021**: System MUST allow emojis, newlines, and special characters in descriptions

#### Data Persistence

- **FR-022**: System MUST store tasks in JSON format at `tasks.json` in project root directory
- **FR-023**: System MUST auto-create tasks.json if missing with empty task array
- **FR-024**: System MUST perform atomic writes (write to temp file, then rename) to prevent corruption
- **FR-025**: System MUST check file permissions on startup and show clear error if inaccessible
- **FR-026**: System MUST create tasks.json.backup before resetting corrupted files
- **FR-027**: System MUST store tasks with fields: id (string, 8 chars), title (string), description (string), status (string: "pending" or "completed"), created_at (string, ISO 8601), updated_at (string, ISO 8601)

#### Error Handling

- **FR-028**: System MUST show user-friendly error messages (no stack traces) with actionable guidance
- **FR-029**: System MUST handle empty task list gracefully with "⚠️ No tasks exist yet. Create your first task!" message
- **FR-030**: System MUST catch KeyboardInterrupt globally and exit gracefully with goodbye message
- **FR-031**: System MUST validate terminal width is at least 80 columns before displaying tables
- **FR-032**: System MUST prevent operations on empty task lists and redirect to main menu automatically

#### Navigation Flow

- **FR-033**: After adding task, system MUST show newly created task details, then return to main menu
- **FR-034**: After updating task, system MUST show updated task details with Back option
- **FR-035**: After deleting task(s), system MUST show success message and all tasks view
- **FR-036**: After marking complete/incomplete, system MUST show success message and all tasks view
- **FR-037**: When viewing tasks table, user MUST have options to "Select a task" or "Back to main menu"
- **FR-038**: When selecting a task from table view, system MUST show submenu: Update, Delete, Toggle status, Back

### Key Entities

- **Task**: Represents a single todo item with attributes:
  - `id`: Unique 8-character identifier
  - `title`: Short description (1-10 words)
  - `description`: Detailed information (0-500 characters, optional)
  - `status`: Current state ("pending" or "completed")
  - `created_at`: Timestamp when task was created (ISO 8601)
  - `updated_at`: Timestamp when task was last modified (ISO 8601)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task and see it displayed in under 10 seconds
- **SC-002**: Users can complete the full workflow (add → view → update → complete → delete) in under 2 minutes
- **SC-003**: System handles 1000+ tasks without performance degradation (table rendering, pagination, filtering)
- **SC-004**: 100% of operations provide immediate visual feedback with appropriate success/error messages
- **SC-005**: Terminal UI remains readable and properly formatted in terminal widths of 80-200 columns
- **SC-006**: Users can navigate any menu or operation with keyboard only (no mouse required)
- **SC-007**: All data operations complete atomically with zero data loss on normal operation
- **SC-008**: System recovers gracefully from file corruption with backup creation in 100% of cases
- **SC-009**: Error messages guide users to resolution without requiring technical knowledge in 100% of error scenarios
- **SC-010**: Users can exit the application cleanly (with confirmation) from any menu state

## Assumptions

1. **Single user environment**: Application is designed for single-user CLI usage on one machine at a time
2. **Python 3.13+ available**: User has Python 3.13 or higher installed and configured
3. **Terminal emulator**: User has a standard terminal emulator supporting ANSI colors and UTF-8 encoding
4. **Filesystem access**: Application has read/write permissions in the project directory
5. **No authentication**: This is a local CLI tool with no user authentication or multi-user support
6. **English language**: All UI text and messages are in English (no internationalization in Phase 1)
7. **Standard keyboard**: User has access to standard keyboard input (Enter, Ctrl+C, Space, arrow keys)
8. **No cloud sync**: Tasks are stored locally only with no cloud backup or synchronization
9. **Manual backups**: Users are responsible for backing up tasks.json if needed
10. **Desktop/laptop environment**: Not designed for mobile or embedded terminals

## Out of Scope (Phase 1)

- Search/filter by text keywords
- Task due dates and reminders
- Task priorities or categories/tags
- Recurring tasks
- Task attachments or links
- Export to other formats (CSV, PDF, etc.)
- Import from other todo applications
- Undo/redo functionality
- Task history or audit trail
- Multi-user support or cloud sync
- Mobile/web interface
- Integration with external services (calendar, email, etc.)
- Task dependencies or subtasks
- Custom color schemes or themes

## Dependencies

- **questionary**: Interactive CLI prompts and menus
- **rich**: Terminal formatting, tables, and panels
- **pytest**: Testing framework
- **pytest-cov**: Code coverage reporting
- **mypy**: Type checking (development)
- **ruff**: Linting (development)
- **black**: Code formatting (development)
- **uv**: Dependency management and virtual environment

## Non-Functional Requirements

- **Testability**: 100% test pass rate required before commit, minimum 100% code coverage goal
- **Type Safety**: All code must include type hints and pass mypy strict mode
- **Code Quality**: Must pass ruff linting and black formatting checks
- **Performance**: Table rendering must complete in under 1 second for 1000 tasks
- **Usability**: All operations must be completable with keyboard only, no mouse required
- **Accessibility**: Provide --simple mode flag for screen reader compatibility (output plain text without colors)
- **Error Recovery**: All error states must be recoverable without data loss
- **Data Integrity**: All file writes must be atomic (write to temp, rename)
