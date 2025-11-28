"""
Analytics Router for AICA-SyS
Phase 9-5: Analytics and reports
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Request Models
class EventTrackRequest(BaseModel):
    """イベント追跡リクエスト"""

    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class MetricRecordRequest(BaseModel):
    """メトリック記録リクエスト"""

    metric_name: str
    metric_value: float
    dimensions: Optional[Dict[str, Any]] = None


class ReportGenerateRequest(BaseModel):
    """レポート生成リクエスト"""

    report_type: str
    title: str
    parameters: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class ScheduledReportCreateRequest(BaseModel):
    """スケジュールレポート作成リクエスト"""

    report_type: str
    title: str
    frequency: str
    recipients: List[str]
    parameters: Optional[Dict[str, Any]] = None


class DashboardCreateRequest(BaseModel):
    """ダッシュボード作成リクエスト"""

    name: str
    user_id: str
    widgets: List[Dict[str, Any]]
    description: Optional[str] = None
    is_public: bool = False


class UserSegmentCreateRequest(BaseModel):
    """ユーザーセグメント作成リクエスト"""

    name: str
    criteria: Dict[str, Any]
    description: Optional[str] = None


# Event Tracking Endpoints
@router.post("/events")
async def track_event(request: EventTrackRequest, db: Session = Depends(get_db)):
    """イベントを追跡"""
    try:
        service = AnalyticsService(db)
        event = await service.track_event(
            event_type=request.event_type,
            user_id=request.user_id,
            session_id=request.session_id,
            properties=request.properties,
        )
        return {"success": True, "event": event}
    except Exception as e:
        logger.error(f"Track event error: {e}")
        raise HTTPException(status_code=500, detail="イベント追跡に失敗しました")


@router.get("/events")
async def get_events(
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """イベント一覧を取得"""
    try:
        service = AnalyticsService(db)
        events = await service.get_events(
            event_type=event_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return {"success": True, "events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Get events error: {e}")
        raise HTTPException(status_code=500, detail="イベント取得に失敗しました")


# Metrics Endpoints
@router.post("/metrics")
async def record_metric(request: MetricRecordRequest, db: Session = Depends(get_db)):
    """メトリックを記録"""
    try:
        service = AnalyticsService(db)
        snapshot = await service.record_metric(
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            dimensions=request.dimensions,
        )
        return {"success": True, "snapshot": snapshot}
    except Exception as e:
        logger.error(f"Record metric error: {e}")
        raise HTTPException(status_code=500, detail="メトリック記録に失敗しました")


@router.get("/metrics/{metric_name}/history")
async def get_metric_history(
    metric_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """メトリック履歴を取得"""
    try:
        service = AnalyticsService(db)
        history = await service.get_metric_history(
            metric_name=metric_name, start_date=start_date, end_date=end_date
        )
        return {"success": True, "history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Get metric history error: {e}")
        raise HTTPException(status_code=500, detail="履歴取得に失敗しました")


# Business Analytics Endpoints
@router.get("/revenue")
async def get_revenue_analytics(
    start_date: datetime, end_date: datetime, db: Session = Depends(get_db)
):
    """売上分析を取得"""
    try:
        service = AnalyticsService(db)
        analytics = await service.get_revenue_analytics(start_date, end_date)
        return {"success": True, "analytics": analytics}
    except Exception as e:
        logger.error(f"Get revenue analytics error: {e}")
        raise HTTPException(status_code=500, detail="分析取得に失敗しました")


@router.get("/user-growth")
async def get_user_growth_analytics(
    start_date: datetime, end_date: datetime, db: Session = Depends(get_db)
):
    """ユーザー成長分析を取得"""
    try:
        service = AnalyticsService(db)
        analytics = await service.get_user_growth_analytics(start_date, end_date)
        return {"success": True, "analytics": analytics}
    except Exception as e:
        logger.error(f"Get user growth analytics error: {e}")
        raise HTTPException(status_code=500, detail="分析取得に失敗しました")


@router.get("/user-behavior")
async def get_user_behavior_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    affiliate_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """ユーザー行動分析を取得"""
    try:
        service = AnalyticsService(db)
        resolved_end = end_date or datetime.utcnow()
        resolved_start = start_date or (resolved_end - timedelta(days=14))
        analytics = await service.get_user_behavior_analytics(
            resolved_start, resolved_end, affiliate_id=affiliate_id
        )
        return {"success": True, "analytics": analytics}
    except Exception as e:
        logger.error(f"Get user behavior analytics error: {e}")
        raise HTTPException(status_code=500, detail="分析取得に失敗しました")


@router.get("/content-performance")
async def get_content_performance(
    start_date: datetime,
    end_date: datetime,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """コンテンツパフォーマンスを取得"""
    try:
        service = AnalyticsService(db)
        performance = await service.get_content_performance(start_date, end_date, limit)
        return {"success": True, "performance": performance}
    except Exception as e:
        logger.error(f"Get content performance error: {e}")
        raise HTTPException(status_code=500, detail="取得に失敗しました")


@router.get("/article-performance/{article_id}")
async def get_article_performance_detail(
    article_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """記事別の詳細パフォーマンス分析を取得"""
    try:
        service = AnalyticsService(db)
        resolved_end = end_date or datetime.utcnow()
        resolved_start = start_date or (resolved_end - timedelta(days=30))
        performance = await service.get_article_performance_detail(
            article_id, resolved_start, resolved_end
        )
        if "error" in performance:
            raise HTTPException(status_code=404, detail=performance["error"])
        return {"success": True, "performance": performance}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get article performance detail error: {e}")
        raise HTTPException(status_code=500, detail="分析取得に失敗しました")


@router.get("/article-rankings")
async def get_article_rankings(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: str = "page_views",
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """記事ランキングを取得"""
    try:
        service = AnalyticsService(db)
        resolved_end = end_date or datetime.utcnow()
        resolved_start = start_date or (resolved_end - timedelta(days=30))
        rankings = await service.get_article_rankings(
            resolved_start, resolved_end, sort_by=sort_by, limit=limit
        )
        return {"success": True, "rankings": rankings}
    except Exception as e:
        logger.error(f"Get article rankings error: {e}")
        raise HTTPException(status_code=500, detail="ランキング取得に失敗しました")


@router.get("/kpis")
async def get_kpis(db: Session = Depends(get_db)):
    """主要KPIを取得"""
    try:
        service = AnalyticsService(db)
        kpis = await service.calculate_kpis()
        return {"success": True, "kpis": kpis}
    except Exception as e:
        logger.error(f"Get KPIs error: {e}")
        raise HTTPException(status_code=500, detail="KPI取得に失敗しました")


# Report Endpoints
@router.post("/reports")
async def generate_report(
    request: ReportGenerateRequest, db: Session = Depends(get_db)
):
    """レポートを生成"""
    try:
        service = AnalyticsService(db)
        report = await service.generate_report(
            report_type=request.report_type,
            title=request.title,
            parameters=request.parameters,
            created_by=request.created_by,
        )
        return {"success": True, "report": report}
    except Exception as e:
        logger.error(f"Generate report error: {e}")
        raise HTTPException(status_code=500, detail="レポート生成に失敗しました")


# Scheduled Report Endpoints
@router.post("/scheduled-reports")
async def create_scheduled_report(
    request: ScheduledReportCreateRequest, db: Session = Depends(get_db)
):
    """スケジュールレポートを作成"""
    try:
        service = AnalyticsService(db)
        scheduled = await service.create_scheduled_report(
            report_type=request.report_type,
            title=request.title,
            frequency=request.frequency,
            recipients=request.recipients,
            parameters=request.parameters,
        )
        return {"success": True, "scheduled_report": scheduled}
    except Exception as e:
        logger.error(f"Create scheduled report error: {e}")
        raise HTTPException(status_code=500, detail="作成に失敗しました")


# Dashboard Endpoints
@router.post("/dashboards")
async def create_dashboard(
    request: DashboardCreateRequest, db: Session = Depends(get_db)
):
    """ダッシュボードを作成"""
    try:
        service = AnalyticsService(db)
        dashboard = await service.create_dashboard(
            name=request.name,
            user_id=request.user_id,
            widgets=request.widgets,
            description=request.description,
            is_public=request.is_public,
        )
        return {"success": True, "dashboard": dashboard}
    except Exception as e:
        logger.error(f"Create dashboard error: {e}")
        raise HTTPException(status_code=500, detail="作成に失敗しました")


@router.get("/dashboards")
async def get_dashboards(
    user_id: Optional[str] = None,
    include_public: bool = True,
    db: Session = Depends(get_db),
):
    """ダッシュボード一覧を取得"""
    try:
        service = AnalyticsService(db)
        dashboards = await service.get_dashboards(user_id, include_public)
        return {"success": True, "dashboards": dashboards, "count": len(dashboards)}
    except Exception as e:
        logger.error(f"Get dashboards error: {e}")
        raise HTTPException(status_code=500, detail="取得に失敗しました")


# User Segment Endpoints
@router.post("/segments")
async def create_user_segment(
    request: UserSegmentCreateRequest, db: Session = Depends(get_db)
):
    """ユーザーセグメントを作成"""
    try:
        service = AnalyticsService(db)
        segment = await service.create_user_segment(
            name=request.name,
            criteria=request.criteria,
            description=request.description,
        )
        return {"success": True, "segment": segment}
    except Exception as e:
        logger.error(f"Create user segment error: {e}")
        raise HTTPException(status_code=500, detail="作成に失敗しました")
