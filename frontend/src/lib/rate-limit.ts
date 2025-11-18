interface RateLimitConfig {
  windowMs: number; // 時間窓（ミリ秒）
  maxRequests: number; // 最大リクエスト数
  keyGenerator?: (req: Request) => string;
  skipSuccessfulRequests?: boolean;
  skipFailedRequests?: boolean;
}

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

class RateLimiter {
  private store = new Map<string, RateLimitEntry>();
  private config: RateLimitConfig;

  constructor(config: RateLimitConfig) {
    this.config = config;
  }

  private getKey(req: Request): string {
    if (this.config.keyGenerator) {
      return this.config.keyGenerator(req);
    }

    // デフォルト: IPアドレスベース
    const forwarded = req.headers.get("x-forwarded-for");
    const ip = forwarded ? forwarded.split(",")[0] : "unknown";
    return ip;
  }

  private cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];

    this.store.forEach((entry, key) => {
      if (now > entry.resetTime) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach((key) => {
      this.store.delete(key);
    });
  }

  async check(req: Request): Promise<{
    allowed: boolean;
    remaining: number;
    resetTime: number;
    retryAfter?: number;
  }> {
    const key = this.getKey(req);
    const now = Date.now();
    const windowStart = now - this.config.windowMs;

    // 期限切れエントリをクリーンアップ
    this.cleanup();

    const entry = this.store.get(key);

    if (!entry || now > entry.resetTime) {
      // 新しいエントリまたは期限切れ
      const newEntry: RateLimitEntry = {
        count: 1,
        resetTime: now + this.config.windowMs,
      };
      this.store.set(key, newEntry);

      return {
        allowed: true,
        remaining: this.config.maxRequests - 1,
        resetTime: newEntry.resetTime,
      };
    }

    if (entry.count >= this.config.maxRequests) {
      // レート制限に達している
      return {
        allowed: false,
        remaining: 0,
        resetTime: entry.resetTime,
        retryAfter: Math.ceil((entry.resetTime - now) / 1000),
      };
    }

    // カウントを増加
    entry.count++;
    this.store.set(key, entry);

    return {
      allowed: true,
      remaining: this.config.maxRequests - entry.count,
      resetTime: entry.resetTime,
    };
  }

  reset(key: string): void {
    this.store.delete(key);
  }

  getStats(): {
    totalKeys: number;
    entries: Array<{ key: string; count: number; resetTime: number }>;
  } {
    const entries = Array.from(this.store.entries()).map(([key, entry]) => ({
      key,
      count: entry.count,
      resetTime: entry.resetTime,
    }));

    return {
      totalKeys: this.store.size,
      entries,
    };
  }
}

// 異なるレート制限設定
export const rateLimiters = {
  // 一般的なAPI呼び出し
  api: new RateLimiter({
    windowMs: 15 * 60 * 1000, // 15分
    maxRequests: 100,
  }),

  // 認証関連
  auth: new RateLimiter({
    windowMs: 15 * 60 * 1000, // 15分
    maxRequests: 5,
  }),

  // パスワードリセット
  passwordReset: new RateLimiter({
    windowMs: 60 * 60 * 1000, // 1時間
    maxRequests: 3,
  }),

  // 検索
  search: new RateLimiter({
    windowMs: 1 * 60 * 1000, // 1分
    maxRequests: 30,
  }),

  // ファイルアップロード
  upload: new RateLimiter({
    windowMs: 60 * 60 * 1000, // 1時間
    maxRequests: 10,
  }),
};

// レート制限ミドルウェア
export async function rateLimit(
  req: Request,
  limiter: RateLimiter = rateLimiters.api,
): Promise<Response | null> {
  const result = await limiter.check(req);

  if (!result.allowed) {
    return new Response(
      JSON.stringify({
        error: "Too Many Requests",
        message: "レート制限に達しました。しばらくしてから再試行してください。",
        retryAfter: result.retryAfter,
      }),
      {
        status: 429,
        headers: {
          "Content-Type": "application/json",
          "Retry-After": result.retryAfter?.toString() || "60",
          "X-RateLimit-Limit": limiter === rateLimiters.api ? "100" : "5",
          "X-RateLimit-Remaining": result.remaining.toString(),
          "X-RateLimit-Reset": new Date(result.resetTime).toISOString(),
        },
      },
    );
  }

  return null;
}
