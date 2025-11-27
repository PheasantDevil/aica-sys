# Stripe本番環境設定ガイド

## 概要

AICA-SySの収益化のため、Stripe決済を本番環境で設定します。このガイドでは、Stripe商品・価格の作成から本番キーの設定、Webhookの構成まで、すべての手順を説明します。

## 前提条件

- Stripeアカウントが作成済み
- ビジネス情報が登録済み
- 銀行口座情報が登録済み

## Phase 3.1: Stripe商品・価格作成

### ステップ1: Stripeダッシュボードにログイン

1. [Stripe Dashboard](https://dashboard.stripe.com/)にアクセス
2. 本番モードに切り替え（画面左下のトグル）

### ステップ2: 商品作成

#### Premium プラン

1. 「Products」→「Add product」をクリック
2. 以下を入力：

   ```
   Name: AICA-SyS Premium
   Description: TypeScriptエコシステム特化型AI自動コンテンツ配信 - プレミアムプラン
   ```

3. Pricing設定：

   ```
   Model: Recurring
   Price: ¥1,980
   Billing period: Monthly
   Currency: JPY (日本円)
   ```

4. 「Save product」をクリック
5. 生成された価格ID（`price_xxx`）をコピー

#### Enterprise プラン（オプション）

1. 「Products」→「Add product」をクリック
2. 以下を入力：

   ```
   Name: AICA-SyS Enterprise
   Description: TypeScriptエコシステム特化型AI自動コンテンツ配信 - エンタープライズプラン
   ```

3. Pricing設定：

   ```
   Model: Recurring
   Price: カスタム（または¥19,800）
   Billing period: Monthly
   Currency: JPY (日本円)
   ```

4. 「Save product」をクリック

### ステップ3: APIキー取得

1. 「Developers」→「API keys」をクリック
2. 以下をコピー：
   - **Publishable key**: `pk_live_...`
   - **Secret key**: `sk_live_...`（Revealをクリックして表示）

⚠️ **重要**: Secret keyは一度しか表示されないので、安全な場所に保存してください。

## Phase 3.2: 環境変数設定

### Vercel環境変数（フロントエンド）

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. AICA-SySプロジェクトを選択
3. 「Settings」→「Environment Variables」
4. 以下を追加：

```bash
# Stripe公開キー
Name: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
Value: pk_live_[YOUR_PUBLISHABLE_KEY]
Environments: Production, Preview

# Stripe秘密キー
Name: STRIPE_SECRET_KEY
Value: sk_live_[YOUR_SECRET_KEY]
Environments: Production, Preview

# Premium価格ID
Name: NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID
Value: price_[YOUR_PRICE_ID]
Environments: Production, Preview

# Enterprise価格ID（オプション）
Name: NEXT_PUBLIC_STRIPE_ENTERPRISE_PRICE_ID
Value: price_[YOUR_ENTERPRISE_PRICE_ID]
Environments: Production, Preview
```

5. 「Save」をクリック
6. プロジェクトを再デプロイ

### Render環境変数（バックエンド）

1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. AICA-SySバックエンドサービスを選択
3. 「Environment」タブを開く
4. 以下を追加：

```bash
Key: STRIPE_SECRET_KEY
Value: sk_live_[YOUR_SECRET_KEY]

Key: STRIPE_PUBLISHABLE_KEY
Value: pk_live_[YOUR_PUBLISHABLE_KEY]

Key: STRIPE_PREMIUM_PRICE_ID
Value: price_[YOUR_PRICE_ID]
```

5. 「Save Changes」をクリック

### ローカル開発環境

`.env.local`を更新：

```bash
# Stripe本番キー（テスト用）
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_[YOUR_PUBLISHABLE_KEY]
STRIPE_SECRET_KEY=sk_live_[YOUR_SECRET_KEY]
NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID=price_[YOUR_PRICE_ID]
```

⚠️ **注意**: ローカル開発では通常テストキーを使用します。本番キーは慎重に扱ってください。

## Phase 3.3: Webhook設定

### ステップ1: WebhookエンドポイントURL確認

本番URL:

```
https://aica-sys.vercel.app/api/webhooks/stripe
```

### ステップ2: Stripe Webhook設定

1. Stripe Dashboard「Developers」→「Webhooks」
2. 「Add endpoint」をクリック
3. 以下を入力：

```
Endpoint URL: https://aica-sys.vercel.app/api/webhooks/stripe
Description: AICA-SyS Production Webhook
```

4. 「Select events」で以下を選択：
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
   - ✅ `checkout.session.completed`

5. 「Add endpoint」をクリック
6. 生成された「Signing secret」（`whsec_...`）をコピー

### ステップ3: Webhook秘密鍵の設定

#### Vercel

```bash
Name: STRIPE_WEBHOOK_SECRET
Value: whsec_[YOUR_WEBHOOK_SECRET]
Environments: Production, Preview
```

#### Render

```bash
Key: STRIPE_WEBHOOK_SECRET
Value: whsec_[YOUR_WEBHOOK_SECRET]
```

## テスト決済の実行

### ステップ1: テストカード情報

Stripe提供のテストカード：

```
カード番号: 4242 4242 4242 4242
有効期限: 任意の未来の日付（例: 12/25）
CVC: 任意の3桁（例: 123）
郵便番号: 任意（例: 123-4567）
```

### ステップ2: 決済フロー確認

1. 本番サイトにアクセス: `https://aica-sys.vercel.app`
2. 「料金プラン」ページへ移動
3. 「Premium」プランを選択
4. 決済画面でテストカード情報を入力
5. 決済完了を確認

### ステップ3: Stripeダッシュボードで確認

1. 「Payments」→「All payments」で決済を確認
2. 「Customers」→「All customers」で顧客を確認
3. 「Subscriptions」→「All subscriptions」でサブスクリプションを確認

### ステップ4: データベース確認

```bash
# バックエンドにSSH接続
cd backend
source venv/bin/activate

# Pythonで確認
python3 -c "
from database import SessionLocal
from models.subscription import Subscription

db = SessionLocal()
subs = db.query(Subscription).all()
for sub in subs:
    print(f'User: {sub.user_id}, Plan: {sub.plan}, Status: {sub.status}')
"
```

## トラブルシューティング

### エラー: "Invalid API Key"

**原因**: APIキーが間違っているか、テストモードと本番モードが混在

**解決**:

1. Stripeダッシュボードで本番モードになっているか確認
2. `pk_live_`と`sk_live_`のキーを使用しているか確認
3. 環境変数が正しく設定されているか確認

### エラー: "Webhook signature verification failed"

**原因**: Webhook秘密鍵が間違っている

**解決**:

1. Stripeダッシュボードで正しい`whsec_`キーを取得
2. 環境変数`STRIPE_WEBHOOK_SECRET`を更新
3. サービスを再デプロイ

### エラー: "Price not found"

**原因**: 価格IDが間違っているか、存在しない

**解決**:

1. Stripe「Products」で価格IDを確認
2. 環境変数`NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID`を更新
3. フロントエンドを再デプロイ

### 決済が完了しない

**チェックリスト**:

- [ ] Webhook URLが正しい
- [ ] Webhookイベントが正しく選択されている
- [ ] Webhook秘密鍵が設定されている
- [ ] バックエンドが稼働している
- [ ] データベース接続が正常

### ログ確認方法

#### Vercel

```bash
# Vercel CLIでログ確認
vercel logs --prod
```

#### Render

```bash
# Render Dashboardでログ確認
Logs タブを開く
```

#### Stripe

```bash
# Stripe Dashboardでイベントログ確認
Developers → Webhooks → エンドポイント → Events
```

## セキュリティベストプラクティス

### APIキー管理

1. **絶対にコミットしない**

   ```bash
   # .gitignoreに含まれていることを確認
   .env
   .env.local
   .env.*.local
   ```

2. **環境ごとに異なるキーを使用**
   - 開発: テストキー（`pk_test_`, `sk_test_`）
   - 本番: 本番キー（`pk_live_`, `sk_live_`）

3. **定期的な更新**
   - APIキーは6ヶ月ごとに更新推奨
   - 古いキーは無効化

4. **権限の最小化**
   - 必要最小限の権限のみ付与
   - 用途ごとにキーを分ける

### Webhook検証

すべてのWebhookリクエストで署名検証を実施：

```typescript
// frontend/src/app/api/webhooks/stripe/route.ts
const signature = headers.get("stripe-signature");
const event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET);
```

### PCI DSS準拠

Stripeを使用することで、PCI DSS準拠が簡単に：

- ✅ カード情報は直接サーバーに送信しない
- ✅ Stripe Elements使用で自動暗号化
- ✅ Stripeがカード情報を安全に保管

## モニタリング

### Stripeダッシュボード

定期的に確認：

1. **Payments**: 決済状況
2. **Customers**: 顧客数推移
3. **Subscriptions**: サブスクリプション状況
4. **Disputes**: 紛争・チャージバック
5. **Radar**: 不正検出

### アラート設定

Stripe Dashboardで以下のアラートを設定：

- 決済失敗
- サブスクリプション解約
- 不正疑い
- Webhook失敗

### 収益レポート

```bash
# 月次収益確認
Stripe Dashboard → Reports → Revenue
```

## 次のステップ

✅ Stripe本番設定完了後：

1. 初回テスト決済実行
2. クーポンコード作成
3. 14日間無料トライアル設定（オプション）
4. Google Analytics eコマース連携

## サポートリソース

- [Stripe公式ドキュメント](https://stripe.com/docs)
- [Stripe APIリファレンス](https://stripe.com/docs/api)
- [Webhook ガイド](https://stripe.com/docs/webhooks)
- [テストカード一覧](https://stripe.com/docs/testing)
- [Stripe サポート](https://support.stripe.com/)

## 連絡先

問題が発生した場合：

- Stripeサポート: support@stripe.com
- AICA-SyS開発チーム: [GitHub Issues](https://github.com/your-repo/aica-sys/issues)
