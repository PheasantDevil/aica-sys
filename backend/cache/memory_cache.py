"""
Memory Cache Implementation
Redisが利用できない場合のフォールバック用メモリキャッシュ
"""

import time
import threading
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class MemoryCache:
    """メモリキャッシュクラス（LRU実装）"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """メモリキャッシュの初期化"""
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0,
            "deletes": 0,
        }

    def _is_expired(self, timestamp: float) -> bool:
        """有効期限の確認"""
        return time.time() > timestamp

    def _cleanup_expired(self):
        """期限切れのエントリを削除"""
        current_time = time.time()
        expired_keys = []

        for key, (_, timestamp) in self._cache.items():
            if current_time > timestamp:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
            self._stats["evictions"] += 1

    def _evict_lru(self):
        """LRUエントリを削除"""
        if self._cache:
            # 最も古いエントリを削除
            key, _ = self._cache.popitem(last=False)
            self._stats["evictions"] += 1
            logger.debug(f"Evicted LRU key: {key}")

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """キャッシュに値を設定"""
        with self._lock:
            try:
                # 期限切れエントリのクリーンアップ
                self._cleanup_expired()

                # サイズ制限の確認
                if len(self._cache) >= self.max_size and key not in self._cache:
                    self._evict_lru()

                # 有効期限の設定
                expire_time = time.time() + (ttl or self.default_ttl)

                # 既存のキーがある場合は削除してから追加
                if key in self._cache:
                    del self._cache[key]

                # 新しいエントリを追加
                self._cache[key] = (value, expire_time)
                self._stats["sets"] += 1

                logger.debug(f"Set cache key: {key}")
                return True
            except Exception as e:
                logger.error(f"Failed to set cache key {key}: {e}")
                return False

    def get(self, key: str) -> Optional[Any]:
        """キャッシュから値を取得"""
        with self._lock:
            try:
                if key not in self._cache:
                    self._stats["misses"] += 1
                    return None

                value, timestamp = self._cache[key]

                # 有効期限の確認
                if self._is_expired(timestamp):
                    del self._cache[key]
                    self._stats["misses"] += 1
                    self._stats["evictions"] += 1
                    return None

                # LRUの更新（アクセスされたエントリを最後に移動）
                self._cache.move_to_end(key)
                self._stats["hits"] += 1

                logger.debug(f"Cache hit for key: {key}")
                return value
            except Exception as e:
                logger.error(f"Failed to get cache key {key}: {e}")
                self._stats["misses"] += 1
                return None

    def delete(self, key: str) -> bool:
        """キャッシュから値を削除"""
        with self._lock:
            try:
                if key in self._cache:
                    del self._cache[key]
                    self._stats["deletes"] += 1
                    logger.debug(f"Deleted cache key: {key}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to delete cache key {key}: {e}")
                return False

    def exists(self, key: str) -> bool:
        """キャッシュキーの存在確認"""
        with self._lock:
            if key not in self._cache:
                return False

            _, timestamp = self._cache[key]
            if self._is_expired(timestamp):
                del self._cache[key]
                return False

            return True

    def clear(self) -> bool:
        """全キャッシュをクリア"""
        with self._lock:
            try:
                self._cache.clear()
                logger.info("Cache cleared")
                return True
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                return False

    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計情報の取得"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                (self._stats["hits"] / total_requests * 100)
                if total_requests > 0
                else 0.0
            )

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "evictions": self._stats["evictions"],
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
            }

    def get_keys(self) -> list:
        """キャッシュキーの一覧取得"""
        with self._lock:
            current_time = time.time()
            valid_keys = []

            for key, (_, timestamp) in self._cache.items():
                if current_time <= timestamp:
                    valid_keys.append(key)
                else:
                    # 期限切れのキーを削除
                    del self._cache[key]
                    self._stats["evictions"] += 1

            return valid_keys


# グローバルメモリキャッシュインスタンス
memory_cache = MemoryCache(max_size=1000, default_ttl=300)


# デコレータ関数
def memory_cache_result(ttl: int = 300):
    """関数の結果をメモリキャッシュするデコレータ"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # キャッシュキーの生成
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # キャッシュから取得を試行
            cached_result = memory_cache.get(key)
            if cached_result is not None:
                return cached_result

            # 関数を実行して結果をキャッシュ
            result = func(*args, **kwargs)
            memory_cache.set(key, result, ttl)

            return result

        return wrapper

    return decorator
