# SEO 基本設定ガイド

**作成日**: 2025-11-18  
**ステータス**: P1タスク - SEO 基本設定

---

## ✅ 完了した設定

1. **Google Analytics 4 (GA4)**
   - 計測ID (`NEXT_PUBLIC_GA_ID`) を利用して Next.js に組み込み
   - `@next/third-parties/google` の `<GoogleAnalytics />` を `app/layout.tsx` に追加
   - 保存時に自動で全ページへ埋め込み

2. **Google Search Console**
   - サイト検証コード (`NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION`) を `metadata.verification` に設定
   - `app/layout.tsx` の `<head>` から自動出力

3. **ベースURLの正規化**
   - `NEXT_PUBLIC_BASE_URL` をメタデータ・OGP・サイトマップ各所で使用
   - すべて `https://aica-sys.vercel.app` を基準に統一

4. **ドキュメント更新**
   - `docs/twitter-api-integration-guide.md` と `docs/environment-setup.md` に SEO 変数を追記
   - このガイドで設定手順を集約

---

## 🧩 必要な環境変数（Frontend）

`.env.local` または Vercel/Render/GitHub Secrets に以下を設定してください。

| 変数名                                 | 用途                                |
| -------------------------------------- | ----------------------------------- |
| `NEXT_PUBLIC_BASE_URL`                 | Canonical URL / OGP 生成用          |
| `NEXT_PUBLIC_API_URL`                  | フロントエンドからの API 参照先     |
| `NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION` | Search Console 用のサイト検証コード |
| `NEXT_PUBLIC_GA_ID`                    | GA4 測定ID (形式: `G-XXXXXXXXXX`)   |

> 参考: `backend/env.example` にサンプルが記載されています。

---

## 📈 Google Analytics 4 設定手順

1. [GA4 プロパティ](https://analytics.google.com/) を作成
2. 測定ID（`G-XXXXXXXXXX`）を取得
3. Vercel / Render / GitHub Secrets に `NEXT_PUBLIC_GA_ID` を設定
4. デプロイ後、GA4 のリアルタイムビューでイベント受信を確認

### ローカルでの確認

```bash
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX npm run dev
# ブラウザでアクセスし、GA4リアルタイムにヒットが届くか確認
```

---

## 🔍 Google Search Console 設定手順

1. [Search Console](https://search.google.com/search-console) にログイン
2. プロパティタイプ「ドメイン」または「URL プレフィックス」を選択
3. 「HTML タグ（メタタグ）」の検証コードを取得
4. `NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION="google-site-verification=xxxx"` を設定
5. デプロイ後、Search Console で「確認」を実行

> `app/layout.tsx` がメタタグを自動出力するため、追加作業は不要です。

---

## 🗺️ サイトマップ & robots.txt

- `frontend/src/app/sitemap.xml/route.ts`
  - 静的/動的ページを統合した XML サイトマップを生成
  - `NEXT_PUBLIC_BASE_URL` を基準に URL を生成
- `frontend/src/app/robots.txt/route.ts`
  - 本番環境のみクローリングを許可
  - `Sitemap: <BASE_URL>/sitemap.xml` を出力

追加で Search Console にサイトマップURLを登録してください。

---

## 🖼️ OGP 画像自動生成 & プレビュー

1. **自動生成 API**
   - `frontend/src/app/api/og/route.tsx`
   - `SEOUtils.generateOGImageUrl()` が `/api/og` を呼び出し、タイトル・説明・ハッシュタグに応じて 1200x630px の画像を生成
   - `theme` / `tags` / `badge` / `slug` などのクエリパラメータでバリエーション指定が可能

2. **既定メタデータ**
   - `app/layout.tsx` の `metadata.openGraph` / `twitter` がデフォルトで `/api/og?...` を参照
   - 各記事ページ (`app/articles/[slug]/page.tsx`) は `SEOUtils.generateOGImageUrl` を使用し、記事本文に合わせた OGP を生成

3. **プレビュー検証手順**
   - 端末1: フロントエンド開発サーバーを起動
     ```bash
     cd frontend
     npm run dev
     ```
   - 端末2: ルートディレクトリで OGP プレビューを取得
     ```bash
     npm run og:preview -- --title="TypeScript 2025 新機能" --description="AST最適化と型安全性が向上" --slug="typescript-2025" --tags="TypeScript,AI自動生成,Next.js"
     ```
   - 生成された PNG は `tmp/og-previews/` に保存されます。
   - **手作業が必要な項目**: ブラウザで `http://localhost:3000/api/og?title=...` を直接開き、SNS プレビュー（Twitter Card Validator 等）で見た目を最終確認。

> 本番環境では Vercel Edge Runtime で自動生成されるため追加設定は不要です。

---

## 🔄 運用フロー

1. **新しいページ追加時**:
   - `SEOUtils.generateMetadata` を利用してページ固有のメタ情報を定義
   - 必要に応じて構造化データを追加

2. **Search Console**
   - カバレッジ / Core Web Vitals / インデックス状況を週次確認
   - サイトマップ送信状況をモニタリング

3. **Analytics**
   - GA4 のリアルタイム / イベント / コンバージョンをモニタリング
   - 将来的に BigQuery 連携や Looker Studio ダッシュボード化を検討

---

## 📚 参考リンク

- [Google Analytics 4 導入ガイド](https://support.google.com/analytics/answer/9304153)
- [Search Console サイト検証](https://support.google.com/webmasters/answer/9008080)
- [Next.js Metadata API](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)
- [@next/third-parties/google](https://nextjs.org/docs/app/building-your-application/optimizing/third-party-scripts)

---

これで SEO 基本設定の初期セットアップは完了です。追加のモニタリングや分析ツールを導入する場合は、このドキュメントに追記してください。
