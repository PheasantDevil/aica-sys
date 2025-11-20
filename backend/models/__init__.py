"""
Models package for AICA-SyS
"""

from models.audit import AuditEvent, AuditEventDB, AuditEventType
from models.collection import AnalysisResult, CollectionJob
from models.content import Article, Newsletter, Trend
from models.subscription import Subscription

# Import all models to make them accessible from the models package
from models.user import User

__all__ = [
    "User",
    "Article",
    "Newsletter",
    "Trend",
    "Subscription",
    "CollectionJob",
    "AnalysisResult",
    "AuditEvent",
    "AuditEventDB",
    "AuditEventType",
]
