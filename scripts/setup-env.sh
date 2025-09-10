#!/bin/bash

echo "🚀 AICA-SyS 環境変数セットアップスクリプト"
echo "=============================================="

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 関数定義
print_step() {
    echo -e "\n${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 必要なツールの確認
print_step "必要なツールの確認"

# Python確認
if command -v python3 &> /dev/null; then
    print_success "Python3 がインストールされています"
else
    print_error "Python3 がインストールされていません"
    exit 1
fi

# pip確認
if command -v pip3 &> /dev/null; then
    print_success "pip3 がインストールされています"
else
    print_error "pip3 がインストールされていません"
    exit 1
fi

# 2. プロジェクトディレクトリの確認
print_step "プロジェクトディレクトリの確認"

if [ -f "backend/main.py" ]; then
    print_success "AICA-SyS プロジェクトディレクトリです"
else
    print_error "AICA-SyS プロジェクトディレクトリではありません"
    echo "このスクリプトをプロジェクトルートで実行してください"
    exit 1
fi

# 3. 依存関係のインストール
print_step "依存関係のインストール"

cd backend
if pip3 install -r requirements.txt; then
    print_success "依存関係のインストールが完了しました"
else
    print_warning "一部の依存関係のインストールに失敗しました"
    echo "手動でインストールしてください: pip3 install -r requirements.txt"
fi

# 4. 環境変数ファイルの作成
print_step "環境変数ファイルの作成"

ENV_FILE="../.env"
if [ -f "$ENV_FILE" ]; then
    print_warning ".env ファイルが既に存在します"
    read -p "上書きしますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "既存の .env ファイルを保持します"
        exit 0
    fi
fi

# 5. シークレット生成
print_step "シークレット生成"

JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)

print_success "シークレットが生成されました"

# 6. .env ファイルの作成
print_step ".env ファイルの作成"

cat > "$ENV_FILE" << EOF
# AICA-SyS Environment Variables
# このファイルは .gitignore に含まれています

# AI APIs (必須)
GOOGLE_AI_API_KEY=your_google_ai_key_here
OPENAI_API_KEY=your_openai_key_here

# GitHub (必須)
GITHUB_TOKEN=your_github_token_here

# Database (必須)
DATABASE_URL=sqlite:///./aica_sys.db

# Security (自動生成済み)
JWT_SECRET_KEY=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
NEXTAUTH_SECRET=$NEXTAUTH_SECRET

# Optional Services
REDIS_URL=redis://localhost:6379
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_key_here

# Frontend URLs
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_GA_ID=your_google_analytics_id_here
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here

# Backend URLs
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
RESEND_API_KEY=your_resend_api_key_here
EOF

print_success ".env ファイルが作成されました"

# 7. データベースの初期化
print_step "データベースの初期化"

python3 -c "
from database import Base, engine
try:
    Base.metadata.create_all(bind=engine)
    print('✅ データベーステーブルが作成されました')
except Exception as e:
    print(f'❌ データベース初期化エラー: {e}')
"

# 8. 設定確認
print_step "設定確認"

echo -e "\n${YELLOW}📋 次の手順でAPIキーを設定してください:${NC}"
echo ""
echo "1. Google AI API Key:"
echo "   - https://aistudio.google.com/ にアクセス"
echo "   - Get API key → Create API key"
echo "   - .env ファイルの GOOGLE_AI_API_KEY を更新"
echo ""
echo "2. OpenAI API Key:"
echo "   - https://platform.openai.com/ にアクセス"
echo "   - API keys → Create new secret key"
echo "   - .env ファイルの OPENAI_API_KEY を更新"
echo ""
echo "3. GitHub Personal Access Token:"
echo "   - GitHub → Settings → Developer settings → Personal access tokens"
echo "   - Generate new token (classic)"
echo "   - Scopes: repo, read:user, read:org"
echo "   - .env ファイルの GITHUB_TOKEN を更新"
echo ""

# 9. テスト実行
print_step "基本テストの実行"

if python3 test_minimal.py; then
    print_success "基本テストが成功しました"
else
    print_warning "基本テストでエラーが発生しました"
fi

# 10. 完了メッセージ
print_step "セットアップ完了"

echo -e "\n${GREEN}🎉 AICA-SyS のセットアップが完了しました！${NC}"
echo ""
echo "📋 次のステップ:"
echo "1. .env ファイルでAPIキーを設定"
echo "2. フロントエンドの起動: cd frontend && npm run dev"
echo "3. バックエンドの起動: cd backend && uvicorn main:app --reload"
echo "4. ブラウザで http://localhost:3000 にアクセス"
echo ""
echo "📚 詳細な設定手順:"
echo "   docs/api-keys-setup.md を参照してください"
echo ""
echo "🔧 トラブルシューティング:"
echo "   - ログファイルを確認"
echo "   - 環境変数が正しく設定されているか確認"
echo "   - 依存関係がインストールされているか確認"
echo ""

print_success "セットアップスクリプトが完了しました"