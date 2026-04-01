"""FastMCP server exposing task CRUD tools via stdio transport.

Run as subprocess: uv run python -m app.mcp.server
The Agents SDK spawns this via MCPServerStdio.
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone

import asyncpg
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("todo_mcp")

_pool: asyncpg.Pool | None = None


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        database_url = os.environ["DATABASE_URL"]
        # Strip SQLAlchemy dialect prefix if present (asyncpg needs plain postgresql://)
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
    return _pool


@mcp.tool(name="todo_create_task")
async def todo_create_task(
    user_id: str, title: str, description: str | None = None
) -> str:
    """Create a new task for the specified user."""
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
            description or "",
            now,
        )
    return f"Created task '{title}' (id: {task_id})"


@mcp.tool(name="todo_list_tasks")
async def todo_list_tasks(user_id: str, status: str = "all") -> str:
    """List tasks for the specified user with optional filtering (all/completed/incomplete)."""
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

    lines = [f"Your tasks ({len(rows)} total):"]
    for i, row in enumerate(rows, 1):
        check = "x" if row["is_completed"] else " "
        lines.append(f"{i}. [{check}] {row['title']} (id: {row['id']})")
    return "\n".join(lines)


@mcp.tool(name="todo_complete_task")
async def todo_complete_task(user_id: str, task_id: str) -> str:
    """Toggle a task's completion status (complete/incomplete)."""
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


@mcp.tool(name="todo_delete_task")
async def todo_delete_task(user_id: str, task_id: str) -> str:
    """Permanently delete a task. This action cannot be undone."""
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


@mcp.tool(name="todo_update_task")
async def todo_update_task(
    user_id: str, task_id: str, title: str | None = None, description: str | None = None
) -> str:
    """Update a task's title and/or description."""
    if not title and description is None:
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
        new_desc = description if description is not None else row["description"]
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
    if description is not None:
        changes.append(f"description: '{new_desc}'")
    return f"Updated task '{row['title']}' -> {', '.join(changes)}"


async def _cleanup():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


if __name__ == "__main__":
    try:
        mcp.run()
    finally:
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.run_until_complete(_cleanup())
        except RuntimeError:
            pass
