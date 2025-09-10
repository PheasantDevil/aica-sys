#!/bin/bash

echo "💳 Stripe 設定を開始します..."

echo ""
echo "📋 Stripe アカウント作成手順:"
echo "1. https://stripe.com にアクセス"
echo "2. 「アカウントを作成」をクリック"
echo "3. メールアドレス、パスワードを入力"
echo "4. 電話番号認証を完了"
echo "5. ビジネス情報を入力"
echo ""

echo "📋 API キー取得手順:"
echo "1. Stripe ダッシュボードにログイン"
echo "2. 左メニュー「開発者」→「API キー」"
echo "3. 「公開可能キー」をコピー (pk_test_...)"
echo "4. 「シークレットキー」をコピー (sk_test_...)"
echo "5. 「Webhook エンドポイント」で新しいエンドポイントを作成"
echo "   - URL: https://aica-sys.vercel.app/api/stripe/webhook"
echo "   - イベント: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted"
echo "6. Webhook シークレットをコピー (whsec_...)"
echo ""

read -p "公開可能キー (pk_test_...): " STRIPE_PUBLISHABLE_KEY
read -p "シークレットキー (sk_test_...): " STRIPE_SECRET_KEY
read -p "Webhook シークレット (whsec_...): " STRIPE_WEBHOOK_SECRET

# フロントエンド環境変数を更新
sed -i '' "s|NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=.*|NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY|" frontend/.env.local
sed -i '' "s|STRIPE_SECRET_KEY=.*|STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY|" frontend/.env.local
sed -i '' "s|STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET|" frontend/.env.local

echo ""
echo "✅ Stripe 設定が完了しました！"
echo ""
echo "設定されたキー:"
echo "公開可能キー: ${STRIPE_PUBLISHABLE_KEY:0:20}..."
echo "シークレットキー: ${STRIPE_SECRET_KEY:0:20}..."
echo "Webhook シークレット: ${STRIPE_WEBHOOK_SECRET:0:20}..."
echo ""
echo "次のステップ:"
echo "1. ローカル動作確認: cd frontend && npm run dev"
echo "2. 決済テスト: http://localhost:3000/pricing"
echo "3. Stripe ダッシュボードでテスト決済を確認"
