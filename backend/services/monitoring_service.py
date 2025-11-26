import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import aiohttp
import asyncpg
import psutil
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from utils.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    SECURITY = "security"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    service: str
    status: HealthStatus
    response_time: float
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class Metric:
    name: str
    value: Union[int, float, str]
    metric_type: MetricType
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None


@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    service: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class MonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.health_checks: List[HealthCheck] = []
        self.is_running = False

        # 監視設定
        self.config = {
            "health_check_interval": 30,  # 秒
            "metrics_collection_interval": 60,  # 秒
            "alert_check_interval": 10,  # 秒
            "retention_days": 30,
        }

        # アラート閾値
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 5.0,
            "error_rate": 5.0,
        }

    async def start_monitoring(self):
        """監視サービスを開始"""
        if self.is_running:
            logger.warning("Monitoring service is already running")
            return

        self.is_running = True
        logger.info("Starting monitoring service")

        # 並行して監視タスクを実行
        tasks = [
            self._health_check_loop(),
            self._metrics_collection_loop(),
            self._alert_check_loop(),
        ]

        await asyncio.gather(*tasks)

    async def stop_monitoring(self):
        """監視サービスを停止"""
        self.is_running = False
        logger.info("Stopping monitoring service")

    async def _health_check_loop(self):
        """ヘルスチェックループ"""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config["health_check_interval"])
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)

    async def _metrics_collection_loop(self):
        """メトリクス収集ループ"""
        while self.is_running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.config["metrics_collection_interval"])
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(5)

    async def _alert_check_loop(self):
        """アラートチェックループ"""
        while self.is_running:
            try:
                await self._check_alerts()
                await asyncio.sleep(self.config["alert_check_interval"])
            except Exception as e:
                logger.error(f"Alert check loop error: {e}")
                await asyncio.sleep(5)

    async def _perform_health_checks(self):
        """ヘルスチェックを実行"""
        checks = [
            self._check_api_health(),
            self._check_database_health(),
            self._check_external_services(),
            self._check_system_resources(),
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check failed: {result}")
            else:
                self.health_checks.append(result)

    async def _check_api_health(self) -> HealthCheck:
        """API ヘルスチェック"""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://127.0.0.1:8000/health",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        status = HealthStatus.HEALTHY
                        message = "API is healthy"
                    else:
                        status = HealthStatus.WARNING
                        message = f"API returned status {response.status}"
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus.CRITICAL
            message = f"API health check failed: {str(e)}"

        return HealthCheck(
            service="api",
            status=status,
            response_time=response_time,
            message=message,
            timestamp=datetime.utcnow(),
        )

    async def _check_database_health(self) -> HealthCheck:
        """データベースヘルスチェック"""
        start_time = time.time()
        try:
            # 簡単なクエリでデータベース接続をテスト
            result = self.db.execute("SELECT 1").fetchone()
            response_time = time.time() - start_time

            if result:
                status = HealthStatus.HEALTHY
                message = "Database is healthy"
            else:
                status = HealthStatus.WARNING
                message = "Database query returned no result"
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus.CRITICAL
            message = f"Database health check failed: {str(e)}"

        return HealthCheck(
            service="database",
            status=status,
            response_time=response_time,
            message=message,
            timestamp=datetime.utcnow(),
        )

    async def _check_external_services(self) -> HealthCheck:
        """外部サービスヘルスチェック"""
        services = {
            "supabase": os.getenv("SUPABASE_URL"),
            "stripe": "https://api.stripe.com/v1/account",
            "openai": "https://api.openai.com/v1/models",
        }

        healthy_services = 0
        total_services = len(services)

        for service_name, url in services.items():
            if not url:
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status in [
                            200,
                            401,
                            403,
                        ]:  # 401/403も正常（認証エラーは正常）
                            healthy_services += 1
            except Exception:
                pass

        if healthy_services == total_services:
            status = HealthStatus.HEALTHY
            message = f"All external services are healthy ({healthy_services}/{total_services})"
        elif healthy_services > 0:
            status = HealthStatus.WARNING
            message = f"Some external services are unhealthy ({healthy_services}/{total_services})"
        else:
            status = HealthStatus.CRITICAL
            message = "All external services are unhealthy"

        return HealthCheck(
            service="external_services",
            status=status,
            response_time=0.0,
            message=message,
            timestamp=datetime.utcnow(),
            details={
                "healthy_services": healthy_services,
                "total_services": total_services,
            },
        )

    async def _check_system_resources(self) -> HealthCheck:
        """システムリソースヘルスチェック"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # 最も厳しい条件でステータスを決定
        if (
            cpu_percent > self.thresholds["cpu_usage"]
            or memory.percent > self.thresholds["memory_usage"]
            or disk.percent > self.thresholds["disk_usage"]
        ):
            status = HealthStatus.CRITICAL
            message = "System resources are critically high"
        elif (
            cpu_percent > self.thresholds["cpu_usage"] * 0.8
            or memory.percent > self.thresholds["memory_usage"] * 0.8
            or disk.percent > self.thresholds["disk_usage"] * 0.8
        ):
            status = HealthStatus.WARNING
            message = "System resources are high"
        else:
            status = HealthStatus.HEALTHY
            message = "System resources are healthy"

        return HealthCheck(
            service="system_resources",
            status=status,
            response_time=0.0,
            message=message,
            timestamp=datetime.utcnow(),
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
            },
        )

    async def _collect_metrics(self):
        """メトリクスを収集"""
        # システムメトリクス
        await self._collect_system_metrics()

        # アプリケーションメトリクス
        await self._collect_application_metrics()

        # ビジネスメトリクス
        await self._collect_business_metrics()

    async def _collect_system_metrics(self):
        """システムメトリクスを収集"""
        timestamp = datetime.utcnow()

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.append(
            Metric(
                name="cpu_usage_percent",
                value=cpu_percent,
                metric_type=MetricType.SYSTEM,
                timestamp=timestamp,
            )
        )

        # メモリ使用率
        memory = psutil.virtual_memory()
        self.metrics.append(
            Metric(
                name="memory_usage_percent",
                value=memory.percent,
                metric_type=MetricType.SYSTEM,
                timestamp=timestamp,
            )
        )

        # ディスク使用率
        disk = psutil.disk_usage("/")
        self.metrics.append(
            Metric(
                name="disk_usage_percent",
                value=disk.percent,
                metric_type=MetricType.SYSTEM,
                timestamp=timestamp,
            )
        )

        # ネットワーク使用量
        network = psutil.net_io_counters()
        self.metrics.append(
            Metric(
                name="network_bytes_sent",
                value=network.bytes_sent,
                metric_type=MetricType.SYSTEM,
                timestamp=timestamp,
            )
        )
        self.metrics.append(
            Metric(
                name="network_bytes_recv",
                value=network.bytes_recv,
                metric_type=MetricType.SYSTEM,
                timestamp=timestamp,
            )
        )

    async def _collect_application_metrics(self):
        """アプリケーションメトリクスを収集"""
        timestamp = datetime.utcnow()

        # アクティブユーザー数
        try:
            active_users = self.db.query(User).filter(User.is_active == True).count()
            self.metrics.append(
                Metric(
                    name="active_users_count",
                    value=active_users,
                    metric_type=MetricType.APPLICATION,
                    timestamp=timestamp,
                )
            )
        except Exception as e:
            logger.error(f"Failed to collect active users metric: {e}")

        # データベース接続数
        try:
            # SQLAlchemyの接続プール情報を取得
            pool = self.db.bind.pool
            self.metrics.append(
                Metric(
                    name="db_connections_active",
                    value=pool.size(),
                    metric_type=MetricType.APPLICATION,
                    timestamp=timestamp,
                )
            )
            self.metrics.append(
                Metric(
                    name="db_connections_checked_out",
                    value=pool.checkedout(),
                    metric_type=MetricType.APPLICATION,
                    timestamp=timestamp,
                )
            )
        except Exception as e:
            logger.error(f"Failed to collect database connection metrics: {e}")

    async def _collect_business_metrics(self):
        """ビジネスメトリクスを収集"""
        timestamp = datetime.utcnow()

        try:
            # 総ユーザー数
            total_users = self.db.query(User).count()
            self.metrics.append(
                Metric(
                    name="total_users_count",
                    value=total_users,
                    metric_type=MetricType.BUSINESS,
                    timestamp=timestamp,
                )
            )

            # 今日の新規ユーザー数
            today = datetime.utcnow().date()
            new_users_today = (
                self.db.query(User).filter(User.created_at >= today).count()
            )
            self.metrics.append(
                Metric(
                    name="new_users_today",
                    value=new_users_today,
                    metric_type=MetricType.BUSINESS,
                    timestamp=timestamp,
                )
            )

        except Exception as e:
            logger.error(f"Failed to collect business metrics: {e}")

    async def _check_alerts(self):
        """アラート条件をチェック"""
        # 最新のメトリクスをチェック
        recent_metrics = [
            m
            for m in self.metrics
            if m.timestamp > datetime.utcnow() - timedelta(minutes=5)
        ]

        for metric in recent_metrics:
            await self._evaluate_alert_conditions(metric)

    async def _evaluate_alert_conditions(self, metric: Metric):
        """メトリクスに基づいてアラート条件を評価"""
        alert_conditions = {
            "cpu_usage_percent": (self.thresholds["cpu_usage"], AlertLevel.CRITICAL),
            "memory_usage_percent": (
                self.thresholds["memory_usage"],
                AlertLevel.CRITICAL,
            ),
            "disk_usage_percent": (self.thresholds["disk_usage"], AlertLevel.CRITICAL),
        }

        if metric.name in alert_conditions:
            threshold, level = alert_conditions[metric.name]

            if isinstance(metric.value, (int, float)) and metric.value > threshold:
                await self._create_alert(
                    level=level,
                    title=f"High {metric.name}",
                    message=f"{metric.name} is {metric.value}%, exceeding threshold of {threshold}%",
                    service=metric.name,
                )

    async def _create_alert(
        self, level: AlertLevel, title: str, message: str, service: str
    ):
        """アラートを作成"""
        alert_id = f"{service}_{int(time.time())}"

        # 既存のアラートと重複チェック
        existing_alert = next(
            (
                a
                for a in self.alerts
                if a.service == service and a.title == title and not a.resolved
            ),
            None,
        )

        if existing_alert:
            return  # 既存のアラートがある場合は新規作成しない

        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            service=service,
            timestamp=datetime.utcnow(),
        )

        self.alerts.append(alert)
        logger.warning(f"Alert created: {title} - {message}")

        # アラート通知を送信
        await self._send_alert_notification(alert)

    async def _send_alert_notification(self, alert: Alert):
        """アラート通知を送信"""
        # ここで実際の通知（Email、Slack、Webhook等）を実装
        logger.info(f"Sending alert notification: {alert.title}")

        # 例: Webhook通知
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if webhook_url:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        webhook_url,
                        json={
                            "level": alert.level.value,
                            "title": alert.title,
                            "message": alert.message,
                            "service": alert.service,
                            "timestamp": alert.timestamp.isoformat(),
                        },
                        timeout=aiohttp.ClientTimeout(total=10),
                    )
            except Exception as e:
                logger.error(f"Failed to send webhook notification: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """現在のヘルスステータスを取得"""
        if not self.health_checks:
            return {"status": "unknown", "message": "No health checks available"}

        # 最新のヘルスチェック結果を取得
        latest_checks = {}
        for check in self.health_checks:
            latest_checks[check.service] = check

        # 全体のステータスを決定
        statuses = [check.status for check in latest_checks.values()]

        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "status": overall_status.value,
            "checks": {
                service: {
                    "status": check.status.value,
                    "response_time": check.response_time,
                    "message": check.message,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details,
                }
                for service, check in latest_checks.items()
            },
        }

    def get_metrics(
        self, metric_type: Optional[MetricType] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """メトリクスを取得"""
        filtered_metrics = self.metrics

        if metric_type:
            filtered_metrics = [
                m for m in filtered_metrics if m.metric_type == metric_type
            ]

        # 最新のメトリクスを返す
        filtered_metrics.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                "name": metric.name,
                "value": metric.value,
                "type": metric.metric_type.value,
                "timestamp": metric.timestamp.isoformat(),
                "tags": metric.tags,
            }
            for metric in filtered_metrics[:limit]
        ]

    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        resolved: Optional[bool] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """アラートを取得"""
        filtered_alerts = self.alerts

        if level:
            filtered_alerts = [a for a in filtered_alerts if a.level == level]

        if resolved is not None:
            filtered_alerts = [a for a in filtered_alerts if a.resolved == resolved]

        # 最新のアラートを返す
        filtered_alerts.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "service": alert.service,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": (
                    alert.resolved_at.isoformat() if alert.resolved_at else None
                ),
            }
            for alert in filtered_alerts[:limit]
        ]

    def resolve_alert(self, alert_id: str) -> bool:
        """アラートを解決済みにする"""
        alert = next((a for a in self.alerts if a.id == alert_id), None)

        if alert and not alert.resolved:
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            logger.info(f"Alert {alert_id} resolved")
            return True

        return False


# グローバルな監視サービスインスタンス
_monitoring_service_instance: Optional[MonitoringService] = None


def get_monitoring_service(db: Session = Depends(get_db)) -> MonitoringService:
    """監視サービスインスタンスを取得"""
    global _monitoring_service_instance
    if _monitoring_service_instance is None:
        _monitoring_service_instance = MonitoringService(db)
    return _monitoring_service_instance


async def start_monitoring_service():
    """監視サービスを開始（アプリケーション起動時に呼び出し）"""
    global _monitoring_service_instance  # noqa: F824
    if _monitoring_service_instance and not _monitoring_service_instance.is_running:
        await _monitoring_service_instance.start_monitoring()


async def stop_monitoring_service():
    """監視サービスを停止（アプリケーション終了時に呼び出し）"""
    global _monitoring_service_instance  # noqa: F824
    if _monitoring_service_instance and _monitoring_service_instance.is_running:
        await _monitoring_service_instance.stop_monitoring()
