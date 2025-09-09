// メモリキャッシュの実装
class MemoryCache {
  private cache = new Map<string, { value: any; expiry: number }>();
  private maxSize = 100; // 最大キャッシュ数

  set(key: string, value: any, ttl: number = 300000) { // デフォルト5分
    // キャッシュサイズ制限
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      expiry: Date.now() + ttl,
    });
  }

  get(key: string): any | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // 期限切れチェック
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  // 期限切れアイテムのクリーンアップ
  cleanup(): void {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expiry) {
        this.cache.delete(key);
      }
    }
  }
}

// シングルトンインスタンス
export const memoryCache = new MemoryCache();

// 定期的なクリーンアップ（5分ごと）
if (typeof window !== 'undefined') {
  setInterval(() => {
    memoryCache.cleanup();
  }, 300000);
}

// キャッシュキー生成ヘルパー
export function generateCacheKey(prefix: string, ...params: any[]): string {
  return `${prefix}:${params.join(':')}`;
}

// データフェッチ用のキャッシュラッパー
export async function withCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 300000
): Promise<T> {
  // キャッシュから取得を試行
  const cached = memoryCache.get(key);
  if (cached !== null) {
    return cached;
  }

  // データをフェッチ
  const data = await fetcher();
  
  // キャッシュに保存
  memoryCache.set(key, data, ttl);
  
  return data;
}
