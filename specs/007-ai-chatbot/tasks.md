---

description: "Task list for AI-Powered Task Management Chatbot implementation"
---

# Tasks: AI-Powered Task Management Chatbot

**Input**: Design documents from `/specs/007-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Tests are OPTIONAL in this implementation - tasks will focus on feature delivery without test-first approach unless explicitly needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: FastAPI + SQLModel
- Frontend: Next.js 15 App Router + React 19

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install backend dependencies (openai-agents[litellm], litellm, fastmcp, dateparser) in backend/requirements.txt
- [X] T002 [P] Install frontend dependencies (@openai/chatkit-react) in frontend/package.json
- [X] T003 [P] Configure environment variables (ZAI_API_KEY, DATABASE_URL) in backend/.env.example
- [X] T004 [P] Update backend project structure with new directories: backend/src/mcp/, backend/src/services/chat_service.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create database migration for conversations table in backend/alembic/versions/xxx_add_conversations_messages.py
- [X] T006 Create database migration for messages table in backend/alembic/versions/xxx_add_conversations_messages.py
- [X] T007 Add due_date and priority columns to tasks table in backend/alembic/versions/xxx_extend_tasks.py
- [X] T008 [P] Create Conversation SQLModel in backend/src/models/conversation.py
- [X] T009 [P] Create Message SQLModel in backend/src/models/message.py
- [X] T010 [P] Extend Task SQLModel with due_date and priority fields in backend/src/models/task.py
- [X] T011 Run database migrations (alembic upgrade head)
- [X] T012 [P] Create ConversationService with CRUD operations in backend/src/services/conversation_service.py
- [X] T013 [P] Create MessageService with CRUD operations in backend/src/services/message_service.py
- [X] T014 [P] Create DateParserService for natural language date parsing in backend/src/services/date_parser_service.py
- [X] T015 Setup FastMCP server in backend/src/mcp/server.py
- [X] T016 Create Pydantic schemas for chat API in backend/src/schemas/chat.py
- [X] T017 [P] Create Pydantic schemas for conversations in backend/src/schemas/conversation.py
- [X] T018 [P] Create Pydantic schemas for messages in backend/src/schemas/message.py
- [X] T019 Setup structured JSON logging with request_id in backend/src/core/logging.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can add new tasks by describing what they need to do in natural conversation without navigating forms or buttons

**Independent Test**: Send message "I need to buy groceries tomorrow" and verify a new task is created with appropriate title and due date

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement add_task MCP tool in backend/src/mcp/tools/task_tools.py
- [X] T021 [P] [US1] Implement list_tasks MCP tool in backend/src/mcp/tools/task_tools.py
- [X] T022 [US1] Register task MCP tools with FastMCP server in backend/src/mcp/server.py
- [X] T023 [US1] Create OpenAI Agent with LiteLLM + GLM-4.5-air configuration in backend/src/services/chat_service.py
- [X] T024 [US1] Implement ChatService.send_message with agent orchestration in backend/src/services/chat_service.py
- [X] T025 [US1] Implement conversation context loading (last 50 messages) in backend/src/services/chat_service.py
- [X] T026 [US1] Implement POST /api/v1/chat endpoint with SSE streaming in backend/src/api/routes/chat.py
- [X] T027 [US1] Add error handling for OpenAI API failures with user-friendly messages in backend/src/services/chat_service.py
- [X] T028 [US1] Add structured logging for tool invocations in backend/src/services/chat_service.py
- [X] T029 [US1] Create ChatInterface component in frontend/components/features/chat/ChatInterface.tsx (using ChatKit React)
- [X] T030 [US1] Integrate @openai/chatkit-react with /api/v1/chatkit endpoint via floating ChatBubble component
- [X] T031 [US1] ChatKit React handles SSE streaming internally (no custom hook needed)
- [X] T032 [US1] Authentication integrated via authClient.token() in ChatInterface component

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - Set Task Metadata via Conversation (Priority: P1)

**Goal**: Users can set due dates, priority levels, and tags for tasks through natural language without using form fields

**Independent Test**: Say "Create a high priority task to submit report by December 30th with tags work and urgent" and verify all metadata is correctly set

### Implementation for User Story 2

- [ ] T033 [P] [US2] Integrate DateParserService into add_task MCP tool in backend/src/mcp/tools/task_tools.py
- [ ] T034 [P] [US2] Add priority parsing logic to add_task MCP tool in backend/src/mcp/tools/task_tools.py
- [ ] T035 [P] [US2] Add tag parsing logic to add_task MCP tool in backend/src/mcp/tools/task_tools.py
- [ ] T036 [US2] Add validation for due_date (must be future) in backend/src/services/date_parser_service.py
- [ ] T037 [US2] Add validation for priority (low, medium, high) in backend/src/mcp/tools/task_tools.py
- [ ] T038 [US2] Implement clarifying questions for ambiguous dates in backend/src/services/chat_service.py
- [ ] T039 [US2] Update agent instructions to extract metadata from natural language in backend/src/services/chat_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can create tasks with full metadata via conversation

---

## Phase 5: User Story 4 - View and Query Tasks (Priority: P1)

**Goal**: Users can ask the chatbot about their tasks using natural language queries, getting filtered views without manually navigating the UI

**Independent Test**: Ask "What are my pending tasks?" or "Show me all my tasks" and verify the chatbot returns the correct task list

### Implementation for User Story 4

- [ ] T040 [P] [US4] Enhance list_tasks MCP tool with filtering by status in backend/src/mcp/tools/task_tools.py
- [ ] T041 [P] [US4] Enhance list_tasks MCP tool with filtering by priority in backend/src/mcp/tools/task_tools.py
- [ ] T042 [P] [US4] Enhance list_tasks MCP tool with filtering by tags in backend/src/mcp/tools/task_tools.py
- [ ] T043 [P] [US4] Enhance list_tasks MCP tool with filtering by due date range in backend/src/mcp/tools/task_tools.py
- [ ] T044 [US4] Update agent instructions to handle query intents (show, list, what, filter) in backend/src/services/chat_service.py
- [ ] T045 [US4] Format list_tasks results for conversational display in backend/src/services/chat_service.py
- [ ] T046 [US4] Add MessageList component to display task results in frontend/src/components/features/chat/MessageList.tsx

**Checkpoint**: At this point, User Stories 1, 2, and 4 are complete - users can create and view tasks conversationally

---

## Phase 6: User Story 9 - Conversational Context and Memory (Priority: P2)

**Goal**: The chatbot maintains conversation history within a session, allowing users to reference previous messages and creating natural conversational flow

**Independent Test**: Have a conversation like "Add a task for groceries" followed by "Also add one for laundry" and verify both tasks are created correctly

### Implementation for User Story 9

- [ ] T047 [US9] Implement conversation persistence (save user and assistant messages) in backend/src/services/chat_service.py
- [ ] T048 [US9] Implement GET /api/v1/conversations endpoint in backend/src/api/v1/conversations.py
- [ ] T049 [US9] Implement GET /api/v1/conversations/{id}/messages endpoint in backend/src/api/v1/conversations.py
- [ ] T050 [US9] Create ConversationList sidebar component in frontend/src/components/features/chat/ConversationList.tsx
- [ ] T051 [US9] Implement useConversations hook in frontend/src/hooks/useConversations.ts
- [ ] T052 [US9] Add conversation switching functionality in frontend/src/components/features/chat/ChatInterface.tsx
- [ ] T053 [US9] Implement message pagination for conversation history in frontend/src/components/features/chat/MessageList.tsx
- [ ] T054 [US9] Add "New Conversation" button in frontend/src/components/features/chat/ConversationList.tsx

**Checkpoint**: At this point, conversational memory is functional - chatbot can reference previous messages

---

## Phase 7: User Story 5 - Mark Tasks as Complete (Priority: P2)

**Goal**: Users can mark tasks as done through conversational commands, getting immediate confirmation without clicking through the UI

**Independent Test**: Say "Mark task 3 as complete" or "I finished the groceries task" and verify the task status changes to completed

### Implementation for User Story 5

- [ ] T055 [P] [US5] Implement complete_task MCP tool in backend/src/mcp/tools/task_tools.py
- [ ] T056 [US5] Register complete_task tool with FastMCP server in backend/src/mcp/server.py
- [ ] T057 [US5] Update agent instructions to handle completion intents (mark complete, done with, finished) in backend/src/services/chat_service.py
- [ ] T058 [US5] Add task disambiguation logic when multiple matches exist in backend/src/services/chat_service.py
- [ ] T059 [US5] Add confirmation messages for task completion in backend/src/services/chat_service.py

**Checkpoint**: Users can now create, view, and complete tasks via conversation

---

## Phase 8: User Story 3 - Use Task Templates (Priority: P2)

**Goal**: Users can create tasks from predefined templates by mentioning the template name, instantly populating all template fields

**Independent Test**: Say "Create a task using the weekly report template" and verify a task is created with all template-defined fields pre-populated

### Implementation for User Story 3

- [ ] T060 [P] [US3] Implement list_templates MCP tool in backend/src/mcp/tools/template_tools.py
- [ ] T061 [P] [US3] Implement create_from_template MCP tool in backend/src/mcp/tools/template_tools.py
- [ ] T062 [US3] Register template tools with FastMCP server in backend/src/mcp/server.py
- [ ] T063 [US3] Update agent instructions to recognize template requests in backend/src/services/chat_service.py
- [ ] T064 [US3] Add template not found error handling with suggestions in backend/src/services/chat_service.py
- [ ] T065 [US3] Implement template customization (override title, due date) in backend/src/mcp/tools/template_tools.py

**Checkpoint**: Template functionality is complete - users can create tasks from templates

---

## Phase 9: User Story 6 - Update Task Details (Priority: P3)

**Goal**: Users can modify existing task titles, descriptions, due dates, priorities, and tags through natural conversation without navigating to edit forms

**Independent Test**: Say "Change task 1 to 'Call mom tonight at 7pm'" and verify the task title is updated accordingly

### Implementation for User Story 6

- [ ] T066 [P] [US6] Implement update_task MCP tool in backend/src/mcp/tools/task_tools.py
- [ ] T067 [US6] Register update_task tool with FastMCP server in backend/src/mcp/server.py
- [ ] T068 [US6] Update agent instructions to handle update intents (change, update, modify) in backend/src/services/chat_service.py
- [ ] T069 [US6] Add field-specific update logic (title, description, due_date, priority, tags) in backend/src/mcp/tools/task_tools.py
- [ ] T070 [US6] Add task disambiguation for vague update requests in backend/src/services/chat_service.py
- [ ] T071 [US6] Add confirmation messages showing what changed in backend/src/services/chat_service.py

**Checkpoint**: Users can now update existing tasks via conversation

---

## Phase 10: User Story 7 - Delete Tasks (Priority: P3)

**Goal**: Users can remove tasks they no longer need through conversational commands

**Independent Test**: Say "Delete task 5" or "Remove the old meeting task" and verify the task is removed from the list

### Implementation for User Story 7

- [ ] T072 [P] [US7] Implement delete_task MCP tool in backend/src/mcp/tools/task_tools.py
- [ ] T073 [US7] Register delete_task tool with FastMCP server in backend/src/mcp/server.py
- [ ] T074 [US7] Update agent instructions to handle delete intents (delete, remove) in backend/src/services/chat_service.py
- [ ] T075 [US7] Add task disambiguation for deletion with multiple matches in backend/src/services/chat_service.py
- [ ] T076 [US7] Add confirmation messages with deleted task details in backend/src/services/chat_service.py

**Checkpoint**: Users can now delete tasks via conversation

---

## Phase 11: User Story 8 - Manage Tags via Conversation (Priority: P3)

**Goal**: Users can create new tags, view available tags, and filter tasks by tags through natural language

**Independent Test**: Ask "What tags do I have?" and verify all unique tags are listed, then say "Show me all tasks tagged with urgent"

### Implementation for User Story 8

- [ ] T077 [P] [US8] Implement list_tags MCP tool in backend/src/mcp/tools/tag_tools.py
- [ ] T078 [P] [US8] Implement add_tag MCP tool in backend/src/mcp/tools/tag_tools.py
- [ ] T079 [P] [US8] Implement remove_tag MCP tool in backend/src/mcp/tools/tag_tools.py
- [ ] T080 [US8] Register tag tools with FastMCP server in backend/src/mcp/server.py
- [ ] T081 [US8] Update agent instructions to handle tag management intents in backend/src/services/chat_service.py
- [ ] T082 [US8] Implement case-insensitive tag matching (Work = work) in backend/src/mcp/tools/tag_tools.py

**Checkpoint**: All user stories are now complete - full conversational task management is functional

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T083 [P] Add health check endpoint GET /health in backend/src/api/v1/health.py
- [ ] T084 [P] Implement rate limiting (100 req/min/user) in backend/src/middleware/rate_limiter.py
- [ ] T085 [P] Add CORS configuration for frontend origin in backend/src/main.py
- [ ] T086 [P] Setup distributed tracing for OpenAI API calls in backend/src/core/tracing.py
- [ ] T087 [P] Add metrics endpoints for monitoring (response time, error rates) in backend/src/api/v1/metrics.py
- [ ] T088 [P] Implement error boundary in frontend in frontend/src/components/ErrorBoundary.tsx
- [ ] T089 [P] Add loading states and empty states to chat UI in frontend/src/components/features/chat/
- [ ] T090 [P] Add toast notifications for errors in frontend/src/components/ui/toast.tsx
- [ ] T091 [P] Implement retry logic for failed OpenAI API calls in backend/src/services/chat_service.py
- [ ] T092 [P] Add input validation (max 2000 chars) for chat messages in frontend/src/components/features/chat/MessageInput.tsx
- [ ] T093 [P] Create Docker configuration files (Dockerfile, docker-compose.yml) in backend/
- [ ] T094 [P] Create frontend Docker configuration in frontend/Dockerfile
- [ ] T095 [P] Update CLAUDE.md with new chat endpoints and MCP tools in CLAUDE.md
- [ ] T096 Run quickstart.md validation to ensure all setup steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-11)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US2 (P1) → US4 (P1) → US9 (P2) → US5 (P2) → US3 (P2) → US6 (P3) → US7 (P3) → US8 (P3)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories ✅ MVP Core
- **User Story 2 (P1)**: Can start after Foundational - Enhances US1, independently testable ✅ MVP Core
- **User Story 4 (P1)**: Can start after Foundational - Requires list_tasks from US1, independently testable ✅ MVP Core
- **User Story 9 (P2)**: Can start after Foundational - Enhances UX across all stories, independently testable
- **User Story 5 (P2)**: Can start after Foundational - Requires list_tasks from US1 for disambiguation
- **User Story 3 (P2)**: Can start after Foundational - Uses task creation from US1, independently testable
- **User Story 6 (P3)**: Can start after Foundational - Requires list_tasks from US1 for disambiguation
- **User Story 7 (P3)**: Can start after Foundational - Requires list_tasks from US1 for disambiguation
- **User Story 8 (P3)**: Can start after Foundational - Independently testable

### Within Each User Story

- MCP tools before agent integration
- Backend services before API endpoints
- API endpoints before frontend components
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- MCP tools within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch MCP tools for User Story 1 together:
Task: "Implement add_task MCP tool in backend/src/mcp/tools/task_tools.py"
Task: "Implement list_tasks MCP tool in backend/src/mcp/tools/task_tools.py"

# After tools are registered, these can run in parallel:
Task: "Create ChatInterface component in frontend/src/components/features/chat/ChatInterface.tsx"
Task: "Add authentication headers to chat API calls in frontend/src/lib/api-client.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 4 Only) - Recommended

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create tasks)
4. Complete Phase 4: User Story 2 (Set metadata)
5. Complete Phase 5: User Story 4 (View/query tasks)
6. **STOP and VALIDATE**: Test MVP independently - users can create, view, and manage tasks conversationally
7. Deploy/demo if ready

**MVP Scope**: US1 + US2 + US4 = Core conversational task management (create, view, query with metadata)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic task creation!)
3. Add User Story 2 → Test independently → Deploy/Demo (Full metadata support!)
4. Add User Story 4 → Test independently → Deploy/Demo (MVP complete - query and view!)
5. Add User Story 9 → Test independently → Deploy/Demo (Conversation memory!)
6. Add User Story 5 → Test independently → Deploy/Demo (Task completion!)
7. Add User Story 3 → Test independently → Deploy/Demo (Templates!)
8. Add User Stories 6, 7, 8 → Test independently → Deploy/Demo (Full CRUD!)
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Create tasks)
   - Developer B: User Story 2 (Metadata)
   - Developer C: User Story 4 (View/query)
3. After MVP (US1, US2, US4) validated:
   - Developer A: User Story 9 (Context)
   - Developer B: User Story 5 (Complete)
   - Developer C: User Story 3 (Templates)
4. Final sprint:
   - Developer A: User Story 6 (Update)
   - Developer B: User Story 7 (Delete)
   - Developer C: User Story 8 (Tags)
5. Polish phase: All developers work on cross-cutting concerns together

---

## Task Summary

**Total Tasks**: 96
**Breakdown by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 15 tasks (BLOCKING)
- Phase 3 (US1 - Create Tasks): 13 tasks ✅ MVP
- Phase 4 (US2 - Set Metadata): 7 tasks ✅ MVP
- Phase 5 (US4 - View/Query): 7 tasks ✅ MVP
- Phase 6 (US9 - Context): 8 tasks
- Phase 7 (US5 - Complete): 5 tasks
- Phase 8 (US3 - Templates): 6 tasks
- Phase 9 (US6 - Update): 6 tasks
- Phase 10 (US7 - Delete): 5 tasks
- Phase 11 (US8 - Tags): 6 tasks
- Phase 12 (Polish): 14 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**MVP Scope (Recommended)**: Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5 = 46 tasks
- Delivers: Create tasks, set metadata, view/query tasks via natural language
- Independent test criteria: Users can fully manage tasks conversationally without UI

**Format Validation**: ✅ All tasks follow the checklist format:
- Checkbox: `- [ ]`
- Task ID: Sequential (T001-T096)
- [P] marker: 45 tasks parallelizable
- [Story] label: All user story tasks labeled (US1-US9)
- Description: Clear action with exact file path

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- OpenAI Agents SDK + LiteLLM + GLM-4.5-air for AI orchestration
- FastMCP 2.0 for MCP server implementation
- @openai/chatkit-react for frontend chat UI
- Server-Sent Events (SSE) for streaming responses
- dateparser for natural language date parsing
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
