# Data Model: AI Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Date**: 2026-03-29

## Existing Entities (No Changes)

### Task (existing — `backend/app/models/task.py`)
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | |
| user_id | str | NOT NULL, indexed | Links to Better Auth user |
| title | str | max 200 chars | |
| description | str? | max 1000 chars, nullable | |
| is_completed | bool | default False | |
| created_at | datetime | UTC, auto-generated | |
| updated_at | datetime | UTC, auto-generated | |

---

## New Entities

### Conversation (ChatKit Thread)

Maps to ChatKit's `ThreadMetadata`. Stores conversation sessions per user.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | str | PK, generated (nanoid/uuid) | ChatKit thread ID |
| user_id | str | NOT NULL, indexed | FK → Better Auth user |
| title | str? | max 200 chars, nullable | Auto-generated after first message |
| status | str | default "active" | "active" or "archived" |
| created_at | datetime | UTC, auto-generated | |
| updated_at | datetime | UTC, auto-generated | |

**Indexes**:
- `ix_conversation_user_id` on `user_id`
- `ix_conversation_user_id_updated_at` on `(user_id, updated_at DESC)` for listing

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: str = Field(primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

---

### Message (ChatKit Thread Item)

Maps to ChatKit's `ThreadItem`. Stores individual messages (user, assistant, tool calls).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | str | PK, generated (nanoid/uuid) | ChatKit item ID |
| conversation_id | str | NOT NULL, FK → conversation.id, indexed | |
| user_id | str | NOT NULL | Denormalized for user isolation queries |
| role | str | NOT NULL | "user", "assistant", or "tool" |
| content | text | NOT NULL | Message text content |
| type | str | NOT NULL, default "message" | ChatKit item type discriminator |
| metadata | jsonb | nullable | Tool call info, model info, etc. |
| created_at | datetime | UTC, auto-generated | |

**Indexes**:
- `ix_message_conversation_id` on `conversation_id`
- `ix_message_conversation_id_created_at` on `(conversation_id, created_at)` for ordering

**SQLModel Definition**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: str = Field(primary_key=True)
    conversation_id: str = Field(
        foreign_key="conversation.id",
        nullable=False,
        index=True,
    )
    user_id: str = Field(nullable=False)
    role: str = Field(nullable=False)  # "user" | "assistant" | "tool"
    content: str = Field(nullable=False)
    type: str = Field(default="message")
    metadata: Optional[dict] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

---

## Entity Relationships

```
User (Better Auth)
 ├── 1:N → Task (existing)
 └── 1:N → Conversation (new)
              └── 1:N → Message (new)
```

- One user has many conversations
- One conversation has many messages
- User isolation enforced at query level (all queries filter by `user_id`)
- No direct FK to Better Auth `user` table (same pattern as existing `Task`)

---

## State Transitions

### Conversation Status
```
[new] → "active" → "archived"
                  ↑
                  └── (can be unarchived)
```

### Message (no state transitions — immutable once created)

---

## Alembic Migration Plan

**Migration**: `create_conversation_and_message_tables`

```sql
-- Up
CREATE TABLE conversation (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR(200),
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE INDEX ix_conversation_user_id ON conversation(user_id);
CREATE INDEX ix_conversation_user_id_updated_at ON conversation(user_id, updated_at DESC);

CREATE TABLE message (
    id VARCHAR PRIMARY KEY,
    conversation_id VARCHAR NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR NOT NULL DEFAULT 'message',
    metadata JSONB,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX ix_message_conversation_id ON message(conversation_id);
CREATE INDEX ix_message_conversation_id_created_at ON message(conversation_id, created_at);

-- Down
DROP TABLE message;
DROP TABLE conversation;
```

---

## ChatKit Store ↔ Data Model Mapping

| ChatKit Store Method | Table | Operation |
|---------------------|-------|-----------|
| `load_thread(id)` | `conversation` | SELECT by id + user_id |
| `save_thread(thread)` | `conversation` | INSERT or UPDATE |
| `delete_thread(id)` | `conversation` | DELETE (cascades to messages) |
| `load_threads()` | `conversation` | SELECT by user_id ORDER BY updated_at DESC |
| `load_thread_items(thread_id)` | `message` | SELECT by conversation_id, paginated |
| `add_thread_item(thread_id, item)` | `message` | INSERT |
| `save_item(thread_id, item)` | `message` | UPDATE |
| `delete_thread_item(thread_id, item_id)` | `message` | DELETE |
| `generate_thread_id()` | — | Generate UUID |
| `generate_item_id()` | — | Generate UUID |

---

## Validation Rules

### Conversation
- `id`: Non-empty string
- `user_id`: Non-empty string (from JWT)
- `title`: max 200 chars (optional, auto-generated)
- `status`: Must be "active" or "archived"

### Message
- `id`: Non-empty string
- `conversation_id`: Must reference existing conversation
- `role`: Must be "user", "assistant", or "tool"
- `content`: Non-empty string
- `type`: Default "message"
