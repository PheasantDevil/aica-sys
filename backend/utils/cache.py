import hashlib
import json
import logging
from functools import wraps
from typing import Any, Optional, Union

import redis

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
            self.enabled = True
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.redis_client = None
            self.enabled = False
            self._memory_cache = {}

    def _get_memory_cache(self, key: str) -> Optional[Any]:
        if key in self._memory_cache:
            return self._memory_cache[key]
        return None

    def _set_memory_cache(self, key: str, value: Any, ttl: int = 300) -> None:
        self._memory_cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return self._get_memory_cache(key)

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.enabled:
            self._set_memory_cache(key, value, ttl)
            return True

        try:
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            if key in self._memory_cache:
                del self._memory_cache[key]
            return True

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        if not self.enabled:
            keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._memory_cache[key]
            return len(keys_to_delete)

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled:
            return key in self._memory_cache

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def get_or_set(self, key: str, func, ttl: int = 300, *args, **kwargs):
        """Get value from cache or set it using function"""
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value

        value = func(*args, **kwargs)
        self.set(key, value, ttl)
        return value


# Global cache instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_result = cache_manager.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key_str}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key_str}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key_str, result, ttl)
            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    return cache_manager.delete_pattern(pattern)


# Cache TTL constants
CACHE_TTL = {
    "SHORT": 60,  # 1 minute
    "MEDIUM": 300,  # 5 minutes
    "LONG": 1800,  # 30 minutes
    "VERY_LONG": 3600,  # 1 hour
}


# Specific cache keys
class CacheKeys:
    ARTICLES = "articles"
    NEWSLETTERS = "newsletters"
    TRENDS = "trends"
    USER = "user"
    SUBSCRIPTION = "subscription"
    CONTENT = "content"

    @staticmethod
    def articles_list(filters: str) -> str:
        return f"{CacheKeys.ARTICLES}:list:{filters}"

    @staticmethod
    def article_detail(article_id: str) -> str:
        return f"{CacheKeys.ARTICLES}:detail:{article_id}"

    @staticmethod
    def newsletters_list(filters: str) -> str:
        return f"{CacheKeys.NEWSLETTERS}:list:{filters}"

    @staticmethod
    def trends_list(filters: str) -> str:
        return f"{CacheKeys.TRENDS}:list:{filters}"

    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"{CacheKeys.USER}:profile:{user_id}"

    @staticmethod
    def user_subscription(user_id: str) -> str:
        return f"{CacheKeys.SUBSCRIPTION}:user:{user_id}"
