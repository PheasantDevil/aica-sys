"""
Performance Monitoring Middleware
API パフォーマンスの監視とログ記録
"""

import time
import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
import asyncio
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """パフォーマンスメトリクス管理クラス"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_times = deque(maxlen=max_history)
        self.response_sizes = deque(maxlen=max_history)
        self.status_codes = defaultdict(int)
        self.endpoint_times = defaultdict(list)
        self.error_count = 0
        self.total_requests = 0
        self.start_time = time.time()
    
    def record_request(self, 
                      endpoint: str, 
                      method: str, 
                      response_time: float, 
                      status_code: int, 
                      response_size: int):
        """リクエスト情報を記録"""
        self.total_requests += 1
        self.request_times.append(response_time)
        self.response_sizes.append(response_size)
        self.status_codes[status_code] += 1
        self.endpoint_times[f"{method} {endpoint}"].append(response_time)
        
        if status_code >= 400:
            self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        if not self.request_times:
            return {}
        
        request_times_list = list(self.request_times)
        response_sizes_list = list(self.response_sizes)
        
        # 平均レスポンス時間
        avg_response_time = sum(request_times_list) / len(request_times_list)
        
        # 95パーセンタイル
        sorted_times = sorted(request_times_list)
        p95_index = int(len(sorted_times) * 0.95)
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        
        # 平均レスポンスサイズ
        avg_response_size = sum(response_sizes_list) / len(response_sizes_list)
        
        # エラー率
        error_rate = (self.error_count / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # システムリソース
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "total_requests": self.total_requests,
            "avg_response_time": round(avg_response_time, 3),
            "p95_response_time": round(p95_response_time, 3),
            "avg_response_size": round(avg_response_size, 0),
            "error_rate": round(error_rate, 2),
            "status_codes": dict(self.status_codes),
            "uptime": round(time.time() - self.start_time, 2),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
            },
            "endpoints": {
                endpoint: {
                    "count": len(times),
                    "avg_time": round(sum(times) / len(times), 3),
                    "max_time": round(max(times), 3),
                    "min_time": round(min(times), 3),
                }
                for endpoint, times in self.endpoint_times.items()
            }
        }

# グローバルメトリクスインスタンス
metrics = PerformanceMetrics()

class PerformanceMiddleware(BaseHTTPMiddleware):
    """パフォーマンス監視ミドルウェア"""
    
    def __init__(self, app, enable_logging: bool = True):
        super().__init__(app)
        self.enable_logging = enable_logging
        self.slow_request_threshold = float(os.getenv("SLOW_REQUEST_THRESHOLD", "1.0"))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """リクエスト処理とパフォーマンス測定"""
        start_time = time.time()
        
        # リクエスト情報の取得
        method = request.method
        url = request.url
        endpoint = url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # リクエストサイズの取得
        request_size = 0
        if hasattr(request, "_body"):
            request_size = len(request._body)
        
        try:
            # リクエスト処理
            response = await call_next(request)
            
            # 処理時間の計算
            process_time = time.time() - start_time
            
            # レスポンスサイズの取得
            response_size = 0
            if hasattr(response, "body"):
                response_size = len(response.body)
            
            # メトリクスの記録
            metrics.record_request(
                endpoint=endpoint,
                method=method,
                response_time=process_time,
                status_code=response.status_code,
                response_size=response_size
            )
            
            # レスポンスヘッダーにパフォーマンス情報を追加
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            response.headers["X-Request-ID"] = f"{int(time.time() * 1000)}-{hash(endpoint) % 10000}"
            
            # ログ記録
            if self.enable_logging:
                self._log_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=response.status_code,
                    process_time=process_time,
                    request_size=request_size,
                    response_size=response_size,
                    client_ip=client_ip
                )
            
            # スローレスポンスの警告
            if process_time > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {method} {endpoint} "
                    f"took {process_time:.3f}s (threshold: {self.slow_request_threshold}s)"
                )
            
            return response
            
        except Exception as e:
            # エラー処理
            process_time = time.time() - start_time
            error_status = 500
            
            # エラーメトリクスの記録
            metrics.record_request(
                endpoint=endpoint,
                method=method,
                response_time=process_time,
                status_code=error_status,
                response_size=0
            )
            
            # エラーログ
            logger.error(
                f"Request error: {method} {endpoint} "
                f"failed after {process_time:.3f}s - {str(e)}"
            )
            
            raise
    
    def _log_request(self, 
                    method: str, 
                    endpoint: str, 
                    status_code: int, 
                    process_time: float,
                    request_size: int,
                    response_size: int,
                    client_ip: str):
        """リクエストログの出力"""
        log_level = "INFO"
        if status_code >= 400:
            log_level = "ERROR"
        elif status_code >= 300:
            log_level = "WARNING"
        
        log_message = (
            f"{method} {endpoint} {status_code} "
            f"{process_time:.3f}s "
            f"req:{request_size}B res:{response_size}B "
            f"ip:{client_ip}"
        )
        
        if log_level == "ERROR":
            logger.error(log_message)
        elif log_level == "WARNING":
            logger.warning(log_message)
        else:
            logger.info(log_message)

class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self):
        self.metrics = metrics
        self.alerts = []
        self.alert_thresholds = {
            "response_time": 2.0,  # 2秒
            "error_rate": 5.0,     # 5%
            "cpu_percent": 80.0,   # 80%
            "memory_percent": 85.0, # 85%
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """現在のメトリクスを取得"""
        return self.metrics.get_stats()
    
    def check_alerts(self) -> list:
        """アラートの確認"""
        stats = self.get_metrics()
        current_alerts = []
        
        # レスポンス時間のアラート
        if stats.get("avg_response_time", 0) > self.alert_thresholds["response_time"]:
            current_alerts.append({
                "type": "high_response_time",
                "message": f"Average response time is {stats['avg_response_time']:.2f}s",
                "value": stats["avg_response_time"],
                "threshold": self.alert_thresholds["response_time"]
            })
        
        # エラー率のアラート
        if stats.get("error_rate", 0) > self.alert_thresholds["error_rate"]:
            current_alerts.append({
                "type": "high_error_rate",
                "message": f"Error rate is {stats['error_rate']:.2f}%",
                "value": stats["error_rate"],
                "threshold": self.alert_thresholds["error_rate"]
            })
        
        # CPU使用率のアラート
        system_stats = stats.get("system", {})
        if system_stats.get("cpu_percent", 0) > self.alert_thresholds["cpu_percent"]:
            current_alerts.append({
                "type": "high_cpu_usage",
                "message": f"CPU usage is {system_stats['cpu_percent']:.1f}%",
                "value": system_stats["cpu_percent"],
                "threshold": self.alert_thresholds["cpu_percent"]
            })
        
        # メモリ使用率のアラート
        if system_stats.get("memory_percent", 0) > self.alert_thresholds["memory_percent"]:
            current_alerts.append({
                "type": "high_memory_usage",
                "message": f"Memory usage is {system_stats['memory_percent']:.1f}%",
                "value": system_stats["memory_percent"],
                "threshold": self.alert_thresholds["memory_percent"]
            })
        
        self.alerts = current_alerts
        return current_alerts
    
    def get_health_status(self) -> Dict[str, Any]:
        """ヘルスステータスの取得"""
        stats = self.get_metrics()
        alerts = self.check_alerts()
        
        # ヘルススコアの計算
        health_score = 100
        for alert in alerts:
            if alert["type"] == "high_response_time":
                health_score -= 20
            elif alert["type"] == "high_error_rate":
                health_score -= 30
            elif alert["type"] == "high_cpu_usage":
                health_score -= 15
            elif alert["type"] == "high_memory_usage":
                health_score -= 15
        
        health_score = max(0, health_score)
        
        return {
            "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
            "score": health_score,
            "alerts": alerts,
            "metrics": stats
        }

# グローバル監視インスタンス
performance_monitor = PerformanceMonitor()
