# Data Model: Task Filtering, Responsive UI & Polish (Part 3)

**Branch**: `002-fullstack-todo-app-part-3` | **Date**: 2026-03-28

## Schema Changes

**None.** Part 3 introduces no new database tables, columns, or migrations.

All data model entities (User, Task) were established in Parts 1–2 and remain unchanged.

## Existing Entities (Reference)

### Task (established in Part 2)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | |
| user_id | str | Indexed, NOT NULL | From JWT `sub` claim |
| title | str | 1–200 chars, NOT NULL | Whitespace-only rejected |
| description | str \| None | Max 1,000 chars | Optional |
| is_completed | bool | Default: false | Toggle target for filter |
| created_at | datetime | UTC, auto-set | Sort key (DESC) |
| updated_at | datetime | UTC, auto-updated | |

**Filter-relevant field**: `is_completed` — used for status filtering (all / completed / incomplete).

### User (managed by Better Auth — established in Part 1)

Better Auth manages the user table directly. The backend references users only via the JWT `sub` claim (user_id string).

## Query Changes

### GET /api/tasks — Optional `status` Filter

The existing query:
```sql
SELECT * FROM task WHERE user_id = :uid ORDER BY created_at DESC
```

With optional `status` parameter:
```sql
-- status = "completed"
SELECT * FROM task WHERE user_id = :uid AND is_completed = true ORDER BY created_at DESC

-- status = "incomplete"
SELECT * FROM task WHERE user_id = :uid AND is_completed = false ORDER BY created_at DESC

-- status = "all" or omitted
SELECT * FROM task WHERE user_id = :uid ORDER BY created_at DESC
```

**No index changes needed** — the existing `user_id` index covers these queries. The `is_completed` boolean filter on a per-user dataset is efficient without a composite index given the expected data volume (no pagination = manageable per-user task counts).
