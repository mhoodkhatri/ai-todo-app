---
id: 0010
title: Plan Part 3 Filtering Responsive Polish
stage: plan
date: 2026-03-28
surface: agent
model: claude-opus-4-6
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app-part-3
user: mhoodkhatri
command: /sp.plan
labels: ["planning", "filtering", "responsive", "polish", "part-3"]
links:
  spec: specs/002-fullstack-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-todo-app/plan.md
  - specs/002-fullstack-todo-app/research.md
  - specs/002-fullstack-todo-app/data-model.md
  - specs/002-fullstack-todo-app/quickstart.md
  - specs/002-fullstack-todo-app/contracts/filter-query.md
tests:
  - none (planning phase — no code changes)
---

## Prompt

for Part 3 (Filtering, Responsive UI & Polish) from specs/002-fullstack-todo-app/phase-breakdown.md
first read the spec.md which located at the root, the path of it is \ai-todo-app\specs\002-fullstack-todo-app\specs.md

## Response snapshot

Generated complete implementation plan for Part 3 of 002-fullstack-todo-app. Created 5 artifacts:

1. **plan.md** — Implementation plan covering filter API polish, responsive design (320px–1024px+), session expiry UX (401 interception), database error resilience, and performance verification. Five design decisions documented (D1–D5): hybrid client/server filtering, mobile-first Tailwind breakpoints, centralized 401 interception, differentiated error messaging, and measure-first performance strategy.

2. **research.md** — Four research items resolved: session expiry detection via Better Auth JWT, Tailwind CSS 4 responsive best practices, Next.js 16 performance optimization approach, and network vs API error differentiation.

3. **data-model.md** — Documents no schema changes; references existing Task model and the optional `status` query filter on GET /api/tasks.

4. **contracts/filter-query.md** — API contract for the new optional `status` query parameter on GET /api/tasks (non-breaking addition).

5. **quickstart.md** — Dev setup guide for Part 3 with testing checklists for responsive, filter, session expiry, error resilience, and performance.

Key finding: filter UI and client-side filtering already implemented in Part 2. Part 3 is primarily responsive polish, error UX, and end-to-end verification.

## Outcome

- ✅ Impact: Complete planning artifacts for Part 3 — ready for `/sp.tasks` to generate testable tasks
- 🧪 Tests: N/A (planning phase)
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, contracts/filter-query.md)
- 🔁 Next prompts: `/sp.tasks` to break plan into testable implementation tasks
- 🧠 Reflection: Part 3 is lighter than Parts 1–2 since core functionality exists. Main risk is responsive testing across breakpoints requiring manual verification.

## Evaluation notes (flywheel)

- Failure modes observed: spec.md path was specified as `specs.md` (plural) — corrected to `spec.md` (singular)
- Graders run and results (PASS/FAIL): Constitution check PASS (pre-design and post-design)
- Prompt variant (if applicable): standard /sp.plan with phase-breakdown scoping
- Next experiment (smallest change to try): none — standard workflow
