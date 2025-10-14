#!/bin/bash

# Alembicマイグレーション実行スクリプト
# Phase 1.3: データベースマイグレーション適用

set -e

echo "🚀 データベースマイグレーション実行開始..."

# バックエンドディレクトリに移動
cd "$(dirname "$0")/../backend"

# 仮想環境をアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 仮想環境が見つかりません"
    exit 1
fi

# データベース接続確認
echo "🔍 データベース接続確認..."
python3 -c "
from database import SessionLocal
try:
    db = SessionLocal()
    db.close()
    print('✅ データベース接続OK')
except Exception as e:
    print(f'❌ データベース接続エラー: {e}')
    exit(1)
"

# 現在のマイグレーション状態確認
echo ""
echo "📊 現在のマイグレーション状態:"
alembic current

# マイグレーション実行
echo ""
echo "⬆️  マイグレーション適用中..."
alembic upgrade head

# 結果確認
echo ""
echo "✅ マイグレーション完了"
echo ""
echo "📊 最終状態:"
alembic current

# テーブル存在確認
echo ""
echo "🔍 テーブル確認:"
python3 -c "
from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)
tables = inspector.get_table_names()

target_tables = ['automated_contents', 'trend_data', 'source_data', 'content_generation_logs']
for table in target_tables:
    if table in tables:
        print(f'✅ {table}')
    else:
        print(f'❌ {table} (not found)')
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ マイグレーション完了！"
echo "   次のステップ: 記事生成テスト"
echo "   python3 scripts/generate_daily_article.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

