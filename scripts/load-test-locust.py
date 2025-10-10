"""
Locust Load Testing Script
Phase 7-5: Load testing and scalability verification
"""

import json
import random
import time
from datetime import datetime
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner

# グローバル統計
stats = {
    "start_time": None,
    "end_time": None,
    "total_requests": 0,
    "failed_requests": 0,
    "response_times": [],
    "error_types": {},
}


class APIUser(HttpUser):
    """API負荷テスト用のユーザークラス"""
    
    # リクエスト間の待機時間（1-3秒のランダム）
    wait_time = between(1, 3)
    
    # ベースURL
    host = "http://127.0.0.1:8000"
    
    def on_start(self):
        """テスト開始時の初期化"""
        if stats["start_time"] is None:
            stats["start_time"] = datetime.now()
    
    @task(40)
    def get_articles(self):
        """記事一覧取得（40%の重み）"""
        with self.client.get(
            "/api/content/articles",
            catch_response=True,
            name="GET /api/content/articles"
        ) as response:
            self._handle_response(response, "articles")
    
    @task(30)
    def get_trends(self):
        """トレンド取得（30%の重み）"""
        with self.client.get(
            "/api/content/trends",
            catch_response=True,
            name="GET /api/content/trends"
        ) as response:
            self._handle_response(response, "trends")
    
    @task(20)
    def get_newsletters(self):
        """ニュースレター取得（20%の重み）"""
        with self.client.get(
            "/api/content/newsletters",
            catch_response=True,
            name="GET /api/content/newsletters"
        ) as response:
            self._handle_response(response, "newsletters")
    
    @task(15)
    def get_optimized_articles(self):
        """最適化された記事取得（15%の重み）"""
        with self.client.get(
            "/api/optimized/articles",
            catch_response=True,
            name="GET /api/optimized/articles"
        ) as response:
            self._handle_response(response, "optimized_articles")
    
    @task(10)
    def get_optimized_dashboard(self):
        """最適化されたダッシュボード取得（10%の重み）"""
        with self.client.get(
            "/api/optimized/dashboard",
            catch_response=True,
            name="GET /api/optimized/dashboard"
        ) as response:
            self._handle_response(response, "optimized_dashboard")
    
    @task(8)
    def get_articles_with_filters(self):
        """フィルター付き記事取得（8%の重み）"""
        params = {
            "skip": random.randint(0, 100),
            "limit": random.choice([10, 20, 50]),
        }
        
        with self.client.get(
            "/api/content/articles",
            params=params,
            catch_response=True,
            name="GET /api/content/articles (filtered)"
        ) as response:
            self._handle_response(response, "articles_filtered")
    
    @task(5)
    def get_health(self):
        """ヘルスチェック（5%の重み）"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="GET /health"
        ) as response:
            self._handle_response(response, "health")
    
    @task(3)
    def get_performance_stats(self):
        """パフォーマンス統計取得（3%の重み）"""
        with self.client.get(
            "/api/optimized/performance/stats",
            catch_response=True,
            name="GET /api/optimized/performance/stats"
        ) as response:
            self._handle_response(response, "performance_stats")
    
    def _handle_response(self, response, endpoint_name):
        """レスポンスハンドリング共通処理"""
        stats["total_requests"] += 1
        
        if response.status_code == 200:
            # 成功時のレスポンス時間を記録
            response_time = response.elapsed.total_seconds() * 1000
            stats["response_times"].append(response_time)
            
            # レスポンス時間が長い場合は警告
            if response_time > 1000:
                response.failure(f"Response time too high: {response_time:.2f}ms")
            else:
                response.success()
        else:
            # エラー時の記録
            stats["failed_requests"] += 1
            error_type = f"{endpoint_name}_{response.status_code}"
            stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
            response.failure(f"Got status code {response.status_code}")


class HighLoadUser(HttpUser):
    """高負荷テスト用のユーザークラス"""
    
    # より短い待機時間（0.5-1.5秒）
    wait_time = between(0.5, 1.5)
    host = "http://127.0.0.1:8000"
    
    @task(50)
    def rapid_article_requests(self):
        """高頻度の記事リクエスト"""
        self.client.get("/api/content/articles")
    
    @task(30)
    def rapid_optimized_requests(self):
        """高頻度の最適化リクエスト"""
        self.client.get("/api/optimized/articles")
    
    @task(20)
    def rapid_dashboard_requests(self):
        """高頻度のダッシュボードリクエスト"""
        self.client.get("/api/optimized/dashboard")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """テスト開始時のイベント"""
    print("\n" + "="*80)
    print("🚀 Load Testing Started")
    print("="*80)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.parsed_options.num_users if hasattr(environment, 'parsed_options') else 'N/A'}")
    print(f"Spawn Rate: {environment.parsed_options.spawn_rate if hasattr(environment, 'parsed_options') else 'N/A'}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """テスト終了時のイベント"""
    stats["end_time"] = datetime.now()
    
    print("\n" + "="*80)
    print("🏁 Load Testing Completed")
    print("="*80)
    
    # 統計情報の出力
    if stats["response_times"]:
        avg_response_time = sum(stats["response_times"]) / len(stats["response_times"])
        sorted_times = sorted(stats["response_times"])
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        print(f"\n📊 Statistics:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Failed Requests: {stats['failed_requests']}")
        print(f"  Success Rate: {(stats['total_requests'] - stats['failed_requests']) / stats['total_requests'] * 100:.2f}%")
        print(f"  Avg Response Time: {avg_response_time:.2f}ms")
        print(f"  Min Response Time: {min(stats['response_times']):.2f}ms")
        print(f"  Max Response Time: {max(stats['response_times']):.2f}ms")
        print(f"  P95 Response Time: {sorted_times[p95_index]:.2f}ms")
        print(f"  P99 Response Time: {sorted_times[p99_index]:.2f}ms")
        
        if stats["error_types"]:
            print(f"\n❌ Error Types:")
            for error_type, count in stats["error_types"].items():
                print(f"  {error_type}: {count}")
    
    # テスト結果をJSONファイルに保存
    test_duration = (stats["end_time"] - stats["start_time"]).total_seconds()
    
    report = {
        "test_id": f"locust-{stats['start_time'].strftime('%Y%m%d-%H%M%S')}",
        "test_type": "load_test",
        "start_time": stats["start_time"].isoformat(),
        "end_time": stats["end_time"].isoformat(),
        "duration_seconds": test_duration,
        "results": {
            "total_requests": stats["total_requests"],
            "failed_requests": stats["failed_requests"],
            "success_rate": (stats["total_requests"] - stats["failed_requests"]) / stats["total_requests"] * 100 if stats["total_requests"] > 0 else 0,
            "requests_per_second": stats["total_requests"] / test_duration if test_duration > 0 else 0,
        },
        "response_times": {
            "average": sum(stats["response_times"]) / len(stats["response_times"]) if stats["response_times"] else 0,
            "min": min(stats["response_times"]) if stats["response_times"] else 0,
            "max": max(stats["response_times"]) if stats["response_times"] else 0,
        },
        "errors": stats["error_types"],
    }
    
    with open(f"locust-results-{stats['start_time'].strftime('%Y%m%d-%H%M%S')}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Results saved to: locust-results-{stats['start_time'].strftime('%Y%m%d-%H%M%S')}.json")
    print("="*80 + "\n")


# コマンドライン実行用
if __name__ == "__main__":
    import os
    os.system("locust -f load-test-locust.py --host=http://127.0.0.1:8000")
