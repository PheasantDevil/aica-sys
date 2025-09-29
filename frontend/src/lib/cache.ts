'use client';

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class MemoryCache {
  private cache = new Map<string, CacheItem<any>>();
  private maxSize: number;

  constructor(maxSize = 100) {
    this.maxSize = maxSize;
  }

  set<T>(key: string, data: T, ttl = 5 * 60 * 1000): void {
    // Remove oldest items if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);

    if (!item) {
      return null;
    }

    // Check if item has expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    const item = this.cache.get(key);
    if (!item) return false;

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }

  // Clean up expired items
  cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];

    this.cache.forEach((item, key) => {
      if (now - item.timestamp > item.ttl) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
  }
}

// Global cache instance
export const memoryCache = new MemoryCache();

// Cache utilities for different data types
export const cacheKeys = {
  articles: (filters: string) => `articles:${filters}`,
  newsletters: (filters: string) => `newsletters:${filters}`,
  trends: (filters: string) => `trends:${filters}`,
  user: (userId: string) => `user:${userId}`,
  subscription: (userId: string) => `subscription:${userId}`,
  content: (type: string, id: string) => `content:${type}:${id}`,
} as const;

// Cache TTL constants (in milliseconds)
export const CACHE_TTL = {
  SHORT: 5 * 60 * 1000, // 5 minutes
  MEDIUM: 30 * 60 * 1000, // 30 minutes
  LONG: 2 * 60 * 60 * 1000, // 2 hours
  VERY_LONG: 24 * 60 * 60 * 1000, // 24 hours
} as const;

// Cache wrapper for API calls
export function withCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = CACHE_TTL.MEDIUM
): Promise<T> {
  return new Promise((resolve, reject) => {
    // Check cache first
    const cached = memoryCache.get<T>(key);
    if (cached !== null) {
      resolve(cached);
      return;
    }

    // Fetch data and cache it
    fetcher()
      .then(data => {
        memoryCache.set(key, data, ttl);
        resolve(data);
      })
      .catch(reject);
  });
}

// Cache invalidation utilities
export function invalidateCache(pattern: string): void {
  const regex = new RegExp(pattern);
  const keysToDelete: string[] = [];

  memoryCache['cache'].forEach((_, key) => {
    if (regex.test(key)) {
      keysToDelete.push(key);
    }
  });

  keysToDelete.forEach(key => memoryCache.delete(key));
}

export function invalidateUserCache(userId: string): void {
  invalidateCache(`user:${userId}`);
  invalidateCache(`subscription:${userId}`);
}

export function invalidateContentCache(): void {
  invalidateCache('articles:');
  invalidateCache('newsletters:');
  invalidateCache('trends:');
}

// Cleanup expired items every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(
    () => {
      memoryCache.cleanup();
    },
    5 * 60 * 1000
  );
}
