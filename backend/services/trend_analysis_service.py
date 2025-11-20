"""
Trend Analysis Service for AICA-SyS
Phase 10-2: Trend analysis workflow
"""

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

from models.automated_content import SourceDataDB, TrendDataDB
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """トレンド分析サービス"""

    def __init__(self, db: Session):
        self.db = db

    async def analyze_daily_trends(self) -> Dict[str, Any]:
        """デイリートレンドを分析"""
        # 過去24時間のソースデータ取得
        yesterday = datetime.utcnow() - timedelta(days=1)
        try:
            source_data = (
                self.db.query(SourceDataDB)
                .filter(SourceDataDB.collected_at >= yesterday)
                .all()
            )
        except (ProgrammingError, OperationalError, SQLAlchemyError) as exc:
            logger.error(
                "source_data table is unavailable. Ensure database migrations ran: %s",
                exc,
            )
            raise RuntimeError(
                "Source data table missing. Run database migrations."
            ) from exc

        if not source_data:
            logger.warning("No source data found for trend analysis")
            return {}

        # キーワード分析
        keywords_analysis = self._analyze_keywords(source_data)

        # カテゴリ分析
        category_analysis = self._analyze_categories(source_data)

        # 上昇トレンド検出
        rising_trends = await self._detect_rising_trends(keywords_analysis)

        # トレンドデータ保存
        for keyword, data in keywords_analysis[:10]:
            await self._save_trend_data(
                trend_name=keyword,
                trend_score=data["score"],
                source_count=data["count"],
                keywords=data.get("related_keywords", []),
                related_topics=data.get("related_topics", []),
            )

        return {
            "date": datetime.utcnow().isoformat(),
            "top_trends": keywords_analysis[:10],
            "rising_trends": rising_trends,
            "categories": category_analysis,
            "total_sources": len(source_data),
        }

    def _analyze_keywords(
        self, source_data: List[SourceDataDB]
    ) -> List[tuple[str, Dict[str, Any]]]:
        """キーワード分析"""
        keywords = []
        keyword_sources = defaultdict(set)

        for item in source_data:
            title = item.title.lower()
            words = title.split()

            for word in words:
                if len(word) > 3:
                    keywords.append(word)
                    keyword_sources[word].add(item.source_type)

        # 頻度カウント
        keyword_freq = Counter(keywords)

        # スコアリング（頻度 × ソース数）
        scored_keywords = []
        for keyword, count in keyword_freq.most_common(50):
            source_count = len(keyword_sources[keyword])
            score = count * source_count * 10

            scored_keywords.append(
                (
                    keyword,
                    {
                        "score": score,
                        "count": count,
                        "sources": list(keyword_sources[keyword]),
                        "related_keywords": [],
                        "related_topics": [],
                    },
                )
            )

        scored_keywords.sort(key=lambda x: x[1]["score"], reverse=True)
        return scored_keywords

    def _analyze_categories(self, source_data: List[SourceDataDB]) -> Dict[str, int]:
        """カテゴリ分析"""
        categories = defaultdict(int)

        # 簡易カテゴリ分類
        category_keywords = {
            "AI": ["ai", "ml", "machine", "learning", "gpt", "llm", "neural"],
            "Web": ["web", "frontend", "react", "vue", "next", "svelte"],
            "Mobile": ["mobile", "ios", "android", "flutter", "react-native"],
            "DevOps": ["devops", "docker", "kubernetes", "ci", "cd", "deploy"],
            "Database": ["database", "sql", "nosql", "postgres", "mongo"],
            "Security": ["security", "auth", "encrypt", "vulnerability"],
        }

        for item in source_data:
            title_lower = item.title.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    categories[category] += 1

        return dict(categories)

    async def _detect_rising_trends(
        self, current_keywords: List[tuple[str, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """上昇トレンド検出"""
        rising = []

        # 7日前のデータと比較
        week_ago = datetime.utcnow() - timedelta(days=7)

        for keyword, data in current_keywords[:20]:
            # 過去のトレンドデータ取得
            past_trend = (
                self.db.query(TrendDataDB)
                .filter(
                    TrendDataDB.trend_name == keyword,
                    TrendDataDB.detected_at >= week_ago,
                )
                .first()
            )

            if past_trend:
                # 成長率計算
                if past_trend.trend_score > 0:
                    growth_rate = (
                        (data["score"] - past_trend.trend_score)
                        / past_trend.trend_score
                        * 100
                    )
                    if growth_rate > 50:  # 50%以上上昇
                        rising.append(
                            {
                                "keyword": keyword,
                                "score": data["score"],
                                "growth_rate": f"+{growth_rate:.1f}%",
                                "is_new": False,
                            }
                        )
            else:
                # 新規トレンド
                if data["score"] > 30:
                    rising.append(
                        {
                            "keyword": keyword,
                            "score": data["score"],
                            "growth_rate": "NEW",
                            "is_new": True,
                        }
                    )

        rising.sort(key=lambda x: x["score"], reverse=True)
        return rising[:10]

    async def _save_trend_data(
        self,
        trend_name: str,
        trend_score: float,
        source_count: int,
        keywords: List[str],
        related_topics: List[str],
    ):
        """トレンドデータを保存"""
        trend = TrendDataDB(
            trend_name=trend_name,
            trend_score=trend_score,
            source_count=source_count,
            keywords=keywords,
            related_topics=related_topics,
            data_snapshot={},
        )
        try:
            self.db.add(trend)
            self.db.commit()
        except (ProgrammingError, OperationalError, SQLAlchemyError) as exc:
            self.db.rollback()
            logger.error("Failed to persist trend data. Ensure migrations ran: %s", exc)
            raise
