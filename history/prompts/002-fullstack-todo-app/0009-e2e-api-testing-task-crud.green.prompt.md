---
id: "0009"
title: E2E API Testing Task CRUD
stage: green
date: 2026-03-26
surface: agent
model: claude-opus-4-6
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app-part-2
user: mhoodkhatri
command: /sp.implement
labels: ["testing", "e2e", "api", "crud", "bug-fix", "part-2"]
links:
  spec: specs/002-fullstack-todo-app/part-2/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models/task.py
  - backend/app/api/tasks.py
tests:
  - "CRUD: 11 tests — create (title only, title+desc), list (sorted), get, update, toggle on/off, delete, verify-delete-404, list-after-delete"
  - "Edge cases: 10 tests — empty title, whitespace title, 201-char title, 200-char title, 1001-char desc, 1000-char desc, no auth, invalid token, non-existent ID, clear title on update"
  - "User isolation: 7 tests — empty list for user 2, cross-user GET/UPDATE/TOGGLE/DELETE all return 404, user 2 creates own task, each user sees only own tasks"
---

## Prompt

test yourself again by signup, signin, CRUD operations and edge cases

## Response snapshot

Ran 28 live API tests against running backend (port 8000) and frontend (port 3000):

1. **Sign-up and sign-in**: Created test user via Better Auth, obtained EdDSA JWT via `/api/auth/token` endpoint. Both work correctly.

2. **CRUD operations (11 tests)**: All pass — create (201), list sorted newest-first (200), get single (200), update title+desc (200), toggle complete/incomplete (200), delete (204), deleted task returns 404, list count decrements correctly.

3. **Edge cases (10 tests)**: All pass — empty title (422), whitespace-only title (422), 201-char title (422), 200-char title (201), 1001-char desc (422), 1000-char desc (201), no auth (401), invalid token (401), non-existent UUID (404), clear title during update (422).

4. **User isolation (7 tests)**: All pass — second user sees empty list, cross-user GET/UPDATE/TOGGLE/DELETE all return 404 (not 403, per FR-015), each user's CRUD is fully isolated.

**Bug found and fixed**: `asyncpg.DataError` on INSERT — Task model used `datetime.now(timezone.utc)` producing tz-aware datetimes, but the DB column is `TIMESTAMP WITHOUT TIME ZONE`. Fixed by adding `.replace(tzinfo=None)` in `models/task.py` (default_factory) and `api/tasks.py` (update_at assignments).

## Outcome

- ✅ Impact: 28/28 tests pass; 1 runtime bug discovered and fixed
- 🧪 Tests: 11 CRUD + 10 edge cases + 7 isolation = 28 total, all PASS
- 📁 Files: backend/app/models/task.py, backend/app/api/tasks.py (datetime fix)
- 🔁 Next prompts: Commit all changes including the bug fix, create PR
- 🧠 Reflection: Static code review (T020 initial pass) missed the datetime/DB type mismatch — live API testing caught a real production bug

## Evaluation notes (flywheel)

- Failure modes observed: datetime timezone mismatch between Python model and PostgreSQL column type — not detectable via import checks or type checking alone
- Graders run and results (PASS/FAIL): TypeScript tsc PASS, Backend imports PASS, 28 API tests PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add a startup self-test or use sa.DateTime(timezone=True) with a proper migration to prevent tz mismatch class of bugs
