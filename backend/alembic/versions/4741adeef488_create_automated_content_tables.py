"""Create automated content and trend tables

Revision ID: 4741adeef488
Revises: 223a0ac841bb
Create Date: 2025-11-20 09:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4741adeef488"
down_revision: Union[str, Sequence[str], None] = "223a0ac841bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create automated content related tables."""
    op.create_table(
        "automated_contents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("slug", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_metadata", sa.JSON(), nullable=True),
        sa.Column("seo_data", sa.JSON(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "ix_automated_contents_content_type", "automated_contents", ["content_type"]
    )
    op.create_index("ix_automated_contents_created_at", "automated_contents", ["created_at"])

    op.create_table(
        "trend_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trend_name", sa.String(length=200), nullable=False),
        sa.Column("trend_score", sa.Float(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("related_topics", sa.JSON(), nullable=True),
        sa.Column("data_snapshot", sa.JSON(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trend_data_trend_name", "trend_data", ["trend_name"])
    op.create_index("ix_trend_data_detected_at", "trend_data", ["detected_at"])

    op.create_table(
        "source_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("source_metadata", sa.JSON(), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_data_source_type", "source_data", ["source_type"])
    op.create_index("ix_source_data_collected_at", "source_data", ["collected_at"])

    op.create_table(
        "content_generation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=True),
        sa.Column("generation_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("api_cost", sa.Float(), nullable=True, server_default="0"),
        sa.Column("generation_time", sa.Float(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_content_generation_logs_generation_type",
        "content_generation_logs",
        ["generation_type"],
    )
    op.create_index("ix_content_generation_logs_created_at", "content_generation_logs", ["created_at"])


def downgrade() -> None:
    """Drop automated content related tables."""
    op.drop_index("ix_content_generation_logs_created_at", table_name="content_generation_logs")
    op.drop_index(
        "ix_content_generation_logs_generation_type",
        table_name="content_generation_logs",
    )
    op.drop_table("content_generation_logs")

    op.drop_index("ix_source_data_collected_at", table_name="source_data")
    op.drop_index("ix_source_data_source_type", table_name="source_data")
    op.drop_table("source_data")

    op.drop_index("ix_trend_data_detected_at", table_name="trend_data")
    op.drop_index("ix_trend_data_trend_name", table_name="trend_data")
    op.drop_table("trend_data")

    op.drop_index("ix_automated_contents_created_at", table_name="automated_contents")
    op.drop_index(
        "ix_automated_contents_content_type", table_name="automated_contents"
    )
    op.drop_table("automated_contents")

