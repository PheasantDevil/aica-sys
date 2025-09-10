#!/bin/bash

# Google OAuth 認証情報設定スクリプト

echo "🔐 Google OAuth 認証情報を設定します..."

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ユーザー入力
echo -e "${BLUE}Google Cloud Console で取得した認証情報を入力してください:${NC}"
echo ""

read -p "Google Client ID: " GOOGLE_CLIENT_ID
read -p "Google Client Secret: " GOOGLE_CLIENT_SECRET

# 入力値の検証
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo -e "${YELLOW}⚠️  認証情報が入力されていません。スキップします。${NC}"
    exit 1
fi

# フロントエンド環境変数ファイルを更新
if [ -f "frontend/.env.local" ]; then
    # macOS用のsedコマンド
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i.bak "s/your-google-client-id/$GOOGLE_CLIENT_ID/g" frontend/.env.local
        sed -i.bak "s/your-google-client-secret/$GOOGLE_CLIENT_SECRET/g" frontend/.env.local
    else
        sed -i "s/your-google-client-id/$GOOGLE_CLIENT_ID/g" frontend/.env.local
        sed -i "s/your-google-client-secret/$GOOGLE_CLIENT_SECRET/g" frontend/.env.local
    fi
    
    echo -e "${GREEN}✅ frontend/.env.local を更新しました${NC}"
else
    echo -e "${YELLOW}⚠️  frontend/.env.local が見つかりません${NC}"
fi

# 設定確認
echo ""
echo -e "${BLUE}設定された認証情報:${NC}"
echo "Client ID: $GOOGLE_CLIENT_ID"
echo "Client Secret: ${GOOGLE_CLIENT_SECRET:0:10}..."

echo ""
echo -e "${GREEN}🎉 Google OAuth 認証情報の設定が完了しました！${NC}"
echo ""
echo -e "${YELLOW}次のステップ:${NC}"
echo "1. 他のAPIサービスの設定を続行"
echo "2. ローカル動作確認: cd frontend && npm run dev"
echo "3. 認証テスト: http://localhost:3000/auth/signin"
