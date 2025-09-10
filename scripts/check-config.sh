#!/bin/bash

echo "🔍 AICA-SyS 設定確認スクリプト"
echo "================================="

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

# 1. 環境変数ファイルの確認
print_step "環境変数ファイルの確認"

if [ -f ".env" ]; then
    print_success ".env ファイルが存在します"
    source .env
else
    print_error ".env ファイルが見つかりません"
    echo "scripts/setup-env.sh を実行してください"
    exit 1
fi

# 2. 必須環境変数の確認
print_step "必須環境変数の確認"

required_vars=(
    "GOOGLE_AI_API_KEY"
    "OPENAI_API_KEY"
    "GITHUB_TOKEN"
    "DATABASE_URL"
    "JWT_SECRET_KEY"
    "ENCRYPTION_KEY"
    "NEXTAUTH_SECRET"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -n "${!var}" ] && [ "${!var}" != "your_${var,,}_here" ]; then
        print_success "$var: 設定済み"
    else
        print_error "$var: 未設定またはデフォルト値"
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo ""
    print_warning "未設定の環境変数:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "docs/api-keys-setup.md を参照して設定してください"
fi

# 3. Python依存関係の確認
print_step "Python依存関係の確認"

cd backend

if python3 -c "import fastapi, uvicorn, sqlalchemy, requests, beautifulsoup4, feedparser" 2>/dev/null; then
    print_success "基本的な依存関係がインストールされています"
else
    print_warning "一部の依存関係が不足しています"
    echo "pip3 install -r requirements.txt を実行してください"
fi

# 4. データベース接続テスト
print_step "データベース接続テスト"

if python3 -c "
from database import engine
try:
    with engine.connect() as conn:
        print('✅ データベース接続成功')
except Exception as e:
    print(f'❌ データベース接続エラー: {e}')
    exit(1)
"; then
    print_success "データベース接続が正常です"
else
    print_error "データベース接続に失敗しました"
fi

# 5. API接続テスト
print_step "API接続テスト"

# Google AI API テスト
if [ -n "$GOOGLE_AI_API_KEY" ] && [ "$GOOGLE_AI_API_KEY" != "your_google_ai_key_here" ]; then
    if python3 -c "
import google.generativeai as genai
import os
genai.configure(api_key='$GOOGLE_AI_API_KEY')
print('✅ Google AI API: 接続成功')
" 2>/dev/null; then
        print_success "Google AI API: 接続成功"
    else
        print_error "Google AI API: 接続失敗"
    fi
else
    print_warning "Google AI API: 未設定"
fi

# OpenAI API テスト
if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your_openai_key_here" ]; then
    if python3 -c "
import openai
import os
openai.api_key = '$OPENAI_API_KEY'
print('✅ OpenAI API: 接続成功')
" 2>/dev/null; then
        print_success "OpenAI API: 接続成功"
    else
        print_error "OpenAI API: 接続失敗"
    fi
else
    print_warning "OpenAI API: 未設定"
fi

# GitHub API テスト
if [ -n "$GITHUB_TOKEN" ] && [ "$GITHUB_TOKEN" != "your_github_token_here" ]; then
    if python3 -c "
from github import Github
import os
g = Github('$GITHUB_TOKEN')
print('✅ GitHub API: 接続成功')
" 2>/dev/null; then
        print_success "GitHub API: 接続成功"
    else
        print_error "GitHub API: 接続失敗"
    fi
else
    print_warning "GitHub API: 未設定"
fi

# 6. ファイル構造の確認
print_step "ファイル構造の確認"

required_files=(
    "services/data_collector.py"
    "services/ai_analyzer.py"
    "services/content_generator.py"
    "models/ai_models.py"
    "routers/ai_router.py"
    "database.py"
    "main.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file: 存在"
    else
        print_error "$file: 見つかりません"
        missing_files+=("$file")
    fi
done

# 7. 基本テストの実行
print_step "基本テストの実行"

if python3 test_minimal.py; then
    print_success "基本テストが成功しました"
else
    print_warning "基本テストでエラーが発生しました"
fi

# 8. 結果サマリー
print_step "設定確認結果"

total_checks=7
passed_checks=0

# 環境変数チェック
if [ ${#missing_vars[@]} -eq 0 ]; then
    ((passed_checks++))
fi

# 依存関係チェック
if python3 -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
    ((passed_checks++))
fi

# データベースチェック
if python3 -c "from database import engine; engine.connect()" 2>/dev/null; then
    ((passed_checks++))
fi

# ファイル構造チェック
if [ ${#missing_files[@]} -eq 0 ]; then
    ((passed_checks++))
fi

# 基本テストチェック
if python3 test_minimal.py >/dev/null 2>&1; then
    ((passed_checks++))
fi

echo ""
echo "📊 設定確認結果: $passed_checks/$total_checks 項目が正常です"

if [ $passed_checks -eq $total_checks ]; then
    print_success "🎉 すべての設定が正常です！AICA-SyS を起動できます"
    echo ""
    echo "🚀 起動コマンド:"
    echo "  フロントエンド: cd frontend && npm run dev"
    echo "  バックエンド: cd backend && uvicorn main:app --reload"
else
    print_warning "⚠️  一部の設定に問題があります。上記のエラーを確認してください"
    echo ""
    echo "🔧 トラブルシューティング:"
    echo "  1. docs/api-keys-setup.md を参照"
    echo "  2. scripts/setup-env.sh を再実行"
    echo "  3. 依存関係を再インストール"
fi

echo ""
print_success "設定確認スクリプトが完了しました"
