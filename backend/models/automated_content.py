"""
Automated Content Models for AICA-SyS
Phase 10-1: Daily article generation
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from database import Base
from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text


class ContentType(str, Enum):
    """コンテンツタイプ"""
    ARTICLE = "article"
    NEWSLETTER = "newsletter"
    TREND = "trend"


class ContentStatus(str, Enum):
    """コンテンツステータス"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SourceType(str, Enum):
    """ソースタイプ"""
    HACKER_NEWS = "hacker_news"
    DEV_TO = "dev_to"
    GITHUB_TRENDING = "github_trending"
    REDDIT = "reddit"
    TECH_CRUNCH = "tech_crunch"


# SQLAlchemy Models
class AutomatedContentDB(Base):
    """自動生成コンテンツDBモデル"""
    __tablename__ = "automated_contents"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, index=True)
    title = Column(String(300))
    slug = Column(String(300), unique=True, index=True)
    summary = Column(Text)
    content = Column(Text)
    content_metadata = Column(JSON)  # 'metadata'は予約語のため'content_metadata'に変更
    seo_data = Column(JSON)
    quality_score = Column(Float, default=0.0)
    status = Column(String, default=ContentStatus.DRAFT)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrendDataDB(Base):
    """トレンドデータDBモデル"""
    __tablename__ = "trend_data"

    id = Column(Integer, primary_key=True, index=True)
    trend_name = Column(String(200), index=True)
    trend_score = Column(Float)
    source_count = Column(Integer, default=1)
    keywords = Column(JSON)
    related_topics = Column(JSON)
    data_snapshot = Column(JSON)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)


class SourceDataDB(Base):
    """ソースデータDBモデル"""
    __tablename__ = "source_data"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, index=True)
    source_url = Column(String)
    title = Column(String(500))
    content = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    source_metadata = Column(JSON)  # 'metadata'は予約語のため'source_metadata'に変更
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)


class ContentGenerationLogDB(Base):
    """コンテンツ生成ログDBモデル"""
    __tablename__ = "content_generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, nullable=True)
    generation_type = Column(String)
    status = Column(String)  # success, failed, skipped
    error_message = Column(Text, nullable=True)
    api_cost = Column(Float, default=0.0)
    generation_time = Column(Float)  # seconds
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Pydantic Models
class AutomatedContent(BaseModel):
    """自動生成コンテンツモデル"""
    id: int
    content_type: str
    title: str
    slug: str
    summary: str
    content: str
    content_metadata: Optional[dict] = None
    seo_data: Optional[dict] = None
    quality_score: float
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrendData(BaseModel):
    """トレンドデータモデル"""
    id: int
    trend_name: str
    trend_score: float
    source_count: int
    keywords: List[str]
    related_topics: List[str]
    data_snapshot: dict
    detected_at: datetime

    class Config:
        from_attributes = True


class SourceData(BaseModel):
    """ソースデータモデル"""
    id: int
    source_type: str
    source_url: str
    title: str
    content: Optional[str] = None
    score: Optional[float] = None
    source_metadata: dict
    collected_at: datetime

    class Config:
        from_attributes = True


class ContentGenerationLog(BaseModel):
    """コンテンツ生成ログモデル"""
    id: int
    content_id: Optional[int] = None
    generation_type: str
    status: str
    error_message: Optional[str] = None
    api_cost: float
    generation_time: float
    quality_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

