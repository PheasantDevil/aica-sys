import { randomBytes, createHmac } from 'crypto';

interface CSRFConfig {
  secret: string;
  tokenLength: number;
  maxAge: number; // ミリ秒
}

const defaultConfig: CSRFConfig = {
  secret: process.env.CSRF_SECRET || 'your-csrf-secret-key',
  tokenLength: 32,
  maxAge: 60 * 60 * 1000, // 1時間
};

class CSRFProtection {
  private config: CSRFConfig;
  private tokenStore = new Map<string, { token: string; expires: number }>();

  constructor(config: Partial<CSRFConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  // CSRFトークンを生成
  generateToken(sessionId: string): string {
    const token = randomBytes(this.config.tokenLength).toString('hex');
    const expires = Date.now() + this.config.maxAge;
    
    this.tokenStore.set(sessionId, { token, expires });
    
    return token;
  }

  // CSRFトークンを検証
  validateToken(sessionId: string, token: string): boolean {
    const stored = this.tokenStore.get(sessionId);
    
    if (!stored) {
      return false;
    }

    // 期限切れチェック
    if (Date.now() > stored.expires) {
      this.tokenStore.delete(sessionId);
      return false;
    }

    // トークン比較
    return stored.token === token;
  }

  // トークンを無効化
  invalidateToken(sessionId: string): void {
    this.tokenStore.delete(sessionId);
  }

  // 期限切れトークンをクリーンアップ
  cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];
    
    this.tokenStore.forEach(({ expires }, sessionId) => {
      if (now > expires) {
        keysToDelete.push(sessionId);
      }
    });
    
    keysToDelete.forEach(sessionId => {
      this.tokenStore.delete(sessionId);
    });
  }

  // トークンのハッシュ値を生成（セキュアな比較用）
  generateTokenHash(token: string): string {
    return createHmac('sha256', this.config.secret)
      .update(token)
      .digest('hex');
  }
}

// シングルトンインスタンス
export const csrfProtection = new CSRFProtection();

// 定期的なクリーンアップ（5分ごと）
if (typeof window !== 'undefined') {
  setInterval(() => {
    csrfProtection.cleanup();
  }, 5 * 60 * 1000);
}

// クライアントサイド用のCSRFトークン管理
export class CSRFClient {
  private token: string | null = null;
  private sessionId: string | null = null;

  setSessionId(sessionId: string) {
    this.sessionId = sessionId;
  }

  async getToken(): Promise<string | null> {
    if (!this.sessionId) {
      return null;
    }

    try {
      const response = await fetch('/api/csrf/token', {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.token;
        return this.token;
      }
    } catch (error) {
      console.error('Failed to get CSRF token:', error);
    }

    return null;
  }

  getStoredToken(): string | null {
    return this.token;
  }

  clearToken(): void {
    this.token = null;
  }

  // リクエストヘッダーにCSRFトークンを追加
  getHeaders(): Record<string, string> {
    if (!this.token) {
      return {};
    }

    return {
      'X-CSRF-Token': this.token,
    };
  }
}

export const csrfClient = new CSRFClient();
