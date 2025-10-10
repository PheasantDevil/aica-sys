"""
Enhanced Subscription Service for AICA-SyS
Phase 9-3: Subscription enhancement
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.subscription_enhanced import (CouponDB, CouponType, InvoiceDB,
                                          InvoiceStatus, PaymentMethodDB,
                                          SubscriptionEventDB,
                                          SubscriptionPlanDB,
                                          UserSubscriptionDB)

logger = logging.getLogger(__name__)


class SubscriptionEnhancedService:
    """拡張サブスクリプションサービス"""

    def __init__(self, db: Session):
        self.db = db

    # プラン管理
    async def create_plan(
        self,
        plan_type: str,
        name: str,
        description: str,
        monthly_price: float,
        yearly_price: float,
        features: List[str],
        max_content_generation: int,
        max_storage_gb: int
    ) -> SubscriptionPlanDB:
        """プランを作成"""
        plan = SubscriptionPlanDB(
            plan_type=plan_type,
            name=name,
            description=description,
            monthly_price=monthly_price,
            yearly_price=yearly_price,
            features=features,
            max_content_generation=max_content_generation,
            max_storage_gb=max_storage_gb
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        logger.info(f"Plan created: {plan.id}")
        return plan

    async def get_plans(
        self,
        active_only: bool = True
    ) -> List[SubscriptionPlanDB]:
        """プラン一覧を取得"""
        query = self.db.query(SubscriptionPlanDB)
        if active_only:
            query = query.filter(SubscriptionPlanDB.is_active == True)
        return query.all()

    async def get_plan_by_type(self, plan_type: str) -> Optional[SubscriptionPlanDB]:
        """プランタイプでプランを取得"""
        return self.db.query(SubscriptionPlanDB).filter(
            SubscriptionPlanDB.plan_type == plan_type
        ).first()

    # サブスクリプション管理
    async def create_subscription(
        self,
        user_id: str,
        plan_type: str,
        billing_cycle: str,
        with_trial: bool = True
    ) -> UserSubscriptionDB:
        """サブスクリプションを作成"""
        plan = await self.get_plan_by_type(plan_type)
        if not plan:
            raise ValueError(f"Plan not found: {plan_type}")

        # トライアル期間設定
        trial_end_date = None
        if with_trial and plan_type != "free":
            trial_end_date = datetime.utcnow() + timedelta(days=14)

        # 期間設定
        current_period_start = datetime.utcnow()
        if billing_cycle == "monthly":
            current_period_end = current_period_start + timedelta(days=30)
        else:  # yearly
            current_period_end = current_period_start + timedelta(days=365)

        subscription = UserSubscriptionDB(
            user_id=user_id,
            plan_id=plan.id,
            billing_cycle=billing_cycle,
            status="active",
            trial_end_date=trial_end_date,
            current_period_start=current_period_start,
            current_period_end=current_period_end
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)

        # イベント記録
        await self._record_event(
            user_id=user_id,
            subscription_id=subscription.id,
            event_type="created",
            to_plan=plan_type
        )

        logger.info(f"Subscription created: {subscription.id}")
        return subscription

    async def upgrade_subscription(
        self,
        subscription_id: int,
        new_plan_type: str
    ) -> UserSubscriptionDB:
        """サブスクリプションをアップグレード"""
        subscription = self.db.query(UserSubscriptionDB).filter(
            UserSubscriptionDB.id == subscription_id
        ).first()

        if not subscription:
            raise ValueError("Subscription not found")

        old_plan = self.db.query(SubscriptionPlanDB).filter(
            SubscriptionPlanDB.id == subscription.plan_id
        ).first()

        new_plan = await self.get_plan_by_type(new_plan_type)
        if not new_plan:
            raise ValueError(f"Plan not found: {new_plan_type}")

        # プラン更新
        subscription.plan_id = new_plan.id
        self.db.commit()
        self.db.refresh(subscription)

        # イベント記録
        await self._record_event(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type="upgraded",
            from_plan=old_plan.plan_type,
            to_plan=new_plan_type
        )

        logger.info(f"Subscription upgraded: {subscription.id}")
        return subscription

    async def cancel_subscription(
        self,
        subscription_id: int,
        cancel_at_period_end: bool = True
    ) -> UserSubscriptionDB:
        """サブスクリプションをキャンセル"""
        subscription = self.db.query(UserSubscriptionDB).filter(
            UserSubscriptionDB.id == subscription_id
        ).first()

        if not subscription:
            raise ValueError("Subscription not found")

        if cancel_at_period_end:
            subscription.cancel_at_period_end = True
        else:
            subscription.status = "canceled"

        self.db.commit()
        self.db.refresh(subscription)

        # イベント記録
        await self._record_event(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            event_type="canceled",
            metadata={"cancel_at_period_end": cancel_at_period_end}
        )

        logger.info(f"Subscription canceled: {subscription.id}")
        return subscription

    # クーポン管理
    async def create_coupon(
        self,
        code: str,
        coupon_type: CouponType,
        amount: float,
        description: Optional[str] = None,
        max_uses: Optional[int] = None,
        valid_until: Optional[datetime] = None
    ) -> CouponDB:
        """クーポンを作成"""
        coupon = CouponDB(
            code=code.upper(),
            coupon_type=coupon_type,
            amount=amount,
            description=description,
            max_uses=max_uses,
            valid_until=valid_until
        )
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        logger.info(f"Coupon created: {coupon.code}")
        return coupon

    async def validate_coupon(self, code: str) -> Optional[CouponDB]:
        """クーポンを検証"""
        coupon = self.db.query(CouponDB).filter(
            CouponDB.code == code.upper(),
            CouponDB.is_active == True
        ).first()

        if not coupon:
            return None

        # 有効期限チェック
        if coupon.valid_until and coupon.valid_until < datetime.utcnow():
            return None

        # 使用回数チェック
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return None

        return coupon

    async def apply_coupon(
        self,
        code: str,
        user_id: str,
        subscription_id: int,
        base_amount: float
    ) -> float:
        """クーポンを適用"""
        coupon = await self.validate_coupon(code)
        if not coupon:
            raise ValueError("Invalid or expired coupon")

        # 割引額計算
        if coupon.coupon_type == CouponType.PERCENTAGE:
            discount_amount = base_amount * (coupon.amount / 100)
        else:  # FIXED_AMOUNT
            discount_amount = min(coupon.amount, base_amount)

        # 使用履歴記録
        from models.subscription_enhanced import CouponUsageDB
        usage = CouponUsageDB(
            coupon_id=coupon.id,
            user_id=user_id,
            subscription_id=subscription_id,
            discount_amount=discount_amount
        )
        self.db.add(usage)

        # 使用回数更新
        coupon.used_count += 1
        self.db.commit()

        logger.info(f"Coupon applied: {code} - {discount_amount}")
        return discount_amount

    # 請求書管理
    async def create_invoice(
        self,
        user_id: str,
        subscription_id: int,
        amount: float,
        tax_rate: float = 0.1
    ) -> InvoiceDB:
        """請求書を作成"""
        tax = amount * tax_rate
        total_amount = amount + tax

        # 請求書番号生成
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"

        invoice = InvoiceDB(
            invoice_number=invoice_number,
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            tax=tax,
            total_amount=total_amount,
            status=InvoiceStatus.OPEN,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        logger.info(f"Invoice created: {invoice.invoice_number}")
        return invoice

    async def mark_invoice_paid(
        self,
        invoice_id: int,
        stripe_invoice_id: Optional[str] = None
    ) -> InvoiceDB:
        """請求書を支払い済みにする"""
        invoice = self.db.query(InvoiceDB).filter(
            InvoiceDB.id == invoice_id
        ).first()

        if not invoice:
            raise ValueError("Invoice not found")

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        if stripe_invoice_id:
            invoice.stripe_invoice_id = stripe_invoice_id

        self.db.commit()
        self.db.refresh(invoice)
        logger.info(f"Invoice marked paid: {invoice.invoice_number}")
        return invoice

    async def get_invoices(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[InvoiceDB]:
        """請求書一覧を取得"""
        invoices = self.db.query(InvoiceDB).filter(
            InvoiceDB.user_id == user_id
        ).order_by(InvoiceDB.created_at.desc()).limit(limit).all()
        return invoices

    # 支払い方法管理
    async def add_payment_method(
        self,
        user_id: str,
        stripe_payment_method_id: str,
        card_brand: Optional[str] = None,
        card_last4: Optional[str] = None,
        set_default: bool = False
    ) -> PaymentMethodDB:
        """支払い方法を追加"""
        # デフォルトに設定する場合、他をデフォルトから外す
        if set_default:
            self.db.query(PaymentMethodDB).filter(
                PaymentMethodDB.user_id == user_id
            ).update({"is_default": False})

        payment_method = PaymentMethodDB(
            user_id=user_id,
            stripe_payment_method_id=stripe_payment_method_id,
            card_brand=card_brand,
            card_last4=card_last4,
            is_default=set_default
        )
        self.db.add(payment_method)
        self.db.commit()
        self.db.refresh(payment_method)
        logger.info(f"Payment method added: {payment_method.id}")
        return payment_method

    async def get_payment_methods(
        self,
        user_id: str
    ) -> List[PaymentMethodDB]:
        """支払い方法一覧を取得"""
        methods = self.db.query(PaymentMethodDB).filter(
            PaymentMethodDB.user_id == user_id
        ).order_by(PaymentMethodDB.is_default.desc()).all()
        return methods

    # 分析
    async def calculate_mrr(self) -> float:
        """MRR（月次経常収益）を計算"""
        # アクティブなサブスクリプションの合計
        result = self.db.query(
            func.sum(SubscriptionPlanDB.monthly_price)
        ).join(
            UserSubscriptionDB,
            UserSubscriptionDB.plan_id == SubscriptionPlanDB.id
        ).filter(
            UserSubscriptionDB.status == "active"
        ).scalar()

        return float(result) if result else 0.0

    async def calculate_churn_rate(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """チャーン率を計算"""
        # 期間開始時のアクティブユーザー数
        start_count = self.db.query(UserSubscriptionDB).filter(
            UserSubscriptionDB.status == "active",
            UserSubscriptionDB.created_at < start_date
        ).count()

        # 期間中にキャンセルされたユーザー数
        churned_count = self.db.query(SubscriptionEventDB).filter(
            SubscriptionEventDB.event_type == "canceled",
            SubscriptionEventDB.created_at >= start_date,
            SubscriptionEventDB.created_at <= end_date
        ).count()

        if start_count == 0:
            return 0.0

        return (churned_count / start_count) * 100

    async def get_revenue_by_plan(self) -> Dict[str, float]:
        """プラン別収益を取得"""
        results = self.db.query(
            SubscriptionPlanDB.plan_type,
            func.sum(SubscriptionPlanDB.monthly_price)
        ).join(
            UserSubscriptionDB,
            UserSubscriptionDB.plan_id == SubscriptionPlanDB.id
        ).filter(
            UserSubscriptionDB.status == "active"
        ).group_by(SubscriptionPlanDB.plan_type).all()

        return {plan_type: float(revenue) for plan_type, revenue in results}

    # 内部メソッド
    async def _record_event(
        self,
        user_id: str,
        subscription_id: int,
        event_type: str,
        from_plan: Optional[str] = None,
        to_plan: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """イベントを記録"""
        event = SubscriptionEventDB(
            user_id=user_id,
            subscription_id=subscription_id,
            event_type=event_type,
            from_plan=from_plan,
            to_plan=to_plan,
            metadata=metadata
        )
        self.db.add(event)
        self.db.commit()

