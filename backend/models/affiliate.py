"""
Affiliate Models for AICA-SyS
Phase 9-4: Affiliate system
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from database import Base


class AffiliateStatus(str, Enum):
    """アフィリエイトステータス"""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class RewardType(str, Enum):
    """報酬タイプ"""

    FIXED = "fixed"  # 定額
    PERCENTAGE = "percentage"  # パーセント
    TIERED = "tiered"  # 段階制


class PayoutStatus(str, Enum):
    """支払いステータス"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversionStatus(str, Enum):
    """コンバージョンステータス"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# SQLAlchemy Models
class AffiliateDB(Base):
    """アフィリエイトDBモデル"""

    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    affiliate_code = Column(String(50), unique=True, index=True)
    status = Column(String, default=AffiliateStatus.PENDING)
    tier = Column(String, default="bronze")  # bronze, silver, gold, platinum
    total_clicks = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_commission = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)  # 未払い残高
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReferralLinkDB(Base):
    """紹介リンクDBモデル"""

    __tablename__ = "referral_links"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    link_code = Column(String(100), unique=True, index=True)
    campaign_name = Column(String(100), nullable=True)
    destination_url = Column(String)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClickTrackingDB(Base):
    """クリック追跡DBモデル"""

    __tablename__ = "click_tracking"

    id = Column(Integer, primary_key=True, index=True)
    referral_link_id = Column(Integer, ForeignKey("referral_links.id"))
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    session_id = Column(String, nullable=True, index=True)
    clicked_at = Column(DateTime, default=datetime.utcnow)


class ConversionDB(Base):
    """コンバージョンDBモデル"""

    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    referral_link_id = Column(Integer, ForeignKey("referral_links.id"))
    referred_user_id = Column(String, index=True)
    subscription_id = Column(Integer, nullable=True)
    conversion_value = Column(Float)  # 売上金額
    commission_rate = Column(Float)  # 報酬率
    commission_amount = Column(Float)  # 報酬額
    status = Column(String, default=ConversionStatus.PENDING)
    converted_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)


class CommissionRuleDB(Base):
    """報酬ルールDBモデル"""

    __tablename__ = "commission_rules"

    id = Column(Integer, primary_key=True, index=True)
    tier = Column(String)
    reward_type = Column(String)
    fixed_amount = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    min_threshold = Column(Float, nullable=True)  # 最小金額
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PayoutDB(Base):
    """支払いDBモデル"""

    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    amount = Column(Float)
    status = Column(String, default=PayoutStatus.PENDING)
    payment_method = Column(String, nullable=True)  # bank_transfer, paypal, stripe
    transaction_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class AffiliateCouponDB(Base):
    """アフィリエイト専用クーポンDBモデル"""

    __tablename__ = "affiliate_coupons"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"))
    coupon_code = Column(String(50), unique=True, index=True)
    discount_type = Column(String)  # percentage, fixed_amount
    discount_value = Column(Float)
    usage_count = Column(Integer, default=0)
    max_uses = Column(Integer, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models
class Affiliate(BaseModel):
    """アフィリエイトモデル"""

    id: int
    user_id: str
    affiliate_code: str
    status: str
    tier: str
    total_clicks: int
    total_conversions: int
    total_revenue: float
    total_commission: float
    balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReferralLink(BaseModel):
    """紹介リンクモデル"""

    id: int
    affiliate_id: int
    link_code: str
    campaign_name: Optional[str] = None
    destination_url: str
    clicks: int
    conversions: int
    is_active: bool
    valid_until: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClickTracking(BaseModel):
    """クリック追跡モデル"""

    id: int
    referral_link_id: int
    affiliate_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None
    clicked_at: datetime

    class Config:
        from_attributes = True


class Conversion(BaseModel):
    """コンバージョンモデル"""

    id: int
    affiliate_id: int
    referral_link_id: int
    referred_user_id: str
    subscription_id: Optional[int] = None
    conversion_value: float
    commission_rate: float
    commission_amount: float
    status: str
    converted_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommissionRule(BaseModel):
    """報酬ルールモデル"""

    id: int
    tier: str
    reward_type: str
    fixed_amount: Optional[float] = None
    percentage: Optional[float] = None
    min_threshold: Optional[float] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Payout(BaseModel):
    """支払いモデル"""

    id: int
    affiliate_id: int
    amount: float
    status: str
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AffiliateCoupon(BaseModel):
    """アフィリエイト専用クーポンモデル"""

    id: int
    affiliate_id: int
    coupon_code: str
    discount_type: str
    discount_value: float
    usage_count: int
    max_uses: Optional[int] = None
    valid_until: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
