# Stripe 本番設定チェックリスト

**作成日**: 2025-11-18  
**ステータス**: P0 タスク - 実運用開始準備

---

## 📋 設定チェックリスト

### Phase 1: Stripe 商品・価格作成

#### 1.1 Stripe ダッシュボード準備

- [ ] Stripe アカウント作成済み
- [ ] ビジネス情報登録済み
- [ ] 銀行口座情報登録済み
- [ ] 本番モードに切り替え（画面左下のトグル）

#### 1.2 Premium プラン作成

- [ ] 「Products」→「Add product」をクリック
- [ ] 以下を入力：
  ```
  Name: AICA-SyS Premium
  Description: TypeScriptエコシステム特化型AI自動コンテンツ配信 - プレミアムプラン
  ```
- [ ] Pricing 設定：
  ```
  Model: Recurring
  Price: ¥1,980
  Billing period: Monthly
  Currency: JPY (日本円)
  ```
- [ ] 「Save product」をクリック
- [ ] 価格 ID（`price_xxx`）をコピーして保存

#### 1.3 Enterprise プラン作成（オプション）

- [ ] 「Products」→「Add product」をクリック
- [ ] 以下を入力：
  ```
  Name: AICA-SyS Enterprise
  Description: TypeScriptエコシステム特化型AI自動コンテンツ配信 - エンタープライズプラン
  ```
- [ ] Pricing 設定：
  ```
  Model: Recurring
  Price: カスタム（または¥19,800）
  Billing period: Monthly
  Currency: JPY (日本円)
  ```
- [ ] 「Save product」をクリック
- [ ] 価格 ID（`price_xxx`）をコピーして保存

#### 1.4 API キー取得

- [ ] 「Developers」→「API keys」をクリック
- [ ] 以下をコピーして安全な場所に保存：
  - **Publishable key**: `pk_live_...`
  - **Secret key**: `sk_live_...`（Reveal をクリックして表示）

⚠️ **重要**: Secret key は一度しか表示されないので、必ず保存してください。

---

### Phase 2: 環境変数設定

#### 2.1 Vercel 環境変数（フロントエンド）

- [ ] [Vercel Dashboard](https://vercel.com/dashboard)にログイン
- [ ] AICA-SyS プロジェクトを選択
- [ ] 「Settings」→「Environment Variables」
- [ ] 以下を追加：

| 変数名                                   | 値                                 | 環境                              |
| ---------------------------------------- | ---------------------------------- | --------------------------------- |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`     | `pk_live_[YOUR_PUBLISHABLE_KEY]`   | Production, Preview               |
| `STRIPE_SECRET_KEY`                      | `sk_live_[YOUR_SECRET_KEY]`        | Production, Preview               |
| `NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID`    | `price_[YOUR_PRICE_ID]`            | Production, Preview               |
| `NEXT_PUBLIC_STRIPE_ENTERPRISE_PRICE_ID` | `price_[YOUR_ENTERPRISE_PRICE_ID]` | Production, Preview（オプション） |
| `STRIPE_WEBHOOK_SECRET`                  | `whsec_[YOUR_WEBHOOK_SECRET]`      | Production, Preview               |

- [ ] 「Save」をクリック
- [ ] プロジェクトを再デプロイ

#### 2.2 Render 環境変数（バックエンド）

- [ ] [Render Dashboard](https://dashboard.render.com/)にログイン
- [ ] AICA-SyS バックエンドサービスを選択
- [ ] 「Environment」タブを開く
- [ ] 以下を追加：

| 変数名                    | 値                               |
| ------------------------- | -------------------------------- |
| `STRIPE_SECRET_KEY`       | `sk_live_[YOUR_SECRET_KEY]`      |
| `STRIPE_PUBLISHABLE_KEY`  | `pk_live_[YOUR_PUBLISHABLE_KEY]` |
| `STRIPE_PREMIUM_PRICE_ID` | `price_[YOUR_PRICE_ID]`          |
| `STRIPE_WEBHOOK_SECRET`   | `whsec_[YOUR_WEBHOOK_SECRET]`    |

- [ ] 「Save Changes」をクリック
- [ ] サービスを再起動

#### 2.3 GitHub Secrets 設定（CI/CD 用）

- [ ] [GitHub Settings](https://github.com/PheasantDevil/aica-sys/settings/secrets/actions)にアクセス
- [ ] 以下を追加：

| Secret 名                 | 値                               |
| ------------------------- | -------------------------------- |
| `STRIPE_SECRET_KEY`       | `sk_live_[YOUR_SECRET_KEY]`      |
| `STRIPE_PUBLISHABLE_KEY`  | `pk_live_[YOUR_PUBLISHABLE_KEY]` |
| `STRIPE_PREMIUM_PRICE_ID` | `price_[YOUR_PRICE_ID]`          |
| `STRIPE_WEBHOOK_SECRET`   | `whsec_[YOUR_WEBHOOK_SECRET]`    |

---

### Phase 3: Webhook 設定

#### 3.1 Webhook エンドポイント URL 確認

本番 URL:

```
https://aica-sys.vercel.app/api/webhooks/stripe
```

#### 3.2 Stripe Webhook 設定

- [ ] Stripe Dashboard「Developers」→「Webhooks」
- [ ] 「Add endpoint」をクリック
- [ ] 以下を入力：
  ```
  Endpoint URL: https://aica-sys.vercel.app/api/webhooks/stripe
  Description: AICA-SyS Production Webhook
  ```
- [ ] 「Select events」で以下を選択：
  - ✅ `customer.subscription.created`
  - ✅ `customer.subscription.updated`
  - ✅ `customer.subscription.deleted`
  - ✅ `invoice.payment_succeeded`
  - ✅ `invoice.payment_failed`
  - ✅ `checkout.session.completed`
- [ ] 「Add endpoint」をクリック
- [ ] 生成された「Signing secret」（`whsec_...`）をコピーして保存

#### 3.3 Webhook テスト

- [ ] Stripe Dashboard で「Send test webhook」をクリック
- [ ] イベントを選択（例: `checkout.session.completed`）
- [ ] 「Send test webhook」をクリック
- [ ] Vercel ログで Webhook 受信を確認

---

### Phase 4: テスト決済

#### 4.1 テストカード情報

Stripe 提供のテストカード：

```
カード番号: 4242 4242 4242 4242
有効期限: 任意の未来の日付（例: 12/25）
CVC: 任意の3桁（例: 123）
郵便番号: 任意（例: 123-4567）
```

#### 4.2 決済フロー確認

- [ ] 本番サイトにアクセス: `https://aica-sys.vercel.app`
- [ ] 「料金プラン」ページへ移動
- [ ] 「Premium」プランを選択
- [ ] 決済画面でテストカード情報を入力
- [ ] 決済完了を確認

#### 4.3 Stripe ダッシュボードで確認

- [ ] 「Payments」→「All payments」で決済を確認
- [ ] 「Customers」→「All customers」で顧客を確認
- [ ] 「Subscriptions」→「All subscriptions」でサブスクリプションを確認

#### 4.4 データベース確認

- [ ] サブスクリプションデータが正しく保存されているか確認
- [ ] ユーザー情報が正しく更新されているか確認

---

## ✅ 完了チェックリスト

### Stripe 設定

- [ ] 商品・価格作成完了
- [ ] API キー取得・保存完了
- [ ] Webhook 設定完了
- [ ] Webhook 秘密鍵取得・保存完了

### 環境変数設定

- [ ] Vercel 環境変数設定完了
- [ ] Render 環境変数設定完了
- [ ] GitHub Secrets 設定完了

### 動作確認

- [ ] テスト決済成功
- [ ] Webhook 受信確認
- [ ] データベース保存確認

---

## 🔄 次のステップ

1. ✅ Stripe 本番設定（このチェックリスト）
2. ⏳ 初回テスト決済実行
3. ⏳ クーポンコード作成（オプション）
4. ⏳ 14 日間無料トライアル設定（オプション）

---

## 📚 参考ドキュメント

- [Stripe 本番環境設定ガイド](./setup-stripe-production.md)
- [実装ステータスレポート](./implementation-status-report-2025-11.md)
- [本番環境デプロイ確認チェックリスト](./production-deployment-checklist.md)

---

## ⚠️ 注意事項

1. **セキュリティ**

   - Secret key は絶対に公開しない
   - GitHub にコミットしない（`.env.local`は`.gitignore`に含まれている）
   - 定期的にキーをローテーション

2. **テストモードと本番モード**

   - 開発時はテストキー（`pk_test_`, `sk_test_`）を使用
   - 本番環境のみ本番キー（`pk_live_`, `sk_live_`）を使用

3. **Webhook 検証**

   - すべての Webhook リクエストで署名検証を実施
   - 本番環境では必ず HTTPS を使用

4. **モニタリング**
   - Stripe Dashboard で定期的に決済状況を確認
   - アラート設定を有効化
