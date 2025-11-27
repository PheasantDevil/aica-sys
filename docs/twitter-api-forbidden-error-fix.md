# Twitter API Forbidden エラー修正ガイド

## エラー内容

```text
Twitter API forbidden. Check account permissions.
```

このエラーは、Twitter API の権限設定の問題で発生します。認証情報は正しく設定されていますが、Twitter Developer Portal でのアプリの権限設定が不適切な場合に発生します。

## 原因

以下のいずれかが原因です：

1. **アプリの権限が「Read-only」になっている**
   - Twitter Developer Portal でアプリの権限が「Read and Write」に設定されていない

2. **Bearer Token または OAuth 認証情報が無効**
   - 認証情報が期限切れまたは無効になっている

3. **Twitter アカウントが制限されている**
   - アカウントが一時的に制限されている、または凍結されている

4. **Twitter Developer アカウントのアクセスレベルが不足**
   - 無料プランでは一部の機能が制限されている可能性がある

## 修正手順（手動で実施が必要）

### Step 1: Twitter Developer Portal にアクセス

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)にアクセス
2. ログインして、該当するアプリを選択

### Step 2: Callback URI の設定

1. アプリのダッシュボードで「Settings」をクリック
2. 「User authentication settings」セクションを開く
3. **Callback URI / Redirect URL** を設定
   - このプロジェクトでは自動投稿用のスクリプトを使用しているため、実際の OAuth 認証フローは使用しません
   - 以下のいずれかを設定してください：
     - `https://aica-sys.vercel.app` （プロジェクトのベース URL）
     - `http://localhost:3000` （ローカル開発用、テスト目的）
     - `https://aica-sys.vercel.app/api/auth/callback/twitter` （将来の拡張用）
   - **推奨**: `https://aica-sys.vercel.app` を設定
4. **Website URL** も設定（必要に応じて）
   - `https://aica-sys.vercel.app` を設定
5. 設定を保存

### Step 3: アプリの権限設定を確認・変更

1. 「User authentication settings」セクションで、以下の設定を確認：
2. **App permissions** で **「Read and Write」** を選択
   - 「Read-only」になっている場合は、「Read and Write」に変更
3. **Type of App** を確認
   - 「Web App, Automated App or Bot」を選択（推奨）
4. 変更を保存

### Step 4: 認証情報を再生成

**重要**: OAuth 2.0 Client ID and Client Secret を変更した場合の対応

1. 「Keys and tokens」タブを開く

2. **Bearer Token の確認・再生成**
   - OAuth 2.0 Client ID/Secret を変更した場合、**Bearer Token は再生成が必要な場合があります**
   - 「Bearer Token」セクションで、既存の Bearer Token が有効か確認
   - エラーが発生する場合は「Regenerate」をクリックして再生成
   - 新しい Bearer Token をコピー

3. **OAuth 1.0a 認証情報の確認**
   - **API Key (Consumer Key) と API Secret (Consumer Secret)** は、OAuth 2.0 Client ID/Secret とは**独立している**ため、通常は再生成不要
   - ただし、アプリの設定を大幅に変更した場合は、再生成が必要な場合があります
   - 「API Key and Secret」セクションで、API Key と Secret を確認
   - 「Access Token and Secret」セクションで、Access Token と Secret を確認
   - エラーが発生する場合は再生成

4. **推奨手順**:
   - まず既存の認証情報で動作確認
   - エラーが発生する場合のみ、順次再生成
   - Bearer Token → API Key/Secret → Access Token/Secret の順で確認

### Step 5: GitHub Secrets を更新

1. [GitHub Repository Settings](https://github.com/PheasantDevil/aica-sys/settings/secrets/actions)にアクセス
2. 以下の Secrets を更新：
   - `TWITTER_BEARER_TOKEN` - 新しい Bearer Token を設定
   - `TWITTER_API_KEY` - API Key を設定（変更した場合）
   - `TWITTER_API_SECRET` - API Secret を設定（変更した場合）
   - `TWITTER_ACCESS_TOKEN` - Access Token を設定（変更した場合）
   - `TWITTER_ACCESS_TOKEN_SECRET` - Access Token Secret を設定（変更した場合）

### Step 6: アプリの設定を確認

1. 「Settings」タブで、以下の設定を確認：
   - **App permissions** で **Read and Write** が選択されている
   - **Callback URI** が正しく設定されている（`https://aica-sys.vercel.app` など）
   - **Website URL** が設定されている（`https://aica-sys.vercel.app`）
   - **App environment** が「Production」になっている

### Step 7: Twitter アカウントの状態を確認

1. 通常の Twitter アカウントにログイン
2. アカウントが制限されていないか確認
3. 必要に応じて、Twitter サポートに問い合わせ

### Step 8: ワークフローを再実行

1. GitHub Actions でワークフローを再実行
2. エラーが解消されているか確認

## Callback URI について

### なぜ Callback URI が必要なのか

Twitter Developer Portal で「Read and Write」権限を有効にするには、Callback URI の設定が必要です。これは、OAuth 認証フローで使用されるリダイレクト URI です。

### このプロジェクトでの Callback URI の使い方

このプロジェクトでは、自動投稿用のスクリプトを使用しているため、実際の OAuth 認証フロー（ユーザーがブラウザで認証する）は使用していません。代わりに、事前に生成された Access Token と Secret を使用しています。

しかし、Twitter Developer Portal で「Read and Write」権限を有効にするには、Callback URI の設定が必要です。以下のいずれかを設定してください：

- **推奨**: `https://aica-sys.vercel.app`
- **代替**: `http://localhost:3000` （ローカル開発用）
- **将来の拡張用**: `https://aica-sys.vercel.app/api/auth/callback/twitter`

### Callback URI の設定方法

1. Twitter Developer Portal でアプリを選択
2. 「Settings」→「User authentication settings」を開く
3. 「Callback URI / Redirect URL」フィールドに上記のいずれかを入力
4. 「Website URL」フィールドにも `https://aica-sys.vercel.app` を入力（必要に応じて）
5. 設定を保存

## 認証情報の関係性について

### OAuth 2.0 Client ID/Secret と Bearer Token の関係

- **OAuth 2.0 Client ID/Secret**: 新しい OAuth 2.0 認証方式で使用される認証情報
- **Bearer Token**: OAuth 2.0 で使用される認証トークン（Client ID/Secret から生成される場合がある）
- **API Key/Secret (OAuth 1.0a)**: 従来の OAuth 1.0a 認証方式で使用される認証情報（Client ID/Secret とは独立）

### 設定変更後の対応

**OAuth 2.0 Client ID/Secret を変更した場合**:

1. **Bearer Token**: 再生成が必要な場合があります
   - 既存の Bearer Token でエラーが発生する場合は再生成
   - 動作する場合はそのまま使用可能

2. **API Key/Secret (OAuth 1.0a)**: 通常は再生成不要
   - OAuth 2.0 Client ID/Secret とは独立しているため
   - ただし、アプリの設定を大幅に変更した場合は再生成が必要な場合があります

3. **Access Token/Secret**: 通常は再生成不要
   - API Key/Secret と同様に、OAuth 2.0 Client ID/Secret とは独立

### 安全な対応方法

1. まず既存の認証情報で動作確認
2. エラーが発生する場合のみ、順次再生成
3. 再生成した認証情報は、すぐに GitHub Secrets に更新

## トラブルシューティング

### 問題: Callback URI の設定が求められる

**原因**: Twitter Developer Portal で「Read and Write」権限を有効にするには、Callback URI の設定が必要です。

**対処法**:

1. 上記の「Callback URI について」セクションを参照
2. `https://aica-sys.vercel.app` を設定
3. 設定を保存してから、再度権限設定を確認

### 問題: 「Read and Write」権限が選択できない

**原因**: Twitter Developer アカウントのアクセスレベルが不足している可能性があります。

**対処法**:

1. Twitter Developer Portal でアカウントの状態を確認
2. 必要に応じて、Twitter Developer アカウントをアップグレード
3. アカウントの審査が完了しているか確認

### 問題: Bearer Token を再生成してもエラーが続く

**原因**: OAuth 1.0a 認証情報が無効になっている可能性があります。

**対処法**:

1. OAuth 1.0a 認証情報（API Key, Secret, Access Token, Secret）をすべて再生成
2. GitHub Secrets をすべて更新
3. ワークフローを再実行

### 問題: 権限を変更してもエラーが続く

**原因**: 変更が反映されるまで時間がかかる場合があります。

**対処法**:

1. 数分待ってから再実行
2. Twitter Developer Portal で設定が正しく保存されているか確認
3. ブラウザのキャッシュをクリアして再確認

## 確認方法

修正が完了したかどうかを確認するには、以下のコマンドをローカルで実行：

```bash
cd /Users/Work/aica-sys
python3 scripts/test_twitter_connection.py
```

正常に動作する場合、以下のメッセージが表示されます：

```text
✅ Twitter API connection successful!
```

## 参考資料

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [Twitter API Authentication](https://developer.twitter.com/en/docs/authentication/overview)
