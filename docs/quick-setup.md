# 🚀 AICA-SyS クイックセットアップ

## 必要な情報と取得手順

### **1. Google AI API Key** (必須)

- **取得先**: https://aistudio.google.com/
- **手順**:
  1. Google アカウントでログイン
  2. 「Get API key」→「Create API key」
  3. API key をコピー
- **設定場所**: GitHub Secrets の `GOOGLE_AI_API_KEY`

### **2. OpenAI API Key** (必須)

- **取得先**: https://platform.openai.com/
- **手順**:
  1. アカウント作成/ログイン
  2. 「API keys」→「Create new secret key」
  3. API key をコピー（一度しか表示されません）
- **設定場所**: GitHub Secrets の `OPENAI_API_KEY`

### **3. GitHub Personal Access Token** (必須)

- **取得先**: GitHub → Settings → Developer settings
- **手順**:
  1. 「Personal access tokens」→「Tokens (classic)」
  2. 「Generate new token (classic)」
  3. Scopes: `repo`, `read:user`, `read:org` を選択
  4. Token をコピー
- **設定場所**: GitHub Secrets の `GITHUB_TOKEN`

### **4. データベース URL** (必須)

- **推奨**: SQLite (開発用)
  ```
  DATABASE_URL=sqlite:///./aica_sys.db
  ```
- **本番用**: PostgreSQL
  - Supabase (無料): https://supabase.com/
  - Railway (無料): https://railway.app/

## 自動セットアップ

### 1. 環境変数セットアップ

```bash
# プロジェクトルートで実行
./scripts/setup-env.sh
```

### 2. 設定確認

```bash
# 設定が正しいか確認
./scripts/check-config.sh
```

### 3. 手動設定が必要な項目

上記のスクリプト実行後、`.env` ファイルで以下を手動設定：

```bash
# .env ファイルを編集
nano .env

# 以下の値を実際のAPI keyに変更
GOOGLE_AI_API_KEY=your_google_ai_key_here
OPENAI_API_KEY=your_openai_key_here
GITHUB_TOKEN=your_github_token_here
```

## GitHub Secrets 設定

### 1. リポジトリの設定画面にアクセス

- GitHub リポジトリ → Settings → Secrets and variables → Actions

### 2. 以下の Secrets を追加

| Name                | Value                  | 説明          |
| ------------------- | ---------------------- | ------------- |
| `GOOGLE_AI_API_KEY` | 取得した API key       | Google AI API |
| `OPENAI_API_KEY`    | 取得した API key       | OpenAI API    |
| `GITHUB_TOKEN`      | 取得した token         | GitHub API    |
| `DATABASE_URL`      | データベース接続文字列 | データベース  |
| `JWT_SECRET_KEY`    | 自動生成された値       | JWT 認証      |
| `ENCRYPTION_KEY`    | 自動生成された値       | データ暗号化  |
| `NEXTAUTH_SECRET`   | 自動生成された値       | NextAuth.js   |

## 起動確認

### 1. バックエンド起動

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. フロントエンド起動

```bash
cd frontend
npm run dev
```

### 3. アクセス確認

- フロントエンド: http://localhost:3000
- バックエンド API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## トラブルシューティング

### よくある問題

1. **依存関係エラー**: `pip3 install -r requirements.txt`
2. **API 接続エラー**: API key が正しく設定されているか確認
3. **データベースエラー**: DATABASE_URL が正しいか確認
4. **ポート競合**: 別のポートを使用

### ログ確認

```bash
# バックエンドログ
cd backend && python3 main.py

# フロントエンドログ
cd frontend && npm run dev
```

## 次のステップ

設定完了後：

1. 初回データ収集の実行
2. AI 分析のテスト
3. コンテンツ生成の確認
4. 本番環境へのデプロイ

詳細は `docs/api-keys-setup.md` を参照してください。
