#!/bin/bash

echo "📊 Google Analytics 設定を開始します..."

echo ""
echo "📋 Google Analytics アカウント作成手順:"
echo "1. https://analytics.google.com にアクセス"
echo "2. 「測定を開始」をクリック"
echo "3. アカウント名を入力（例: AICA-SyS）"
echo "4. プロパティ名を入力（例: AICA-SyS Website）"
echo "5. レポートのタイムゾーンを選択（日本）"
echo "6. 通貨を選択（日本円）"
echo "7. ビジネス情報を入力"
echo "8. データ共有設定を選択"
echo ""

echo "📋 測定ID取得手順:"
echo "1. Google Analytics ダッシュボードにログイン"
echo "2. 左メニュー「管理」"
echo "3. 「プロパティ」セクションで「データストリーム」をクリック"
echo "4. 「ウェブ」を選択"
echo "5. ウェブサイトURLを入力: https://aica-sys.vercel.app"
echo "6. ストリーム名を入力: AICA-SyS Web"
echo "7. 測定IDをコピー (G-XXXXXXXXXX)"
echo ""

read -p "Google Analytics 測定ID (G-...): " GA_ID

# キーの形式をチェック
if [[ ! $GA_ID =~ ^G- ]]; then
    echo "❌ Google Analytics測定IDの形式が正しくありません (G- で始まる必要があります)"
    exit 1
fi

# フロントエンド環境変数を更新
sed -i '' "s|NEXT_PUBLIC_GA_ID=.*|NEXT_PUBLIC_GA_ID=$GA_ID|" frontend/.env.local

echo ""
echo "✅ Google Analytics 設定が完了しました！"
echo ""
echo "設定された測定ID: $GA_ID"
echo ""
echo "次のステップ:"
echo "1. リアルタイムレポートでアクセスを確認"
echo "2. イベントトラッキングのテスト"
