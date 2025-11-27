# コンテンツ推薦システム基礎実装ガイド

## 概要

コンテンツ推薦システムの基礎実装を完了しました。このシステムは、ユーザーの閲覧履歴を記録し、類似記事やトレンド記事を推薦する機能を提供します。

## 実装内容

### 1. バックエンド実装

#### データベース連携

- `ContentRecommendationService`を改善し、データベースセッションを受け取るように変更
- `UserInteraction`モデルを使用して閲覧履歴をデータベースに保存
- `AutomatedContentDB`モデルから実際のコンテンツデータを取得

#### 推薦アルゴリズム

**ユーザーベース推薦 (`recommend_for_user`)**

- ユーザーの閲覧履歴から興味プロフィールを構築
- カテゴリ・タグ・キーワードに基づいてコンテンツをスコアリング
- 閲覧済みコンテンツを除外可能

**類似コンテンツ推薦 (`recommend_similar_content`)**

- コンテンツのベクトル表現（タグ、カテゴリ、キーワード）を構築
- コサイン類似度で類似コンテンツを計算
- 公開済みコンテンツから類似度の高い記事を推薦

**トレンドコンテンツ推薦 (`recommend_trending`)**

- 最近 24 時間のインタラクション（閲覧、いいね、シェア）を集計
- インタラクションスコアと公開日の新しさを考慮
- カテゴリフィルタリング対応

**パーソナライズド推薦 (`recommend_personalized`)**

- ユーザーベース推薦（70%）とトレンド推薦（30%）をハイブリッド
- 重複除去とスコアソート

#### コンテンツベクトル構築

`_build_content_vector`メソッドで以下からベクトルを構築：

- SEO キーワード（重み: 1.0）
- カテゴリ（重み: 2.0）
- タグ（重み: 1.5）
- 技術用語（重み: 1.0）

#### インタラクション記録

`record_interaction`メソッドで以下を記録：

- メモリキャッシュ（高速アクセス用）
- データベース保存（永続化）
- セッション ID 対応（未ログインユーザー）

### 2. フロントエンド実装

#### API クライアント拡張

`frontend/src/lib/api-client.ts`に以下を追加：

- `getRecommendations`: ユーザーへの推薦記事取得
- `getSimilarContent`: 類似記事取得
- `getTrendingContent`: トレンド記事取得
- `recordInteraction`: インタラクション記録

#### コンポーネント

**`RecommendedArticles`コンポーネント**

- 類似記事、トレンド記事、パーソナライズド記事を表示
- ローディング状態とエラーハンドリング
- レスポンシブグリッドレイアウト

**`ArticleViewTracker`コンポーネント**

- 記事閲覧時に自動的にインタラクションを記録
- メタデータ（カテゴリ、タグ、タイトル）を含む
- ユーザーエージェントとリファラーを記録

#### 記事詳細ページ統合

`frontend/src/app/articles/[slug]/page.tsx`に以下を追加：

- 閲覧履歴の自動記録
- 類似記事推薦セクション

## API エンドポイント

### GET `/api/content-quality/recommendations/{user_id}`

ユーザーへのパーソナライズド推薦記事を取得

**パラメータ:**

- `user_id` (path): ユーザー ID
- `limit` (query): 取得件数（デフォルト: 10）

**レスポンス:**

```json
{
  "success": true,
  "user_id": "123",
  "recommendations": [
    {
      "id": 1,
      "title": "記事タイトル",
      "slug": "article-slug",
      "summary": "記事の要約",
      "score": 85.5,
      "published_at": "2024-01-15T10:00:00Z"
    }
  ],
  "count": 10
}
```

### GET `/api/content-quality/similar/{content_id}`

類似記事を取得

**パラメータ:**

- `content_id` (path): コンテンツ ID
- `limit` (query): 取得件数（デフォルト: 5）

**レスポンス:**

```json
{
  "success": true,
  "content_id": "1",
  "similar_contents": [
    {
      "id": 2,
      "title": "類似記事タイトル",
      "slug": "similar-article-slug",
      "summary": "記事の要約",
      "similarity": 0.85,
      "published_at": "2024-01-15T10:00:00Z"
    }
  ],
  "count": 5
}
```

### GET `/api/content-quality/trending`

トレンド記事を取得

**パラメータ:**

- `category` (query, optional): カテゴリフィルタ
- `limit` (query): 取得件数（デフォルト: 10）

### POST `/api/content-quality/interaction`

インタラクションを記録

**リクエストボディ:**

```json
{
  "user_id": "123",
  "content_id": "1",
  "interaction_type": "view",
  "metadata": {
    "category": "tutorial",
    "tags": ["TypeScript", "JavaScript"]
  }
}
```

## 使用方法

### バックエンド

```python
from services.content_recommendation_service import ContentRecommendationService
from database import get_db

# データベースセッションを渡してサービスを初期化
db = next(get_db())
recommendation_service = ContentRecommendationService(db=db)

# ユーザーへの推薦記事を取得
recommendations = await recommendation_service.recommend_personalized(
    user_id="123",
    limit=10
)

# 類似記事を取得
similar = await recommendation_service.recommend_similar_content(
    content_id="1",
    limit=5
)

# インタラクションを記録
recommendation_service.record_interaction(
    user_id="123",
    content_id="1",
    interaction_type="view",
    metadata={"category": "tutorial"}
)
```

### フロントエンド

```tsx
import { RecommendedArticles } from "@/components/content/recommended-articles";
import { ArticleViewTracker } from "@/components/content/article-view-tracker";

// 記事詳細ページで使用
<ArticleViewTracker
  articleId={article.id}
  metadata={{
    category: article.category,
    tags: article.tags,
  }}
/>

<RecommendedArticles
  contentId={article.id}
  type="similar"
  limit={6}
  title="関連記事"
/>
```

## 今後の改善点

1. **ベクトル検索の高度化**
   - 埋め込みベクトル（OpenAI/Groq）を使用したセマンティック検索
   - より精度の高い類似度計算

2. **推薦アルゴリズムの改善**
   - 協調フィルタリング（ユーザー間の類似性）
   - コンテンツベースフィルタリングの精度向上
   - ハイブリッド推薦の重み調整

3. **パフォーマンス最適化**
   - 推薦結果のキャッシング
   - バッチ処理によるスコア計算の最適化
   - インデックス最適化

4. **A/B テスト対応**
   - 異なる推薦アルゴリズムの比較
   - クリック率（CTR）の測定
   - 推薦効果の分析

5. **リアルタイム推薦**
   - WebSocket を使用したリアルタイム更新
   - ユーザー行動に基づく動的推薦

## 関連ドキュメント

- [実装状況レポート](../docs/implementation-status-report-2025-11.md)
- [品質スコアリング改善ガイド](./quality-scoring-improvement-guide.md)
