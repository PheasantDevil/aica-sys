"""
Affiliate Service for AICA-SyS
Phase 9-4: Affiliate system
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import case, func
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
        valid_until: Optional[datetime] = None,
    ) -> ReferralLinkDB:
        """紹介リンクを作成"""
        link_code = self._generate_link_code()

        link = ReferralLinkDB(
            affiliate_id=affiliate_id,
            link_code=link_code,
            campaign_name=campaign_name,
            destination_url=destination_url,
            valid_until=valid_until,
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
            # 有効期限が切れていないリンクのみ
            query = query.filter(
                (ReferralLinkDB.valid_until.is_(None))
                | (ReferralLinkDB.valid_until > datetime.utcnow())
            )
        return query.all()

    async def update_referral_link(
        self,
        link_id: int,
        is_active: Optional[bool] = None,
        valid_until: Optional[datetime] = None,
    ) -> ReferralLinkDB:
        """紹介リンクを更新"""
        link = (
            self.db.query(ReferralLinkDB).filter(ReferralLinkDB.id == link_id).first()
        )

        if not link:
            raise ValueError("Referral link not found")

        if is_active is not None:
            link.is_active = is_active
        if valid_until is not None:
            link.valid_until = valid_until

        self.db.commit()
        self.db.refresh(link)
        logger.info(f"Referral link updated: {link.id}")
        return link

    async def get_all_referral_links(
        self, active_only: bool = True, limit: int = 100
    ) -> List[ReferralLinkDB]:
        """全紹介リンクを取得（管理者用）"""
        query = self.db.query(ReferralLinkDB)
        if active_only:
            query = query.filter(ReferralLinkDB.is_active == True)
            query = query.filter(
                (ReferralLinkDB.valid_until.is_(None))
                | (ReferralLinkDB.valid_until > datetime.utcnow())
            )
        return query.order_by(ReferralLinkDB.created_at.desc()).limit(limit).all()

    async def get_click_statistics(
        self, affiliate_id: Optional[int] = None, link_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """クリック統計を取得"""
        base_query = self.db.query(ClickTrackingDB)

        if affiliate_id:
            base_query = base_query.filter(ClickTrackingDB.affiliate_id == affiliate_id)
        if link_id:
            base_query = base_query.filter(ClickTrackingDB.referral_link_id == link_id)

        total_clicks = base_query.count()

        # セッション別クリック数（ユニークセッション数）
        unique_sessions = (
            base_query.filter(ClickTrackingDB.session_id.isnot(None))
            .with_entities(ClickTrackingDB.session_id)
            .distinct()
            .count()
        )

        # リファラー別クリック数（ユニークリファラー数）
        unique_referrers = (
            base_query.filter(ClickTrackingDB.referrer.isnot(None))
            .with_entities(ClickTrackingDB.referrer)
            .distinct()
            .count()
        )

        return {
            "total_clicks": total_clicks,
            "unique_sessions": unique_sessions,
            "unique_referrers": unique_referrers,
        }

    # クリック追跡
    async def track_click(
        self,
        link_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
        session_id: Optional[str] = None,
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

        # 有効期限チェック
        if link.valid_until and link.valid_until < datetime.utcnow():
            raise ValueError("Referral link has expired")

        # クリック記録
        click = ClickTrackingDB(
            referral_link_id=link.id,
            affiliate_id=link.affiliate_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            session_id=session_id,
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
        configuration: Optional[Dict[str, Any]] = None,
    ) -> CommissionRuleDB:
        """報酬ルールを作成"""
        rule = CommissionRuleDB(
            tier=tier,
            reward_type=reward_type,
            fixed_amount=fixed_amount,
            percentage=percentage,
            min_threshold=min_threshold,
            configuration=configuration,
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

    async def list_conversions(
        self,
        affiliate_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 200,
    ) -> List[ConversionDB]:
        """コンバージョン一覧を取得"""
        start, end = self._normalize_period(start_date, end_date)
        query = self.db.query(ConversionDB).filter(
            ConversionDB.converted_at >= start, ConversionDB.converted_at <= end
        )

        if affiliate_id:
            query = query.filter(ConversionDB.affiliate_id == affiliate_id)
        if status:
            query = query.filter(ConversionDB.status == status)

        return query.order_by(ConversionDB.converted_at.desc()).limit(limit).all()

    async def get_commission_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        affiliate_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """コミッションレポートを取得"""
        start, end = self._normalize_period(start_date, end_date)
        filters = [
            ConversionDB.converted_at >= start,
            ConversionDB.converted_at <= end,
        ]
        if affiliate_id:
            filters.append(ConversionDB.affiliate_id == affiliate_id)

        totals = (
            self.db.query(
                func.count(ConversionDB.id),
                func.coalesce(func.sum(ConversionDB.commission_amount), 0.0),
                func.coalesce(
                    func.sum(
                        case(
                            (ConversionDB.status == ConversionStatus.PENDING, 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (ConversionDB.status == ConversionStatus.APPROVED, 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                ConversionDB.status == ConversionStatus.PENDING,
                                ConversionDB.commission_amount,
                            ),
                            else_=0.0,
                        )
                    ),
                    0.0,
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                ConversionDB.status == ConversionStatus.APPROVED,
                                ConversionDB.commission_amount,
                            ),
                            else_=0.0,
                        )
                    ),
                    0.0,
                ),
            )
            .filter(*filters)
            .one()
        )

        (
            total_conversions,
            total_commission,
            pending_conversions,
            approved_conversions,
            pending_commission,
            approved_commission,
        ) = totals

        breakdown = (
            self.db.query(
                ConversionDB.affiliate_id,
                AffiliateDB.affiliate_code,
                AffiliateDB.tier,
                func.count(ConversionDB.id).label("conversion_count"),
                func.sum(ConversionDB.commission_amount).label("total_commission"),
                func.sum(
                    case(
                        (
                            ConversionDB.status == ConversionStatus.PENDING,
                            ConversionDB.commission_amount,
                        ),
                        else_=0.0,
                    )
                ).label("pending_commission"),
                func.sum(
                    case(
                        (
                            ConversionDB.status == ConversionStatus.APPROVED,
                            ConversionDB.commission_amount,
                        ),
                        else_=0.0,
                    )
                ).label("approved_commission"),
                func.sum(
                    case(
                        (ConversionDB.status == ConversionStatus.PENDING, 1),
                        else_=0,
                    )
                ).label("pending_conversions"),
                func.sum(
                    case(
                        (ConversionDB.status == ConversionStatus.APPROVED, 1),
                        else_=0,
                    )
                ).label("approved_conversions"),
                func.max(ConversionDB.converted_at).label("last_conversion_at"),
            )
            .join(AffiliateDB, AffiliateDB.id == ConversionDB.affiliate_id)
            .filter(*filters)
            .group_by(
                ConversionDB.affiliate_id,
                AffiliateDB.affiliate_code,
                AffiliateDB.tier,
            )
            .all()
        )

        breakdown_payload = [
            {
                "affiliate_id": row.affiliate_id,
                "affiliate_code": row.affiliate_code,
                "tier": row.tier,
                "conversion_count": int(row.conversion_count or 0),
                "total_commission": float(row.total_commission or 0.0),
                "pending_commission": float(row.pending_commission or 0.0),
                "approved_commission": float(row.approved_commission or 0.0),
                "pending_conversions": int(row.pending_conversions or 0),
                "approved_conversions": int(row.approved_conversions or 0),
                "last_conversion_at": (
                    row.last_conversion_at.isoformat()
                    if row.last_conversion_at
                    else None
                ),
            }
            for row in breakdown
        ]

        return {
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "summary": {
                "total_conversions": int(total_conversions or 0),
                "total_commission": float(total_commission or 0.0),
                "pending_conversions": int(pending_conversions or 0),
                "approved_conversions": int(approved_conversions or 0),
                "pending_commission": float(pending_commission or 0.0),
                "approved_commission": float(approved_commission or 0.0),
            },
            "breakdown": breakdown_payload,
        }

    async def settle_commissions(
        self,
        min_balance: float = 5000.0,
        payment_method: str = "bank_transfer",
    ) -> List[PayoutDB]:
        """一定額以上の残高を自動的に支払いリクエストへ変換"""
        affiliates = (
            self.db.query(AffiliateDB).filter(AffiliateDB.balance >= min_balance).all()
        )

        payouts: List[PayoutDB] = []
        for affiliate in affiliates:
            payout = PayoutDB(
                affiliate_id=affiliate.id,
                amount=round(affiliate.balance, 2),
                payment_method=payment_method,
                status=PayoutStatus.PENDING,
            )
            affiliate.balance = 0.0
            self.db.add(payout)
            payouts.append(payout)

        self.db.commit()
        for payout in payouts:
            self.db.refresh(payout)

        logger.info(f"Auto settled payouts: {len(payouts)}")
        return payouts

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

    def _normalize_period(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> tuple[datetime, datetime]:
        """開始・終了日時を正規化"""
        end = end_date or datetime.utcnow()
        start = start_date or (end - timedelta(days=30))
        if start > end:
            start, end = end, start
        return start, end

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
        rule = (
            self.db.query(CommissionRuleDB)
            .filter(CommissionRuleDB.tier == tier, CommissionRuleDB.is_active == True)
            .first()
        )

        if not rule:
            commission_rate = 10.0
            commission_amount = conversion_value * 0.1
            return commission_rate, round(commission_amount, 2)

        if rule.min_threshold and conversion_value < rule.min_threshold:
            return 0.0, 0.0

        if rule.reward_type == RewardType.FIXED:
            commission_amount = rule.fixed_amount or 0.0
            commission_rate = (
                round((commission_amount / conversion_value) * 100, 2)
                if conversion_value
                else 0.0
            )
        elif rule.reward_type == RewardType.PERCENTAGE:
            commission_rate = rule.percentage or 10.0
            commission_amount = conversion_value * (commission_rate / 100)
        else:  # TIERED
            percentage = rule.percentage or 10.0
            config = rule.configuration or {}
            tiers = config.get("tiers", [])

            for tier_config in tiers:
                min_value = tier_config.get("min", 0)
                max_value = tier_config.get("max")
                if conversion_value < min_value:
                    continue
                if max_value is None or conversion_value < max_value:
                    percentage = tier_config.get("percentage", percentage)
                    break

            commission_rate = percentage
            commission_amount = conversion_value * (percentage / 100)

        return round(commission_rate, 2), round(commission_amount, 2)
