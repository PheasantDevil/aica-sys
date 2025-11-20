"""add social post log table

Revision ID: 1cf2ab5a8998
Revises: 223a0ac841bb
Create Date: 2025-11-19 19:20:39.170947

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1cf2ab5a8998"
down_revision: Union[str, Sequence[str], None] = "223a0ac841bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "social_post_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "platform", sa.String(length=50), nullable=False, server_default="twitter"
        ),
        sa.Column("post_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("hashtags", sa.JSON(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("tweet_id", sa.String(length=100), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("tweet_text", sa.Text(), nullable=True),
        sa.Column("tweet_metrics", sa.JSON(), nullable=True),
        sa.Column(
            "post_metadata", sa.JSON(), nullable=True
        ),  # 'metadata'は予約語のため'post_metadata'に変更
        sa.Column(
            "posted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("metrics_updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_social_post_logs_platform", "social_post_logs", ["platform"])
    op.create_index("ix_social_post_logs_post_type", "social_post_logs", ["post_type"])
    op.create_index("ix_social_post_logs_tweet_id", "social_post_logs", ["tweet_id"])
    op.create_index("ix_social_post_logs_status", "social_post_logs", ["status"])
    op.create_index("ix_social_post_logs_posted_at", "social_post_logs", ["posted_at"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_social_post_logs_posted_at", table_name="social_post_logs")
    op.drop_index("ix_social_post_logs_status", table_name="social_post_logs")
    op.drop_index("ix_social_post_logs_tweet_id", table_name="social_post_logs")
    op.drop_index("ix_social_post_logs_post_type", table_name="social_post_logs")
    op.drop_index("ix_social_post_logs_platform", table_name="social_post_logs")
    op.drop_table("social_post_logs")
