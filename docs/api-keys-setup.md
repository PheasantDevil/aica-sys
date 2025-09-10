# API Keys Setup Guide

AICA-SyS に必要な API キーの取得と設定手順

## 1. Google AI API Key

### 取得手順

1. **Google AI Studio** にアクセス

   - URL: https://aistudio.google.com/
   - Google アカウントでログイン

2. **API Key の作成**

   - 左サイドバーの「Get API key」をクリック
   - 「Create API key」をクリック
   - プロジェクトを選択（または新規作成）
   - API key をコピー

3. **GitHub Secrets に設定**
   - リポジトリの Settings → Secrets and variables → Actions
   - 「New repository secret」をクリック
   - Name: `GOOGLE_AI_API_KEY`
   - Secret: 取得した API key を貼り付け

### 確認方法

```bash
# 環境変数として設定してテスト
export GOOGLE_AI_API_KEY="your_api_key_here"
python3 -c "import google.generativeai as genai; genai.configure(api_key='$GOOGLE_AI_API_KEY'); print('✅ Google AI API Key is valid')"
```

---

## 2. OpenAI API Key

### 取得手順

1. **OpenAI Platform** にアクセス

   - URL: https://platform.openai.com/
   - アカウント作成またはログイン

2. **API Key の作成**

   - 左サイドバーの「API keys」をクリック
   - 「Create new secret key」をクリック
   - キー名を入力（例: "AICA-SyS"）
   - API key をコピー（一度しか表示されません）

3. **GitHub Secrets に設定**
   - Name: `OPENAI_API_KEY`
   - Secret: 取得した API key を貼り付け

### 確認方法

```bash
export OPENAI_API_KEY="your_api_key_here"
python3 -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('✅ OpenAI API Key is valid')"
```

---

## 3. GitHub Personal Access Token

### 取得手順

1. **GitHub Settings** にアクセス

   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Token の作成**

   - 「Generate new token」→「Generate new token (classic)」
   - Note: "AICA-SyS Data Collection"
   - Expiration: 90 days（推奨）
   - Scopes: 以下を選択
     - `repo` (Full control of private repositories)
     - `read:user` (Read user profile data)
     - `read:org` (Read org and team membership)

3. **GitHub Secrets に設定**
   - Name: `GITHUB_TOKEN`
   - Secret: 取得した token を貼り付け

### 確認方法

```bash
export GITHUB_TOKEN="your_token_here"
python3 -c "from github import Github; g = Github('$GITHUB_TOKEN'); print('✅ GitHub Token is valid')"
```

---

## 4. データベース URL

### 選択肢

#### A. SQLite (開発用・推奨)

```bash
# ローカル開発用
DATABASE_URL="sqlite:///./aica_sys.db"
```

#### B. PostgreSQL (本番用)

1. **Supabase** (無料プランあり)

   - URL: https://supabase.com/
   - プロジェクト作成
   - Settings → Database → Connection string をコピー

2. **Railway** (無料プランあり)
   - URL: https://railway.app/
   - PostgreSQL サービスを作成
   - Connection string をコピー

### GitHub Secrets に設定

- Name: `DATABASE_URL`
- Secret: 選択したデータベースの接続文字列

---

## 5. その他の必要な環境変数

### 自動生成可能な値

以下の値は自動生成できます：

```bash
# スクリプトを実行して生成
./scripts/generate-secrets.sh
```

生成される値：

- `JWT_SECRET_KEY`: JWT 認証用
- `ENCRYPTION_KEY`: データ暗号化用
- `NEXTAUTH_SECRET`: NextAuth.js 用

### 手動設定が必要な値

- `REDIS_URL`: Redis 接続文字列（オプション）
- `QDRANT_URL`: Qdrant 接続文字列（オプション）
- `QDRANT_API_KEY`: Qdrant API key（オプション）

---

## 6. 設定確認スクリプト

### 環境変数チェック

```bash
#!/bin/bash
echo "🔍 AICA-SyS 環境変数チェック"
echo "================================"

# 必須の環境変数
required_vars=(
    "GOOGLE_AI_API_KEY"
    "OPENAI_API_KEY"
    "GITHUB_TOKEN"
    "DATABASE_URL"
    "JWT_SECRET_KEY"
    "ENCRYPTION_KEY"
    "NEXTAUTH_SECRET"
)

for var in "${required_vars[@]}"; do
    if [ -n "${!var}" ]; then
        echo "✅ $var: 設定済み"
    else
        echo "❌ $var: 未設定"
    fi
done

echo ""
echo "📋 設定手順:"
echo "1. 上記の手順でAPIキーを取得"
echo "2. GitHub Secrets に設定"
echo "3. ローカル開発時は .env ファイルに設定"
```

---

## 7. ローカル開発用 .env ファイル

### 作成手順

```bash
# プロジェクトルートに .env ファイルを作成
cat > .env << EOF
# AI APIs
GOOGLE_AI_API_KEY=your_google_ai_key_here
OPENAI_API_KEY=your_openai_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here

# Database
DATABASE_URL=sqlite:///./aica_sys.db

# Security
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
NEXTAUTH_SECRET=your_nextauth_secret_here

# Optional
REDIS_URL=redis://localhost:6379
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_key_here
EOF
```

### 注意事項

- `.env` ファイルは `.gitignore` に含まれています
- 本番環境では GitHub Secrets を使用
- ローカル開発時のみ `.env` ファイルを使用

---

## 8. 設定完了後の確認

### 1. 依存関係のインストール

```bash
cd backend
pip install -r requirements.txt
```

### 2. データベースの初期化

```bash
python3 -c "
from database import Base, engine
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"
```

### 3. API 接続テスト

```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

# Google AI API テスト
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
    print('✅ Google AI API: OK')
except Exception as e:
    print(f'❌ Google AI API: {e}')

# OpenAI API テスト
try:
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    print('✅ OpenAI API: OK')
except Exception as e:
    print(f'❌ OpenAI API: {e}')

# GitHub API テスト
try:
    from github import Github
    g = Github(os.getenv('GITHUB_TOKEN'))
    print('✅ GitHub API: OK')
except Exception as e:
    print(f'❌ GitHub API: {e}')
"
```

### 4. 初回データ収集テスト

```bash
# FastAPI サーバーを起動
uvicorn main:app --reload --port 8000

# 別のターミナルでデータ収集をテスト
curl -X POST "http://localhost:8000/ai/collect"
```

---

## 📞 サポート

設定で問題が発生した場合：

1. エラーメッセージを確認
2. API キーの権限を確認
3. ネットワーク接続を確認
4. ログファイルを確認

すべての設定が完了したら、AICA-SyS の本格運用を開始できます！
