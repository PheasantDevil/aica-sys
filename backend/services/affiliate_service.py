"""
Affiliate Service for AICA-SyS
Phase 9-4: Affiliate system
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.affiliate import (
    AffiliateCouponDB,
    AffiliateDB,
    AffiliateStatus,
    ClickTrackingDB,
    CommissionRuleDB,
    ConversionDB,
    ConversionStatus,
    PayoutDB,
    PayoutStatus,
    ReferralLinkDB,
    RewardType,
)

logger = logging.getLogger(__name__)


class AffiliateService:
    """アフィリエイトサービス"""

    def __init__(self, db: Session):
        self.db = db

    # アフィリエイト登録
    async def register_affiliate(self, user_id: str) -> AffiliateDB:
        """アフィリエイトを登録"""
        # 既存チェック
        existing = (
            self.db.query(AffiliateDB).filter(AffiliateDB.user_id == user_id).first()
        )

        if existing:
            return existing

        # アフィリエイトコード生成
        affiliate_code = self._generate_affiliate_code()

        affiliate = AffiliateDB(
            user_id=user_id,
            affiliate_code=affiliate_code,
            status=AffiliateStatus.ACTIVE,
            tier="bronze",
        )
        self.db.add(affiliate)
        self.db.commit()
        self.db.refresh(affiliate)
        logger.info(f"Affiliate registered: {affiliate.id}")
        return affiliate

    async def get_affiliate(self, user_id: str) -> Optional[AffiliateDB]:
        """アフィリエイトを取得"""
        return self.db.query(AffiliateDB).filter(AffiliateDB.user_id == user_id).first()

    async def update_affiliate_tier(
        self, affiliate_id: int, new_tier: str
    ) -> AffiliateDB:
        """アフィリエイトのティアを更新"""
        affiliate = (
            self.db.query(AffiliateDB).filter(AffiliateDB.id == affiliate_id).first()
        )

        if not affiliate:
            raise ValueError("Affiliate not found")

        affiliate.tier = new_tier
        self.db.commit()
        self.db.refresh(affiliate)
        logger.info(f"Affiliate tier updated: {affiliate_id} -> {new_tier}")
        return affiliate

    # 紹介リンク
    async def create_referral_link(
        self,
        affiliate_id: int,
        destination_url: str,
        campaign_name: Optional[str] = None,
    ) -> ReferralLinkDB:
        """紹介リンクを作成"""
        link_code = self._generate_link_code()

        link = ReferralLinkDB(
            affiliate_id=affiliate_id,
            link_code=link_code,
            campaign_name=campaign_name,
            destination_url=destination_url,
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        logger.info(f"Referral link created: {link.id}")
        return link

    async def get_referral_links(
        self, affiliate_id: int, active_only: bool = True
    ) -> List[ReferralLinkDB]:
        """紹介リンク一覧を取得"""
        query = self.db.query(ReferralLinkDB).filter(
            ReferralLinkDB.affiliate_id == affiliate_id
        )
        if active_only:
            query = query.filter(ReferralLinkDB.is_active == True)
        return query.all()

    # クリック追跡
    async def track_click(
        self,
        link_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
    ) -> ClickTrackingDB:
        """クリックを追跡"""
        # リンク取得
        link = (
            self.db.query(ReferralLinkDB)
            .filter(
                ReferralLinkDB.link_code == link_code, ReferralLinkDB.is_active == True
            )
            .first()
        )

        if not link:
            raise ValueError("Referral link not found or inactive")

        # クリック記録
        click = ClickTrackingDB(
            referral_link_id=link.id,
            affiliate_id=link.affiliate_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
        )
        self.db.add(click)

        # クリック数更新
        link.clicks += 1
        affiliate = (
            self.db.query(AffiliateDB)
            .filter(AffiliateDB.id == link.affiliate_id)
            .first()
        )
        if affiliate:
            affiliate.total_clicks += 1

        self.db.commit()
        self.db.refresh(click)
        logger.info(f"Click tracked: {click.id}")
        return click

    # コンバージョン
    async def record_conversion(
        self,
        link_code: str,
        referred_user_id: str,
        conversion_value: float,
        subscription_id: Optional[int] = None,
    ) -> ConversionDB:
        """コンバージョンを記録"""
        # リンク取得
        link = (
            self.db.query(ReferralLinkDB)
            .filter(ReferralLinkDB.link_code == link_code)
            .first()
        )

        if not link:
            raise ValueError("Referral link not found")

        # アフィリエイト取得
        affiliate = (
            self.db.query(AffiliateDB)
            .filter(AffiliateDB.id == link.affiliate_id)
            .first()
        )

        if not affiliate:
            raise ValueError("Affiliate not found")

        # 報酬計算
        commission_rate, commission_amount = await self._calculate_commission(
            affiliate.tier, conversion_value
        )

        # コンバージョン記録
        conversion = ConversionDB(
            affiliate_id=affiliate.id,
            referral_link_id=link.id,
            referred_user_id=referred_user_id,
            subscription_id=subscription_id,
            conversion_value=conversion_value,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            status=ConversionStatus.PENDING,
        )
        self.db.add(conversion)

        # 統計更新
        link.conversions += 1
        affiliate.total_conversions += 1
        affiliate.total_revenue += conversion_value

        self.db.commit()
        self.db.refresh(conversion)
        logger.info(f"Conversion recorded: {conversion.id}")
        return conversion

    async def approve_conversion(self, conversion_id: int) -> ConversionDB:
        """コンバージョンを承認"""
        conversion = (
            self.db.query(ConversionDB).filter(ConversionDB.id == conversion_id).first()
        )

        if not conversion:
            raise ValueError("Conversion not found")

        conversion.status = ConversionStatus.APPROVED
        conversion.approved_at = datetime.utcnow()

        # アフィリエイトの残高更新
        affiliate = (
            self.db.query(AffiliateDB)
            .filter(AffiliateDB.id == conversion.affiliate_id)
            .first()
        )

        if affiliate:
            affiliate.total_commission += conversion.commission_amount
            affiliate.balance += conversion.commission_amount

        self.db.commit()
        self.db.refresh(conversion)
        logger.info(f"Conversion approved: {conversion.id}")
        return conversion

    # 報酬ルール
    async def create_commission_rule(
        self,
        tier: str,
        reward_type: RewardType,
        fixed_amount: Optional[float] = None,
        percentage: Optional[float] = None,
        min_threshold: Optional[float] = None,
    ) -> CommissionRuleDB:
        """報酬ルールを作成"""
        rule = CommissionRuleDB(
            tier=tier,
            reward_type=reward_type,
            fixed_amount=fixed_amount,
            percentage=percentage,
            min_threshold=min_threshold,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        logger.info(f"Commission rule created: {rule.id}")
        return rule

    async def get_commission_rules(
        self, tier: Optional[str] = None, active_only: bool = True
    ) -> List[CommissionRuleDB]:
        """報酬ルール一覧を取得"""
        query = self.db.query(CommissionRuleDB)
        if tier:
            query = query.filter(CommissionRuleDB.tier == tier)
        if active_only:
            query = query.filter(CommissionRuleDB.is_active == True)
        return query.all()

    # 支払い
    async def request_payout(
        self,
        affiliate_id: int,
        amount: Optional[float] = None,
        payment_method: str = "bank_transfer",
    ) -> PayoutDB:
        """支払いをリクエスト"""
        affiliate = (
            self.db.query(AffiliateDB).filter(AffiliateDB.id == affiliate_id).first()
        )

        if not affiliate:
            raise ValueError("Affiliate not found")

        # 金額が指定されていない場合は全額
        payout_amount = amount if amount else affiliate.balance

        if payout_amount <= 0:
            raise ValueError("Invalid payout amount")

        if payout_amount > affiliate.balance:
            raise ValueError("Insufficient balance")

        payout = PayoutDB(
            affiliate_id=affiliate_id,
            amount=payout_amount,
            payment_method=payment_method,
            status=PayoutStatus.PENDING,
        )
        self.db.add(payout)

        # 残高減算
        affiliate.balance -= payout_amount

        self.db.commit()
        self.db.refresh(payout)
        logger.info(f"Payout requested: {payout.id}")
        return payout

    async def complete_payout(
        self, payout_id: int, transaction_id: Optional[str] = None
    ) -> PayoutDB:
        """支払いを完了"""
        payout = self.db.query(PayoutDB).filter(PayoutDB.id == payout_id).first()

        if not payout:
            raise ValueError("Payout not found")

        payout.status = PayoutStatus.COMPLETED
        payout.completed_at = datetime.utcnow()
        if transaction_id:
            payout.transaction_id = transaction_id

        self.db.commit()
        self.db.refresh(payout)
        logger.info(f"Payout completed: {payout.id}")
        return payout

    async def get_payouts(self, affiliate_id: int, limit: int = 50) -> List[PayoutDB]:
        """支払い履歴を取得"""
        payouts = (
            self.db.query(PayoutDB)
            .filter(PayoutDB.affiliate_id == affiliate_id)
            .order_by(PayoutDB.requested_at.desc())
            .limit(limit)
            .all()
        )
        return payouts

    # 専用クーポン
    async def create_affiliate_coupon(
        self,
        affiliate_id: int,
        discount_type: str,
        discount_value: float,
        max_uses: Optional[int] = None,
        valid_until: Optional[datetime] = None,
    ) -> AffiliateCouponDB:
        """アフィリエイト専用クーポンを作成"""
        # クーポンコード生成
        coupon_code = self._generate_coupon_code()

        coupon = AffiliateCouponDB(
            affiliate_id=affiliate_id,
            coupon_code=coupon_code,
            discount_type=discount_type,
            discount_value=discount_value,
            max_uses=max_uses,
            valid_until=valid_until,
        )
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        logger.info(f"Affiliate coupon created: {coupon.id}")
        return coupon

    # 分析
    async def get_affiliate_stats(self, affiliate_id: int) -> Dict[str, Any]:
        """アフィリエイト統計を取得"""
        affiliate = (
            self.db.query(AffiliateDB).filter(AffiliateDB.id == affiliate_id).first()
        )

        if not affiliate:
            raise ValueError("Affiliate not found")

        # コンバージョン率
        conversion_rate = 0.0
        if affiliate.total_clicks > 0:
            conversion_rate = (
                affiliate.total_conversions / affiliate.total_clicks
            ) * 100

        # 平均注文額
        avg_order_value = 0.0
        if affiliate.total_conversions > 0:
            avg_order_value = affiliate.total_revenue / affiliate.total_conversions

        # 保留中のコンバージョン
        pending_conversions = (
            self.db.query(ConversionDB)
            .filter(
                ConversionDB.affiliate_id == affiliate_id,
                ConversionDB.status == ConversionStatus.PENDING,
            )
            .count()
        )

        return {
            "affiliate_code": affiliate.affiliate_code,
            "tier": affiliate.tier,
            "total_clicks": affiliate.total_clicks,
            "total_conversions": affiliate.total_conversions,
            "conversion_rate": round(conversion_rate, 2),
            "total_revenue": affiliate.total_revenue,
            "total_commission": affiliate.total_commission,
            "avg_order_value": round(avg_order_value, 2),
            "balance": affiliate.balance,
            "pending_conversions": pending_conversions,
        }

    async def get_top_affiliates(
        self, limit: int = 10, order_by: str = "total_revenue"
    ) -> List[AffiliateDB]:
        """トップアフィリエイトを取得"""
        query = self.db.query(AffiliateDB).filter(
            AffiliateDB.status == AffiliateStatus.ACTIVE
        )

        if order_by == "total_revenue":
            query = query.order_by(AffiliateDB.total_revenue.desc())
        elif order_by == "total_conversions":
            query = query.order_by(AffiliateDB.total_conversions.desc())
        elif order_by == "total_commission":
            query = query.order_by(AffiliateDB.total_commission.desc())

        return query.limit(limit).all()

    # 内部メソッド
    def _generate_affiliate_code(self) -> str:
        """アフィリエイトコードを生成"""
        while True:
            code = f"AFF-{secrets.token_hex(4).upper()}"
            existing = (
                self.db.query(AffiliateDB)
                .filter(AffiliateDB.affiliate_code == code)
                .first()
            )
            if not existing:
                return code

    def _generate_link_code(self) -> str:
        """リンクコードを生成"""
        while True:
            code = secrets.token_urlsafe(8)
            existing = (
                self.db.query(ReferralLinkDB)
                .filter(ReferralLinkDB.link_code == code)
                .first()
            )
            if not existing:
                return code

    def _generate_coupon_code(self) -> str:
        """クーポンコードを生成"""
        while True:
            code = f"PARTNER-{secrets.token_hex(3).upper()}"
            existing = (
                self.db.query(AffiliateCouponDB)
                .filter(AffiliateCouponDB.coupon_code == code)
                .first()
            )
            if not existing:
                return code

    async def _calculate_commission(
        self, tier: str, conversion_value: float
    ) -> tuple[float, float]:
        """報酬を計算"""
        # ティア別のルールを取得
        rule = (
            self.db.query(CommissionRuleDB)
            .filter(CommissionRuleDB.tier == tier, CommissionRuleDB.is_active == True)
            .first()
        )

        if not rule:
            # デフォルト: 10%
            commission_rate = 10.0
            commission_amount = conversion_value * 0.1
        elif rule.reward_type == RewardType.FIXED:
            commission_rate = 0.0
            commission_amount = rule.fixed_amount or 0.0
        elif rule.reward_type == RewardType.PERCENTAGE:
            commission_rate = rule.percentage or 10.0
            commission_amount = conversion_value * (commission_rate / 100)
        else:  # TIERED
            # 段階制の実装（簡略版）
            commission_rate = rule.percentage or 10.0
            commission_amount = conversion_value * (commission_rate / 100)

        return commission_rate, commission_amount
