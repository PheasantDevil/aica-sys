"""
Analytics Models for AICA-SyS
Phase 9-5: Analytics and reports
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from database import Base
from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text


class ReportType(str, Enum):
    """レポートタイプ"""
    REVENUE = "revenue"
    USERS = "users"
    CONTENT = "content"
    SUBSCRIPTION = "subscription"
    AFFILIATE = "affiliate"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """レポートフォーマット"""
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class ScheduleFrequency(str, Enum):
    """スケジュール頻度"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# SQLAlchemy Models
class AnalyticsEventDB(Base):
    """アナリティクスイベントDBモデル"""
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    user_id = Column(String, index=True, nullable=True)
    session_id = Column(String, index=True, nullable=True)
    properties = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class MetricSnapshotDB(Base):
    """メトリックスナップショットDBモデル"""
    __tablename__ = "metric_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    metric_value = Column(Float)
    dimensions = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ReportDB(Base):
    """レポートDBモデル"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    title = Column(String(200))
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)
    format = Column(String)
    file_url = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScheduledReportDB(Base):
    """スケジュールレポートDBモデル"""
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    title = Column(String(200))
    frequency = Column(String)
    recipients = Column(JSON)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class DashboardDB(Base):
    """ダッシュボードDBモデル"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text, nullable=True)
    user_id = Column(String, index=True)
    widgets = Column(JSON)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSegmentDB(Base):
    """ユーザーセグメントDBモデル"""
    __tablename__ = "user_segments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text, nullable=True)
    criteria = Column(JSON)
    user_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Models
class AnalyticsEvent(BaseModel):
    """アナリティクスイベントモデル"""
    id: int
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MetricSnapshot(BaseModel):
    """メトリックスナップショットモデル"""
    id: int
    metric_name: str
    metric_value: float
    dimensions: Optional[dict] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class Report(BaseModel):
    """レポートモデル"""
    id: int
    report_type: str
    title: str
    description: Optional[str] = None
    parameters: Optional[dict] = None
    data: Optional[dict] = None
    format: str
    file_url: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduledReport(BaseModel):
    """スケジュールレポートモデル"""
    id: int
    report_type: str
    title: str
    frequency: str
    recipients: list
    parameters: Optional[dict] = None
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class Dashboard(BaseModel):
    """ダッシュボードモデル"""
    id: int
    name: str
    description: Optional[str] = None
    user_id: str
    widgets: list
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSegment(BaseModel):
    """ユーザーセグメントモデル"""
    id: int
    name: str
    description: Optional[str] = None
    criteria: dict
    user_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

