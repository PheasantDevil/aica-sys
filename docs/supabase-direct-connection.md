# Supabase 直接接続ガイド（Docker不要）

## 概要

Docker Desktop不要で、ローカル・リモート両方でSupabaseに直接接続する設定方法。

## 1. Supabase接続情報の取得

### Supabase Dashboardで確認

1. [Supabase Dashboard](https://app.supabase.com/)にログイン
2. プロジェクト「AICA-SyS-DB」を選択
3. Settings → Database → Connection Info

### 必要な情報

```
Project URL: https://ndetbklyymekcifheqaj.supabase.co
Project REF: ndetbklyymekcifheqaj
```

### 接続文字列（Connection String）

#### Pooler接続（推奨 - 本番環境）
```
Host: aws-0-ap-northeast-1.pooler.supabase.com
Database: postgres
Port: 5432
User: postgres.ndetbklyymekcifheqaj
Password: [YOUR_DATABASE_PASSWORD]

URI:
postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

#### Direct接続（低レイテンシー - 開発環境）
```
Host: db.ndetbklyymekcifheqaj.supabase.co
Database: postgres
Port: 5432
User: postgres
Password: [YOUR_DATABASE_PASSWORD]

URI:
postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres
```

### パスワード確認方法

1. Supabase Dashboard → Settings → Database
2. 「Reset Database Password」をクリック（必要な場合）
3. 新しいパスワードをコピー（一度しか表示されません）

## 2. ローカル開発環境設定

### backend/.env.local 作成

```bash
cd /Users/Work/aica-sys/backend
cp env.example .env.local
```

### backend/.env.local 編集

```bash
# Supabase Database（Direct接続 - 開発用）
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres

# Supabase API
SUPABASE_URL=https://ndetbklyymekcifheqaj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzU5NDcxMiwiZXhwIjoyMDczMTcwNzEyfQ.8g1d_7fNn32CzuTvj7y4_gqmXjMrhtMsiPAn1cMQFjw

# Groq API
GROQ_API_KEY=your-groq-api-key-here

# 他の設定はenv.exampleから
ENVIRONMENT=development
DEBUG=True
```

### フロントエンド環境変数

`frontend/.env.local` 作成：

```bash
# Supabase（公開OK）
NEXT_PUBLIC_SUPABASE_URL=https://ndetbklyymekcifheqaj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0

# バックエンドAPI
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here
```

## 3. PostgreSQLドライバーのインストール

### psycopg2-binary有効化

`backend/requirements.txt` を更新：

```bash
# Database
sqlalchemy==2.0.36
psycopg2-binary==2.9.9  # Supabase接続用に有効化
```

### インストール

```bash
cd /Users/Work/aica-sys/backend
source venv/bin/activate
pip install psycopg2-binary==2.9.9
```

## 4. 接続テスト

### バックエンド接続確認

```bash
cd /Users/Work/aica-sys/backend
source venv/bin/activate

python3 -c "
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

DATABASE_URL = os.getenv('DATABASE_URL')
print(f'DATABASE_URL: {DATABASE_URL[:50]}...')

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    version = result.fetchone()[0]
    print(f'✅ PostgreSQL接続成功!')
    print(f'Version: {version[:50]}...')
    
    result = conn.execute(text(
        \"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename\"
    ))
    tables = [row[0] for row in result]
    print(f'\\n📊 テーブル数: {len(tables)}')
    for table in tables:
        print(f'  - {table}')
"
```

### フロントエンド接続確認

```bash
cd /Users/Work/aica-sys/frontend

# Supabase JSクライアントインストール
npm install @supabase/supabase-js

# 接続テスト
node -e "
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  'https://ndetbklyymekcifheqaj.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0'
);

console.log('✅ Supabase クライアント作成成功');
"
```

## 5. マイグレーション実行

### Alembicマイグレーション（ローカル→Supabase）

```bash
cd /Users/Work/aica-sys/backend
source venv/bin/activate

# 既存のマイグレーション状態確認
alembic current

# Supabaseに既存のマイグレーションを適用
alembic upgrade head

# テーブル確認
python3 -c "
from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)
tables = inspector.get_table_names()

print('📊 Supabaseテーブル確認:')
for table in sorted(tables):
    print(f'  - {table}')
"
```

## 6. 本番環境設定

### Vercel環境変数

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://ndetbklyymekcifheqaj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database（Pooler URL使用）
DATABASE_URL=postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Groq
GROQ_API_KEY=gsk_...

# NextAuth
NEXTAUTH_URL=https://aica-sys.vercel.app
NEXTAUTH_SECRET=your-production-secret
```

### Render環境変数

```bash
# Database（Pooler URL使用）
DATABASE_URL=postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Supabase
SUPABASE_URL=https://ndetbklyymekcifheqaj.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Groq
GROQ_API_KEY=gsk_...
```

### GitHub Secrets

```bash
# GitHub Secrets に追加
gh secret set DATABASE_URL --body "postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
gh secret set SUPABASE_SERVICE_KEY --body "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
gh secret set GROQ_API_KEY --body "gsk_..."
```

## 7. 接続プール設定

### SQLAlchemy設定最適化

`backend/database.py` はすでに最適化済み：

```python
if is_postgresql:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,      # 接続プールサイズ
        max_overflow=30,   # 最大オーバーフロー
        pool_pre_ping=True,
        pool_recycle=3600
    )
```

### Supabase接続制限

- **Pooler接続**: 推奨、自動スケーリング
- **Direct接続**: 60接続まで（Free tier）

## 8. トラブルシューティング

### エラー: "could not connect to server"

**原因**: パスワードが間違っている、またはネットワークの問題

**解決**:
```bash
# パスワードを再確認
# Supabase Dashboard → Settings → Database → Reset Password

# 接続テスト
psql "postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres" -c "SELECT 1"
```

### エラー: "psycopg2 not installed"

**原因**: PostgreSQLドライバーがインストールされていない

**解決**:
```bash
pip install psycopg2-binary==2.9.9
```

### エラー: "SSL connection required"

**原因**: Supabaseは常にSSL接続を要求

**解決**:
```bash
# DATABASE_URLに?sslmode=requireを追加
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres?sslmode=require
```

## 9. パフォーマンス最適化

### Pooler vs Direct接続

| 接続タイプ | 推奨用途 | メリット | デメリット |
|----------|---------|---------|----------|
| **Pooler** | 本番環境 | 自動スケーリング、接続制限なし | やや高レイテンシー |
| **Direct** | 開発環境 | 低レイテンシー | 60接続制限 |

### 推奨設定

```bash
# ローカル開発: Direct接続
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres

# 本番環境: Pooler接続
DATABASE_URL=postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

## 10. セキュリティ

### パスワード管理

```bash
# ❌ 絶対にコミットしない
backend/.env.local
frontend/.env.local

# ✅ .gitignoreに含まれていることを確認
git check-ignore backend/.env.local
# 出力: backend/.env.local（無視されている）
```

### サービスロールキーの使用

```python
# バックエンドのみで使用
SUPABASE_SERVICE_KEY=...  # 全権限

# フロントエンドでは絶対に使用しない
# 代わりにanon keyを使用
NEXT_PUBLIC_SUPABASE_ANON_KEY=...  # 制限された権限
```

## 11. 開発ワークフロー

### ローカル開発

```bash
# 1. バックエンド起動
cd backend
source venv/bin/activate
uvicorn main:app --reload
# → Supabaseに直接接続

# 2. フロントエンド起動
cd frontend
npm run dev
# → バックエンドAPI経由でSupabaseにアクセス
```

### マイグレーション

```bash
# Alembicマイグレーション作成
cd backend
alembic revision --autogenerate -m "Add new feature"

# Supabaseに適用
alembic upgrade head

# または、Supabase CLIで適用
cd ..
supabase db push
```

### 記事生成テスト

```bash
# Supabaseに直接接続して記事生成
cd /Users/Work/aica-sys
source backend/venv/bin/activate
python3 scripts/generate_daily_article.py

# データ確認（Supabase Dashboard）
# https://app.supabase.com/project/ndetbklyymekcifheqaj/editor
```

## 12. チェックリスト

### 初回セットアップ

- [ ] Supabaseパスワード取得
- [ ] backend/.env.local作成・設定
- [ ] frontend/.env.local作成・設定
- [ ] psycopg2-binaryインストール
- [ ] 接続テスト成功
- [ ] マイグレーション適用成功

### デプロイ前確認

- [ ] Vercel環境変数設定完了
- [ ] Render環境変数設定完了
- [ ] GitHub Secrets設定完了
- [ ] RLS有効化確認
- [ ] 本番接続テスト成功

## 13. よくある質問

### Q: SQLiteからSupabaseに切り替えるメリットは？

**A:**
- ✅ 本番環境と同じデータベース
- ✅ RLS（Row Level Security）テスト可能
- ✅ リアルタイム機能使用可能
- ✅ バックアップ自動
- ✅ スケーラビリティ

### Q: ローカルでもSupabaseを使うとコストは？

**A:**
- ✅ Free tierは無料
- ✅ 500MB までのデータベース
- ✅ 50,000 月間アクティブユーザー
- ✅ 2GB 帯域幅
- ✅ 開発用途なら十分

### Q: Docker不要で本当に問題ない？

**A:**
- ✅ 問題なし
- ✅ Supabase直接接続で十分
- ✅ Docker は以下の場合のみ必要:
  - コンテナ化検証
  - Kubernetesテスト
  - 完全オフライン開発

## 参考リソース

- [Supabase Database接続](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [SQLAlchemy + Supabase](https://supabase.com/docs/guides/integrations/sqlalchemy)
- [Supabase.js](https://supabase.com/docs/reference/javascript/introduction)

