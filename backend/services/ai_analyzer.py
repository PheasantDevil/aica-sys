"""
AI分析エンジン
収集したデータを分析し、重要度スコアリング、カテゴリ分類、トレンド分析を実行
"""

import asyncio

# from sentence_transformers import SentenceTransformer
# import numpy as np
import json
import logging
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from groq import Groq

from .data_collector import ContentItem

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """分析結果"""

    content_id: str
    importance_score: float
    category: str
    subcategory: str
    trend_score: float
    sentiment: str
    key_topics: List[str]
    summary: str
    recommendations: List[str]
    created_at: datetime


class AIAnalyzer:
    """AI分析エンジンのメインクラス"""

    def __init__(self, groq_api_key: str = None):
        # API設定
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        # Groq client初期化
        if self.groq_api_key:
            try:
                # Groq client initialization - only pass api_key to avoid proxies error
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception:
                logger.exception("Failed to initialize Groq client")
                self.groq_client = None
        else:
            self.groq_client = None

        # モデル初期化（簡略化）
        # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        # self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

        # カテゴリ定義
        self.categories = {
            "framework": ["react", "vue", "angular", "svelte", "nextjs", "nuxt"],
            "language": ["typescript", "javascript", "node", "deno", "bun"],
            "tooling": ["webpack", "vite", "esbuild", "jest", "vitest", "cypress"],
            "database": ["prisma", "mongodb", "postgresql", "mysql"],
            "api": ["graphql", "trpc", "rest", "apollo", "relay"],
            "styling": ["tailwind", "css", "sass", "styled-components"],
            "deployment": ["vercel", "netlify", "aws", "docker", "kubernetes"],
            "testing": ["jest", "vitest", "cypress", "playwright", "testing-library"],
            "security": ["auth", "jwt", "oauth", "security", "vulnerability"],
            "performance": ["performance", "optimization", "bundle", "lighthouse"],
        }

        # 重要度の重み付け
        self.importance_weights = {
            "github_star_count": 0.3,
            "recent_activity": 0.25,
            "keyword_density": 0.2,
            "source_authority": 0.15,
            "engagement_metrics": 0.1,
        }

    async def analyze_content(self, items: List[ContentItem]) -> List[AnalysisResult]:
        """コンテンツを分析"""
        logger.info(f"{len(items)} 件のコンテンツを分析開始...")

        results = []

        # バッチ処理で分析を実行
        batch_size = 10
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batch_results = await self._analyze_batch(batch)
            results.extend(batch_results)

            # API制限を考慮して少し待機
            await asyncio.sleep(1)

        logger.info(f"分析完了: {len(results)} 件の結果を生成")
        return results

    async def _analyze_batch(self, items: List[ContentItem]) -> List[AnalysisResult]:
        """バッチでコンテンツを分析"""
        results = []

        for item in items:
            try:
                # 重要度スコアを計算
                importance_score = await self._calculate_importance_score(item)

                # カテゴリ分類
                category, subcategory = await self._classify_content(item)

                # トレンドスコアを計算
                trend_score = await self._calculate_trend_score(item)

                # センチメント分析
                sentiment = await self._analyze_sentiment(item)

                # キートピック抽出
                key_topics = await self._extract_key_topics(item)

                # 要約生成
                summary = await self._generate_summary(item)

                # 推奨事項生成
                recommendations = await self._generate_recommendations(item, category)

                result = AnalysisResult(
                    content_id=f"{item.source}_{hash(item.url)}",
                    importance_score=importance_score,
                    category=category,
                    subcategory=subcategory,
                    trend_score=trend_score,
                    sentiment=sentiment,
                    key_topics=key_topics,
                    summary=summary,
                    recommendations=recommendations,
                    created_at=datetime.now(),
                )

                results.append(result)

            except Exception as e:
                logger.error(f"コンテンツ分析エラー {item.url}: {e}")
                continue

        return results

    async def _calculate_importance_score(self, item: ContentItem) -> float:
        """重要度スコアを計算"""
        score = 0.0

        # 1. GitHub スター数（GitHubソースの場合）
        if "github" in item.source.lower():
            try:
                # GitHub APIからスター数を取得（実装は簡略化）
                score += 0.3 * min(1.0, len(item.tags) / 10)  # タグ数で代用
            except:
                pass

        # 2. 最近の活動度
        days_old = (datetime.now() - item.published_at).days
        recency_score = max(0, 1 - (days_old / 30))  # 30日で線形減少
        score += self.importance_weights["recent_activity"] * recency_score

        # 3. キーワード密度
        text = f"{item.title} {item.content}".lower()
        keyword_count = sum(
            1 for keyword in self._get_all_keywords() if keyword in text
        )
        keyword_density = keyword_count / max(1, len(text.split()))
        score += self.importance_weights["keyword_density"] * min(
            1.0, keyword_density * 10
        )

        # 4. ソース権威性
        source_authority = self._get_source_authority(item.source)
        score += self.importance_weights["source_authority"] * source_authority

        # 5. エンゲージメント指標（簡略化）
        engagement_score = min(1.0, len(item.content) / 1000)  # コンテンツ長で代用
        score += self.importance_weights["engagement_metrics"] * engagement_score

        return min(1.0, score)  # 0-1の範囲に正規化

    async def _classify_content(self, item: ContentItem) -> Tuple[str, str]:
        """コンテンツをカテゴリ分類"""
        text = f"{item.title} {item.content}".lower()

        # 各カテゴリのスコアを計算
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            category_scores[category] = score

        # 最高スコアのカテゴリを選択
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category, self._get_subcategory(text, best_category)

        return "general", "other"

    def _get_subcategory(self, text: str, category: str) -> str:
        """サブカテゴリを取得"""
        subcategory_mapping = {
            "framework": {
                "react": "react",
                "vue": "vue",
                "angular": "angular",
                "svelte": "svelte",
            },
            "language": {
                "typescript": "typescript",
                "javascript": "javascript",
                "node": "nodejs",
            },
            "tooling": {"webpack": "bundler", "vite": "bundler", "jest": "testing"},
        }

        if category in subcategory_mapping:
            for keyword, subcat in subcategory_mapping[category].items():
                if keyword in text:
                    return subcat

        return "general"

    async def _calculate_trend_score(self, item: ContentItem) -> float:
        """トレンドスコアを計算"""
        # 時間的トレンド（最近の方が高いスコア）
        days_old = (datetime.now() - item.published_at).days
        time_trend = max(0, 1 - (days_old / 7))  # 7日で線形減少

        # キーワードの流行度（簡略化）
        text = f"{item.title} {item.content}".lower()
        trending_keywords = [
            "new",
            "latest",
            "update",
            "release",
            "v2",
            "v3",
            "beta",
            "alpha",
        ]
        trend_keyword_score = sum(
            1 for keyword in trending_keywords if keyword in text
        ) / len(trending_keywords)

        # 重要度との組み合わせ
        importance_weight = 0.7
        keyword_weight = 0.3

        return (importance_weight * time_trend) + (keyword_weight * trend_keyword_score)

    async def _analyze_sentiment(self, item: ContentItem) -> str:
        """センチメント分析"""
        text = f"{item.title} {item.content}"

        # 簡易的なセンチメント分析
        positive_words = [
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "best",
            "awesome",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "worst",
            "problem",
            "issue",
            "bug",
            "error",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    async def _extract_key_topics(self, item: ContentItem) -> List[str]:
        """キートピックを抽出"""
        text = f"{item.title} {item.content}"

        # 既存のタグを使用
        topics = item.tags.copy()

        # 追加のキーワード抽出
        all_keywords = self._get_all_keywords()
        text_lower = text.lower()

        for keyword in all_keywords:
            if keyword in text_lower and keyword not in topics:
                topics.append(keyword)

        # 上位10個に制限
        return topics[:10]

    async def _generate_summary(self, item: ContentItem) -> str:
        """要約を生成"""
        if not item.summary:
            # 既存の要約がない場合は簡易生成
            text = f"{item.title} {item.content}"
            return text[:200] + "..." if len(text) > 200 else text

        return item.summary

    async def _generate_recommendations(
        self, item: ContentItem, category: str
    ) -> List[str]:
        """推奨事項を生成"""
        recommendations = []

        # カテゴリ別の推奨事項
        category_recommendations = {
            "framework": [
                "最新のベストプラクティスを確認",
                "パフォーマンス最適化を検討",
                "セキュリティアップデートを確認",
            ],
            "language": [
                "新しい言語機能を学習",
                "型安全性の向上を検討",
                "パフォーマンス改善を実装",
            ],
            "tooling": [
                "ツールの最新版にアップデート",
                "設定の最適化を検討",
                "代替ツールの評価",
            ],
        }

        if category in category_recommendations:
            recommendations.extend(category_recommendations[category][:2])

        # 汎用的な推奨事項
        recommendations.extend(
            ["関連するドキュメントを確認", "コミュニティの議論に参加"]
        )

        return recommendations[:3]  # 最大3件

    def _get_all_keywords(self) -> List[str]:
        """全キーワードを取得"""
        keywords = []
        for category_keywords in self.categories.values():
            keywords.extend(category_keywords)
        return keywords

    def _get_source_authority(self, source: str) -> float:
        """ソースの権威性スコアを取得"""
        authority_scores = {
            "github": 0.9,
            "dev.to": 0.8,
            "medium": 0.7,
            "reddit": 0.6,
            "blog": 0.5,
            "rss": 0.4,
        }

        source_lower = source.lower()
        for key, score in authority_scores.items():
            if key in source_lower:
                return score

        return 0.3  # デフォルトスコア

    async def analyze_trends(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """トレンド分析を実行"""
        logger.info("トレンド分析を開始...")

        # カテゴリ別の統計
        category_counts = Counter(result.category for result in results)
        sentiment_counts = Counter(result.sentiment for result in results)

        # 重要度の高いコンテンツ
        high_importance = [r for r in results if r.importance_score > 0.7]

        # トレンドスコアの高いコンテンツ
        trending = [r for r in results if r.trend_score > 0.6]

        # キートピックの頻度
        all_topics = []
        for result in results:
            all_topics.extend(result.key_topics)
        topic_counts = Counter(all_topics)

        trend_analysis = {
            "total_content": len(results),
            "high_importance_count": len(high_importance),
            "trending_count": len(trending),
            "category_distribution": dict(category_counts),
            "sentiment_distribution": dict(sentiment_counts),
            "top_topics": dict(topic_counts.most_common(10)),
            "trending_content": [
                {
                    "content_id": r.content_id,
                    "title": r.key_topics[0] if r.key_topics else "Unknown",
                    "trend_score": r.trend_score,
                    "category": r.category,
                }
                for r in trending[:5]
            ],
        }

        logger.info("トレンド分析完了")
        return trend_analysis


# 使用例
async def main():
    """分析エンジンの実行例"""
    openai_api_key = "your_openai_api_key"
    google_ai_api_key = "your_google_ai_api_key"

    analyzer = AIAnalyzer(openai_api_key, google_ai_api_key)

    # サンプルデータ
    sample_items = [
        ContentItem(
            title="TypeScript 5.0 Released",
            url="https://example.com/typescript-5",
            content="TypeScript 5.0 brings new features...",
            source="GitHub: microsoft/TypeScript",
            published_at=datetime.now(),
            tags=["typescript", "release", "javascript"],
        )
    ]

    results = await analyzer.analyze_content(sample_items)
    trends = await analyzer.analyze_trends(results)

    print(f"分析結果: {len(results)} 件")
    print(f"トレンド分析: {trends}")


if __name__ == "__main__":
    asyncio.run(main())
