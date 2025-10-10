"""
Response Optimizer for AICA-SyS
Phase 7-3: API response optimization
"""

import gzip
import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class OptimizedResponse(BaseModel):
    """最適化されたレスポンスのベースモデル"""
    success: bool = True
    data: Any = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class PaginatedResponse(OptimizedResponse):
    """ページネーション付きレスポンス"""
    pagination: Dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(OptimizedResponse):
    """エラーレスポンス"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ResponseOptimizer:
    """レスポンス最適化クラス"""
    
    def __init__(self):
        self.compression_threshold = 1024  # 1KB以上で圧縮
        self.max_response_size = 10 * 1024 * 1024  # 10MB
    
    def create_optimized_response(
        self,
        data: Any,
        status_code: int = 200,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
        compress: bool = True
    ) -> JSONResponse:
        """最適化されたレスポンスを作成"""
        try:
            # レスポンスデータを作成
            response_data = OptimizedResponse(
                success=True,
                data=data,
                message=message,
                request_id=request_id
            )
            
            # JSONにシリアライズ
            json_data = response_data.model_dump_json()
            
            # サイズチェック
            if len(json_data.encode('utf-8')) > self.max_response_size:
                logger.warning(f"Response size exceeds limit: {len(json_data)} bytes")
                return self._create_error_response(
                    "Response too large",
                    413,
                    request_id
                )
            
            # 圧縮の適用
            if compress and len(json_data) > self.compression_threshold:
                compressed_data = gzip.compress(json_data.encode('utf-8'))
                response = Response(
                    content=compressed_data,
                    status_code=status_code,
                    media_type="application/json",
                    headers={
                        "Content-Encoding": "gzip",
                        "Content-Length": str(len(compressed_data)),
                        "X-Response-Time": str(datetime.utcnow().timestamp()),
                        "X-Request-ID": request_id or "unknown"
                    }
                )
            else:
                response = JSONResponse(
                    content=response_data.model_dump(),
                    status_code=status_code,
                    headers={
                        "X-Response-Time": str(datetime.utcnow().timestamp()),
                        "X-Request-ID": request_id or "unknown"
                    }
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating optimized response: {e}")
            return self._create_error_response(
                "Internal server error",
                500,
                request_id
            )
    
    def create_paginated_response(
        self,
        items: List[Any],
        total: int,
        page: int,
        per_page: int,
        status_code: int = 200,
        message: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """ページネーション付きレスポンスを作成"""
        try:
            # ページネーション情報を計算
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            pagination_info = {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None
            }
            
            # レスポンスデータを作成
            response_data = PaginatedResponse(
                success=True,
                data=items,
                message=message,
                request_id=request_id,
                pagination=pagination_info
            )
            
            return JSONResponse(
                content=response_data.model_dump(),
                status_code=status_code,
                headers={
                    "X-Response-Time": str(datetime.utcnow().timestamp()),
                    "X-Request-ID": request_id or "unknown"
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating paginated response: {e}")
            return self._create_error_response(
                "Internal server error",
                500,
                request_id
            )
    
    def create_error_response(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """エラーレスポンスを作成"""
        return self._create_error_response(
            message, status_code, error_code, details, request_id
        )
    
    def _create_error_response(
        self,
        message: str,
        status_code: int,
        request_id: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """内部エラーレスポンス作成"""
        error_data = ErrorResponse(
            success=False,
            data=None,
            message=message,
            request_id=request_id,
            error_code=error_code,
            details=details
        )
        
        return JSONResponse(
            content=error_data.model_dump(),
            status_code=status_code,
            headers={
                "X-Response-Time": str(datetime.utcnow().timestamp()),
                "X-Request-ID": request_id or "unknown"
            }
        )
    
    def optimize_data_structure(self, data: Any) -> Any:
        """データ構造を最適化"""
        if isinstance(data, list):
            return [self.optimize_data_structure(item) for item in data]
        elif isinstance(data, dict):
            # 不要なフィールドを削除
            optimized = {}
            for key, value in data.items():
                if value is not None and value != "":
                    optimized[key] = self.optimize_data_structure(value)
            return optimized
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
    
    def create_etag(self, data: Any) -> str:
        """ETagを生成"""
        try:
            json_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(json_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error creating ETag: {e}")
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def check_etag_match(self, request: Request, etag: str) -> bool:
        """ETagの一致をチェック"""
        if_none_match = request.headers.get("if-none-match")
        return if_none_match == etag
    
    def create_conditional_response(
        self,
        data: Any,
        etag: str,
        request: Request,
        status_code: int = 200,
        message: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Union[JSONResponse, Response]:
        """条件付きレスポンスを作成"""
        if self.check_etag_match(request, etag):
            return Response(
                status_code=304,
                headers={
                    "ETag": etag,
                    "X-Request-ID": request_id or "unknown"
                }
            )
        
        response = self.create_optimized_response(
            data, status_code, message, request_id
        )
        response.headers["ETag"] = etag
        return response

# グローバルインスタンス
response_optimizer = ResponseOptimizer()

# 便利な関数
def create_success_response(
    data: Any,
    status_code: int = 200,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """成功レスポンスを作成"""
    return response_optimizer.create_optimized_response(
        data, status_code, message, request_id
    )

def create_error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """エラーレスポンスを作成"""
    return response_optimizer.create_error_response(
        message, status_code, error_code, details, request_id
    )

def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
    status_code: int = 200,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """ページネーション付きレスポンスを作成"""
    return response_optimizer.create_paginated_response(
        items, total, page, per_page, status_code, message, request_id
    )

def optimize_data(data: Any) -> Any:
    """データを最適化"""
    return response_optimizer.optimize_data_structure(data)

def create_etag(data: Any) -> str:
    """ETagを生成"""
    return response_optimizer.create_etag(data)

def create_conditional_response(
    data: Any,
    etag: str,
    request: Request,
    status_code: int = 200,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> Union[JSONResponse, Response]:
    """条件付きレスポンスを作成"""
    return response_optimizer.create_conditional_response(
        data, etag, request, status_code, message, request_id
    )
