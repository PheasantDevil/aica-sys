"""
Cache Decorators for AICA-SyS
Phase 7-2: Cache strategy implementation
"""

import functools
import hashlib
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from services.cache_service import cache_service

logger = logging.getLogger(__name__)


def cache_result(
    expire: Optional[int] = None,
    key_prefix: str = "",
    key_func: Optional[Callable] = None,
    condition: Optional[Callable] = None,
    invalidate_on: Optional[List[str]] = None,
) -> Callable:
    """
    Cache function result decorator

    Args:
        expire: Cache expiration time in seconds
        key_prefix: Prefix for cache key
        key_func: Custom function to generate cache key
        condition: Function to determine if result should be cached
        invalidate_on: List of function names to invalidate cache on
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Execute function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)

            # Check condition
            if condition and not condition(result):
                return result

            # Cache result
            cache_service.set(cache_key, result, expire)

            return result

        # Add cache invalidation method
        wrapper.invalidate_cache = lambda *args, **kwargs: _invalidate_cache(
            func, key_prefix, *args, **kwargs
        )

        return wrapper

    return decorator


def cache_invalidate(
    key_prefix: str = "",
    key_func: Optional[Callable] = None,
    pattern: Optional[str] = None,
) -> Callable:
    """
    Cache invalidation decorator

    Args:
        key_prefix: Prefix for cache key
        key_func: Custom function to generate cache key
        pattern: Pattern to match keys for invalidation
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function first
            result = func(*args, **kwargs)

            # Invalidate cache
            if pattern:
                cache_service.clear_pattern(pattern)
            elif key_func:
                cache_key = key_func(*args, **kwargs)
                cache_service.delete(cache_key)
            else:
                cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)
                cache_service.delete(cache_key)

            logger.debug(f"Cache invalidated for function: {func.__name__}")
            return result

        return wrapper

    return decorator


def cache_async_result(
    expire: Optional[int] = None,
    key_prefix: str = "",
    key_func: Optional[Callable] = None,
    condition: Optional[Callable] = None,
) -> Callable:
    """
    Cache async function result decorator
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Execute function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)

            # Check condition
            if condition and not condition(result):
                return result

            # Cache result
            cache_service.set(cache_key, result, expire)

            return result

        # Add cache invalidation method
        wrapper.invalidate_cache = lambda *args, **kwargs: _invalidate_cache(
            func, key_prefix, *args, **kwargs
        )

        return wrapper

    return decorator


def _generate_cache_key(func: Callable, key_prefix: str, *args, **kwargs) -> str:
    """Generate cache key from function and arguments"""
    # Get function signature
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    # Create key components
    key_components = [func.__module__, func.__name__]

    if key_prefix:
        key_components.insert(0, key_prefix)

    # Add arguments to key
    for param_name, param_value in bound_args.arguments.items():
        if param_name in ["self", "cls"]:
            continue

        # Convert value to string for hashing
        if isinstance(param_value, (list, dict, set)):
            param_value = str(
                sorted(param_value) if isinstance(param_value, set) else param_value
            )
        else:
            param_value = str(param_value)

        key_components.append(f"{param_name}:{param_value}")

    # Create hash for long keys
    key_string = ":".join(key_components)
    if len(key_string) > 250:  # Redis key length limit
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        key_components = [key_components[0], key_hash]
        key_string = ":".join(key_components)

    return key_string


def _invalidate_cache(func: Callable, key_prefix: str, *args, **kwargs) -> bool:
    """Invalidate cache for function"""
    cache_key = _generate_cache_key(func, key_prefix, *args, **kwargs)
    return cache_service.delete(cache_key)


# Specialized cache decorators for common use cases


def cache_user_data(expire: int = 3600):
    """Cache user-related data"""
    return cache_result(
        expire=expire, key_prefix="user", condition=lambda result: result is not None
    )


def cache_article_data(expire: int = 86400):
    """Cache article-related data"""
    return cache_result(
        expire=expire, key_prefix="article", condition=lambda result: result is not None
    )


def cache_api_response(expire: int = 300):
    """Cache API response data"""
    return cache_result(
        expire=expire, key_prefix="api", condition=lambda result: result is not None
    )


def cache_trends_data(expire: int = 3600):
    """Cache trends data"""
    return cache_result(
        expire=expire, key_prefix="trends", condition=lambda result: result is not None
    )


def cache_newsletter_data(expire: int = 1800):
    """Cache newsletter data"""
    return cache_result(
        expire=expire,
        key_prefix="newsletters",
        condition=lambda result: result is not None,
    )


def invalidate_user_cache():
    """Invalidate all user-related cache"""
    return cache_invalidate(pattern="user:*")


def invalidate_article_cache():
    """Invalidate all article-related cache"""
    return cache_invalidate(pattern="article:*")


def invalidate_api_cache():
    """Invalidate all API-related cache"""
    return cache_invalidate(pattern="api:*")


# Cache warming utilities


def warm_cache(func: Callable, *args, **kwargs) -> Any:
    """Warm cache by calling function"""
    try:
        result = func(*args, **kwargs)
        logger.info(f"Cache warmed for function: {func.__name__}")
        return result
    except Exception as e:
        logger.error(f"Cache warming failed for function {func.__name__}: {e}")
        return None


async def warm_cache_async(func: Callable, *args, **kwargs) -> Any:
    """Warm cache by calling async function"""
    try:
        result = await func(*args, **kwargs)
        logger.info(f"Cache warmed for async function: {func.__name__}")
        return result
    except Exception as e:
        logger.error(f"Cache warming failed for async function {func.__name__}: {e}")
        return None


# Cache statistics and monitoring


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return cache_service.get_stats()


def get_cache_health() -> Dict[str, Any]:
    """Get cache health status"""
    return cache_service.health_check()


def clear_all_cache() -> int:
    """Clear all cache (use with caution)"""
    return cache_service.clear_pattern("*")


def clear_pattern_cache(pattern: str) -> int:
    """Clear cache matching pattern"""
    return cache_service.clear_pattern(pattern)
