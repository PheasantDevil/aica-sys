from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.audit import AuditEvent, AuditEventType
from services.audit_service import AuditService, get_audit_service
from sqlalchemy.orm import Session
from utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/events", response_model=List[AuditEvent])
async def get_audit_events(
    event_type: Optional[AuditEventType] = Query(
        None, description="Filter by event type"
    ),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(
        None, description="Start date for filtering"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of events to return"
    ),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    監査イベントを取得します。
    """
    try:
        logger.info(
            f"API: Fetching audit events with filters: type={event_type}, user_id={user_id}"
        )

        events = audit_service.get_events(
            db=db,
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return events

    except Exception as e:
        logger.error(f"Error fetching audit events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit events: {str(e)}",
        )


@router.get("/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(
    event_id: str,
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    特定の監査イベントを取得します。
    """
    try:
        logger.info(f"API: Fetching audit event: {event_id}")

        event = audit_service.get_event_by_id(db, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audit event not found"
            )

        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audit event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit event: {str(e)}",
        )


@router.get("/events/user/{user_id}", response_model=List[AuditEvent])
async def get_user_audit_events(
    user_id: str,
    event_type: Optional[AuditEventType] = Query(
        None, description="Filter by event type"
    ),
    start_date: Optional[datetime] = Query(
        None, description="Start date for filtering"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of events to return"
    ),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    特定のユーザーの監査イベントを取得します。
    """
    try:
        logger.info(f"API: Fetching audit events for user: {user_id}")

        events = audit_service.get_user_events(
            db=db,
            user_id=user_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return events

    except Exception as e:
        logger.error(f"Error fetching audit events for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user audit events: {str(e)}",
        )


@router.get(
    "/events/resource/{resource_type}/{resource_id}", response_model=List[AuditEvent]
)
async def get_resource_audit_events(
    resource_type: str,
    resource_id: str,
    event_type: Optional[AuditEventType] = Query(
        None, description="Filter by event type"
    ),
    start_date: Optional[datetime] = Query(
        None, description="Start date for filtering"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of events to return"
    ),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    特定のリソースの監査イベントを取得します。
    """
    try:
        logger.info(
            f"API: Fetching audit events for resource: {resource_type}/{resource_id}"
        )

        events = audit_service.get_resource_events(
            db=db,
            resource_type=resource_type,
            resource_id=resource_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return events

    except Exception as e:
        logger.error(
            f"Error fetching audit events for resource {resource_type}/{resource_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resource audit events: {str(e)}",
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_audit_stats(
    start_date: Optional[datetime] = Query(
        None, description="Start date for statistics"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    監査統計を取得します。
    """
    try:
        logger.info("API: Fetching audit statistics")

        stats = audit_service.get_statistics(
            db=db, start_date=start_date, end_date=end_date
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching audit statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit statistics: {str(e)}",
        )


@router.get("/stats/events", response_model=Dict[str, Any])
async def get_event_type_stats(
    start_date: Optional[datetime] = Query(
        None, description="Start date for statistics"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    イベントタイプ別の統計を取得します。
    """
    try:
        logger.info("API: Fetching event type statistics")

        stats = audit_service.get_event_type_statistics(
            db=db, start_date=start_date, end_date=end_date
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching event type statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch event type statistics: {str(e)}",
        )


@router.get("/stats/users", response_model=Dict[str, Any])
async def get_user_activity_stats(
    start_date: Optional[datetime] = Query(
        None, description="Start date for statistics"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of users to return"
    ),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    ユーザーアクティビティ統計を取得します。
    """
    try:
        logger.info("API: Fetching user activity statistics")

        stats = audit_service.get_user_activity_statistics(
            db=db, start_date=start_date, end_date=end_date, limit=limit
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching user activity statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user activity statistics: {str(e)}",
        )


@router.get("/stats/resources", response_model=Dict[str, Any])
async def get_resource_activity_stats(
    start_date: Optional[datetime] = Query(
        None, description="Start date for statistics"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of resources to return"
    ),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_db),
):
    """
    リソースアクティビティ統計を取得します。
    """
    try:
        logger.info("API: Fetching resource activity statistics")

        stats = audit_service.get_resource_activity_statistics(
            db=db, start_date=start_date, end_date=end_date, limit=limit
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching resource activity statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resource activity statistics: {str(e)}",
        )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_audit_dashboard(
    start_date: Optional[datetime] = Query(
        None, description="Start date for dashboard data"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for dashboard data"
    ),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    監査ダッシュボード用のデータを取得します。
    """
    try:
        logger.info("API: Fetching audit dashboard data")

        # デフォルトの期間を設定（過去30日）
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        dashboard_data = audit_service.get_dashboard_data(
            db=db, start_date=start_date, end_date=end_date
        )

        return dashboard_data

    except Exception as e:
        logger.error(f"Error fetching audit dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit dashboard data: {str(e)}",
        )


@router.post("/events/search", response_model=List[AuditEvent])
async def search_audit_events(
    search_query: str = Query(..., description="Search query"),
    event_type: Optional[AuditEventType] = Query(
        None, description="Filter by event type"
    ),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(
        None, description="Start date for filtering"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of events to return"
    ),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    監査イベントを検索します。
    """
    try:
        logger.info(f"API: Searching audit events with query: {search_query}")

        events = audit_service.search_events(
            db=db,
            search_query=search_query,
            event_type=event_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return events

    except Exception as e:
        logger.error(f"Error searching audit events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search audit events: {str(e)}",
        )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_event(
    event_id: str,
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    監査イベントを削除します（管理者のみ）。
    """
    try:
        logger.info(f"API: Deleting audit event: {event_id}")

        # 実際の実装では、管理者権限をチェック
        # if not current_user.is_superuser:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to delete audit events"
        #     )

        success = audit_service.delete_event(db, event_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audit event not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting audit event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete audit event: {str(e)}",
        )


@router.post("/events/export", response_model=Dict[str, Any])
async def export_audit_events(
    event_type: Optional[AuditEventType] = Query(
        None, description="Filter by event type"
    ),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(
        None, description="Start date for filtering"
    ),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    format: str = Query("json", description="Export format (json, csv)"),
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    監査イベントをエクスポートします。
    """
    try:
        logger.info(f"API: Exporting audit events in format: {format}")

        # 実際の実装では、管理者権限をチェック
        # if not current_user.is_superuser:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not authorized to export audit events"
        #     )

        export_data = audit_service.export_events(
            db=db,
            event_type=event_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            format=format,
        )

        return export_data

    except Exception as e:
        logger.error(f"Error exporting audit events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export audit events: {str(e)}",
        )
