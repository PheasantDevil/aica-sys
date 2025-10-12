'use client';

import { QueryClient } from '@tanstack/react-query';

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

// React Query configuration with cache optimization
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 3,
      refetchOnWindowFocus: false,
      refetchOnMount: false,
      refetchOnReconnect: 'always',
    },
    mutations: {
      retry: 1,
    },
  },
});

// Query key factory for consistent cache keys
export const queryKeys = {
  articles: {
    all: ['articles'] as const,
    lists: () => [...queryKeys.articles.all, 'list'] as const,
    list: (filters: Record<string, any>) =>
      [...queryKeys.articles.lists(), { filters }] as const,
    details: () => [...queryKeys.articles.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.articles.details(), id] as const,
  },
  newsletters: {
    all: ['newsletters'] as const,
    lists: () => [...queryKeys.newsletters.all, 'list'] as const,
    list: (filters: Record<string, any>) =>
      [...queryKeys.newsletters.lists(), { filters }] as const,
    details: () => [...queryKeys.newsletters.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.newsletters.details(), id] as const,
  },
  trends: {
    all: ['trends'] as const,
    lists: () => [...queryKeys.trends.all, 'list'] as const,
    list: (filters: Record<string, any>) =>
      [...queryKeys.trends.lists(), { filters }] as const,
    details: () => [...queryKeys.trends.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.trends.details(), id] as const,
  },
  user: {
    all: ['user'] as const,
    profile: (id: string) => [...queryKeys.user.all, 'profile', id] as const,
    subscription: (id: string) =>
      [...queryKeys.user.all, 'subscription', id] as const,
  },
  auth: {
    all: ['auth'] as const,
    user: () => [...queryKeys.auth.all, 'user'] as const,
    session: () => [...queryKeys.auth.all, 'session'] as const,
  },
} as const;

// Cache invalidation helpers for React Query
export function invalidateQueries(queryClient: QueryClient, pattern: string) {
  queryClient.invalidateQueries({ queryKey: [pattern] });
}

export function invalidateUserQueries(
  queryClient: QueryClient,
  userId: string
) {
  queryClient.invalidateQueries({ queryKey: queryKeys.user.all });
  queryClient.invalidateQueries({ queryKey: queryKeys.auth.all });
}

export function invalidateContentQueries(queryClient: QueryClient) {
  queryClient.invalidateQueries({ queryKey: queryKeys.articles.all });
  queryClient.invalidateQueries({ queryKey: queryKeys.newsletters.all });
  queryClient.invalidateQueries({ queryKey: queryKeys.trends.all });
}

// Prefetch utilities
export async function prefetchArticles(
  queryClient: QueryClient,
  filters: Record<string, any> = {}
) {
  await queryClient.prefetchQuery({
    queryKey: queryKeys.articles.list(filters),
    queryFn: () => fetch('/api/content/articles').then(res => res.json()),
    staleTime: 5 * 60 * 1000,
  });
}

export async function prefetchTrends(
  queryClient: QueryClient,
  filters: Record<string, any> = {}
) {
  await queryClient.prefetchQuery({
    queryKey: queryKeys.trends.list(filters),
    queryFn: () => fetch('/api/content/trends').then(res => res.json()),
    staleTime: 5 * 60 * 1000,
  });
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
