---
id: 5
title: Implement AI Todo Chatbot
stage: green
date: 2026-03-29
surface: agent
model: claude-opus-4-6
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: developer
command: /sp.implement
labels: ["implementation", "chatbot", "mcp", "chatkit", "agents-sdk"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/pyproject.toml
  - backend/app/core/config.py
  - backend/app/chat/__init__.py
  - backend/app/chat/context.py
  - backend/app/chat/agent.py
  - backend/app/chat/store.py
  - backend/app/chat/server.py
  - backend/app/mcp/__init__.py
  - backend/app/mcp/server.py
  - backend/app/models/conversation.py
  - backend/app/schemas/chat.py
  - backend/app/api/chat.py
  - backend/app/main.py
  - backend/alembic/env.py
  - backend/alembic/versions/a1b2c3d4e5f6_create_chat_tables.py
  - frontend/package.json
  - frontend/app/layout.tsx
  - frontend/app/(protected)/dashboard/page.tsx
  - frontend/app/(protected)/chat/page.tsx
  - frontend/app/api/chatkit/route.ts
  - frontend/components/chat/chat-interface.tsx
  - frontend/lib/chat.ts
  - frontend/proxy.ts
tests:
  - Manual: quickstart.md verification checklist (8 checks)
---

## Prompt

/sp.implement

## Response snapshot

Implemented the full AI Todo Chatbot feature (31 tasks across 11 phases):

**Phase 1 (Setup)**: Added openai-agents, mcp[cli], openai-chatkit to backend; @openai/chatkit-react to frontend; GEMINI_API_KEY config; module directories.

**Phase 2 (Foundational)**: Created Conversation + Message SQLModel models, Alembic migration, RequestContext dataclass, PostgreSQL ChatKit Store (10 interface methods with user isolation), chat schemas, FastMCP server skeleton with asyncpg pool, agent factory (Gemini 2.5 Flash via OpenAIChatCompletionsModel), ChatKit script tag in layout, Next.js API proxy route.

**Phase 3 (MVP)**: Implemented todo_create_task MCP tool, TodoChatKitServer.respond() with history loading + streaming, POST /chatkit endpoint with JWT auth, CORS update, ChatKit wrapper component with auth fetch, protected chat page, chat utilities, dashboard nav link.

**Phases 4-7 (CRUD Tools)**: Implemented todo_list_tasks, todo_complete_task, todo_delete_task, todo_update_task MCP tools — all with user isolation via user_id parameter.

**Phases 8-10 (Advanced)**: Multi-step chaining instructions in system prompt, conversation history loading (last 20 messages), new conversation button with thread switching.

**Phase 11 (Polish)**: Error handling with logging for history loading and agent execution failures, disambiguation logic in agent system prompt.

## Outcome

- Impact: Full AI chatbot feature implemented — users can manage tasks via natural language chat
- Tests: Manual verification checklist in quickstart.md (8 checks)
- Files: 23 files created/modified (14 backend, 7 frontend, 2 config)
- Next prompts: Install dependencies (uv sync, npm install), run migration (alembic upgrade head), set GEMINI_API_KEY, test end-to-end
- Reflection: All 5 MCP tools implemented in single file for simplicity; ChatKit Store uses raw SQL via SQLAlchemy text() for direct control; agent system prompt handles multi-step and disambiguation

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation — code written to spec
- Graders run and results (PASS/FAIL): N/A — manual verification needed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run end-to-end test with actual Gemini API key
