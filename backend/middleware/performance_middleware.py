"""
Performance Middleware for AICA-SyS
Phase 7-3: API response optimization
"""

import asyncio
import logging
import os
import time
from collections import defaultdict, deque
from typing import Any, Callable, Dict

import psutil
from fastapi import Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """パフォーマンスメトリクスを管理するクラス"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.response_times = deque(maxlen=max_history)
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.endpoint_times = defaultdict(list)
        self.memory_usage = deque(maxlen=max_history)
        self.cpu_usage = deque(maxlen=max_history)
        
    def record_response_time(self, endpoint: str, response_time: float):
        """レスポンス時間を記録"""
        self.response_times.append(response_time)
        self.endpoint_times[endpoint].append(response_time)
        if len(self.endpoint_times[endpoint]) > self.max_history:
            self.endpoint_times[endpoint] = self.endpoint_times[endpoint][-self.max_history:]
    
    def record_request(self, endpoint: str):
        """リクエスト数を記録"""
        self.request_counts[endpoint] += 1
    
    def record_error(self, endpoint: str, status_code: int):
        """エラー数を記録"""
        self.error_counts[f"{endpoint}:{status_code}"] += 1
    
    def record_system_metrics(self):
        """システムメトリクスを記録"""
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        if not self.response_times:
            return {
                "total_requests": 0,
                "average_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "p95_response_time": 0,
                "error_rate": 0,
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
            }
        
        response_times = list(self.response_times)
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_requests": total_requests,
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": self._calculate_percentile(response_times, 95),
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "memory_usage_mb": list(self.memory_usage)[-1] if self.memory_usage else 0,
            "cpu_usage_percent": list(self.cpu_usage)[-1] if self.cpu_usage else 0,
            "endpoint_stats": self._get_endpoint_stats(),
        }
    
    def _calculate_percentile(self, data: list, percentile: int) -> float:
        """パーセンタイルを計算"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """エンドポイント別の統計を取得"""
        stats = {}
        for endpoint, times in self.endpoint_times.items():
            if times:
                stats[endpoint] = {
                    "count": self.request_counts.get(endpoint, 0),
                    "average_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "p95_time": self._calculate_percentile(times, 95),
                }
        return stats

# グローバルメトリクスインスタンス
performance_metrics = PerformanceMetrics()

class PerformanceMiddleware:
    """パフォーマンス測定ミドルウェア"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        self.app = app
        self.max_request_size = max_request_size
    
    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # リクエストサイズチェック
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            response = JSONResponse(
                status_code=413,
                content={"error": "Request too large", "max_size": self.max_request_size}
            )
            await response(scope, receive, send)
            return
        
        # エンドポイント名を取得
        endpoint = f"{request.method} {request.url.path}"
        
        # リクエスト数を記録
        performance_metrics.record_request(endpoint)
        
        # レスポンスを処理
        response_sent = False
        response_status = 200
        
        async def send_wrapper(message):
            nonlocal response_sent, response_status
            
            if message["type"] == "http.response.start":
                response_status = message["status"]
                
                # レスポンス時間を計算
                response_time = time.time() - start_time
                performance_metrics.record_response_time(endpoint, response_time)
                
                # エラーを記録
                if response_status >= 400:
                    performance_metrics.record_error(endpoint, response_status)
                
                # システムメトリクスを記録
                performance_metrics.record_system_metrics()
                
                # パフォーマンスヘッダーを追加
                message["headers"].append([b"x-response-time", str(response_time).encode()])
                message["headers"].append([b"x-request-id", str(int(start_time * 1000)).encode()])
                
                response_sent = True
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            if not response_sent:
                performance_metrics.record_error(endpoint, 500)
                logger.error(f"Error in endpoint {endpoint}: {e}")
            raise

class RequestSizeMiddleware:
    """リクエストサイズ制限ミドルウェア"""
    
    def __init__(self, max_size: int = 10 * 1024 * 1024):  # 10MB
        self.max_size = max_size
    
    async def __call__(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > self.max_size:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Request too large",
                    "max_size": self.max_size,
                    "received_size": int(content_length)
                }
            )
        
        return await call_next(request)

class CompressionMiddleware:
    """圧縮ミドルウェア"""
    
    def __init__(self, min_size: int = 1024):  # 1KB
        self.min_size = min_size
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # レスポンスサイズをチェック
        if hasattr(response, 'body') and len(response.body) > self.min_size:
            # gzip圧縮を適用
            import gzip
            compressed_body = gzip.compress(response.body)
            response.body = compressed_body
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed_body))
        
        return response

class CacheHeadersMiddleware:
    """キャッシュヘッダーミドルウェア"""
    
    def __init__(self):
        self.cache_rules = {
            "/api/static/": {"cache_control": "public, max-age=31536000, immutable"},
            "/api/articles": {"cache_control": "public, max-age=300, s-maxage=600"},
            "/api/trends": {"cache_control": "public, max-age=600, s-maxage=1200"},
            "/api/newsletters": {"cache_control": "public, max-age=1800, s-maxage=3600"},
            "/api/health": {"cache_control": "no-cache, no-store, must-revalidate"},
        }
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # パスに基づいてキャッシュヘッダーを設定
        for path_pattern, headers in self.cache_rules.items():
            if request.url.path.startswith(path_pattern):
                for header_name, header_value in headers.items():
                    response.headers[header_name.replace("_", "-")] = header_value
                break
        
        return response

class RateLimitMiddleware:
    """レート制限ミドルウェア"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # 古いリクエストを削除
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # リクエスト数をチェック
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "retry_after": self.window_seconds
                }
            )
        
        # リクエストを記録
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)

# ミドルウェアの設定関数
def setup_performance_middleware(app):
    """パフォーマンスミドルウェアを設定"""
    
    # レート制限ミドルウェア
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    
    # リクエストサイズ制限ミドルウェア
    app.add_middleware(RequestSizeMiddleware, max_size=10 * 1024 * 1024)
    
    # キャッシュヘッダーミドルウェア
    app.add_middleware(CacheHeadersMiddleware)
    
    # 圧縮ミドルウェア
    app.add_middleware(CompressionMiddleware, min_size=1024)
    
    # パフォーマンス測定ミドルウェア
    app.add_middleware(PerformanceMiddleware, max_request_size=10 * 1024 * 1024)
    
    return app

# パフォーマンス統計取得エンドポイント
def get_performance_stats():
    """パフォーマンス統計を取得"""
    return performance_metrics.get_stats()

# パフォーマンス統計リセット
def reset_performance_stats():
    """パフォーマンス統計をリセット"""
    global performance_metrics
    performance_metrics = PerformanceMetrics()