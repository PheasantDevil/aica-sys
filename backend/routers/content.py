"""
Content API router for AICA-SyS
"""

from typing import List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models.collection import AnalysisResult
from models.content import Article, Newsletter, Trend
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/articles")
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_premium: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of articles"""
    query = db.query(Article)
    
    if is_premium is not None:
        query = query.filter(Article.is_premium == is_premium)
    
    articles = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "articles": articles,
        "total": total,
        "skip": skip,
        "limit": limit
    }


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
    db: Session = Depends(get_db)
):
    """Get list of newsletters"""
    newsletters = db.query(Newsletter).offset(skip).limit(limit).all()
    total = db.query(Newsletter).count()
    
    return {
        "newsletters": newsletters,
        "total": total,
        "skip": skip,
        "limit": limit
    }


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
    db: Session = Depends(get_db)
):
    """Get list of trends"""
    query = db.query(Trend)
    
    if category:
        query = query.filter(Trend.category == category)
    
    if impact:
        query = query.filter(Trend.impact == impact)
    
    trends = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "trends": trends,
        "total": total,
        "skip": skip,
        "limit": limit
    }


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
    db: Session = Depends(get_db)
):
    """Search content"""
    results = {"articles": [], "newsletters": [], "trends": []}
    
    if not content_type or content_type == "articles":
        articles = db.query(Article).filter(
            Article.title.contains(q) | Article.content.contains(q)
        ).offset(skip).limit(limit).all()
        results["articles"] = articles
    
    if not content_type or content_type == "newsletters":
        newsletters = db.query(Newsletter).filter(
            Newsletter.title.contains(q) | Newsletter.content.contains(q)
        ).offset(skip).limit(limit).all()
        results["newsletters"] = newsletters
    
    if not content_type or content_type == "trends":
        trends = db.query(Trend).filter(
            Trend.title.contains(q) | Trend.description.contains(q)
        ).offset(skip).limit(limit).all()
        results["trends"] = trends
    
    return results
