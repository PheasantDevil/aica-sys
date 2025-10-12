"""
Content Quality Router for AICA-SyS
Phase 9-1: Content quality improvement
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.content_quality_service import content_quality_service
from services.content_recommendation_service import content_recommendation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content-quality", tags=["content-quality"])

class ContentEvaluationRequest(BaseModel):
    """コンテンツ評価リクエスト"""
    title: str
    content: str

class InteractionRequest(BaseModel):
    """インタラクション記録リクエスト"""
    user_id: str
    content_id: str
    interaction_type: str  # view, like, share, bookmark
    metadata: Optional[dict] = None

@router.post("/evaluate")
async def evaluate_content(request: ContentEvaluationRequest):
    """コンテンツの品質を評価"""
    try:
        result = content_quality_service.evaluate_content(
            content=request.content,
            title=request.title
        )
        
        return {
            "success": True,
            "evaluation": result
        }
    except Exception as e:
        logger.error(f"Content evaluation error: {e}")
        raise HTTPException(status_code=500, detail="評価に失敗しました")

@router.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    limit: int = 10
):
    """ユーザーへのコンテンツ推薦"""
    try:
        recommendations = await content_recommendation_service.recommend_personalized(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="推薦に失敗しました")

@router.get("/similar/{content_id}")
async def get_similar_content(
    content_id: str,
    limit: int = 5
):
    """類似コンテンツの取得"""
    try:
        similar = await content_recommendation_service.recommend_similar_content(
            content_id=content_id,
            limit=limit
        )
        
        return {
            "success": True,
            "content_id": content_id,
            "similar_contents": similar,
            "count": len(similar)
        }
    except Exception as e:
        logger.error(f"Similar content error: {e}")
        raise HTTPException(status_code=500, detail="類似コンテンツ取得に失敗しました")

@router.get("/trending")
async def get_trending_content(
    category: Optional[str] = None,
    limit: int = 10
):
    """トレンドコンテンツの取得"""
    try:
        trending = await content_recommendation_service.recommend_trending(
            category=category,
            limit=limit
        )
        
        return {
            "success": True,
            "category": category,
            "trending_contents": trending,
            "count": len(trending)
        }
    except Exception as e:
        logger.error(f"Trending content error: {e}")
        raise HTTPException(status_code=500, detail="トレンド取得に失敗しました")

@router.post("/interaction")
async def record_interaction(request: InteractionRequest):
    """ユーザーインタラクションを記録"""
    try:
        content_recommendation_service.record_interaction(
            user_id=request.user_id,
            content_id=request.content_id,
            interaction_type=request.interaction_type,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "message": "インタラクションを記録しました"
        }
    except Exception as e:
        logger.error(f"Interaction recording error: {e}")
        raise HTTPException(status_code=500, detail="記録に失敗しました")
