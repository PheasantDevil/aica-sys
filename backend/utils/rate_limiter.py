import logging
import time
from functools import wraps
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request, status
from utils.cache import CACHE_TTL, cache_manager

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        self.default_limits = {
            "login": {"requests": 5, "window": 300},  # 5 attempts per 5 minutes
            "api": {"requests": 100, "window": 3600},  # 100 requests per hour
            "password_reset": {"requests": 3, "window": 3600},  # 3 attempts per hour
            "registration": {"requests": 3, "window": 3600},  # 3 registrations per hour
            "stripe_webhook": {
                "requests": 1000,
                "window": 60,
            },  # 1000 webhooks per minute
        }

    def get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get real IP from headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host

        # Include user agent for additional uniqueness
        user_agent = request.headers.get("User-Agent", "")
        return f"{client_ip}:{hash(user_agent) % 10000}"

    def is_rate_limited(
        self,
        identifier: str,
        limit_type: str,
        custom_limits: Optional[Dict[str, int]] = None,
    ) -> Tuple[bool, Dict[str, any]]:
        """Check if request is rate limited"""
        limits = custom_limits or self.default_limits.get(
            limit_type, {"requests": 100, "window": 3600}
        )
        requests_limit = limits["requests"]
        window_seconds = limits["window"]

        # Create cache key
        cache_key = f"rate_limit:{limit_type}:{identifier}"

        # Get current request count
        current_requests = cache_manager.get(cache_key) or 0

        # Check if limit exceeded
        if current_requests >= requests_limit:
            return True, {
                "limit_exceeded": True,
                "requests": current_requests,
                "limit": requests_limit,
                "window": window_seconds,
                "retry_after": window_seconds,
            }

        # Increment request count
        cache_manager.set(cache_key, current_requests + 1, window_seconds)

        return False, {
            "limit_exceeded": False,
            "requests": current_requests + 1,
            "limit": requests_limit,
            "window": window_seconds,
            "remaining": requests_limit - (current_requests + 1),
        }

    def get_rate_limit_info(self, identifier: str, limit_type: str) -> Dict[str, any]:
        """Get current rate limit information"""
        limits = self.default_limits.get(limit_type, {"requests": 100, "window": 3600})
        cache_key = f"rate_limit:{limit_type}:{identifier}"
        current_requests = cache_manager.get(cache_key) or 0

        return {
            "requests": current_requests,
            "limit": limits["requests"],
            "window": limits["window"],
            "remaining": max(0, limits["requests"] - current_requests),
            "reset_time": time.time() + limits["window"],
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit_type: str, custom_limits: Optional[Dict[str, int]] = None):
    """Decorator for rate limiting endpoints"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)

            # Get client identifier
            identifier = rate_limiter.get_client_identifier(request)

            # Check rate limit
            is_limited, info = rate_limiter.is_rate_limited(
                identifier, limit_type, custom_limits
            )

            if is_limited:
                logger.warning(f"Rate limit exceeded for {identifier} on {limit_type}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {info['limit']} per {info['window']} seconds",
                        "retry_after": info["retry_after"],
                        "limit_info": info,
                    },
                    headers={
                        "Retry-After": str(info["retry_after"]),
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(
                            int(time.time() + info["retry_after"])
                        ),
                    },
                )

            # Add rate limit headers to response
            response = await func(*args, **kwargs)
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(
                    int(time.time() + info["window"])
                )

            return response

        return wrapper

    return decorator


# Specific rate limit decorators
def login_rate_limit(func):
    """Rate limit for login attempts"""
    return rate_limit("login")(func)


def api_rate_limit(func):
    """Rate limit for API endpoints"""
    return rate_limit("api")(func)


def password_reset_rate_limit(func):
    """Rate limit for password reset"""
    return rate_limit("password_reset")(func)


def registration_rate_limit(func):
    """Rate limit for user registration"""
    return rate_limit("registration")(func)


def stripe_webhook_rate_limit(func):
    """Rate limit for Stripe webhooks"""
    return rate_limit("stripe_webhook")(func)


# Advanced rate limiting with sliding window
class SlidingWindowRateLimiter:
    def __init__(self):
        self.windows = {}

    def is_allowed(
        self, identifier: str, limit_type: str, requests_limit: int, window_seconds: int
    ) -> Tuple[bool, Dict[str, any]]:
        """Check if request is allowed using sliding window"""
        current_time = time.time()
        window_start = current_time - window_seconds

        # Get or create window for this identifier
        cache_key = f"sliding_window:{limit_type}:{identifier}"
        window_data = cache_manager.get(cache_key) or {
            "requests": [],
            "last_cleanup": current_time,
        }

        # Clean up old requests
        window_data["requests"] = [
            req_time for req_time in window_data["requests"] if req_time > window_start
        ]

        # Check if limit exceeded
        if len(window_data["requests"]) >= requests_limit:
            return False, {
                "allowed": False,
                "requests": len(window_data["requests"]),
                "limit": requests_limit,
                "window": window_seconds,
                "oldest_request": (
                    min(window_data["requests"]) if window_data["requests"] else None
                ),
            }

        # Add current request
        window_data["requests"].append(current_time)
        window_data["last_cleanup"] = current_time

        # Save updated window
        cache_manager.set(cache_key, window_data, window_seconds)

        return True, {
            "allowed": True,
            "requests": len(window_data["requests"]),
            "limit": requests_limit,
            "window": window_seconds,
            "remaining": requests_limit - len(window_data["requests"]),
        }


# Global sliding window rate limiter
sliding_rate_limiter = SlidingWindowRateLimiter()


# Rate limit middleware
class RateLimitMiddleware:
    def __init__(self, app, default_limits: Optional[Dict[str, Dict[str, int]]] = None):
        self.app = app
        self.default_limits = default_limits or rate_limiter.default_limits

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        identifier = rate_limiter.get_client_identifier(request)

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
        is_limited, info = rate_limiter.is_rate_limited(identifier, limit_type)

        if is_limited:
            response = HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
