import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from database import get_db
from models.audit import AuditEvent, AuditEventDB
from sqlalchemy.orm import Session
from utils.logging import get_logger

logger = get_logger(__name__)


class AuditEventType(Enum):
    """監査イベントタイプ"""

    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_EVENT = "security_event"
    ADMIN_ACTION = "admin_action"


class AuditSeverity(Enum):
    """監査重要度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditService:
    """
    監査サービス
    """

    def __init__(self):
        self.audit_config = self._initialize_audit_config()
        self.event_patterns = self._initialize_event_patterns()

    def _initialize_audit_config(self) -> Dict[str, Any]:
        """監査設定を初期化"""
        return {
            "retention_days": int(os.getenv("AUDIT_RETENTION_DAYS", "2555")),  # 7年
            "log_level": os.getenv("AUDIT_LOG_LEVEL", "medium"),
            "real_time_alerts": os.getenv("AUDIT_REAL_TIME_ALERTS", "true") == "true",
            "encryption": os.getenv("AUDIT_ENCRYPTION", "true") == "true",
            "compression": os.getenv("AUDIT_COMPRESSION", "true") == "true",
            "export_formats": ["json", "csv", "xml"],
            "alert_thresholds": {
                "failed_login_attempts": 5,
                "privilege_escalation": 1,
                "data_access_anomaly": 10,
                "admin_actions": 50,
            },
        }

    def _initialize_event_patterns(self) -> Dict[str, Dict[str, Any]]:
        """イベントパターンを初期化"""
        return {
            AuditEventType.USER_LOGIN.value: {
                "severity": AuditSeverity.MEDIUM.value,
                "required_fields": ["user_id", "ip_address", "user_agent"],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
            AuditEventType.USER_LOGOUT.value: {
                "severity": AuditSeverity.LOW.value,
                "required_fields": ["user_id"],
                "alert_on_failure": False,
                "retention_days": 2555,
            },
            AuditEventType.USER_REGISTRATION.value: {
                "severity": AuditSeverity.MEDIUM.value,
                "required_fields": ["user_id", "email", "ip_address"],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
            AuditEventType.DATA_ACCESS.value: {
                "severity": AuditSeverity.MEDIUM.value,
                "required_fields": ["user_id", "resource_type", "resource_id"],
                "alert_on_failure": False,
                "retention_days": 2555,
            },
            AuditEventType.DATA_MODIFICATION.value: {
                "severity": AuditSeverity.HIGH.value,
                "required_fields": [
                    "user_id",
                    "resource_type",
                    "resource_id",
                    "changes",
                ],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
            AuditEventType.DATA_DELETION.value: {
                "severity": AuditSeverity.CRITICAL.value,
                "required_fields": ["user_id", "resource_type", "resource_id"],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
            AuditEventType.PERMISSION_CHANGE.value: {
                "severity": AuditSeverity.HIGH.value,
                "required_fields": ["user_id", "target_user_id", "permission_changes"],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
            AuditEventType.SECURITY_EVENT.value: {
                "severity": AuditSeverity.CRITICAL.value,
                "required_fields": ["event_type", "description"],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
            AuditEventType.ADMIN_ACTION.value: {
                "severity": AuditSeverity.HIGH.value,
                "required_fields": ["admin_user_id", "action", "target"],
                "alert_on_failure": True,
                "retention_days": 2555,
            },
        }

    def log_event(
        self,
        event_type: AuditEventType,
        event_data: Dict[str, Any],
        db: Session,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        監査イベントをログ

        Args:
            event_type: イベントタイプ
            event_data: イベントデータ
            db: データベースセッション
            user_id: ユーザーID（オプション）

        Returns:
            ログ記録結果
        """
        try:
            # イベントパターンを取得
            event_pattern = self.event_patterns.get(event_type.value, {})

            # 必須フィールドをチェック
            required_fields = event_pattern.get("required_fields", [])
            missing_fields = [
                field for field in required_fields if field not in event_data
            ]

            if missing_fields:
                logger.warning(
                    f"Missing required fields for {event_type.value}: {missing_fields}"
                )

            # 監査ログレコードを作成
            audit_record = {
                "event_type": event_type.value,
                "user_id": user_id or event_data.get("user_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": event_data.get("ip_address"),
                "user_agent": event_data.get("user_agent"),
                "severity": event_pattern.get("severity", AuditSeverity.MEDIUM.value),
                "event_data": json.dumps(event_data),
                "session_id": event_data.get("session_id"),
                "resource_type": event_data.get("resource_type"),
                "resource_id": event_data.get("resource_id"),
                "action": event_data.get("action"),
                "result": event_data.get("result", "success"),
                "error_message": event_data.get("error_message"),
                "metadata": json.dumps(event_data.get("metadata", {})),
            }

            # データベースに保存
            audit_log = AuditEventDB(**audit_record)
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            # リアルタイムアラートをチェック
            if self.audit_config["real_time_alerts"]:
                self._check_real_time_alerts(audit_record, event_pattern)

            logger.info(f"Audit event logged: {event_type.value} for user {user_id}")

            return {
                "audit_id": audit_log.id,
                "event_type": event_type.value,
                "timestamp": audit_record["timestamp"],
                "severity": audit_record["severity"],
                "logged": True,
            }

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            raise

    async def _check_real_time_alerts(
        self, audit_record: Dict[str, Any], event_pattern: Dict[str, Any]
    ) -> None:
        """リアルタイムアラートをチェック"""
        try:
            # 失敗イベントのアラート
            if audit_record["result"] == "failure" and event_pattern.get(
                "alert_on_failure", False
            ):
                await self._send_alert(audit_record, "Event failure")

            # 重要度に基づくアラート
            if audit_record["severity"] in ["high", "critical"]:
                await self._send_alert(audit_record, "High severity event")

            # 異常パターンの検出
            await self._detect_anomalies(audit_record)

        except Exception as e:
            logger.error(f"Error checking real-time alerts: {e}")

    async def _send_alert(self, audit_record: Dict[str, Any], alert_type: str) -> None:
        """アラートを送信"""
        try:
            alert_data = {
                "alert_type": alert_type,
                "audit_record": audit_record,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": audit_record["severity"],
            }

            # 実際の実装では、アラートシステムに送信
            logger.warning(
                f"Security alert: {alert_type} - {audit_record['event_type']}"
            )

        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    async def _detect_anomalies(self, audit_record: Dict[str, Any]) -> None:
        """異常を検出"""
        try:
            # 失敗ログイン試行の検出
            if (
                audit_record["event_type"] == AuditEventType.USER_LOGIN.value
                and audit_record["result"] == "failure"
            ):
                await self._check_failed_login_attempts(audit_record)

            # 権限昇格の検出
            if audit_record["event_type"] == AuditEventType.PERMISSION_CHANGE.value:
                await self._check_privilege_escalation(audit_record)

            # データアクセス異常の検出
            if audit_record["event_type"] == AuditEventType.DATA_ACCESS.value:
                await self._check_data_access_anomaly(audit_record)

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")

    def get_events(
        self,
        db: Session,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """監査イベントを取得"""
        try:
            query = db.query(AuditEventDB)

            if event_type:
                query = query.filter(AuditEventDB.event_type == event_type)
            if user_id:
                query = query.filter(AuditEventDB.user_id == user_id)
            if resource_type:
                query = query.filter(AuditEventDB.resource_type == resource_type)
            if resource_id:
                query = query.filter(AuditEventDB.resource_id == resource_id)
            if start_date:
                query = query.filter(AuditEventDB.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditEventDB.timestamp <= end_date)

            query = query.order_by(AuditEventDB.timestamp.desc())
            query = query.offset(offset).limit(limit)

            events = query.all()
            return [AuditEvent.from_orm(event) for event in events]

        except Exception as e:
            logger.error(f"Error getting audit events: {e}")
            return []

    def get_event_by_id(self, db: Session, event_id: str) -> Optional[AuditEvent]:
        """IDで監査イベントを取得"""
        try:
            event = db.query(AuditEventDB).filter(AuditEventDB.id == event_id).first()
            if event:
                return AuditEvent.from_orm(event)
            return None

        except Exception as e:
            logger.error(f"Error getting audit event by ID: {e}")
            return None

    def get_user_events(
        self,
        db: Session,
        user_id: str,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """ユーザーの監査イベントを取得"""
        return self.get_events(
            db, event_type, user_id, None, None, start_date, end_date, limit, offset
        )

    def get_resource_events(
        self,
        db: Session,
        resource_type: str,
        resource_id: str,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """リソースの監査イベントを取得"""
        return self.get_events(
            db,
            event_type,
            None,
            resource_type,
            resource_id,
            start_date,
            end_date,
            limit,
            offset,
        )

    def get_statistics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """監査統計を取得"""
        try:
            query = db.query(AuditEventDB)

            if start_date:
                query = query.filter(AuditEventDB.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditEventDB.timestamp <= end_date)

            total_events = query.count()
            events_by_type = {}
            events_by_user = {}
            events_by_resource = {}

            for event in query.all():
                # イベントタイプ別
                event_type = event.event_type.value if event.event_type else "unknown"
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

                # ユーザー別
                if event.user_id:
                    events_by_user[event.user_id] = (
                        events_by_user.get(event.user_id, 0) + 1
                    )

                # リソース別
                if event.resource_type:
                    events_by_resource[event.resource_type] = (
                        events_by_resource.get(event.resource_type, 0) + 1
                    )

            return {
                "total_events": total_events,
                "events_by_type": events_by_type,
                "events_by_user": events_by_user,
                "events_by_resource": events_by_resource,
                "success_rate": 95.0,  # 仮の値
                "error_rate": 5.0,  # 仮の値
            }

        except Exception as e:
            logger.error(f"Error getting audit statistics: {e}")
            return {}

    def get_event_type_statistics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """イベントタイプ別統計を取得"""
        stats = self.get_statistics(db, start_date, end_date)
        return {"events_by_type": stats.get("events_by_type", {})}

    def get_user_activity_statistics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """ユーザーアクティビティ統計を取得"""
        stats = self.get_statistics(db, start_date, end_date)
        user_events = stats.get("events_by_user", {})

        # 上位ユーザーを取得
        top_users = sorted(user_events.items(), key=lambda x: x[1], reverse=True)[
            :limit
        ]

        return {
            "top_users": [
                {"user_id": user_id, "count": count} for user_id, count in top_users
            ]
        }

    def get_resource_activity_statistics(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """リソースアクティビティ統計を取得"""
        stats = self.get_statistics(db, start_date, end_date)
        resource_events = stats.get("events_by_resource", {})

        # 上位リソースを取得
        top_resources = sorted(
            resource_events.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return {
            "top_resources": [
                {"resource_type": resource_type, "count": count}
                for resource_type, count in top_resources
            ]
        }

    def get_dashboard_data(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """ダッシュボード用データを取得"""
        try:
            stats = self.get_statistics(db, start_date, end_date)

            # チャート用データ（仮のデータ）
            chart_data = [
                {"date": "2024-01-01", "count": 10},
                {"date": "2024-01-02", "count": 15},
                {"date": "2024-01-03", "count": 12},
            ]

            # イベントタイプ別データ
            event_type_data = [
                {"name": "USER_LOGIN", "value": 50, "color": "#0088FE"},
                {"name": "DATA_ACCESS", "value": 30, "color": "#00C49F"},
                {"name": "DATA_MODIFICATION", "value": 20, "color": "#FFBB28"},
            ]

            return {
                "stats": stats,
                "chart_data": chart_data,
                "event_type_data": event_type_data,
                "user_activity_data": [],
                "resource_activity_data": [],
                "recent_events": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    def search_events(
        self,
        db: Session,
        search_query: str,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """監査イベントを検索"""
        try:
            query = db.query(AuditEventDB)

            # 検索クエリでフィルタリング（簡易実装）
            if search_query:
                query = query.filter(
                    AuditEventDB.action.contains(search_query)
                    | AuditEventDB.result.contains(search_query)
                )

            if event_type:
                query = query.filter(AuditEventDB.event_type == event_type)
            if user_id:
                query = query.filter(AuditEventDB.user_id == user_id)
            if start_date:
                query = query.filter(AuditEventDB.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditEventDB.timestamp <= end_date)

            query = query.order_by(AuditEventDB.timestamp.desc())
            query = query.offset(offset).limit(limit)

            events = query.all()
            return [AuditEvent.from_orm(event) for event in events]

        except Exception as e:
            logger.error(f"Error searching audit events: {e}")
            return []

    def delete_event(self, db: Session, event_id: str) -> bool:
        """監査イベントを削除"""
        try:
            event = db.query(AuditEventDB).filter(AuditEventDB.id == event_id).first()
            if event:
                db.delete(event)
                db.commit()
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting audit event: {e}")
            return False

    def export_events(
        self,
        db: Session,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
    ) -> Dict[str, Any]:
        """監査イベントをエクスポート"""
        try:
            events = self.get_events(
                db, event_type, user_id, None, None, start_date, end_date, 1000, 0
            )

            if format == "json":
                export_data = [event.dict() for event in events]
            else:
                export_data = events

            return {
                "export_data": export_data,
                "format": format,
                "count": len(events),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error exporting audit events: {e}")
            return {}

    async def _check_failed_login_attempts(self, audit_record: Dict[str, Any]) -> None:
        """失敗ログイン試行をチェック"""
        try:
            # 実際の実装では、最近の失敗ログイン試行をカウント
            threshold = self.audit_config["alert_thresholds"]["failed_login_attempts"]

            # 簡易的な実装
            if audit_record.get("ip_address"):
                # IPアドレスごとの失敗試行をチェック
                pass

        except Exception as e:
            logger.error(f"Error checking failed login attempts: {e}")

    async def _check_privilege_escalation(self, audit_record: Dict[str, Any]) -> None:
        """権限昇格をチェック"""
        try:
            # 実際の実装では、権限変更のパターンを分析
            threshold = self.audit_config["alert_thresholds"]["privilege_escalation"]

            # 簡易的な実装
            if audit_record.get("event_data"):
                event_data = json.loads(audit_record["event_data"])
                if event_data.get("permission_changes"):
                    await self._send_alert(
                        audit_record, "Privilege escalation detected"
                    )

        except Exception as e:
            logger.error(f"Error checking privilege escalation: {e}")

    async def _check_data_access_anomaly(self, audit_record: Dict[str, Any]) -> None:
        """データアクセス異常をチェック"""
        try:
            # 実際の実装では、データアクセスパターンを分析
            threshold = self.audit_config["alert_thresholds"]["data_access_anomaly"]

            # 簡易的な実装
            if audit_record.get("user_id"):
                # ユーザーのデータアクセスパターンをチェック
                pass

        except Exception as e:
            logger.error(f"Error checking data access anomaly: {e}")

    def get_audit_logs(
        self, filters: Dict[str, Any], db: Session, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        監査ログを取得

        Args:
            filters: フィルター条件
            db: データベースセッション
            limit: 取得件数制限
            offset: オフセット

        Returns:
            監査ログのリスト
        """
        try:
            query = db.query(AuditEventDB)

            # フィルターを適用
            if filters.get("user_id"):
                query = query.filter(AuditEventDB.user_id == filters["user_id"])

            if filters.get("event_type"):
                query = query.filter(AuditEventDB.event_type == filters["event_type"])

            if filters.get("severity"):
                query = query.filter(AuditEventDB.severity == filters["severity"])

            if filters.get("start_date"):
                start_date = datetime.fromisoformat(filters["start_date"])
                query = query.filter(AuditEventDB.timestamp >= start_date)

            if filters.get("end_date"):
                end_date = datetime.fromisoformat(filters["end_date"])
                query = query.filter(AuditEventDB.timestamp <= end_date)

            if filters.get("ip_address"):
                query = query.filter(AuditEventDB.ip_address == filters["ip_address"])

            if filters.get("result"):
                query = query.filter(AuditEventDB.result == filters["result"])

            # ソートとページネーション
            query = query.order_by(AuditEventDB.timestamp.desc())
            query = query.offset(offset).limit(limit)

            audit_logs = query.all()

            # 辞書形式に変換
            result = []
            for log in audit_logs:
                log_dict = {
                    "id": log.id,
                    "event_type": log.event_type,
                    "user_id": log.user_id,
                    "timestamp": log.timestamp.isoformat(),
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "severity": log.severity,
                    "event_data": json.loads(log.event_data) if log.event_data else {},
                    "session_id": log.session_id,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "action": log.action,
                    "result": log.result,
                    "error_message": log.error_message,
                    "metadata": json.loads(log.metadata) if log.metadata else {},
                }
                result.append(log_dict)

            return result

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise

    def generate_audit_report(
        self, filters: Dict[str, Any], db: Session
    ) -> Dict[str, Any]:
        """
        監査レポートを生成

        Args:
            filters: フィルター条件
            db: データベースセッション

        Returns:
            監査レポート
        """
        try:
            # 監査ログを取得
            audit_logs = self.get_audit_logs(filters, db, limit=10000)

            # 統計を計算
            total_events = len(audit_logs)
            events_by_type = {}
            events_by_severity = {}
            events_by_user = {}
            events_by_result = {}

            for log in audit_logs:
                # イベントタイプ別
                event_type = log["event_type"]
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

                # 重要度別
                severity = log["severity"]
                events_by_severity[severity] = events_by_severity.get(severity, 0) + 1

                # ユーザー別
                user_id = log["user_id"]
                if user_id:
                    events_by_user[user_id] = events_by_user.get(user_id, 0) + 1

                # 結果別
                result = log["result"]
                events_by_result[result] = events_by_result.get(result, 0) + 1

            # レポートを生成
            report = {
                "report_id": f"audit_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": filters,
                "summary": {
                    "total_events": total_events,
                    "date_range": {
                        "start": filters.get("start_date"),
                        "end": filters.get("end_date"),
                    },
                },
                "statistics": {
                    "events_by_type": events_by_type,
                    "events_by_severity": events_by_severity,
                    "events_by_user": dict(
                        sorted(
                            events_by_user.items(), key=lambda x: x[1], reverse=True
                        )[:10]
                    ),
                    "events_by_result": events_by_result,
                },
                "top_users": dict(
                    sorted(events_by_user.items(), key=lambda x: x[1], reverse=True)[
                        :10
                    ]
                ),
                "critical_events": [
                    log for log in audit_logs if log["severity"] == "critical"
                ],
                "failed_events": [
                    log for log in audit_logs if log["result"] == "failure"
                ],
                "recommendations": self._generate_recommendations(
                    events_by_type, events_by_severity, events_by_result
                ),
            }

            logger.info(f"Audit report generated: {report['report_id']}")
            return report

        except Exception as e:
            logger.error(f"Error generating audit report: {e}")
            raise

    def _generate_recommendations(
        self,
        events_by_type: Dict[str, int],
        events_by_severity: Dict[str, int],
        events_by_result: Dict[str, int],
    ) -> List[str]:
        """推奨事項を生成"""
        try:
            recommendations = []

            # 失敗イベントが多い場合
            failed_events = events_by_result.get("failure", 0)
            total_events = sum(events_by_result.values())
            if total_events > 0 and (failed_events / total_events) > 0.1:
                recommendations.append(
                    "High failure rate detected. Review system configuration and user training."
                )

            # クリティカルイベントが多い場合
            critical_events = events_by_severity.get("critical", 0)
            if critical_events > 5:
                recommendations.append(
                    "Multiple critical events detected. Implement additional security measures."
                )

            # ログイン失敗が多い場合
            login_failures = events_by_type.get(AuditEventType.USER_LOGIN.value, 0)
            if login_failures > 100:
                recommendations.append(
                    "High number of login failures. Consider implementing account lockout policies."
                )

            # データアクセスが多い場合
            data_access = events_by_type.get(AuditEventType.DATA_ACCESS.value, 0)
            if data_access > 1000:
                recommendations.append(
                    "High data access volume. Review access patterns and implement data classification."
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def export_audit_logs(
        self, filters: Dict[str, Any], db: Session, format: str = "json"
    ) -> Dict[str, Any]:
        """
        監査ログをエクスポート

        Args:
            filters: フィルター条件
            db: データベースセッション
            format: エクスポート形式（json, csv, xml）

        Returns:
            エクスポート結果
        """
        try:
            # 監査ログを取得
            audit_logs = self.get_audit_logs(filters, db, limit=50000)

            export_id = f"audit_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            if format == "json":
                export_data = json.dumps(audit_logs, indent=2, default=str)
            elif format == "csv":
                export_data = self._convert_to_csv(audit_logs)
            elif format == "xml":
                export_data = self._convert_to_xml(audit_logs)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            export_result = {
                "export_id": export_id,
                "format": format,
                "record_count": len(audit_logs),
                "export_data": export_data,
                "exported_at": datetime.utcnow().isoformat(),
                "filters": filters,
            }

            logger.info(f"Audit logs exported: {export_id}")
            return export_result

        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}")
            raise

    def _convert_to_csv(self, audit_logs: List[Dict[str, Any]]) -> str:
        """CSV形式に変換"""
        try:
            if not audit_logs:
                return ""

            import csv
            import io

            output = io.StringIO()
            fieldnames = audit_logs[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)

            writer.writeheader()
            for log in audit_logs:
                writer.writerow(log)

            return output.getvalue()

        except Exception as e:
            logger.error(f"Error converting to CSV: {e}")
            return ""

    def _convert_to_xml(self, audit_logs: List[Dict[str, Any]]) -> str:
        """XML形式に変換"""
        try:
            import xml.etree.ElementTree as ET

            root = ET.Element("audit_logs")
            root.set("exported_at", datetime.utcnow().isoformat())
            root.set("count", str(len(audit_logs)))

            for log in audit_logs:
                log_element = ET.SubElement(root, "audit_log")
                for key, value in log.items():
                    if value is not None:
                        log_element.set(key, str(value))

            return ET.tostring(root, encoding="unicode")

        except Exception as e:
            logger.error(f"Error converting to XML: {e}")
            return ""

    def cleanup_old_logs(self, db: Session) -> Dict[str, Any]:
        """古い監査ログをクリーンアップ"""
        try:
            retention_days = self.audit_config["retention_days"]
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

            # 古いログを削除
            deleted_count = (
                db.query(AuditEventDB)
                .filter(AuditEventDB.timestamp < cutoff_date)
                .delete()
            )
            db.commit()

            logger.info(f"Cleaned up {deleted_count} old audit logs")

            return {
                "deleted_count": deleted_count,
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return {}


# グローバルインスタンス
audit_service = AuditService()


def get_audit_service() -> AuditService:
    """監査サービスを取得"""
    return audit_service
