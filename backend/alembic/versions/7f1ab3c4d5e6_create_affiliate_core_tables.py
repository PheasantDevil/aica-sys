"""create affiliate core tables

Revision ID: 7f1ab3c4d5e6
Revises: 6d4f9e2c0e1a
Create Date: 2025-11-25 12:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f1ab3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "6d4f9e2c0e1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "affiliates"):
        op.create_table(
            "affiliates",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.String(), unique=True, index=True),
            sa.Column("affiliate_code", sa.String(length=50), unique=True, index=True),
            sa.Column("status", sa.String(), server_default="pending"),
            sa.Column("tier", sa.String(), server_default="bronze"),
            sa.Column("total_clicks", sa.Integer(), server_default="0"),
            sa.Column("total_conversions", sa.Integer(), server_default="0"),
            sa.Column("total_revenue", sa.Float(), server_default="0"),
            sa.Column("total_commission", sa.Float(), server_default="0"),
            sa.Column("balance", sa.Float(), server_default="0"),
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

    if not _has_table(inspector, "referral_links"):
        op.create_table(
            "referral_links",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("affiliate_id", sa.Integer(), sa.ForeignKey("affiliates.id")),
            sa.Column("link_code", sa.String(length=100), unique=True, index=True),
            sa.Column("campaign_name", sa.String(length=100), nullable=True),
            sa.Column("destination_url", sa.String(), nullable=False),
            sa.Column("clicks", sa.Integer(), server_default="0"),
            sa.Column("conversions", sa.Integer(), server_default="0"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("valid_until", sa.DateTime(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "click_tracking"):
        op.create_table(
            "click_tracking",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "referral_link_id", sa.Integer(), sa.ForeignKey("referral_links.id")
            ),
            sa.Column("affiliate_id", sa.Integer(), sa.ForeignKey("affiliates.id")),
            sa.Column("ip_address", sa.String(), nullable=True),
            sa.Column("user_agent", sa.String(), nullable=True),
            sa.Column("referrer", sa.String(), nullable=True),
            sa.Column("session_id", sa.String(), nullable=True),
            sa.Column(
                "clicked_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "conversions"):
        op.create_table(
            "conversions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("affiliate_id", sa.Integer(), sa.ForeignKey("affiliates.id")),
            sa.Column(
                "referral_link_id", sa.Integer(), sa.ForeignKey("referral_links.id")
            ),
            sa.Column("referred_user_id", sa.String(), index=True),
            sa.Column("subscription_id", sa.Integer(), nullable=True),
            sa.Column("conversion_value", sa.Float(), nullable=False),
            sa.Column("commission_rate", sa.Float(), nullable=False),
            sa.Column("commission_amount", sa.Float(), nullable=False),
            sa.Column("status", sa.String(), server_default="pending"),
            sa.Column(
                "converted_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
        )

    if not _has_table(inspector, "commission_rules"):
        op.create_table(
            "commission_rules",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tier", sa.String(), nullable=False),
            sa.Column("reward_type", sa.String(), nullable=False),
            sa.Column("fixed_amount", sa.Float(), nullable=True),
            sa.Column("percentage", sa.Float(), nullable=True),
            sa.Column("min_threshold", sa.Float(), nullable=True),
            sa.Column("configuration", sa.JSON(), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not _has_table(inspector, "payouts"):
        op.create_table(
            "payouts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("affiliate_id", sa.Integer(), sa.ForeignKey("affiliates.id")),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("status", sa.String(), server_default="pending"),
            sa.Column("payment_method", sa.String(), nullable=True),
            sa.Column("transaction_id", sa.String(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "requested_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
        )

    if not _has_table(inspector, "affiliate_coupons"):
        op.create_table(
            "affiliate_coupons",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("affiliate_id", sa.Integer(), sa.ForeignKey("affiliates.id")),
            sa.Column("coupon_code", sa.String(length=50), unique=True, index=True),
            sa.Column("discount_type", sa.String(), nullable=False),
            sa.Column("discount_value", sa.Float(), nullable=False),
            sa.Column("usage_count", sa.Integer(), server_default="0"),
            sa.Column("max_uses", sa.Integer(), nullable=True),
            sa.Column("valid_until", sa.DateTime(), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
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
        "affiliate_coupons",
        "payouts",
        "commission_rules",
        "conversions",
        "click_tracking",
        "referral_links",
        "affiliates",
    ]:
        if _has_table(inspector, table):
            op.drop_table(table)
