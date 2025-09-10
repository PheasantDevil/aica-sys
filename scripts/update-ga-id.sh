#!/bin/bash

echo "📊 Google Analytics 測定IDを更新します..."

echo ""
echo "取得した測定IDを入力してください（G-XXXXXXXXXX形式）："
read -p "測定ID: " GA_ID

# キーの形式をチェック
if [[ ! $GA_ID =~ ^G- ]]; then
    echo "❌ 測定IDの形式が正しくありません (G- で始まる必要があります)"
    exit 1
fi

# ローカル環境変数を更新
sed -i '' "s|NEXT_PUBLIC_GA_ID=.*|NEXT_PUBLIC_GA_ID=$GA_ID|" frontend/.env.local

# Vercel環境変数を更新
echo ""
echo "Vercel環境変数も更新しますか？ (y/n)"
read -p "> " update_vercel

if [[ $update_vercel == "y" || $update_vercel == "Y" ]]; then
    vercel env add NEXT_PUBLIC_GA_ID production <<< "$GA_ID"
    echo "✅ Vercel環境変数を更新しました"
fi

echo ""
echo "✅ Google Analytics 測定IDを更新しました！"
echo ""
echo "設定された測定ID: $GA_ID"
echo ""
echo "次のステップ:"
echo "1. ローカル環境を再起動: cd frontend && npm run dev"
echo "2. 本番環境を再デプロイ: vercel --prod"
echo "3. Google Analytics でリアルタイムレポートを確認"
