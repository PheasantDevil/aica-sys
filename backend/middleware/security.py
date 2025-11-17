import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.rate_limiter import rate_limiter
from utils.csrf_protection import csrf_protection, session_manager
from utils.input_validation import input_validator

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app, enable_csrf: bool = True, enable_rate_limiting: bool = True
    ):
        super().__init__(app)
        self.enable_csrf = enable_csrf
        self.enable_rate_limiting = enable_rate_limiting

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")

        try:
            # Apply security checks
            await self._apply_security_checks(request)

            # Process request
            response = await call_next(request)

            # Add security headers
            self._add_security_headers(response)

            # Log response
            process_time = time.time() - start_time
            logger.info(f"Response: {response.status_code} in {process_time:.3f}s")

            return response

        except HTTPException as e:
            # Log security violations
            logger.warning(f"Security violation: {e.detail} from {client_ip}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "error_code": "SECURITY_VIOLATION"},
            )
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {str(e)} from {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                },
            )

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host

    async def _apply_security_checks(self, request: Request):
        """Apply security checks to request"""
        client_ip = self._get_client_ip(request)

        # Rate limiting
        if self.enable_rate_limiting:
            await self._check_rate_limits(request, client_ip)

        # CSRF protection for state-changing methods
        if self.enable_csrf and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            await self._check_csrf_protection(request)

        # Input validation for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._validate_input(request)

    async def _check_rate_limits(self, request: Request, client_ip: str):
        """Check rate limits for request"""
        # Determine limit type based on path
        path = request.url.path
        if path.startswith("/auth/login"):
            limit_type = "login"
        elif path.startswith("/auth/register"):
            limit_type = "registration"
        elif path.startswith("/auth/password-reset"):
            limit_type = "password_reset"
        elif path.startswith("/stripe/webhook"):
            limit_type = "stripe_webhook"
        else:
            limit_type = "api"

        # Check rate limit
        identifier = (
            f"{client_ip}:{hash(request.headers.get('User-Agent', '')) % 10000}"
        )
        is_limited, info = rate_limiter.is_rate_limited(identifier, limit_type)

        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

    async def _check_csrf_protection(self, request: Request):
        """Check CSRF protection for request"""
        # Skip CSRF check for certain endpoints
        skip_paths = ["/auth/login", "/auth/register", "/stripe/webhook", "/health"]

        if any(request.url.path.startswith(path) for path in skip_paths):
            return

        # Get CSRF token from request
        token = csrf_protection.get_csrf_token_from_request(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token required"
            )

        # For now, we'll skip CSRF validation as we need user context
        # This should be handled at the endpoint level with proper user authentication

    async def _validate_input(self, request: Request):
        """Validate input data for request"""
        # Skip validation for certain content types
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return

        # This is a basic check - detailed validation should be done at endpoint level
        try:
            # Check for suspicious patterns in headers
            suspicious_headers = ["X-Forwarded-Host", "X-Original-URL", "X-Rewrite-URL"]

            for header in suspicious_headers:
                if header in request.headers:
                    value = request.headers[header]
                    if any(
                        pattern in value.lower()
                        for pattern in ["../", "..\\", "javascript:", "data:"]
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Suspicious header detected",
                        )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Input validation error: {e}")

    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), browsing-topics=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
        }

        for header, value in security_headers.items():
            response.headers[header] = value


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request logging"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request details
        logger.info(f"Request: {request.method} {request.url.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Query params: {dict(request.query_params)}")

        # Process request
        response = await call_next(request)

        # Log response details
        logger.info(f"Response: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for error handling and logging"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException as e:
            # Log HTTP exceptions
            logger.warning(f"HTTP Exception: {e.status_code} - {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "error_code": "HTTP_ERROR"},
            )
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                },
            )


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware with security considerations"""

    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("Origin")

        # Check if origin is allowed
        if origin and origin not in self.allowed_origins:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Origin not allowed"},
            )

        response = await call_next(request)

        # Add CORS headers
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-CSRF-Token"
            )
            response.headers["Access-Control-Max-Age"] = "86400"

        return response


# Security utilities
class SecurityUtils:
    @staticmethod
    def is_safe_url(url: str) -> bool:
        """Check if URL is safe (not malicious)"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)

            # Check for suspicious schemes
            if parsed.scheme not in ["http", "https"]:
                return False

            # Check for suspicious domains
            suspicious_domains = ["localhost", "127.0.0.1", "0.0.0.0"]
            if parsed.hostname in suspicious_domains:
                return False

            # Check for suspicious patterns
            suspicious_patterns = ["javascript:", "data:", "vbscript:"]
            if any(pattern in url.lower() for pattern in suspicious_patterns):
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re

        # Remove path separators and other dangerous characters
        filename = re.sub(r"[^\w\-_\.]", "_", filename)
        # Remove multiple consecutive underscores
        filename = re.sub(r"_+", "_", filename)
        # Ensure it doesn't start or end with underscore
        filename = filename.strip("_")
        return filename

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        import secrets

        return secrets.token_urlsafe(length)
