'use client';

import { Analytics as AnalyticsService } from '@/lib/analytics';
import { usePathname, useSearchParams } from 'next/navigation';
import { Suspense, useEffect } from 'react';

// Google Analytics プロバイダー
export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    AnalyticsService.init();
  }, []);

  return <>{children}</>;
}

// ページビュー追跡コンポーネント（内部）
function PageViewTrackerInner() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const url =
      pathname + (searchParams.toString() ? `?${searchParams.toString()}` : '');
    AnalyticsService.trackPageView(url);
  }, [pathname, searchParams]);

  return null;
}

// ページビュー追跡コンポーネント（Suspense境界付き）
export function PageViewTracker() {
  return (
    <Suspense fallback={null}>
      <PageViewTrackerInner />
    </Suspense>
  );
}

// スクロール深度追跡コンポーネント
export function ScrollDepthTracker() {
  useEffect(() => {
    let maxScrollDepth = 0;
    let scrollDepthTracked = false;

    const handleScroll = () => {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
      const documentHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const scrollDepth = Math.round((scrollTop / documentHeight) * 100);

      if (scrollDepth > maxScrollDepth) {
        maxScrollDepth = scrollDepth;
      }

      // 25%, 50%, 75%, 100% のポイントで追跡
      const milestones = [25, 50, 75, 100];
      milestones.forEach(milestone => {
        if (scrollDepth >= milestone && !scrollDepthTracked) {
          AnalyticsService.event('scroll_depth', {
            category: 'engagement',
            label: `${milestone}%`,
            value: milestone,
          });
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
          AnalyticsService.event('click_external_link', {
            link_url: link.href,
            link_text: linkText,
          });
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
        const lcpObserver = new PerformanceObserver(list => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          AnalyticsService.event('timing_complete', {
            category: 'performance',
            label: 'LCP',
            value: Math.round(lastEntry.startTime),
          });
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // FID (First Input Delay)
        const fidObserver = new PerformanceObserver(list => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            AnalyticsService.event('timing_complete', {
              category: 'performance',
              label: 'FID',
              value: Math.round(entry.processingStart - entry.startTime),
            });
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        // CLS (Cumulative Layout Shift)
        let clsValue = 0;
        const clsObserver = new PerformanceObserver(list => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          });
          AnalyticsService.event('timing_complete', {
            category: 'performance',
            label: 'CLS',
            value: Math.round(clsValue * 1000),
          });
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
      }

      // ページ読み込み時間
      window.addEventListener('load', () => {
        const loadTime =
          performance.timing.loadEventEnd - performance.timing.navigationStart;
        AnalyticsService.event('timing_complete', {
          category: 'performance',
          label: 'page_load_time',
          value: loadTime,
        });
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
      AnalyticsService.event('javascript_error', {
        error_message: event.message,
        error_type: 'javascript_error',
      });
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      AnalyticsService.event('unhandled_promise_rejection', {
        error_reason: event.reason,
        error_type: 'unhandled_promise_rejection',
      });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener(
        'unhandledrejection',
        handleUnhandledRejection
      );
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
