# 監視・アラートガイド

Phase 8-3: 監視とアラート体制

## 概要

Prometheus、Grafana、Alertmanagerを使用した包括的な監視システムのセットアップと運用方法。

## クイックスタート

### Docker Composeで監視スタックを起動

```bash
# 監視スタックを起動
docker-compose -f docker-compose.monitoring.yml up -d

# アクセス
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin123)
# Alertmanager: http://localhost:9093
```

### Kubernetesで監視スタックをデプロイ

```bash
# デプロイ
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml
kubectl apply -f k8s/alertmanager-deployment.yaml
kubectl apply -f k8s/prometheus-alerts.yaml

# アクセス
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:80
kubectl port-forward svc/alertmanager 9093:9093
```

## Prometheus

### メトリクスの確認

```bash
# Prometheusにアクセス
open http://localhost:9090

# クエリ例
# - CPU使用率: rate(process_cpu_seconds_total[5m]) * 100
# - メモリ使用量: process_resident_memory_bytes
# - リクエスト数: rate(http_requests_total[5m])
# - エラー率: rate(http_requests_total{status=~"5.."}[5m])
```

### 主要メトリクス

#### アプリケーションメトリクス
- `http_requests_total` - HTTPリクエスト総数
- `http_request_duration_seconds` - リクエスト処理時間
- `http_requests_in_flight` - 処理中のリクエスト数
- `cache_hits_total` - キャッシュヒット数
- `cache_misses_total` - キャッシュミス数
- `database_query_duration_seconds` - DBクエリ時間

#### システムメトリクス
- `process_cpu_seconds_total` - CPU使用時間
- `process_resident_memory_bytes` - メモリ使用量
- `process_open_fds` - オープンファイルディスクリプタ数
- `node_cpu_seconds_total` - ノードCPU時間
- `node_memory_MemTotal_bytes` - 総メモリ量

## Grafana

### ダッシュボードのインポート

1. Grafanaにログイン（http://localhost:3001）
2. Configuration > Data Sources > Add data source
3. Prometheus を選択
4. URL: `http://prometheus:9090`
5. Save & Test

### 推奨ダッシュボード

#### システム概要ダッシュボード
- CPU使用率（全コンテナ）
- メモリ使用率（全コンテナ）
- ネットワークI/O
- ディスクI/O

#### アプリケーションダッシュボード
- リクエスト数（エンドポイント別）
- レスポンス時間（P50、P95、P99）
- エラー率
- アクティブ接続数

#### ビジネスダッシュボード
- アクティブユーザー数
- API使用率
- コンテンツ生成数
- サブスクリプション数

## Alertmanager

### アラート設定

#### Slack通知の設定

```yaml
# monitoring/alertmanager.yml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#aica-sys-critical'
        title: '🚨 CRITICAL ALERT'
        text: '{{ range .Alerts }}{{ .Annotations.description }}\n{{ end }}'
```

#### メール通知の設定

```yaml
receivers:
  - name: 'critical'
    email_configs:
      - to: 'ops@aica-sys.com'
        from: 'alerts@aica-sys.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@aica-sys.com'
        auth_password: 'APP_PASSWORD'
```

### アラートルール

#### 定義済みアラート

1. **HighErrorRate** - エラー率 > 5%
2. **SlowResponseTime** - P95レスポンス > 1秒
3. **HighCPUUsage** - CPU使用率 > 80%
4. **HighMemoryUsage** - メモリ使用率 > 80%
5. **PodDown** - Pod停止
6. **DatabaseConnectionError** - DB接続エラー
7. **LowCacheHitRate** - キャッシュヒット率 < 50%
8. **HighDiskUsage** - ディスク空き < 20%

## 監視のベストプラクティス

### メトリクス収集

1. **適切な間隔**: 15秒（デフォルト）
2. **保持期間**: 30日
3. **ラベル付け**: 環境、サービス、バージョン

### アラート設定

1. **適切な閾値**: 本番データに基づいて調整
2. **遅延設定**: 一時的な問題を無視（5-10分）
3. **重複排除**: 同じアラートの繰り返しを防ぐ

### ダッシュボード設計

1. **階層化**: 概要 → 詳細
2. **リアルタイム**: 自動更新
3. **アラート統合**: ダッシュボードにアラート表示

## トラブルシューティング

### Prometheusがメトリクスを収集できない

```bash
# ターゲットの状態確認
curl http://localhost:9090/api/v1/targets

# ログ確認
docker logs aica-sys-prometheus
```

### Grafanaでグラフが表示されない

```bash
# データソース接続確認
curl http://localhost:3001/api/health

# Prometheusの接続テスト
curl http://prometheus:9090/api/v1/query?query=up
```

### アラートが送信されない

```bash
# Alertmanagerの状態確認
curl http://localhost:9093/api/v1/status

# アラートルールの確認
curl http://localhost:9090/api/v1/rules
```

## カスタムメトリクスの追加

### バックエンド（Python）

```python
from prometheus_client import Counter, Histogram, Gauge

# カウンター
api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])

# ヒストグラム
response_time = Histogram('api_response_time_seconds', 'API response time')

# ゲージ
active_users = Gauge('active_users', 'Active users')

# 使用例
@app.get("/api/example")
async def example():
    api_requests.labels(method='GET', endpoint='/api/example', status='200').inc()
    with response_time.time():
        # 処理
        pass
```

### フロントエンド（Next.js）

```typescript
// Web Vitals を Prometheus 形式で送信
export function sendMetricsToPrometheus(metric: Metric) {
  fetch('/api/metrics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: metric.name,
      value: metric.value,
      labels: { page: window.location.pathname },
    }),
  });
}
```

## 監視ダッシュボード例

### システムヘルス

```
┌─────────────────────────────────────────────────────────┐
│  CPU Usage: [████████░░] 80%   Memory: [███████░░░] 70% │
│  Disk: [███░░░░░░░] 30%        Network: 100 MB/s        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Active Pods: 5/10              Response Time: 150ms     │
│  Error Rate: 0.1%               Cache Hit Rate: 85%      │
└─────────────────────────────────────────────────────────┘
```

### アプリケーションパフォーマンス

```
Requests/sec:  ▁▂▃▅▇█▇▅▃▂▁  (50-200 req/s)
Response Time: ▂▂▂▃▅▆▄▃▂▂▂  (100-300ms)
Error Rate:    ▁▁▁▁▁▂▁▁▁▁▁  (0-1%)
```

## アラート通知先の設定

### Slack Webhook

```bash
# Slackワークスペースで設定
1. Slack App を作成
2. Incoming Webhook を有効化
3. Webhook URL を取得
4. monitoring/alertmanager.yml に設定
```

### メール（Gmail）

```bash
# Gmailアプリパスワードの取得
1. Googleアカウント > セキュリティ
2. 2段階認証を有効化
3. アプリパスワードを生成
4. monitoring/alertmanager.yml に設定
```

## 参考資料

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
