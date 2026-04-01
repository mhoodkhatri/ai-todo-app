"""create conversation and message tables

Revision ID: a1b2c3d4e5f6
Revises: 4d90e771f885
Create Date: 2026-03-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "4d90e771f885"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversation",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("status", sa.String(), server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_conversation_user_id", "conversation", ["user_id"])
    op.create_index(
        "ix_conversation_user_id_updated_at",
        "conversation",
        ["user_id", sa.text("updated_at DESC")],
    )

    op.create_table(
        "message",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(),
            sa.ForeignKey("conversation.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("type", sa.String(), nullable=False, server_default="message"),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_message_conversation_id", "message", ["conversation_id"])
    op.create_index(
        "ix_message_conversation_id_created_at",
        "message",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("message")
    op.drop_table("conversation")
