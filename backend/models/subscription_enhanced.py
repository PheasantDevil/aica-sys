"""
Enhanced Subscription Models for AICA-SyS
Phase 9-3: Subscription enhancement
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
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


class PlanType(str, Enum):
    """プランタイプ"""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    """請求サイクル"""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class CouponType(str, Enum):
    """クーポンタイプ"""

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class InvoiceStatus(str, Enum):
    """請求書ステータス"""

    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


# SQLAlchemy Models
class SubscriptionPlanDB(Base):
    """サブスクリプションプランDBモデル"""

    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_type = Column(String, unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    monthly_price = Column(Float)
    yearly_price = Column(Float)
    features = Column(JSON)  # プラン機能のリスト
    max_content_generation = Column(Integer)  # 月間生成上限
    max_storage_gb = Column(Integer)  # ストレージ上限（GB）
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSubscriptionDB(Base):
    """ユーザーサブスクリプションDBモデル"""

    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    billing_cycle = Column(String)
    status = Column(String, default="active")  # active, canceled, past_due
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CouponDB(Base):
    """クーポンDBモデル"""

    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    coupon_type = Column(String)
    amount = Column(Float)  # パーセントまたは固定額
    description = Column(Text, nullable=True)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CouponUsageDB(Base):
    """クーポン使用履歴DBモデル"""

    __tablename__ = "coupon_usage"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"))
    user_id = Column(String, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"))
    discount_amount = Column(Float)
    used_at = Column(DateTime, default=datetime.utcnow)


class InvoiceDB(Base):
    """請求書DBモデル"""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True)
    user_id = Column(String, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"))
    amount = Column(Float)
    tax = Column(Float, default=0)
    total_amount = Column(Float)
    status = Column(String)
    stripe_invoice_id = Column(String, nullable=True)
    invoice_pdf_url = Column(String, nullable=True)
    due_date = Column(DateTime)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaymentMethodDB(Base):
    """支払い方法DBモデル"""

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    stripe_payment_method_id = Column(String, unique=True)
    card_brand = Column(String, nullable=True)
    card_last4 = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubscriptionEventDB(Base):
    """サブスクリプションイベントDBモデル"""

    __tablename__ = "subscription_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"))
    event_type = Column(String)  # created, upgraded, downgraded, canceled, renewed
    from_plan = Column(String, nullable=True)
    to_plan = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models
class SubscriptionPlan(BaseModel):
    """サブスクリプションプランモデル"""

    id: int
    plan_type: str
    name: str
    description: str
    monthly_price: float
    yearly_price: float
    features: list
    max_content_generation: int
    max_storage_gb: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSubscription(BaseModel):
    """ユーザーサブスクリプションモデル"""

    id: int
    user_id: str
    plan_id: int
    billing_cycle: str
    status: str
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    trial_end_date: Optional[datetime] = None
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Coupon(BaseModel):
    """クーポンモデル"""

    id: int
    code: str
    coupon_type: str
    amount: float
    description: Optional[str] = None
    max_uses: Optional[int] = None
    used_count: int
    valid_from: datetime
    valid_until: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Invoice(BaseModel):
    """請求書モデル"""

    id: int
    invoice_number: str
    user_id: str
    subscription_id: int
    amount: float
    tax: float
    total_amount: float
    status: str
    stripe_invoice_id: Optional[str] = None
    invoice_pdf_url: Optional[str] = None
    due_date: datetime
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentMethod(BaseModel):
    """支払い方法モデル"""

    id: int
    user_id: str
    stripe_payment_method_id: str
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionEvent(BaseModel):
    """サブスクリプションイベントモデル"""

    id: int
    user_id: str
    subscription_id: int
    event_type: str
    from_plan: Optional[str] = None
    to_plan: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
