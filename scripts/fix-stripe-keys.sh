#!/bin/bash

echo "🔧 Stripe キーを修正します..."

echo ""
echo "正しいStripeキーを入力してください："
echo ""

read -p "公開可能キー (pk_test_...): " STRIPE_PUBLISHABLE_KEY
read -p "シークレットキー (sk_test_...): " STRIPE_SECRET_KEY
read -p "Webhook シークレット (whsec_...): " STRIPE_WEBHOOK_SECRET

# キーの形式をチェック
if [[ ! $STRIPE_PUBLISHABLE_KEY =~ ^pk_test_ ]]; then
    echo "❌ 公開可能キーの形式が正しくありません (pk_test_ で始まる必要があります)"
    exit 1
fi

if [[ ! $STRIPE_SECRET_KEY =~ ^sk_test_ ]]; then
    echo "❌ シークレットキーの形式が正しくありません (sk_test_ で始まる必要があります)"
    exit 1
fi

if [[ ! $STRIPE_WEBHOOK_SECRET =~ ^whsec_ ]]; then
    echo "❌ Webhookシークレットの形式が正しくありません (whsec_ で始まる必要があります)"
    exit 1
fi

# フロントエンド環境変数を更新
sed -i '' "s|NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=.*|NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY|" frontend/.env.local
sed -i '' "s|STRIPE_SECRET_KEY=.*|STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY|" frontend/.env.local
sed -i '' "s|STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET|" frontend/.env.local

echo ""
echo "✅ Stripe キーを修正しました！"
echo ""
echo "設定されたキー:"
echo "公開可能キー: ${STRIPE_PUBLISHABLE_KEY:0:20}..."
echo "シークレットキー: ${STRIPE_SECRET_KEY:0:20}..."
echo "Webhook シークレット: ${STRIPE_WEBHOOK_SECRET:0:20}..."
