# Vercel CLI ガイド

## インストール

```bash
# グローバルインストール（推奨）
npm install -g vercel

# バージョン確認
vercel --version
```

## 初期設定

### 1. ログイン

```bash
# ブラウザでログイン
vercel login

# トークンを使用したログイン
vercel login --token YOUR_TOKEN
```

### 2. プロジェクトをリンク

```bash
# 現在のディレクトリをVercelプロジェクトにリンク
cd /path/to/project
vercel link

# または、自動的にセットアップ
vercel
```

## 基本コマンド

### デプロイ関連

```bash
# プロダクションデプロイ
vercel --prod

# プレビューデプロイ（デフォルト）
vercel

# 特定のディレクトリをデプロイ
vercel ./frontend --prod

# 環境変数を指定してデプロイ
vercel -e NODE_ENV=production --prod
```

### ログ確認

```bash
# 最新デプロイのログを表示
vercel logs

# 特定のデプロイのログを表示
vercel logs [deployment-url]

# リアルタイムログ（tail -f相当）
vercel logs --follow

# JSON形式で出力
vercel logs --output json
```

### デプロイ一覧

```bash
# デプロイ一覧を表示
vercel list

# 特定のプロジェクトのデプロイ一覧
vercel list my-project

# JSON形式で出力
vercel list --output json
```

### プロジェクト情報

```bash
# 現在のユーザー情報
vercel whoami

# プロジェクト一覧
vercel projects list

# デプロイの詳細情報
vercel inspect [deployment-url]
```

### 環境変数管理

```bash
# 環境変数一覧
vercel env ls

# 環境変数を追加
vercel env add [name]

# 環境変数を削除
vercel env rm [name]

# 環境変数をプル（ローカルに取得）
vercel env pull .env.local
```

### ローカル開発

```bash
# ローカル開発サーバー起動（Vercel環境を再現）
vercel dev

# ポート指定
vercel dev --listen 3000
```

### ビルド

```bash
# ローカルでビルド
vercel build

# プロダクションビルド
vercel build --prod
```

## 複数プロジェクト管理

### プロジェクトの切り替え

```bash
# スコープ（チーム/個人）を切り替え
vercel switch [scope-name]

# プロジェクトをリンク（複数プロジェクトがある場合）
cd /path/to/project-1
vercel link

cd /path/to/project-2
vercel link
```

### プロジェクト固有の設定

各プロジェクトのルートに`.vercel`ディレクトリが作成され、プロジェクト固有の設定が保存されます。

```
project-1/
  .vercel/
    project.json    # プロジェクトID、org ID
  vercel.json       # デプロイ設定

project-2/
  .vercel/
    project.json
  vercel.json
```

## トラブルシューティング

### デプロイエラーの確認

```bash
# 詳細なエラーログ
vercel logs [deployment-url] --debug

# ビルドログ
vercel logs [deployment-url] | grep "error"
```

### キャッシュクリア

```bash
# ビルドキャッシュをクリア
vercel build --force

# または、Vercelダッシュボードで手動クリア
```

### 認証トークンの再取得

```bash
# ログアウト
vercel logout

# 再ログイン
vercel login
```

## CI/CD統合

### GitHub Actionsでの使用

```yaml
name: Vercel Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Vercel CLI
        run: npm install -g vercel
      
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          vercel --token $VERCEL_TOKEN --prod
```

### トークンの取得方法

1. Vercel Dashboard → Settings → Tokens
2. "Create Token" をクリック
3. スコープとExpiration（有効期限）を設定
4. 生成されたトークンをコピー

## ベストプラクティス

### 1. 環境ごとのデプロイ

```bash
# 開発環境（プレビュー）
vercel

# ステージング環境
vercel --prod --scope staging-team

# 本番環境
vercel --prod --scope production-team
```

### 2. セキュリティ

- **トークンは絶対にGitにコミットしない**
- 環境変数は`.env.local`に保存（`.gitignore`に追加）
- CI/CDではSecretsを使用

### 3. パフォーマンス

```bash
# ビルド時間の確認
vercel inspect [deployment-url] --timeout 30s

# ビルドキャッシュの活用
vercel build --debug
```

## よく使うコマンド一覧

```bash
# ログイン
vercel login

# プロジェクトリンク
vercel link

# プロダクションデプロイ
vercel --prod

# ログ確認
vercel logs --follow

# 環境変数取得
vercel env pull

# ローカル開発
vercel dev

# デプロイ一覧
vercel list

# 現在のユーザー
vercel whoami

# プロジェクト一覧
vercel projects list
```

## リファレンス

- [公式ドキュメント](https://vercel.com/docs/cli)
- [CLI Reference](https://vercel.com/docs/cli/commands)
- [環境変数ガイド](https://vercel.com/docs/environment-variables)
- [デプロイ設定](https://vercel.com/docs/deployments/overview)

