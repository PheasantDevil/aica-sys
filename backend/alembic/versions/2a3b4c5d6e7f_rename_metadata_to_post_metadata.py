"""rename metadata to post_metadata

Revision ID: 2a3b4c5d6e7f
Revises: 1cf2ab5a8998
Create Date: 2025-11-20 02:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a3b4c5d6e7f"
down_revision: Union[str, Sequence[str], None] = "1cf2ab5a8998"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if metadata column exists before renaming
    # This handles the case where the table was created with the old column name
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("social_post_logs")]

    if "metadata" in columns and "post_metadata" not in columns:
        op.alter_column(
            "social_post_logs",
            "metadata",
            new_column_name="post_metadata",
            existing_type=sa.JSON(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Rename back to metadata for rollback
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("social_post_logs")]

    if "post_metadata" in columns and "metadata" not in columns:
        op.alter_column(
            "social_post_logs",
            "post_metadata",
            new_column_name="metadata",
            existing_type=sa.JSON(),
            existing_nullable=True,
        )
