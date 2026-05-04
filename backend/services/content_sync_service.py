"""
Synchronize automated_contents into core content tables.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.automated_content import AutomatedContentDB, ContentStatus, ContentType
from models.content import Article, Newsletter, Trend, TrendCategory, TrendImpact

logger = logging.getLogger(__name__)


class ContentSyncService:
    """Synchronize published automated content into articles/newsletters/trends."""

    def sync_published_content(
        self, db: Session, limit: Optional[int] = None
    ) -> Dict[str, int]:
        query = db.query(AutomatedContentDB).filter(
            AutomatedContentDB.status == ContentStatus.PUBLISHED.value
        )
        query = query.order_by(
            AutomatedContentDB.updated_at.asc(), AutomatedContentDB.id.asc()
        )

        if limit:
            query = query.limit(limit)

        rows = query.all()
        stats = {
            "scanned": len(rows),
            "article_upserts": 0,
            "newsletter_upserts": 0,
            "trend_upserts": 0,
            "skipped": 0,
        }

        for row in rows:
            if row.content_type == ContentType.ARTICLE.value:
                self._upsert_article(db, row)
                stats["article_upserts"] += 1
            elif row.content_type == ContentType.NEWSLETTER.value:
                self._upsert_newsletter(db, row)
                stats["newsletter_upserts"] += 1
            elif row.content_type == ContentType.TREND.value:
                self._upsert_trend(db, row)
                stats["trend_upserts"] += 1
            else:
                stats["skipped"] += 1

        if rows:
            db.commit()

        return stats

    def _upsert_article(self, db: Session, automated: AutomatedContentDB) -> None:
        article_id = self._stable_uuid(automated)
        article = db.query(Article).filter(Article.id == article_id).first()
        metadata = automated.content_metadata or {}

        if not article:
            article = Article(id=article_id, title="", content="", summary="")
            db.add(article)

        article.title = automated.title or "Untitled"
        article.content = automated.content or ""
        article.summary = automated.summary or (automated.content or "")[:240]
        article.tags = self._as_list(metadata.get("tags"))
        article.published_at = (
            automated.published_at or automated.created_at or datetime.utcnow()
        )
        article.author = str(metadata.get("author", "AICA-SyS"))
        article.read_time = self._as_int(metadata.get("read_time"), default=5)
        article.is_premium = self._as_bool(metadata.get("is_premium"), default=False)
        article.views = self._as_int(metadata.get("views"), default=0)
        article.likes = self._as_int(metadata.get("likes"), default=0)
        article.created_at = automated.created_at or datetime.utcnow()
        article.updated_at = automated.updated_at or datetime.utcnow()

    def _upsert_newsletter(self, db: Session, automated: AutomatedContentDB) -> None:
        newsletter_id = self._stable_uuid(automated)
        newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
        metadata = automated.content_metadata or {}

        if not newsletter:
            newsletter = Newsletter(id=newsletter_id, title="", content="")
            db.add(newsletter)

        newsletter.title = automated.title or "Untitled"
        newsletter.content = automated.content or ""
        newsletter.published_at = (
            automated.published_at or automated.created_at or datetime.utcnow()
        )
        newsletter.subscribers = self._as_int(metadata.get("subscribers"), default=0)
        newsletter.open_rate = self._as_int(metadata.get("open_rate"), default=0)
        newsletter.created_at = automated.created_at or datetime.utcnow()

    def _upsert_trend(self, db: Session, automated: AutomatedContentDB) -> None:
        trend_id = self._stable_uuid(automated)
        trend = db.query(Trend).filter(Trend.id == trend_id).first()
        metadata = automated.content_metadata or {}

        if not trend:
            trend = Trend(
                id=trend_id,
                title="",
                description="",
                category=TrendCategory.ECOSYSTEM.value,
                impact=TrendImpact.MEDIUM.value,
            )
            db.add(trend)

        trend.title = automated.title or "Untitled"
        trend.description = automated.summary or automated.content or ""
        trend.category = self._normalize_trend_category(
            metadata.get("category", TrendCategory.ECOSYSTEM.value)
        )
        trend.impact = self._normalize_trend_impact(
            metadata.get("impact", TrendImpact.MEDIUM.value)
        )
        trend.related_articles = self._as_list(metadata.get("related_articles"))
        trend.created_at = automated.created_at or datetime.utcnow()

    @staticmethod
    def _stable_uuid(automated: AutomatedContentDB) -> str:
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL, f"aica-sys:{automated.content_type}:{automated.id}"
            )
        )

    @staticmethod
    def _as_list(value: Any) -> list:
        if isinstance(value, list):
            return value
        return []

    @staticmethod
    def _as_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _as_bool(value: Any, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "on"}
        if isinstance(value, (int, float)):
            return bool(value)
        return default

    @staticmethod
    def _normalize_trend_category(value: Any) -> str:
        raw = str(value or "").lower()
        allowed = {item.value for item in TrendCategory}
        return raw if raw in allowed else TrendCategory.ECOSYSTEM.value

    @staticmethod
    def _normalize_trend_impact(value: Any) -> str:
        raw = str(value or "").lower()
        allowed = {item.value for item in TrendImpact}
        return raw if raw in allowed else TrendImpact.MEDIUM.value


_content_sync_service = ContentSyncService()


def get_content_sync_service() -> ContentSyncService:
    return _content_sync_service
