---
id: "0004"
title: "Plan Part 1 Foundation Database Auth"
stage: plan
date: 2026-03-25
surface: agent
model: claude-opus-4-6
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app
user: developer
command: /sp.plan
labels: ["planning", "authentication", "database", "monorepo", "better-auth", "fastapi", "nextjs"]
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
  - specs/002-fullstack-todo-app/contracts/auth-flow.md
  - specs/002-fullstack-todo-app/contracts/backend-api.yaml
tests:
  - None (planning phase — no code produced)
---

## Prompt

let's start Part 1 but first read the \specs\002-fullstack-todo-app/spec then start
/sp.plan for Part 1 (Foundation, database & Authentication) from specs/002-fullstack-todo-app/phase-breakdown.md

## Response snapshot

Generated the complete implementation plan for Part 1 (Foundation, Database & Authentication) of the Full-Stack Todo App. Created 6 artifacts:

1. **plan.md** — Main implementation plan covering monorepo structure (Next.js 16+ frontend + FastAPI backend), Neon PostgreSQL database, Better Auth JWT authentication flow, 5 implementation phases (A–E), acceptance criteria, and validation rules.

2. **research.md** — Consolidated research on Better Auth JWT plugin, JWKS-based JWT verification in FastAPI, asyncpg + NullPool for Neon, Next.js 16 breaking changes (proxy.ts, async params), UV project setup, and token management.

3. **data-model.md** — Entity definitions for Better Auth tables (user, session, account, verification) and application table (task with UUID PK, user_id, title, description, is_completed, timestamps). No FK between systems — app-layer enforcement.

4. **contracts/auth-flow.md** — Authentication flow architecture diagram, all Better Auth endpoints (signup, signin, signout, session, token, JWKS), FastAPI JWT verification contract, and proxy.ts route protection rules.

5. **contracts/backend-api.yaml** — OpenAPI 3.1 spec for FastAPI backend: health check (Part 1) plus task CRUD endpoint stubs (Part 2) with schemas, security, and error responses.

6. **quickstart.md** — Setup guide for Neon database, backend (UV + Alembic), frontend (npm + Better Auth CLI), environment variables, and verification steps.

Key architectural decisions: (1) JWKS-based JWT verification instead of shared secret, (2) no SQLModel User model — Task references Better Auth user ID directly, (3) asyncpg + NullPool for serverless Neon, (4) Next.js 16 proxy.ts for route protection.

## Outcome

- ✅ Impact: Complete Part 1 implementation plan ready for `/sp.tasks`
- 🧪 Tests: N/A — planning phase
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, contracts/auth-flow.md, contracts/backend-api.yaml)
- 🔁 Next prompts: `/sp.tasks` to break plan into testable tasks, then `/sp.implement`
- 🧠 Reflection: Research agents ran in parallel effectively. Key insight: Better Auth uses asymmetric JWT (EdDSA + JWKS) not shared-secret HMAC — this refines the constitution's "shared secret" wording.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS (all 7 gates)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify Better Auth JWT plugin HS256 support during implementation
