#!/bin/bash

# Alembicマイグレーション作成スクリプト
# Phase 1.3: 自動コンテンツテーブル作成

set -e

echo "🚀 Alembicマイグレーション作成開始..."

# バックエンドディレクトリに移動
cd "$(dirname "$0")/../backend"

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "❌ 仮想環境が見つかりません"
    echo "   以下のコマンドで作成してください："
    echo "   python3 -m venv venv"
    exit 1
fi

# 仮想環境をアクティベート
source venv/bin/activate

# 必要なパッケージの確認
echo "📦 依存パッケージ確認..."
pip install -q alembic sqlalchemy

# マイグレーション作成
echo "📝 マイグレーションファイル作成..."
alembic revision --autogenerate -m "Add automated content tables (automated_contents, trend_data, source_data, content_generation_logs)"

# 作成されたマイグレーションファイルを表示
LATEST_MIGRATION=$(ls -t alembic/versions/*.py | head -1)
echo ""
echo "✅ マイグレーションファイルが作成されました:"
echo "   ${LATEST_MIGRATION}"
echo ""
echo "📄 マイグレーション内容:"
head -30 "${LATEST_MIGRATION}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "次のステップ:"
echo "1. マイグレーション内容を確認"
echo "2. 以下のコマンドでマイグレーション実行:"
echo "   cd backend && alembic upgrade head"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

