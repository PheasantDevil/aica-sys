# Phase 10-1: デイリー記事生成ワークフロー

## 概要

平日毎日、最新の技術トレンドを分析し、高品質な記事を自動生成するシステム。

## ファイル構成と役割

```plaintext
Phase 10-1 関連ファイル:
├── .github/workflows/daily-articles.yml          # GitHub Actions ワークフロー定義
├── backend/services/source_aggregator_service.py # 情報収集サービス
├── backend/services/content_automation_service.py # 記事生成サービス
├── backend/models/automated_content.py           # データモデル
├── scripts/generate_daily_article.py             # 実行スクリプト
└── docs/phase10-1-daily-articles.md              # この計画書
```

## 情報収集ソース

### 1. Hacker News API

- **URL**: `https://hacker-news.firebaseio.com/v0/topstories.json`
- **取得**: トップ30件
- **重み**: 高（技術コミュニティで実証済み）

### 2. Dev.to API

- **URL**: `https://dev.to/api/articles`
- **取得**: 人気記事トップ20件
- **重み**: 中（実践的コンテンツ）

### 3. GitHub Trending

- **URL**: `https://api.github.com/search/repositories`
- **取得**: 日次トレンディングリポジトリ
- **重み**: 高（実際の開発トレンド）

### 4. Reddit r/programming

- **URL**: `https://www.reddit.com/r/programming/hot.json`
- **取得**: ホット投稿トップ25件
- **重み**: 中（コミュニティ議論）

### 5. Tech Crunch RSS

- **URL**: `https://techcrunch.com/feed/`
- **取得**: 最新10件
- **重み**: 中（業界ニュース）

## 記事生成プロセス

### ステップ1: 情報収集（5-10分）

```python
sources = [
    HackerNewsSource(),
    DevToSource(),
    GitHubTrendingSource(),
    RedditSource(),
    TechCrunchSource()
]
raw_data = aggregate_sources(sources)
```

### ステップ2: トレンド分析（2-3分）

```python
# クロスリファレンス分析
trends = analyze_trends(raw_data)
# スコアリング（複数ソースでの出現頻度）
scored_trends = score_trends(trends)
# トップ5選出
top_trends = select_top_trends(scored_trends, limit=5)
```

### ステップ3: 記事生成（5-10分/記事）

```python
for trend in top_trends:
    article = generate_article(
        trend=trend,
        template="comprehensive",  # 包括的テンプレート
        target_length=2000,        # 目標文字数
        seo_optimize=True          # SEO最適化
    )
    save_article(article)
```

### ステップ4: 品質チェック（1-2分）

```python
quality_score = evaluate_quality(article)
if quality_score < 80:
    regenerate_or_skip(article)
```

## 記事構造（3層価値提供）

### レイヤー1: 概要（初見ユーザー向け）

```markdown
# {技術名}が注目を集めている理由

## 一言で言うと

{技術の簡潔な説明}

## なぜ今重要なのか

{トレンドになっている背景}

## 主要な特徴

- 特徴1
- 特徴2
- 特徴3
```

### レイヤー2: 詳細解説（振り返りユーザー向け）

````markdown
## 技術的詳細

### アーキテクチャ

{技術的な仕組み}

### 実装例

```python
{実際のコード例}
```
````

### ユースケース

1. ケース1: {具体例}
2. ケース2: {具体例}

### ベストプラクティス

- プラクティス1
- プラクティス2

````

### レイヤー3: リファレンス（検索AI向け）
```markdown
## FAQ

**Q: {よくある質問1}**
A: {明確な回答}

**Q: {よくある質問2}**
A: {明確な回答}

## 関連技術
- 技術A: {関係性の説明}
- 技術B: {関係性の説明}

## 学習リソース
- [公式ドキュメント]({URL})
- [チュートリアル]({URL})
- [コミュニティ]({URL})

## 参考文献
1. {ソース1}
2. {ソース2}
````

## SEO 最適化

### メタデータ

```json
{
  "title": "{技術名}とは？2024年に注目される理由を解説",
  "description": "{技術の簡潔な説明}。特徴、使い方、実装例を詳しく解説します。",
  "keywords": ["{技術名}", "{関連語1}", "{関連語2}"],
  "author": "AICA-SyS",
  "published_date": "2024-10-11",
  "modified_date": "2024-10-11"
}
```

### 構造化データ（Schema.org）

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{タイトル}",
  "description": "{説明}",
  "author": {
    "@type": "Organization",
    "name": "AICA-SyS"
  },
  "datePublished": "2024-10-11",
  "dateModified": "2024-10-11"
}
```

## 品質スコアリング

### 評価項目

```python
quality_metrics = {
    "readability": 0.3,      # 読みやすさ（30%）
    "technical_depth": 0.25,  # 技術的深度（25%）
    "uniqueness": 0.2,        # ユニーク性（20%）
    "seo_score": 0.15,        # SEO（15%）
    "structure": 0.1          # 構造（10%）
}
```

### 合格基準

- **最低スコア**: 80点
- **理想スコア**: 90点以上

## コスト見積もり

### OpenAI API

- **モデル**: GPT-4-turbo
- **1記事**: 約3,000 tokens（入力）+ 2,000 tokens（出力）
- **コスト**: $0.006/記事
- **1日5記事**: $0.03/日
- **月間（平日22日）**: $0.66

### GitHub Actions

- **1実行時間**: 約10分
- **月間実行**: 22回
- **総時間**: 220分
- **コスト**: 無料枠内

## ワークフロー設定

### 実行スケジュール

```yaml
schedule:
  - cron: "0 0 * * 1-5" # 平日午前9時（JST = UTC 0:00）
```

### 環境変数

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## エラーハンドリング

### リトライロジック

```python
@retry(max_attempts=3, backoff=exponential)
def generate_article(trend):
    try:
        return call_openai_api(trend)
    except RateLimitError:
        wait_and_retry()
    except APIError:
        use_fallback_source()
```

### フェイルセーフ

- API失敗時: 次のトレンドにスキップ
- 全失敗時: 通知送信、手動確認

## モニタリング

### 成功メトリクス

- ✅ 生成成功率 > 95%
- ✅ 平均品質スコア > 85
- ✅ 実行時間 < 30分
- ✅ コスト < $1/日

### アラート条件

- ❌ 3記事連続失敗
- ❌ 品質スコア < 70
- ❌ 実行時間 > 45分
- ❌ API エラー率 > 10%

## 期待される効果

### 短期（1ヶ月）

- 毎日3-5記事の自動生成
- 月間60-100記事の蓄積
- SEO順位の向上開始

### 中期（3ヶ月）

- 200-300記事のコンテンツライブラリ
- オーガニック検索流入の増加
- ドメインオーソリティの向上

### 長期（6ヶ月）

- 500+記事の充実したコンテンツ
- 検索AI（Gemini等）での引用開始
- 業界での認知度向上
