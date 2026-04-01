"""PostgreSQL-backed ChatKit Store implementation.

Implements all ChatKit Store interface methods with user isolation.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Literal

from chatkit.server import Store
from chatkit.types import (
    ActiveStatus,
    ClosedStatus,
    Page,
    ThreadMetadata,
    UserMessageItem,
    UserMessageTextContent,
    InferenceOptions,
    AssistantMessageItem,
    AssistantMessageContent,
)

from app.chat.context import RequestContext
from app.core.database import engine


def _text(sql: str):
    from sqlalchemy import text
    return text(sql)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _status_to_str(status) -> str:
    """Convert ChatKit status object to DB string."""
    if isinstance(status, str):
        return status
    return getattr(status, "type", "active")


def _str_to_status(s: str):
    """Convert DB status string to ChatKit status object."""
    if s == "closed":
        return ClosedStatus()
    return ActiveStatus()


def _make_thread(row_id: str, title: str | None, status_str: str, created_at: datetime | None = None) -> ThreadMetadata:
    """Build a ThreadMetadata with proper status object and created_at."""
    return ThreadMetadata(
        id=row_id,
        title=title or "",
        status=_str_to_status(status_str),
        created_at=created_at or _now(),
    )


def _row_to_item(row) -> UserMessageItem | AssistantMessageItem:
    """Convert a DB row to a ChatKit thread item based on role."""
    role = row["role"]
    content = row["content"] or ""
    item_id = row["id"]
    thread_id = row["conversation_id"] if "conversation_id" in row.keys() else ""
    created_at = row["created_at"] if "created_at" in row.keys() else _now()

    if role == "user":
        return UserMessageItem(
            id=item_id,
            thread_id=thread_id,
            type="user_message",
            created_at=created_at,
            content=[UserMessageTextContent(type="input_text", text=content)],
            attachments=[],
            inference_options=InferenceOptions(),
        )
    else:
        return AssistantMessageItem(
            id=item_id,
            thread_id=thread_id,
            type="assistant_message",
            created_at=created_at,
            content=[AssistantMessageContent(type="output_text", text=content)],
        )


def _item_role(item) -> str:
    item_type = getattr(item, "type", "")
    if item_type == "user_message":
        return "user"
    return "assistant"


def _item_content(item) -> str:
    content = getattr(item, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            elif isinstance(part, str):
                parts.append(part)
            else:
                parts.append(str(getattr(part, "text", "")))
        return " ".join(parts)
    return str(content) if content else ""


class PostgresStore(Store[RequestContext]):
    """ChatKit Store backed by PostgreSQL (Neon) via SQLAlchemy async engine."""

    def generate_thread_id(self, context: RequestContext) -> str:
        return str(uuid.uuid4())

    def generate_item_id(
        self,
        item_type: Literal[
            "thread", "message", "tool_call", "task",
            "workflow", "attachment", "sdk_hidden_context",
        ],
        thread: ThreadMetadata,
        context: RequestContext,
    ) -> str:
        return str(uuid.uuid4())

    async def load_thread(
        self, thread_id: str, context: RequestContext
    ) -> ThreadMetadata:
        async with engine.connect() as conn:
            result = await conn.execute(
                _text(
                    "SELECT id, title, status, created_at "
                    "FROM conversation WHERE id = :id AND user_id = :uid"
                ),
                {"id": thread_id, "uid": context.user_id},
            )
            row = result.mappings().first()
            if not row:
                return _make_thread(thread_id, "", "active")
            return _make_thread(
                row["id"], row["title"], row["status"],
                created_at=row["created_at"],
            )

    async def save_thread(
        self, thread: ThreadMetadata, context: RequestContext
    ) -> None:
        now = _now()
        status_str = _status_to_str(thread.status)
        async with engine.begin() as conn:
            existing = await conn.execute(
                _text("SELECT id FROM conversation WHERE id = :id"),
                {"id": thread.id},
            )
            if existing.first():
                await conn.execute(
                    _text(
                        "UPDATE conversation SET title = :title, status = :status, "
                        "updated_at = :now WHERE id = :id AND user_id = :uid"
                    ),
                    {
                        "title": thread.title or "",
                        "status": status_str,
                        "now": now,
                        "id": thread.id,
                        "uid": context.user_id,
                    },
                )
            else:
                await conn.execute(
                    _text(
                        "INSERT INTO conversation (id, user_id, title, status, created_at, updated_at) "
                        "VALUES (:id, :uid, :title, :status, :now, :now)"
                    ),
                    {
                        "id": thread.id,
                        "uid": context.user_id,
                        "title": thread.title or "",
                        "status": status_str,
                        "now": now,
                    },
                )

    async def delete_thread(
        self, thread_id: str, context: RequestContext
    ) -> None:
        async with engine.begin() as conn:
            await conn.execute(
                _text("DELETE FROM message WHERE conversation_id = :tid AND user_id = :uid"),
                {"tid": thread_id, "uid": context.user_id},
            )
            await conn.execute(
                _text("DELETE FROM conversation WHERE id = :id AND user_id = :uid"),
                {"id": thread_id, "uid": context.user_id},
            )

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        async with engine.connect() as conn:
            params: dict = {"uid": context.user_id, "limit": limit}
            query = "SELECT id, title, status, created_at FROM conversation WHERE user_id = :uid"

            if after:
                query += " AND updated_at < (SELECT updated_at FROM conversation WHERE id = :after)"
                params["after"] = after

            query += " ORDER BY updated_at DESC LIMIT :limit"

            result = await conn.execute(_text(query), params)
            rows = result.mappings().all()
            threads = [
                _make_thread(row["id"], row["title"], row["status"], row["created_at"])
                for row in rows
            ]
            has_more = len(threads) == limit
            return Page(data=threads, has_more=has_more)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page:
        async with engine.connect() as conn:
            params: dict = {"tid": thread_id, "uid": context.user_id, "limit": limit}
            query = (
                "SELECT id, conversation_id, role, content, type, metadata, created_at "
                "FROM message WHERE conversation_id = :tid AND user_id = :uid"
            )

            if after:
                if order == "desc":
                    query += " AND created_at < (SELECT created_at FROM message WHERE id = :after)"
                else:
                    query += " AND created_at > (SELECT created_at FROM message WHERE id = :after)"
                params["after"] = after

            direction = "DESC" if order == "desc" else "ASC"
            query += f" ORDER BY created_at {direction} LIMIT :limit"

            result = await conn.execute(_text(query), params)
            rows = result.mappings().all()

            items = [_row_to_item(row) for row in rows]
            has_more = len(items) == limit
            return Page(data=items, has_more=has_more)

    async def load_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ):
        async with engine.connect() as conn:
            result = await conn.execute(
                _text(
                    "SELECT id, conversation_id, role, content, type, metadata, created_at "
                    "FROM message WHERE id = :id AND conversation_id = :tid AND user_id = :uid"
                ),
                {"id": item_id, "tid": thread_id, "uid": context.user_id},
            )
            row = result.mappings().first()
            if not row:
                return None
            return _row_to_item(row)

    async def add_thread_item(
        self, thread_id: str, item, context: RequestContext
    ) -> None:
        now = _now()
        role = _item_role(item)
        content = _item_content(item)
        item_type = getattr(item, "type", "message")
        meta = getattr(item, "metadata", None)

        async with engine.begin() as conn:
            await conn.execute(
                _text(
                    "INSERT INTO message (id, conversation_id, user_id, role, content, type, metadata, created_at) "
                    "VALUES (:id, :tid, :uid, :role, :content, :type, :meta, :now) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": item.id,
                    "tid": thread_id,
                    "uid": context.user_id,
                    "role": role,
                    "content": content,
                    "type": item_type,
                    "meta": json.dumps(meta) if meta else None,
                    "now": now,
                },
            )

    async def save_item(
        self, thread_id: str, item, context: RequestContext
    ) -> None:
        content = _item_content(item)
        meta = getattr(item, "metadata", None)
        async with engine.begin() as conn:
            await conn.execute(
                _text(
                    "UPDATE message SET content = :content, metadata = :meta "
                    "WHERE id = :id AND conversation_id = :tid AND user_id = :uid"
                ),
                {
                    "id": item.id,
                    "tid": thread_id,
                    "uid": context.user_id,
                    "content": content,
                    "meta": json.dumps(meta) if meta else None,
                },
            )

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        async with engine.begin() as conn:
            await conn.execute(
                _text(
                    "DELETE FROM message WHERE id = :id AND conversation_id = :tid AND user_id = :uid"
                ),
                {"id": item_id, "tid": thread_id, "uid": context.user_id},
            )

    async def load_attachment(self, attachment_id: str, context: RequestContext):
        return None

    async def save_attachment(self, attachment, context: RequestContext) -> None:
        pass

    async def delete_attachment(self, attachment_id: str, context: RequestContext) -> None:
        pass
