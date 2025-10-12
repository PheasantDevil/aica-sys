"""
Engagement Models for AICA-SyS
Phase 9-2: User engagement enhancement
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text)

from database import Base


class ReactionType(str, Enum):
    """リアクションタイプ"""
    LIKE = "like"
    LOVE = "love"
    HELPFUL = "helpful"
    INSIGHTFUL = "insightful"
    BOOKMARK = "bookmark"


class NotificationType(str, Enum):
    """通知タイプ"""
    COMMENT = "comment"
    REPLY = "reply"
    REACTION = "reaction"
    FOLLOW = "follow"
    MENTION = "mention"
    BADGE = "badge"
    LEVEL_UP = "level_up"


# SQLAlchemy Models
class CommentDB(Base):
    """コメントDBモデル"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, index=True)
    user_id = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReviewDB(Base):
    """レビューDBモデル"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, index=True)
    user_id = Column(String, index=True)
    rating = Column(Integer)  # 1-5
    title = Column(String(200))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReactionDB(Base):
    """リアクションDBモデル"""
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String)  # content, comment, review
    target_id = Column(String, index=True)
    user_id = Column(String, index=True)
    reaction_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class FollowDB(Base):
    """フォローDBモデル"""
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String, index=True)
    following_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationDB(Base):
    """通知DBモデル"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    notification_type = Column(String)
    title = Column(String(200))
    content = Column(Text)
    link = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPointDB(Base):
    """ユーザーポイントDBモデル"""
    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BadgeDB(Base):
    """バッジDBモデル"""
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    icon = Column(String)
    points_required = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserBadgeDB(Base):
    """ユーザーバッジDBモデル"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models
class Comment(BaseModel):
    """コメントモデル"""
    id: int
    content_id: str
    user_id: str
    parent_id: Optional[int] = None
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Review(BaseModel):
    """レビューモデル"""
    id: int
    content_id: str
    user_id: str
    rating: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Reaction(BaseModel):
    """リアクションモデル"""
    id: int
    target_type: str
    target_id: str
    user_id: str
    reaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class Follow(BaseModel):
    """フォローモデル"""
    id: int
    follower_id: str
    following_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class Notification(BaseModel):
    """通知モデル"""
    id: int
    user_id: str
    notification_type: str
    title: str
    content: str
    link: Optional[str] = None
    is_read: bool
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserPoint(BaseModel):
    """ユーザーポイントモデル"""
    id: int
    user_id: str
    total_points: int
    level: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Badge(BaseModel):
    """バッジモデル"""
    id: int
    name: str
    description: str
    icon: str
    points_required: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBadge(BaseModel):
    """ユーザーバッジモデル"""
    id: int
    user_id: str
    badge_id: int
    earned_at: datetime

    class Config:
        from_attributes = True

