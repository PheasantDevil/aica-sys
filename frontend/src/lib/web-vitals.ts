/**
 * Web Vitals Monitoring
 * Phase 7-4: Frontend optimization
 */

import { getCLS, getFCP, getFID, getLCP, getTTFB, Metric } from 'web-vitals';

export interface WebVitalsMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  navigationType: string;
}

// Web Vitals閾値
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  FCP: { good: 1800, poor: 3000 },
  TTFB: { good: 600, poor: 1200 },
};

// メトリクスの評価
function getRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[name as keyof typeof THRESHOLDS];
  if (!threshold) return 'good';
  
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

// メトリクスをサーバーに送信
async function sendToAnalytics(metric: WebVitalsMetric) {
  try {
    // Google Analyticsに送信
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', metric.name, {
        event_category: 'Web Vitals',
        event_label: metric.id,
        value: Math.round(metric.value),
        non_interaction: true,
      });
    }

    // カスタムアナリティクスエンドポイントに送信
    if (process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT) {
      await fetch(process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric: metric.name,
          value: metric.value,
          rating: metric.rating,
          timestamp: Date.now(),
          url: window.location.href,
          userAgent: navigator.userAgent,
        }),
      });
    }

    // コンソールに出力（開発環境のみ）
    if (process.env.NODE_ENV === 'development') {
      console.log('📊 Web Vital:', {
        name: metric.name,
        value: Math.round(metric.value),
        rating: metric.rating,
      });
    }
  } catch (error) {
    console.error('Failed to send web vitals:', error);
  }
}

// Web Vitals の収集
export function reportWebVitals(onPerfEntry?: (metric: WebVitalsMetric) => void) {
  const handleMetric = (metric: Metric) => {
    const webVitalsMetric: WebVitalsMetric = {
      name: metric.name,
      value: metric.value,
      rating: getRating(metric.name, metric.value),
      delta: metric.delta,
      id: metric.id,
      navigationType: metric.navigationType,
    };

    // カスタムコールバック
    if (onPerfEntry) {
      onPerfEntry(webVitalsMetric);
    }

    // アナリティクスに送信
    sendToAnalytics(webVitalsMetric);
  };

  // 各メトリクスの収集
  getCLS(handleMetric);
  getFCP(handleMetric);
  getFID(handleMetric);
  getLCP(handleMetric);
  getTTFB(handleMetric);
}

// パフォーマンスマーク
export function performanceMark(name: string) {
  if (typeof window !== 'undefined' && window.performance) {
    window.performance.mark(name);
  }
}

// パフォーマンス測定
export function performanceMeasure(name: string, startMark: string, endMark: string) {
  if (typeof window !== 'undefined' && window.performance) {
    try {
      window.performance.measure(name, startMark, endMark);
      const measure = window.performance.getEntriesByName(name)[0];
      if (measure) {
        console.log(`⏱️ ${name}: ${Math.round(measure.duration)}ms`);
      }
    } catch (error) {
      console.error('Performance measure error:', error);
    }
  }
}

// カスタムメトリクスの記録
export function recordCustomMetric(name: string, value: number, unit: string = 'ms') {
  try {
    if (process.env.NODE_ENV === 'development') {
      console.log(`📊 Custom Metric: ${name} = ${value}${unit}`);
    }

    // カスタムアナリティクスに送信
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'custom_metric', {
        event_category: 'Performance',
        event_label: name,
        value: Math.round(value),
        unit: unit,
      });
    }
  } catch (error) {
    console.error('Failed to record custom metric:', error);
  }
}

// パフォーマンスレポートの取得
export function getPerformanceReport() {
  if (typeof window === 'undefined' || !window.performance) {
    return null;
  }

  const navigation = window.performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  const paint = window.performance.getEntriesByType('paint');
  
  return {
    // ナビゲーションタイミング
    dns: navigation ? navigation.domainLookupEnd - navigation.domainLookupStart : 0,
    tcp: navigation ? navigation.connectEnd - navigation.connectStart : 0,
    request: navigation ? navigation.responseStart - navigation.requestStart : 0,
    response: navigation ? navigation.responseEnd - navigation.responseStart : 0,
    domProcessing: navigation ? navigation.domComplete - navigation.domLoading : 0,
    domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0,
    domComplete: navigation ? navigation.domComplete : 0,
    loadComplete: navigation ? navigation.loadEventEnd : 0,
    
    // ペイントタイミング
    firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
    firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
    
    // リソース統計
    resources: window.performance.getEntriesByType('resource').length,
    
    // メモリ使用量（Chrome のみ）
    memory: (window.performance as any).memory ? {
      usedJSHeapSize: (window.performance as any).memory.usedJSHeapSize,
      totalJSHeapSize: (window.performance as any).memory.totalJSHeapSize,
      jsHeapSizeLimit: (window.performance as any).memory.jsHeapSizeLimit,
    } : null,
  };
}

// パフォーマンスオブザーバー
export function observePerformance() {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
    return;
  }

  try {
    // Long Tasksの監視
    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) {
          console.warn(`⚠️ Long Task detected: ${Math.round(entry.duration)}ms`);
          recordCustomMetric('long_task', entry.duration);
        }
      }
    });
    longTaskObserver.observe({ entryTypes: ['longtask'] });

    // Layout Shiftsの監視
    const layoutShiftObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries() as any[]) {
        if (entry.hadRecentInput) continue;
        console.log(`📐 Layout Shift: ${entry.value.toFixed(4)}`);
      }
    });
    layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
  } catch (error) {
    console.error('Performance observer error:', error);
  }
}
