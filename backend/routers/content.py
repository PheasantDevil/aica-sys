"""
Content API router for AICA-SyS
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.automated_content import AutomatedContentDB, ContentStatus, ContentType
from models.collection import AnalysisResult
from models.content import Article, Newsletter, Trend
from services.content_sync_service import get_content_sync_service

router = APIRouter(prefix="/api/content", tags=["content"])
_last_sync_at: Optional[datetime] = None
_sync_interval = timedelta(minutes=5)
logger = logging.getLogger(__name__)


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _automated_to_article(content: AutomatedContentDB) -> dict:
    metadata = content.content_metadata or {}
    return {
        "id": str(content.id),
        "title": content.title or "",
        "description": content.summary or "",
        "summary": content.summary or "",
        "content": content.content or "",
        "author": {"name": metadata.get("author", "AICA-SyS")},
        "category": metadata.get("category", "general"),
        "tags": metadata.get("tags", []),
        "publishedAt": content.published_at or content.created_at,
        "published_at": content.published_at or content.created_at,
        "readTime": _to_int(metadata.get("read_time", 5), default=5),
        "read_time": _to_int(metadata.get("read_time", 5), default=5),
        "views": _to_int(metadata.get("views", 0)),
        "likes": _to_int(metadata.get("likes", 0)),
        "isPremium": bool(metadata.get("is_premium", False)),
        "is_premium": bool(metadata.get("is_premium", False)),
    }


def _automated_to_newsletter(content: AutomatedContentDB) -> dict:
    metadata = content.content_metadata or {}
    return {
        "id": str(content.id),
        "title": content.title or "",
        "description": content.summary or "",
        "content": content.content or "",
        "publishedAt": content.published_at or content.created_at,
        "published_at": content.published_at or content.created_at,
        "subscribers": _to_int(metadata.get("subscribers", 0)),
        "openRate": _to_float(metadata.get("open_rate", 0)),
        "open_rate": _to_float(metadata.get("open_rate", 0)),
        "clickRate": _to_float(metadata.get("click_rate", 0)),
        "click_rate": _to_float(metadata.get("click_rate", 0)),
        "isPremium": bool(metadata.get("is_premium", False)),
        "is_premium": bool(metadata.get("is_premium", False)),
        "tags": metadata.get("tags", []),
    }


def _automated_to_trend(content: AutomatedContentDB) -> dict:
    metadata = content.content_metadata or {}
    return {
        "id": str(content.id),
        "title": content.title or "",
        "description": content.summary or "",
        "category": metadata.get("category", "general"),
        "impact": metadata.get("impact", "medium"),
        "trendScore": _to_float(
            metadata.get("trend_score", content.quality_score or 0)
        ),
        "trend_score": _to_float(
            metadata.get("trend_score", content.quality_score or 0)
        ),
        "relatedArticles": metadata.get("related_articles", []),
        "related_articles": metadata.get("related_articles", []),
        "created_at": content.created_at,
    }


def _ensure_core_tables_synced(db: Session) -> None:
    global _last_sync_at
    now = datetime.utcnow()
    if _last_sync_at and now - _last_sync_at < _sync_interval:
        return

    try:
        sync_service = get_content_sync_service()
        stats = sync_service.sync_published_content(db)
        _last_sync_at = now

        if stats["scanned"] > 0:
            logger.info(
                f"[content-sync] scanned={stats['scanned']} "
                f"article={stats['article_upserts']} "
                f"newsletter={stats['newsletter_upserts']} "
                f"trend={stats['trend_upserts']}"
            )
    except Exception:
        # Synchronization failure must not block read API responses.
        logger.exception("Failed to synchronize automated content into core tables")


@router.get("/articles")
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_premium: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Get list of articles"""
    _ensure_core_tables_synced(db)
    query = db.query(Article)

    if is_premium is not None:
        query = query.filter(Article.is_premium == is_premium)

    articles = query.offset(skip).limit(limit).all()
    total = query.count()

    if total == 0:
        automated_query = db.query(AutomatedContentDB).filter(
            AutomatedContentDB.content_type == ContentType.ARTICLE.value,
            AutomatedContentDB.status == ContentStatus.PUBLISHED.value,
        )
        automated_total = automated_query.count()
        automated_articles = (
            automated_query.order_by(AutomatedContentDB.published_at.desc().nullslast())
            .offset(skip)
            .limit(limit)
            .all()
        )
        if automated_total > 0:
            return {
                "articles": [
                    _automated_to_article(item) for item in automated_articles
                ],
                "total": automated_total,
                "skip": skip,
                "limit": limit,
                "source": "automated_contents",
            }

    return {"articles": articles, "total": total, "skip": skip, "limit": limit}


@router.get("/articles/{article_id}")
async def get_article(article_id: str, db: Session = Depends(get_db)):
    """Get specific article by ID"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment view count
    article.views += 1
    db.commit()

    return article


@router.get("/newsletters")
async def get_newsletters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get list of newsletters"""
    _ensure_core_tables_synced(db)
    newsletters = db.query(Newsletter).offset(skip).limit(limit).all()
    total = db.query(Newsletter).count()

    if total == 0:
        automated_query = db.query(AutomatedContentDB).filter(
            AutomatedContentDB.content_type == ContentType.NEWSLETTER.value,
            AutomatedContentDB.status == ContentStatus.PUBLISHED.value,
        )
        automated_total = automated_query.count()
        automated_newsletters = (
            automated_query.order_by(AutomatedContentDB.published_at.desc().nullslast())
            .offset(skip)
            .limit(limit)
            .all()
        )
        if automated_total > 0:
            return {
                "newsletters": [
                    _automated_to_newsletter(item) for item in automated_newsletters
                ],
                "total": automated_total,
                "skip": skip,
                "limit": limit,
                "source": "automated_contents",
            }

    return {"newsletters": newsletters, "total": total, "skip": skip, "limit": limit}


@router.get("/newsletters/{newsletter_id}")
async def get_newsletter(newsletter_id: str, db: Session = Depends(get_db)):
    """Get specific newsletter by ID"""
    newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()

    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    return newsletter


@router.get("/trends")
async def get_trends(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    impact: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get list of trends"""
    _ensure_core_tables_synced(db)
    query = db.query(Trend)

    if category:
        query = query.filter(Trend.category == category)

    if impact:
        query = query.filter(Trend.impact == impact)

    trends = query.offset(skip).limit(limit).all()
    total = query.count()

    if total == 0:
        automated_query = db.query(AutomatedContentDB).filter(
            AutomatedContentDB.content_type == ContentType.TREND.value,
            AutomatedContentDB.status == ContentStatus.PUBLISHED.value,
        )
        automated_total = automated_query.count()
        automated_trends = (
            automated_query.order_by(AutomatedContentDB.published_at.desc().nullslast())
            .offset(skip)
            .limit(limit)
            .all()
        )
        if automated_total > 0:
            return {
                "trends": [_automated_to_trend(item) for item in automated_trends],
                "total": automated_total,
                "skip": skip,
                "limit": limit,
                "source": "automated_contents",
            }

    return {"trends": trends, "total": total, "skip": skip, "limit": limit}


@router.get("/trends/{trend_id}")
async def get_trend(trend_id: str, db: Session = Depends(get_db)):
    """Get specific trend by ID"""
    trend = db.query(Trend).filter(Trend.id == trend_id).first()

    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    return trend


@router.post("/articles/{article_id}/like")
async def like_article(article_id: str, db: Session = Depends(get_db)):
    """Like an article"""
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.likes += 1
    db.commit()

    return {"message": "Article liked", "likes": article.likes}


@router.get("/search")
async def search_content(
    q: str = Query(..., min_length=1),
    content_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search content"""
    results = {"articles": [], "newsletters": [], "trends": []}

    if not content_type or content_type == "articles":
        articles = (
            db.query(Article)
            .filter(Article.title.contains(q) | Article.content.contains(q))
            .offset(skip)
            .limit(limit)
            .all()
        )
        results["articles"] = articles

    if not content_type or content_type == "newsletters":
        newsletters = (
            db.query(Newsletter)
            .filter(Newsletter.title.contains(q) | Newsletter.content.contains(q))
            .offset(skip)
            .limit(limit)
            .all()
        )
        results["newsletters"] = newsletters

    if not content_type or content_type == "trends":
        trends = (
            db.query(Trend)
            .filter(Trend.title.contains(q) | Trend.description.contains(q))
            .offset(skip)
            .limit(limit)
            .all()
        )
        results["trends"] = trends

    return results
