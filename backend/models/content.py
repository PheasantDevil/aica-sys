"""
Content models for AICA-SyS
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TrendCategory(str, Enum):
    FRAMEWORK = "framework"
    LIBRARY = "library"
    TOOL = "tool"
    LANGUAGE = "language"
    ECOSYSTEM = "ecosystem"


class TrendImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    author: Mapped[str] = mapped_column(String(255), default="AICA-SyS")
    read_time: Mapped[int] = mapped_column(Integer, default=5)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title={self.title[:50]}...)>"


class Newsletter(Base):
    __tablename__ = "newsletters"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subscribers: Mapped[int] = mapped_column(Integer, default=0)
    open_rate: Mapped[float] = mapped_column(Integer, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Newsletter(id={self.id}, title={self.title[:50]}...)>"


class Trend(Base):
    __tablename__ = "trends"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[TrendCategory] = mapped_column(String(50), nullable=False)
    impact: Mapped[TrendImpact] = mapped_column(String(50), nullable=False)
    related_articles: Mapped[List[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Trend(id={self.id}, title={self.title[:50]}...)>"
