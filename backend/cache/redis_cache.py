"""
Redis Cache Implementation
高性能なキャッシュシステムの実装
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Union, List, Dict
from datetime import datetime, timedelta
import redis
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis キャッシュクラス"""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 6379, 
                 db: int = 0,
                 password: Optional[str] = None,
                 decode_responses: bool = True):
        """Redis キャッシュの初期化"""
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # 接続テスト
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _serialize(self, data: Any) -> str:
        """データのシリアライズ"""
        try:
            return json.dumps(data, default=str)
        except (TypeError, ValueError):
            return pickle.dumps(data).hex()
    
    def _deserialize(self, data: str) -> Any:
        """データのデシリアライズ"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            try:
                return pickle.loads(bytes.fromhex(data))
            except (ValueError, pickle.PickleError):
                return data
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """キャッシュキーの生成"""
        return f"{namespace}:{key}"
    
    def set(self, 
            key: str, 
            value: Any, 
            expire: Optional[int] = None,
            namespace: str = "default") -> bool:
        """キャッシュに値を設定"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key, namespace)
            serialized_value = self._serialize(value)
            
            if expire:
                result = self.redis_client.setex(cache_key, expire, serialized_value)
            else:
                result = self.redis_client.set(cache_key, serialized_value)
            
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """キャッシュから値を取得"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_key(key, namespace)
            value = self.redis_client.get(cache_key)
            
            if value is None:
                return None
            
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """キャッシュから値を削除"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key, namespace)
            result = self.redis_client.delete(cache_key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    def exists(self, key: str, namespace: str = "default") -> bool:
        """キャッシュキーの存在確認"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key, namespace)
            return bool(self.redis_client.exists(cache_key))
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int, namespace: str = "default") -> bool:
        """キャッシュキーの有効期限設定"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key, namespace)
            return bool(self.redis_client.expire(cache_key, seconds))
        except Exception as e:
            logger.error(f"Failed to set expiry for cache key {key}: {e}")
            return False
    
    def ttl(self, key: str, namespace: str = "default") -> int:
        """キャッシュキーの残り有効期限取得"""
        if not self.redis_client:
            return -1
        
        try:
            cache_key = self._generate_key(key, namespace)
            return self.redis_client.ttl(cache_key)
        except Exception as e:
            logger.error(f"Failed to get TTL for cache key {key}: {e}")
            return -1
    
    def clear_namespace(self, namespace: str = "default") -> bool:
        """名前空間内の全キーを削除"""
        if not self.redis_client:
            return False
        
        try:
            pattern = f"{namespace}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計情報の取得"""
        if not self.redis_client:
            return {}
        
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """ヒット率の計算"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# グローバルキャッシュインスタンス
cache = RedisCache(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    password=os.getenv("REDIS_PASSWORD"),
)

# デコレータ関数
def cache_result(expire: int = 300, namespace: str = "api"):
    """関数の結果をキャッシュするデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # キャッシュキーの生成
            key_data = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            key_hash = hashlib.md5(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()
            
            # キャッシュから取得を試行
            cached_result = cache.get(key_hash, namespace)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # 関数を実行して結果をキャッシュ
            result = func(*args, **kwargs)
            cache.set(key_hash, result, expire, namespace)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

# キャッシュ管理関数
def invalidate_pattern(pattern: str, namespace: str = "api") -> bool:
    """パターンに一致するキーを無効化"""
    if not cache.redis_client:
        return False
    
    try:
        full_pattern = f"{namespace}:{pattern}"
        keys = cache.redis_client.keys(full_pattern)
        if keys:
            return bool(cache.redis_client.delete(*keys))
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate pattern {pattern}: {e}")
        return False

def warm_cache(data: Dict[str, Any], namespace: str = "api") -> bool:
    """キャッシュのウォームアップ"""
    try:
        for key, value in data.items():
            cache.set(key, value, namespace=namespace)
        return True
    except Exception as e:
        logger.error(f"Failed to warm cache: {e}")
        return False
