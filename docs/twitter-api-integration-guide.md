# Twitter API 統合ガイド

**作成日**: 2025-11-18  
**ステータス**: P1 タスク - 認知度向上自動化

---

## 📋 概要

AICA-SyS の Twitter API 統合により、記事公開時の自動投稿や定期投稿が可能になります。

## 🎯 実装内容

### 実装済み機能

1. **TwitterClient** (`backend/services/twitter_client.py`)

   - Twitter API v2 統合
   - OAuth 2.0 (Bearer Token) サポート
   - OAuth 1.0a サポート（メディアアップロード用）
   - ツイート投稿機能
   - メディアアップロード機能
   - 認証確認機能

2. **SocialMediaService** (`backend/services/social_media_service.py`)

   - 記事投稿機能
   - サービス紹介投稿機能
   - トレンド情報投稿機能
   - ツイートフォーマット機能
   - ハッシュタグ管理

3. **テストスクリプト** (`scripts/test_twitter_connection.py`)
   - 環境変数確認
   - API 接続テスト
   - ツイートフォーマットテスト

---

## 🔧 セットアップ手順

### Step 1: Twitter Developer アカウント作成

1. [Twitter Developer Portal](https://developer.twitter.com/)にアクセス
2. 「Sign up」をクリックしてアカウント作成
3. 開発者アカウント申請（審査が必要な場合あり）

### Step 2: Twitter App 作成

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)にログイン
2. 「Create App」をクリック
3. アプリ情報を入力：
   ```
   App name: AICA-SyS
   App environment: Production
   Use case: Making automated posts
   ```

### Step 3: API キー取得

#### Option 1: OAuth 2.0 (推奨) - Bearer Token のみ

1. 「Keys and tokens」タブを開く
2. 「Bearer Token」セクションで「Generate」をクリック
3. 生成された Bearer Token をコピー

**メリット**:

- シンプルな設定
- セキュリティが高い
- 基本的なツイート投稿に十分

**デメリット**:

- メディアアップロードには使用不可

#### Option 2: OAuth 1.0a - 完全な認証情報

1. 「Keys and tokens」タブを開く
2. 以下をコピー：
   - **API Key**: `TWITTER_API_KEY`
   - **API Secret**: `TWITTER_API_SECRET`
3. 「Access Token and Secret」セクションで「Generate」をクリック
4. 以下をコピー：
   - **Access Token**: `TWITTER_ACCESS_TOKEN`
   - **Access Token Secret**: `TWITTER_ACCESS_TOKEN_SECRET`

**メリット**:

- メディアアップロードに対応
- より高度な機能が使用可能

**デメリット**:

- 設定が複雑
- より多くの認証情報を管理する必要がある

### Step 4: 環境変数設定

#### ローカル開発環境

`backend/.env.local`に以下を追加：

```bash
# Option 1: OAuth 2.0 (推奨)
TWITTER_BEARER_TOKEN=your-bearer-token-here

# Option 2: OAuth 1.0a (メディアアップロードが必要な場合)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
```

#### Vercel 環境変数

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. プロジェクトを選択
3. 「Settings」→「Environment Variables」
4. 以下を追加（Production, Preview 環境）：
   - `TWITTER_BEARER_TOKEN`
   - または `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`

#### Render 環境変数

1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. サービスを選択
3. 「Environment」タブ
4. 以下を追加：
   - `TWITTER_BEARER_TOKEN`
   - または `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`

#### GitHub Secrets

1. [GitHub Settings](https://github.com/PheasantDevil/aica-sys/settings/secrets/actions)
2. 以下を追加：
   - `TWITTER_BEARER_TOKEN`
   - または `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`

### Step 5: 依存関係インストール

```bash
cd backend
pip install tweepy>=5.0.0
```

または、`requirements.txt`が更新されている場合：

```bash
pip install -r requirements.txt
```

### Step 6: 接続テスト

```bash
cd /Users/Work/aica-sys
python3 scripts/test_twitter_connection.py
```

---

## 📝 使用方法

### 基本的な使用例

```python
from services.social_media_service import SocialMediaService

# サービス初期化
service = SocialMediaService()

# 記事投稿
result = service.post_article(
    title="TypeScript 5.6 Released",
    summary="TypeScript 5.6 introduces new decorators...",
    url="https://aica-sys.vercel.app/articles/typescript-5-6",
    hashtags=["#TypeScript", "#JavaScript"]
)

# サービス紹介投稿
result = service.post_service_introduction(
    message="🚀 AICA-SySが始動しました！\n\nTypeScriptエコシステムの最新トレンドをAIが毎日自動分析・記事化📝",
    hashtags=["#TypeScript", "#AI", "#開発ツール"]
)

# トレンド情報投稿
result = service.post_trend_info(
    trend_title="TypeScript Decorators",
    trend_summary="Decoratorsが本番環境で使用可能になりました",
    url="https://aica-sys.vercel.app/trends/typescript-decorators"
)
```

### 記事生成スクリプトでの自動投稿

`scripts/generate_daily_article.py` では、記事が保存されたタイミングで `SocialMediaService` を呼び出し、Twitter へ自動投稿するフックを追加済みです。

```bash
cd /Users/Work/aica-sys
python3 scripts/generate_daily_article.py             # 本番データで実行
python3 scripts/generate_daily_article.py --mock-data # モックデータでテスト（投稿はスキップ）
python3 scripts/generate_daily_article.py --skip-social-post  # 投稿せずに実行
```

実行結果に `📣 Posted to Twitter` が表示されれば投稿成功です。`--skip-social-post` オプションを使うと、Twitter への投稿を行わずに記事生成のみをテストできます。

---

## 🔒 セキュリティ注意事項

1. **認証情報の管理**

   - API キーは絶対に公開しない
   - GitHub にコミットしない（`.env.local`は`.gitignore`に含まれている）
   - 環境変数として安全に管理

2. **レート制限**

   - Twitter API にはレート制限がある
   - `wait_on_rate_limit=True`が設定されているため、自動的に待機する

3. **OAuth 2.0 vs OAuth 1.0a**
   - 基本的な投稿には OAuth 2.0 (Bearer Token)で十分
   - メディアアップロードが必要な場合のみ OAuth 1.0a を使用

---

## 🧪 テスト

### 接続テスト

```bash
python3 scripts/test_twitter_connection.py
```

### ツイート投稿テスト（Dry Run）

スクリプト内でツイートフォーマットをテスト（実際には投稿しない）

### 定期投稿ワークフロー

- GitHub Actions: `.github/workflows/social-media-post.yml`
  - 毎日 03:00 UTC に実行
  - 月・水・金はサービス紹介を自動投稿
  - 毎日トレンドハイライトを投稿
- `workflow_dispatch` で手動実行も可能（例: 新機能告知を即時投稿したい場合）
- 実行コマンド: `python scripts/post_to_social_media.py ...`
- `--dry-run` オプションで実際に投稿せず内容確認ができる
- 環境変数は GitHub Secrets (`TWITTER_*`) から読み込まれます

---

## 📚 参考リソース

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [tweepy Documentation](https://docs.tweepy.org/)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [Twitter API Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)

---

## 🔄 次のステップ

1. ✅ Twitter API 統合（このドキュメント）
2. ✅ 記事公開時自動投稿フック実装
3. ✅ 定期自動投稿ワークフロー作成
4. ⏳ SEO 基本設定

---

## ⚠️ トラブルシューティング

### エラー: "tweepy not installed"

```bash
pip install tweepy>=5.0.0
```

### エラー: "Twitter API credentials not set"

環境変数が正しく設定されているか確認：

```bash
python3 scripts/test_twitter_connection.py
```

### エラー: "Twitter API unauthorized"

- API キーが正しいか確認
- Twitter Developer Portal でアプリの権限を確認
- Bearer Token が有効期限内か確認

### エラー: "Rate limit exceeded"

- レート制限に達しています
- `wait_on_rate_limit=True`が設定されているため、自動的に待機します
- 投稿頻度を調整することを検討してください
