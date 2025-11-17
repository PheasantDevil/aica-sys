import hashlib
import hmac
import logging
import secrets
import time
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from utils.cache import CACHE_TTL, cache_manager
from utils.jwt_auth import User, get_current_user

logger = logging.getLogger(__name__)


class CSRFProtection:
    def __init__(self):
        self.secret_key = secrets.token_urlsafe(32)
        self.token_expiry = 3600  # 1 hour
        self.header_name = "X-CSRF-Token"
        self.cookie_name = "csrf_token"

    def generate_csrf_token(
        self, user_id: str, session_id: Optional[str] = None
    ) -> str:
        """Generate CSRF token for user"""
        try:
            # Create token data
            timestamp = str(int(time.time()))
            nonce = secrets.token_urlsafe(16)

            # Create token payload
            payload = f"{user_id}:{session_id or 'default'}:{timestamp}:{nonce}"

            # Sign the token
            signature = hmac.new(
                self.secret_key.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            # Combine payload and signature
            token = f"{payload}:{signature}"

            # Store token in cache for validation
            cache_key = f"csrf_token:{user_id}:{session_id or 'default'}"
            cache_manager.set(
                cache_key,
                {"token": token, "timestamp": timestamp, "nonce": nonce},
                self.token_expiry,
            )

            return token
        except Exception as e:
            logger.error(f"CSRF token generation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="CSRF token generation failed",
            )

    def validate_csrf_token(
        self, token: str, user_id: str, session_id: Optional[str] = None
    ) -> bool:
        """Validate CSRF token"""
        try:
            if not token:
                return False

            # Split token into parts
            parts = token.split(":")
            if len(parts) != 5:
                return False

            token_user_id, token_session_id, timestamp, nonce, signature = parts

            # Verify user ID and session ID
            if token_user_id != user_id or token_session_id != (
                session_id or "default"
            ):
                return False

            # Check token age
            token_time = int(timestamp)
            if time.time() - token_time > self.token_expiry:
                return False

            # Verify signature
            payload = f"{token_user_id}:{token_session_id}:{timestamp}:{nonce}"
            expected_signature = hmac.new(
                self.secret_key.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return False

            # Check if token exists in cache
            cache_key = f"csrf_token:{user_id}:{session_id or 'default'}"
            cached_token = cache_manager.get(cache_key)

            if not cached_token or cached_token.get("token") != token:
                return False

            return True
        except Exception as e:
            logger.error(f"CSRF token validation error: {e}")
            return False

    def get_csrf_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request"""
        # Try header first
        token = request.headers.get(self.header_name)
        if token:
            return token

        # Try cookie
        token = request.cookies.get(self.cookie_name)
        if token:
            return token

        return None

    def require_csrf_token(self, user: User = Depends(get_current_user)):
        """Dependency to require CSRF token validation"""

        def csrf_validator(request: Request):
            token = self.get_csrf_token_from_request(request)
            session_id = request.headers.get("X-Session-ID")

            if not self.validate_csrf_token(token, str(user.id), session_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or missing CSRF token",
                )

            return True

        return csrf_validator

    def invalidate_csrf_token(self, user_id: str, session_id: Optional[str] = None):
        """Invalidate CSRF token for user"""
        cache_key = f"csrf_token:{user_id}:{session_id or 'default'}"
        cache_manager.delete(cache_key)

    def invalidate_all_csrf_tokens(self, user_id: str):
        """Invalidate all CSRF tokens for user"""
        pattern = f"csrf_token:{user_id}:*"
        cache_manager.delete_pattern(pattern)


# Global CSRF protection instance
csrf_protection = CSRFProtection()


# CSRF protection decorator
def csrf_protect(func):
    """Decorator for CSRF protection"""

    async def wrapper(*args, **kwargs):
        # Find request and user in arguments
        request = None
        user = None

        for arg in args:
            if isinstance(arg, Request):
                request = arg
            elif isinstance(arg, User):
                user = arg

        if not request or not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="CSRF protection requires request and user",
            )

        # Validate CSRF token
        token = csrf_protection.get_csrf_token_from_request(request)
        session_id = request.headers.get("X-Session-ID")

        if not csrf_protection.validate_csrf_token(token, str(user.id), session_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing CSRF token",
            )

        return await func(*args, **kwargs)

    return wrapper


# CSRF token endpoint
async def get_csrf_token(user: User = Depends(get_current_user)) -> Dict[str, str]:
    """Get CSRF token for authenticated user"""
    token = csrf_protection.generate_csrf_token(str(user.id))
    return {
        "csrf_token": token,
        "header_name": csrf_protection.header_name,
        "expires_in": csrf_protection.token_expiry,
    }


# Session management for CSRF
class SessionManager:
    def __init__(self):
        self.session_expiry = 3600  # 1 hour

    def create_session(self, user_id: str) -> str:
        """Create new session for user"""
        session_id = secrets.token_urlsafe(32)
        cache_key = f"session:{user_id}:{session_id}"

        session_data = {
            "user_id": user_id,
            "created_at": time.time(),
            "last_activity": time.time(),
            "csrf_token": csrf_protection.generate_csrf_token(user_id, session_id),
        }

        cache_manager.set(cache_key, session_data, self.session_expiry)
        return session_id

    def validate_session(self, user_id: str, session_id: str) -> bool:
        """Validate session"""
        cache_key = f"session:{user_id}:{session_id}"
        session_data = cache_manager.get(cache_key)

        if not session_data:
            return False

        # Check if session is expired
        if time.time() - session_data["last_activity"] > self.session_expiry:
            cache_manager.delete(cache_key)
            return False

        # Update last activity
        session_data["last_activity"] = time.time()
        cache_manager.set(cache_key, session_data, self.session_expiry)

        return True

    def invalidate_session(self, user_id: str, session_id: str):
        """Invalidate specific session"""
        cache_key = f"session:{user_id}:{session_id}"
        cache_manager.delete(cache_key)

    def invalidate_all_sessions(self, user_id: str):
        """Invalidate all sessions for user"""
        pattern = f"session:{user_id}:*"
        cache_manager.delete_pattern(pattern)


# Global session manager
session_manager = SessionManager()


# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add security headers
                security_headers = [
                    (b"x-frame-options", b"DENY"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (
                        b"permissions-policy",
                        b"camera=(), microphone=(), geolocation=()",
                    ),
                    (
                        b"strict-transport-security",
                        b"max-age=31536000; includeSubDomains",
                    ),
                ]

                # Add CSRF token to response headers
                if "csrf_token" in message.get("headers", {}):
                    security_headers.append(
                        (b"x-csrf-token", message["headers"]["csrf_token"].encode())
                    )

                headers.extend(security_headers)
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)
