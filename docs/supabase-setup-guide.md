# Supabase セットアップガイド

## 概要

AICA-SySをSupabaseと連携させるための完全ガイド。Row Level Security (RLS)の設定、Supabase CLIの活用、環境変数設定をカバーします。

## 1. Supabase CLI インストールと連携

### Supabase CLIとは

Supabase CLIを使用すると、以下が可能になります：
- ローカルでSupabaseを実行
- マイグレーションの管理
- データベーススキーマの同期
- シードデータの投入
- プロジェクトのリンクと管理

### インストール

#### macOS (Homebrew)
```bash
brew install supabase/tap/supabase
```

#### npm (クロスプラットフォーム)
```bash
npm install -g supabase
```

### Supabaseプロジェクトにリンク

```bash
# プロジェクトディレクトリで実行
cd /Users/Work/aica-sys

# Supabaseにログイン
supabase login

# プロジェクトにリンク
supabase link --project-ref <your-project-ref>

# または、対話的にリンク
supabase link
```

### プロジェクトREF確認方法

1. [Supabase Dashboard](https://app.supabase.com/)にログイン
2. プロジェクトを選択
3. Settings → General → Reference IDをコピー

## 2. Row Level Security (RLS) 有効化

### RLSとは

Row Level Security (RLS)は、テーブルの各行へのアクセスをユーザーごとに制御するPostgreSQLの機能です。Supabaseではセキュリティのため、すべての公開テーブルでRLSの有効化が推奨されます。

### 方法1: Supabase CLIで適用（推奨）

```bash
# SQLファイルを実行
supabase db execute --file backend/security/enable_rls.sql

# または、ローカルで開発中の場合
supabase db push
```

### 方法2: Supabase Dashboardで手動適用

1. [Supabase Dashboard](https://app.supabase.com/)でプロジェクトを開く
2. SQL Editor を開く
3. `backend/security/enable_rls.sql` の内容をコピー＆ペースト
4. 「Run」をクリック

### 方法3: psqlで直接適用

```bash
# Supabaseデータベースに接続
psql "postgresql://postgres:[PASSWORD]@[PROJECT_REF].supabase.co:5432/postgres"

# SQLファイルを実行
\i backend/security/enable_rls.sql

# または
cat backend/security/enable_rls.sql | psql "postgresql://..."
```

## 3. RLSポリシーの説明

### テーブルごとのポリシー

#### 公開コンテンツ（articles, trends, automated_contents）
```sql
-- 誰でも読める
CREATE POLICY "Allow public to read published articles"
ON public.articles FOR SELECT
TO anon, authenticated
USING (true);

-- サービスロールは全権限
CREATE POLICY "Allow service role full access"
ON public.articles FOR ALL
TO service_role
USING (true);
```

#### ユーザーデータ（users, subscriptions）
```sql
-- ユーザーは自分のデータのみ読める
CREATE POLICY "Users can read own data"
ON public.users FOR SELECT
TO authenticated
USING (auth.uid()::text = id);

-- ユーザーは自分のデータのみ更新可能
CREATE POLICY "Users can update own data"
ON public.users FOR UPDATE
TO authenticated
USING (auth.uid()::text = id);
```

#### 管理データ（collection_jobs, source_data）
```sql
-- 認証済みユーザーのみ読める
CREATE POLICY "Allow authenticated users to read"
ON public.source_data FOR SELECT
TO authenticated
USING (true);
```

## 4. Supabase CLI 主要コマンド

### プロジェクト管理

```bash
# ログイン
supabase login

# プロジェクト一覧
supabase projects list

# プロジェクトにリンク
supabase link --project-ref <ref>

# プロジェクト情報確認
supabase status
```

### データベース管理

```bash
# マイグレーション作成
supabase migration new <migration_name>

# マイグレーション適用
supabase db push

# リモートからマイグレーションを取得
supabase db pull

# SQL実行
supabase db execute --file <file.sql>

# データベースリセット（ローカル）
supabase db reset
```

### 関数・トリガー管理

```bash
# 関数一覧
supabase functions list

# 関数デプロイ
supabase functions deploy <function_name>

# 関数ログ確認
supabase functions logs <function_name>
```

### シークレット管理

```bash
# シークレット設定
supabase secrets set KEY=VALUE

# シークレット一覧
supabase secrets list

# シークレット削除
supabase secrets unset KEY
```

## 5. 環境変数設定

### Supabase接続情報取得

```bash
# プロジェクト設定を表示
supabase projects api-keys --project-ref <ref>
```

または、Dashboardから：
1. Settings → API
2. 以下をコピー：
   - Project URL
   - anon public key
   - service_role key（秘密鍵）

### ローカル環境（backend/.env.local）

```bash
# Supabase Database
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGc...（anon public key）
SUPABASE_SERVICE_KEY=eyJhbGc...（service_role key）

# Groq API
GROQ_API_KEY=gsk_...
```

### Vercel環境変数

```bash
# Vercel Dashboard → Settings → Environment Variables
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT_REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

### Render環境変数

```bash
# Render Dashboard → Environment
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
GROQ_API_KEY=gsk_...
```

## 6. マイグレーション管理

### Alembic → Supabase 連携

```bash
# 1. Alembicマイグレーション生成（ローカルSQLite）
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Add new tables"

# 2. 生成されたマイグレーションをSupabase用に変換
# alembic/versions/xxx.py の内容を確認

# 3. Supabaseマイグレーション作成
cd ..
supabase migration new add_new_tables

# 4. AlembicのSQL文をSupabaseマイグレーションにコピー
# supabase/migrations/[timestamp]_add_new_tables.sql

# 5. Supabaseに適用
supabase db push
```

### Supabase直接マイグレーション

```bash
# 新しいマイグレーション作成
supabase migration new enable_rls

# supabase/migrations/[timestamp]_enable_rls.sql を編集
# backend/security/enable_rls.sql の内容をコピー

# Supabaseに適用
supabase db push
```

## 7. RLS確認とテスト

### RLS状態確認

```bash
# Supabase CLIで確認
supabase db execute --query "
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
"
```

### ポリシー一覧確認

```bash
supabase db execute --query "
SELECT 
    schemaname,
    tablename,
    policyname,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
"
```

### RLSテスト

```bash
# 匿名ユーザーとしてテスト
supabase db execute --query "
SET ROLE anon;
SELECT * FROM articles LIMIT 1;
"

# 認証ユーザーとしてテスト
supabase db execute --query "
SET ROLE authenticated;
SELECT * FROM subscriptions LIMIT 1;
"
```

## 8. ローカル開発環境

### Supabaseローカル環境起動

```bash
# Supabaseローカル環境を初期化
supabase init

# Docker経由でSupabaseを起動
supabase start

# 起動後、以下が利用可能：
# - API URL: http://localhost:54321
# - GraphiQL: http://localhost:54323
# - Studio: http://localhost:54323
# - Inbucket (メール): http://localhost:54324
# - DB URL: postgresql://postgres:postgres@localhost:54322/postgres
```

### ローカル環境変数

```bash
# ローカルSupabase用
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<local_anon_key>
SUPABASE_SERVICE_KEY=<local_service_key>
```

## 9. GitHub Actions連携

### Supabase CLIをGitHub Actionsで使用

`.github/workflows/supabase-deploy.yml`:

```yaml
name: Deploy to Supabase

on:
  push:
    branches:
      - main
    paths:
      - 'backend/security/**'
      - 'supabase/migrations/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: supabase/setup-cli@v1
        with:
          version: latest
      
      - name: Link to Supabase project
        run: supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      
      - name: Push migrations
        run: supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      
      - name: Execute RLS script
        run: supabase db execute --file backend/security/enable_rls.sql
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

### GitHub Secrets設定

```bash
# GitHub Secrets に追加
SUPABASE_ACCESS_TOKEN=sbp_...
SUPABASE_PROJECT_REF=xxxxxxxxxxxxx
```

## 10. トラブルシューティング

### エラー: "RLS Disabled in Public"

**原因**: Row Level Securityが有効化されていない

**解決**:
```bash
supabase db execute --file backend/security/enable_rls.sql
```

### エラー: "Permission denied"

**原因**: RLSポリシーでアクセスが拒否された

**解決**:
1. 正しいロール（anon/authenticated/service_role）を使用
2. ポリシー条件を確認
3. `auth.uid()`が正しく機能しているか確認

### エラー: "Could not connect to database"

**原因**: 接続文字列が間違っている

**解決**:
```bash
# Pooler URLを使用（推奨）
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Direct URLも利用可能（低レイテンシー）
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

## 11. セキュリティベストプラクティス

### 1. サービスロールキーの管理

```bash
# ❌ 絶対にフロントエンドで使用しない
# service_role keyは全権限を持つ

# ✅ バックエンドでのみ使用
# サーバーサイド処理でのみ使用
```

### 2. RLSポリシーの原則

```sql
-- ✅ 最小権限の原則
CREATE POLICY "Users can read own data"
ON public.users FOR SELECT
USING (auth.uid()::text = id);

-- ❌ 過度な権限
CREATE POLICY "Allow all"
ON public.users FOR ALL
USING (true);  -- これは避ける
```

### 3. 環境ごとの分離

- 開発: ローカルSupabase（`supabase start`）
- ステージング: Supabase Staging Project
- 本番: Supabase Production Project

## 12. 便利なSupabase CLIコマンド

### プロジェクト情報

```bash
# プロジェクト状態
supabase status

# プロジェクト設定
supabase projects list

# APIキー確認
supabase projects api-keys --project-ref <ref>
```

### データベース操作

```bash
# テーブル一覧
supabase db execute --query "SELECT tablename FROM pg_tables WHERE schemaname='public'"

# RLS状態確認
supabase db execute --query "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public'"

# データベースダンプ
supabase db dump -f backup.sql

# データベースリストア
supabase db restore backup.sql
```

### 型生成（TypeScript）

```bash
# Supabaseの型をTypeScriptに生成
supabase gen types typescript --linked > frontend/src/types/supabase.ts
```

## 13. 実行手順

### ステップ1: Supabase CLI インストール

```bash
brew install supabase/tap/supabase
supabase --version
```

### ステップ2: プロジェクトにリンク

```bash
cd /Users/Work/aica-sys
supabase login
supabase link --project-ref <your-project-ref>
```

### ステップ3: RLS有効化

```bash
# SQLスクリプト実行
supabase db execute --file backend/security/enable_rls.sql

# 確認
supabase db execute --query "
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname='public' 
ORDER BY tablename;
"
```

### ステップ4: マイグレーション同期

```bash
# リモートの変更をローカルに取得
supabase db pull

# ローカルの変更をリモートにプッシュ
supabase db push
```

### ステップ5: 環境変数設定

```bash
# プロジェクト情報確認
supabase projects api-keys --project-ref <ref>

# 環境変数に設定（Vercel/Render）
```

## 14. GitHub Actions統合例

完全な自動化ワークフロー：

```yaml
name: Supabase Deploy

on:
  push:
    branches: [main]
    paths:
      - 'backend/models/**'
      - 'backend/security/**'
      - 'supabase/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: supabase/setup-cli@v1
      
      - name: Link to Supabase
        run: |
          supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      
      - name: Apply migrations
        run: supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      
      - name: Apply RLS policies
        run: supabase db execute --file backend/security/enable_rls.sql
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      
      - name: Verify RLS
        run: |
          supabase db execute --query "
          SELECT tablename, rowsecurity 
          FROM pg_tables 
          WHERE schemaname='public' AND rowsecurity=false;
          "
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

## 15. チェックリスト

### セットアップ完了確認

- [ ] Supabase CLIインストール完了
- [ ] プロジェクトリンク完了
- [ ] RLS有効化完了（すべてのテーブル）
- [ ] RLSポリシー作成完了
- [ ] 環境変数設定完了（Vercel/Render）
- [ ] マイグレーション同期完了
- [ ] アクセステスト完了

### セキュリティ確認

- [ ] service_role keyがサーバーサイドのみで使用
- [ ] anon keyがフロントエンドで使用
- [ ] すべての公開テーブルでRLS有効
- [ ] ユーザーデータがauth.uid()で保護
- [ ] パスワードなど機密情報がGitにコミットされていない

## 16. 参考リソース

- [Supabase公式ドキュメント](https://supabase.com/docs)
- [Supabase CLI リファレンス](https://supabase.com/docs/reference/cli)
- [Row Level Security ガイド](https://supabase.com/docs/guides/auth/row-level-security)
- [Database Linter](https://supabase.com/docs/guides/database/database-linter)
- [Supabase + Next.js ガイド](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)

## 17. サポート

問題が発生した場合：
- [Supabase Discord](https://discord.supabase.com/)
- [GitHub Discussions](https://github.com/supabase/supabase/discussions)
- [Supabase Support](https://supabase.com/support)

