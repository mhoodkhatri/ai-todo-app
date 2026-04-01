from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"
    __table_args__ = (
        Index("ix_conversation_user_id_updated_at", "user_id", "updated_at"),
    )

    id: str = Field(primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    status: str = Field(default="active")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )


class Message(SQLModel, table=True):
    __tablename__ = "message"
    __table_args__ = (
        Index("ix_message_conversation_id_created_at", "conversation_id", "created_at"),
    )

    id: str = Field(primary_key=True)
    conversation_id: str = Field(
        foreign_key="conversation.id",
        nullable=False,
        index=True,
    )
    user_id: str = Field(nullable=False)
    role: str = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    type: str = Field(default="message", nullable=False)
    metadata_: Optional[dict] = Field(default=None, sa_column=Column("metadata", JSONB))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
