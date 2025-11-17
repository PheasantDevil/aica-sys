"""
Content Recommendation Service for AICA-SyS
Phase 9-1: Content quality improvement
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class ContentRecommendationService:
    """コンテンツ推薦サービス"""

    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.content_vectors = {}

    async def recommend_for_user(
        self, user_id: str, limit: int = 10, exclude_viewed: bool = True
    ) -> List[Dict[str, Any]]:
        """ユーザーに基づいたコンテンツ推薦"""

        # ユーザーの閲覧履歴を取得
        user_history = self._get_user_history(user_id)

        # ユーザーの興味プロフィールを作成
        user_profile = self._build_user_profile(user_history)

        # コンテンツをスコアリング
        recommendations = []

        # ここで実際のコンテンツデータを取得する実装を追加
        # 現在は例として返す

        return recommendations[:limit]

    async def recommend_similar_content(
        self, content_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """類似コンテンツの推薦"""

        # コンテンツのベクトル表現を取得
        content_vector = self._get_content_vector(content_id)

        # 類似度計算
        similar_contents = self._calculate_similarity(content_vector, limit)

        return similar_contents

    async def recommend_trending(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """トレンドコンテンツの推薦"""

        # 最近24時間のアクセス数を集計
        trending_scores = self._calculate_trending_scores(category)

        # スコアでソート
        trending_contents = sorted(
            trending_scores, key=lambda x: x["score"], reverse=True
        )

        return trending_contents[:limit]

    async def recommend_personalized(
        self, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """パーソナライズド推薦（ハイブリッド）"""

        # ユーザーベース推薦
        user_based = await self.recommend_for_user(user_id, limit=5)

        # トレンド推薦
        trending = await self.recommend_trending(limit=5)

        # ハイブリッド（70%ユーザーベース、30%トレンド）
        recommendations = []

        # ユーザーベースから70%
        recommendations.extend(user_based[: int(limit * 0.7)])

        # トレンドから30%
        recommendations.extend(trending[: int(limit * 0.3)])

        # 重複削除
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec.get("id") not in seen:
                seen.add(rec.get("id"))
                unique_recommendations.append(rec)

        return unique_recommendations[:limit]

    def record_interaction(
        self,
        user_id: str,
        content_id: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """ユーザーのコンテンツインタラクションを記録"""

        interaction = {
            "content_id": content_id,
            "type": interaction_type,  # view, like, share, bookmark
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {},
        }

        self.user_interactions[user_id].append(interaction)

        logger.info(
            f"Recorded interaction: {user_id} - {interaction_type} - {content_id}"
        )

    def _get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーの閲覧履歴を取得"""
        return self.user_interactions.get(user_id, [])

    def _build_user_profile(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ユーザープロフィールを構築"""

        # カテゴリ別の興味度
        category_scores = defaultdict(float)

        # タグ別の興味度
        tag_scores = defaultdict(float)

        # 最近30日の履歴のみ使用
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        recent_history = [h for h in history if h["timestamp"] > recent_cutoff]

        # インタラクションタイプ別の重み
        weights = {"view": 1.0, "like": 3.0, "share": 5.0, "bookmark": 4.0}

        for interaction in recent_history:
            interaction_type = interaction.get("type", "view")
            weight = weights.get(interaction_type, 1.0)

            # メタデータからカテゴリとタグを取得
            metadata = interaction.get("metadata", {})
            category = metadata.get("category")
            tags = metadata.get("tags", [])

            if category:
                category_scores[category] += weight

            for tag in tags:
                tag_scores[tag] += weight

        return {
            "categories": dict(category_scores),
            "tags": dict(tag_scores),
            "interaction_count": len(recent_history),
            "last_interaction": (
                recent_history[-1]["timestamp"] if recent_history else None
            ),
        }

    def _get_content_vector(self, content_id: str) -> Dict[str, float]:
        """コンテンツのベクトル表現を取得"""
        # 実装では実際のコンテンツからベクトルを生成
        return self.content_vectors.get(content_id, {})

    def _calculate_similarity(
        self, vector: Dict[str, float], limit: int
    ) -> List[Dict[str, Any]]:
        """コサイン類似度で類似コンテンツを計算"""

        similarities = []

        for content_id, content_vector in self.content_vectors.items():
            similarity = self._cosine_similarity(vector, content_vector)
            similarities.append({"content_id": content_id, "similarity": similarity})

        # 類似度でソート
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        return similarities[:limit]

    def _cosine_similarity(
        self, vec1: Dict[str, float], vec2: Dict[str, float]
    ) -> float:
        """コサイン類似度を計算"""

        # 共通のキー
        common_keys = set(vec1.keys()) & set(vec2.keys())

        if not common_keys:
            return 0.0

        # 内積
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)

        # ノルム
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _calculate_trending_scores(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """トレンドスコアを計算"""

        # 最近24時間のインタラクションを集計
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)

        content_scores = defaultdict(float)

        for user_id, interactions in self.user_interactions.items():
            for interaction in interactions:
                if interaction["timestamp"] > recent_cutoff:
                    content_id = interaction["content_id"]
                    interaction_type = interaction["type"]

                    # スコア加算
                    if interaction_type == "view":
                        content_scores[content_id] += 1
                    elif interaction_type == "like":
                        content_scores[content_id] += 3
                    elif interaction_type == "share":
                        content_scores[content_id] += 5

        # スコアでソート
        trending = [
            {"content_id": cid, "score": score} for cid, score in content_scores.items()
        ]

        return trending

    def _evaluate_length(self, content: str) -> float:
        """長さを評価（0-100）"""
        word_count = len(content.split())

        if word_count < self.min_word_count:
            return (word_count / self.min_word_count) * 100
        elif word_count > self.max_word_count:
            return max(0, 100 - ((word_count - self.max_word_count) / 100))
        else:
            return 100

    def _get_quality_level(self, score: float) -> str:
        """スコアから品質レベルを取得"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        else:
            return "needs_improvement"

    def _generate_suggestions(
        self,
        readability: float,
        structure: float,
        length: float,
        title: float,
        technical: float,
    ) -> List[str]:
        """改善提案を生成"""
        suggestions = []

        if readability < 70:
            suggestions.append("文章をもっと短く、読みやすくしましょう")

        if structure < 70:
            suggestions.append("見出しやリストで構造化しましょう")

        if length < 70:
            suggestions.append("コンテンツの長さを調整しましょう")

        if title < 70:
            suggestions.append("タイトルをより魅力的にしましょう")

        if technical < 70:
            suggestions.append("コードサンプルや技術情報を追加しましょう")

        return suggestions


# グローバルインスタンス
content_recommendation_service = ContentRecommendationService()


def get_recommendations(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """推薦コンテンツを取得"""
    import asyncio

    return asyncio.run(
        content_recommendation_service.recommend_personalized(user_id, limit)
    )
