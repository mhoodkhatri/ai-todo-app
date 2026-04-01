# Implementation Plan: AI Todo Chatbot

**Branch**: `003-ai-todo-chatbot` | **Date**: 2026-03-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-ai-todo-chatbot/spec.md`

## Summary

Add an AI-powered chatbot to the existing fullstack todo app. Users interact with a chat UI (OpenAI ChatKit) to manage tasks via natural language (e.g., "create a task called Buy groceries"). The backend uses OpenAI Agents SDK with Gemini 2.5 Flash as the LLM, connecting to an MCP server that exposes task CRUD as tools. Conversations persist in PostgreSQL. Responses stream token-by-token.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK (`openai-agents`), MCP SDK (`mcp`), ChatKit SDK (`openai-chatkit` + `@openai/chatkit-react`)
**Storage**: Neon Serverless PostgreSQL (existing DB — add `conversation` + `message` tables)
**Testing**: pytest (backend), manual verification (frontend)
**Target Platform**: Web application (Windows dev, cloud deploy)
**Project Type**: Web (monorepo — `frontend/` + `backend/`)
**Performance Goals**: Chat response <10s end-to-end (SC-006), 90% NL intent accuracy (SC-001)
**Constraints**: Stateless server (FR-014), user isolation (FR-010), free-tier Gemini model only
**Scale/Scope**: Single-user dev/demo, unbounded conversation history with 20-message context window per request

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Pre-Research | Post-Design | Notes |
|------|-------------|-------------|-------|
| I. Spec-Driven | PASS | PASS | spec.md exists, plan follows SDD workflow |
| II. AI-First | PASS | PASS | OpenAI Agents SDK + MCP SDK per constitution |
| III. Phase III (AI Chatbot) | PASS | PASS | Basic Level features targeted |
| IV. Cloud-Native | PASS | PASS | Stateless server, DB-persisted state |
| V. Clean Code | PASS | PASS | JWT auth reused, env vars, modular design |
| VI. Monorepo | PASS | PASS | Extends existing frontend/ + backend/ |
| VII. Tech Stack | PASS | PASS | ChatKit, Agents SDK, MCP SDK — all per constitution |

No violations. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-todo-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0: Technology research (7 decisions)
├── data-model.md        # Phase 1: Conversation + Message models
├── quickstart.md        # Phase 1: Setup and verification guide
├── contracts/
│   ├── chatkit-api.yaml # ChatKit endpoint contract
│   └── mcp-tools.yaml   # MCP tool definitions (5 tools)
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                    # Add CORS for ChatKit, mount /chatkit
│   ├── core/
│   │   ├── config.py              # Add GEMINI_API_KEY setting
│   │   ├── database.py            # (no changes)
│   │   └── security.py            # (no changes — reuse JWT auth)
│   ├── models/
│   │   ├── task.py                # (no changes)
│   │   └── conversation.py        # NEW: Conversation + Message SQLModel
│   ├── schemas/
│   │   ├── task.py                # (no changes)
│   │   └── chat.py                # NEW: Chat request/response schemas
│   ├── api/
│   │   ├── tasks.py               # (no changes)
│   │   └── chat.py                # NEW: POST /chatkit endpoint
│   ├── chat/
│   │   ├── __init__.py            # NEW
│   │   ├── server.py              # NEW: TodoChatKitServer (respond + agent)
│   │   ├── store.py               # NEW: PostgreSQL Store implementation
│   │   ├── context.py             # NEW: RequestContext dataclass
│   │   └── agent.py               # NEW: Agent factory (Gemini model setup)
│   └── mcp/
│       ├── __init__.py            # NEW
│       └── server.py              # NEW: FastMCP server (5 task tools)
├── alembic/
│   └── versions/
│       └── xxxx_create_chat_tables.py  # NEW: conversation + message migration
└── pyproject.toml                 # Add: openai-agents, mcp, openai-chatkit

frontend/
├── app/
│   ├── layout.tsx                 # Add ChatKit script tag (beforeInteractive)
│   ├── (protected)/
│   │   ├── layout.tsx             # (no changes)
│   │   ├── dashboard/page.tsx     # Add navigation link to /chat
│   │   └── chat/
│   │       └── page.tsx           # NEW: Chat page
│   └── api/
│       └── chatkit/
│           └── route.ts           # NEW: httpOnly cookie → Bearer proxy
├── components/
│   ├── tasks/                     # (no changes)
│   └── chat/
│       └── chat-interface.tsx     # NEW: ChatKit wrapper with auth
├── lib/
│   ├── api.ts                     # (no changes)
│   └── chat.ts                    # NEW: Chat utilities
└── package.json                   # Add: @openai/chatkit-react
```

**Structure Decision**: Extends the existing monorepo. Backend gets two new modules (`chat/` for ChatKit server, `mcp/` for MCP tools). Frontend adds a `/chat` route with ChatKit component. All new code is additive — zero changes to existing task CRUD.

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Browser                                                                  │
│  ┌──────────────┐                                                        │
│  │ ChatKit React │─── useChatKit({ api: { url, fetch } }) ──────────┐   │
│  │ Component     │                                                    │   │
│  └──────────────┘                                                    ▼   │
│                                                              ┌────────────┐
│                                                              │ Next.js    │
│                                                              │ API Proxy  │
│                                                              │ /api/chatkit│
│                                                              └─────┬──────┘
│                                                                    │
└─────────────────────────────────────────────────────────────────────┼──────┘
                                                                     │
                                                          Bearer JWT │ SSE
                                                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ FastAPI Backend (:8000)                                                  │
│                                                                          │
│  POST /chatkit ─────────────────────────────────────────────┐           │
│                                                              ▼           │
│  ┌──────────────────────┐    ┌───────────────────────────────────┐      │
│  │ ChatKitServer        │    │ PostgreSQL Store                   │      │
│  │ ├── respond()        │───>│ ├── load_thread_items()           │      │
│  │ │   ├── load history │    │ ├── add_thread_item()             │      │
│  │ │   ├── create Agent │    │ ├── save_thread()                 │      │
│  │ │   └── stream resp  │    │ └── ... (ChatKit Store interface) │      │
│  │ └────────────────────┘    └───────────────────────────────────┘      │
│           │                                    │                         │
│           ▼                                    ▼                         │
│  ┌──────────────────┐              ┌──────────────────────┐             │
│  │ OpenAI Agents SDK│              │ Neon PostgreSQL       │             │
│  │ Agent(Gemini 2.5)│              │ ├── task (existing)   │             │
│  │ Runner.run_stream│              │ ├── conversation (new)│             │
│  └────────┬─────────┘              │ └── message (new)     │             │
│           │ MCP stdio              └──────────────────────┘             │
│           ▼                                    ▲                         │
│  ┌──────────────────┐                          │                         │
│  │ FastMCP Server   │──── asyncpg ─────────────┘                         │
│  │ (subprocess)     │                                                    │
│  │ ├── create_task  │                                                    │
│  │ ├── list_tasks   │                                                    │
│  │ ├── complete_task│                                                    │
│  │ ├── delete_task  │                                                    │
│  │ └── update_task  │                                                    │
│  └──────────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Rationale | See |
|----------|--------|-----------|-----|
| LLM Provider | Gemini 2.5 Flash via OpenAI-compatible endpoint | Free tier, spec requirement | [research.md#R1](research.md) |
| MCP Transport | stdio (MCPServerStdio) | Simplest for same-machine, clean process boundary | [research.md#R2](research.md) |
| Chat Backend | ChatKit Python SDK (ChatKitServer) | Handles SSE, persistence hooks, agent integration | [research.md#R3](research.md) |
| Chat Frontend | @openai/chatkit-react (useChatKit) | Pre-built UI, streaming, thread management | [research.md#R4](research.md) |
| Persistence | Custom Store → PostgreSQL (Neon) | Reuses existing DB, ChatKit Store interface | [research.md#R5](research.md) |
| Auth Proxy | Next.js API route (/api/chatkit) | httpOnly cookies can't be read by JS | [research.md#R4](research.md) |
| MCP Auth | user_id as tool parameter via system prompt | MCP stdio doesn't forward HTTP headers | [research.md#R7](research.md) |

### Request Flow (Send Message)

1. User types message in ChatKit React component
2. `useChatKit` POSTs to Next.js proxy `/api/chatkit`
3. Proxy reads Better Auth session cookie, adds `Authorization: Bearer <jwt>`
4. Proxy forwards to FastAPI `POST /chatkit`
5. FastAPI extracts `user_id` from JWT (reuses existing `security.py`)
6. `ChatKitServer.process()` routes to `respond()`
7. `respond()` loads last 20 messages via `Store.load_thread_items()`
8. `simple_to_agent_input()` converts to Agent SDK format
9. Agent created with Gemini model + MCP server (stdio subprocess)
10. `Runner.run_streamed()` sends message + history to Gemini
11. Gemini decides to call MCP tools (e.g., `todo_create_task`)
12. Agent SDK routes tool call → MCP client → MCP server subprocess
13. MCP server executes DB query → returns text result
14. Gemini generates final response incorporating tool results
15. `stream_agent_response()` converts to ChatKit SSE events
16. SSE streamed back through proxy to ChatKit React
17. ChatKit auto-persists completed items via Store hooks

### Agent System Prompt

```
You are a helpful todo assistant. You manage tasks for the authenticated user.

## Capabilities
- Create new tasks (todo_create_task)
- List tasks with optional filtering (todo_list_tasks)
- Mark tasks complete/incomplete (todo_complete_task)
- Update task title or description (todo_update_task)
- Delete tasks (todo_delete_task)

## Authentication Context
- User ID: {user_id}
CRITICAL: When calling ANY tool, you MUST include user_id="{user_id}".
Never use a different user_id.

## Behavior Rules
- Be concise and friendly
- When the user asks to see tasks, always call todo_list_tasks first
- Confirm destructive actions (delete) before executing
- If a request is ambiguous, ask for clarification
- For non-task-related questions, politely redirect to task management
```

## Complexity Tracking

No constitution violations — no complexity justifications needed.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gemini OpenAI-compatible endpoint instability | Agent fails to respond | Wrap agent calls in try/except, return friendly error |
| MCP subprocess startup latency | First message slow (~2-5s) | Cache MCP server connection, pre-warm on startup |
| ChatKit web component CDN unavailable | Chat UI doesn't render | Add loading state detection, show fallback UI |

## Follow-ups

1. **Phase IV (future)**: Add chat widgets for interactive task cards (building-chat-widgets skill)
2. **Phase IV (future)**: Add conversation search and export
3. **Performance**: Consider MCP server connection pooling if subprocess overhead is significant
