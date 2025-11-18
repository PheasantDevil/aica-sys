# 本番環境デプロイ確認チェックリスト

**作成日**: 2025-11-18  
**ステータス**: P0タスク - 実運用開始準備

---

## 📋 デプロイ確認項目

### 1. Vercel（フロントエンド）デプロイ確認

#### 1.1 デプロイ状態確認

**方法1: Vercel Dashboard**
1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. プロジェクト `aica-sys` を選択
3. **Deployments** タブで最新デプロイの状態を確認
   - ✅ Status: Ready
   - ✅ URL: https://aica-sys.vercel.app

**方法2: Vercel CLI**
```bash
cd /Users/Work/aica-sys
vercel login  # 初回のみ
vercel list
vercel inspect https://aica-sys.vercel.app
```

#### 1.2 環境変数確認

**必須環境変数**（Vercel Dashboard → Settings → Environment Variables）:

| 変数名 | 値 | 環境 | ステータス |
|--------|-----|------|-----------|
| `DATABASE_URL` | `postgresql://postgres.ndetbklyymekcifheqaj:r2mSO4MkD2GLWLe4@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` | Production, Preview, Development | ⚠️ 要設定 |
| `SUPABASE_URL` | `https://ndetbklyymekcifheqaj.supabase.co` | Production, Preview, Development | ⚠️ 要設定 |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development | ⚠️ 要設定 |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development | ⚠️ 要設定 |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://ndetbklyymekcifheqaj.supabase.co` | Production, Preview, Development | ⚠️ 要設定 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development | ⚠️ 要設定 |
| `NEXTAUTH_URL` | `https://aica-sys.vercel.app` | Production | ✅ 設定済み |
| `NEXT_PUBLIC_BASE_URL` | `https://aica-sys.vercel.app` | Production | ✅ 設定済み |
| `NEXT_PUBLIC_API_URL` | `https://aica-sys-backend.onrender.com` | Production | ✅ 設定済み |
| `ENVIRONMENT` | `production` | Production | ✅ 設定済み |

**設定方法（Vercel CLI）**:
```bash
cd /Users/Work/aica-sys
vercel login
vercel env add DATABASE_URL production
# 値を入力（Pooler接続URL）
vercel env add SUPABASE_URL production
# 値を入力
vercel env add SUPABASE_ANON_KEY production
# 値を入力
vercel env add SUPABASE_SERVICE_KEY production
# 値を入力
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# 値を入力
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# 値を入力
```

#### 1.3 動作確認

```bash
# フロントエンドURLにアクセス
curl -I https://aica-sys.vercel.app

# ヘルスチェック
curl https://aica-sys.vercel.app/api/health
```

---

### 2. Render（バックエンド）デプロイ確認

#### 2.1 デプロイ状態確認

**方法1: Render Dashboard**
1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. サービス `aica-sys-backend` を選択
3. **Events** タブで最新デプロイの状態を確認
   - ✅ Status: Live
   - ✅ URL: https://aica-sys-backend.onrender.com

**方法2: Render CLI**
```bash
render services -o json | jq '.[] | select(.name == "aica-sys-backend")'
render deploys [service-id] -o json
```

#### 2.2 環境変数確認

**必須環境変数**（Render Dashboard → Environment）:

| 変数名 | 値 | ステータス |
|--------|-----|-----------|
| `PYTHON_VERSION` | `3.11.0` | ✅ 設定済み（render.yaml） |
| `DATABASE_URL` | `postgresql://postgres.ndetbklyymekcifheqaj:r2mSO4MkD2GLWLe4@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` | ⚠️ 要設定 |
| `ENVIRONMENT` | `production` | ✅ 設定済み（render.yaml） |
| `CORS_ORIGINS` | `https://aica-sys.vercel.app,https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app` | ✅ 設定済み（render.yaml） |
| `GROQ_API_KEY` | （GitHub Secretsから取得） | ⚠️ 要設定 |
| `STRIPE_SECRET_KEY` | （Stripe本番キー） | ⚠️ 要設定（次のステップ） |
| `STRIPE_PUBLISHABLE_KEY` | （Stripe本番キー） | ⚠️ 要設定（次のステップ） |
| `NEXTAUTH_SECRET` | （シークレット） | ⚠️ 要設定 |
| `GOOGLE_CLIENT_ID` | （Google OAuth） | ⚠️ 要設定 |
| `GOOGLE_CLIENT_SECRET` | （Google OAuth） | ⚠️ 要設定 |

**設定方法（Render Dashboard）**:
1. Render Dashboard → サービス選択
2. **Environment** タブ
3. **Add Environment Variable** をクリック
4. 変数名と値を入力して保存

#### 2.3 動作確認

```bash
# バックエンドURLにアクセス
curl -I https://aica-sys-backend.onrender.com

# ヘルスチェック
curl https://aica-sys-backend.onrender.com/health

# API動作確認
curl https://aica-sys-backend.onrender.com/api/health
```

---

### 3. データベース接続確認

#### 3.1 Supabase接続確認

```bash
cd /Users/Work/aica-sys
python3 scripts/check_database_url.py
```

#### 3.2 マイグレーション状態確認

```bash
cd /Users/Work/aica-sys/backend
# Supabase接続URLを設定
export DATABASE_URL="postgresql://postgres.ndetbklyymekcifheqaj:r2mSO4MkD2GLWLe4@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
python3 -m alembic current
```

---

### 4. CI/CD確認

#### 4.1 GitHub Actions確認

1. [GitHub Actions](https://github.com/PheasantDevil/aica-sys/actions)を開く
2. 最新のワークフロー実行を確認
   - ✅ `backend-ci-cd.yml`: 成功
   - ✅ `frontend-ci-cd.yml`: 成功
   - ✅ `daily-articles.yml`: 成功（DATABASE_URL設定後）

#### 4.2 自動デプロイ確認

- ✅ Vercel: `main`ブランチへのpushで自動デプロイ
- ✅ Render: `main`ブランチへのpushで自動デプロイ（`autoDeploy: true`）

---

## ✅ 完了チェックリスト

### Vercel
- [ ] デプロイ状態確認（Status: Ready）
- [ ] 環境変数設定（Supabase関連）
- [ ] 動作確認（URLアクセス、ヘルスチェック）

### Render
- [ ] デプロイ状態確認（Status: Live）
- [ ] 環境変数設定（DATABASE_URL, GROQ_API_KEY等）
- [ ] 動作確認（URLアクセス、ヘルスチェック）

### データベース
- [ ] Supabase接続確認
- [ ] マイグレーション状態確認

### CI/CD
- [ ] GitHub Actions正常動作確認
- [ ] 自動デプロイ動作確認

---

## 🔄 次のステップ

1. ✅ 本番環境デプロイ確認（このドキュメント）
2. ⏳ Stripe本番設定（次のステップ）
3. ⏳ テスト決済実行

---

## 📚 参考ドキュメント

- [Supabase セットアップ完了レポート](./supabase-setup-completed.md)
- [Vercel デプロイメントガイド](./vercel-deployment-guide.md)
- [Render デプロイメントガイド](./render-deployment-guide.md)
- [実装ステータスレポート](./implementation-status-report-2025-11.md)

