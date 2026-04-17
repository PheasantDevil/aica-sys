"""merge three alembic heads (analytics + affiliate branches)

Revision ID: c7d9f2a1b4e0
Revises: 9e13f1c94b71, 2a3b4c5d6e7f, 8e2f13c5d7b8
Create Date: 2026-04-12

"""

from typing import Sequence, Union

revision: str = "c7d9f2a1b4e0"
down_revision: Union[str, Sequence[str], None] = (
    "9e13f1c94b71",
    "2a3b4c5d6e7f",
    "8e2f13c5d7b8",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge branches; schema changes live in parent revisions."""
    pass


def downgrade() -> None:
    """Split is not supported for merge revisions."""
    pass
