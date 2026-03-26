# Data Model: Task CRUD Operations (Part 2)

**Date**: 2026-03-25 | **Plan**: [plan.md](./plan.md)

## Entities

### Task (existing — created in Part 1)

The `task` table already exists via Alembic migration `4d90e771f885`. **No schema changes required for Part 2.**

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK, auto-generated (`uuid4`) | Unique task identifier |
| `user_id` | String | NOT NULL, indexed | References Better Auth user ID; used for isolation |
| `title` | VARCHAR(200) | NOT NULL | 1–200 chars, whitespace-only rejected at API layer |
| `description` | VARCHAR(1000) | NULLABLE | Optional, max 1000 chars |
| `is_completed` | BOOLEAN | NOT NULL, default `false` | Toggle target |
| `created_at` | DATETIME (UTC) | NOT NULL, auto-set on create | Immutable after creation |
| `updated_at` | DATETIME (UTC) | NOT NULL, auto-set on create | Explicitly updated on PUT/PATCH |

**SQLModel definition**: `backend/app/models/task.py` (no changes needed)

### User (managed by Better Auth — out of Part 2 scope)

Better Auth manages the `user` table. The `task.user_id` column stores the Better Auth user ID (string). There is no foreign key constraint — the relationship is enforced at the application layer via JWT verification.

## Request/Response Schemas (new — Part 2)

### TaskCreate (request body for POST)

| Field | Type | Validation | Notes |
|-------|------|-----------|-------|
| `title` | string | Required, trimmed, 1–200 chars, non-whitespace-only | FR-005, FR-006 |
| `description` | string \| null | Optional, max 1000 chars | FR-005 |

### TaskUpdate (request body for PUT)

| Field | Type | Validation | Notes |
|-------|------|-----------|-------|
| `title` | string | Required, trimmed, 1–200 chars, non-whitespace-only | FR-009, FR-006 |
| `description` | string \| null | Optional, max 1000 chars | FR-009 |

### TaskResponse (response body)

| Field | Type | Notes |
|-------|------|-------|
| `id` | string (UUID) | Serialized as string for JSON |
| `title` | string | |
| `description` | string \| null | |
| `is_completed` | boolean | |
| `created_at` | string (ISO 8601) | UTC timestamp |
| `updated_at` | string (ISO 8601) | UTC timestamp |

**Note**: `user_id` is intentionally excluded from `TaskResponse` — the client already knows the user from the session.

## Validation Rules

### Backend (Pydantic validators)

| Rule | Field | Error Message |
|------|-------|---------------|
| Non-empty after trim | `title` | "Title is required" |
| Max 200 chars | `title` | "Title must be 200 characters or less" |
| Non-whitespace-only | `title` | "Title is required" |
| Max 1000 chars | `description` | "Description must be 1,000 characters or less" |

### Frontend (Zod schemas — `lib/validations.ts`)

| Schema | Fields | Mirrors |
|--------|--------|---------|
| `taskCreateSchema` | `title` (trim, 1-200), `description` (optional, max 1000) | Backend `TaskCreate` |
| `taskUpdateSchema` | Same as `taskCreateSchema` | Backend `TaskUpdate` |

## State Transitions

### Task Completion

```
[incomplete] --(toggle)--> [complete]
[complete]   --(toggle)--> [incomplete]
```

- Default state on creation: `incomplete` (`is_completed = false`)
- Toggle via `PATCH /api/tasks/{id}/toggle` — flips `is_completed` boolean
- `updated_at` is refreshed on every toggle

### Task Lifecycle

```
[create] --> [active] --> [update]*  --> [delete]
                     \--> [toggle]*  -/
```

- Creation: `POST /api/tasks` → task enters active state
- Update: `PUT /api/tasks/{id}` → title/description changed, `updated_at` refreshed
- Toggle: `PATCH /api/tasks/{id}/toggle` → completion flipped, `updated_at` refreshed
- Delete: `DELETE /api/tasks/{id}` → permanent removal, no soft delete

## Relationships

```
User (Better Auth) 1──────* Task
     └── user_id (string)      └── user_id (string, indexed)
```

- One user owns zero or more tasks
- No foreign key constraint (Better Auth manages users separately)
- Isolation enforced by filtering `WHERE user_id = <authenticated_user_id>` on every query

## Sort Order

- Task list: `ORDER BY created_at DESC` (newest first, FR-021)
- Not user-configurable
