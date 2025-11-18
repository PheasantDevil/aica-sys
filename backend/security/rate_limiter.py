"""
Advanced Rate Limiting System
Implements multiple rate limiting strategies for different use cases
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

import redis
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    requests: int
    window: int  # in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_limit: Optional[int] = None
    refill_rate: Optional[float] = None


class RateLimiter:
    """Advanced rate limiter with multiple strategies"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.memory_store: Dict[str, Dict[str, Any]] = {}

    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"rate_limit:{identifier}:{endpoint}"

    def _get_memory_key(self, identifier: str, endpoint: str) -> str:
        """Generate memory key for rate limiting"""
        return f"{identifier}:{endpoint}"

    async def _fixed_window_limit(
        self, key: str, config: RateLimitConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """Fixed window rate limiting"""
        current_time = int(time.time())
        window_start = current_time - (current_time % config.window)

        if self.redis:
            pipe = self.redis.pipeline()
            pipe.incr(f"{key}:{window_start}")
            pipe.expire(f"{key}:{window_start}", config.window)
            results = await pipe.execute()
            count = results[0]
        else:
            memory_key = f"{key}:{window_start}"
            if memory_key not in self.memory_store:
                self.memory_store[memory_key] = {
                    "count": 0,
                    "expires": current_time + config.window,
                }

            self.memory_store[memory_key]["count"] += 1
            count = self.memory_store[memory_key]["count"]

            # Clean expired entries
            self._clean_expired_entries()

        remaining = max(0, config.requests - count)
        reset_time = window_start + config.window

        return count <= config.requests, {
            "limit": config.requests,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": max(0, reset_time - current_time),
        }

    async def _sliding_window_limit(
        self, key: str, config: RateLimitConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """Sliding window rate limiting"""
        current_time = time.time()
        window_start = current_time - config.window

        if self.redis:
            # Use Redis sorted set for sliding window
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, config.window)
            results = await pipe.execute()
            count = results[1]
        else:
            memory_key = self._get_memory_key(key, "")
            if memory_key not in self.memory_store:
                self.memory_store[memory_key] = {
                    "requests": [],
                    "expires": current_time + config.window,
                }

            # Remove old requests
            self.memory_store[memory_key]["requests"] = [
                req_time
                for req_time in self.memory_store[memory_key]["requests"]
                if req_time > window_start
            ]

            # Add current request
            self.memory_store[memory_key]["requests"].append(current_time)
            count = len(self.memory_store[memory_key]["requests"])

            # Clean expired entries
            self._clean_expired_entries()

        remaining = max(0, config.requests - count)
        reset_time = int(current_time + config.window)

        return count <= config.requests, {
            "limit": config.requests,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": max(0, int(config.window - (current_time % config.window))),
        }

    async def _token_bucket_limit(
        self, key: str, config: RateLimitConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """Token bucket rate limiting"""
        if not config.burst_limit or not config.refill_rate:
            raise ValueError("Token bucket requires burst_limit and refill_rate")

        current_time = time.time()

        if self.redis:
            pipe = self.redis.pipeline()
            pipe.hmget(key, "tokens", "last_refill")
            results = await pipe.execute()

            tokens, last_refill = results[0]
            tokens = float(tokens) if tokens else config.burst_limit
            last_refill = float(last_refill) if last_refill else current_time

            # Refill tokens
            time_passed = current_time - last_refill
            tokens = min(
                config.burst_limit, tokens + (time_passed * config.refill_rate)
            )

            if tokens >= 1:
                tokens -= 1
                allowed = True
            else:
                allowed = False

            pipe.hmset(key, {"tokens": tokens, "last_refill": current_time})
            pipe.expire(key, config.window)
            await pipe.execute()
        else:
            memory_key = self._get_memory_key(key, "")
            if memory_key not in self.memory_store:
                self.memory_store[memory_key] = {
                    "tokens": config.burst_limit,
                    "last_refill": current_time,
                    "expires": current_time + config.window,
                }

            # Refill tokens
            time_passed = current_time - self.memory_store[memory_key]["last_refill"]
            self.memory_store[memory_key]["tokens"] = min(
                config.burst_limit,
                self.memory_store[memory_key]["tokens"]
                + (time_passed * config.refill_rate),
            )

            if self.memory_store[memory_key]["tokens"] >= 1:
                self.memory_store[memory_key]["tokens"] -= 1
                allowed = True
            else:
                allowed = False

            self.memory_store[memory_key]["last_refill"] = current_time
            self._clean_expired_entries()

        remaining = int(tokens) if "tokens" in locals() else 0
        reset_time = int(current_time + config.window)

        return allowed, {
            "limit": config.burst_limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": max(0, int(1 / config.refill_rate)) if not allowed else 0,
        }

    def _clean_expired_entries(self):
        """Clean expired entries from memory store"""
        current_time = time.time()
        expired_keys = [
            key
            for key, data in self.memory_store.items()
            if data.get("expires", 0) < current_time
        ]
        for key in expired_keys:
            del self.memory_store[key]

    async def check_rate_limit(
        self, identifier: str, endpoint: str, config: RateLimitConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit for identifier and endpoint"""
        key = self._get_key(identifier, endpoint)

        try:
            if config.strategy == RateLimitStrategy.FIXED_WINDOW:
                return await self._fixed_window_limit(key, config)
            elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return await self._sliding_window_limit(key, config)
            elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return await self._token_bucket_limit(key, config)
            else:
                raise ValueError(f"Unsupported strategy: {config.strategy}")
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            # Fail open - allow request if rate limiting fails
            return True, {
                "limit": config.requests,
                "remaining": config.requests,
                "reset": 0,
                "retry_after": 0,
            }


# Predefined rate limit configurations
RATE_LIMIT_CONFIGS = {
    "api": RateLimitConfig(
        requests=1000, window=3600, strategy=RateLimitStrategy.SLIDING_WINDOW  # 1 hour
    ),
    "auth": RateLimitConfig(
        requests=10, window=300, strategy=RateLimitStrategy.SLIDING_WINDOW  # 5 minutes
    ),
    "upload": RateLimitConfig(
        requests=50, window=3600, strategy=RateLimitStrategy.SLIDING_WINDOW  # 1 hour
    ),
    "search": RateLimitConfig(
        requests=200, window=3600, strategy=RateLimitStrategy.SLIDING_WINDOW  # 1 hour
    ),
    "burst": RateLimitConfig(
        requests=100,
        window=60,  # 1 minute
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        burst_limit=100,
        refill_rate=1.0,  # 1 request per second
    ),
}


class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Get identifier (user ID or IP)
        identifier = self._get_identifier(request)
        endpoint = self._get_endpoint(request)

        # Get rate limit config for endpoint
        config = self._get_config_for_endpoint(endpoint)

        if config:
            allowed, info = await self.rate_limiter.check_rate_limit(
                identifier, endpoint, config
            )

            if not allowed:
                logger.warning(f"Rate limit exceeded for {identifier} on {endpoint}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset"]),
                        "Retry-After": str(info["retry_after"]),
                    },
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])
            return response

        return await call_next(request)

    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting"""
        # Try to get user ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # Decode JWT to get user ID (simplified)
                import jwt

                payload = jwt.decode(token, options={"verify_signature": False})
                return f"user:{payload.get('sub', 'unknown')}"
            except:
                pass

        # Fall back to IP address
        return f"ip:{request.client.host}"

    def _get_endpoint(self, request: Request) -> str:
        """Get endpoint for rate limiting"""
        return f"{request.method}:{request.url.path}"

    def _get_config_for_endpoint(self, endpoint: str) -> Optional[RateLimitConfig]:
        """Get rate limit config for endpoint"""
        if endpoint.startswith("POST:/api/auth/"):
            return RATE_LIMIT_CONFIGS["auth"]
        elif endpoint.startswith("POST:/api/upload/"):
            return RATE_LIMIT_CONFIGS["upload"]
        elif endpoint.startswith("GET:/api/search/"):
            return RATE_LIMIT_CONFIGS["search"]
        elif endpoint.startswith(
            ("GET:/api/", "POST:/api/", "PUT:/api/", "DELETE:/api/")
        ):
            return RATE_LIMIT_CONFIGS["api"]
        else:
            return None


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit decorator for endpoints
def rate_limit(config_name: str):
    """Decorator for rate limiting specific endpoints"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                return await func(*args, **kwargs)

            identifier = f"ip:{request.client.host}"
            endpoint = f"{request.method}:{request.url.path}"
            config = RATE_LIMIT_CONFIGS.get(config_name)

            if config:
                allowed, info = await rate_limiter.check_rate_limit(
                    identifier, endpoint, config
                )

                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded",
                        headers={
                            "X-RateLimit-Limit": str(info["limit"]),
                            "X-RateLimit-Remaining": str(info["remaining"]),
                            "X-RateLimit-Reset": str(info["reset"]),
                            "Retry-After": str(info["retry_after"]),
                        },
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
