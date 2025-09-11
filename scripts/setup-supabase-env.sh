#!/bin/bash
# Supabase環境変数設定スクリプト

echo "🚀 Supabase環境変数設定スクリプト"
echo "=================================="

# Vercelから環境変数を取得
echo "📋 Vercelから環境変数を取得中..."

# Vercel CLIがインストールされているかチェック
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLIがインストールされていません"
    echo "以下のコマンドでインストールしてください:"
    echo "npm i -g vercel"
    exit 1
fi

# Vercelにログインしているかチェック
if ! vercel whoami &> /dev/null; then
    echo "❌ Vercelにログインしていません"
    echo "以下のコマンドでログインしてください:"
    echo "vercel login"
    exit 1
fi

# 環境変数を取得
echo "📥 環境変数を取得中..."
vercel env pull .env.local

# .env.localファイルが作成されたかチェック
if [ ! -f ".env.local" ]; then
    echo "❌ .env.localファイルが作成されませんでした"
    exit 1
fi

echo "✅ 環境変数が .env.local に保存されました"

# 必要な環境変数が設定されているかチェック
echo "🔍 環境変数の確認中..."

required_vars=("DATABASE_URL" "SUPABASE_URL" "SUPABASE_ANON_KEY" "SUPABASE_SERVICE_KEY")

for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" .env.local; then
        echo "✅ ${var} が設定されています"
    else
        echo "❌ ${var} が設定されていません"
    fi
done

echo ""
echo "🎉 セットアップ完了！"
echo "以下のコマンドでデータベース初期化を実行できます:"
echo "python backend/supabase_init.py"
