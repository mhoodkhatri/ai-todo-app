# Research: Task CRUD Operations (Part 2)

**Date**: 2026-03-25 | **Plan**: [plan.md](./plan.md)

## Research Summary

Part 2 builds on a fully established Part 1 foundation. All technology choices, authentication patterns, and database schemas are already implemented and working. This research phase focuses on confirming existing patterns and documenting decisions for the CRUD implementation layer.

---

## R1: Backend API Pattern — FastAPI Router for Task CRUD

**Question**: How should the 6 task endpoints be organized in the existing FastAPI backend?

**Decision**: Single router module at `backend/app/api/tasks.py` with `APIRouter(prefix="/tasks", tags=["tasks"])`, included in `main.py` under `/api`.

**Rationale**:
- Part 1 established the pattern with `api/health.py` + router inclusion in `main.py`
- All 6 endpoints operate on the same `Task` model — one file keeps them cohesive
- Prefix `/api/tasks` follows RESTful convention per Constitution V

**Alternatives considered**:
- Separate file per operation (e.g., `create_task.py`, `list_tasks.py`) — rejected, unnecessary granularity for 6 related endpoints
- Generic CRUD base class — rejected, over-engineering for a single entity

---

## R2: Request/Response Schemas — Pydantic via SQLModel

**Question**: How should request/response validation schemas be structured?

**Decision**: Separate `backend/app/schemas/task.py` with `TaskCreate`, `TaskUpdate`, and `TaskResponse` Pydantic models (not SQLModel table models).

**Rationale**:
- SQLModel table model (`Task`) is for DB; Pydantic models are for API boundary validation
- Part 1 established `schemas/common.py` pattern
- `TaskCreate` enforces title 1-200 chars (stripped, non-whitespace-only), description max 1000 chars
- `TaskUpdate` makes both fields optional (partial update)
- `TaskResponse` serializes UUID, timestamps, completion status

**Alternatives considered**:
- Reuse SQLModel `Task` directly for request/response — rejected, exposes internal fields (`user_id`) and doesn't enforce trimming/whitespace validation
- Separate create vs update files — rejected, too few schemas to warrant splitting

---

## R3: User Isolation Strategy

**Question**: How should user isolation be enforced on every CRUD operation?

**Decision**: Every database query includes `Task.user_id == current_user_id` in the WHERE clause. For single-resource endpoints (GET/PUT/PATCH/DELETE by ID), query by both `id` AND `user_id` — if no row found, return 404 (never 403).

**Rationale**:
- FR-013 mandates scoping to authenticated user
- FR-015 requires 404 (not 403) to prevent information leakage
- `get_current_user` dependency (Part 1) returns `user_id` from JWT `sub` claim
- Simple pattern: `select(Task).where(Task.id == task_id, Task.user_id == user_id)`

**Alternatives considered**:
- Global query filter / SQLAlchemy event listener — rejected, magic behavior that's harder to audit
- Check ownership separately and return 403 — rejected, violates FR-015

---

## R4: Frontend API Client Pattern

**Question**: How should the frontend call the backend API?

**Decision**: Create `frontend/lib/api.ts` module with typed functions wrapping `fetch()`. Each function gets the JWT from Better Auth client session and sets `Authorization: Bearer <token>` header. Backend base URL from `NEXT_PUBLIC_API_URL` env var (already set to `http://localhost:8000`).

**Rationale**:
- Native `fetch` is available in Next.js 16 client components — no additional HTTP library needed
- Better Auth client (`authClient`) provides session with JWT access token
- Typed return values from API functions match `TaskResponse` interface

**Alternatives considered**:
- Server Actions calling backend — rejected, adds unnecessary indirection; the backend is a separate FastAPI service
- Axios/ky library — rejected, Constitution V says use existing deps; `fetch` is built-in
- tRPC — rejected, backend is Python FastAPI, not TypeScript

---

## R5: Frontend Component Architecture

**Question**: How should task UI components be organized?

**Decision**: Client components under `frontend/components/tasks/` with 4 files:
- `task-list.tsx` — Fetches and renders task list, handles empty state (FR-020)
- `task-item.tsx` — Single task row with toggle, edit trigger, delete trigger
- `task-form.tsx` — Reusable create/edit form with Zod validation
- `delete-dialog.tsx` — Confirmation dialog before deletion (FR-011)

Dashboard page becomes a thin server component wrapper that renders `<TaskList />`.

**Rationale**:
- Task operations require client-side interactivity (forms, toggles, dialogs)
- Zod validation schemas in `lib/validations.ts` (extending Part 1 pattern)
- Each component has a single responsibility
- Part 1 established `components/auth/` pattern — `components/tasks/` mirrors it

**Alternatives considered**:
- Single monolithic dashboard component — rejected, too large and hard to maintain
- Server components with server actions — rejected, requires calling external FastAPI service which is better done client-side with JWT

---

## R6: Timestamp Management

**Question**: How should `created_at` and `updated_at` be managed?

**Decision**: `created_at` set by SQLModel default factory (already done in Part 1 model). `updated_at` explicitly set to `datetime.now(timezone.utc)` in the update/toggle endpoint handler before committing.

**Rationale**:
- SQLModel `default_factory` only runs on INSERT, not UPDATE
- No SQLAlchemy `onupdate` configured in the existing model — adding it would require a migration for no schema change
- Explicit `task.updated_at = datetime.now(timezone.utc)` is simple, visible, and testable

**Alternatives considered**:
- Database trigger for `updated_at` — rejected, adds DB-level complexity; hackathon scope
- SQLAlchemy `onupdate` parameter — would require model change but no schema migration; however explicit is clearer

---

## R7: Concurrency Strategy

**Question**: How to handle concurrent edits from multiple tabs?

**Decision**: Last write wins. No optimistic concurrency control, no ETags, no version columns.

**Rationale**:
- Spec explicitly states "last write wins" for Phase II (edge case section)
- Adding versioning would require a migration and additional logic — deferred to later phases

---

## R8: Delete Confirmation UX

**Question**: How to implement the delete confirmation dialog?

**Decision**: Client-side confirmation dialog rendered inline (not browser `window.confirm()`). A `DeleteDialog` component with "Cancel" and "Delete" buttons, triggered from the task item.

**Rationale**:
- FR-011 requires confirmation before permanent deletion
- Native `window.confirm()` is functional but doesn't match the app's styled UI
- A custom dialog component is consistent with the Tailwind-styled auth forms from Part 1
- No additional UI library needed — simple conditional render with backdrop

**Alternatives considered**:
- `window.confirm()` — rejected, inconsistent UX with the rest of the app
- shadcn/ui Dialog — rejected, not installed and adding a component library for one dialog is over-engineering
