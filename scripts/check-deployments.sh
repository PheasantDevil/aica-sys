#!/bin/bash

# デプロイ状態確認スクリプト
# Vercel と Render の両方のデプロイ状態を確認します

set -e

echo "================================================"
echo "  デプロイ状態確認"
echo "================================================"
echo ""

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vercel の確認
echo "${BLUE}📦 Vercel デプロイ状態${NC}"
echo "----------------------------------------"

if command -v vercel &> /dev/null; then
    # ログイン状態確認
    if vercel whoami &> /dev/null; then
        echo "${GREEN}✓${NC} Vercel CLI: ログイン済み"
        USER=$(vercel whoami 2>/dev/null | head -n 1)
        echo "  ユーザー: $USER"
        echo ""
        
        # 最新デプロイを取得
        echo "最新のデプロイ:"
        
        # frontendディレクトリが存在する場合はそこで実行
        VERCEL_CMD="vercel list --output json"
        if [ -d "frontend" ] && [ -d "frontend/.vercel" ]; then
            VERCEL_CMD="cd frontend && vercel list --output json"
        fi
        
        if eval "$VERCEL_CMD" &> /dev/null; then
            LATEST=$(eval "$VERCEL_CMD" 2>/dev/null | jq -r '.[0] // empty')
            if [ -n "$LATEST" ]; then
                URL=$(echo "$LATEST" | jq -r '.url')
                STATE=$(echo "$LATEST" | jq -r '.state')
                CREATED=$(echo "$LATEST" | jq -r '.created')
                
                if [ "$STATE" = "READY" ]; then
                    echo "  ${GREEN}● READY${NC}"
                elif [ "$STATE" = "ERROR" ]; then
                    echo "  ${RED}● ERROR${NC}"
                else
                    echo "  ${YELLOW}● $STATE${NC}"
                fi
                
                echo "  URL: https://$URL"
                echo "  作成日時: $CREATED"
            else
                echo "  ${YELLOW}デプロイが見つかりません${NC}"
            fi
        else
            echo "  ${YELLOW}プロジェクトがリンクされていません${NC}"
            echo "  実行: cd frontend && vercel link"
        fi
    else
        echo "${YELLOW}⚠${NC} Vercel CLI: 未ログイン"
        echo "  実行: vercel login"
    fi
else
    echo "${RED}✗${NC} Vercel CLI: 未インストール"
    echo "  実行: npm install -g vercel"
fi

echo ""
echo "----------------------------------------"
echo ""

# Render の確認
echo "${BLUE}🚀 Render デプロイ状態${NC}"
echo "----------------------------------------"

if command -v render &> /dev/null; then
    # ログイン状態確認
    if render whoami -o text &> /dev/null 2>&1; then
        echo "${GREEN}✓${NC} Render CLI: ログイン済み"
        USER=$(render whoami -o text 2>/dev/null | head -n 1 | awk '{print $1}')
        echo "  ユーザー: $USER"
        echo ""
        
        # サービス一覧を取得
        echo "サービス状態:"
        if render services -o json &> /dev/null 2>&1; then
            SERVICES=$(render services -o json 2>/dev/null | jq -c '.[] | select(.name | contains("aica-sys"))')
            
            if [ -n "$SERVICES" ]; then
                echo "$SERVICES" | while IFS= read -r service; do
                    NAME=$(echo "$service" | jq -r '.name')
                    STATUS=$(echo "$service" | jq -r '.status // "unknown"')
                    TYPE=$(echo "$service" | jq -r '.type')
                    
                    if [ "$STATUS" = "live" ] || [ "$STATUS" = "available" ]; then
                        echo "  ${GREEN}● $STATUS${NC} - $NAME ($TYPE)"
                    elif [ "$STATUS" = "deploying" ]; then
                        echo "  ${YELLOW}● $STATUS${NC} - $NAME ($TYPE)"
                    else
                        echo "  ${RED}● $STATUS${NC} - $NAME ($TYPE)"
                    fi
                done
            else
                echo "  ${YELLOW}AICA-SyS関連のサービスが見つかりません${NC}"
            fi
        else
            echo "  ${YELLOW}サービス情報を取得できません${NC}"
        fi
    else
        echo "${YELLOW}⚠${NC} Render CLI: 未ログイン"
        echo "  実行: render login"
    fi
else
    echo "${RED}✗${NC} Render CLI: 未インストール"
    echo "  実行: brew install render"
fi

echo ""
echo "----------------------------------------"
echo ""

# まとめ
echo "${BLUE}📊 まとめ${NC}"
echo "----------------------------------------"

VERCEL_OK=false
RENDER_OK=false

if command -v vercel &> /dev/null && vercel whoami &> /dev/null; then
    VERCEL_OK=true
fi

if command -v render &> /dev/null && render whoami -o json &> /dev/null 2>&1; then
    RENDER_OK=true
fi

if $VERCEL_OK && $RENDER_OK; then
    echo "${GREEN}✓${NC} すべてのCLIが正常に動作しています"
elif $VERCEL_OK || $RENDER_OK; then
    echo "${YELLOW}⚠${NC} 一部のCLIが未設定です"
else
    echo "${RED}✗${NC} CLIの設定が必要です"
fi

echo ""
echo "詳細なログを確認する場合:"
echo "  Vercel: vercel logs --follow"
echo "  Render: render logs --tail"
echo ""
echo "================================================"

