import json
import time
from typing import Any, Callable, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from services.audit_service import AuditEventType, AuditService, get_audit_service
from utils.logging import get_logger

logger = get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """監査ミドルウェア"""

    def __init__(self, app):
        super().__init__(app)
        self.audit_service = get_audit_service()
        self.audit_config = self._initialize_audit_config()

    def _initialize_audit_config(self) -> Dict[str, Any]:
        """監査設定を初期化"""
        return {
            "enabled": True,
            "audit_paths": [
                "/api/auth/",
                "/api/users/",
                "/api/admin/",
                "/api/subscriptions/",
                "/api/payments/",
                "/api/monitoring/",
            ],
            "exclude_paths": [
                "/health",
                "/metrics",
                "/docs",
                "/openapi.json",
                "/favicon.ico",
            ],
            "audit_methods": ["POST", "PUT", "DELETE", "PATCH"],
            "include_get_requests": False,
            "mask_sensitive_data": True,
            "sensitive_fields": [
                "password",
                "token",
                "secret",
                "key",
                "ssn",
                "credit_card",
                "api_key",
            ],
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """リクエストを処理し、監査ログを記録"""
        try:
            # 監査が必要かチェック
            if not self._should_audit_request(request):
                return await call_next(request)

            # リクエスト情報を記録
            request_info = await self._capture_request_info(request)

            # リクエストを処理
            start_time = time.time()
            response = await call_next(request)
            end_time = time.time()

            # レスポンス情報を記録
            response_info = await self._capture_response_info(
                response, end_time - start_time
            )

            # 監査イベントを記録
            await self._log_audit_event(request_info, response_info, request, response)

            return response

        except Exception as e:
            logger.error(f"Error in audit middleware: {e}")
            return await call_next(request)

    def _should_audit_request(self, request: Request) -> bool:
        """リクエストを監査すべきかチェック"""
        try:
            if not self.audit_config["enabled"]:
                return False

            # パスをチェック
            path = request.url.path
            if any(
                path.startswith(exclude_path)
                for exclude_path in self.audit_config["exclude_paths"]
            ):
                return False

            # 監査対象パスをチェック
            if not any(
                path.startswith(audit_path)
                for audit_path in self.audit_config["audit_paths"]
            ):
                return False

            # HTTPメソッドをチェック
            method = request.method
            if method not in self.audit_config["audit_methods"]:
                if method == "GET" and not self.audit_config["include_get_requests"]:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking audit requirement: {e}")
            return False

    async def _capture_request_info(self, request: Request) -> Dict[str, Any]:
        """リクエスト情報をキャプチャ"""
        try:
            # リクエストボディを読み取り
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        body = json.loads(body_bytes.decode("utf-8"))
                        # センシティブデータをマスク
                        if self.audit_config["mask_sensitive_data"]:
                            body = self._mask_sensitive_data(body)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body = body_bytes.decode("utf-8", errors="ignore")[
                        :1000
                    ]  # 最初の1000文字のみ

            # クエリパラメータを取得
            query_params = dict(request.query_params)
            if self.audit_config["mask_sensitive_data"]:
                query_params = self._mask_sensitive_data(query_params)

            # ヘッダーを取得（センシティブなヘッダーを除外）
            headers = dict(request.headers)
            sensitive_headers = ["authorization", "cookie", "x-api-key"]
            for header in sensitive_headers:
                if header in headers:
                    headers[header] = "***MASKED***"

            request_info = {
                "method": request.method,
                "path": request.url.path,
                "query_params": query_params,
                "headers": headers,
                "body": body,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
                "timestamp": time.time(),
            }

            return request_info

        except Exception as e:
            logger.error(f"Error capturing request info: {e}")
            return {}

    async def _capture_response_info(
        self, response: Response, duration: float
    ) -> Dict[str, Any]:
        """レスポンス情報をキャプチャ"""
        try:
            response_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "duration_seconds": duration,
                "timestamp": time.time(),
            }

            return response_info

        except Exception as e:
            logger.error(f"Error capturing response info: {e}")
            return {}

    async def _log_audit_event(
        self,
        request_info: Dict[str, Any],
        response_info: Dict[str, Any],
        request: Request,
        response: Response,
    ) -> None:
        """監査イベントをログ"""
        try:
            # イベントタイプを決定
            event_type = self._determine_event_type(request_info, response_info)

            # ユーザーIDを取得
            user_id = self._extract_user_id(request)

            # イベントデータを構築
            event_data = {
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "query_params": request_info.get("query_params"),
                "status_code": response_info.get("status_code"),
                "duration_seconds": response_info.get("duration_seconds"),
                "ip_address": request_info.get("client_ip"),
                "user_agent": request_info.get("user_agent"),
                "request_body": request_info.get("body"),
                "response_headers": response_info.get("headers"),
                "session_id": self._extract_session_id(request),
                "resource_type": self._extract_resource_type(request_info.get("path")),
                "resource_id": self._extract_resource_id(request_info.get("path")),
                "action": self._extract_action(
                    request_info.get("method"), request_info.get("path")
                ),
                "result": (
                    "success"
                    if response_info.get("status_code", 500) < 400
                    else "failure"
                ),
                "error_message": (
                    None
                    if response_info.get("status_code", 500) < 400
                    else f"HTTP {response_info.get('status_code')}"
                ),
            }

            # データベースセッションを取得（実際の実装では適切に取得）
            from database import get_db

            db = next(get_db())

            # 監査イベントをログ
            self.audit_service.log_event(event_type, event_data, db, user_id)

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")

    def _determine_event_type(
        self, request_info: Dict[str, Any], response_info: Dict[str, Any]
    ) -> AuditEventType:
        """イベントタイプを決定"""
        try:
            method = request_info.get("method", "")
            path = request_info.get("path", "")

            # 認証関連
            if "/auth/login" in path:
                return AuditEventType.USER_LOGIN
            elif "/auth/logout" in path:
                return AuditEventType.USER_LOGOUT
            elif "/auth/register" in path:
                return AuditEventType.USER_REGISTRATION

            # ユーザー管理
            elif "/users/" in path:
                if method in ["PUT", "PATCH"]:
                    return AuditEventType.USER_UPDATE
                elif method == "DELETE":
                    return AuditEventType.USER_DELETE
                else:
                    return AuditEventType.DATA_ACCESS

            # データ操作
            elif method in ["POST", "PUT", "PATCH"]:
                return AuditEventType.DATA_MODIFICATION
            elif method == "DELETE":
                return AuditEventType.DATA_DELETION
            elif method == "GET":
                return AuditEventType.DATA_ACCESS

            # 管理者操作
            elif "/admin/" in path:
                return AuditEventType.ADMIN_ACTION

            # 権限変更
            elif "/permissions/" in path or "/roles/" in path:
                return AuditEventType.PERMISSION_CHANGE

            # デフォルト
            else:
                return AuditEventType.DATA_ACCESS

        except Exception as e:
            logger.error(f"Error determining event type: {e}")
            return AuditEventType.DATA_ACCESS

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """ユーザーIDを抽出"""
        try:
            # 実際の実装では、認証情報からユーザーIDを取得
            # ここでは簡易的な実装
            auth_header = request.headers.get("authorization")
            if auth_header:
                # JWTトークンからユーザーIDを抽出（簡易実装）
                return "user_123"  # 仮のユーザーID

            return None

        except Exception as e:
            logger.error(f"Error extracting user ID: {e}")
            return None

    def _extract_session_id(self, request: Request) -> Optional[str]:
        """セッションIDを抽出"""
        try:
            # 実際の実装では、セッション情報からセッションIDを取得
            return request.headers.get("x-session-id")

        except Exception as e:
            logger.error(f"Error extracting session ID: {e}")
            return None

    def _extract_resource_type(self, path: str) -> Optional[str]:
        """リソースタイプを抽出"""
        try:
            if not path:
                return None

            # パスからリソースタイプを抽出
            path_parts = path.strip("/").split("/")
            if len(path_parts) >= 2:
                return path_parts[1]  # /api/users/123 -> users

            return None

        except Exception as e:
            logger.error(f"Error extracting resource type: {e}")
            return None

    def _extract_resource_id(self, path: str) -> Optional[str]:
        """リソースIDを抽出"""
        try:
            if not path:
                return None

            # パスからリソースIDを抽出
            path_parts = path.strip("/").split("/")
            if len(path_parts) >= 3:
                return path_parts[2]  # /api/users/123 -> 123

            return None

        except Exception as e:
            logger.error(f"Error extracting resource ID: {e}")
            return None

    def _extract_action(self, method: str, path: str) -> str:
        """アクションを抽出"""
        try:
            if not method or not path:
                return "unknown"

            # HTTPメソッドとパスからアクションを決定
            if method == "GET":
                return "read"
            elif method in ["POST", "PUT", "PATCH"]:
                return "write"
            elif method == "DELETE":
                return "delete"
            else:
                return "unknown"

        except Exception as e:
            logger.error(f"Error extracting action: {e}")
            return "unknown"

    def _mask_sensitive_data(self, data: Any) -> Any:
        """センシティブデータをマスク"""
        try:
            if isinstance(data, dict):
                masked_data = {}
                for key, value in data.items():
                    if any(
                        sensitive_field in key.lower()
                        for sensitive_field in self.audit_config["sensitive_fields"]
                    ):
                        masked_data[key] = "***MASKED***"
                    else:
                        masked_data[key] = self._mask_sensitive_data(value)
                return masked_data
            elif isinstance(data, list):
                return [self._mask_sensitive_data(item) for item in data]
            else:
                return data

        except Exception as e:
            logger.error(f"Error masking sensitive data: {e}")
            return data

    def update_audit_config(self, new_config: Dict[str, Any]) -> None:
        """監査設定を更新"""
        try:
            self.audit_config.update(new_config)
            logger.info("Audit middleware configuration updated")

        except Exception as e:
            logger.error(f"Error updating audit configuration: {e}")
            raise

    def get_audit_stats(self) -> Dict[str, Any]:
        """監査統計を取得"""
        try:
            return {
                "enabled": self.audit_config["enabled"],
                "audit_paths_count": len(self.audit_config["audit_paths"]),
                "exclude_paths_count": len(self.audit_config["exclude_paths"]),
                "audit_methods": self.audit_config["audit_methods"],
                "include_get_requests": self.audit_config["include_get_requests"],
                "mask_sensitive_data": self.audit_config["mask_sensitive_data"],
                "sensitive_fields_count": len(self.audit_config["sensitive_fields"]),
            }

        except Exception as e:
            logger.error(f"Error getting audit stats: {e}")
            return {}


class SelectiveAuditMiddleware(AuditMiddleware):
    """選択的監査ミドルウェア"""

    def __init__(
        self,
        app,
        audit_paths: Optional[list] = None,
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)

        if audit_paths:
            self.audit_config["audit_paths"] = audit_paths
        if exclude_paths:
            self.audit_config["exclude_paths"] = exclude_paths

    def _should_audit_request(self, request: Request) -> bool:
        """リクエストを監査すべきかチェック（選択的）"""
        try:
            if not self.audit_config["enabled"]:
                return False

            # パスをチェック
            path = request.url.path
            if any(
                path.startswith(exclude_path)
                for exclude_path in self.audit_config["exclude_paths"]
            ):
                return False

            # 監査対象パスをチェック
            if not any(
                path.startswith(audit_path)
                for audit_path in self.audit_config["audit_paths"]
            ):
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking selective audit requirement: {e}")
            return False
