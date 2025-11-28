"""
Analytics Service for AICA-SyS
Phase 9-5: Analytics and reports
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.analytics import (
    AnalyticsEventDB,
    DashboardDB,
    MetricSnapshotDB,
    ReportDB,
    ReportType,
    ScheduledReportDB,
    UserSegmentDB,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """アナリティクスサービス"""

    def __init__(self, db: Session):
        self.db = db

    # イベント追跡
    async def track_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsEventDB:
        """イベントを追跡"""
        event = AnalyticsEventDB(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            properties=properties,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        logger.info(f"Event tracked: {event_type}")
        return event

    async def get_events(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[AnalyticsEventDB]:
        """イベント一覧を取得"""
        query = self.db.query(AnalyticsEventDB)

        if event_type:
            query = query.filter(AnalyticsEventDB.event_type == event_type)
        if user_id:
            query = query.filter(AnalyticsEventDB.user_id == user_id)
        if start_date:
            query = query.filter(AnalyticsEventDB.created_at >= start_date)
        if end_date:
            query = query.filter(AnalyticsEventDB.created_at <= end_date)

        return query.order_by(AnalyticsEventDB.created_at.desc()).limit(limit).all()

    # メトリックスナップショット
    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        dimensions: Optional[Dict[str, Any]] = None,
    ) -> MetricSnapshotDB:
        """メトリックを記録"""
        snapshot = MetricSnapshotDB(
            metric_name=metric_name, metric_value=metric_value, dimensions=dimensions
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        logger.info(f"Metric recorded: {metric_name} = {metric_value}")
        return snapshot

    async def get_metric_history(
        self,
        metric_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        dimensions: Optional[Dict[str, Any]] = None,
    ) -> List[MetricSnapshotDB]:
        """メトリック履歴を取得"""
        query = self.db.query(MetricSnapshotDB).filter(
            MetricSnapshotDB.metric_name == metric_name
        )

        if start_date:
            query = query.filter(MetricSnapshotDB.timestamp >= start_date)
        if end_date:
            query = query.filter(MetricSnapshotDB.timestamp <= end_date)

        return query.order_by(MetricSnapshotDB.timestamp).all()

    # ビジネス分析
    async def get_revenue_analytics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """売上分析を取得"""
        # 実装では実際のサブスクリプションデータから集計
        from models.subscription_enhanced import SubscriptionPlanDB, UserSubscriptionDB

        # 期間内のアクティブサブスクリプション
        subscriptions = (
            self.db.query(UserSubscriptionDB, SubscriptionPlanDB)
            .join(
                SubscriptionPlanDB, UserSubscriptionDB.plan_id == SubscriptionPlanDB.id
            )
            .filter(
                UserSubscriptionDB.current_period_start >= start_date,
                UserSubscriptionDB.current_period_start <= end_date,
                UserSubscriptionDB.status == "active",
            )
            .all()
        )

        total_revenue = sum(plan.monthly_price for _, plan in subscriptions)

        # プラン別収益
        plan_revenue = {}
        for sub, plan in subscriptions:
            if plan.plan_type not in plan_revenue:
                plan_revenue[plan.plan_type] = 0
            plan_revenue[plan.plan_type] += plan.monthly_price

        return {
            "total_revenue": total_revenue,
            "subscription_count": len(subscriptions),
            "average_revenue": (
                total_revenue / len(subscriptions) if subscriptions else 0
            ),
            "revenue_by_plan": plan_revenue,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        }

    async def get_revenue_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """収益レポート (MRR/ARR/LTV/CACなど) を取得"""
        from models.affiliate import PayoutDB, PayoutStatus
        from models.subscription_enhanced import (
            InvoiceDB,
            SubscriptionEventDB,
            SubscriptionPlanDB,
            UserSubscriptionDB,
        )

        def fetch_active_subscriptions(
            period_start: datetime, period_end: datetime
        ) -> List[Any]:
            return (
                self.db.query(UserSubscriptionDB, SubscriptionPlanDB)
                .join(
                    SubscriptionPlanDB,
                    UserSubscriptionDB.plan_id == SubscriptionPlanDB.id,
                )
                .filter(
                    UserSubscriptionDB.current_period_start <= period_end,
                    UserSubscriptionDB.current_period_end >= period_start,
                    UserSubscriptionDB.status == "active",
                )
                .all()
            )

        subscriptions = fetch_active_subscriptions(start_date, end_date)

        def normalized_monthly_amount(subscription: Any, plan: Any) -> float:
            monthly_price = plan.monthly_price or 0.0
            if (
                subscription.billing_cycle
                and subscription.billing_cycle.lower() == "yearly"
            ):
                if plan.yearly_price:
                    return plan.yearly_price / 12
                if monthly_price:
                    return monthly_price
            if monthly_price == 0 and plan.yearly_price:
                return plan.yearly_price / 12
            return monthly_price

        plan_breakdown = defaultdict(float)
        mrr_total = 0.0
        mrr_trend_map: Dict[str, float] = defaultdict(float)

        for subscription, plan in subscriptions:
            monthly_value = normalized_monthly_amount(subscription, plan)
            mrr_total += monthly_value
            plan_key = plan.plan_type or plan.name or "unknown"
            plan_breakdown[plan_key] += monthly_value
            period_key = (
                subscription.current_period_start.replace(day=1).date().isoformat()
                if subscription.current_period_start
                else start_date.replace(day=1).date().isoformat()
            )
            mrr_trend_map[period_key] += monthly_value

        plan_breakdown_list = [
            {"plan": key, "mrr": round(value, 2)}
            for key, value in plan_breakdown.items()
        ]

        mrr_trend = [
            {"period": key, "mrr": round(value, 2)}
            for key, value in sorted(mrr_trend_map.items())
        ]

        previous_period_end = start_date - timedelta(days=1)
        previous_period_start = previous_period_end - (end_date - start_date)
        previous_subscriptions = fetch_active_subscriptions(
            previous_period_start, previous_period_end
        )
        previous_mrr = sum(
            normalized_monthly_amount(subscription, plan)
            for subscription, plan in previous_subscriptions
        )

        arr_value = mrr_total * 12
        previous_arr = previous_mrr * 12
        arr_growth_rate = (
            ((arr_value - previous_arr) / previous_arr) * 100 if previous_arr else 0.0
        )

        invoice_total = (
            self.db.query(func.coalesce(func.sum(InvoiceDB.total_amount), 0.0))
            .filter(
                InvoiceDB.status == "paid",
                InvoiceDB.paid_at.isnot(None),
                InvoiceDB.paid_at >= start_date,
                InvoiceDB.paid_at <= end_date,
            )
            .scalar()
            or 0.0
        )

        invoice_count = (
            self.db.query(func.count(InvoiceDB.id))
            .filter(
                InvoiceDB.status == "paid",
                InvoiceDB.paid_at.isnot(None),
                InvoiceDB.paid_at >= start_date,
                InvoiceDB.paid_at <= end_date,
            )
            .scalar()
            or 0
        )

        average_order_value = (
            invoice_total / invoice_count if invoice_count else invoice_total
        )

        active_customers = len(
            {subscription.user_id for subscription, _ in subscriptions}
        )
        average_revenue_per_user = (
            invoice_total / active_customers if active_customers else 0.0
        )

        cancellations = (
            self.db.query(func.count(SubscriptionEventDB.id))
            .filter(
                SubscriptionEventDB.event_type == "canceled",
                SubscriptionEventDB.created_at >= start_date,
                SubscriptionEventDB.created_at <= end_date,
            )
            .scalar()
            or 0
        )

        churn_rate = (
            cancellations / active_customers
            if cancellations and active_customers
            else 0.0
        )
        fallback_churn = 0.05
        churn_for_ltv = churn_rate if churn_rate > 0 else fallback_churn
        ltv = average_revenue_per_user / churn_for_ltv if churn_for_ltv else 0.0

        new_customers = (
            self.db.query(func.count(UserSubscriptionDB.id))
            .filter(
                UserSubscriptionDB.created_at >= start_date,
                UserSubscriptionDB.created_at <= end_date,
            )
            .scalar()
            or 0
        )

        marketing_spend = (
            self.db.query(func.coalesce(func.sum(PayoutDB.amount), 0.0))
            .filter(
                PayoutDB.status == PayoutStatus.COMPLETED,
                PayoutDB.completed_at.isnot(None),
                PayoutDB.completed_at >= start_date,
                PayoutDB.completed_at <= end_date,
            )
            .scalar()
            or 0.0
        )

        cac = marketing_spend / new_customers if new_customers else marketing_spend
        ltv_cac_ratio = ltv / cac if cac > 0 else None

        alerts: List[str] = []
        if churn_rate > 0.05:
            alerts.append(
                "直近期間のチャーン率が 5% を超えています。解約理由の分析を検討してください。"
            )
        if ltv_cac_ratio is not None and ltv_cac_ratio < 3:
            alerts.append(
                "LTV/CAC 比率が 3 未満です。獲得効率の改善が必要かもしれません。"
            )
        if arr_growth_rate < 0:
            alerts.append(
                "ARR が減少しています。価格やプラン構成の見直しを検討してください。"
            )

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_revenue": round(invoice_total, 2),
                "mrr": round(mrr_total, 2),
                "arr": round(arr_value, 2),
                "arr_growth_rate": round(arr_growth_rate, 2),
                "active_customers": active_customers,
                "invoice_count": invoice_count,
                "average_order_value": round(average_order_value, 2),
            },
            "plan_breakdown": plan_breakdown_list,
            "mrr_trend": mrr_trend,
            "ltv": {
                "ltv": round(ltv, 2),
                "average_revenue_per_user": round(average_revenue_per_user, 2),
                "churn_rate": round(churn_rate * 100, 2),
            },
            "acquisition": {
                "new_customers": new_customers,
                "marketing_spend": round(marketing_spend, 2),
                "cac": round(cac, 2),
                "ltv_to_cac": round(ltv_cac_ratio, 2) if ltv_cac_ratio else None,
            },
            "alerts": alerts,
        }

    async def get_user_growth_analytics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """ユーザー成長分析を取得"""
        from models.subscription_enhanced import UserSubscriptionDB

        # 新規ユーザー数（期間内）
        new_users = (
            self.db.query(UserSubscriptionDB)
            .filter(
                UserSubscriptionDB.created_at >= start_date,
                UserSubscriptionDB.created_at <= end_date,
            )
            .count()
        )

        # チャーンユーザー数
        churned_users = (
            self.db.query(UserSubscriptionDB)
            .filter(
                UserSubscriptionDB.status == "canceled",
                UserSubscriptionDB.updated_at >= start_date,
                UserSubscriptionDB.updated_at <= end_date,
            )
            .count()
        )

        # アクティブユーザー数
        active_users = (
            self.db.query(UserSubscriptionDB)
            .filter(UserSubscriptionDB.status == "active")
            .count()
        )

        # 成長率
        growth_rate = 0.0
        if active_users > 0:
            growth_rate = ((new_users - churned_users) / active_users) * 100

        return {
            "new_users": new_users,
            "churned_users": churned_users,
            "active_users": active_users,
            "net_growth": new_users - churned_users,
            "growth_rate": round(growth_rate, 2),
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        }

    async def get_user_behavior_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        affiliate_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """ユーザー行動分析を取得"""
        events = (
            self.db.query(AnalyticsEventDB)
            .filter(AnalyticsEventDB.created_at >= start_date)
            .filter(AnalyticsEventDB.created_at <= end_date)
            .order_by(AnalyticsEventDB.created_at.asc())
            .all()
        )

        filtered_events: List[AnalyticsEventDB] = []
        for event in events:
            props = event.properties or {}
            if affiliate_id is not None:
                prop_aff = props.get("affiliate_id") or props.get("affiliateId")
                if prop_aff is None or str(prop_aff) != str(affiliate_id):
                    continue
            filtered_events.append(event)

        if not filtered_events:
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "overview": {
                    "total_page_views": 0,
                    "unique_users": 0,
                    "total_sessions": 0,
                    "conversion_rate": 0.0,
                },
                "page_metrics": {
                    "average_time_on_page": 0.0,
                    "average_scroll_depth": 0.0,
                },
                "session_metrics": {
                    "average_session_duration": 0.0,
                    "bounce_rate": 0.0,
                },
                "conversion_metrics": {
                    "total_conversions": 0,
                    "conversion_value": 0.0,
                },
                "engagement": {
                    "scroll_distribution": {
                        "0-25%": 0,
                        "25-50%": 0,
                        "50-75%": 0,
                        "75-100%": 0,
                    }
                },
                "trend": [],
            }

        page_view_events = [
            event
            for event in filtered_events
            if event.event_type in ("page_view", "content_view")
        ]
        conversion_events = [
            event for event in filtered_events if event.event_type == "conversion"
        ]
        unique_users = {
            event.user_id for event in filtered_events if event.user_id is not None
        }

        session_map: Dict[str, Dict[str, Any]] = {}
        scroll_values: List[float] = []
        dwell_values: List[float] = []
        session_lengths: List[float] = []
        trend_map: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "date": "",
                "page_views": 0,
                "conversions": 0,
                "scroll_sum": 0.0,
                "scroll_count": 0,
            }
        )

        for event in filtered_events:
            props = event.properties or {}
            session_id = event.session_id
            if session_id:
                info = session_map.setdefault(
                    session_id,
                    {
                        "first": event.created_at,
                        "last": event.created_at,
                        "page_views": 0,
                    },
                )
                if event.created_at < info["first"]:
                    info["first"] = event.created_at
                if event.created_at > info["last"]:
                    info["last"] = event.created_at
                if event.event_type in ("page_view", "content_view"):
                    info["page_views"] += 1

            if event.event_type in ("page_view", "content_view"):
                duration = props.get("duration")
                if duration is not None:
                    try:
                        dwell_values.append(float(duration))
                    except (TypeError, ValueError):
                        pass
                scroll_depth = props.get("scroll_depth")
                if scroll_depth is not None:
                    try:
                        value = float(scroll_depth)
                        if value <= 1:
                            value *= 100
                        scroll_values.append(value)
                    except (TypeError, ValueError):
                        pass

            day_key = event.created_at.date().isoformat()
            bucket = trend_map[day_key]
            bucket["date"] = day_key
            if event.event_type in ("page_view", "content_view"):
                bucket["page_views"] += 1
            if event.event_type == "conversion":
                bucket["conversions"] += 1
            if "scroll_depth" in props:
                try:
                    sd = float(props["scroll_depth"])
                    if sd <= 1:
                        sd *= 100
                    bucket["scroll_sum"] += sd
                    bucket["scroll_count"] += 1
                except (TypeError, ValueError):
                    pass

        for session in session_map.values():
            duration = (session["last"] - session["first"]).total_seconds()
            if duration >= 0:
                session_lengths.append(duration)

        total_sessions = len(session_map)
        bounce_sessions = sum(
            1 for session in session_map.values() if session["page_views"] <= 1
        )
        average_session_duration = (
            sum(session_lengths) / len(session_lengths) if session_lengths else 0.0
        )
        average_time_on_page = (
            sum(dwell_values) / len(dwell_values) if dwell_values else 0.0
        )
        average_scroll_depth = (
            sum(scroll_values) / len(scroll_values) if scroll_values else 0.0
        )
        total_conversions = len(conversion_events)
        conversion_value = sum(
            float((event.properties or {}).get("value", 0))
            for event in conversion_events
        )
        conversion_rate = (
            (total_conversions / len(page_view_events) * 100)
            if page_view_events
            else 0.0
        )

        scroll_distribution = {
            "0-25%": 0,
            "25-50%": 0,
            "50-75%": 0,
            "75-100%": 0,
        }
        for value in scroll_values:
            if value < 25:
                scroll_distribution["0-25%"] += 1
            elif value < 50:
                scroll_distribution["25-50%"] += 1
            elif value < 75:
                scroll_distribution["50-75%"] += 1
            else:
                scroll_distribution["75-100%"] += 1

        trend_list: List[Dict[str, Any]] = []
        current = start_date.date()
        end_date_only = end_date.date()
        while current <= end_date_only:
            key = current.isoformat()
            bucket = trend_map.get(
                key,
                {
                    "date": key,
                    "page_views": 0,
                    "conversions": 0,
                    "scroll_sum": 0.0,
                    "scroll_count": 0,
                },
            )
            avg_scroll = (
                bucket["scroll_sum"] / bucket["scroll_count"]
                if bucket["scroll_count"]
                else 0.0
            )
            trend_list.append(
                {
                    "date": key,
                    "page_views": bucket["page_views"],
                    "conversions": bucket["conversions"],
                    "avg_scroll_depth": round(avg_scroll, 2),
                }
            )
            current += timedelta(days=1)

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "overview": {
                "total_page_views": len(page_view_events),
                "unique_users": len(unique_users),
                "total_sessions": total_sessions,
                "conversion_rate": round(conversion_rate, 2),
            },
            "page_metrics": {
                "average_time_on_page": round(average_time_on_page, 2),
                "average_scroll_depth": round(average_scroll_depth, 2),
            },
            "session_metrics": {
                "average_session_duration": round(average_session_duration, 2),
                "bounce_rate": round(
                    (bounce_sessions / total_sessions * 100) if total_sessions else 0.0,
                    2,
                ),
            },
            "conversion_metrics": {
                "total_conversions": total_conversions,
                "conversion_value": round(conversion_value, 2),
            },
            "engagement": {"scroll_distribution": scroll_distribution},
            "trend": trend_list,
        }

    async def get_content_performance(
        self, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> Dict[str, Any]:
        """コンテンツパフォーマンスを取得"""
        # イベントから集計
        views = (
            self.db.query(
                AnalyticsEventDB.properties["content_id"].label("content_id"),
                func.count(AnalyticsEventDB.id).label("view_count"),
            )
            .filter(
                AnalyticsEventDB.event_type == "content_view",
                AnalyticsEventDB.created_at >= start_date,
                AnalyticsEventDB.created_at <= end_date,
            )
            .group_by(AnalyticsEventDB.properties["content_id"])
            .order_by(func.count(AnalyticsEventDB.id).desc())
            .limit(limit)
            .all()
        )

        top_content = [
            {"content_id": row.content_id, "views": row.view_count} for row in views
        ]

        total_views = sum(row.view_count for row in views)

        return {
            "total_views": total_views,
            "top_content": top_content,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        }

    async def get_article_performance_detail(
        self,
        article_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """記事別の詳細パフォーマンス分析を取得"""
        from models.content import Article

        # 記事情報を取得
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return {
                "error": "Article not found",
                "article_id": article_id,
            }

        # 期間内のイベントを取得
        events = (
            self.db.query(AnalyticsEventDB)
            .filter(
                AnalyticsEventDB.properties["content_id"].astext == article_id,
                AnalyticsEventDB.created_at >= start_date,
                AnalyticsEventDB.created_at <= end_date,
            )
            .order_by(AnalyticsEventDB.created_at.asc())
            .all()
        )

        if not events:
            return {
                "article_id": article_id,
                "article_title": article.title,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "metrics": {
                    "page_views": 0,
                    "unique_users": 0,
                    "average_time_on_page": 0.0,
                    "engagement_rate": 0.0,
                    "conversion_rate": 0.0,
                },
                "engagement": {
                    "likes": 0,
                    "shares": 0,
                    "comments": 0,
                },
                "trend": [],
            }

        # イベントタイプ別に分類
        page_view_events = [
            e for e in events if e.event_type in ("page_view", "content_view")
        ]
        like_events = [e for e in events if e.event_type == "like"]
        share_events = [e for e in events if e.event_type == "share"]
        comment_events = [e for e in events if e.event_type == "comment"]
        conversion_events = [e for e in events if e.event_type == "conversion"]

        # ユニークユーザー数
        unique_users = {e.user_id for e in events if e.user_id is not None}

        # 滞在時間の計算
        dwell_times = []
        for event in page_view_events:
            props = event.properties or {}
            duration = props.get("duration")
            if duration is not None:
                try:
                    dwell_times.append(float(duration))
                except (TypeError, ValueError):
                    pass

        average_time_on_page = (
            sum(dwell_times) / len(dwell_times) if dwell_times else 0.0
        )

        # エンゲージメント率 (いいね+シェア+コメント) / PV
        total_engagements = len(like_events) + len(share_events) + len(comment_events)
        engagement_rate = (
            (total_engagements / len(page_view_events) * 100)
            if page_view_events
            else 0.0
        )

        # コンバージョン率
        conversion_rate = (
            (len(conversion_events) / len(page_view_events) * 100)
            if page_view_events
            else 0.0
        )

        # 日次トレンド
        trend_map: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "date": "",
                "page_views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "conversions": 0,
            }
        )

        for event in events:
            day_key = event.created_at.date().isoformat()
            bucket = trend_map[day_key]
            bucket["date"] = day_key

            if event.event_type in ("page_view", "content_view"):
                bucket["page_views"] += 1
            elif event.event_type == "like":
                bucket["likes"] += 1
            elif event.event_type == "share":
                bucket["shares"] += 1
            elif event.event_type == "comment":
                bucket["comments"] += 1
            elif event.event_type == "conversion":
                bucket["conversions"] += 1

        trend_list: List[Dict[str, Any]] = []
        current = start_date.date()
        end_date_only = end_date.date()
        while current <= end_date_only:
            key = current.isoformat()
            bucket = trend_map.get(
                key,
                {
                    "date": key,
                    "page_views": 0,
                    "likes": 0,
                    "shares": 0,
                    "comments": 0,
                    "conversions": 0,
                },
            )
            trend_list.append(bucket)
            current += timedelta(days=1)

        return {
            "article_id": article_id,
            "article_title": article.title,
            "article_published_at": (
                article.published_at.isoformat() if article.published_at else None
            ),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "metrics": {
                "page_views": len(page_view_events),
                "unique_users": len(unique_users),
                "average_time_on_page": round(average_time_on_page, 2),
                "engagement_rate": round(engagement_rate, 2),
                "conversion_rate": round(conversion_rate, 2),
            },
            "engagement": {
                "likes": len(like_events),
                "shares": len(share_events),
                "comments": len(comment_events),
            },
            "trend": trend_list,
        }

    async def get_article_rankings(
        self,
        start_date: datetime,
        end_date: datetime,
        sort_by: str = "page_views",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """記事ランキングを取得"""
        from models.content import Article

        # イベントから記事別の集計
        content_stats = (
            self.db.query(
                AnalyticsEventDB.properties["content_id"].label("content_id"),
                func.count(
                    func.case(
                        (
                            AnalyticsEventDB.event_type.in_(
                                ("page_view", "content_view")
                            ),
                            1,
                        )
                    )
                ).label("page_views"),
                func.count(func.case((AnalyticsEventDB.event_type == "like", 1))).label(
                    "likes"
                ),
                func.count(
                    func.case((AnalyticsEventDB.event_type == "share", 1))
                ).label("shares"),
                func.count(
                    func.case((AnalyticsEventDB.event_type == "comment", 1))
                ).label("comments"),
                func.count(
                    func.case((AnalyticsEventDB.event_type == "conversion", 1))
                ).label("conversions"),
                func.count(func.distinct(AnalyticsEventDB.user_id)).label(
                    "unique_users"
                ),
            )
            .filter(
                AnalyticsEventDB.created_at >= start_date,
                AnalyticsEventDB.created_at <= end_date,
            )
            .group_by(AnalyticsEventDB.properties["content_id"])
        )

        # ソート順を決定
        if sort_by == "page_views":
            content_stats = content_stats.order_by(
                func.count(
                    func.case(
                        (
                            AnalyticsEventDB.event_type.in_(
                                ("page_view", "content_view")
                            ),
                            1,
                        )
                    )
                ).desc()
            )
        elif sort_by == "engagement":
            # エンゲージメント = likes + shares + comments
            content_stats = content_stats.order_by(
                (
                    func.count(func.case((AnalyticsEventDB.event_type == "like", 1)))
                    + func.count(func.case((AnalyticsEventDB.event_type == "share", 1)))
                    + func.count(
                        func.case((AnalyticsEventDB.event_type == "comment", 1))
                    )
                ).desc()
            )
        elif sort_by == "conversions":
            content_stats = content_stats.order_by(
                func.count(
                    func.case((AnalyticsEventDB.event_type == "conversion", 1))
                ).desc()
            )
        else:
            content_stats = content_stats.order_by(
                func.count(
                    func.case(
                        (
                            AnalyticsEventDB.event_type.in_(
                                ("page_view", "content_view")
                            ),
                            1,
                        )
                    )
                ).desc()
            )

        stats = content_stats.limit(limit).all()

        # 記事IDのリストを作成
        article_ids = [stat.content_id for stat in stats if stat.content_id]

        # 一度のクエリで全ての記事情報を取得（N+1問題の回避）
        articles_dict = {}
        if article_ids:
            articles = self.db.query(Article).filter(Article.id.in_(article_ids)).all()
            articles_dict = {article.id: article for article in articles}

        # 記事情報を取得してランキングを作成
        rankings = []
        for stat in stats:
            article_id = stat.content_id
            article = articles_dict.get(article_id) if article_id else None

            if article:
                total_engagement = stat.likes + stat.shares + stat.comments
                engagement_rate = (
                    (total_engagement / stat.page_views * 100)
                    if stat.page_views > 0
                    else 0.0
                )
                conversion_rate = (
                    (stat.conversions / stat.page_views * 100)
                    if stat.page_views > 0
                    else 0.0
                )

                rankings.append(
                    {
                        "article_id": article_id,
                        "article_title": article.title,
                        "article_published_at": (
                            article.published_at.isoformat()
                            if article.published_at
                            else None
                        ),
                        "metrics": {
                            "page_views": stat.page_views,
                            "unique_users": stat.unique_users,
                            "likes": stat.likes,
                            "shares": stat.shares,
                            "comments": stat.comments,
                            "conversions": stat.conversions,
                            "engagement_rate": round(engagement_rate, 2),
                            "conversion_rate": round(conversion_rate, 2),
                        },
                    }
                )

        return {
            "rankings": rankings,
            "sort_by": sort_by,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "count": len(rankings),
        }

    # KPI計算
    async def calculate_kpis(self) -> Dict[str, Any]:
        """主要KPIを計算"""
        from models.subscription_enhanced import SubscriptionPlanDB, UserSubscriptionDB

        # MRR
        mrr_result = (
            self.db.query(func.sum(SubscriptionPlanDB.monthly_price))
            .join(
                UserSubscriptionDB, UserSubscriptionDB.plan_id == SubscriptionPlanDB.id
            )
            .filter(UserSubscriptionDB.status == "active")
            .scalar()
        )
        mrr = float(mrr_result) if mrr_result else 0.0

        # ARR
        arr = mrr * 12

        # アクティブユーザー数
        active_users = (
            self.db.query(UserSubscriptionDB)
            .filter(UserSubscriptionDB.status == "active")
            .count()
        )

        # ARPU
        arpu = mrr / active_users if active_users > 0 else 0

        # 30日間のチャーン率
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        churned_30d = (
            self.db.query(UserSubscriptionDB)
            .filter(
                UserSubscriptionDB.status == "canceled",
                UserSubscriptionDB.updated_at >= thirty_days_ago,
            )
            .count()
        )

        churn_rate = (churned_30d / active_users * 100) if active_users > 0 else 0

        return {
            "mrr": round(mrr, 2),
            "arr": round(arr, 2),
            "active_users": active_users,
            "arpu": round(arpu, 2),
            "churn_rate_30d": round(churn_rate, 2),
            "calculated_at": datetime.utcnow().isoformat(),
        }

    # レポート生成
    async def generate_report(
        self,
        report_type: str,
        title: str,
        parameters: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> ReportDB:
        """レポートを生成"""
        # レポートデータ生成
        data = await self._generate_report_data(report_type, parameters)

        report = ReportDB(
            report_type=report_type,
            title=title,
            parameters=parameters,
            data=data,
            format="json",
            created_by=created_by,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        logger.info(f"Report generated: {report.id}")
        return report

    async def _generate_report_data(
        self, report_type: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """レポートデータを生成"""
        params = parameters or {}
        start_date = params.get("start_date", datetime.utcnow() - timedelta(days=30))
        end_date = params.get("end_date", datetime.utcnow())

        if report_type == "revenue":
            return await self.get_revenue_analytics(start_date, end_date)
        elif report_type == "users":
            return await self.get_user_growth_analytics(start_date, end_date)
        elif report_type == "content":
            return await self.get_content_performance(start_date, end_date)
        elif report_type == "kpi":
            return await self.calculate_kpis()
        else:
            return {}

    async def save_social_post_report(
        self,
        title: str,
        summary: Dict[str, Any],
        period: Dict[str, Any],
        created_by: Optional[str] = None,
    ) -> ReportDB:
        """SNS投稿レポートを保存"""
        report = ReportDB(
            report_type=ReportType.SOCIAL.value,
            title=title,
            description="Automated SNS posting summary",
            parameters={"period": period},
            data=summary,
            format="json",
            created_by=created_by,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        logger.info(f"Social post report stored: {report.id}")
        return report

    # スケジュールレポート
    async def create_scheduled_report(
        self,
        report_type: str,
        title: str,
        frequency: str,
        recipients: List[str],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ScheduledReportDB:
        """スケジュールレポートを作成"""
        # 次回実行日時を計算
        next_run = self._calculate_next_run(frequency)

        scheduled = ScheduledReportDB(
            report_type=report_type,
            title=title,
            frequency=frequency,
            recipients=recipients,
            parameters=parameters,
            next_run=next_run,
        )
        self.db.add(scheduled)
        self.db.commit()
        self.db.refresh(scheduled)
        logger.info(f"Scheduled report created: {scheduled.id}")
        return scheduled

    def _calculate_next_run(self, frequency: str) -> datetime:
        """次回実行日時を計算"""
        now = datetime.utcnow()
        if frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        elif frequency == "monthly":
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=1)

    # ダッシュボード
    async def create_dashboard(
        self,
        name: str,
        user_id: str,
        widgets: List[Dict[str, Any]],
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> DashboardDB:
        """ダッシュボードを作成"""
        dashboard = DashboardDB(
            name=name,
            description=description,
            user_id=user_id,
            widgets=widgets,
            is_public=is_public,
        )
        self.db.add(dashboard)
        self.db.commit()
        self.db.refresh(dashboard)
        logger.info(f"Dashboard created: {dashboard.id}")
        return dashboard

    async def get_dashboards(
        self, user_id: Optional[str] = None, include_public: bool = True
    ) -> List[DashboardDB]:
        """ダッシュボード一覧を取得"""
        query = self.db.query(DashboardDB)

        if user_id:
            if include_public:
                query = query.filter(
                    (DashboardDB.user_id == user_id) | (DashboardDB.is_public == True)
                )
            else:
                query = query.filter(DashboardDB.user_id == user_id)
        elif include_public:
            query = query.filter(DashboardDB.is_public == True)

        return query.all()

    # ユーザーセグメント
    async def create_user_segment(
        self, name: str, criteria: Dict[str, Any], description: Optional[str] = None
    ) -> UserSegmentDB:
        """ユーザーセグメントを作成"""
        # ユーザー数を計算
        user_count = await self._calculate_segment_size(criteria)

        segment = UserSegmentDB(
            name=name, description=description, criteria=criteria, user_count=user_count
        )
        self.db.add(segment)
        self.db.commit()
        self.db.refresh(segment)
        logger.info(f"User segment created: {segment.id}")
        return segment

    async def _calculate_segment_size(self, criteria: Dict[str, Any]) -> int:
        """セグメントサイズを計算"""
        # 簡易実装
        from models.subscription_enhanced import UserSubscriptionDB

        query = self.db.query(UserSubscriptionDB)

        # 条件適用
        if "tier" in criteria:
            # ティア別フィルタ（実装例）
            pass

        return query.count()
