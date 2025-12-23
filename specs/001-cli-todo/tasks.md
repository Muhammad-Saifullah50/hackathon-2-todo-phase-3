# Tasks: CLI Todo Application

**Input**: Design documents from `/specs/001-cli-todo/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Tests**: This project follows strict TDD (Test-Driven Development). All test tasks are **REQUIRED** and must be written FIRST (RED), then implementation (GREEN), then refactor.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: src/{models,storage,services,cli/{commands,display,utils}}, tests/{unit,integration,contract}, specs/001-cli-todo/
- [x] T002 Initialize Python project with uv: create pyproject.toml with dependencies (questionary, rich), dev dependencies (pytest, pytest-cov, mypy, ruff, black)
- [x] T003 [P] Create .python-version file with "3.13"
- [x] T004 [P] Configure mypy strict mode in mypy.ini
- [x] T005 [P] Configure ruff linting in .ruff.toml
- [x] T006 [P] Create .gitignore with tasks.json, tasks.json.backup, .venv/, __pycache__/, .coverage, htmlcov/
- [x] T007 Create src/__init__.py and all package __init__.py files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 [P] Create custom exception classes in src/exceptions.py: TaskValidationError, StorageError, TaskNotFoundError, FilePermissionError, FileCorruptionError
- [x] T009 [P] Create validation constants in src/services/validators.py: MAX_TITLE_WORDS=10, MAX_DESC_CHARS=500, ID_LENGTH=8, MIN_TERMINAL_WIDTH=80
- [x] T010 [P] Create pytest fixtures in tests/conftest.py: tmp_path for storage file, mock_storage, sample_tasks fixtures
- [x] T011 Test: Write unit tests for validators in tests/unit/test_validators.py (RED: tests should FAIL)
- [x] T012 Implement validation functions in src/services/validators.py: validate_title, validate_description, validate_id, validate_status, validate_timestamp
- [x] T013 Run tests for validators (GREEN: tests should PASS)
- [x] T014 Test: Write unit tests for Task model in tests/unit/test_task_model.py (RED: tests should FAIL)
- [x] T015 Implement Task dataclass in src/models/task.py with validation, to_dict(), from_dict(), mark_completed(), mark_pending(), update_title(), update_description()
- [x] T016 Run tests for Task model (GREEN: tests should PASS)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View First Task (Priority: P1) 🎯 MVP

**Goal**: User can add a task with title/description and view it in a formatted table

**Independent Test**: Launch app with no tasks, add task "Buy groceries" with description "Milk, eggs", verify success message with 8-char ID, view all tasks, see formatted table with task showing (✗) status icon and truncated description

### Tests for User Story 1 (TDD: Write these FIRST)

> **RED Phase**: Write tests, verify they FAIL before implementation

- [x] T017 [P] [US1] Test: Write contract tests for StorageInterface in tests/contract/test_storage_contract.py: test_load_creates_file_if_missing, test_save_atomic_write, test_create_backup
- [x] T018 [P] [US1] Test: Write unit tests for JSONStorage in tests/unit/test_json_storage.py: test_load_empty, test_save_tasks, test_atomic_write_pattern, test_file_permissions, test_corruption_backup
- [x] T019 [P] [US1] Test: Write unit tests for TaskService.add_task in tests/unit/test_task_service.py: test_add_task_generates_unique_id, test_add_task_sets_timestamps, test_add_task_validates_title, test_add_task_validates_description
- [x] T020 [P] [US1] Test: Write unit tests for TaskService.get_all_tasks in tests/unit/test_task_service.py: test_get_all_tasks_empty, test_get_all_tasks_sorted_newest_first
- [x] T021 [P] [US1] Test: Write unit tests for formatters in tests/unit/test_formatters.py: test_create_task_table, test_show_success_panel, test_show_error_panel
- [x] T022 [P] [US1] Test: Write integration test for add workflow in tests/integration/test_add_workflow.py: test_add_task_end_to_end_with_storage
- [x] T023 [P] [US1] Test: Write integration test for view workflow in tests/integration/test_view_workflow.py: test_view_all_tasks_end_to_end
- [x] T024 Run all User Story 1 tests (verify they FAIL - RED phase complete)

### Implementation for User Story 1

> **GREEN Phase**: Implement just enough to make tests pass

- [x] T025 [P] [US1] Implement StorageInterface protocol in src/storage/interface.py with load(), save(), create_backup(), file_path property
- [x] T026 [P] [US1] Implement JSONStorage in src/storage/json_storage.py: __init__(file_path), load() with auto-create, save() with atomic write (temp + rename), create_backup(), _validate_schema()
- [ ] T027 [US1] Run JSONStorage tests (verify they PASS)
- [x] T028 [P] [US1] Implement TaskServiceInterface protocol in src/services/interface.py with add_task(), get_task(), get_all_tasks() methods
- [x] T029 [US1] Implement TaskService in src/services/task_service.py: __init__(storage), add_task() with UUID generation and collision detection, get_task(), get_all_tasks() with sorting
- [ ] T030 [US1] Run TaskService tests for add_task and get_all_tasks (verify they PASS)
- [x] T031 [P] [US1] Implement rich formatters in src/cli/display/formatters.py: create_task_table(), create_single_task_panel(), show_success(), show_error() with custom theme
- [x] T032 [P] [US1] Implement message constants in src/cli/display/messages.py: SUCCESS_TASK_ADDED, ERROR_TITLE_EMPTY, ERROR_TITLE_TOO_LONG, etc.
- [ ] T033 [US1] Run formatter tests (verify they PASS)
- [x] T034 [US1] Implement AddCommand in src/cli/commands/add.py: prompt for title (questionary.text with validation), prompt for description, call service.add_task(), show success with task details
- [x] T035 [US1] Implement ViewCommand in src/cli/commands/view.py: show_all_tasks() to get tasks from service, display with create_task_table(), handle empty state
- [x] T036 [US1] Implement main menu in src/cli/app.py: questionary.select() with options (Add, View, Update, Delete, Mark Complete, Exit), route to commands
- [x] T037 [US1] Implement main entry point in src/main.py: initialize JSONStorage, TaskService, CLIApp, handle KeyboardInterrupt gracefully
- [x] T038 [US1] Run integration tests for add and view workflows (verify they PASS - GREEN phase complete)

> **REFACTOR Phase**: Clean up code while keeping tests green

- [x] T039 [US1] Refactor: Extract UUID generation to helper function, extract timestamp generation to helper
- [x] T040 [US1] Refactor: Review error handling, ensure all exceptions have user-friendly messages
- [x] T041 [US1] Run all User Story 1 tests again (verify they still PASS after refactoring)

**Checkpoint**: User Story 1 is fully functional and testable independently. User can add and view tasks.

---

## Phase 4: User Story 2 - Update Task Details (Priority: P2)

**Goal**: User can select a task and update its title and/or description

**Independent Test**: Create task, select "Update task", see task list, select task, choose "Title only", enter new title, verify success message shows updated task with new title and updated_at timestamp

### Tests for User Story 2 (TDD: Write these FIRST)

> **RED Phase**: Write tests, verify they FAIL

- [x] T042 [P] [US2] Test: Write unit tests for TaskService.update_task in tests/unit/test_task_service.py: test_update_title_only, test_update_description_only, test_update_both, test_update_nonexistent_task_raises_error, test_update_empty_title_raises_error
- [x] T043 [P] [US2] Test: Write integration test for update workflow in tests/integration/test_update_workflow.py: test_update_task_end_to_end
- [x] T044 Run User Story 2 tests (verify they FAIL - RED phase)

### Implementation for User Story 2

> **GREEN Phase**: Implement to make tests pass

- [x] T045 [US2] Add update_task() method to TaskServiceInterface protocol in src/services/interface.py
- [x] T046 [US2] Implement TaskService.update_task() in src/services/task_service.py: validate task exists, validate new title/description, call task.update_title()/update_description(), save to storage
- [x] T047 [US2] Run TaskService.update_task tests (verify they PASS)
- [x] T048 [US2] Implement UpdateCommand in src/cli/commands/update.py: show task selection (questionary.select with task list), show update menu (Title/Description/Both/Cancel), prompt for new values, call service.update_task(), show updated task
- [x] T049 [US2] Add "Update task" option to main menu routing in src/cli/app.py
- [x] T050 [US2] Run integration test for update workflow (verify PASS - GREEN phase)

> **REFACTOR Phase**

- [x] T051 [US2] Refactor: Extract task selection to reusable helper in src/cli/utils/
- [x] T052 [US2] Run all User Story 2 tests (verify still PASS)

**Checkpoint**: User Story 2 complete. User can now add, view, AND update tasks independently.

---

## Phase 5: User Story 3 - Mark Tasks Complete/Incomplete (Priority: P2)

**Goal**: User can mark tasks as complete (✓) or incomplete (✗) with separate filtered menus

**Independent Test**: Create 2 pending tasks, select "Mark as complete", see only pending tasks in checkbox list, select both, confirm with count, verify success message and tasks show (✓) status

### Tests for User Story 3 (TDD: Write these FIRST)

> **RED Phase**

- [ ] T053 [P] [US3] Test: Write unit tests for TaskService status methods in tests/unit/test_task_service.py: test_mark_completed, test_mark_pending, test_mark_tasks_completed_bulk, test_mark_tasks_pending_bulk, test_mark_nonexistent_task_raises_error
- [ ] T054 [P] [US3] Test: Write unit tests for TaskService.filter_by_status in tests/unit/test_task_service.py: test_filter_pending, test_filter_completed, test_filter_invalid_status_raises_error
- [ ] T055 [P] [US3] Test: Write integration test for complete workflow in tests/integration/test_complete_workflow.py: test_mark_complete_end_to_end, test_mark_incomplete_end_to_end
- [ ] T056 Run User Story 3 tests (verify FAIL - RED phase)

### Implementation for User Story 3

> **GREEN Phase**

- [ ] T057 [US3] Add status methods to TaskServiceInterface in src/services/interface.py: mark_completed(), mark_pending(), mark_tasks_completed(), mark_tasks_pending(), filter_by_status()
- [ ] T058 [US3] Implement TaskService.mark_completed/mark_pending in src/services/task_service.py: validate task exists, call task.mark_completed()/mark_pending(), save
- [ ] T059 [US3] Implement TaskService.mark_tasks_completed/mark_tasks_pending for bulk operations in src/services/task_service.py: validate all IDs exist, update all, save once
- [ ] T060 [US3] Implement TaskService.filter_by_status in src/services/task_service.py: validate status, filter tasks, return sorted list
- [ ] T061 [US3] Run TaskService status tests (verify PASS)
- [ ] T062 [US3] Implement CompleteCommand in src/cli/commands/complete.py: show status action menu (Mark Complete/Mark Incomplete/Back), filter tasks by opposite status, show checkbox selection, confirm with count, call service bulk methods, show success
- [ ] T063 [US3] Add "Mark complete/incomplete" option to main menu in src/cli/app.py
- [ ] T064 [US3] Run integration tests for complete workflow (verify PASS - GREEN phase)

> **REFACTOR Phase**

- [ ] T065 [US3] Refactor: Extract confirmation helper for bulk operations
- [ ] T066 [US3] Run all User Story 3 tests (verify still PASS)

**Checkpoint**: User Story 3 complete. User can now add, view, update, AND toggle task status independently.

---

## Phase 6: User Story 4 - Delete Unwanted Tasks (Priority: P3)

**Goal**: User can select and delete single or multiple tasks with confirmation

**Independent Test**: Create 3 tasks, select "Delete task", see all tasks in checkbox, select 2 tasks, see "Delete 2 selected tasks?" confirmation, confirm, verify success and remaining task shown

### Tests for User Story 4 (TDD: Write these FIRST)

> **RED Phase**

- [ ] T067 [P] [US4] Test: Write unit tests for TaskService delete methods in tests/unit/test_task_service.py: test_delete_task, test_delete_nonexistent_returns_false, test_delete_tasks_bulk, test_delete_tasks_partial_success
- [ ] T068 [P] [US4] Test: Write integration test for delete workflow in tests/integration/test_delete_workflow.py: test_delete_single_task_end_to_end, test_delete_multiple_tasks_end_to_end
- [ ] T069 Run User Story 4 tests (verify FAIL - RED phase)

### Implementation for User Story 4

> **GREEN Phase**

- [ ] T070 [US4] Add delete methods to TaskServiceInterface in src/services/interface.py: delete_task(), delete_tasks()
- [ ] T071 [US4] Implement TaskService.delete_task in src/services/task_service.py: check if exists, remove from storage, save, return boolean
- [ ] T072 [US4] Implement TaskService.delete_tasks for bulk in src/services/task_service.py: count successful deletions, remove all, save once, return count
- [ ] T073 [US4] Run TaskService delete tests (verify PASS)
- [ ] T074 [US4] Implement DeleteCommand in src/cli/commands/delete.py: show all tasks in checkbox, validate non-empty selection, show confirmation with count (questionary.confirm), call service.delete_tasks(), show success and remaining tasks
- [ ] T075 [US4] Add "Delete task" option to main menu in src/cli/app.py
- [ ] T076 [US4] Run integration tests for delete workflow (verify PASS - GREEN phase)

> **REFACTOR Phase**

- [ ] T077 [US4] Refactor: Ensure consistent confirmation pattern across delete/complete commands
- [ ] T078 [US4] Run all User Story 4 tests (verify still PASS)

**Checkpoint**: User Story 4 complete. User can now add, view, update, toggle status, AND delete tasks independently.

---

## Phase 7: User Story 5 - Filter and Navigate Task Lists (Priority: P3)

**Goal**: User can filter tasks by status (all/pending/completed) and navigate paginated results (10 per page)

**Independent Test**: Create 15 tasks (8 pending, 7 completed), select "View pending tasks", verify only 8 pending shown with pagination controls, navigate to page 2, verify correct tasks shown, select task from view, see submenu (Update/Delete/Toggle/Back)

### Tests for User Story 5 (TDD: Write these FIRST)

> **RED Phase**

- [ ] T079 [P] [US5] Test: Write unit tests for TaskService.paginate in tests/unit/test_task_service.py: test_paginate_first_page, test_paginate_middle_page, test_paginate_last_page, test_paginate_beyond_range_returns_empty
- [ ] T080 [P] [US5] Test: Write unit tests for TaskService.count_tasks in tests/unit/test_task_service.py: test_count_tasks_returns_stats
- [ ] T081 [P] [US5] Test: Write integration test for filter/pagination in tests/integration/test_view_workflow.py: test_filter_pending_with_pagination, test_filter_completed_with_pagination
- [ ] T082 Run User Story 5 tests (verify FAIL - RED phase)

### Implementation for User Story 5

> **GREEN Phase**

- [ ] T083 [US5] Add pagination methods to TaskServiceInterface in src/services/interface.py: paginate(), count_tasks()
- [ ] T084 [US5] Implement TaskService.paginate in src/services/task_service.py: slice tasks by page/page_size, return page slice
- [ ] T085 [US5] Implement TaskService.count_tasks in src/services/task_service.py: count total/pending/completed, return dict
- [ ] T086 [US5] Run TaskService pagination tests (verify PASS)
- [ ] T087 [US5] Update ViewCommand in src/cli/commands/view.py: add filter menu (All/Pending/Completed/Back), add pagination navigation (Next/Previous/Back), show "Showing X-Y of Z" header, implement page state tracking
- [ ] T088 [US5] Add task action submenu to ViewCommand: after viewing table, show "Select a task" or "Back to main menu", if task selected show submenu (Update/Delete/Toggle status/Back), route to appropriate command
- [ ] T089 [US5] Run integration tests for filter/pagination (verify PASS - GREEN phase)

> **REFACTOR Phase**

- [ ] T090 [US5] Refactor: Extract pagination logic to reusable helper
- [ ] T091 [US5] Run all User Story 5 tests (verify still PASS)

**Checkpoint**: User Story 5 complete. All 5 user stories now independently functional. Application feature-complete for MVP scope.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories and final quality gates

- [ ] T092 [P] Implement terminal width detection in src/cli/utils/terminal.py: get_terminal_width(), validate_terminal_width() with MIN_TERMINAL_WIDTH check
- [ ] T093 [P] Implement keyboard interrupt handler in src/cli/utils/interrupts.py: catch KeyboardInterrupt, show "👋 Thanks for using Todo CLI! Goodbye." message
- [ ] T094 [P] Add --simple flag support to src/main.py for accessibility (plain text output, no colors)
- [ ] T095 [P] Test: Write unit tests for terminal utils in tests/unit/test_terminal_utils.py
- [ ] T096 [P] Test: Write unit tests for interrupt handling in tests/unit/test_interrupts.py
- [ ] T097 Add logging infrastructure: create logger in src/cli/app.py with DEBUG level for development, ERROR level for production
- [ ] T098 Add empty state handling across all commands: check for empty task list, show "⚠️ No tasks exist yet. Create your first task!" message with appropriate routing
- [ ] T099 Implement file permission check on startup in src/storage/json_storage.py: validate read/write access to project root, set chmod 600 on tasks.json
- [ ] T100 [P] Create pyproject.toml with complete configuration: project metadata, dependencies, tool.black, tool.ruff, tool.pytest, tool.coverage
- [ ] T101 [P] Create mypy.ini with strict mode configuration: enable Protocols, disallow_untyped_defs, no_implicit_optional
- [ ] T102 [P] Create .ruff.toml with linting rules: line-length=100, select rules E,F,I,N,W,UP
- [ ] T103 Run full test suite: pytest --cov=src --cov-report=term-missing --cov-report=html tests/ (verify 100% pass, 80%+ coverage)
- [ ] T104 Run type checking: mypy . (verify no errors in strict mode)
- [ ] T105 Run linting: ruff check . (verify no errors)
- [ ] T106 Run formatting check: black --check . (verify all files formatted)
- [ ] T107 Manual integration test: Run through all 5 user stories end-to-end, verify all acceptance criteria met
- [ ] T108 [P] Update README.md with installation instructions, usage guide, development setup (defer to quickstart.md)
- [ ] T109 Performance test: Create 1000 tasks, verify table renders in < 1s, verify operations remain responsive
- [ ] T110 Security audit: Verify no hardcoded paths, no secrets, file permissions set correctly, input validation complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if team capacity allows)
  - OR sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P2) → US4 (P3) → US5 (P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (T016) - **No dependencies on other stories** ✅
- **User Story 2 (P2)**: Can start after Foundational (T016) - **No dependencies on other stories** ✅
- **User Story 3 (P2)**: Can start after Foundational (T016) - **No dependencies on other stories** ✅
- **User Story 4 (P3)**: Can start after Foundational (T016) - **No dependencies on other stories** ✅
- **User Story 5 (P3)**: Can start after Foundational (T016) - Extends US1's view command but independently testable ✅

### TDD Workflow Within Each User Story

1. **RED Phase**: Write tests FIRST, verify they FAIL (no implementation yet)
2. **GREEN Phase**: Implement just enough code to make tests PASS
3. **REFACTOR Phase**: Clean up code while keeping all tests green
4. Repeat RED-GREEN-REFACTOR for each feature within the story

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003, T004, T005, T006 can run in parallel (different files)

**Foundational Phase (Phase 2)**:
- T008, T009, T010 can run in parallel (different files)
- Test/implementation pairs must run sequentially within TDD cycle

**User Story Phases (Phases 3-7)**:
- After Foundational complete, **ALL user stories can start in parallel** if team has capacity
- Within each user story:
  - All test tasks marked [P] can run in parallel (RED phase)
  - Implementation tasks marked [P] can run in parallel (GREEN phase)
  - Example US1: T017, T018, T019, T020, T021, T022, T023 (all tests) can run together
  - Example US1: T025, T026, T028, T031, T032 (models + formatters) can run together after tests written

**Polish Phase (Phase 8)**:
- T092, T093, T094, T095, T096, T100, T101, T102, T108 can run in parallel

---

## Parallel Example: User Story 1 (RED Phase)

```bash
# Launch all User Story 1 tests together (RED phase):
Task: "Contract tests for StorageInterface in tests/contract/test_storage_contract.py"
Task: "Unit tests for JSONStorage in tests/unit/test_json_storage.py"
Task: "Unit tests for TaskService.add_task in tests/unit/test_task_service.py"
Task: "Unit tests for TaskService.get_all_tasks in tests/unit/test_task_service.py"
Task: "Unit tests for formatters in tests/unit/test_formatters.py"
Task: "Integration test for add workflow in tests/integration/test_add_workflow.py"
Task: "Integration test for view workflow in tests/integration/test_view_workflow.py"

# Then verify all tests FAIL (no implementation yet)
# Then move to GREEN phase implementation
```

## Parallel Example: User Story 1 (GREEN Phase)

```bash
# After tests are written and failing, launch parallel implementation:
Task: "Implement StorageInterface protocol in src/storage/interface.py"
Task: "Implement JSONStorage in src/storage/json_storage.py"
Task: "Implement TaskServiceInterface protocol in src/services/interface.py"
Task: "Implement formatters in src/cli/display/formatters.py"
Task: "Implement message constants in src/cli/display/messages.py"

# Then implement sequential dependencies (TaskService needs interfaces first)
# Then implement CLI commands (need services + formatters)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Minimum Viable Product)

1. Complete **Phase 1: Setup** (T001-T007)
2. Complete **Phase 2: Foundational** (T008-T016) - **CRITICAL BLOCKER**
3. Complete **Phase 3: User Story 1** (T017-T041)
4. **STOP and VALIDATE**: Run all User Story 1 tests independently
5. Manual test: Add task, view task, verify it works end-to-end
6. **Deploy/Demo MVP** (if ready)

At this point you have a working todo app where users can add and view tasks!

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → **Foundation ready** ✅
2. Add **User Story 1** → Test independently → **MVP Deployed!** 🎯
3. Add **User Story 2** → Test independently → **v1.1 Deployed** (now with updates)
4. Add **User Story 3** → Test independently → **v1.2 Deployed** (now with status tracking)
5. Add **User Story 4** → Test independently → **v1.3 Deployed** (now with deletion)
6. Add **User Story 5** → Test independently → **v1.4 Deployed** (now with filters/pagination)
7. Complete **Polish** → **v2.0 Production Ready** 🚀

Each story adds value incrementally without breaking previous functionality.

### Parallel Team Strategy (if multiple developers available)

1. **All team members** complete Setup + Foundational together
2. Once Foundational is done (after T016):
   - **Developer A**: User Story 1 (T017-T041)
   - **Developer B**: User Story 2 (T042-T052)
   - **Developer C**: User Story 3 (T053-T066)
   - **Developer D**: User Story 4 (T067-T078)
   - **Developer E**: User Story 5 (T079-T091)
3. Stories complete independently and integrate without conflicts
4. All stories merge and work together

---

## Task Summary

- **Total Tasks**: 110
- **Setup Phase**: 7 tasks
- **Foundational Phase**: 9 tasks (includes TDD cycles)
- **User Story 1 (P1)**: 25 tasks (7 test tasks + 18 implementation/refactor)
- **User Story 2 (P2)**: 11 tasks (3 test tasks + 8 implementation/refactor)
- **User Story 3 (P2)**: 14 tasks (4 test tasks + 10 implementation/refactor)
- **User Story 4 (P3)**: 12 tasks (3 test tasks + 9 implementation/refactor)
- **User Story 5 (P3)**: 13 tasks (4 test tasks + 9 implementation/refactor)
- **Polish Phase**: 19 tasks

**Parallel Opportunities**: 42 tasks marked [P] can run in parallel (38% of tasks)

**Independent Stories**: All 5 user stories are independently testable after Foundational phase

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 41 tasks

---

## Notes

- **TDD REQUIRED**: This project follows strict TDD. All test tasks are MANDATORY and must be written BEFORE implementation
- **RED-GREEN-REFACTOR**: Each user story follows the cycle: write failing tests (RED) → implement to pass (GREEN) → clean up code (REFACTOR)
- **100% Test Pass Rate**: Constitution requires 100% of tests must pass before commit. No exceptions.
- **80-100% Coverage Goal**: Aim for 100% code coverage, minimum 80% required
- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] label**: Maps task to user story for traceability (US1, US2, US3, US4, US5)
- **Independent Stories**: Each story can be completed, tested, and demoed independently
- **Commit Strategy**: Commit after each GREEN phase (tests pass), and after each REFACTOR phase
- **Quality Gates**: Run ruff, black, mypy, pytest before every commit
- **Stop at Checkpoints**: Validate each story independently before moving to next priority

---

## Validation Checklist

Before considering tasks complete:

- [ ] All 110 tasks have clear file paths
- [ ] All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with path`
- [ ] All test tasks are marked as required (not optional)
- [ ] Each user story has RED-GREEN-REFACTOR phases clearly marked
- [ ] Each user story has Independent Test criteria defined
- [ ] Each user story has Checkpoint validation step
- [ ] Dependencies clearly show Foundational blocks all stories
- [ ] User stories can proceed in parallel after Foundational
- [ ] MVP scope clearly identified (Phase 1 + 2 + 3)
- [ ] Parallel opportunities identified and marked [P]
- [ ] TDD workflow (RED-GREEN-REFACTOR) explained and enforced
