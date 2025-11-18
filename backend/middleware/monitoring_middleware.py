import time
from typing import Any, Callable, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logging import get_logger

logger = get_logger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """リクエスト/レスポンスの監視とメトリクス収集を行うミドルウェア"""

    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.response_times = []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """リクエストを処理し、メトリクスを収集"""
        start_time = time.time()

        # リクエスト情報を収集
        request_info = self._extract_request_info(request)

        try:
            # リクエストを処理
            response = await call_next(request)

            # レスポンス情報を収集
            response_time = time.time() - start_time
            response_info = self._extract_response_info(response, response_time)

            # メトリクスを記録
            await self._record_request_metrics(request_info, response_info)

            return response

        except Exception as e:
            # エラーを記録
            response_time = time.time() - start_time
            await self._record_error_metrics(request_info, str(e), response_time)
            raise

    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """リクエスト情報を抽出"""
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

    def _extract_response_info(
        self, response: Response, response_time: float
    ) -> Dict[str, Any]:
        """レスポンス情報を抽出"""
        return {
            "status_code": response.status_code,
            "response_time": response_time,
            "headers": dict(response.headers),
            "is_error": response.status_code >= 400,
            "is_success": 200 <= response.status_code < 300,
        }

    async def _record_request_metrics(
        self, request_info: Dict[str, Any], response_info: Dict[str, Any]
    ):
        """リクエストメトリクスを記録"""
        self.request_count += 1

        # レスポンス時間を記録
        self.response_times.append(response_info["response_time"])

        # レスポンス時間の履歴を保持（最新100件）
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]

        # エラーカウント
        if response_info["is_error"]:
            self.error_count += 1

        # ログ出力
        logger.info(
            f"{request_info['method']} {request_info['path']} "
            f"{response_info['status_code']} {response_info['response_time']:.3f}s"
        )

        # 監視サービスにメトリクスを送信
        await self._send_metrics_to_monitoring_service(request_info, response_info)

    async def _record_error_metrics(
        self, request_info: Dict[str, Any], error_message: str, response_time: float
    ):
        """エラーメトリクスを記録"""
        self.error_count += 1

        logger.error(
            f"Error in {request_info['method']} {request_info['path']}: "
            f"{error_message} ({response_time:.3f}s)"
        )

        # 監視サービスにエラーメトリクスを送信
        await self._send_error_metrics_to_monitoring_service(
            request_info, error_message, response_time
        )

    async def _send_metrics_to_monitoring_service(
        self, request_info: Dict[str, Any], response_info: Dict[str, Any]
    ):
        """監視サービスにメトリクスを送信"""
        try:
            from datetime import datetime

            from services.monitoring_service import Metric, MetricType

            # レスポンス時間メトリクス
            response_time_metric = Metric(
                name="api_response_time",
                value=response_info["response_time"],
                metric_type=MetricType.APPLICATION,
                timestamp=datetime.utcnow(),
                tags={
                    "method": request_info["method"],
                    "path": request_info["path"],
                    "status_code": str(response_info["status_code"]),
                },
            )

            # リクエスト数メトリクス
            request_count_metric = Metric(
                name="api_request_count",
                value=1,
                metric_type=MetricType.APPLICATION,
                timestamp=datetime.utcnow(),
                tags={
                    "method": request_info["method"],
                    "path": request_info["path"],
                },
            )

            # メトリクスを監視サービスに追加（グローバルインスタンスを使用）
            from services.monitoring_service import _monitoring_service_instance

            if _monitoring_service_instance:
                _monitoring_service_instance.metrics.extend(
                    [response_time_metric, request_count_metric]
                )

        except Exception as e:
            logger.error(f"Failed to send metrics to monitoring service: {e}")

    async def _send_error_metrics_to_monitoring_service(
        self, request_info: Dict[str, Any], error_message: str, response_time: float
    ):
        """監視サービスにエラーメトリクスを送信"""
        try:
            from datetime import datetime

            from services.monitoring_service import (
                Alert,
                AlertLevel,
                Metric,
                MetricType,
            )

            # エラー数メトリクス
            error_count_metric = Metric(
                name="api_error_count",
                value=1,
                metric_type=MetricType.APPLICATION,
                timestamp=datetime.utcnow(),
                tags={
                    "method": request_info["method"],
                    "path": request_info["path"],
                    "error": error_message[:100],  # エラーメッセージを短縮
                },
            )

            # メトリクスを監視サービスに追加（グローバルインスタンスを使用）
            from services.monitoring_service import _monitoring_service_instance

            if _monitoring_service_instance:
                _monitoring_service_instance.metrics.append(error_count_metric)

                # エラー率が高い場合はアラートを作成
                error_rate = self.error_count / max(self.request_count, 1) * 100
                if error_rate > 5.0:  # エラー率が5%を超えた場合
                    alert = Alert(
                        id=f"high_error_rate_{int(time.time())}",
                        level=AlertLevel.WARNING,
                        title="High API Error Rate",
                        message=f"API error rate is {error_rate:.1f}% ({self.error_count}/{self.request_count})",
                        service="api",
                        timestamp=datetime.utcnow(),
                    )
                    _monitoring_service_instance.alerts.append(alert)

        except Exception as e:
            logger.error(f"Failed to send error metrics to monitoring service: {e}")

    def get_request_stats(self) -> Dict[str, Any]:
        """リクエスト統計を取得"""
        if not self.response_times:
            return {
                "total_requests": self.request_count,
                "error_count": self.error_count,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
            }

        return {
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count) * 100,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
        }
