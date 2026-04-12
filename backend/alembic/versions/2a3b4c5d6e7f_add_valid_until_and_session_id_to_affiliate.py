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


def _index_names(inspector, table: str) -> set[str]:
    return {i["name"] for i in inspector.get_indexes(table)}


def upgrade() -> None:
    """Upgrade schema (idempotent for partially-applied DBs)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    ref_cols = {c["name"] for c in inspector.get_columns("referral_links")}
    if "valid_until" not in ref_cols:
        op.add_column(
            "referral_links",
            sa.Column("valid_until", sa.DateTime(), nullable=True),
        )
    inspector = sa.inspect(bind)
    idx_ref = op.f("ix_referral_links_valid_until")
    if idx_ref not in _index_names(inspector, "referral_links"):
        op.create_index(
            idx_ref,
            "referral_links",
            ["valid_until"],
            unique=False,
        )

    click_cols = {c["name"] for c in inspector.get_columns("click_tracking")}
    if "session_id" not in click_cols:
        op.add_column(
            "click_tracking",
            sa.Column("session_id", sa.String(), nullable=True),
        )
    inspector = sa.inspect(bind)
    idx_click = op.f("ix_click_tracking_session_id")
    if idx_click not in _index_names(inspector, "click_tracking"):
        op.create_index(
            idx_click,
            "click_tracking",
            ["session_id"],
            unique=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    idx_click = op.f("ix_click_tracking_session_id")
    if idx_click in _index_names(inspector, "click_tracking"):
        op.drop_index(idx_click, table_name="click_tracking")

    idx_ref = op.f("ix_referral_links_valid_until")
    if idx_ref in _index_names(inspector, "referral_links"):
        op.drop_index(idx_ref, table_name="referral_links")

    click_cols = {c["name"] for c in inspector.get_columns("click_tracking")}
    if "session_id" in click_cols:
        op.drop_column("click_tracking", "session_id")

    ref_cols = {c["name"] for c in inspector.get_columns("referral_links")}
    if "valid_until" in ref_cols:
        op.drop_column("referral_links", "valid_until")
