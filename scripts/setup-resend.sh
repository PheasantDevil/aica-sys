#!/bin/bash

echo "📧 Resend メール送信設定を開始します..."

echo ""
echo "📋 Resend アカウント作成手順:"
echo "1. https://resend.com にアクセス"
echo "2. 「Get Started」をクリック"
echo "3. メールアドレス、パスワードを入力"
echo "4. メール認証を完了"
echo "5. ドメインを追加（オプション）"
echo ""

echo "📋 API キー取得手順:"
echo "1. Resend ダッシュボードにログイン"
echo "2. 左メニュー「API Keys」"
echo "3. 「Create API Key」をクリック"
echo "4. キー名を入力（例: AICA-SyS Production）"
echo "5. 権限を選択（Send emails）"
echo "6. 生成されたキーをコピー (re_...)"
echo ""

read -p "Resend API キー (re_...): " RESEND_API_KEY

# キーの形式をチェック
if [[ ! $RESEND_API_KEY =~ ^re_ ]]; then
    echo "❌ Resend APIキーの形式が正しくありません (re_ で始まる必要があります)"
    exit 1
fi

# フロントエンド環境変数を更新
sed -i '' "s|RESEND_API_KEY=.*|RESEND_API_KEY=$RESEND_API_KEY|" frontend/.env.local

echo ""
echo "✅ Resend 設定が完了しました！"
echo ""
echo "設定されたキー: ${RESEND_API_KEY:0:20}..."
echo ""
echo "次のステップ:"
echo "1. メール送信テスト: http://localhost:3000/api/email/send"
echo "2. メールテンプレートの確認"
