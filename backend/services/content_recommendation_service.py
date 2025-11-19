"""
Content Recommendation Service for AICA-SyS
Phase 9-1: Content quality improvement
"""

import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from models.ai_models import UserInteraction
from models.automated_content import AutomatedContentDB
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ContentRecommendationService:
    """コンテンツ推薦サービス（改善版：データベース連携）"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.user_interactions = defaultdict(list)  # メモリキャッシュ（オプション）
        self.content_vectors = {}

    async def recommend_for_user(
        self, user_id: str, limit: int = 10, exclude_viewed: bool = True
    ) -> List[Dict[str, Any]]:
        """ユーザーに基づいたコンテンツ推薦（改善版：データベース連携）"""

        if not self.db:
            logger.warning("Database session not provided, returning empty recommendations")
            return []

        # ユーザーの閲覧履歴を取得
        user_history = self._get_user_history(user_id)

        # ユーザーの興味プロフィールを作成
        user_profile = self._build_user_profile(user_history)

        # 公開済みコンテンツを取得
        published_contents = (
            self.db.query(AutomatedContentDB)
            .filter(AutomatedContentDB.status == "published")
            .order_by(AutomatedContentDB.published_at.desc())
            .limit(100)  # 候補を100件に制限
            .all()
        )

        # 閲覧済みコンテンツIDを取得（除外用）
        viewed_content_ids = set()
        if exclude_viewed:
            viewed_content_ids = {
                h.get("content_id") for h in user_history if h.get("type") == "view"
            }

        # コンテンツをスコアリング
        scored_contents = []
        for content in published_contents:
            if exclude_viewed and content.id in viewed_content_ids:
                continue

            # スコア計算
            score = self._calculate_content_score(content, user_profile)
            scored_contents.append(
                {
                    "id": content.id,
                    "title": content.title,
                    "slug": content.slug,
                    "summary": content.summary,
                    "score": score,
                    "published_at": content.published_at.isoformat() if content.published_at else None,
                }
            )

        # スコアでソート
        scored_contents.sort(key=lambda x: x["score"], reverse=True)

        return scored_contents[:limit]

    async def recommend_similar_content(
        self, content_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """類似コンテンツの推薦（改善版：データベース連携）"""

        if not self.db:
            logger.warning("Database session not provided, returning empty recommendations")
            return []

        # 対象コンテンツを取得
        target_content = (
            self.db.query(AutomatedContentDB)
            .filter(AutomatedContentDB.id == int(content_id))
            .first()
        )

        if not target_content:
            logger.warning(f"Content {content_id} not found")
            return []

        # コンテンツのベクトル表現を取得
        target_vector = self._build_content_vector(target_content)

        # 公開済みコンテンツを取得（対象を除く）
        published_contents = (
            self.db.query(AutomatedContentDB)
            .filter(
                AutomatedContentDB.status == "published",
                AutomatedContentDB.id != int(content_id),
            )
            .limit(100)
            .all()
        )

        # 類似度計算
        similar_contents = []
        for content in published_contents:
            content_vector = self._build_content_vector(content)
            similarity = self._cosine_similarity(target_vector, content_vector)

            similar_contents.append(
                {
                    "id": content.id,
                    "title": content.title,
                    "slug": content.slug,
                    "summary": content.summary,
                    "similarity": similarity,
                    "published_at": content.published_at.isoformat() if content.published_at else None,
                }
            )

        # 類似度でソート
        similar_contents.sort(key=lambda x: x["similarity"], reverse=True)

        return similar_contents[:limit]

    async def recommend_trending(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """トレンドコンテンツの推薦（改善版：データベース連携）"""

        if not self.db:
            logger.warning("Database session not provided, returning empty recommendations")
            return []

        # 最近24時間のインタラクションを集計
        trending_scores = self._calculate_trending_scores(category)

        # コンテンツIDとスコアのマッピング
        content_scores = {item["content_id"]: item["score"] for item in trending_scores}

        # 公開済みコンテンツを取得
        query = self.db.query(AutomatedContentDB).filter(
            AutomatedContentDB.status == "published"
        )

        if category:
            # カテゴリフィルタ（メタデータから）
            query = query.filter(
                AutomatedContentDB.content_metadata["category"].astext == category
            )

        published_contents = query.order_by(
            AutomatedContentDB.published_at.desc()
        ).limit(100).all()

        # スコアとコンテンツ情報を結合
        trending_contents = []
        for content in published_contents:
            score = content_scores.get(content.id, 0.0)
            # インタラクションがない場合でも、公開日が新しいものにスコアを付与
            if score == 0.0 and content.published_at:
                days_old = (datetime.utcnow() - content.published_at).days
                score = max(0, 10 - days_old)  # 新しいコンテンツほど高スコア

            trending_contents.append(
                {
                    "id": content.id,
                    "title": content.title,
                    "slug": content.slug,
                    "summary": content.summary,
                    "score": score,
                    "published_at": content.published_at.isoformat() if content.published_at else None,
                }
            )

        # スコアでソート
        trending_contents.sort(key=lambda x: x["score"], reverse=True)

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
        session_id: Optional[str] = None,
    ):
        """ユーザーのコンテンツインタラクションを記録（改善版：データベース保存）"""

        # メモリキャッシュにも保存（高速アクセス用）
        interaction = {
            "content_id": content_id,
            "type": interaction_type,  # view, like, share, bookmark
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {},
        }
        self.user_interactions[user_id].append(interaction)

        # データベースに保存
        if self.db:
            try:
                db_interaction = UserInteraction(
                    user_id=int(user_id) if user_id.isdigit() else None,
                    session_id=session_id,
                    content_id=int(content_id),
                    interaction_type=interaction_type,
                    interaction_data=metadata or {},
                )
                self.db.add(db_interaction)
                self.db.commit()
                logger.info(
                    f"Recorded interaction to DB: {user_id} - {interaction_type} - {content_id}"
                )
            except Exception as e:
                logger.error(f"Failed to save interaction to DB: {e}")
                self.db.rollback()
        else:
            logger.info(
                f"Recorded interaction (memory only): {user_id} - {interaction_type} - {content_id}"
            )

    def _get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーの閲覧履歴を取得（改善版：データベースから取得）"""
        # メモリキャッシュから取得
        memory_history = self.user_interactions.get(user_id, [])

        # データベースから取得
        if self.db:
            try:
                db_interactions = (
                    self.db.query(UserInteraction)
                    .filter(
                        (UserInteraction.user_id == int(user_id))
                        if user_id.isdigit()
                        else (UserInteraction.session_id == user_id)
                    )
                    .order_by(UserInteraction.created_at.desc())
                    .limit(100)
                    .all()
                )

                db_history = [
                    {
                        "content_id": str(interaction.content_id),
                        "type": interaction.interaction_type,
                        "timestamp": interaction.created_at,
                        "metadata": interaction.interaction_data or {},
                    }
                    for interaction in db_interactions
                ]

                # メモリとDBの履歴をマージ（重複除去）
                all_history = memory_history + db_history
                seen = set()
                unique_history = []
                for h in all_history:
                    key = (h.get("content_id"), h.get("type"), h.get("timestamp"))
                    if key not in seen:
                        seen.add(key)
                        unique_history.append(h)

                return sorted(unique_history, key=lambda x: x.get("timestamp", datetime.min), reverse=True)
            except Exception as e:
                logger.error(f"Failed to get user history from DB: {e}")
                return memory_history

        return memory_history

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

    def _build_content_vector(self, content: AutomatedContentDB) -> Dict[str, float]:
        """コンテンツのベクトル表現を構築（タグ、カテゴリ、キーワードから）"""
        vector = {}

        # SEOデータからキーワードを取得
        if content.seo_data:
            keywords = content.seo_data.get("keywords", [])
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(",")]
            for keyword in keywords:
                vector[f"keyword:{keyword.lower()}"] = 1.0

        # メタデータからカテゴリとタグを取得
        if content.content_metadata:
            category = content.content_metadata.get("category")
            if category:
                vector[f"category:{category.lower()}"] = 2.0

            tags = content.content_metadata.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",")]
            for tag in tags:
                vector[f"tag:{tag.lower()}"] = 1.5

        # タイトルとサマリーから重要な単語を抽出
        title_words = content.title.lower().split() if content.title else []
        summary_words = content.summary.lower().split() if content.summary else []

        # 技術用語の重み付け
        tech_terms = [
            "typescript",
            "javascript",
            "react",
            "next.js",
            "node.js",
            "api",
            "framework",
            "library",
        ]
        for word in title_words + summary_words:
            if word in tech_terms:
                vector[f"term:{word}"] = vector.get(f"term:{word}", 0) + 1.0

        return vector

    def _calculate_content_score(
        self, content: AutomatedContentDB, user_profile: Dict[str, Any]
    ) -> float:
        """コンテンツのユーザー適合スコアを計算"""
        score = 0.0

        # コンテンツのベクトルを構築
        content_vector = self._build_content_vector(content)

        # ユーザープロフィールのカテゴリとタグとマッチング
        user_categories = user_profile.get("categories", {})
        user_tags = user_profile.get("tags", {})

        # カテゴリマッチング
        if content.content_metadata:
            content_category = content.content_metadata.get("category", "").lower()
            if content_category in user_categories:
                score += user_categories[content_category] * 10

        # タグマッチング
        if content.content_metadata:
            content_tags = content.content_metadata.get("tags", [])
            if isinstance(content_tags, str):
                content_tags = [t.strip().lower() for t in content_tags.split(",")]

            for tag in content_tags:
                if tag in user_tags:
                    score += user_tags[tag] * 5

        # 品質スコアを考慮
        if content.quality_score:
            score += content.quality_score * 0.1

        # 公開日の新しさを考慮（30日以内は加点）
        if content.published_at:
            days_old = (datetime.utcnow() - content.published_at).days
            if days_old <= 30:
                score += max(0, (30 - days_old) * 0.5)

        return score

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
        """トレンドスコアを計算（改善版：データベース連携）"""

        # 最近24時間のインタラクションを集計
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)

        content_scores = defaultdict(float)

        # メモリキャッシュから集計
        for user_id, interactions in self.user_interactions.items():
            for interaction in interactions:
                if interaction["timestamp"] > recent_cutoff:
                    content_id = interaction["content_id"]
                    interaction_type = interaction["type"]

                    # スコア加算
                    if interaction_type == "view":
                        content_scores[int(content_id)] += 1
                    elif interaction_type == "like":
                        content_scores[int(content_id)] += 3
                    elif interaction_type == "share":
                        content_scores[int(content_id)] += 5

        # データベースから集計
        if self.db:
            try:
                db_interactions = (
                    self.db.query(UserInteraction)
                    .filter(UserInteraction.created_at >= recent_cutoff)
                    .all()
                )

                for interaction in db_interactions:
                    content_id = interaction.content_id
                    interaction_type = interaction.interaction_type

                    # スコア加算
                    if interaction_type == "view":
                        content_scores[content_id] += 1
                    elif interaction_type == "like":
                        content_scores[content_id] += 3
                    elif interaction_type == "share":
                        content_scores[content_id] += 5
                    elif interaction_type == "bookmark":
                        content_scores[content_id] += 2

            except Exception as e:
                logger.error(f"Failed to calculate trending scores from DB: {e}")

        # スコアでソート
        trending = [
            {"content_id": cid, "score": score} for cid, score in content_scores.items()
        ]

        return trending

