# マイグレーション問題のトラブルシューティングガイド

## 概要

このガイドでは、Alembicマイグレーションで発生する一般的な問題とその解決方法を説明します。自動修復機能が実装されていますが、手動での対応が必要な場合もあります。

## 自動修復機能について

ワークフロー（`.github/workflows/daily-trends.yml`）には自動修復機能が組み込まれており、以下の問題を自動的に検出・修復します：

- 重複リビジョンID
- 複数のheadリビジョン
- マイグレーションチェーンの不整合

## よくある問題と対応方法

### 1. 重複リビジョンID

**症状**:
```
UserWarning: Revision 2a3b4c5d6e7f is present more than once
```

**原因**: 同じリビジョンIDが2つ以上のマイグレーションファイルで使用されている

**自動修復**:
ワークフローが自動的に検出・修復します。一方のファイルのリビジョンIDを新しいIDに変更します。

**手動対応が必要な場合**:

1. **問題の確認**:
```bash
cd backend
python3 scripts/detect_migration_issues.py
```

2. **自動修復の実行**:
```bash
python3 scripts/auto_fix_migrations.py
```

3. **手動で修正する場合**:
```bash
# 重複しているリビジョンIDを確認
grep -r "revision.*2a3b4c5d6e7f" alembic/versions/

# 一方のファイルを編集して新しいリビジョンIDを生成
# 例: revision: str = "新しい12文字の16進数ID"
```

4. **修正後の確認**:
```bash
python3 scripts/detect_migration_issues.py
python3 -m alembic history
```

### 2. 複数のheadリビジョン

**症状**:
```
ERROR [alembic.util.messaging] Multiple head revisions are present for given argument 'head'
```

**原因**: マイグレーションチェーンが分岐している（複数のブランチから同時にマイグレーションが作成された）

**自動修復**:
ワークフローが自動的にマージマイグレーションを作成しようとします。

**手動対応が必要な場合**:

1. **現在のheadを確認**:
```bash
cd backend
python3 -m alembic heads
```

2. **自動修復の実行**:
```bash
python3 scripts/fix_multiple_heads.py
```

3. **手動でマージマイグレーションを作成**:
```bash
# headリビジョンを確認
python3 -m alembic heads

# マージマイグレーションを作成（例: head1とhead2をマージ）
python3 -m alembic revision --autogenerate -m "merge multiple heads" \
  --head head1 --head head2
```

4. **マージマイグレーションを適用**:
```bash
python3 -m alembic upgrade head
```

### 3. マイグレーションチェーンの不整合

**症状**:
```
ERROR: Can't locate revision identified by 'xxxxx'
```

**原因**: マイグレーションファイルが削除された、またはチェーンが壊れている

**対応方法**:

1. **現在の状態を確認**:
```bash
cd backend
python3 -m alembic current
python3 -m alembic history
```

2. **データベースの状態を確認**:
```bash
# データベースに記録されているマイグレーションを確認
python3 << 'EOF'
from sqlalchemy import text
from database import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    versions = [row[0] for row in result]
    print(f"Applied migrations: {', '.join(versions)}")
EOF
```

3. **適切なリビジョンにスタンプ**:
```bash
# データベースの状態に合わせてスタンプ
python3 -m alembic stamp <revision_id>

# 例: すべてのテーブルが存在する場合
python3 scripts/fix_migration_chain.py
```

### 4. テーブルが存在しない

**症状**:
```
ERROR: relation "xxxxx" does not exist
```

**原因**: マイグレーションが記録されているが、実際のテーブルが作成されていない

**対応方法**:

1. **テーブルの存在確認**:
```bash
cd backend
python3 << 'EOF'
from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Existing tables: {', '.join(sorted(tables))}")
EOF
```

2. **マイグレーションの再適用**:
```bash
# マイグレーションをリセットして再適用
python3 -m alembic downgrade base
python3 -m alembic upgrade head
```

3. **手動でテーブルを作成**:
```bash
# マイグレーションファイルからSQLを抽出して手動実行
# または、Supabase DashboardのSQL Editorで実行
```

## ワークフローが失敗した場合の対応

### ステップ1: エラーログの確認

1. GitHub Actionsのワークフロー実行ページを開く
2. 失敗したステップのログを確認
3. エラーメッセージをコピー

### ステップ2: 自動修復の確認

ワークフローには自動修復ステップが含まれています。以下のメッセージを確認：

- `✅ No migration issues detected` - 問題なし
- `⚠️ Migration issues detected, attempting auto-fix...` - 自動修復を試行中
- `❌ Auto-fix failed` - 自動修復失敗、手動対応が必要

### ステップ3: ローカルでの再現と修正

1. **ローカル環境で再現**:
```bash
cd backend
source venv/bin/activate
python3 scripts/detect_migration_issues.py
```

2. **問題を修正**:
```bash
# 自動修復を試行
python3 scripts/auto_fix_migrations.py

# それでも解決しない場合は手動で修正
```

3. **修正内容をコミット・プッシュ**:
```bash
git add backend/alembic/versions/*.py
git commit -m "fix: マイグレーション問題を修正"
git push
```

### ステップ4: Issueの確認

ワークフローが失敗すると、自動的にIssueが作成されます。Issueには以下の情報が含まれます：

- エラーの詳細
- マイグレーション履歴
- 現在のリビジョン状態
- 推奨される対応方法

## 予防策

### 1. マイグレーション作成時の注意点

- **リビジョンIDの確認**: 新しいマイグレーションを作成する前に、既存のリビジョンIDと重複していないか確認
- **ブランチでの作業**: 複数のブランチで同時にマイグレーションを作成しない
- **マージ前の確認**: PRをマージする前に、マイグレーションの整合性を確認

### 2. 定期的なチェック

```bash
# 週次でマイグレーション状態を確認
cd backend
python3 scripts/detect_migration_issues.py
```

### 3. マイグレーション作成のベストプラクティス

1. **最新のmainブランチから作業開始**:
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature
```

2. **マイグレーション作成前の確認**:
```bash
cd backend
python3 -m alembic current
python3 -m alembic heads
```

3. **マイグレーション作成**:
```bash
python3 -m alembic revision --autogenerate -m "description"
```

4. **作成後の確認**:
```bash
python3 scripts/detect_migration_issues.py
python3 -m alembic history
```

## 緊急時の対応

### データベースがロックされている場合

```bash
# データベース接続を確認
# PostgreSQLの場合
psql $DATABASE_URL -c "SELECT pid, state, query FROM pg_stat_activity WHERE datname = current_database();"

# ロックしているプロセスを終了
psql $DATABASE_URL -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND state = 'idle in transaction';"
```

### マイグレーションをロールバックする必要がある場合

```bash
cd backend
# 特定のリビジョンに戻す
python3 -m alembic downgrade <revision_id>

# または、1つ前のリビジョンに戻す
python3 -m alembic downgrade -1
```

### 完全にリセットする場合（⚠️ データが失われます）

```bash
cd backend
# すべてのマイグレーションをロールバック
python3 -m alembic downgrade base

# データベースを初期化
python3 -c "from database import init_db; init_db()"

# マイグレーションを再適用
python3 -m alembic upgrade head
```

## 参考リソース

- [Alembic公式ドキュメント](https://alembic.sqlalchemy.org/)
- [SQLAlchemyマイグレーションガイド](https://docs.sqlalchemy.org/en/20/core/metadata.html)
- プロジェクト内のスクリプト:
  - `backend/scripts/detect_migration_issues.py` - 問題の検出
  - `backend/scripts/auto_fix_migrations.py` - 自動修復
  - `backend/scripts/fix_duplicate_revisions.py` - 重複リビジョンIDの修正
  - `backend/scripts/fix_multiple_heads.py` - 複数headの修正

## サポート

問題が解決しない場合は、以下を確認してください：

1. GitHub Actionsのログ
2. 自動生成されたIssue
3. データベースの状態（Supabase Dashboardなど）

必要に応じて、詳細なエラーメッセージと共にIssueを作成してください。

