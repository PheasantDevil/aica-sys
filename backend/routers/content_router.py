"""
コンテンツ関連のAPIエンドポイント
Phase 2: 自動生成コンテンツ配信
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.automated_content import AutomatedContentDB, ContentStatus, ContentType

router = APIRouter(prefix="/content", tags=["Content"])


class ArticleResponse(BaseModel):
    """記事レスポンスモデル"""
    id: int
    title: str
    slug: str
    summary: str
    content: str
    tags: Optional[List[str]] = []
    quality_score: float
    status: str
    read_time: int
    seo_data: Optional[dict] = {}
    metadata: Optional[dict] = {}
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """記事一覧レスポンスモデル"""
    articles: List[ArticleResponse]
    total: int
    page: int
    page_size: int


@router.get("/")
async def get_content():
    """コンテンツエンドポイント確認"""
    return {"message": "Content API ready", "status": "ok", "version": "2.0"}


@router.get("/articles", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="記事ステータス（published, draft, archived）"),
    min_quality: float = Query(0.0, ge=0.0, le=100.0, description="最小品質スコア"),
    db: Session = Depends(get_db)
):
    """自動生成記事一覧を取得"""
    
    # クエリ構築
    query = db.query(AutomatedContentDB).filter(
        AutomatedContentDB.content_type == ContentType.ARTICLE
    )
    
    # フィルタ適用
    if status:
        query = query.filter(AutomatedContentDB.status == status)
    if min_quality > 0:
        query = query.filter(AutomatedContentDB.quality_score >= min_quality)
    
    # 総数取得
    total = query.count()
    
    # ページネーション
    offset = (page - 1) * page_size
    articles = query.order_by(AutomatedContentDB.created_at.desc()).offset(offset).limit(page_size).all()
    
    # レスポンス変換
    article_responses = []
    for article in articles:
        article_responses.append(ArticleResponse(
            id=article.id,
            title=article.title,
            slug=article.slug,
            summary=article.summary or "",
            content=article.content or "",
            tags=article.metadata.get('tags', []) if article.metadata else [],
            quality_score=article.quality_score,
            status=article.status,
            read_time=article.metadata.get('read_time', 5) if article.metadata else 5,
            seo_data=article.seo_data or {},
            metadata=article.metadata or {},
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at
        ))
    
    return ArticleListResponse(
        articles=article_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """記事詳細を取得"""
    
    article = db.query(AutomatedContentDB).filter(
        AutomatedContentDB.id == article_id,
        AutomatedContentDB.content_type == ContentType.ARTICLE
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        slug=article.slug,
        summary=article.summary or "",
        content=article.content or "",
        tags=article.metadata.get('tags', []) if article.metadata else [],
        quality_score=article.quality_score,
        status=article.status,
        read_time=article.metadata.get('read_time', 5) if article.metadata else 5,
        seo_data=article.seo_data or {},
        metadata=article.metadata or {},
        published_at=article.published_at,
        created_at=article.created_at,
        updated_at=article.updated_at
    )
