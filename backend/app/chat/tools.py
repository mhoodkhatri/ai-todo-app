"""In-process function tools for the todo agent (replaces MCP subprocess)."""

import os
import uuid
from datetime import datetime, timezone

import asyncpg
from agents import function_tool

_pool: asyncpg.Pool | None = None


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        database_url = os.environ["DATABASE_URL"]
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
    return _pool


@function_tool
async def todo_create_task(user_id: str, title: str, description: str = "") -> str:
    """Create a new task for the specified user.

    Args:
        user_id: The authenticated user's ID.
        title: The task title.
        description: Optional task description.
    """
    pool = await _get_pool()
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO task (id, user_id, title, description, is_completed, created_at, updated_at)
            VALUES ($1, $2, $3, $4, false, $5, $5)
            """,
            uuid.UUID(task_id),
            user_id,
            title,
            description,
            now,
        )
    return f"Created task '{title}' (id: {task_id})"


@function_tool
async def todo_list_tasks(user_id: str, status: str = "all") -> str:
    """List tasks for the specified user with optional filtering.

    Args:
        user_id: The authenticated user's ID.
        status: Filter — 'all', 'completed', or 'incomplete'.
    """
    pool = await _get_pool()
    async with pool.acquire() as conn:
        if status == "completed":
            rows = await conn.fetch(
                "SELECT id, title, is_completed FROM task WHERE user_id = $1 AND is_completed = true ORDER BY created_at DESC",
                user_id,
            )
        elif status == "incomplete":
            rows = await conn.fetch(
                "SELECT id, title, is_completed FROM task WHERE user_id = $1 AND is_completed = false ORDER BY created_at DESC",
                user_id,
            )
        else:
            rows = await conn.fetch(
                "SELECT id, title, is_completed FROM task WHERE user_id = $1 ORDER BY created_at DESC",
                user_id,
            )

    if not rows:
        return "No tasks found."

    import json
    tasks = []
    for row in rows:
        tasks.append({
            "id": str(row["id"]),
            "title": row["title"],
            "completed": bool(row["is_completed"]),
        })
    return json.dumps({"total": len(tasks), "tasks": tasks})


@function_tool
async def todo_complete_task(user_id: str, task_id: str) -> str:
    """Toggle a task's completion status (complete/incomplete).

    Args:
        user_id: The authenticated user's ID.
        task_id: The UUID of the task to toggle.
    """
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, title, is_completed FROM task WHERE id = $1 AND user_id = $2",
            uuid.UUID(task_id),
            user_id,
        )
        if not row:
            return f"Task not found (id: {task_id}). Make sure you're using the correct task ID."

        new_status = not row["is_completed"]
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await conn.execute(
            "UPDATE task SET is_completed = $1, updated_at = $2 WHERE id = $3 AND user_id = $4",
            new_status,
            now,
            uuid.UUID(task_id),
            user_id,
        )

    status_text = "completed" if new_status else "incomplete"
    return f"Task '{row['title']}' marked as {status_text}"


@function_tool
async def todo_delete_task(user_id: str, task_id: str) -> str:
    """Permanently delete a task. This action cannot be undone.

    Args:
        user_id: The authenticated user's ID.
        task_id: The UUID of the task to delete.
    """
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, title FROM task WHERE id = $1 AND user_id = $2",
            uuid.UUID(task_id),
            user_id,
        )
        if not row:
            return f"Task not found (id: {task_id}). Make sure you're using the correct task ID."

        await conn.execute(
            "DELETE FROM task WHERE id = $1 AND user_id = $2",
            uuid.UUID(task_id),
            user_id,
        )

    return f"Deleted task '{row['title']}'"


@function_tool
async def todo_update_task(
    user_id: str, task_id: str, title: str = "", description: str = ""
) -> str:
    """Update a task's title and/or description. You only need to provide the fields you want to change.

    Args:
        user_id: The authenticated user's ID.
        task_id: The UUID of the task to update.
        title: New title (send empty string to keep current).
        description: New description (send empty string to keep current).
    """
    if not title and not description:
        return "Please provide a new title or description to update."

    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, title, description FROM task WHERE id = $1 AND user_id = $2",
            uuid.UUID(task_id),
            user_id,
        )
        if not row:
            return f"Task not found (id: {task_id}). Make sure you're using the correct task ID."

        new_title = title if title else row["title"]
        new_desc = description if description else row["description"]
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await conn.execute(
            "UPDATE task SET title = $1, description = $2, updated_at = $3 WHERE id = $4 AND user_id = $5",
            new_title,
            new_desc,
            now,
            uuid.UUID(task_id),
            user_id,
        )

    changes = []
    if title:
        changes.append(f"title: '{new_title}'")
    if description:
        changes.append(f"description: '{new_desc}'")
    return f"Updated task '{row['title']}' -> {', '.join(changes)}"


ALL_TOOLS = [
    todo_create_task,
    todo_list_tasks,
    todo_complete_task,
    todo_delete_task,
    todo_update_task,
]
