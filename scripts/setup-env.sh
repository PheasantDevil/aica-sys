#!/bin/bash

# AICA-SyS 環境変数設定スクリプト

echo "🚀 AICA-SyS 環境変数設定を開始します..."

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 関数定義
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
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

# フロントエンド環境変数ファイル作成
print_step "フロントエンド環境変数ファイルを作成中..."
if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << 'EOF'
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
EOF
    print_success "frontend/.env.local を作成しました"
else
    print_warning "frontend/.env.local は既に存在します"
fi

# バックエンド環境変数ファイル作成
print_step "バックエンド環境変数ファイルを作成中..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
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
EOF
    print_success "backend/.env を作成しました"
else
    print_warning "backend/.env は既に存在します"
fi

# セキュリティキー生成
print_step "セキュリティキーを生成中..."

# NextAuth シークレット生成
NEXTAUTH_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "your-nextauth-secret-key-here")
print_success "NextAuth シークレットを生成しました"

# アプリケーションシークレット生成
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || echo "your-secret-key-here")
print_success "アプリケーションシークレットを生成しました"

# 生成されたキーをファイルに反映
if command -v sed >/dev/null 2>&1; then
    sed -i.bak "s/your-nextauth-secret-key-here/$NEXTAUTH_SECRET/g" frontend/.env.local
    sed -i.bak "s/your-secret-key-here/$SECRET_KEY/g" backend/.env
    print_success "生成されたキーを環境変数ファイルに反映しました"
fi

# 環境変数ファイルの権限設定
chmod 600 frontend/.env.local
chmod 600 backend/.env
print_success "環境変数ファイルの権限を設定しました"

# 設定完了メッセージ
echo ""
echo -e "${GREEN}🎉 環境変数設定が完了しました！${NC}"
echo ""
echo -e "${YELLOW}次のステップ:${NC}"
echo "1. 各APIサービスのアカウントを作成"
echo "2. APIキーを取得"
echo "3. 環境変数ファイルを編集してAPIキーを設定"
echo "4. 詳細な設定方法は docs/environment-setup.md を参照"
echo ""
echo -e "${BLUE}必要なAPIサービス:${NC}"
echo "• Google OAuth (認証)"
echo "• Stripe (決済)"
echo "• Resend (メール送信)"
echo "• Google Analytics (分析)"
echo "• Google AI Studio (AI生成)"
echo "• OpenAI (AI生成)"
echo "• GitHub (データ収集)"
echo ""
echo -e "${GREEN}設定完了後、以下のコマンドで動作確認を行ってください:${NC}"
echo "cd frontend && npm run dev"
echo "cd backend && python main.py"
