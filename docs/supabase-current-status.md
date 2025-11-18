# Supabase 現状確認レポート

**確認日時**: 2025-11-18  
**確認者**: Supabase CLI

## 📊 プロジェクト情報

### 基本情報

- **プロジェクト名**: AICA-SyS-DB
- **Reference ID**: `ndetbklyymekcifheqaj`
- **リージョン**: Northeast Asia (Tokyo)
- **作成日**: 2025-09-11 12:45:12 UTC
- **ステータス**: ✅ リンク済み

### 接続URL

**Supabase API URL:**
```
https://ndetbklyymekcifheqaj.supabase.co
```

**データベース接続URL（2種類）:**

1. **Direct接続（開発用）:**
   ```
   postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres
   ```

2. **Pooler接続（本番用・推奨）:**
   ```
   postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
   ```

## 🔑 APIキー

### Anon Key（公開可能・フロントエンド用）

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0
```

### Service Role Key（秘密・バックエンド専用）

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzU5NDcxMiwiZXhwIjoyMDczMTcwNzEyfQ.8g1d_7fNn32CzuTvj7y4_gqmXjMrhtMsiPAn1cMQFjw
```

⚠️ **重要**: Service Role Keyは絶対に公開しないでください！

## 🔧 ローカル環境の状態

### 環境変数設定状況

- ❌ `DATABASE_URL`: 未設定（現在SQLiteを使用）
- ❌ `SUPABASE_URL`: 未設定
- ❌ `SUPABASE_ANON_KEY`: 未設定
- ❌ `SUPABASE_SERVICE_KEY`: 未設定
- ❌ `NEXT_PUBLIC_SUPABASE_URL`: 未設定
- ❌ `NEXT_PUBLIC_SUPABASE_ANON_KEY`: 未設定

### Supabase CLI

- **バージョン**: v2.54.11（インストール済み）
- **最新バージョン**: v2.58.5
- **アップデート推奨**: あり

### マイグレーション

- ✅ RLSポリシー: `supabase/migrations/20251015102236_enable_rls_policies.sql` が存在

## 📝 必要な設定

### 1. ローカル環境変数の設定

`backend/.env.local` を作成して以下を設定：

```bash
# Supabase Database（Pooler接続推奨）
DATABASE_URL=postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Supabase API
SUPABASE_URL=https://ndetbklyymekcifheqaj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzU5NDcxMiwiZXhwIjoyMDczMTcwNzEyfQ.8g1d_7fNn32CzuTvj7y4_gqmXjMrhtMsiPAn1cMQFjw
```

**注意**: `[PASSWORD]` はSupabase Dashboard → Settings → Database から取得してください。

### 2. Vercel環境変数の設定

Vercel Dashboard → Settings → Environment Variables で以下を設定：

| 変数名 | 値 |
|--------|-----|
| `DATABASE_URL` | `postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` |
| `SUPABASE_URL` | `https://ndetbklyymekcifheqaj.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`（上記のAnon Key） |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`（上記のService Role Key） |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://ndetbklyymekcifheqaj.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`（上記のAnon Key） |

### 3. GitHub Secretsの設定

GitHubリポジトリ → Settings → Secrets and variables → Actions で以下を設定：

| Secret名 | 値 |
|----------|-----|
| `DATABASE_URL` | `postgresql://postgres.ndetbklyymekcifheqaj:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` |
| `SUPABASE_URL` | `https://ndetbklyymekcifheqaj.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_PROJECT_REF` | `ndetbklyymekcifheqaj` |

## 🔄 次のアクション

1. ✅ Supabase CLIインストール済み
2. ✅ プロジェクトリンク済み
3. ⚠️ ローカル環境変数の設定が必要
4. ⚠️ Vercel環境変数の設定が必要
5. ⚠️ GitHub Secretsの設定が必要
6. ⚠️ データベースパスワードの取得が必要

## 📚 参考

- [Supabase Dashboard](https://app.supabase.com/project/ndetbklyymekcifheqaj)
- [Supabase + Vercel セットアップガイド](./supabase-vercel-setup-guide.md)
- [データベースURL確認ガイド](./database-url-check-guide.md)

