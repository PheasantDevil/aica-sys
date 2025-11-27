# 負荷テスト・スケーラビリティ検証ガイド

Phase 7-5: 負荷テストとスケーラビリティ検証

## 概要

このディレクトリには、AICA-SyS システムの負荷テストとスケーラビリティ検証のためのスクリプトが含まれています。

## テストツール

### 1. K6 負荷テスト（推奨）

**特徴**:

- 軽量で高性能
- JavaScript でテストシナリオを記述
- 詳細なパフォーマンス分析

**インストール**:

```bash
# macOS (Homebrew使用)
brew install k6

# その他のプラットフォーム
# https://k6.io/docs/getting-started/installation/
```

**実行方法**:

```bash
# 基本実行
k6 run scripts/load-test-k6.js

# VUカスタマイズ
k6 run --vus 100 --duration 5m scripts/load-test-k6.js

# 結果をJSON出力
k6 run --out json=results.json scripts/load-test-k6.js
```

### 2. Locust 負荷テスト

**特徴**:

- Python で記述
- Webベースのリアルタイム監視UI
- 分散負荷テスト対応

**インストール**:

```bash
cd backend
source venv/bin/activate
pip install locust
```

**実行方法**:

```bash
# Web UIモード（推奨）
locust -f scripts/load-test-locust.py --host=http://127.0.0.1:8000

# ヘッドレスモード
locust -f scripts/load-test-locust.py \
  --host=http://127.0.0.1:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

### 3. Node.js 包括的負荷テスト

**特徴**:

- Node.js で実装
- 追加の依存関係不要
- 詳細なレポート生成

**実行方法**:

```bash
# デフォルト設定（50ユーザー、60秒）
node scripts/comprehensive-load-test.js

# カスタム設定
node scripts/comprehensive-load-test.js \
  --users=100 \
  --duration=120 \
  --requests=200
```

### 4. スケーラビリティ検証

**特徴**:

- 段階的な負荷増加テスト
- スケーラビリティ評価
- 推奨事項の自動生成

**実行方法**:

```bash
node scripts/verify-scalability.js
```

## テストシナリオ

### シナリオ 1: ロードテスト（通常負荷）

**目的**: 通常の負荷下でのパフォーマンス確認

**設定**:

- ユーザー数: 50-100
- 期間: 5-10分
- 期待値: 成功率 99%以上、P95 < 500ms

**実行コマンド**:

```bash
k6 run --vus 100 --duration 10m scripts/load-test-k6.js
```

### シナリオ 2: ストレステスト（高負荷）

**目的**: システムの限界点を特定

**設定**:

- ユーザー数: 200-500
- 期間: 5-10分
- 期待値: 成功率 95%以上、システムダウンなし

**実行コマンド**:

```bash
node scripts/comprehensive-load-test.js --users=500 --duration=300
```

### シナリオ 3: スパイクテスト

**目的**: 急激な負荷増加への対応確認

**設定**:

- ユーザー数: 10 → 500 → 10（急激に変化）
- 期間: 5-10分

**K6スクリプトを修正**:

```javascript
export const options = {
  stages: [
    { duration: "1m", target: 10 },
    { duration: "30s", target: 500 }, // 急激に増加
    { duration: "2m", target: 500 },
    { duration: "30s", target: 10 }, // 急激に減少
    { duration: "1m", target: 10 },
  ],
};
```

### シナリオ 4: 耐久テスト（ソークテスト）

**目的**: 長時間稼働時のメモリリークや性能劣化を検出

**設定**:

- ユーザー数: 100
- 期間: 4時間以上
- 監視: メモリ使用量、CPU使用率の推移

**実行コマンド**:

```bash
# パフォーマンスモニタリングを開始
python3 scripts/monitor-performance.py --interval=10 --duration=14400 &

# 負荷テストを実行
k6 run --vus 100 --duration 4h scripts/load-test-k6.js
```

## パフォーマンス目標値

### 応答時間

- **平均**: 200ms以下
- **P95**: 500ms以下
- **P99**: 1000ms以下

### スループット

- **最小**: 50 req/s
- **目標**: 100 req/s
- **理想**: 200 req/s以上

### 成功率

- **最小**: 99%
- **目標**: 99.9%

### システムリソース

- **CPU**: 80%以下
- **メモリ**: 80%以下
- **接続数**: 1000以下

## テスト前の準備

### 1. バックエンドの起動

```bash
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. フロントエンドの起動（オプション）

```bash
cd frontend
npm run dev
```

### 3. データベースの準備

```bash
# データベースを初期化
cd backend
source venv/bin/activate
python3 -c "from database import init_db; init_db()"

# 最適化を実行
python3 scripts/sqlite-optimization.py
```

### 4. キャッシュの準備（オプション）

```bash
# Redisを起動（インストール済みの場合）
redis-server
```

## テスト実行の推奨順序

1. **ヘルスチェック**:

   ```bash
   curl http://127.0.0.1:8000/health
   ```

2. **軽い負荷テスト**:

   ```bash
   node scripts/comprehensive-load-test.js --users=10 --duration=30
   ```

3. **通常負荷テスト**:

   ```bash
   node scripts/comprehensive-load-test.js --users=50 --duration=60
   ```

4. **スケーラビリティ検証**:

   ```bash
   node scripts/verify-scalability.js
   ```

5. **高負荷テスト**（システムが安定している場合のみ）:
   ```bash
   node scripts/comprehensive-load-test.js --users=200 --duration=120
   ```

## 結果の分析

### レポートファイル

テスト実行後、以下のレポートファイルが生成されます：

- `docs/load-test-report-*.json` - 負荷テスト結果
- `docs/scalability-test-*.json` - スケーラビリティ検証結果
- `performance-monitoring-*.json` - パフォーマンス監視結果

### 評価基準

#### ✅ 合格基準

- 成功率 ≥ 99%
- P95レスポンス時間 < 500ms
- P99レスポンス時間 < 1000ms
- CPU使用率 < 80%
- メモリ使用率 < 80%

#### ⚠️ 警告基準

- 成功率 95-99%
- P95レスポンス時間 500-1000ms
- CPU/メモリ使用率 80-90%

#### ❌ 失敗基準

- 成功率 < 95%
- P95レスポンス時間 > 1000ms
- システムクラッシュ

## トラブルシューティング

### 問題: 接続エラーが多発

**原因**: バックエンドが起動していない、または過負荷

**解決策**:

```bash
# バックエンドの状態確認
curl http://127.0.0.1:8000/health

# プロセス確認
ps aux | grep uvicorn

# 再起動
pkill -f uvicorn
cd backend && source venv/bin/activate && python3 -m uvicorn main:app --reload
```

### 問題: レスポンスタイムが長い

**原因**: データベースクエリの最適化不足、キャッシュ未使用

**解決策**:

```bash
# データベース最適化を実行
python3 scripts/sqlite-optimization.py

# キャッシュ状態を確認
curl http://127.0.0.1:8000/api/optimized/performance/stats
```

### 問題: メモリ使用量が増加し続ける

**原因**: メモリリーク

**解決策**:

- アプリケーションログを確認
- プロファイリングツールで原因を特定
- 長時間テストで問題を再現

## 継続的な監視

### プロダクション環境での監視

1. **アプリケーションメトリクス**:
   - `/api/optimized/performance/stats` エンドポイントを定期的にチェック

2. **システムメトリクス**:

   ```bash
   python3 scripts/monitor-performance.py --interval=60 --duration=86400
   ```

3. **アラート設定**:
   - レスポンス時間が閾値を超えた場合
   - エラー率が1%を超えた場合
   - CPU/メモリ使用率が80%を超えた場合

## 参考資料

- [K6 Documentation](https://k6.io/docs/)
- [Locust Documentation](https://docs.locust.io/)
- [Web Performance Best Practices](https://web.dev/performance/)
- [Node.js Performance Optimization](https://nodejs.org/en/docs/guides/simple-profiling/)
