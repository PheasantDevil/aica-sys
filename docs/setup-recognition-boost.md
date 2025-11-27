# 認知度向上施策実装ガイド

## 概要

AICA-SyS の認知度を高めるため、SEO 最適化、ソーシャルメディア展開、初回キャンペーンを実施します。

## Phase 4.1: Google Search Console 設定

### ステップ 1: サイト所有権確認

1. [Google Search Console](https://search.google.com/search-console)にアクセス
2. 「プロパティを追加」をクリック
3. URL プレフィックスを選択: `https://aica-sys.vercel.app`
4. 所有権確認方法を選択

#### 方法 A: HTML ファイルアップロード

1. 確認ファイルをダウンロード（例: `google-verification-xxxxx.html`）
2. `public/`フォルダに配置
3. Vercel に再デプロイ
4. 「確認」をクリック

#### 方法 B: メタタグ

1. メタタグをコピー
2. `frontend/src/app/layout.tsx`の`<head>`に追加：
   ```tsx
   <meta name="google-site-verification" content="xxxxxxxxxxxxx" />
   ```
3. 再デプロイ後、「確認」をクリック

### ステップ 2: サイトマップ送信

1. Search Console ダッシュボードで「サイトマップ」を選択
2. 以下の URL を入力：
   ```
   https://aica-sys.vercel.app/sitemap.xml
   ```
3. 「送信」をクリック
4. ステータスが「成功」になるまで待機（数時間〜数日）

### ステップ 3: インデックス登録リクエスト

1. 「URL 検査」ツールを開く
2. 重要な URL を入力：
   ```
   https://aica-sys.vercel.app/
   https://aica-sys.vercel.app/articles
   https://aica-sys.vercel.app/pricing
   ```
3. 各 URL で「インデックス登録をリクエスト」をクリック

### ステップ 4: Core Web Vitals 確認

1. 「エクスペリエンス」→「Core Web Vitals」
2. 問題があれば「PageSpeed Insights」で詳細確認
3. Vercel Speed Insights と照合

### モニタリング設定

週次で以下を確認：

- 検索パフォーマンス（クリック数、表示回数）
- インデックス登録状況
- モバイルユーザビリティ
- Core Web Vitals

## Phase 4.2: ソーシャルメディア設定

### Twitter（X）アカウント作成

#### アカウント設定

1. [Twitter](https://twitter.com)で新規アカウント作成
2. ユーザー名: `@aica_sys`（または類似）
3. プロフィール設定：
   ```
   名前: AICA-SyS
   プロフィール: TypeScriptエコシステム特化型AI自動コンテンツ配信 | 最新トレンド・技術記事を毎日自動生成 | #TypeScript #AI #DevTools
   リンク: https://aica-sys.vercel.app
   場所: Tokyo, Japan
   ```

#### プロフィール画像作成

```bash
# ロゴ画像を400x400pxに変換
# public/logo.png を使用
```

#### ヘッダー画像作成

1. サイズ: 1500x500px
2. ブランドカラーを使用
3. キャッチコピー追加

#### 初回投稿

```
🚀 AICA-SySが始動しました！

TypeScriptエコシステムの最新トレンドを
AIが毎日自動分析・記事化📝

✨ 高品質な技術記事
🤖 AI駆動コンテンツ生成
📊 データドリブン分析

👉 https://aica-sys.vercel.app

#TypeScript #AI #開発ツール #TechNews
```

### OGP 画像生成

#### デフォルト OG 画像作成

1. サイズ: 1200x630px
2. 以下の要素を含める：
   - ロゴ
   - サービス名
   - キャッチコピー
   - URL

3. `public/og-default.png`として保存

#### 動的 OG 画像生成（オプション）

`frontend/src/app/api/og/route.tsx`を作成（Next.js の ImageResponse 使用）

### ソーシャルメディア自動投稿設定

#### GitHub Actions ワークフロー作成

`.github/workflows/social-post.yml`:

```yaml
name: Social Media Auto Post

on:
  schedule:
    # 新記事公開時に自動投稿（毎日午前9時）
    - cron: "0 0 * * 1-5"
  workflow_dispatch:

jobs:
  post-to-twitter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get latest article
        id: article
        run: |
          # 最新記事取得ロジック

      - name: Post to Twitter
        uses: snow-actions/tweet@v1
        with:
          status: |
            📝 新着記事公開！
            ${{ steps.article.outputs.title }}
            👉 ${{ steps.article.outputs.url }}
            #TypeScript #技術記事
        env:
          TWITTER_CONSUMER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_CONSUMER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_TOKEN_SECRET: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
```

## Phase 4.3: 初回キャンペーン実施

### クーポンコード作成（Stripe）

1. Stripe Dashboard →「Products」→「Coupons」
2. 「Create coupon」をクリック
3. 設定：
   ```
   Name: LAUNCH2024
   Type: Percentage discount
   Discount: 20% off
   Duration: Once / 3 months / Forever（選択）
   Max redemptions: 100（制限数）
   ```
4. 「Create coupon」をクリック

### ランディングページ最適化

#### キャンペーンバナー追加

`frontend/src/app/page.tsx`に追加：

```tsx
<div className="bg-primary text-primary-foreground p-4 text-center">
  <p className="text-lg font-bold">🎉 ローンチキャンペーン実施中！ クーポンコード「LAUNCH2024」で20%オフ</p>
</div>
```

#### CTA 強化

- ボタン文言変更
- 緊急性の追加（期間限定）
- 社会的証明（初回ユーザー数表示）

### Google Analytics 4 設定

#### GA4 プロパティ作成

1. [Google Analytics](https://analytics.google.com/)にログイン
2. 「管理」→「プロパティを作成」
3. プロパティ名: `AICA-SyS Production`
4. タイムゾーン: `日本`
5. 通貨: `日本円（JPY）`

#### 測定 ID 取得

1. 「データストリーム」→「ウェブ」
2. URL: `https://aica-sys.vercel.app`
3. ストリーム名: `Production`
4. 測定 ID（`G-XXXXXXXXXX`）をコピー

#### Vercel 環境変数設定

```bash
Name: NEXT_PUBLIC_GA_MEASUREMENT_ID
Value: G-XXXXXXXXXX
Environments: Production
```

#### フロントエンド実装確認

`frontend/src/lib/analytics.ts`が既に実装済みであることを確認

#### イベントトラッキング設定

主要イベント：

- `page_view`: ページビュー
- `sign_up`: 新規登録
- `purchase`: サブスクリプション購入
- `article_view`: 記事閲覧
- `social_share`: ソーシャルシェア

### キャンペーン実施スケジュール

#### Week 1: ソフトローンチ

- Twitter 初回投稿
- 友人・知人への共有
- Product Hunt 投稿準備

#### Week 2: パブリックローンチ

- Product Hunt 投稿
- Hacker News 投稿
- Reddit r/typescript 投稿
- Tech 系 Discord コミュニティ投稿

#### Week 3: コンテンツマーケティング

- 技術ブログ（Zenn、Qiita）に紹介記事
- YouTube 技術解説動画
- ポッドキャスト出演依頼

#### Week 4: 振り返りと最適化

- アナリティクス分析
- ユーザーフィードバック収集
- A/B テスト実施

## 成功指標（KPI）

### 1 週間以内

- Twitter フォロワー: 100 人
- サイト訪問: 500 PV
- 新規登録: 10 人

### 1 ヶ月以内

- Twitter フォロワー: 500 人
- サイト訪問: 5,000 PV
- 新規登録: 100 人
- 有料会員: 5 人
- MRR: ¥9,900

### 3 ヶ月以内

- Twitter フォロワー: 2,000 人
- サイト訪問: 30,000 PV
- 新規登録: 500 人
- 有料会員: 50 人
- MRR: ¥99,000

## モニタリングダッシュボード

### 日次確認

- [ ] Google Analytics: PV、ユーザー数
- [ ] Twitter: フォロワー数、エンゲージメント
- [ ] Stripe: 新規サブスクリプション

### 週次確認

- [ ] Search Console: 検索順位、クリック率
- [ ] 記事品質スコア平均
- [ ] コンバージョン率

### 月次確認

- [ ] MRR 推移
- [ ] チャーン率
- [ ] LTV/CAC 比率
- [ ] コンテンツパフォーマンス分析

## トラブルシューティング

### Search Console でインデックスされない

**原因**: robots.txt、サイトマップの問題

**解決**:

1. `https://aica-sys.vercel.app/robots.txt`を確認
2. `Allow: /`が設定されているか確認
3. サイトマップ URL が正しいか確認

### OGP 画像が表示されない

**原因**: 画像サイズ、キャッシュ

**解決**:

1. 画像サイズ確認（1200x630px）
2. [OGP 確認ツール](https://www.opengraph.xyz/)でテスト
3. Twitter Card Validator でテスト
4. CDN キャッシュクリア

### GA4 でイベントが記録されない

**原因**: 測定 ID、実装ミス

**解決**:

1. 測定 ID が正しいか確認
2. `gtag.js`が読み込まれているか確認
3. ブラウザ開発者ツールでネットワーク確認

## チェックリスト

### ローンチ前

- [ ] Google Search Console 設定完了
- [ ] サイトマップ送信完了
- [ ] Twitter アカウント作成完了
- [ ] OGP 画像生成完了
- [ ] GA4 設定完了
- [ ] Stripe クーポン作成完了

### ローンチ時

- [ ] Twitter 初回投稿
- [ ] キャンペーンバナー表示
- [ ] Product Hunt 投稿準備
- [ ] プレスリリース準備（オプション）

### ローンチ後

- [ ] 毎日のアナリティクス確認
- [ ] ユーザーフィードバック収集
- [ ] A/B テスト実施
- [ ] コンテンツ最適化

## 参考リソース

- [Google Search Console ヘルプ](https://support.google.com/webmasters)
- [Twitter for Business](https://business.twitter.com/)
- [OGP 仕様](https://ogp.me/)
- [Google Analytics 4 ヘルプ](https://support.google.com/analytics)
- [Product Hunt ベストプラクティス](https://www.producthunt.com/ship)
