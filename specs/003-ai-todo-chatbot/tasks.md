# Tasks: AI Todo Chatbot

**Input**: Design documents from `/specs/003-ai-todo-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested — test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app monorepo**: `backend/` (FastAPI), `frontend/` (Next.js)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependencies, configuration, and directory scaffolding

- [x] T001 Add backend dependencies (openai-agents, mcp[cli], openai-chatkit) to backend/pyproject.toml
- [x] T002 [P] Add frontend dependency (@openai/chatkit-react) to frontend/package.json
- [x] T003 [P] Add GEMINI_API_KEY setting to backend/app/core/config.py
- [x] T004 [P] Create backend module directories with __init__.py files for backend/app/chat/ and backend/app/mcp/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, database migration, ChatKit Store, MCP server skeleton, agent factory, and frontend chat infrastructure

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create Conversation and Message SQLModel models in backend/app/models/conversation.py per data-model.md
- [x] T006 Create Alembic migration for conversation and message tables in backend/alembic/versions/ per data-model.md SQL
- [x] T007 [P] Create RequestContext dataclass with user_id field in backend/app/chat/context.py
- [x] T008 Implement PostgreSQL ChatKit Store (all 10 interface methods + user isolation) in backend/app/chat/store.py per research.md R5
- [x] T009 [P] Create chat request/response Pydantic schemas in backend/app/schemas/chat.py
- [x] T010 [P] Create FastMCP server skeleton with asyncpg connection pool and __main__ entry point in backend/app/mcp/server.py per research.md R2
- [x] T011 [P] Create agent factory function (Gemini 2.5 Flash via OpenAIChatCompletionsModel, set_tracing_disabled) in backend/app/chat/agent.py per research.md R1
- [x] T012 [P] Add ChatKit web component script tag (beforeInteractive) to frontend/app/layout.tsx per research.md R4
- [x] T013 [P] Create Next.js API proxy route (read httpOnly cookie → forward as Bearer JWT) in frontend/app/api/chatkit/route.ts per research.md R4

**Checkpoint**: Foundation ready — database tables exist, Store persists conversations, MCP server starts, agent connects to Gemini, frontend can proxy to backend

---

## Phase 3: User Story 1 — Chat to Add a Task (Priority: P1) 🎯 MVP

**Goal**: An authenticated user types a natural language message like "Add a task to buy groceries" and the AI creates the task and confirms

**Independent Test**: Send "Add a task to buy groceries" in the chat UI → verify task appears in the user's task list (/dashboard) and the assistant confirms with the task title

### Implementation for User Story 1

- [x] T014 [US1] Implement todo_create_task MCP tool (user_id, title, description params, asyncpg INSERT, return confirmation string) in backend/app/mcp/server.py per contracts/mcp-tools.yaml
- [x] T015 [US1] Implement TodoChatKitServer.respond() — create agent with MCP server, run streamed, yield SSE events (no history loading yet) — in backend/app/chat/server.py per research.md R3
- [x] T016 [US1] Create POST /chatkit endpoint that extracts user_id from JWT and delegates to TodoChatKitServer.process() in backend/app/api/chat.py per contracts/chatkit-api.yaml
- [x] T017 [US1] Update backend/app/main.py to add frontend origin to CORS and include chat router
- [x] T018 [P] [US1] Create ChatKit wrapper component with useChatKit hook and auth fetch in frontend/components/chat/chat-interface.tsx per research.md R4
- [x] T019 [US1] Create protected chat page that renders ChatInterface component in frontend/app/(protected)/chat/page.tsx
- [x] T020 [P] [US1] Create chat utility functions (getJwtToken helper) in frontend/lib/chat.ts
- [x] T021 [P] [US1] Add navigation link to /chat on the dashboard page in frontend/app/(protected)/dashboard/page.tsx

**Checkpoint**: User can open /chat, type "Add a task to buy groceries", and see the task created. Full end-to-end streaming works. This is the MVP.

---

## Phase 4: User Story 2 — Chat to View Tasks (Priority: P1)

**Goal**: User asks "Show me all my tasks" or "What's pending?" and the assistant lists the appropriate tasks

**Independent Test**: Create several tasks via dashboard, then ask "Show my tasks" in chat → verify correct task list is returned with status indicators

### Implementation for User Story 2

- [x] T022 [US2] Implement todo_list_tasks MCP tool (user_id, status filter: all/completed/incomplete, asyncpg SELECT, formatted list output) in backend/app/mcp/server.py per contracts/mcp-tools.yaml

**Checkpoint**: User can ask to see all, pending, or completed tasks and gets a correctly filtered list

---

## Phase 5: User Story 3 — Chat to Complete a Task (Priority: P2)

**Goal**: User says "Mark task 3 as complete" and the assistant toggles the task's completion status

**Independent Test**: Create a pending task, note its ID, send "Complete task {id}" in chat → verify task status changes to completed

### Implementation for User Story 3

- [x] T023 [US3] Implement todo_complete_task MCP tool (user_id, task_id params, asyncpg UPDATE toggle is_completed, return new status) in backend/app/mcp/server.py per contracts/mcp-tools.yaml

**Checkpoint**: User can mark tasks complete/incomplete via chat

---

## Phase 6: User Story 4 — Chat to Delete a Task (Priority: P2)

**Goal**: User says "Delete task 2" and the assistant removes the task after confirmation

**Independent Test**: Create a task, send "Delete task {id}" in chat → verify task is removed from the database

### Implementation for User Story 4

- [x] T024 [US4] Implement todo_delete_task MCP tool (user_id, task_id params, asyncpg DELETE with user isolation, return confirmation) in backend/app/mcp/server.py per contracts/mcp-tools.yaml

**Checkpoint**: User can delete tasks via chat

---

## Phase 7: User Story 5 — Chat to Update a Task (Priority: P2)

**Goal**: User says "Change task 1 to 'Call mom tonight'" and the assistant updates the task title

**Independent Test**: Create a task, send "Rename task {id} to 'New title'" in chat → verify task title is updated

### Implementation for User Story 5

- [x] T025 [US5] Implement todo_update_task MCP tool (user_id, task_id, optional title/description params, asyncpg UPDATE, return confirmation) in backend/app/mcp/server.py per contracts/mcp-tools.yaml

**Checkpoint**: User can update task titles and descriptions via chat

---

## Phase 8: User Story 6 — Multi-Step Chat Commands (Priority: P3)

**Goal**: User sends compound requests like "Delete task 3 and show me what's left" and the assistant chains both actions

**Independent Test**: Send "Add a task called Test and show all my tasks" → verify task is created AND full list (including new task) is returned in one response

### Implementation for User Story 6

- [x] T026 [US6] Enhance agent system prompt with multi-step chaining instructions (handle compound requests, execute actions sequentially, consolidate response) in backend/app/chat/agent.py

**Checkpoint**: User can issue compound commands and get consolidated responses with all actions executed

---

## Phase 9: User Story 7 — Persistent Conversation History (Priority: P3)

**Goal**: User can resume a previous conversation and the assistant has context from prior messages. Conversations survive server restarts.

**Independent Test**: Send a message, note the conversation ID, restart the server, send a follow-up in the same conversation → verify the assistant references prior context

### Implementation for User Story 7

- [x] T027 [US7] Update TodoChatKitServer.respond() to load last 20 messages via Store.load_thread_items() and convert with simple_to_agent_input() before running agent in backend/app/chat/server.py per research.md R6

**Checkpoint**: Conversations persist across server restarts and the assistant maintains context within a 20-message window

---

## Phase 10: User Story 8 — Start New Conversations (Priority: P3)

**Goal**: User can start a fresh conversation at any time, leaving previous conversations intact

**Independent Test**: Have an existing conversation, click "New Chat" → verify a new conversation ID is assigned and no prior context carries over

### Implementation for User Story 8

- [x] T028 [US8] Add new conversation support in chat-interface.tsx (new chat button, thread switching via ChatKit) in frontend/components/chat/chat-interface.tsx

**Checkpoint**: User can start new conversations and switch between them without cross-contamination

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and validation

- [x] T029 [P] Add graceful error handling for Gemini API failures, MCP subprocess errors, and DB connection issues in backend/app/chat/server.py
- [x] T030 [P] Add disambiguation logic to agent system prompt — when multiple tasks match a name query, list them with IDs and ask user to choose — in backend/app/chat/agent.py
- [x] T031 Run quickstart.md verification checklist end-to-end (all 8 checks)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — delivers MVP
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) — can run in parallel with US1 after foundation
- **US3–US5 (Phases 5–7)**: Depend on Foundational (Phase 2) — can run in parallel with each other
- **US6 (Phase 8)**: Depends on US1+US2 (needs multiple tools to chain)
- **US7 (Phase 9)**: Depends on US1 (needs working respond() to enhance)
- **US8 (Phase 10)**: Depends on US1 (needs working chat UI to extend)
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no story dependencies
- **US2 (P1)**: Can start after Phase 2 — independent of US1
- **US3 (P2)**: Can start after Phase 2 — independent of US1/US2
- **US4 (P2)**: Can start after Phase 2 — independent of US1/US2/US3
- **US5 (P2)**: Can start after Phase 2 — independent of other stories
- **US6 (P3)**: Requires US1+US2 tools to exist (needs multiple tools for chaining)
- **US7 (P3)**: Requires US1 respond() implementation to enhance with history loading
- **US8 (P3)**: Requires US1 chat UI to extend with new conversation button

### Within Each User Story

- MCP tools before ChatKit server integration
- Backend before frontend
- Core implementation before refinements

### Parallel Opportunities

- T002, T003, T004 can all run in parallel (Phase 1)
- T005, T007, T009, T010, T011, T012, T013 can all run in parallel (Phase 2)
- T018, T020, T021 can run in parallel within US1 (different frontend files)
- US2, US3, US4, US5 (T022–T025) are all independent MCP tool implementations in the same file — execute sequentially but each is self-contained
- T029 and T030 can run in parallel (Phase 11)

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch all independent foundational tasks together:
Task T005: "Create Conversation + Message models in backend/app/models/conversation.py"
Task T007: "Create RequestContext dataclass in backend/app/chat/context.py"
Task T009: "Create chat schemas in backend/app/schemas/chat.py"
Task T010: "Create MCP server skeleton in backend/app/mcp/server.py"
Task T011: "Create agent factory in backend/app/chat/agent.py"
Task T012: "Add ChatKit script tag to frontend/app/layout.tsx"
Task T013: "Create Next.js API proxy route in frontend/app/api/chatkit/route.ts"

# Then sequentially (depends on T005):
Task T006: "Create Alembic migration"

# Then (depends on T005, T007):
Task T008: "Implement PostgreSQL ChatKit Store"
```

## Parallel Example: User Story 1

```bash
# Backend first (sequential — each builds on previous):
Task T014: "Implement todo_create_task MCP tool"
Task T015: "Implement TodoChatKitServer.respond()"
Task T016: "Create POST /chatkit endpoint"
Task T017: "Update main.py with CORS + chat router"

# Frontend (parallel — different files):
Task T018: "Create chat-interface.tsx component"
Task T020: "Create chat utilities in lib/chat.ts"
Task T021: "Add chat nav link to dashboard"

# Then (depends on T018):
Task T019: "Create chat page"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (9 tasks)
3. Complete Phase 3: User Story 1 (8 tasks)
4. **STOP and VALIDATE**: Send "Add a task to buy groceries" in /chat → task created + confirmation streamed
5. Deploy/demo if ready — this is the minimum viable AI chatbot

### Incremental Delivery

1. Setup + Foundational → Foundation ready (13 tasks)
2. Add US1 → Test create task via chat → **MVP!** (21 tasks cumulative)
3. Add US2 → Test list/filter tasks via chat (22 tasks)
4. Add US3–US5 → Full CRUD via chat (25 tasks)
5. Add US6 → Multi-step commands work (26 tasks)
6. Add US7–US8 → Conversation persistence + new conversations (28 tasks)
7. Polish → Error handling, disambiguation, validation (31 tasks)

### Recommended Execution Order (Single Developer)

Phase 1 → Phase 2 → Phase 3 (MVP) → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10 → Phase 11

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- All MCP tools are in one file (backend/app/mcp/server.py) — implement sequentially per story
- ChatKit Store handles all persistence — US7 enhances respond() to load history, not Store
- Agent system prompt is the primary mechanism for multi-step (US6) and disambiguation (Polish)
- No changes to existing task CRUD (FR-013) — all new code is additive
