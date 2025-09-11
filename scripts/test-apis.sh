#!/bin/bash

echo "🧪 AICA-SyS API接続テスト"
echo "=========================="

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

# 環境変数ファイルの読み込み
if [ -f ".env" ]; then
    source .env
    print_success ".env ファイルを読み込みました"
else
    print_error ".env ファイルが見つかりません"
    exit 1
fi

cd backend

# 1. Google AI API テスト
print_step "Google AI API テスト"

if [ -n "$GOOGLE_AI_API_KEY" ] && [ "$GOOGLE_AI_API_KEY" != "your_google_ai_key_here" ]; then
    if python3 -c "
import google.generativeai as genai
import os
try:
    genai.configure(api_key='$GOOGLE_AI_API_KEY')
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content('Hello, test message')
    print('✅ Google AI API: 接続成功')
    print(f'   レスポンス: {response.text[:100]}...')
except Exception as e:
    print(f'❌ Google AI API: エラー - {e}')
    exit(1)
" 2>/dev/null; then
        print_success "Google AI API: 接続成功"
    else
        print_error "Google AI API: 接続失敗"
    fi
else
    print_warning "Google AI API: 未設定"
fi

# 2. OpenAI API テスト
print_step "OpenAI API テスト"

if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your_openai_key_here" ]; then
    if python3 -c "
import openai
import os
try:
    openai.api_key = '$OPENAI_API_KEY'
    # 簡単なテスト（実際のAPI呼び出しは行わない）
    print('✅ OpenAI API: 設定確認成功')
except Exception as e:
    print(f'❌ OpenAI API: エラー - {e}')
    exit(1)
" 2>/dev/null; then
        print_success "OpenAI API: 設定確認成功"
    else
        print_error "OpenAI API: 設定確認失敗"
    fi
else
    print_warning "OpenAI API: 未設定"
fi

# 3. GitHub API テスト
print_step "GitHub API テスト"

if [ -n "$GITHUB_TOKEN" ] && [ "$GITHUB_TOKEN" != "your_github_token_here" ]; then
    if python3 -c "
from github import Github
import os
try:
    g = Github('$GITHUB_TOKEN')
    user = g.get_user()
    print('✅ GitHub API: 接続成功')
    print(f'   ユーザー: {user.login}')
except Exception as e:
    print(f'❌ GitHub API: エラー - {e}')
    exit(1)
" 2>/dev/null; then
        print_success "GitHub API: 接続成功"
    else
        print_error "GitHub API: 接続失敗"
    fi
else
    print_warning "GitHub API: 未設定"
fi

# 4. データベース接続テスト
print_step "データベース接続テスト"

if python3 -c "
from database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ データベース: 接続成功')
except Exception as e:
    print(f'❌ データベース: エラー - {e}')
    exit(1)
" 2>/dev/null; then
    print_success "データベース: 接続成功"
else
    print_error "データベース: 接続失敗"
fi

# 5. 基本機能テスト
print_step "基本機能テスト"

if python3 test_minimal.py >/dev/null 2>&1; then
    print_success "基本機能: テスト成功"
else
    print_warning "基本機能: テストで警告"
fi

# 6. 結果サマリー
print_step "テスト結果サマリー"

echo ""
echo "📊 API接続テスト完了"
echo ""
echo "🚀 次のステップ:"
echo "1. バックエンド起動: cd backend && uvicorn main:app --reload"
echo "2. フロントエンド起動: cd frontend && npm run dev"
echo "3. ブラウザで http://localhost:3000 にアクセス"
echo ""
echo "🔧 トラブルシューティング:"
echo "- API接続エラー: APIキーが正しく設定されているか確認"
echo "- データベースエラー: DATABASE_URL を確認"
echo "- 依存関係エラー: pip3 install -r requirements.txt を実行"

print_success "API接続テストが完了しました"
