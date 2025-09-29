/**
 * Asset Optimization Utilities
 * 静的アセットの最適化とCDN管理
 */

export interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  quality?: number;
  format?: 'webp' | 'avif' | 'jpeg' | 'png';
  priority?: boolean;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
}

export interface CDNConfig {
  baseUrl: string;
  fallbackUrl?: string;
  enableWebP: boolean;
  enableAVIF: boolean;
  quality: number;
}

// CDN設定
const CDN_CONFIG: CDNConfig = {
  baseUrl: process.env.NEXT_PUBLIC_CDN_URL || '',
  fallbackUrl: process.env.NEXT_PUBLIC_FALLBACK_URL || '',
  enableWebP: true,
  enableAVIF: true,
  quality: 80,
};

/**
 * 画像URLを最適化
 */
export function optimizeImageUrl(
  src: string,
  width: number,
  height: number,
  options: Partial<OptimizedImageProps> = {}
): string {
  const { quality = CDN_CONFIG.quality, format = 'auto' } = options;

  // CDNが設定されている場合
  if (CDN_CONFIG.baseUrl) {
    const params = new URLSearchParams({
      w: width.toString(),
      h: height.toString(),
      q: quality.toString(),
      f: format === 'auto' ? 'auto' : format,
    });

    return `${CDN_CONFIG.baseUrl}/${src}?${params.toString()}`;
  }

  // フォールバックURL
  if (CDN_CONFIG.fallbackUrl) {
    return `${CDN_CONFIG.fallbackUrl}/${src}`;
  }

  return src;
}

/**
 * レスポンシブ画像のsrcSetを生成
 */
export function generateSrcSet(
  src: string,
  sizes: number[],
  options: Partial<OptimizedImageProps> = {}
): string {
  return sizes
    .map(size => {
      const url = optimizeImageUrl(src, size, size, options);
      return `${url} ${size}w`;
    })
    .join(', ');
}

/**
 * 画像のプレースホルダーを生成
 */
export function generateBlurDataURL(width: number, height: number): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d');
  if (!ctx) return '';

  // シンプルなグラデーション
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, '#f3f4f6');
  gradient.addColorStop(1, '#e5e7eb');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  return canvas.toDataURL('image/jpeg', 0.1);
}

/**
 * アセットのプリロード
 */
export function preloadAsset(href: string, as: string, type?: string): void {
  if (typeof window === 'undefined') return;

  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;

  if (type) {
    link.type = type;
  }

  document.head.appendChild(link);
}

/**
 * フォントのプリロード
 */
export function preloadFont(href: string, type: string = 'font/woff2'): void {
  preloadAsset(href, 'font', type);
}

/**
 * 画像のプリロード
 */
export function preloadImage(href: string): void {
  preloadAsset(href, 'image');
}

/**
 * スクリプトのプリロード
 */
export function preloadScript(
  href: string,
  type: string = 'text/javascript'
): void {
  preloadAsset(href, 'script', type);
}

/**
 * スタイルシートのプリロード
 */
export function preloadStylesheet(href: string): void {
  preloadAsset(href, 'style', 'text/css');
}

/**
 * アセットの遅延読み込み
 */
export function lazyLoadAsset(
  element: HTMLElement,
  callback: () => void,
  options: IntersectionObserverInit = {}
): IntersectionObserver {
  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          callback();
          observer.unobserve(entry.target);
        }
      });
    },
    {
      rootMargin: '50px',
      threshold: 0.1,
      ...options,
    }
  );

  observer.observe(element);
  return observer;
}

/**
 * 画像の遅延読み込み
 */
export function lazyLoadImage(
  img: HTMLImageElement,
  src: string,
  options: Partial<OptimizedImageProps> = {}
): IntersectionObserver {
  return lazyLoadAsset(img, () => {
    img.src = optimizeImageUrl(src, img.width, img.height, options);
    img.classList.add('loaded');
  });
}

/**
 * アセットのキャッシュ管理
 */
export class AssetCache {
  private cache = new Map<string, any>();
  private maxSize = 100;

  set(key: string, value: any): void {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, value);
  }

  get(key: string): any {
    return this.cache.get(key);
  }

  has(key: string): boolean {
    return this.cache.has(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// グローバルアセットキャッシュ
export const assetCache = new AssetCache();

/**
 * アセットの最適化設定
 */
export const ASSET_OPTIMIZATION = {
  images: {
    formats: ['image/webp', 'image/avif'],
    quality: 80,
    sizes: [320, 640, 768, 1024, 1280, 1920],
  },
  fonts: {
    preload: true,
    display: 'swap',
  },
  scripts: {
    defer: true,
    async: true,
  },
  styles: {
    preload: true,
    critical: true,
  },
} as const;
