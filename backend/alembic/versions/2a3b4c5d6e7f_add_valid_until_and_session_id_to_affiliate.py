"""add valid_until and session_id to affiliate

Revision ID: 9e13f1c94b71
Revises: 1cf2ab5a8998
Create Date: 2025-11-19 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e13f1c94b71"
down_revision: Union[str, Sequence[str], None] = "1cf2ab5a8998"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add valid_until to referral_links table
    op.add_column(
        "referral_links",
        sa.Column("valid_until", sa.DateTime(), nullable=True),
    )
    op.create_index(
        op.f("ix_referral_links_valid_until"),
        "referral_links",
        ["valid_until"],
        unique=False,
    )

    # Add session_id to click_tracking table
    op.add_column(
        "click_tracking",
        sa.Column("session_id", sa.String(), nullable=True),
    )
    op.create_index(
        op.f("ix_click_tracking_session_id"),
        "click_tracking",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove indexes
    op.drop_index(op.f("ix_click_tracking_session_id"), table_name="click_tracking")
    op.drop_index(op.f("ix_referral_links_valid_until"), table_name="referral_links")

    # Remove columns
    op.drop_column("click_tracking", "session_id")
    op.drop_column("referral_links", "valid_until")
