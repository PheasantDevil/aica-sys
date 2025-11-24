# Twitter API Forbidden エラー修正ガイド

## エラー内容

```
Twitter API forbidden. Check account permissions.
```

このエラーは、Twitter APIの権限設定の問題で発生します。認証情報は正しく設定されていますが、Twitter Developer Portalでのアプリの権限設定が不適切な場合に発生します。

## 原因

以下のいずれかが原因です：

1. **アプリの権限が「Read-only」になっている**
   - Twitter Developer Portalでアプリの権限が「Read and Write」に設定されていない

2. **Bearer TokenまたはOAuth認証情報が無効**
   - 認証情報が期限切れまたは無効になっている

3. **Twitterアカウントが制限されている**
   - アカウントが一時的に制限されている、または凍結されている

4. **Twitter Developerアカウントのアクセスレベルが不足**
   - 無料プランでは一部の機能が制限されている可能性がある

## 修正手順（手動で実施が必要）

### Step 1: Twitter Developer Portalにアクセス

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)にアクセス
2. ログインして、該当するアプリを選択

### Step 2: アプリの権限設定を確認・変更

1. アプリのダッシュボードで「Settings」をクリック
2. 「User authentication settings」セクションを確認
3. **「Read and Write」権限が有効になっているか確認**
   - 「Read-only」になっている場合は、「Read and Write」に変更
4. 変更を保存

### Step 3: 認証情報を再生成

1. 「Keys and tokens」タブを開く
2. **Bearer Token**を再生成（必要に応じて）
   - 「Bearer Token」セクションで「Regenerate」をクリック
   - 新しいBearer Tokenをコピー
3. **OAuth 1.0a認証情報**を確認
   - 「API Key and Secret」セクションで、API KeyとSecretを確認
   - 「Access Token and Secret」セクションで、Access TokenとSecretを確認
   - 必要に応じて再生成

### Step 4: GitHub Secretsを更新

1. [GitHub Repository Settings](https://github.com/PheasantDevil/aica-sys/settings/secrets/actions)にアクセス
2. 以下のSecretsを更新：
   - `TWITTER_BEARER_TOKEN` - 新しいBearer Tokenを設定
   - `TWITTER_API_KEY` - API Keyを設定（変更した場合）
   - `TWITTER_API_SECRET` - API Secretを設定（変更した場合）
   - `TWITTER_ACCESS_TOKEN` - Access Tokenを設定（変更した場合）
   - `TWITTER_ACCESS_TOKEN_SECRET` - Access Token Secretを設定（変更した場合）

### Step 5: アプリの設定を確認

1. 「App permissions」セクションで、以下の設定を確認：
   - **Read and Write** が選択されている
   - **Callback URI** が正しく設定されている（必要に応じて）
   - **App environment** が「Production」になっている

### Step 6: Twitterアカウントの状態を確認

1. 通常のTwitterアカウントにログイン
2. アカウントが制限されていないか確認
3. 必要に応じて、Twitterサポートに問い合わせ

### Step 7: ワークフローを再実行

1. GitHub Actionsでワークフローを再実行
2. エラーが解消されているか確認

## トラブルシューティング

### 問題: 「Read and Write」権限が選択できない

**原因**: Twitter Developerアカウントのアクセスレベルが不足している可能性があります。

**対処法**:
1. Twitter Developer Portalでアカウントの状態を確認
2. 必要に応じて、Twitter Developerアカウントをアップグレード
3. アカウントの審査が完了しているか確認

### 問題: Bearer Tokenを再生成してもエラーが続く

**原因**: OAuth 1.0a認証情報が無効になっている可能性があります。

**対処法**:
1. OAuth 1.0a認証情報（API Key, Secret, Access Token, Secret）をすべて再生成
2. GitHub Secretsをすべて更新
3. ワークフローを再実行

### 問題: 権限を変更してもエラーが続く

**原因**: 変更が反映されるまで時間がかかる場合があります。

**対処法**:
1. 数分待ってから再実行
2. Twitter Developer Portalで設定が正しく保存されているか確認
3. ブラウザのキャッシュをクリアして再確認

## 確認方法

修正が完了したかどうかを確認するには、以下のコマンドをローカルで実行：

```bash
cd /Users/Work/aica-sys
python3 scripts/test_twitter_connection.py
```

正常に動作する場合、以下のメッセージが表示されます：

```
✅ Twitter API connection successful!
```

## 参考資料

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [Twitter API Authentication](https://developer.twitter.com/en/docs/authentication/overview)

