# API Contract: Task List Filter Query Parameter

**Date**: 2026-03-28 | **Affects**: `GET /api/tasks`

## Change Type

Non-breaking addition — new optional query parameter on existing endpoint.

## Endpoint

```
GET /api/tasks?status={status}
```

### Query Parameters

| Parameter | Type | Required | Default | Values |
|-----------|------|----------|---------|--------|
| `status` | string | No | `"all"` | `"all"`, `"completed"`, `"incomplete"` |

### Behavior

| `status` value | Filter applied |
|----------------|---------------|
| `"all"` (or omitted) | No filter — return all user's tasks |
| `"completed"` | `is_completed = true` |
| `"incomplete"` | `is_completed = false` |

### Response

Unchanged — returns `TaskResponse[]` as defined in Part 2.

```json
[
  {
    "id": "uuid-string",
    "title": "Task title",
    "description": "Optional description",
    "is_completed": true,
    "created_at": "2026-03-28T12:00:00",
    "updated_at": "2026-03-28T12:00:00"
  }
]
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Valid request (including empty result) | `[]` or `[TaskResponse, ...]` |
| 401 | Missing/invalid/expired JWT | `{"detail": "Invalid or expired token"}` |
| 422 | Invalid `status` value | `{"detail": [{"msg": "..."}]}` |

### Notes

- This parameter is optional and additive — existing clients that don't pass `status` see no behavior change
- Client-side filtering remains the primary mechanism; this parameter exists for API completeness and future pagination support
- Sorting remains fixed: `created_at DESC` regardless of filter
