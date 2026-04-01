# Feature Specification: AI Todo Chatbot

**Feature Branch**: `003-ai-todo-chatbot`
**Created**: 2026-03-29
**Status**: Draft
**Input**: User description: "Transform the existing Phase II Todo web app into an AI-powered chatbot that manages todos through natural language, using MCP (Model Context Protocol) server architecture."

## Clarifications

### Session 2026-03-29

- Q: Should the backend use MCP (Model Context Protocol) server architecture or direct AI tool-calling? → A: MCP server architecture — Backend exposes task CRUD as MCP tools; AI client connects via MCP protocol.
- Q: Should AI responses stream token-by-token or be delivered as a complete message? → A: Streaming via OpenAI ChatKit's default streaming behavior — tokens stream to the UI in real-time.
- Q: When multiple tasks match a name query, what should the assistant do? → A: Disambiguate — list matching tasks and ask the user to choose by ID.
- Q: Which model provider approach for OpenAI Agents SDK? → A: OpenAI Agents SDK with Gemini 2.5 Flash via its OpenAI-compatible endpoint (custom model provider).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat to Add a Task (Priority: P1)

An authenticated user opens the chat interface and types a natural language message like "Add a task to buy groceries" or "I need to remember to pay bills." The AI assistant interprets the intent, creates the task in the user's task list, and confirms the action with a friendly response.

**Why this priority**: This is the core value proposition — managing tasks through conversation. Without the ability to create tasks via chat, the feature has no purpose.

**Independent Test**: Can be fully tested by sending a chat message with an intent to create a task, then verifying the task appears in the user's task list and the assistant confirms the action.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the chat page, **When** they type "Add a task to buy groceries", **Then** a new task titled "Buy groceries" is created for that user and the assistant responds confirming the creation with the task title.
2. **Given** an authenticated user on the chat page, **When** they type "I need to remember to pay bills", **Then** a new task titled "Pay bills" is created and the assistant confirms it.
3. **Given** an authenticated user on the chat page, **When** they type "Add a task to call mom with the description remind her about Sunday dinner", **Then** a task is created with the title "Call mom" and description "Remind her about Sunday dinner", and the assistant confirms.

---

### User Story 2 - Chat to View Tasks (Priority: P1)

An authenticated user asks the chatbot to show their tasks. They can ask for all tasks, only pending tasks, or only completed tasks. The assistant retrieves the appropriate list and displays it in a readable format.

**Why this priority**: Viewing tasks is essential for the chatbot to be useful — users need to see what they have before they can manage it. Co-equal with P1 because add + view form the minimum viable chat experience.

**Independent Test**: Can be tested by having a user with existing tasks send messages like "Show me all my tasks" or "What's pending?" and verifying the correct filtered list is returned.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 5 tasks (3 pending, 2 completed), **When** they type "Show me all my tasks", **Then** the assistant lists all 5 tasks with their completion status.
2. **Given** an authenticated user with tasks, **When** they type "What's pending?", **Then** only pending (incomplete) tasks are shown.
3. **Given** an authenticated user with tasks, **When** they type "What have I completed?", **Then** only completed tasks are shown.
4. **Given** an authenticated user with no tasks, **When** they type "Show my tasks", **Then** the assistant responds indicating the task list is empty.

---

### User Story 3 - Chat to Complete a Task (Priority: P2)

An authenticated user tells the chatbot they've finished a task. They can reference a task by its ID number. The assistant marks the task as complete and confirms.

**Why this priority**: Completing tasks is the natural next step after adding and viewing. It closes the core task lifecycle loop.

**Independent Test**: Can be tested by creating a task, then sending a message like "Mark task 3 as complete" and verifying the task's status changes to completed.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a pending task (ID 3), **When** they type "Mark task 3 as complete", **Then** the task is marked completed and the assistant confirms with the task title.
2. **Given** an authenticated user referencing a non-existent task ID, **When** they type "Complete task 999", **Then** the assistant responds gracefully indicating the task was not found.

---

### User Story 4 - Chat to Delete a Task (Priority: P2)

An authenticated user asks the chatbot to remove a task. They can reference a task by ID or by name. When referenced by name, the assistant first looks up the task then deletes it.

**Why this priority**: Deletion is important for task hygiene but slightly less critical than completion for MVP.

**Independent Test**: Can be tested by creating a task, sending "Delete task 2" and verifying the task is removed from the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task (ID 2), **When** they type "Delete task 2", **Then** the task is permanently removed and the assistant confirms.
2. **Given** an authenticated user with a task titled "Team meeting", **When** they type "Delete the meeting task", **Then** the assistant identifies the matching task and deletes it, confirming the action.
3. **Given** an authenticated user referencing a non-existent task, **When** they type "Delete task 999", **Then** the assistant responds gracefully indicating the task was not found.

---

### User Story 5 - Chat to Update a Task (Priority: P2)

An authenticated user asks the chatbot to change a task's title or description. The assistant updates the specified fields and confirms.

**Why this priority**: Updating is important for correcting mistakes and refining tasks but is less frequently used than add/view/complete.

**Independent Test**: Can be tested by creating a task, sending "Change task 1 to 'Call mom tonight'" and verifying the task title is updated.

**Acceptance Scenarios**:

1. **Given** an authenticated user with task ID 1 titled "Call mom", **When** they type "Change task 1 to 'Call mom tonight'", **Then** the task title is updated to "Call mom tonight" and the assistant confirms.
2. **Given** an authenticated user referencing a non-existent task, **When** they type "Update task 999 to 'New title'", **Then** the assistant responds gracefully indicating the task was not found.

---

### User Story 6 - Multi-Step Chat Commands (Priority: P3)

An authenticated user issues a compound request in a single message, such as "Delete task 3 and show me what's left." The assistant chains the appropriate actions sequentially — first deleting the task, then listing remaining tasks — and provides a consolidated response.

**Why this priority**: Multi-step commands enhance the conversational experience but are an advanced capability beyond the core single-action flows.

**Independent Test**: Can be tested by sending "Delete task 3 and show me what's left" and verifying the task is deleted AND the remaining tasks are listed in the response.

**Acceptance Scenarios**:

1. **Given** an authenticated user with tasks including ID 3, **When** they type "Delete task 3 and show me what's left", **Then** task 3 is deleted and the remaining tasks are listed in the same response.
2. **Given** an authenticated user, **When** they type "Add a task to buy milk and show all my tasks", **Then** the task is created and the full task list (including the new task) is displayed.

---

### User Story 7 - Persistent Conversation History (Priority: P3)

An authenticated user can continue a previous conversation. When returning to an existing conversation, the chatbot has context of prior messages and can reference earlier interactions. Conversations survive server restarts.

**Why this priority**: Conversation persistence provides a better user experience but the core task management works without it (each message can stand alone).

**Independent Test**: Can be tested by sending a message in a conversation, noting the conversation ID, then sending a follow-up message with the same conversation ID and verifying the assistant has context from the first message.

**Acceptance Scenarios**:

1. **Given** an authenticated user starts a new conversation, **When** they send their first message, **Then** a new conversation is created and the conversation ID is returned.
2. **Given** an existing conversation with history, **When** the user sends a follow-up message using the same conversation ID, **Then** the assistant has context of prior messages in that conversation.
3. **Given** a server restart occurs, **When** a user resumes a previous conversation by ID, **Then** the full conversation history is preserved and available.

---

### User Story 8 - Start New Conversations (Priority: P3)

An authenticated user can start a fresh conversation at any time, leaving previous conversations intact. The chat interface supports creating new conversation sessions.

**Why this priority**: Supports clean separation of conversation contexts, but not critical for core functionality.

**Independent Test**: Can be tested by starting a new conversation, verifying a new conversation ID is assigned and no prior conversation history carries over.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an existing conversation, **When** they choose to start a new conversation, **Then** a new conversation ID is assigned and the chat starts fresh with no prior context.

---

### Edge Cases

- What happens when the user sends an empty message or gibberish? The assistant should respond helpfully, asking the user to clarify their intent.
- What happens when the user references a task ID that belongs to another user? The system must enforce user isolation — users can only manage their own tasks.
- What happens when the user sends a very long message? The system should handle it gracefully within reasonable limits.
- What happens when the AI service is temporarily unavailable? The system should return a clear error message indicating the service is temporarily down, not expose internal errors.
- What happens when the database is unreachable during a chat request? The system should return a meaningful error rather than crashing.
- What happens when two users chat simultaneously? Each user's conversation and task operations must be fully isolated.
- What happens when a user references a task by name and multiple tasks match? The assistant MUST list all matching tasks with their IDs and ask the user to choose, rather than acting on an ambiguous match.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to create tasks through natural language chat messages.
- **FR-002**: System MUST allow authenticated users to list their tasks (all, pending, or completed) through natural language chat messages.
- **FR-003**: System MUST allow authenticated users to mark tasks as complete through natural language chat messages.
- **FR-004**: System MUST allow authenticated users to delete tasks through natural language chat messages.
- **FR-005**: System MUST allow authenticated users to update task titles and descriptions through natural language chat messages.
- **FR-006**: System MUST support chaining multiple task operations in a single chat message.
- **FR-007**: System MUST persist all conversation messages (both user and assistant) to the database.
- **FR-008**: System MUST support resuming previous conversations with full history context.
- **FR-009**: System MUST support starting new conversations at any time.
- **FR-010**: System MUST enforce user isolation — users can only access and manage their own tasks and conversations.
- **FR-011**: System MUST require authentication for all chat interactions, using the same authentication mechanism as the existing application.
- **FR-012**: System MUST provide the chat interface as a new page/route accessible to authenticated users.
- **FR-013**: System MUST NOT break any existing task management functionality (REST API, web UI).
- **FR-014**: System MUST be stateless at the server level — all conversation state must be persisted to the database, and the server must hold no in-memory state between requests.
- **FR-015**: System MUST confirm every task action with a friendly, human-readable response.
- **FR-016**: System MUST handle errors gracefully (task not found, invalid requests, service unavailable) with user-friendly messages.
- **FR-017**: System MUST interpret natural language intent to determine the correct task operation (e.g., "I need to remember to pay bills" maps to creating a task).
- **FR-018**: System MUST expose task operations (create, list, complete, delete, update) as MCP (Model Context Protocol) tools via an MCP server.
- **FR-019**: System MUST use an MCP client to connect the AI model to the MCP server, enabling the AI to invoke task tools through the MCP protocol.
- **FR-020**: System MUST stream AI assistant responses token-by-token to the frontend using OpenAI ChatKit's streaming capabilities.
- **FR-021**: When a task is referenced by name and multiple tasks match, the system MUST present the matching tasks with their IDs and ask the user to disambiguate before acting.

### Key Entities

- **Conversation**: Represents a chat session belonging to a user. Contains a unique identifier, the owning user, and timestamps. Has many Messages.
- **Message**: Represents a single message within a conversation. Contains the sender role (user or assistant), the message content, a reference to the parent conversation, the owning user, and a timestamp.
- **Task** (existing): Represents a to-do item. Already exists with title, description, completed status, and user ownership. Unchanged by this feature.

## Assumptions

- The existing authentication system (Better Auth + JWT) is working and will be reused as-is for protecting the chat endpoint.
- The existing Task model and its database table will not be modified — new tables will be added alongside it.
- Users interact with the chatbot via text input only (no voice, no file uploads).
- The AI assistant responds in English only.
- The AI model used is Google Gemini 2.5 Flash (free-tier) accessed via its OpenAI-compatible endpoint. The OpenAI Agents SDK connects to Gemini through a custom model provider configuration, satisfying both the constitution's SDK requirement and the free-tier cost constraint.
- Conversation history is unbounded per conversation (no message count limit). If performance becomes a concern, a sliding window can be introduced later.
- The existing REST API endpoints and web UI for task management will continue to function alongside the new chat interface.
- The backend implements an MCP server that exposes task CRUD operations as MCP tools. An MCP client mediates between the AI model and the MCP server, allowing the AI to discover and invoke tools via the MCP protocol.
- AI assistant responses are streamed token-by-token to the frontend via OpenAI ChatKit's native streaming support, providing real-time feedback to users.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully create, list, complete, delete, and update tasks through natural language chat with at least 90% accuracy on the specified example interactions.
- **SC-002**: Users can complete a basic task management workflow (add a task, view it, mark it complete) in under 30 seconds of total chat interaction time.
- **SC-003**: Conversation history is fully preserved across server restarts — 100% of messages in a conversation are retrievable after restart.
- **SC-004**: All chat interactions enforce user isolation — 0% cross-user data leakage in task operations and conversation history.
- **SC-005**: The existing REST API and web UI continue to function identically — 0 regressions in existing functionality.
- **SC-006**: The chat endpoint responds to user messages within 10 seconds under normal conditions (excluding AI processing latency spikes).
- **SC-007**: 95% of single-intent natural language messages (from the specified interaction examples) are correctly interpreted and routed to the appropriate task operation.
