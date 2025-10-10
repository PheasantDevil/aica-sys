"""
Query Optimizer Service for AICA-SyS
Phase 7-3: API response optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from models.content import Article, Newsletter, Trend
from models.subscription import Subscription
from models.user import User
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload
from utils.cache_decorators import cache_api_response, cache_result

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """データベースクエリ最適化サービス"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @cache_result(expire=300, key_prefix="articles_optimized")
    async def get_articles_optimized(
        self, 
        skip: int = 0, 
        limit: int = 10,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """記事を最適化されたクエリで取得"""
        try:
            # ベースクエリを作成
            query = select(Article).options(
                selectinload(Article.tags),
                selectinload(Article.author)
            )
            
            # フィルター条件を追加
            conditions = []
            
            if category:
                conditions.append(Article.category == category)
            
            if tags:
                # タグでのフィルタリング（IN句を使用）
                conditions.append(Article.tags.any(tag_name=tags[0]))
                for tag in tags[1:]:
                    conditions.append(Article.tags.any(tag_name=tag))
            
            if author_id:
                conditions.append(Article.author_id == author_id)
            
            if date_from:
                conditions.append(Article.created_at >= date_from)
            
            if date_to:
                conditions.append(Article.created_at <= date_to)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # 総数を取得（並列実行）
            count_query = select(func.count(Article.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            # 並列でクエリを実行
            articles_task = self.session.execute(
                query.offset(skip).limit(limit).order_by(Article.created_at.desc())
            )
            count_task = self.session.execute(count_query)
            
            articles_result, count_result = await asyncio.gather(
                articles_task, count_task
            )
            
            articles = articles_result.scalars().all()
            total = count_result.scalar()
            
            return {
                "articles": [self._serialize_article(article) for article in articles],
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total,
                "has_prev": skip > 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error in get_articles_optimized: {e}")
            raise
    
    @cache_result(expire=600, key_prefix="trends_optimized")
    async def get_trends_optimized(
        self,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """トレンドを最適化されたクエリで取得"""
        try:
            query = select(Trend).options(
                selectinload(Trend.tags)
            )
            
            conditions = []
            
            if category:
                conditions.append(Trend.category == category)
            
            if date_from:
                conditions.append(Trend.created_at >= date_from)
            
            if date_to:
                conditions.append(Trend.created_at <= date_to)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # 並列でクエリを実行
            trends_task = self.session.execute(
                query.offset(skip).limit(limit).order_by(Trend.trend_score.desc())
            )
            count_task = self.session.execute(
                select(func.count(Trend.id)).where(and_(*conditions) if conditions else True)
            )
            
            trends_result, count_result = await asyncio.gather(
                trends_task, count_task
            )
            
            trends = trends_result.scalars().all()
            total = count_result.scalar()
            
            return {
                "trends": [self._serialize_trend(trend) for trend in trends],
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total,
                "has_prev": skip > 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error in get_trends_optimized: {e}")
            raise
    
    @cache_result(expire=1800, key_prefix="newsletters_optimized")
    async def get_newsletters_optimized(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """ニュースレターを最適化されたクエリで取得"""
        try:
            query = select(Newsletter).options(
                selectinload(Newsletter.tags)
            )
            
            conditions = []
            
            if status:
                conditions.append(Newsletter.status == status)
            
            if date_from:
                conditions.append(Newsletter.created_at >= date_from)
            
            if date_to:
                conditions.append(Newsletter.created_at <= date_to)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # 並列でクエリを実行
            newsletters_task = self.session.execute(
                query.offset(skip).limit(limit).order_by(Newsletter.created_at.desc())
            )
            count_task = self.session.execute(
                select(func.count(Newsletter.id)).where(and_(*conditions) if conditions else True)
            )
            
            newsletters_result, count_result = await asyncio.gather(
                newsletters_task, count_task
            )
            
            newsletters = newsletters_result.scalars().all()
            total = count_result.scalar()
            
            return {
                "newsletters": [self._serialize_newsletter(newsletter) for newsletter in newsletters],
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total,
                "has_prev": skip > 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error in get_newsletters_optimized: {e}")
            raise
    
    async def get_dashboard_data_optimized(self) -> Dict[str, Any]:
        """ダッシュボードデータを並列で取得"""
        try:
            # 並列で複数のクエリを実行
            articles_task = self._get_recent_articles(5)
            trends_task = self._get_recent_trends(5)
            newsletters_task = self._get_recent_newsletters(5)
            stats_task = self._get_content_stats()
            
            articles, trends, newsletters, stats = await asyncio.gather(
                articles_task, trends_task, newsletters_task, stats_task
            )
            
            return {
                "recent_articles": articles,
                "recent_trends": trends,
                "recent_newsletters": newsletters,
                "stats": stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in get_dashboard_data_optimized: {e}")
            raise
    
    async def _get_recent_articles(self, limit: int) -> List[Dict[str, Any]]:
        """最近の記事を取得"""
        result = await self.session.execute(
            select(Article)
            .options(selectinload(Article.tags))
            .order_by(Article.created_at.desc())
            .limit(limit)
        )
        articles = result.scalars().all()
        return [self._serialize_article(article) for article in articles]
    
    async def _get_recent_trends(self, limit: int) -> List[Dict[str, Any]]:
        """最近のトレンドを取得"""
        result = await self.session.execute(
            select(Trend)
            .options(selectinload(Trend.tags))
            .order_by(Trend.created_at.desc())
            .limit(limit)
        )
        trends = result.scalars().all()
        return [self._serialize_trend(trend) for trend in trends]
    
    async def _get_recent_newsletters(self, limit: int) -> List[Dict[str, Any]]:
        """最近のニュースレターを取得"""
        result = await self.session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tags))
            .order_by(Newsletter.created_at.desc())
            .limit(limit)
        )
        newsletters = result.scalars().all()
        return [self._serialize_newsletter(newsletter) for newsletter in newsletters]
    
    async def _get_content_stats(self) -> Dict[str, Any]:
        """コンテンツ統計を取得"""
        try:
            # 並列で統計クエリを実行
            articles_count_task = self.session.execute(select(func.count(Article.id)))
            trends_count_task = self.session.execute(select(func.count(Trend.id)))
            newsletters_count_task = self.session.execute(select(func.count(Newsletter.id)))
            
            articles_count, trends_count, newsletters_count = await asyncio.gather(
                articles_count_task, trends_count_task, newsletters_count_task
            )
            
            return {
                "total_articles": articles_count.scalar(),
                "total_trends": trends_count.scalar(),
                "total_newsletters": newsletters_count.scalar(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in _get_content_stats: {e}")
            return {
                "total_articles": 0,
                "total_trends": 0,
                "total_newsletters": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def _serialize_article(self, article: Article) -> Dict[str, Any]:
        """記事をシリアライズ"""
        return {
            "id": str(article.id),
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "tags": [tag.name for tag in article.tags] if article.tags else [],
            "author": {
                "id": str(article.author.id),
                "name": article.author.name,
                "email": article.author.email
            } if article.author else None,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat() if article.updated_at else None,
            "status": article.status,
            "view_count": article.view_count,
            "like_count": article.like_count
        }
    
    def _serialize_trend(self, trend: Trend) -> Dict[str, Any]:
        """トレンドをシリアライズ"""
        return {
            "id": str(trend.id),
            "title": trend.title,
            "description": trend.description,
            "category": trend.category,
            "tags": [tag.name for tag in trend.tags] if trend.tags else [],
            "trend_score": trend.trend_score,
            "created_at": trend.created_at.isoformat(),
            "updated_at": trend.updated_at.isoformat() if trend.updated_at else None,
            "status": trend.status
        }
    
    def _serialize_newsletter(self, newsletter: Newsletter) -> Dict[str, Any]:
        """ニュースレターをシリアライズ"""
        return {
            "id": str(newsletter.id),
            "title": newsletter.title,
            "content": newsletter.content,
            "tags": [tag.name for tag in newsletter.tags] if newsletter.tags else [],
            "created_at": newsletter.created_at.isoformat(),
            "updated_at": newsletter.updated_at.isoformat() if newsletter.updated_at else None,
            "status": newsletter.status,
            "scheduled_at": newsletter.scheduled_at.isoformat() if newsletter.scheduled_at else None
        }

# クエリ最適化のユーティリティ関数
async def optimize_query_execution(queries: List[Any]) -> List[Any]:
    """複数のクエリを並列実行して最適化"""
    try:
        results = await asyncio.gather(*queries, return_exceptions=True)
        
        # エラーが発生したクエリをチェック
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query {i} failed: {result}")
                results[i] = None
        
        return results
    except Exception as e:
        logger.error(f"Error in optimize_query_execution: {e}")
        raise

def create_optimized_pagination(
    items: List[Any], 
    total: int, 
    skip: int, 
    limit: int
) -> Dict[str, Any]:
    """最適化されたページネーション情報を作成"""
    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit,
        "total_pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
        "next_page": (skip // limit) + 2 if skip + limit < total else None,
        "prev_page": skip // limit if skip > 0 else None
    }
