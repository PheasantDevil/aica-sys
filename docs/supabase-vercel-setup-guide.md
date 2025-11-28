# Supabase + Vercel セットアップ完全ガイド

## 📋 概要

[Supabase](https://supabase.com/)は、PostgreSQL ベースの BaaS（Backend as a Service）で、Vercel との連携実績が豊富です。このガイドでは、AICA-SyS プロジェクトで Supabase を使用するための完全なセットアップ手順を説明します。

## 🎯 必要な URL と設定値

### 1. Supabase プロジェクトの作成

1. [Supabase Dashboard](https://app.supabase.com/)にアクセス
2. 「New Project」をクリック
3. プロジェクト情報を入力：
   - **Name**: `aica-sys`（任意）
   - **Database Password**: 強力なパスワードを設定（**必ず保存**）
   - **Region**: `Northeast Asia (Tokyo)` を推奨
   - **Pricing Plan**: Free tier で開始可能

### 2. 必要な接続情報の取得

Supabase Dashboard → **Settings** → **Database** から以下を取得：

#### データベース接続 URL（2 種類）

**① Direct 接続（開発・低レイテンシー用）**

```
postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

**② Pooler 接続（本番・スケーリング用）** ⭐ 推奨

```
postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

**パラメータ説明：**

- `[PROJECT_REF]`: プロジェクトの Reference ID（例: `ndetbklyymekcifheqaj`）
- `[YOUR_PASSWORD]`: プロジェクト作成時に設定したデータベースパスワード

#### プロジェクト URL と API キー

Supabase Dashboard → **Settings** → **API** から取得：

```
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（anon public key）
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（service_role key - 秘密）
```

**重要：**

- `SUPABASE_ANON_KEY`: フロントエンドで使用（公開 OK）
- `SUPABASE_SERVICE_KEY`: バックエンドのみで使用（**絶対に公開しない**）

### 3. Project Reference ID の確認方法

1. Supabase Dashboard → **Settings** → **General**
2. **Reference ID** をコピー（例: `ndetbklyymekcifheqaj`）

## 🔧 環境変数の設定

### ローカル開発環境（backend/.env.local）

```bash
# Supabase Database（Direct接続 - 開発用）
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Supabase API
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=[ANON_KEY]
SUPABASE_SERVICE_KEY=[SERVICE_KEY]

# その他の設定
GROQ_API_KEY=[YOUR_GROQ_API_KEY]
ENVIRONMENT=development
DEBUG=True
```

### Vercel 環境変数設定

#### 方法 1: Vercel Dashboard から設定

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. プロジェクトを選択
3. **Settings** → **Environment Variables**
4. 以下を追加：

| 変数名                          | 値                                                                                                      | 環境                             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `DATABASE_URL`                  | `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` | Production, Preview, Development |
| `SUPABASE_URL`                  | `https://[PROJECT_REF].supabase.co`                                                                     | Production, Preview, Development |
| `SUPABASE_ANON_KEY`             | `[ANON_KEY]`                                                                                            | Production, Preview, Development |
| `SUPABASE_SERVICE_KEY`          | `[SERVICE_KEY]`                                                                                         | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_URL`      | `https://[PROJECT_REF].supabase.co`                                                                     | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `[ANON_KEY]`                                                                                            | Production, Preview, Development |
| `GROQ_API_KEY`                  | `[YOUR_GROQ_API_KEY]`                                                                                   | Production, Preview, Development |

**注意：**

- `NEXT_PUBLIC_` プレフィックスは、フロントエンドで使用する変数に必要
- `SUPABASE_SERVICE_KEY` はバックエンドのみで使用（`NEXT_PUBLIC_` は付けない）

#### 方法 2: Vercel CLI から設定

```bash
# Vercel CLIをインストール
npm i -g vercel

# ログイン
vercel login

# 環境変数を設定
vercel env add DATABASE_URL production
vercel env add SUPABASE_URL production
vercel env add SUPABASE_ANON_KEY production
vercel env add SUPABASE_SERVICE_KEY production
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
```

### GitHub Secrets 設定（CI/CD 用）

1. GitHub リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** をクリック
3. 以下を追加：

| Secret 名               | 値                                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`          | `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` |
| `SUPABASE_URL`          | `https://[PROJECT_REF].supabase.co`                                                                     |
| `SUPABASE_ANON_KEY`     | `[ANON_KEY]`                                                                                            |
| `SUPABASE_SERVICE_KEY`  | `[SERVICE_KEY]`                                                                                         |
| `SUPABASE_PROJECT_REF`  | `[PROJECT_REF]`                                                                                         |
| `SUPABASE_ACCESS_TOKEN` | `[ACCESS_TOKEN]`（Supabase CLI 用）                                                                     |

**Supabase Access Token の取得：**

1. [Supabase Dashboard](https://app.supabase.com/) → **Account Settings** → **Access Tokens**
2. **Generate new token** をクリック
3. トークンをコピー（一度しか表示されません）

## 🔗 Vercel と Supabase の連携

### 1. Supabase プロジェクトの設定

Supabase Dashboard → **Settings** → **API** → **CORS** で以下を追加：

```
https://your-project.vercel.app
https://*.vercel.app
```

### 2. Vercel 環境変数の確認

Vercel Dashboard → **Settings** → **Environment Variables** で以下が設定されているか確認：

- ✅ `DATABASE_URL`（Pooler 接続推奨）
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_ANON_KEY`
- ✅ `SUPABASE_SERVICE_KEY`
- ✅ `NEXT_PUBLIC_SUPABASE_URL`
- ✅ `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### 3. 接続テスト

Vercel にデプロイ後、以下で接続を確認：

```bash
# ローカルでテスト
curl https://your-project.vercel.app/api/health

# データベース接続確認
python3 scripts/check_database_url.py
```

## 📝 設定値の例（実際の形式）

### データベース URL 形式

**Direct 接続（開発用）：**

```
postgresql://postgres:your-password@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres
```

**Pooler 接続（本番用）：**

```
postgresql://postgres.ndetbklyymekcifheqaj:your-password@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

**違い：**

- Direct: `postgres@db.[REF].supabase.co`（低レイテンシー、接続数制限あり）
- Pooler: `postgres.[REF]@aws-0-ap-northeast-1.pooler.supabase.com`（スケーリング対応、推奨）

### API URL 形式

```
https://ndetbklyymekcifheqaj.supabase.co
```

### API キー形式

**Anon Key（公開可能）：**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1OTQ3MTIsImV4cCI6MjA3MzE3MDcxMn0.fsnTvaefyUayFmNusThORLRjTMpOvXQOBaf2yTOk1t0
```

**Service Role Key（秘密）：**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kZXRia2x5eW1la2NpZmhlcWFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzU5NDcxMiwiZXhwIjoyMDczMTcwNzEyfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🚀 セットアップ手順（まとめ）

### ステップ 1: Supabase プロジェクト作成

1. [Supabase Dashboard](https://app.supabase.com/)でプロジェクト作成
2. データベースパスワードを保存
3. Project Reference ID を確認

### ステップ 2: 接続情報の取得

1. **Settings** → **Database** → **Connection string** から URL をコピー
2. **Settings** → **API** から以下をコピー：
   - Project URL
   - `anon` `public` key
   - `service_role` `secret` key

### ステップ 3: 環境変数の設定

#### ローカル

```bash
cd backend
cp env.example .env.local
# .env.localを編集して上記の値を設定
```

#### Vercel

- Dashboard → Settings → Environment Variables で設定
- または `vercel env add` コマンドで設定

#### GitHub Secrets

- リポジトリ → Settings → Secrets and variables → Actions で設定

### ステップ 4: 接続確認

```bash
# ローカルで確認
python3 scripts/check_database_url.py

# Vercelデプロイ後確認
curl https://your-project.vercel.app/api/health
```

## 🔒 セキュリティ注意事項

1. **Service Role Key は絶対に公開しない**
   - フロントエンドコードに含めない
   - GitHub にコミットしない
   - 環境変数でのみ管理

2. **Anon Key は公開可能だが制限付き**
   - フロントエンドで使用可能
   - Row Level Security (RLS)で保護

3. **データベースパスワードの管理**
   - 強力なパスワードを使用
   - 定期的に変更
   - 環境変数でのみ管理

## 📚 参考リソース

- [Supabase 公式ドキュメント](https://supabase.com/docs)
- [Supabase + Vercel 統合ガイド](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)
- [Supabase Database 接続ガイド](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Vercel 環境変数ガイド](https://vercel.com/docs/concepts/projects/environment-variables)

## 🆘 トラブルシューティング

### 接続エラーが発生する場合

1. **URL 形式を確認**
   - Pooler 接続: `postgres.[REF]@pooler.supabase.com`
   - Direct 接続: `postgres@db.[REF].supabase.co`

2. **パスワードを確認**
   - Supabase Dashboard → Settings → Database → Reset password

3. **ネットワークを確認**
   - ファイアウォール設定
   - IP 制限の有無

### 環境変数が読み込まれない場合

1. **Vercel で再デプロイ**

   ```bash
   vercel --prod
   ```

2. **環境変数のプレフィックス確認**
   - フロントエンド用: `NEXT_PUBLIC_` が必要
   - バックエンド用: プレフィックス不要

3. **変数名のタイポ確認**
   - `DATABASE_URL`（大文字）
   - `SUPABASE_URL`（大文字）
