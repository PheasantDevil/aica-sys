"""
Optimized Content Router for AICA-SyS
Phase 7-3: API response optimization
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from middleware.performance_middleware import performance_metrics
from services.query_optimizer import QueryOptimizer
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response_optimizer import (create_conditional_response, create_error_response,
                                      create_etag, create_paginated_response,
                                      create_success_response, optimize_data)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/optimized", tags=["optimized-content"])


@router.get("/articles")
async def get_articles_optimized(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    author_id: Optional[str] = Query(None, description="Filter by author ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
):
    """最適化された記事取得エンドポイント"""
    try:
        # タグのパース
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        # クエリ最適化サービスを使用
        query_optimizer = QueryOptimizer(db)
        result = await query_optimizer.get_articles_optimized(
            skip=skip,
            limit=limit,
            category=category,
            tags=tag_list,
            author_id=author_id,
            date_from=date_from,
            date_to=date_to,
        )

        # データを最適化
        optimized_data = optimize_data(result)

        # ETagを生成
        etag = create_etag(optimized_data)

        # 条件付きレスポンスを作成
        return create_conditional_response(
            data=optimized_data,
            etag=etag,
            request=request,
            message="Articles retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error in get_articles_optimized: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends")
async def get_trends_optimized(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
):
    """最適化されたトレンド取得エンドポイント"""
    try:
        query_optimizer = QueryOptimizer(db)
        result = await query_optimizer.get_trends_optimized(
            skip=skip,
            limit=limit,
            category=category,
            date_from=date_from,
            date_to=date_to,
        )

        # データを最適化
        optimized_data = optimize_data(result)

        # ETagを生成
        etag = create_etag(optimized_data)

        # 条件付きレスポンスを作成
        return create_conditional_response(
            data=optimized_data,
            etag=etag,
            request=request,
            message="Trends retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error in get_trends_optimized: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/newsletters")
async def get_newsletters_optimized(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
):
    """最適化されたニュースレター取得エンドポイント"""
    try:
        query_optimizer = QueryOptimizer(db)
        result = await query_optimizer.get_newsletters_optimized(
            skip=skip, limit=limit, status=status, date_from=date_from, date_to=date_to
        )

        # データを最適化
        optimized_data = optimize_data(result)

        # ETagを生成
        etag = create_etag(optimized_data)

        # 条件付きレスポンスを作成
        return create_conditional_response(
            data=optimized_data,
            etag=etag,
            request=request,
            message="Newsletters retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error in get_newsletters_optimized: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/dashboard")
async def get_dashboard_optimized(request: Request, db: AsyncSession = Depends(get_db)):
    """最適化されたダッシュボードデータ取得エンドポイント"""
    try:
        query_optimizer = QueryOptimizer(db)
        result = await query_optimizer.get_dashboard_data_optimized()

        # データを最適化
        optimized_data = optimize_data(result)

        # ETagを生成
        etag = create_etag(optimized_data)

        # 条件付きレスポンスを作成
        return create_conditional_response(
            data=optimized_data,
            etag=etag,
            request=request,
            message="Dashboard data retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error in get_dashboard_optimized: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/performance/stats")
async def get_performance_stats():
    """パフォーマンス統計取得エンドポイント"""
    try:
        stats = performance_metrics.get_stats()
        return create_success_response(
            data=stats, message="Performance statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error in get_performance_stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/performance/reset")
async def reset_performance_stats():
    """パフォーマンス統計リセットエンドポイント"""
    try:
        from middleware.performance_middleware import reset_performance_stats

        reset_performance_stats()
        return create_success_response(
            data={"reset": True}, message="Performance statistics reset successfully"
        )
    except Exception as e:
        logger.error(f"Error in reset_performance_stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        # 基本的なヘルスチェック
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": "unknown",  # 実際の実装ではuptimeを計算
        }

        return create_success_response(data=health_data, message="Service is healthy")
    except Exception as e:
        logger.error(f"Error in health_check: {e}")
        return create_error_response(
            message="Service is unhealthy",
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
        )


# バッチ処理エンドポイント
@router.post("/batch/articles")
async def batch_get_articles(
    request: Request, article_ids: List[str], db: AsyncSession = Depends(get_db)
):
    """複数の記事を一括取得"""
    try:
        if len(article_ids) > 50:  # バッチサイズ制限
            raise HTTPException(
                status_code=400, detail="Too many articles requested (max 50)"
            )

        query_optimizer = QueryOptimizer(db)
        # ここでバッチ取得の実装を追加
        # 現在は個別取得の実装例

        results = []
        for article_id in article_ids:
            try:
                # 個別記事取得の実装
                # result = await query_optimizer.get_article_by_id(article_id)
                # results.append(result)
                pass
            except Exception as e:
                logger.warning(f"Failed to fetch article {article_id}: {e}")
                results.append({"id": article_id, "error": "Not found"})

        return create_success_response(
            data=results, message=f"Batch articles retrieved ({len(results)} items)"
        )

    except Exception as e:
        logger.error(f"Error in batch_get_articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
