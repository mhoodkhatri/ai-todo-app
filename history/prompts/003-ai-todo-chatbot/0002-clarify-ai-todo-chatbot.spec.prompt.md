---
id: "0002"
title: Clarify AI Todo Chatbot Spec
stage: spec
date: 2026-03-29
surface: agent
model: claude-opus-4-6
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: mhoodkhatri
command: /sp.clarify
labels: ["clarification", "spec", "mcp", "streaming", "agents-sdk"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/spec.md
tests:
  - null
---

## Prompt

/sp.clarify

## Response snapshot

Ran structured ambiguity & coverage scan across 10 taxonomy categories on the AI Todo Chatbot spec. Asked 5 clarification questions (4 answered, 1 skipped):

1. **MCP Architecture** → Option A: MCP server architecture — backend exposes task CRUD as MCP tools; AI client connects via MCP protocol.
2. **Streaming** → Option A: Streaming via OpenAI ChatKit's default streaming behavior — tokens stream to UI in real-time.
3. **Urdu/Voice scope** → Skipped/deferred — not in scope for Phase III.
4. **Task name disambiguation** → Option B: List matching tasks with IDs and ask user to choose.
5. **Model provider** → Option A: OpenAI Agents SDK with Gemini 2.5 Flash via OpenAI-compatible endpoint (custom model provider).

Integrated all answers into spec: added Clarifications section, FR-018 through FR-021, updated Edge Cases and Assumptions. Constitution cross-referenced to validate tech stack alignment (OpenAI ChatKit, Agents SDK, MCP SDK).

## Outcome

- ✅ Impact: 4 critical ambiguities resolved; spec ready for /sp.plan
- 🧪 Tests: N/A (spec clarification, no code changes)
- 📁 Files: specs/003-ai-todo-chatbot/spec.md updated (Clarifications, FRs, Edge Cases, Assumptions)
- 🔁 Next prompts: /sp.plan to generate implementation plan
- 🧠 Reflection: Constitution review was essential — revealed prescribed tech stack (ChatKit, Agents SDK, MCP SDK) that shaped all questions. Skipping Urdu/voice was pragmatic for Phase III scope.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
