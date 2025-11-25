"""add configuration column to commission rules

Revision ID: 6d4f9e2c0e1a
Revises: 2a3b4c5d6e7f
Create Date: 2025-11-20 12:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6d4f9e2c0e1a"
down_revision: Union[str, Sequence[str], None] = "2a3b4c5d6e7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("commission_rules"):
        op.create_table(
            "commission_rules",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("tier", sa.String(), nullable=False),
            sa.Column("reward_type", sa.String(), nullable=False),
            sa.Column("fixed_amount", sa.Float(), nullable=True),
            sa.Column("percentage", sa.Float(), nullable=True),
            sa.Column("min_threshold", sa.Float(), nullable=True),
            sa.Column("configuration", sa.JSON(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )
    else:
        columns = [col["name"] for col in inspector.get_columns("commission_rules")]
        if "configuration" not in columns:
            op.add_column(
                "commission_rules",
                sa.Column("configuration", sa.JSON(), nullable=True),
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("commission_rules"):
        columns = [col["name"] for col in inspector.get_columns("commission_rules")]
        if "configuration" in columns and len(columns) > 1:
            op.drop_column("commission_rules", "configuration")
        elif len(columns) == 1 and "configuration" in columns:
            op.drop_table("commission_rules")

