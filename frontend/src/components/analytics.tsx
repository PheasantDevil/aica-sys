'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { loadGA, trackPageView, trackEvent, analyticsEvents } from '@/lib/analytics';

// Google Analytics プロバイダー
export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    loadGA();
  }, []);

  return <>{children}</>;
}

// ページビュー追跡コンポーネント
export function PageViewTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const url = pathname + (searchParams.toString() ? `?${searchParams.toString()}` : '');
    trackPageView(url);
  }, [pathname, searchParams]);

  return null;
}

// スクロール深度追跡コンポーネント
export function ScrollDepthTracker() {
  useEffect(() => {
    let maxScrollDepth = 0;
    let scrollDepthTracked = false;

    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollDepth = Math.round((scrollTop / documentHeight) * 100);

      if (scrollDepth > maxScrollDepth) {
        maxScrollDepth = scrollDepth;
      }

      // 25%, 50%, 75%, 100% のポイントで追跡
      const milestones = [25, 50, 75, 100];
      milestones.forEach(milestone => {
        if (scrollDepth >= milestone && !scrollDepthTracked) {
          trackEvent('scroll_depth', 'engagement', `${milestone}%`, milestone);
          if (milestone === 100) {
            scrollDepthTracked = true;
          }
        }
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return null;
}

// 外部リンク追跡コンポーネント
export function ExternalLinkTracker() {
  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const link = target.closest('a');
      
      if (link && link.href) {
        const url = new URL(link.href);
        const currentDomain = window.location.hostname;
        
        // 外部リンクの場合
        if (url.hostname !== currentDomain) {
          const linkText = link.textContent?.trim() || 'Unknown';
          analyticsEvents.clickExternalLink(link.href, linkText);
        }
      }
    };

    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, []);

  return null;
}

// パフォーマンス追跡コンポーネント
export function PerformanceTracker() {
  useEffect(() => {
    // Core Web Vitals の追跡
    const trackWebVitals = () => {
      // LCP (Largest Contentful Paint)
      if ('PerformanceObserver' in window) {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          trackEvent('timing_complete', 'performance', 'LCP', Math.round(lastEntry.startTime));
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // FID (First Input Delay)
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            trackEvent('timing_complete', 'performance', 'FID', Math.round(entry.processingStart - entry.startTime));
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        // CLS (Cumulative Layout Shift)
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          });
          trackEvent('timing_complete', 'performance', 'CLS', Math.round(clsValue * 1000));
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
      }

      // ページ読み込み時間
      window.addEventListener('load', () => {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        trackEvent('timing_complete', 'performance', 'page_load_time', loadTime);
      });
    };

    trackWebVitals();
  }, []);

  return null;
}

// エラー追跡コンポーネント
export function ErrorTracker() {
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      analyticsEvents.trackError('javascript_error', event.message);
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      analyticsEvents.trackError('unhandled_promise_rejection', event.reason);
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return null;
}

// 統合アナリティクスコンポーネント
export function Analytics() {
  return (
    <>
      <PageViewTracker />
      <ScrollDepthTracker />
      <ExternalLinkTracker />
      <PerformanceTracker />
      <ErrorTracker />
    </>
  );
}
