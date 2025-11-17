"""
Audit Models
Defines audit event and related models for security auditing
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuditEventType(str, Enum):
    """Audit event types"""

    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    USER_REGISTRATION = "USER_REGISTRATION"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    DATA_ACCESS = "DATA_ACCESS"
    DATA_MODIFICATION = "DATA_MODIFICATION"
    DATA_DELETION = "DATA_DELETION"
    ADMIN_ACTION = "ADMIN_ACTION"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    SECURITY_EVENT = "SECURITY_EVENT"


class AuditEvent(BaseModel):
    """Audit event Pydantic model"""

    id: str
    event_type: AuditEventType
    user_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    result: str  # success, failure, error
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AuditEventDB(Base):
    """Audit event SQLAlchemy model"""

    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, index=True)
    event_type = Column(SQLEnum(AuditEventType), nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    resource_type = Column(String, nullable=True, index=True)
    resource_id = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False)
    result = Column(String, nullable=False)  # success, failure, error
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    event_data = Column(JSON, nullable=True)
    session_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type.value if self.event_type else None,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "result": self.result,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "event_data": self.event_data,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<AuditEventDB(id={self.id}, event_type={self.event_type}, user_id={self.user_id})>"
