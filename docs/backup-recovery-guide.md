# バックアップ・復旧ガイド

Phase 8-4: バックアップと復旧

## 概要

システムに異常があった場合、直近のバックアップデータに戻すための手順を説明します。

## バックアップ

### 手動バックアップ

```bash
# バックアップスクリプトを実行
./scripts/backup.sh

# または Makefile を使用
make backup
```

### 自動バックアップ

**GitHub Actions**: 毎日午前3時（JST）に自動実行

- ワークフロー: `.github/workflows/scheduled-backup.yml`
- 保持期間: 7日間
- 手動実行: `Actions` タブから `Scheduled Backup` を実行

### バックアップ内容

1. **データベース**: `backend/aica_sys.db`
2. **アップロードファイル**: `public/uploads/`
3. **設定ファイル**: `.env.production`
4. **マニフェスト**: バックアップ情報（JSON）

### バックアップファイル

```
backups/
├── backup_20241010_030000.tar.gz
├── backup_20241009_030000.tar.gz
└── backup_20241008_030000.tar.gz
```

ファイル名形式: `backup_YYYYMMDD_HHMMSS.tar.gz`

## 復旧

### 手動復旧

#### 1. 最新のバックアップから復旧

```bash
# リストアスクリプトを実行（最新バックアップを使用）
./scripts/restore.sh

# または Makefile を使用
make restore
```

#### 2. 特定のバックアップから復旧

```bash
# 利用可能なバックアップを確認
ls -lh backups/*.tar.gz

# 特定のバックアップを指定
./scripts/restore.sh backups/backup_20241010_030000.tar.gz
```

### 復旧手順

1. **バックアップ一覧の表示**
2. **復旧するバックアップの選択**
3. **確認プロンプト**（yes/no）
4. **現在のデータを一時バックアップ**
5. **バックアップファイルの展開**
6. **データベースの復旧**
7. **アップロードファイルの復旧**
8. **設定ファイルの復旧**
9. **整合性チェック**
10. **完了**

### 復旧後の作業

```bash
# バックエンドを再起動
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --reload

# または Docker を使用
docker-compose restart backend

# 動作確認
curl http://localhost:8000/health
```

## バックアップの検証

### 整合性チェック

```bash
# SQLite整合性チェック
sqlite3 backend/aica_sys.db "PRAGMA integrity_check;"

# 出力: ok
```

### テストリストア

```bash
# テスト用ディレクトリで復旧テスト
mkdir -p test_restore
cd test_restore

# バックアップをコピー
cp ../backups/backup_20241010_030000.tar.gz .

# 展開して確認
tar -xzf backup_20241010_030000.tar.gz
ls -la
```

## トラブルシューティング

### バックアップが見つからない

**症状**: `backups/` ディレクトリが空

**解決策**:
```bash
# 手動でバックアップを作成
./scripts/backup.sh

# GitHub Actionsから手動実行
# Actions > Scheduled Backup > Run workflow
```

### 復旧後にデータベースエラー

**症状**: `database is locked` エラー

**解決策**:
```bash
# WALファイルを削除
rm -f backend/aica_sys.db-wal backend/aica_sys.db-shm

# バックエンドを再起動
pkill -f uvicorn
cd backend && python3 -m uvicorn main:app --reload
```

### 復旧後にアプリケーションが起動しない

**症状**: バックエンドが起動しない

**解決策**:
```bash
# データベースの初期化
cd backend
python3 -c "from database import init_db; init_db()"

# 最適化を実行
python3 ../scripts/sqlite-optimization.py
```

## ベストプラクティス

### バックアップ

1. **定期的な実行**: 毎日自動バックアップ
2. **複数世代管理**: 7日分保持
3. **バックアップ検証**: 定期的に復旧テスト
4. **オフサイトバックアップ**: 別の場所に保存

### 復旧

1. **事前確認**: 復旧前に現在のデータをバックアップ
2. **段階的復旧**: データベース→ファイル→設定の順
3. **検証**: 復旧後に必ず整合性チェック
4. **ログ確認**: 復旧後のエラーログを確認

## 自動化

### Cron設定（Linux/macOS）

```bash
# crontabを編集
crontab -e

# 毎日午前3時にバックアップ
0 3 * * * cd /path/to/aica-sys && ./scripts/backup.sh >> /var/log/aica-sys-backup.log 2>&1

# 毎週日曜日午前2時にバックアップ
0 2 * * 0 cd /path/to/aica-sys && ./scripts/backup.sh >> /var/log/aica-sys-backup.log 2>&1
```

### Docker定期バックアップ

```bash
# Docker Composeで定期バックアップコンテナを追加
# docker-compose.yml に追加:
#
# backup:
#   image: alpine:latest
#   volumes:
#     - ./backend:/app/backend:ro
#     - ./backups:/backups
#   command: |
#     sh -c "while true; do
#       cp /app/backend/aica_sys.db /backups/backup_\$(date +%Y%m%d_%H%M%S).db
#       sleep 86400
#     done"
```

## 参考資料

- [SQLite Backup](https://www.sqlite.org/backup.html)
- [Disaster Recovery Best Practices](https://cloud.google.com/architecture/dr-scenarios-planning-guide)
