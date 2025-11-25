"""create analytics tables if missing

Revision ID: 8e2f13c5d7b8
Revises: 7f1ab3c4d5e6
Create Date: 2025-11-25 12:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e2f13c5d7b8"
down_revision: Union[str, Sequence[str], None] = "7f1ab3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "analytics_events"):
        op.create_table(
            "analytics_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("event_type", sa.String(), index=True),
            sa.Column("user_id", sa.String(), index=True, nullable=True),
            sa.Column("session_id", sa.String(), index=True, nullable=True),
            sa.Column("properties", sa.JSON(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "metric_snapshots"):
        op.create_table(
            "metric_snapshots",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("metric_name", sa.String(), index=True),
            sa.Column("metric_value", sa.Float(), nullable=False),
            sa.Column("dimensions", sa.JSON(), nullable=True),
            sa.Column(
                "timestamp",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "reports"):
        op.create_table(
            "reports",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("report_type", sa.String(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("parameters", sa.JSON(), nullable=True),
            sa.Column("data", sa.JSON(), nullable=True),
            sa.Column("format", sa.String(), nullable=False, server_default="json"),
            sa.Column("file_url", sa.String(), nullable=True),
            sa.Column("created_by", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "scheduled_reports"):
        op.create_table(
            "scheduled_reports",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("report_type", sa.String(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("frequency", sa.String(), nullable=False),
            sa.Column("recipients", sa.JSON(), nullable=True),
            sa.Column("parameters", sa.JSON(), nullable=True),
            sa.Column("next_run", sa.DateTime(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "dashboards"):
        op.create_table(
            "dashboards",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("layout", sa.JSON(), nullable=True),
            sa.Column("filters", sa.JSON(), nullable=True),
            sa.Column("created_by", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "user_segments"):
        op.create_table(
            "user_segments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("conditions", sa.JSON(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table in [
        "user_segments",
        "dashboards",
        "scheduled_reports",
        "reports",
        "metric_snapshots",
        "analytics_events",
    ]:
        if _has_table(inspector, table):
            op.drop_table(table)

