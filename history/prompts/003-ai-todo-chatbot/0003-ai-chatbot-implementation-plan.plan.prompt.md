---
id: "0003"
title: "AI Chatbot Implementation Plan"
stage: plan
date: 2026-03-29
surface: agent
model: claude-opus-4-6
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: developer
command: /sp.plan
labels: ["planning", "architecture", "chatbot", "mcp", "chatkit"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/plan.md
  - specs/003-ai-todo-chatbot/research.md
  - specs/003-ai-todo-chatbot/data-model.md
  - specs/003-ai-todo-chatbot/quickstart.md
  - specs/003-ai-todo-chatbot/contracts/chatkit-api.yaml
  - specs/003-ai-todo-chatbot/contracts/mcp-tools.yaml
  - CLAUDE.md
tests:
  - N/A (planning phase - no code or tests)
---

## Prompt

I've added multiple skills for you so you can implement the latest spec better

## Response snapshot

Executed /sp.plan for 003-ai-todo-chatbot feature. Generated 6 design artifacts:

1. **research.md** — 7 research decisions covering: Gemini custom model provider (R1), MCP stdio transport (R2), ChatKit Python backend (R3), ChatKit React frontend (R4), PostgreSQL Store (R5), streaming flow (R6), MCP auth via system prompt (R7).

2. **data-model.md** — Two new entities: `Conversation` (ChatKit thread) and `Message` (ChatKit thread item), both with SQLModel definitions, Alembic migration SQL, and ChatKit Store method mapping.

3. **contracts/chatkit-api.yaml** — ChatKit protocol endpoint contract (POST /chatkit) with SSE streaming for agent responses and JSON for CRUD operations.

4. **contracts/mcp-tools.yaml** — 5 MCP tools: todo_create_task, todo_list_tasks, todo_complete_task, todo_delete_task, todo_update_task with full input schemas and annotations.

5. **quickstart.md** — Setup guide with new dependencies, environment variables, file structure, architecture diagram, and verification checklist.

6. **plan.md** — Complete architectural plan with component diagram, request flow (17-step), agent system prompt, project structure, and key decisions table.

Skills leveraged: building-mcp-servers, scaffolding-openai-agents, streaming-llm-responses, building-chat-interfaces. All Constitution gates passed (pre-research and post-design).

## Outcome

- ✅ Impact: Full implementation plan ready for /sp.tasks generation
- 🧪 Tests: N/A (planning phase)
- 📁 Files: 6 artifacts created + CLAUDE.md updated with new tech stack
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, then /sp.implement
- 🧠 Reflection: Parallel research agents saved time but couldn't access web tools — direct skill loading + WebFetch was more effective

## Evaluation notes (flywheel)

- Failure modes observed: Subagents denied WebSearch/WebFetch/Bash — had to do research in main context
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Grant subagents web tool access for faster parallel research
