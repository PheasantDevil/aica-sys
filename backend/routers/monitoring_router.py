from datetime import datetime, timedelta
from typing import List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from pydantic import BaseModel
from security.auth_middleware import get_current_user
from services.monitoring_service import (
    AlertLevel,
    HealthStatus,
    MetricType,
    MonitoringService,
    get_monitoring_service,
)
from sqlalchemy.orm import Session
from utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


class AlertResolveRequest(BaseModel):
    alert_id: str


class MetricQueryRequest(BaseModel):
    metric_type: Optional[MetricType] = None
    limit: int = 100
    hours: int = 24


class AlertQueryRequest(BaseModel):
    level: Optional[AlertLevel] = None
    resolved: Optional[bool] = None
    limit: int = 50


@router.get("/health", response_model=dict)
async def get_health_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    システムのヘルスステータスを取得
    """
    try:
        health_status = monitoring_service.get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health status",
        )


@router.get("/metrics", response_model=List[dict])
async def get_metrics(
    metric_type: Optional[MetricType] = None,
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    メトリクスを取得
    """
    try:
        metrics = monitoring_service.get_metrics(metric_type, limit)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics",
        )


@router.get("/metrics/system", response_model=List[dict])
async def get_system_metrics(
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    システムメトリクスを取得
    """
    try:
        metrics = monitoring_service.get_metrics(MetricType.SYSTEM, limit)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics",
        )


@router.get("/metrics/application", response_model=List[dict])
async def get_application_metrics(
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    アプリケーションメトリクスを取得
    """
    try:
        metrics = monitoring_service.get_metrics(MetricType.APPLICATION, limit)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get application metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application metrics",
        )


@router.get("/metrics/business", response_model=List[dict])
async def get_business_metrics(
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    ビジネスメトリクスを取得
    """
    try:
        metrics = monitoring_service.get_metrics(MetricType.BUSINESS, limit)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get business metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve business metrics",
        )


@router.get("/alerts", response_model=List[dict])
async def get_alerts(
    level: Optional[AlertLevel] = None,
    resolved: Optional[bool] = None,
    limit: int = 50,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    アラートを取得
    """
    try:
        alerts = monitoring_service.get_alerts(level, resolved, limit)
        return alerts
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts",
        )


@router.get("/alerts/active", response_model=List[dict])
async def get_active_alerts(
    level: Optional[AlertLevel] = None,
    limit: int = 50,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    アクティブなアラートを取得
    """
    try:
        alerts = monitoring_service.get_alerts(level, resolved=False, limit=limit)
        return alerts
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active alerts",
        )


@router.post("/alerts/{alert_id}/resolve", response_model=dict)
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    アラートを解決済みにする（管理者のみ）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to resolve alerts",
        )

    try:
        success = monitoring_service.resolve_alert(alert_id)
        if success:
            return {"message": f"Alert {alert_id} resolved successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or already resolved",
            )
    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert",
        )


@router.get("/dashboard", response_model=dict)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    監視ダッシュボード用のデータを取得（管理者のみ）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access dashboard data",
        )

    try:
        # ヘルスステータス
        health_status = monitoring_service.get_health_status()

        # 最新のメトリクス
        system_metrics = monitoring_service.get_metrics(MetricType.SYSTEM, limit=10)
        application_metrics = monitoring_service.get_metrics(
            MetricType.APPLICATION, limit=10
        )
        business_metrics = monitoring_service.get_metrics(MetricType.BUSINESS, limit=10)

        # アクティブなアラート
        active_alerts = monitoring_service.get_alerts(resolved=False, limit=10)

        # ダッシュボードデータを構築
        dashboard_data = {
            "health_status": health_status,
            "metrics": {
                "system": system_metrics,
                "application": application_metrics,
                "business": business_metrics,
            },
            "alerts": {
                "active": active_alerts,
                "total_active": len(active_alerts),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data",
        )


@router.get("/stats", response_model=dict)
async def get_monitoring_stats(
    current_user: User = Depends(get_current_user),
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    監視統計情報を取得（管理者のみ）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access monitoring stats",
        )

    try:
        # メトリクス統計
        all_metrics = monitoring_service.get_metrics(limit=1000)

        # メトリクスタイプ別の統計
        metrics_by_type = {}
        for metric_type in MetricType:
            type_metrics = [m for m in all_metrics if m["type"] == metric_type.value]
            metrics_by_type[metric_type.value] = {
                "count": len(type_metrics),
                "latest": type_metrics[0] if type_metrics else None,
            }

        # アラート統計
        all_alerts = monitoring_service.get_alerts(limit=1000)
        alerts_by_level = {}
        for level in AlertLevel:
            level_alerts = [a for a in all_alerts if a["level"] == level.value]
            alerts_by_level[level.value] = {
                "total": len(level_alerts),
                "active": len([a for a in level_alerts if not a["resolved"]]),
                "resolved": len([a for a in level_alerts if a["resolved"]]),
            }

        # ヘルスチェック統計
        health_checks = monitoring_service.health_checks
        health_stats = {
            "total_checks": len(health_checks),
            "by_status": {},
        }

        for health_status_value in HealthStatus:
            status_checks = [
                h for h in health_checks if h.status == health_status_value
            ]
            health_stats["by_status"][health_status_value.value] = len(status_checks)

        stats = {
            "metrics": {
                "total": len(all_metrics),
                "by_type": metrics_by_type,
            },
            "alerts": {
                "total": len(all_alerts),
                "by_level": alerts_by_level,
            },
            "health_checks": health_stats,
            "monitoring_service": {
                "is_running": monitoring_service.is_running,
                "config": monitoring_service.config,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        return stats

    except Exception as e:
        logger.error(f"Failed to get monitoring stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monitoring stats",
        )


@router.post("/health-check", response_model=dict)
async def trigger_health_check(
    current_user: User = Depends(get_current_user),
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    手動でヘルスチェックを実行（管理者のみ）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to trigger health checks",
        )

    try:
        # 手動でヘルスチェックを実行
        await monitoring_service._perform_health_checks()

        # 最新のヘルスステータスを取得
        health_status = monitoring_service.get_health_status()

        return {
            "message": "Health check completed",
            "status": health_status,
        }

    except Exception as e:
        logger.error(f"Failed to trigger health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger health check",
        )


@router.get("/services", response_model=dict)
async def get_service_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    """
    各サービスのステータスを取得
    """
    try:
        health_status = monitoring_service.get_health_status()

        # サービス別の詳細情報を構築
        services = {}
        if "checks" in health_status:
            for service_name, check_data in health_status["checks"].items():
                services[service_name] = {
                    "status": check_data["status"],
                    "message": check_data["message"],
                    "response_time": check_data.get("response_time", 0),
                    "last_check": check_data["timestamp"],
                    "details": check_data.get("details", {}),
                }

        return {
            "services": services,
            "overall_status": health_status.get("status", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service status",
        )
