#!/bin/bash

echo "🚀 Vercel 環境変数設定を開始します..."

echo ""
echo "📋 必要な環境変数:"
echo "• NEXTAUTH_SECRET"
echo "• GOOGLE_CLIENT_ID"
echo "• GOOGLE_CLIENT_SECRET"
echo "• NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
echo "• STRIPE_SECRET_KEY"
echo "• STRIPE_WEBHOOK_SECRET"
echo "• RESEND_API_KEY"
echo "• NEXT_PUBLIC_GA_ID"
echo ""

# 現在の環境変数を読み込み
source frontend/.env.local

echo "現在の環境変数:"
echo "NEXTAUTH_SECRET: ${NEXTAUTH_SECRET:0:20}..."
echo "GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:0:20}..."
echo "GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:0:20}..."
echo "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: ${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY:0:20}..."
echo "STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY:0:20}..."
echo "STRIPE_WEBHOOK_SECRET: ${STRIPE_WEBHOOK_SECRET:0:20}..."
echo "RESEND_API_KEY: ${RESEND_API_KEY:0:20}..."
echo "NEXT_PUBLIC_GA_ID: ${NEXT_PUBLIC_GA_ID:0:20}..."
echo ""

echo "Vercelに環境変数を設定しますか？ (y/n)"
read -p "> " confirm

if [[ $confirm == "y" || $confirm == "Y" ]]; then
    echo ""
    echo "Vercelにログインしてください..."
    vercel login
    
    echo ""
    echo "プロジェクトをリンクしてください..."
    vercel link
    
    echo ""
    echo "環境変数を設定中..."
    
    # 環境変数を設定
    vercel env add NEXTAUTH_SECRET production <<< "$NEXTAUTH_SECRET"
    vercel env add GOOGLE_CLIENT_ID production <<< "$GOOGLE_CLIENT_ID"
    vercel env add GOOGLE_CLIENT_SECRET production <<< "$GOOGLE_CLIENT_SECRET"
    vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY production <<< "$NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
    vercel env add STRIPE_SECRET_KEY production <<< "$STRIPE_SECRET_KEY"
    vercel env add STRIPE_WEBHOOK_SECRET production <<< "$STRIPE_WEBHOOK_SECRET"
    vercel env add RESEND_API_KEY production <<< "$RESEND_API_KEY"
    vercel env add NEXT_PUBLIC_GA_ID production <<< "$NEXT_PUBLIC_GA_ID"
    
    echo ""
    echo "✅ Vercel環境変数設定が完了しました！"
    echo ""
    echo "次のステップ:"
    echo "1. vercel --prod でデプロイ"
    echo "2. ドメイン設定の確認"
    echo "3. 本番環境での動作確認"
else
    echo "環境変数設定をスキップしました。"
fi
