"""
AI関連のデータベースモデル
収集データ、分析結果、生成コンテンツを管理
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CollectedContent(Base):
    """収集されたコンテンツ"""

    __tablename__ = "collected_content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1000), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=True)
    source = Column(String(200), nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    author = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)  # 元の生データ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    analysis_results = relationship("AnalysisResult", back_populates="content")
    generated_contents = relationship(
        "GeneratedContent", back_populates="source_content"
    )


class AnalysisResult(Base):
    """分析結果"""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("collected_content.id"), nullable=False)
    importance_score = Column(Float, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True, index=True)
    trend_score = Column(Float, nullable=False, index=True)
    sentiment = Column(String(50), nullable=False, index=True)
    key_topics = Column(JSON, nullable=True)  # List[str]
    summary = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)  # List[str]
    analysis_metadata = Column(JSON, nullable=True)  # 分析時のメタデータ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    content = relationship("CollectedContent", back_populates="analysis_results")
    generated_contents = relationship(
        "GeneratedContent", back_populates="analysis_result"
    )


class GeneratedContent(Base):
    """生成されたコンテンツ"""

    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(
        String(50), nullable=False, index=True
    )  # article, newsletter, etc.
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List[str]
    target_audience = Column(String(100), nullable=False)
    tone = Column(String(50), nullable=False)
    word_count = Column(Integer, nullable=False)
    source_content_id = Column(
        Integer, ForeignKey("collected_content.id"), nullable=True
    )
    analysis_result_id = Column(
        Integer, ForeignKey("analysis_results.id"), nullable=True
    )
    generation_metadata = Column(JSON, nullable=True)  # 生成時のメタデータ
    is_published = Column(Boolean, default=False, index=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    source_content = relationship(
        "CollectedContent", back_populates="generated_contents"
    )
    analysis_result = relationship(
        "AnalysisResult", back_populates="generated_contents"
    )


class TrendAnalysis(Base):
    """トレンド分析結果"""

    __tablename__ = "trend_analysis"

    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    total_content_count = Column(Integer, nullable=False)
    high_importance_count = Column(Integer, nullable=False)
    trending_count = Column(Integer, nullable=False)
    category_distribution = Column(JSON, nullable=True)  # Dict[str, int]
    sentiment_distribution = Column(JSON, nullable=True)  # Dict[str, int]
    top_topics = Column(JSON, nullable=True)  # Dict[str, int]
    trending_content_ids = Column(JSON, nullable=True)  # List[int]
    analysis_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentCollection(Base):
    """コンテンツコレクション（キュレーション）"""

    __tablename__ = "content_collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    collection_type = Column(String(50), nullable=False)  # weekly, monthly, topic-based
    target_audience = Column(String(100), nullable=False)
    content_ids = Column(JSON, nullable=False)  # List[int] - GeneratedContent IDs
    is_published = Column(Boolean, default=False, index=True)
    published_at = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIConfiguration(Base):
    """AI設定"""

    __tablename__ = "ai_configurations"

    id = Column(Integer, primary_key=True, index=True)
    config_name = Column(String(100), nullable=False, unique=True, index=True)
    config_type = Column(
        String(50), nullable=False
    )  # data_collection, analysis, content_generation
    parameters = Column(JSON, nullable=False)  # 設定パラメータ
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentPerformance(Base):
    """コンテンツパフォーマンス"""

    __tablename__ = "content_performance"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("generated_content.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # view, like, share, engagement
    metric_value = Column(Float, nullable=False)
    metric_date = Column(DateTime, nullable=False, index=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserInteraction(Base):
    """ユーザーインタラクション"""

    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # ログイン済みユーザー
    session_id = Column(String(100), nullable=True)  # セッションID
    content_id = Column(Integer, ForeignKey("generated_content.id"), nullable=False)
    interaction_type = Column(
        String(50), nullable=False
    )  # view, like, share, bookmark, comment
    interaction_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ヘルパー関数
def create_content_from_item(item) -> CollectedContent:
    """ContentItemからCollectedContentを作成"""
    return CollectedContent(
        title=item.title,
        url=item.url,
        content=item.content,
        source=item.source,
        published_at=item.published_at,
        author=item.author,
        summary=item.summary,
        raw_data={
            "tags": item.tags,
            "importance_score": item.importance_score,
            "category": item.category,
        },
    )


def create_analysis_from_result(result, content_id: int) -> AnalysisResult:
    """AnalysisResultからAnalysisResultを作成"""
    return AnalysisResult(
        content_id=content_id,
        importance_score=result.importance_score,
        category=result.category,
        subcategory=result.subcategory,
        trend_score=result.trend_score,
        sentiment=result.sentiment,
        key_topics=result.key_topics,
        summary=result.summary,
        recommendations=result.recommendations,
        analysis_metadata={
            "created_at": result.created_at.isoformat(),
            "source": "ai_analyzer",
        },
    )


def create_generated_content_from_result(
    result, content_id: int = None, analysis_id: int = None
) -> GeneratedContent:
    """GeneratedContentからGeneratedContentを作成"""
    return GeneratedContent(
        content_type=result.content_type.value,
        title=result.title,
        content=result.content,
        summary=result.summary,
        tags=result.tags,
        target_audience=result.target_audience,
        tone=result.tone,
        word_count=result.word_count,
        source_content_id=content_id,
        analysis_result_id=analysis_id,
        generation_metadata=result.metadata,
    )
