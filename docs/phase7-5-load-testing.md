# Phase 7-5: 負荷テストとスケーラビリティ検証

## 目的

システムの負荷耐性とスケーラビリティを検証し、本番環境での安定稼働を保証する。

## 負荷テスト戦略

### 1. テストの種類

#### 1.1 ロードテスト
- **目的**: 通常の負荷下でのシステム性能を測定
- **指標**: レスポンス時間、スループット、エラー率
- **期間**: 30分〜1時間

#### 1.2 ストレステスト
- **目的**: 限界まで負荷をかけてシステムの耐久性を確認
- **指標**: 最大同時接続数、破綻点、回復時間
- **期間**: 15分〜30分

#### 1.3 スパイクテスト
- **目的**: 急激な負荷増加への対応を確認
- **指標**: レスポンス時間の変動、エラー率、自動スケーリング
- **期間**: 5分〜10分

#### 1.4 耐久テスト（ソークテスト）
- **目的**: 長時間稼働時のメモリリークや性能劣化を検出
- **指標**: メモリ使用量、CPU使用率、レスポンス時間の推移
- **期間**: 4時間〜8時間

### 2. テストシナリオ

#### 2.1 APIエンドポイントテスト
```
シナリオ1: コンテンツ取得
- GET /api/content/articles
- GET /api/content/trends
- GET /api/content/newsletters

シナリオ2: 検索・フィルタリング
- GET /api/content/articles?category=tech&limit=50
- GET /api/content/trends?date_from=2024-01-01

シナリオ3: 認証・ユーザー操作
- POST /api/auth/login
- GET /api/user/profile
- PUT /api/user/settings

シナリオ4: 最適化されたエンドポイント
- GET /api/optimized/articles
- GET /api/optimized/dashboard
- GET /api/optimized/performance/stats
```

#### 2.2 同時接続数パターン
```
パターン1: 段階的増加
- 10 → 50 → 100 → 500 → 1000 ユーザー

パターン2: スパイク
- 10 → 1000 → 10 ユーザー（急激な変動）

パターン3: 持続的高負荷
- 500 ユーザーを4時間維持
```

## 実装計画

### 1. 負荷テストツールの選定と実装

#### 1.1 k6を使用した負荷テスト
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // 100ユーザーまで増加
    { duration: '5m', target: 100 },  // 100ユーザーを維持
    { duration: '2m', target: 200 },  // 200ユーザーまで増加
    { duration: '5m', target: 200 },  // 200ユーザーを維持
    { duration: '2m', target: 0 },    // 0まで減少
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%のリクエストが500ms以下
    http_req_failed: ['rate<0.01'],   // エラー率1%未満
  },
};

export default function () {
  const res = http.get('http://localhost:8000/api/content/articles');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

#### 1.2 Locustを使用した負荷テスト
```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_articles(self):
        self.client.get("/api/content/articles")
    
    @task(2)
    def get_trends(self):
        self.client.get("/api/content/trends")
    
    @task(1)
    def get_newsletters(self):
        self.client.get("/api/content/newsletters")
    
    @task(1)
    def get_optimized_dashboard(self):
        self.client.get("/api/optimized/dashboard")
```

### 2. パフォーマンス監視の実装

#### 2.1 システムメトリクス収集
```python
import psutil
import time

def collect_system_metrics():
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_io': psutil.disk_io_counters(),
        'network_io': psutil.net_io_counters(),
        'connections': len(psutil.net_connections()),
    }
```

#### 2.2 アプリケーションメトリクス
```python
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_connections = Gauge('active_connections', 'Active connections')
```

### 3. テストレポートの自動生成

#### 3.1 レポート構造
```json
{
  "test_id": "load-test-2024-01-01",
  "test_type": "load_test",
  "duration": "30m",
  "results": {
    "total_requests": 100000,
    "successful_requests": 99500,
    "failed_requests": 500,
    "error_rate": 0.5,
    "avg_response_time": 150,
    "p95_response_time": 450,
    "p99_response_time": 800,
    "throughput": 55.5,
    "max_concurrent_users": 500
  },
  "system_metrics": {
    "avg_cpu": 45.5,
    "max_cpu": 78.2,
    "avg_memory": 62.3,
    "max_memory": 85.7
  },
  "recommendations": []
}
```

## 実装手順

1. **負荷テストスクリプトの作成**
2. **システム監視ツールの設定**
3. **テストシナリオの実装**
4. **自動レポート生成の実装**
5. **負荷テストの実行**
6. **結果の分析と最適化**
7. **スケーラビリティ検証**

## 目標値

### パフォーマンス目標
- **平均レスポンス時間**: 200ms以下
- **95パーセンタイルレスポンス時間**: 500ms以下
- **99パーセンタイルレスポンス時間**: 1000ms以下
- **エラー率**: 0.1%以下
- **スループット**: 50 req/s以上

### スケーラビリティ目標
- **同時接続数**: 1000ユーザー対応
- **1日あたりのリクエスト数**: 100万リクエスト対応
- **データベース接続**: 100接続まで対応
- **メモリ使用量**: 2GB以下で安定稼働

## 監視指標

### システムメトリクス
- CPU使用率
- メモリ使用率
- ディスクI/O
- ネットワークI/O
- アクティブ接続数

### アプリケーションメトリクス
- リクエスト数
- レスポンス時間
- エラー率
- キャッシュヒット率
- データベースクエリ時間

### ビジネスメトリクス
- ユーザーあたりのリクエスト数
- ページビュー
- API使用率
- コンバージョン率

## テスト環境

### ハードウェア要件
- CPU: 4コア以上
- メモリ: 8GB以上
- ディスク: SSD推奨

### ソフトウェア要件
- Python 3.13
- Node.js 18以上
- k6またはLocust
- PostgreSQL/SQLite
- Redis（オプション）

## 期待される成果

- **負荷耐性の確認**: システムが目標負荷に耐えられることを確認
- **ボトルネックの特定**: パフォーマンス問題の箇所を特定
- **最適化の効果測定**: Phase 7-1〜7-4の最適化効果を定量的に測定
- **スケーラビリティの検証**: 水平・垂直スケーリングの効果を確認
