# Data Model: Console Todo Application (Phase I)

**Feature**: 001-console-todo-app | **Date**: 2026-03-24

## Entities

### Task

Represents a single to-do item in the system.

| Field | Type | Required | Default | Constraints | Notes |
|-------|------|----------|---------|-------------|-------|
| `id` | `int` | Yes (auto) | Auto-increment from 1 | Positive integer, unique, never reused | Assigned by TaskService, not user |
| `title` | `str` | Yes | — | 1–200 characters, stripped of leading/trailing whitespace | Empty or whitespace-only rejected |
| `description` | `str` | No | `""` (empty string) | Max 1000 characters | Optional on create and update |
| `completed` | `bool` | Yes (auto) | `False` | — | Toggled via dedicated operation |
| `created_at` | `datetime` | Yes (auto) | `datetime.now()` | — | Set once on creation, never modified |
| `updated_at` | `datetime` | Yes (auto) | `datetime.now()` | — | Updated on every modification (update, toggle) |

### Python Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

### Validation Rules

| Rule | Where Enforced | Error Message |
|------|---------------|---------------|
| Title is not empty/whitespace | UI layer (before service call) | "Title is required" |
| Title ≤ 200 characters | UI layer (before service call) | "Title must be 200 characters or less" |
| Description ≤ 1000 characters | UI layer (before service call) | "Description must be 1000 characters or less" |
| Task ID exists | Service layer | "Task with ID {id} not found" |
| Task ID is a valid integer | UI layer (input parsing) | "Please enter a valid number" |

## Collections

### TaskService (In-Memory Store)

| Attribute | Type | Purpose |
|-----------|------|---------|
| `_tasks` | `dict[int, Task]` | Maps task ID → Task object |
| `_next_id` | `int` | Auto-increment counter, starts at 1 |

### Operations

| Operation | Input | Output | Side Effects |
|-----------|-------|--------|-------------|
| `add_task(title, description)` | title: str, description: str | Task | Creates Task, increments `_next_id`, adds to `_tasks` |
| `get_all_tasks()` | — | list[Task] | None |
| `get_task(task_id)` | task_id: int | Task \| None | None |
| `update_task(task_id, title, description)` | task_id: int, title: str \| None, description: str \| None | Task \| None | Updates fields if non-None/non-empty, sets `updated_at` |
| `delete_task(task_id)` | task_id: int | bool | Removes from `_tasks` if exists |
| `toggle_task(task_id)` | task_id: int | Task \| None | Flips `completed`, sets `updated_at` |
| `get_summary()` | — | tuple[int, int] | None — returns (total, completed) counts |

## State Transitions

```
Task Lifecycle:
  Created (incomplete) → Toggled (complete) → Toggled (incomplete) → ...
                       → Updated (fields changed)
                       → Deleted (removed from store)
```

The only state that transitions is `completed` (via toggle). All other modifications are field updates.

## Phase II Migration Notes

- `Task` dataclass → `SQLModel` model with `table=True`
- `id` → database primary key with auto-increment
- `_tasks` dict → PostgreSQL table via Neon
- `TaskService` → FastAPI dependency with database session
- Add `user_id` foreign key for multi-user support
- Timestamps → timezone-aware with `datetime.now(UTC)`
