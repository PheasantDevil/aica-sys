# 環境変数設定ガイド

## 概要

AICA-SySの動作に必要な環境変数の設定方法を説明します。

## フロントエンド環境変数 (.env.local)

`frontend/.env.local` ファイルを作成し、以下の内容を設定してください：

```env
# NextAuth.js 設定
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-key-here

# Google OAuth 設定
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Stripe 決済設定
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-stripe-webhook-secret

# Resend メール送信設定
RESEND_API_KEY=re_your-resend-api-key

# Google Analytics 設定
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# API 設定
NEXT_PUBLIC_API_URL=http://localhost:8000

# ベースURL設定
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## バックエンド環境変数 (.env)

`backend/.env` ファイルを作成し、以下の内容を設定してください：

```env
# データベース設定
DATABASE_URL=postgresql://user:password@localhost:5432/aica_sys

# Redis 設定
REDIS_URL=redis://localhost:6379

# Qdrant 設定
QDRANT_URL=http://localhost:6333

# AI API 設定
GOOGLE_AI_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key

# GitHub API 設定
GITHUB_TOKEN=your-github-token

# セキュリティ設定
SECRET_KEY=your-secret-key-here

# デバッグ設定
DEBUG=True
```

## 環境変数の取得方法

### 1. Google OAuth 設定

#### 1.1 Google Cloud Console でプロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. プロジェクト名: `aica-sys`

#### 1.2 OAuth 同意画面の設定

1. 「APIs & Services」→「OAuth consent screen」
2. 「External」を選択
3. アプリ名: `AICA-SyS`
4. ユーザーサポートメール: あなたのメールアドレス
5. 開発者連絡先情報: あなたのメールアドレス

#### 1.3 OAuth クライアントIDの作成

1. 「APIs & Services」→「Credentials」
2. 「Create Credentials」→「OAuth client ID」
3. アプリケーションタイプ: 「Web application」
4. 名前: `AICA-SyS Web Client`
5. 承認済みのリダイレクトURI:
   - `http://localhost:3000/api/auth/callback/google`
   - `https://your-domain.com/api/auth/callback/google`

#### 1.4 クライアントIDとシークレットを取得

- `GOOGLE_CLIENT_ID`: クライアントID
- `GOOGLE_CLIENT_SECRET`: クライアントシークレット

### 2. Stripe 決済設定

#### 2.1 Stripe アカウント作成

1. [Stripe](https://stripe.com/) にアクセス
2. アカウントを作成
3. ダッシュボードにログイン

#### 2.2 API キーの取得

1. ダッシュボードの「Developers」→「API keys」
2. テスト用キーを取得:
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Publishable key
   - `STRIPE_SECRET_KEY`: Secret key

#### 2.3 Webhook の設定

1. 「Developers」→「Webhooks」
2. 「Add endpoint」をクリック
3. エンドポイントURL: `https://your-domain.com/api/stripe/webhook`
4. イベントを選択:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Webhook シークレットを取得: `STRIPE_WEBHOOK_SECRET`

### 3. Resend メール送信設定

#### 3.1 Resend アカウント作成

1. [Resend](https://resend.com/) にアクセス
2. アカウントを作成
3. ダッシュボードにログイン

#### 3.2 API キーの取得

1. 「API Keys」セクション
2. 「Create API Key」をクリック
3. キー名: `AICA-SyS Production`
4. API キーを取得: `RESEND_API_KEY`

#### 3.3 ドメインの設定

1. 「Domains」セクション
2. 「Add Domain」をクリック
3. ドメイン名: `your-domain.com`
4. DNS レコードを設定
5. ドメインの検証を完了

### 4. Google Analytics 設定

#### 4.1 Google Analytics アカウント作成

1. [Google Analytics](https://analytics.google.com/) にアクセス
2. アカウントを作成
3. プロパティを作成

#### 4.2 データストリームの設定

1. 「Admin」→「Data Streams」
2. 「Add stream」→「Web」
3. ウェブサイトURL: `https://your-domain.com`
4. ストリーム名: `AICA-SyS Website`
5. Measurement ID を取得: `NEXT_PUBLIC_GA_ID`

### 5. AI API 設定

#### 5.1 Google AI Studio 設定

1. [Google AI Studio](https://aistudio.google.com/) にアクセス
2. アカウントでログイン
3. 「Get API key」をクリック
4. API キーを作成: `GOOGLE_AI_API_KEY`

#### 5.2 OpenAI API 設定

1. [OpenAI Platform](https://platform.openai.com/) にアクセス
2. アカウントを作成
3. 「API Keys」セクション
4. 「Create new secret key」をクリック
5. API キーを作成: `OPENAI_API_KEY`

### 6. GitHub API 設定

#### 6.1 GitHub Personal Access Token 作成

1. [GitHub](https://github.com/) にログイン
2. 「Settings」→「Developer settings」
3. 「Personal access tokens」→「Tokens (classic)」
4. 「Generate new token」をクリック
5. スコープを選択:
   - `repo` (リポジトリアクセス)
   - `read:user` (ユーザー情報読み取り)
6. トークンを生成: `GITHUB_TOKEN`

### 7. セキュリティキーの生成

#### 7.1 NextAuth シークレット

```bash
openssl rand -base64 32
```

#### 7.2 アプリケーションシークレット

```bash
openssl rand -base64 32
```

## 本番環境での設定

### Vercel 環境変数設定

1. Vercel ダッシュボードにアクセス
2. プロジェクトを選択
3. 「Settings」→「Environment Variables」
4. 上記の環境変数をすべて追加

### GCP Cloud Functions 環境変数設定

1. Google Cloud Console にアクセス
2. Cloud Functions を選択
3. 関数を選択
4. 「Edit」→「Runtime, build, connections and security settings」
5. 「Runtime environment variables」で環境変数を設定

## 環境変数の確認

### フロントエンド

```bash
cd frontend
npm run dev
```

### バックエンド

```bash
cd backend
python main.py
```

## トラブルシューティング

### よくある問題

1. **環境変数が読み込まれない**: ファイル名とパスを確認
2. **API キーが無効**: キーの形式と権限を確認
3. **CORS エラー**: ドメイン設定を確認
4. **認証エラー**: OAuth 設定を確認

### デバッグ方法

```bash
# フロントエンド
console.log(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)

# バックエンド
print(os.getenv('GOOGLE_AI_API_KEY'))
```

## セキュリティ注意事項

1. **環境変数ファイルをGitにコミットしない**
2. **本番環境のAPIキーは適切に管理**
3. **定期的にAPIキーをローテーション**
4. **最小権限の原則を適用**

## 次のステップ

環境変数設定完了後:

1. ローカル動作確認
2. データベース初期化
3. 基本機能テスト
4. 本番デプロイ準備
