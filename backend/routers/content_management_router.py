"""
コンテンツ管理ルーター
コンテンツの作成、編集、承認、配信管理
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from database import get_db
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from models.content import Article, Newsletter, Trend
from models.user import User
from pydantic import BaseModel, Field
from security.auth_middleware import get_current_user
from services.content_generator import ContentGenerator, ContentType, GeneratedContent
from services.content_scheduler import DeliverySchedule, ScheduleType, scheduler
from sqlalchemy.orm import Session
from utils.logging import get_logger

router = APIRouter(prefix="/api/content-management", tags=["content-management"])
logger = get_logger(__name__)


# Pydantic models
class ContentStatus(str, Enum):
    """コンテンツステータス"""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentCreateRequest(BaseModel):
    """コンテンツ作成リクエスト"""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    tags: List[str] = []
    content_type: str = Field(..., pattern="^(article|newsletter|trend)$")
    target_audience: str = "developers"
    tone: str = "professional"
    auto_generate: bool = False
    keywords: List[str] = []


class ContentUpdateRequest(BaseModel):
    """コンテンツ更新リクエスト"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ContentStatus] = None


class ContentReviewRequest(BaseModel):
    """コンテンツレビューリクエスト"""

    status: ContentStatus
    feedback: Optional[str] = None
    reviewer_notes: Optional[str] = None


class ScheduleCreateRequest(BaseModel):
    """スケジュール作成リクエスト"""

    name: str = Field(..., min_length=1, max_length=255)
    schedule_type: str = Field(..., pattern="^(daily|weekly|monthly|custom)$")
    content_type: str = Field(..., pattern="^(article|newsletter|technical_guide)$")
    target_audience: str = "developers"
    tone: str = "professional"
    enabled: bool = True
    custom_interval_hours: Optional[int] = None


class ContentResponse(BaseModel):
    """コンテンツレスポンス"""

    id: str
    title: str
    content: str
    summary: str
    tags: List[str]
    content_type: str
    status: str
    author_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    view_count: int = 0
    like_count: int = 0


@router.get("/content", response_model=List[ContentResponse])
async def get_content_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None),
    status: Optional[ContentStatus] = Query(None),
    author_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """コンテンツ一覧を取得"""
    try:
        query = db.query(Article)

        if content_type == "newsletter":
            query = db.query(Newsletter)
        elif content_type == "trend":
            query = db.query(Trend)

        if status:
            # ステータスフィルタリング（実装は簡略化）
            pass

        if author_id:
            query = query.filter(Article.author_id == author_id)

        content_items = query.offset(skip).limit(limit).all()

        return [
            ContentResponse(
                id=str(item.id),
                title=item.title,
                content=item.content,
                summary=getattr(item, "summary", ""),
                tags=getattr(item, "tags", []),
                content_type=content_type or "article",
                status="published",  # デフォルト
                author_id=str(item.author_id) if item.author_id else None,
                created_at=item.created_at,
                updated_at=item.updated_at,
                published_at=getattr(item, "published_at", None),
            )
            for item in content_items
        ]

    except Exception as e:
        logger.error(f"Failed to get content list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content list",
        )


@router.post("/content", response_model=ContentResponse)
async def create_content(
    request: ContentCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新しいコンテンツを作成"""
    try:
        if request.auto_generate:
            # AI自動生成
            background_tasks.add_task(
                _generate_content_background, request, current_user.id, db
            )
            return {"message": "Content generation started in background"}

        # 手動作成
        if request.content_type == "article":
            article = Article(
                title=request.title,
                content=request.content,
                summary=request.summary or request.content[:200] + "...",
                tags=request.tags,
                author_id=current_user.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(article)
            db.commit()
            db.refresh(article)

            return ContentResponse(
                id=str(article.id),
                title=article.title,
                content=article.content,
                summary=article.summary,
                tags=article.tags,
                content_type="article",
                status="draft",
                author_id=str(article.author_id),
                created_at=article.created_at,
                updated_at=article.updated_at,
            )

        elif request.content_type == "newsletter":
            newsletter = Newsletter(
                title=request.title,
                content=request.content,
                summary=request.summary or request.content[:200] + "...",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(newsletter)
            db.commit()
            db.refresh(newsletter)

            return ContentResponse(
                id=str(newsletter.id),
                title=newsletter.title,
                content=newsletter.content,
                summary=newsletter.summary,
                tags=[],
                content_type="newsletter",
                status="draft",
                author_id=str(current_user.id),
                created_at=newsletter.created_at,
                updated_at=newsletter.updated_at,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported content type",
            )

    except Exception as e:
        logger.error(f"Failed to create content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content",
        )


@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    request: ContentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """コンテンツを更新"""
    try:
        # 記事を検索
        article = db.query(Article).filter(Article.id == content_id).first()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )

        # 権限チェック（作成者または管理者のみ）
        if article.author_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this content",
            )

        # 更新
        if request.title:
            article.title = request.title
        if request.content:
            article.content = request.content
        if request.summary:
            article.summary = request.summary
        if request.tags:
            article.tags = request.tags

        article.updated_at = datetime.now()

        db.commit()
        db.refresh(article)

        return ContentResponse(
            id=str(article.id),
            title=article.title,
            content=article.content,
            summary=article.summary,
            tags=article.tags,
            content_type="article",
            status="draft",
            author_id=str(article.author_id),
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content",
        )


@router.post("/content/{content_id}/review")
async def review_content(
    content_id: str,
    request: ContentReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """コンテンツをレビュー"""
    try:
        # 管理者のみレビュー可能
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        article = db.query(Article).filter(Article.id == content_id).first()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )

        # レビュー情報を保存（実装は簡略化）
        logger.info(
            f"Content {content_id} reviewed by {current_user.email}: {request.status}"
        )

        return {"message": "Content review completed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to review content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to review content",
        )


@router.post("/content/{content_id}/publish")
async def publish_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """コンテンツを公開"""
    try:
        article = db.query(Article).filter(Article.id == content_id).first()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )

        # 権限チェック
        if article.author_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to publish this content",
            )

        # 公開
        article.published_at = datetime.now()
        article.updated_at = datetime.now()

        db.commit()

        logger.info(f"Content {content_id} published by {current_user.email}")

        return {"message": "Content published successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish content",
        )


@router.delete("/content/{content_id}")
async def delete_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """コンテンツを削除"""
    try:
        article = db.query(Article).filter(Article.id == content_id).first()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )

        # 権限チェック
        if article.author_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this content",
            )

        db.delete(article)
        db.commit()

        logger.info(f"Content {content_id} deleted by {current_user.email}")

        return {"message": "Content deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content",
        )


@router.get("/schedules")
async def get_schedules(current_user: User = Depends(get_current_user)):
    """配信スケジュール一覧を取得"""
    try:
        # 管理者のみスケジュール管理可能
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        schedules = await scheduler.get_schedule_list()
        return {"schedules": schedules}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schedules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schedules",
        )


@router.post("/schedules")
async def create_schedule(
    request: ScheduleCreateRequest, current_user: User = Depends(get_current_user)
):
    """新しい配信スケジュールを作成"""
    try:
        # 管理者のみスケジュール作成可能
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        schedule = DeliverySchedule(
            id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=request.name,
            schedule_type=ScheduleType(request.schedule_type),
            content_type=ContentType(request.content_type),
            target_audience=request.target_audience,
            tone=request.tone,
            enabled=request.enabled,
            metadata={"custom_interval_hours": request.custom_interval_hours},
        )

        await scheduler.create_schedule(schedule)

        logger.info(f"Schedule created: {request.name} by {current_user.email}")

        return {"message": "Schedule created successfully", "schedule_id": schedule.id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create schedule",
        )


@router.get("/schedules/status")
async def get_scheduler_status(current_user: User = Depends(get_current_user)):
    """スケジューラーの状態を取得"""
    try:
        # 管理者のみ状態確認可能
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        schedule_status = await scheduler.get_schedule_status()
        return schedule_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scheduler status",
        )


async def _generate_content_background(
    request: ContentCreateRequest, user_id: str, db: Session
):
    """バックグラウンドでコンテンツを生成"""
    try:
        # AIコンテンツ生成（実装は簡略化）
        logger.info(f"Generating content for user {user_id}: {request.title}")

        # 実際の実装では、ContentGeneratorを使用してコンテンツを生成
        # ここでは簡略化

    except Exception as e:
        logger.error(f"Background content generation failed: {e}")
