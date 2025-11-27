# 運用マニュアル

Phase 8-5: セキュリティ強化と運用

## 日次運用タスク

### 毎日実施

- [ ] システムヘルスチェック
- [ ] エラーログ確認
- [ ] パフォーマンスメトリクス確認
- [ ] バックアップ成功確認

```bash
# ヘルスチェック
curl http://localhost:8000/health
curl http://localhost:3000/api/health

# ログ確認
make logs | grep ERROR

# メトリクス確認
curl http://localhost:8000/metrics

# バックアップ確認
make list-backups
```

## 週次運用タスク

### 毎週月曜日実施

- [ ] セキュリティスキャン確認
- [ ] 依存関係更新確認
- [ ] パフォーマンスレビュー
- [ ] ディスク使用量確認

```bash
# セキュリティスキャン
make security-check

# 依存関係更新（Dependabot PR確認）
gh pr list --label dependencies

# パフォーマンスレビュー
# Grafana ダッシュボードで確認

# ディスク使用量
df -h
```

## 月次運用タスク

### 毎月1日実施

- [ ] 包括的セキュリティ監査
- [ ] バックアップ復旧テスト
- [ ] パフォーマンス最適化レビュー
- [ ] ドキュメント更新

```bash
# セキュリティ監査
./scripts/security-check.sh

# 復旧テスト
./scripts/restore.sh

# 最適化レビュー
python3 scripts/sqlite-optimization.py
node scripts/verify-scalability.js
```

## インシデント対応

### レベル1: 緊急（サービス停止）

**対応時間**: 即座

**手順**:

1. 問題の確認
2. 影響範囲の特定
3. 一時的な回避策の実施
4. 根本原因の調査
5. 恒久対策の実施
6. 事後報告

```bash
# サービス状態確認
kubectl get pods
docker ps

# ログ確認
kubectl logs -f <pod-name>
docker logs <container-id>

# ロールバック
gh pr list --state merged | head -1
# 前のバージョンに戻す

# または
make restore  # バックアップから復旧
```

### レベル2: 高（パフォーマンス劣化）

**対応時間**: 4時間以内

**手順**:

1. メトリクス確認
2. ボトルネック特定
3. スケーリング検討
4. 最適化実施

```bash
# メトリクス確認
curl http://localhost:9090  # Prometheus

# スケーリング
kubectl scale deployment aica-sys-backend --replicas=5
docker-compose up -d --scale backend=3

# 最適化
python3 scripts/sqlite-optimization.py
```

### レベル3: 中（マイナーな問題）

**対応時間**: 1営業日以内

**手順**:

1. 問題の記録
2. 優先度付け
3. 修正計画
4. 実装とテスト

## デプロイ手順

### 通常デプロイ

```bash
# 1. ブランチ作成
git checkout -b feature/new-feature

# 2. 開発・テスト
# ... コーディング ...

# 3. ローカルテスト
make test

# 4. コミット・プッシュ
git add .
git commit -m "feat: 新機能"
git push origin feature/new-feature

# 5. PR作成
gh pr create --base main --title "feat: 新機能"

# 6. CI/CDパイプライン確認
# GitHub Actions で自動テスト実行

# 7. レビュー・マージ
# レビュー承認後、マージ

# 8. 本番デプロイ
# main へのマージで自動デプロイ
```

### ホットフィックス

```bash
# 1. mainから直接ブランチ
git checkout main
git pull
git checkout -b hotfix/critical-fix

# 2. 修正
# ... 修正 ...

# 3. テスト
make test

# 4. 即座にデプロイ
git add .
git commit -m "fix: 緊急修正"
git push origin hotfix/critical-fix
gh pr create --base main --title "fix: 緊急修正"
gh pr merge --merge

# 5. develop にもマージ
git checkout develop
git merge main
git push
```

## トラブルシューティング

### サービスが起動しない

```bash
# ログ確認
docker logs aica-sys-backend
kubectl logs -f deployment/aica-sys-backend

# 設定確認
cat .env.production

# データベース確認
sqlite3 backend/aica_sys.db "PRAGMA integrity_check;"

# 再起動
make down && make up
kubectl rollout restart deployment/aica-sys-backend
```

### パフォーマンスが悪い

```bash
# メトリクス確認
curl http://localhost:8000/metrics

# データベース最適化
python3 scripts/sqlite-optimization.py

# キャッシュ確認
curl http://localhost:8000/api/optimized/performance/stats

# スケーリング
kubectl scale deployment aica-sys-backend --replicas=5
```

### メモリリーク疑い

```bash
# メモリ使用量確認
docker stats
kubectl top pods

# プロセス再起動
make restart
kubectl rollout restart deployment/aica-sys-backend

# ログでメモリ状況確認
grep -i "memory" logs/
```

## セキュリティチェックリスト

### デプロイ前

- [ ] 全テストが成功
- [ ] セキュリティスキャン合格
- [ ] 依存関係に既知の脆弱性なし
- [ ] シークレットがコードに含まれていない
- [ ] 環境変数が正しく設定されている

### デプロイ後

- [ ] ヘルスチェック成功
- [ ] エラーログなし
- [ ] パフォーマンス正常
- [ ] セキュリティヘッダー確認
- [ ] SSL証明書有効

## 定期メンテナンス

### 毎週

- 依存関係の更新（Dependabot PR確認）
- セキュリティスキャン
- パフォーマンスレビュー

### 毎月

- バックアップ復旧テスト
- SSL証明書の有効期限確認
- ログのアーカイブ
- リソース使用量の最適化

### 四半期ごと

- 包括的セキュリティ監査
- ディザスタリカバリ訓練
- ドキュメントレビュー
- アーキテクチャレビュー

## 連絡先

### エスカレーション

- **レベル1**: 開発チーム
- **レベル2**: テックリード
- **レベル3**: CTO/運用責任者

### 外部サポート

- **Vercel**: https://vercel.com/support
- **GitHub**: https://support.github.com
- **Supabase**: https://supabase.com/support
