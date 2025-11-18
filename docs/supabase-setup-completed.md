# Supabase セットアップ完了レポート

**完了日時**: 2025-11-18

## ✅ 完了した設定

### 1. ローカル環境変数

**ファイル**: `backend/.env.local`

以下の設定が完了しました：

```bash
DATABASE_URL=postgresql://postgres:r2mSO4MkD2GLWLe4@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres
SUPABASE_URL=https://ndetbklyymekcifheqaj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. GitHub Secrets

以下の Secrets が設定されました：

- ✅ `DATABASE_URL` (Pooler 接続)
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_ANON_KEY`
- ✅ `SUPABASE_SERVICE_KEY`
- ✅ `SUPABASE_PROJECT_REF`

## ⚠️ 手作業が必要な設定

### 1. Vercel 環境変数の設定

**理由**: Vercel CLI のログインが必要

**手順**:

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. プロジェクトを選択
3. **Settings** → **Environment Variables** を開く
4. 以下を追加：

| 変数名                          | 値                                                                                                                                                                                                                            | 環境                             |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `DATABASE_URL`                  | `postgresql://postgres.ndetbklyymekcifheqaj:r2mSO4MkD2GLWLe4@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres`                                                                                                          | Production, Preview, Development |
| `SUPABASE_URL`                  | `https://ndetbklyymekcifheqaj.supabase.co`                                                                                                                                                                                    | Production, Preview, Development |
| `SUPABASE_ANON_KEY`             | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0`            | Production, Preview, Development |
| `SUPABASE_SERVICE_KEY`          | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzU5NDcxMiwiZXhwIjoyMDczMTcwNzEyfQ.8g1d_7fNn32CzuTvj7y4_gqmXjMrhtMsiPAn1cMQFjw` | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_URL`      | `https://ndetbklyymekcifheqaj.supabase.co`                                                                                                                                                                                    | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0`            | Production, Preview, Development |

**または、Vercel CLI で設定（ログイン後）:**

```bash
cd /Users/Work/aica-sys
vercel login
vercel env add DATABASE_URL production
# 値を入力: postgresql://postgres.ndetbklyymekcifheqaj:r2mSO4MkD2GLWLe4@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

vercel env add SUPABASE_URL production
# 値を入力: https://ndetbklyymekcifheqaj.supabase.co

vercel env add SUPABASE_ANON_KEY production
# 値を入力: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

vercel env add SUPABASE_SERVICE_KEY production
# 値を入力: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 値を入力: https://ndetbklyymekcifheqaj.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# 値を入力: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. データベース接続の確認

**手順**:

```bash
cd /Users/Work/aica-sys
python3 scripts/check_database_url.py
```

### 3. Supabase RLS ポリシーの適用確認

**手順**:

```bash
cd /Users/Work/aica-sys
supabase db execute --file supabase/migrations/20251015102236_enable_rls_policies.sql
```

## 📋 設定値まとめ

### プロジェクト情報

- **Project REF**: `ndetbklyymekcifheqaj`
- **Database Password**: `r2mSO4MkD2GLWLe4`
- **Region**: Northeast Asia (Tokyo)

### 接続 URL

**Direct 接続（開発用）:**

```
postgresql://postgres:r2mSO4MkD2GLWLe4@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres
```

**Pooler 接続（本番用・推奨）:**

```
postgresql://postgres.ndetbklyymekcifheqaj:r2mSO4MkD2GLWLe4@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

**API URL:**

```
https://ndetbklyymekcifheqaj.supabase.co
```

### API キー

**Anon Key:**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0
```

**Service Role Key:**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzU5NDcxMiwiZXhwIjoyMDczMTcwNzEyfQ.8g1d_7fNn32CzuTvj7y4_gqmXjMrhtMsiPAn1cMQFjw
```

## 🔄 次のステップ

1. ✅ ローカル環境変数設定完了
2. ✅ GitHub Secrets 設定完了
3. ⚠️ Vercel 環境変数の設定（手作業）
4. ⚠️ データベース接続テスト
5. ⚠️ RLS ポリシーの適用確認

## 📚 参考ドキュメント

- [Supabase 現状確認レポート](./supabase-current-status.md)
- [Supabase + Vercel セットアップガイド](./supabase-vercel-setup-guide.md)
- [データベース URL 確認ガイド](./database-url-check-guide.md)
