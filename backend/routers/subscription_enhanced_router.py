"""
Enhanced Subscription Router for AICA-SyS
Phase 9-3: Subscription enhancement
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.subscription_enhanced_service import SubscriptionEnhancedService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscription-enhanced", tags=["subscription-enhanced"])


# Request Models
class PlanCreateRequest(BaseModel):
    """プラン作成リクエスト"""
    plan_type: str
    name: str
    description: str
    monthly_price: float
    yearly_price: float
    features: List[str]
    max_content_generation: int
    max_storage_gb: int


class SubscriptionCreateRequest(BaseModel):
    """サブスクリプション作成リクエスト"""
    user_id: str
    plan_type: str
    billing_cycle: str
    with_trial: bool = True


class SubscriptionUpgradeRequest(BaseModel):
    """サブスクリプションアップグレードリクエスト"""
    subscription_id: int
    new_plan_type: str


class SubscriptionCancelRequest(BaseModel):
    """サブスクリプションキャンセルリクエスト"""
    subscription_id: int
    cancel_at_period_end: bool = True


class CouponCreateRequest(BaseModel):
    """クーポン作成リクエスト"""
    code: str
    coupon_type: str
    amount: float
    description: Optional[str] = None
    max_uses: Optional[int] = None
    valid_until: Optional[datetime] = None


class CouponApplyRequest(BaseModel):
    """クーポン適用リクエスト"""
    code: str
    user_id: str
    subscription_id: int
    base_amount: float


class InvoiceCreateRequest(BaseModel):
    """請求書作成リクエスト"""
    user_id: str
    subscription_id: int
    amount: float
    tax_rate: float = 0.1


class PaymentMethodRequest(BaseModel):
    """支払い方法リクエスト"""
    user_id: str
    stripe_payment_method_id: str
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    set_default: bool = False


# Plan Endpoints
@router.post("/plans")
async def create_plan(
    request: PlanCreateRequest,
    db: Session = Depends(get_db)
):
    """プランを作成"""
    try:
        service = SubscriptionEnhancedService(db)
        plan = await service.create_plan(
            plan_type=request.plan_type,
            name=request.name,
            description=request.description,
            monthly_price=request.monthly_price,
            yearly_price=request.yearly_price,
            features=request.features,
            max_content_generation=request.max_content_generation,
            max_storage_gb=request.max_storage_gb
        )
        return {"success": True, "plan": plan}
    except Exception as e:
        logger.error(f"Plan creation error: {e}")
        raise HTTPException(status_code=500, detail="プラン作成に失敗しました")


@router.get("/plans")
async def get_plans(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """プラン一覧を取得"""
    try:
        service = SubscriptionEnhancedService(db)
        plans = await service.get_plans(active_only)
        return {"success": True, "plans": plans, "count": len(plans)}
    except Exception as e:
        logger.error(f"Get plans error: {e}")
        raise HTTPException(status_code=500, detail="プラン取得に失敗しました")


# Subscription Endpoints
@router.post("/subscriptions")
async def create_subscription(
    request: SubscriptionCreateRequest,
    db: Session = Depends(get_db)
):
    """サブスクリプションを作成"""
    try:
        service = SubscriptionEnhancedService(db)
        subscription = await service.create_subscription(
            user_id=request.user_id,
            plan_type=request.plan_type,
            billing_cycle=request.billing_cycle,
            with_trial=request.with_trial
        )
        return {"success": True, "subscription": subscription}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Subscription creation error: {e}")
        raise HTTPException(status_code=500, detail="サブスクリプション作成に失敗しました")


@router.put("/subscriptions/upgrade")
async def upgrade_subscription(
    request: SubscriptionUpgradeRequest,
    db: Session = Depends(get_db)
):
    """サブスクリプションをアップグレード"""
    try:
        service = SubscriptionEnhancedService(db)
        subscription = await service.upgrade_subscription(
            subscription_id=request.subscription_id,
            new_plan_type=request.new_plan_type
        )
        return {"success": True, "subscription": subscription}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Subscription upgrade error: {e}")
        raise HTTPException(status_code=500, detail="アップグレードに失敗しました")


@router.put("/subscriptions/cancel")
async def cancel_subscription(
    request: SubscriptionCancelRequest,
    db: Session = Depends(get_db)
):
    """サブスクリプションをキャンセル"""
    try:
        service = SubscriptionEnhancedService(db)
        subscription = await service.cancel_subscription(
            subscription_id=request.subscription_id,
            cancel_at_period_end=request.cancel_at_period_end
        )
        return {"success": True, "subscription": subscription}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Subscription cancel error: {e}")
        raise HTTPException(status_code=500, detail="キャンセルに失敗しました")


# Coupon Endpoints
@router.post("/coupons")
async def create_coupon(
    request: CouponCreateRequest,
    db: Session = Depends(get_db)
):
    """クーポンを作成"""
    try:
        service = SubscriptionEnhancedService(db)
        coupon = await service.create_coupon(
            code=request.code,
            coupon_type=request.coupon_type,
            amount=request.amount,
            description=request.description,
            max_uses=request.max_uses,
            valid_until=request.valid_until
        )
        return {"success": True, "coupon": coupon}
    except Exception as e:
        logger.error(f"Coupon creation error: {e}")
        raise HTTPException(status_code=500, detail="クーポン作成に失敗しました")


@router.get("/coupons/validate/{code}")
async def validate_coupon(
    code: str,
    db: Session = Depends(get_db)
):
    """クーポンを検証"""
    try:
        service = SubscriptionEnhancedService(db)
        coupon = await service.validate_coupon(code)
        if coupon:
            return {"success": True, "valid": True, "coupon": coupon}
        else:
            return {"success": True, "valid": False}
    except Exception as e:
        logger.error(f"Coupon validation error: {e}")
        raise HTTPException(status_code=500, detail="クーポン検証に失敗しました")


@router.post("/coupons/apply")
async def apply_coupon(
    request: CouponApplyRequest,
    db: Session = Depends(get_db)
):
    """クーポンを適用"""
    try:
        service = SubscriptionEnhancedService(db)
        discount_amount = await service.apply_coupon(
            code=request.code,
            user_id=request.user_id,
            subscription_id=request.subscription_id,
            base_amount=request.base_amount
        )
        final_amount = request.base_amount - discount_amount
        return {
            "success": True,
            "discount_amount": discount_amount,
            "final_amount": final_amount
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Coupon apply error: {e}")
        raise HTTPException(status_code=500, detail="クーポン適用に失敗しました")


# Invoice Endpoints
@router.post("/invoices")
async def create_invoice(
    request: InvoiceCreateRequest,
    db: Session = Depends(get_db)
):
    """請求書を作成"""
    try:
        service = SubscriptionEnhancedService(db)
        invoice = await service.create_invoice(
            user_id=request.user_id,
            subscription_id=request.subscription_id,
            amount=request.amount,
            tax_rate=request.tax_rate
        )
        return {"success": True, "invoice": invoice}
    except Exception as e:
        logger.error(f"Invoice creation error: {e}")
        raise HTTPException(status_code=500, detail="請求書作成に失敗しました")


@router.put("/invoices/{invoice_id}/paid")
async def mark_invoice_paid(
    invoice_id: int,
    stripe_invoice_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """請求書を支払い済みにする"""
    try:
        service = SubscriptionEnhancedService(db)
        invoice = await service.mark_invoice_paid(invoice_id, stripe_invoice_id)
        return {"success": True, "invoice": invoice}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Mark invoice paid error: {e}")
        raise HTTPException(status_code=500, detail="請求書更新に失敗しました")


@router.get("/invoices/{user_id}")
async def get_invoices(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """請求書一覧を取得"""
    try:
        service = SubscriptionEnhancedService(db)
        invoices = await service.get_invoices(user_id, limit)
        return {"success": True, "invoices": invoices, "count": len(invoices)}
    except Exception as e:
        logger.error(f"Get invoices error: {e}")
        raise HTTPException(status_code=500, detail="請求書取得に失敗しました")


# Payment Method Endpoints
@router.post("/payment-methods")
async def add_payment_method(
    request: PaymentMethodRequest,
    db: Session = Depends(get_db)
):
    """支払い方法を追加"""
    try:
        service = SubscriptionEnhancedService(db)
        payment_method = await service.add_payment_method(
            user_id=request.user_id,
            stripe_payment_method_id=request.stripe_payment_method_id,
            card_brand=request.card_brand,
            card_last4=request.card_last4,
            set_default=request.set_default
        )
        return {"success": True, "payment_method": payment_method}
    except Exception as e:
        logger.error(f"Add payment method error: {e}")
        raise HTTPException(status_code=500, detail="支払い方法追加に失敗しました")


@router.get("/payment-methods/{user_id}")
async def get_payment_methods(
    user_id: str,
    db: Session = Depends(get_db)
):
    """支払い方法一覧を取得"""
    try:
        service = SubscriptionEnhancedService(db)
        methods = await service.get_payment_methods(user_id)
        return {"success": True, "payment_methods": methods, "count": len(methods)}
    except Exception as e:
        logger.error(f"Get payment methods error: {e}")
        raise HTTPException(status_code=500, detail="支払い方法取得に失敗しました")


# Analytics Endpoints
@router.get("/analytics/mrr")
async def get_mrr(
    db: Session = Depends(get_db)
):
    """MRR（月次経常収益）を取得"""
    try:
        service = SubscriptionEnhancedService(db)
        mrr = await service.calculate_mrr()
        return {"success": True, "mrr": mrr}
    except Exception as e:
        logger.error(f"Get MRR error: {e}")
        raise HTTPException(status_code=500, detail="MRR計算に失敗しました")


@router.get("/analytics/churn-rate")
async def get_churn_rate(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """チャーン率を取得"""
    try:
        service = SubscriptionEnhancedService(db)
        churn_rate = await service.calculate_churn_rate(start_date, end_date)
        return {"success": True, "churn_rate": churn_rate}
    except Exception as e:
        logger.error(f"Get churn rate error: {e}")
        raise HTTPException(status_code=500, detail="チャーン率計算に失敗しました")


@router.get("/analytics/revenue-by-plan")
async def get_revenue_by_plan(
    db: Session = Depends(get_db)
):
    """プラン別収益を取得"""
    try:
        service = SubscriptionEnhancedService(db)
        revenue = await service.get_revenue_by_plan()
        return {"success": True, "revenue_by_plan": revenue}
    except Exception as e:
        logger.error(f"Get revenue by plan error: {e}")
        raise HTTPException(status_code=500, detail="収益取得に失敗しました")

