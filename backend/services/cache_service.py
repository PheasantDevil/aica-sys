"""
Cache Service for AICA-SyS
Phase 7-2: Cache strategy implementation
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based cache service with advanced features"""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))

        # Redis connection pool
        self.pool = redis.ConnectionPool.from_url(
            self.redis_url,
            db=self.redis_db,
            password=self.redis_password,
            max_connections=self.max_connections,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
        )

        self.redis = redis.Redis(connection_pool=self.pool)

        # Cache key prefixes
        self.prefixes = {
            "user": "user",
            "article": "article",
            "articles": "articles",
            "trend": "trend",
            "trends": "trends",
            "newsletter": "newsletter",
            "newsletters": "newsletters",
            "session": "session",
            "auth": "auth",
            "api": "api",
        }

        # Default TTL settings (seconds)
        self.default_ttl = {
            "user": 3600,  # 1 hour
            "article": 86400,  # 24 hours
            "articles": 1800,  # 30 minutes
            "trend": 3600,  # 1 hour
            "trends": 3600,  # 1 hour
            "newsletter": 86400,  # 24 hours
            "newsletters": 1800,  # 30 minutes
            "session": 86400,  # 24 hours
            "auth": 3600,  # 1 hour
            "api": 300,  # 5 minutes
        }

    def _get_key(self, prefix: str, *args: str) -> str:
        """Generate cache key with prefix"""
        return f"{self.prefixes.get(prefix, prefix)}:{':'.join(args)}"

    def _serialize(self, data: Any) -> str:
        """Serialize data for storage"""
        if isinstance(data, (str, int, float, bool)):
            return str(data)
        return json.dumps(data, default=str, ensure_ascii=False)

    def _deserialize(self, data: str) -> Any:
        """Deserialize data from storage"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            data = self.redis.get(key)
            if data is None:
                return None
            return self._deserialize(data.decode("utf-8"))
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = self._serialize(value)
            if ttl is None:
                ttl = self.default_ttl.get(key.split(":")[0], 300)

            result = self.redis.setex(key, ttl, serialized_value)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = self.redis.delete(key)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis.exists(key))
        except RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        try:
            return bool(self.redis.expire(key, ttl))
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get TTL for key"""
        try:
            return self.redis.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -1

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        try:
            return self.redis.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Redis INCRBY error for key {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement numeric value"""
        try:
            return self.redis.decrby(key, amount)
        except RedisError as e:
            logger.error(f"Redis DECRBY error for key {key}: {e}")
            return None

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            if not keys:
                return {}

            values = self.redis.mget(keys)
            result = {}

            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value.decode("utf-8"))
                else:
                    result[key] = None

            return result
        except RedisError as e:
            logger.error(f"Redis MGET error for keys {keys}: {e}")
            return {}

    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        try:
            if not mapping:
                return True

            # Serialize values
            serialized_mapping = {
                key: self._serialize(value) for key, value in mapping.items()
            }

            # Set values
            result = self.redis.mset(serialized_mapping)

            # Set TTL for each key
            if ttl is not None:
                for key in mapping.keys():
                    self.redis.expire(key, ttl)

            return bool(result)
        except RedisError as e:
            logger.error(f"Redis MSET error for mapping {mapping}: {e}")
            return False

    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache"""
        try:
            if not keys:
                return 0
            return self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Redis KEYS/DELETE error for pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                "hit_rate": self._calculate_hit_rate(info),
            }
        except RedisError as e:
            logger.error(f"Redis INFO error: {e}")
            return {}

    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses

        if total == 0:
            return 0.0

        return (hits / total) * 100

    def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        try:
            # Test basic operations
            test_key = "health_check_test"
            test_value = "ok"

            # Test set
            set_result = self.set(test_key, test_value, 10)
            if not set_result:
                return {"status": "unhealthy", "error": "SET operation failed"}

            # Test get
            get_result = self.get(test_key)
            if get_result != test_value:
                return {"status": "unhealthy", "error": "GET operation failed"}

            # Test delete
            delete_result = self.delete(test_key)
            if not delete_result:
                return {"status": "unhealthy", "error": "DELETE operation failed"}

            # Get stats
            stats = self.get_stats()

            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "stats": stats,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global cache service instance
cache_service = CacheService()


# Convenience functions
def get_cache() -> CacheService:
    """Get cache service instance"""
    return cache_service


def cache_key(prefix: str, *args: str) -> str:
    """Generate cache key"""
    return cache_service._get_key(prefix, *args)


def cache_get(key: str) -> Optional[Any]:
    """Get from cache"""
    return cache_service.get(key)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set in cache"""
    return cache_service.set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete from cache"""
    return cache_service.delete(key)


def cache_clear_pattern(pattern: str) -> int:
    """Clear cache pattern"""
    return cache_service.clear_pattern(pattern)
