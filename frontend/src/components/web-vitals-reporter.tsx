'use client';

/**
 * Web Vitals Reporter Component
 * Phase 7-4: Frontend optimization
 */

import { useEffect } from 'react';
import { reportWebVitals, observePerformance, getPerformanceReport } from '@/lib/web-vitals';

export function WebVitalsReporter() {
  useEffect(() => {
    // Web Vitals の監視を開始
    reportWebVitals();

    // パフォーマンスオブザーバーを起動
    observePerformance();

    // ページロード完了後にレポートを生成
    if (typeof window !== 'undefined') {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const report = getPerformanceReport();
          if (report && process.env.NODE_ENV === 'development') {
            console.log('📊 Performance Report:', report);
          }
        }, 0);
      });
    }
  }, []);

  // このコンポーネントは何もレンダリングしない
  return null;
}

export default WebVitalsReporter;
