import json
from typing import Any, Callable, Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from services.data_classification import (
    DataClassificationService,
    get_data_classification_service,
)
from utils.logging import get_logger

logger = get_logger(__name__)


class DataMaskingMiddleware(BaseHTTPMiddleware):
    """データマスキングミドルウェア"""

    def __init__(self, app):
        super().__init__(app)
        self.data_classification_service = get_data_classification_service()
        self.masking_config = self._initialize_masking_config()

    def _initialize_masking_config(self) -> Dict[str, Any]:
        """マスキング設定を初期化"""
        return {
            # エンドポイント別のマスキング設定
            "endpoints": {
                "/api/users/": {"masking_type": "partial", "enabled": True},
                "/api/auth/": {"masking_type": "full", "enabled": True},
                "/api/subscriptions/": {"masking_type": "partial", "enabled": True},
                "/api/payments/": {"masking_type": "full", "enabled": True},
                "/api/monitoring/": {"masking_type": "partial", "enabled": True},
            },
            # フィールド別のマスキング設定
            "fields": {
                "email": {"masking_type": "partial", "pattern": r"(\w{2})\w+@(\w+)"},
                "phone": {"masking_type": "partial", "pattern": r"(\d{3})\d{3}(\d{4})"},
                "ssn": {"masking_type": "full", "pattern": r"\d{3}-\d{2}-\d{4}"},
                "credit_card": {
                    "masking_type": "full",
                    "pattern": r"\d{4}-\d{4}-\d{4}-\d{4}",
                },
                "password": {"masking_type": "full", "pattern": r".+"},
                "api_key": {"masking_type": "partial", "pattern": r"(\w{4})\w+(\w{4})"},
            },
            # ロール別のマスキング設定
            "roles": {
                "admin": {"masking_type": "none", "enabled": False},
                "user": {"masking_type": "partial", "enabled": True},
                "guest": {"masking_type": "full", "enabled": True},
            },
            # デフォルト設定
            "default": {"masking_type": "partial", "enabled": True},
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """リクエストを処理し、レスポンスデータをマスキング"""
        try:
            # リクエストを処理
            response = await call_next(request)

            # マスキングが必要かチェック
            if not self._should_mask_response(request, response):
                return response

            # レスポンスデータをマスキング
            masked_response = await self._mask_response_data(request, response)

            return masked_response

        except Exception as e:
            logger.error(f"Error in data masking middleware: {e}")
            return response

    def _should_mask_response(self, request: Request, response: Response) -> bool:
        """レスポンスをマスキングすべきかチェック"""
        try:
            # 成功レスポンスのみマスキング
            if response.status_code >= 400:
                return False

            # JSONレスポンスのみマスキング
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return False

            # エンドポイント設定をチェック
            path = request.url.path
            endpoint_config = self._get_endpoint_config(path)

            return endpoint_config.get("enabled", True)

        except Exception as e:
            logger.error(f"Error checking masking requirement: {e}")
            return False

    def _get_endpoint_config(self, path: str) -> Dict[str, Any]:
        """エンドポイント設定を取得"""
        for endpoint_pattern, config in self.masking_config["endpoints"].items():
            if path.startswith(endpoint_pattern):
                return config

        return self.masking_config["default"]

    async def _mask_response_data(
        self, request: Request, response: Response
    ) -> Response:
        """レスポンスデータをマスキング"""
        try:
            # レスポンスボディを取得
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # JSONデータをパース
            try:
                data = json.loads(response_body.decode("utf-8"))
            except json.JSONDecodeError:
                # JSONでない場合はそのまま返す
                return response

            # データをマスキング
            masked_data = self._mask_data_recursive(data, request)

            # マスキングされたデータをJSONに変換
            masked_json = json.dumps(masked_data, ensure_ascii=False)

            # 新しいレスポンスを作成
            from fastapi.responses import Response as FastAPIResponse

            return FastAPIResponse(
                content=masked_json,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json",
            )

        except Exception as e:
            logger.error(f"Error masking response data: {e}")
            return response

    def _mask_data_recursive(self, data: Any, request: Request) -> Any:
        """データを再帰的にマスキング"""
        try:
            if isinstance(data, dict):
                return {
                    key: self._mask_data_recursive(value, request)
                    for key, value in data.items()
                }
            elif isinstance(data, list):
                return [self._mask_data_recursive(item, request) for item in data]
            elif isinstance(data, str):
                return self._mask_string_data(data, request)
            else:
                return data

        except Exception as e:
            logger.error(f"Error in recursive masking: {e}")
            return data

    def _mask_string_data(self, data: str, request: Request) -> str:
        """文字列データをマスキング"""
        try:
            # ユーザーロールを取得（実際の実装では認証情報から取得）
            user_role = self._get_user_role(request)

            # ロール別のマスキング設定を取得
            role_config = self.masking_config["roles"].get(
                user_role, self.masking_config["default"]
            )

            if not role_config.get("enabled", True):
                return data

            masking_type = role_config.get("masking_type", "partial")

            # データ分類を実行
            classification_result = self.data_classification_service.classify_data(data)

            # マスキングが必要な場合のみマスキング
            if classification_result["masking_required"]:
                return self.data_classification_service.mask_data(data, masking_type)

            return data

        except Exception as e:
            logger.error(f"Error masking string data: {e}")
            return data

    def _get_user_role(self, request: Request) -> str:
        """ユーザーロールを取得"""
        try:
            # 実際の実装では、認証情報からロールを取得
            # ここでは簡易的な実装
            auth_header = request.headers.get("authorization")
            if auth_header and "admin" in auth_header.lower():
                return "admin"
            elif auth_header:
                return "user"
            else:
                return "guest"

        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return "guest"

    def _mask_field_by_name(
        self, field_name: str, field_value: str, masking_type: str = "partial"
    ) -> str:
        """フィールド名に基づいてマスキング"""
        try:
            field_config = self.masking_config["fields"].get(field_name)
            if not field_config:
                return field_value

            field_masking_type = field_config.get("masking_type", masking_type)
            pattern = field_config.get("pattern")

            if pattern:
                import re

                if field_masking_type == "full":
                    return re.sub(pattern, lambda m: "*" * len(m.group()), field_value)
                elif field_masking_type == "partial":
                    return re.sub(
                        pattern,
                        lambda m: (
                            m.group(1) + "*" * (len(m.group()) - 2) + m.group(2)
                            if len(m.groups()) >= 2
                            else "*" * len(m.group())
                        ),
                        field_value,
                    )

            return field_value

        except Exception as e:
            logger.error(f"Error masking field by name: {e}")
            return field_value

    def update_masking_config(self, new_config: Dict[str, Any]) -> None:
        """マスキング設定を更新"""
        try:
            self.masking_config.update(new_config)
            logger.info("Data masking configuration updated")

        except Exception as e:
            logger.error(f"Error updating masking configuration: {e}")
            raise

    def get_masking_stats(self) -> Dict[str, Any]:
        """マスキング統計を取得"""
        try:
            return {
                "endpoints_configured": len(self.masking_config["endpoints"]),
                "fields_configured": len(self.masking_config["fields"]),
                "roles_configured": len(self.masking_config["roles"]),
                "default_masking_type": self.masking_config["default"]["masking_type"],
                "default_enabled": self.masking_config["default"]["enabled"],
            }

        except Exception as e:
            logger.error(f"Error getting masking stats: {e}")
            return {}


class SelectiveDataMaskingMiddleware(DataMaskingMiddleware):
    """選択的データマスキングミドルウェア"""

    def __init__(
        self,
        app,
        mask_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.mask_fields = mask_fields or []
        self.exclude_fields = exclude_fields or []

    def _should_mask_field(self, field_name: str) -> bool:
        """フィールドをマスキングすべきかチェック"""
        # 除外フィールドに含まれている場合はマスキングしない
        if field_name in self.exclude_fields:
            return False

        # マスキングフィールドが指定されている場合は、そのフィールドのみマスキング
        if self.mask_fields:
            return field_name in self.mask_fields

        # デフォルトの動作
        return True

    def _mask_data_recursive(
        self, data: Any, request: Request, field_name: str = ""
    ) -> Any:
        """データを再帰的にマスキング（フィールド名を考慮）"""
        try:
            if isinstance(data, dict):
                masked_dict = {}
                for key, value in data.items():
                    current_field = f"{field_name}.{key}" if field_name else key
                    if self._should_mask_field(current_field):
                        masked_dict[key] = self._mask_data_recursive(
                            value, request, current_field
                        )
                    else:
                        masked_dict[key] = value
                return masked_dict
            elif isinstance(data, list):
                return [
                    self._mask_data_recursive(item, request, field_name)
                    for item in data
                ]
            elif isinstance(data, str):
                if self._should_mask_field(field_name):
                    return self._mask_string_data(data, request)
                else:
                    return data
            else:
                return data

        except Exception as e:
            logger.error(f"Error in selective recursive masking: {e}")
            return data
