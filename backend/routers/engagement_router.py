"""
Engagement Router for AICA-SyS
Phase 9-2: User engagement enhancement
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.engagement_service import EngagementService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/engagement", tags=["engagement"])


# Request Models
class CommentCreateRequest(BaseModel):
    """コメント作成リクエスト"""

    content_id: str
    user_id: str
    content: str
    parent_id: Optional[int] = None


class ReviewCreateRequest(BaseModel):
    """レビュー作成リクエスト"""

    content_id: str
    user_id: str
    rating: int
    title: str
    content: str


class ReactionRequest(BaseModel):
    """リアクションリクエスト"""

    target_type: str
    target_id: str
    user_id: str
    reaction_type: str


class FollowRequest(BaseModel):
    """フォローリクエスト"""

    follower_id: str
    following_id: str


# Comment Endpoints
@router.post("/comments")
async def create_comment(request: CommentCreateRequest, db: Session = Depends(get_db)):
    """コメントを作成"""
    try:
        service = EngagementService(db)
        comment = await service.create_comment(
            content_id=request.content_id,
            user_id=request.user_id,
            content=request.content,
            parent_id=request.parent_id,
        )
        return {"success": True, "comment": comment}
    except Exception as e:
        logger.error(f"Comment creation error: {e}")
        raise HTTPException(status_code=500, detail="コメント作成に失敗しました")


@router.get("/comments/{content_id}")
async def get_comments(content_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """コメント一覧を取得"""
    try:
        service = EngagementService(db)
        comments = await service.get_comments(content_id, limit)
        return {"success": True, "comments": comments, "count": len(comments)}
    except Exception as e:
        logger.error(f"Get comments error: {e}")
        raise HTTPException(status_code=500, detail="コメント取得に失敗しました")


# Review Endpoints
@router.post("/reviews")
async def create_review(request: ReviewCreateRequest, db: Session = Depends(get_db)):
    """レビューを作成"""
    try:
        service = EngagementService(db)
        review = await service.create_review(
            content_id=request.content_id,
            user_id=request.user_id,
            rating=request.rating,
            title=request.title,
            content=request.content,
        )
        return {"success": True, "review": review}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Review creation error: {e}")
        raise HTTPException(status_code=500, detail="レビュー作成に失敗しました")


@router.get("/reviews/{content_id}")
async def get_reviews(content_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """レビュー一覧を取得"""
    try:
        service = EngagementService(db)
        reviews = await service.get_reviews(content_id, limit)
        avg_rating = await service.get_average_rating(content_id)
        return {
            "success": True,
            "reviews": reviews,
            "count": len(reviews),
            "average_rating": avg_rating,
        }
    except Exception as e:
        logger.error(f"Get reviews error: {e}")
        raise HTTPException(status_code=500, detail="レビュー取得に失敗しました")


# Reaction Endpoints
@router.post("/reactions")
async def add_reaction(request: ReactionRequest, db: Session = Depends(get_db)):
    """リアクションを追加"""
    try:
        service = EngagementService(db)
        reaction = await service.add_reaction(
            target_type=request.target_type,
            target_id=request.target_id,
            user_id=request.user_id,
            reaction_type=request.reaction_type,
        )
        return {"success": True, "reaction": reaction}
    except Exception as e:
        logger.error(f"Add reaction error: {e}")
        raise HTTPException(status_code=500, detail="リアクション追加に失敗しました")


@router.delete("/reactions")
async def remove_reaction(request: ReactionRequest, db: Session = Depends(get_db)):
    """リアクションを削除"""
    try:
        service = EngagementService(db)
        success = await service.remove_reaction(
            target_type=request.target_type,
            target_id=request.target_id,
            user_id=request.user_id,
            reaction_type=request.reaction_type,
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Remove reaction error: {e}")
        raise HTTPException(status_code=500, detail="リアクション削除に失敗しました")


@router.get("/reactions/{target_type}/{target_id}")
async def get_reactions(
    target_type: str, target_id: str, db: Session = Depends(get_db)
):
    """リアクション数を取得"""
    try:
        service = EngagementService(db)
        counts = await service.get_reaction_counts(target_type, target_id)
        return {"success": True, "reactions": counts}
    except Exception as e:
        logger.error(f"Get reactions error: {e}")
        raise HTTPException(status_code=500, detail="リアクション取得に失敗しました")


# Follow Endpoints
@router.post("/follow")
async def follow_user(request: FollowRequest, db: Session = Depends(get_db)):
    """ユーザーをフォロー"""
    try:
        service = EngagementService(db)
        follow = await service.follow_user(
            follower_id=request.follower_id, following_id=request.following_id
        )
        return {"success": True, "follow": follow}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Follow error: {e}")
        raise HTTPException(status_code=500, detail="フォローに失敗しました")


@router.delete("/follow")
async def unfollow_user(request: FollowRequest, db: Session = Depends(get_db)):
    """ユーザーをアンフォロー"""
    try:
        service = EngagementService(db)
        success = await service.unfollow_user(
            follower_id=request.follower_id, following_id=request.following_id
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Unfollow error: {e}")
        raise HTTPException(status_code=500, detail="アンフォローに失敗しました")


@router.get("/followers/{user_id}")
async def get_followers(user_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """フォロワー一覧を取得"""
    try:
        service = EngagementService(db)
        followers = await service.get_followers(user_id, limit)
        return {"success": True, "followers": followers, "count": len(followers)}
    except Exception as e:
        logger.error(f"Get followers error: {e}")
        raise HTTPException(status_code=500, detail="フォロワー取得に失敗しました")


@router.get("/following/{user_id}")
async def get_following(user_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """フォロー中一覧を取得"""
    try:
        service = EngagementService(db)
        following = await service.get_following(user_id, limit)
        return {"success": True, "following": following, "count": len(following)}
    except Exception as e:
        logger.error(f"Get following error: {e}")
        raise HTTPException(status_code=500, detail="フォロー中取得に失敗しました")


# Notification Endpoints
@router.get("/notifications/{user_id}")
async def get_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """通知一覧を取得"""
    try:
        service = EngagementService(db)
        notifications = await service.get_notifications(user_id, unread_only, limit)
        return {
            "success": True,
            "notifications": notifications,
            "count": len(notifications),
        }
    except Exception as e:
        logger.error(f"Get notifications error: {e}")
        raise HTTPException(status_code=500, detail="通知取得に失敗しました")


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int, user_id: str, db: Session = Depends(get_db)
):
    """通知を既読にする"""
    try:
        service = EngagementService(db)
        success = await service.mark_notification_read(notification_id, user_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Mark notification read error: {e}")
        raise HTTPException(status_code=500, detail="通知更新に失敗しました")


@router.put("/notifications/{user_id}/read-all")
async def mark_all_notifications_read(user_id: str, db: Session = Depends(get_db)):
    """全通知を既読にする"""
    try:
        service = EngagementService(db)
        count = await service.mark_all_read(user_id)
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"Mark all read error: {e}")
        raise HTTPException(status_code=500, detail="通知更新に失敗しました")


# Gamification Endpoints
@router.get("/points/{user_id}")
async def get_user_points(user_id: str, db: Session = Depends(get_db)):
    """ユーザーポイントを取得"""
    try:
        service = EngagementService(db)
        points = await service.get_user_points(user_id)
        return {"success": True, "points": points}
    except Exception as e:
        logger.error(f"Get user points error: {e}")
        raise HTTPException(status_code=500, detail="ポイント取得に失敗しました")


@router.get("/badges/{user_id}")
async def get_user_badges(user_id: str, db: Session = Depends(get_db)):
    """ユーザーバッジを取得"""
    try:
        service = EngagementService(db)
        badges = await service.get_user_badges(user_id)
        return {"success": True, "badges": badges, "count": len(badges)}
    except Exception as e:
        logger.error(f"Get user badges error: {e}")
        raise HTTPException(status_code=500, detail="バッジ取得に失敗しました")


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 100, db: Session = Depends(get_db)):
    """リーダーボードを取得"""
    try:
        service = EngagementService(db)
        leaderboard = await service.get_leaderboard(limit)
        return {"success": True, "leaderboard": leaderboard, "count": len(leaderboard)}
    except Exception as e:
        logger.error(f"Get leaderboard error: {e}")
        raise HTTPException(status_code=500, detail="リーダーボード取得に失敗しました")
