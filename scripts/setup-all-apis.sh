#!/bin/bash

echo "🚀 全API設定を開始します..."

echo ""
echo "📋 設定が必要なAPIサービス:"
echo "1. Stripe (決済)"
echo "2. Resend (メール送信)"
echo "3. Google Analytics (分析)"
echo ""

# Stripe設定
echo "💳 Stripe設定"
echo "Stripeダッシュボードから正しいキーを取得してください："
echo "https://dashboard.stripe.com/test/apikeys"
echo ""
read -p "公開可能キー (pk_test_...): " STRIPE_PUBLISHABLE_KEY
read -p "シークレットキー (sk_test_...): " STRIPE_SECRET_KEY
read -p "Webhook シークレット (whsec_...): " STRIPE_WEBHOOK_SECRET

# キーの形式をチェック
if [[ ! $STRIPE_PUBLISHABLE_KEY =~ ^pk_test_ ]]; then
    echo "❌ 公開可能キーの形式が正しくありません"
    exit 1
fi

if [[ ! $STRIPE_SECRET_KEY =~ ^sk_test_ ]]; then
    echo "❌ シークレットキーの形式が正しくありません"
    exit 1
fi

if [[ ! $STRIPE_WEBHOOK_SECRET =~ ^whsec_ ]]; then
    echo "❌ Webhookシークレットの形式が正しくありません"
    exit 1
fi

# Resend設定
echo ""
echo "📧 Resend設定"
echo "ResendダッシュボードからAPIキーを取得してください："
echo "https://resend.com/api-keys"
echo ""
read -p "Resend API キー (re_...): " RESEND_API_KEY

if [[ ! $RESEND_API_KEY =~ ^re_ ]]; then
    echo "❌ Resend APIキーの形式が正しくありません"
    exit 1
fi

# Google Analytics設定
echo ""
echo "📊 Google Analytics設定"
echo "Google Analyticsから測定IDを取得してください："
echo "https://analytics.google.com"
echo ""
read -p "Google Analytics 測定ID (G-...): " GA_ID

if [[ ! $GA_ID =~ ^G- ]]; then
    echo "❌ Google Analytics測定IDの形式が正しくありません"
    exit 1
fi

# 環境変数ファイルを更新
echo ""
echo "📝 環境変数ファイルを更新中..."

sed -i '' "s|NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=.*|NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY|" frontend/.env.local
sed -i '' "s|STRIPE_SECRET_KEY=.*|STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY|" frontend/.env.local
sed -i '' "s|STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET|" frontend/.env.local
sed -i '' "s|RESEND_API_KEY=.*|RESEND_API_KEY=$RESEND_API_KEY|" frontend/.env.local
sed -i '' "s|NEXT_PUBLIC_GA_ID=.*|NEXT_PUBLIC_GA_ID=$GA_ID|" frontend/.env.local

echo ""
echo "✅ 全API設定が完了しました！"
echo ""
echo "設定されたキー:"
echo "Stripe公開可能キー: ${STRIPE_PUBLISHABLE_KEY:0:20}..."
echo "Stripeシークレットキー: ${STRIPE_SECRET_KEY:0:20}..."
echo "Stripe Webhookシークレット: ${STRIPE_WEBHOOK_SECRET:0:20}..."
echo "Resend APIキー: ${RESEND_API_KEY:0:20}..."
echo "Google Analytics測定ID: $GA_ID"
echo ""
echo "次のステップ:"
echo "1. ローカル動作確認: cd frontend && npm run dev"
echo "2. Vercelデプロイ: vercel --prod"
echo "3. 本番環境での動作確認"
