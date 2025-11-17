"use client";

import { useEffect, useState } from "react";

interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
}

export function PerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    // Performance Observer の設定
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();

      entries.forEach((entry) => {
        if (entry.entryType === "paint") {
          if (entry.name === "first-contentful-paint") {
            setMetrics(
              (prev) =>
                ({
                  ...prev,
                  fcp: entry.startTime,
                }) as PerformanceMetrics,
            );
          }
        }

        if (entry.entryType === "largest-contentful-paint") {
          setMetrics(
            (prev) =>
              ({
                ...prev,
                lcp: entry.startTime,
              }) as PerformanceMetrics,
          );
        }

        if (entry.entryType === "first-input") {
          setMetrics(
            (prev) =>
              ({
                ...prev,
                fid: (entry as any).processingStart - entry.startTime,
              }) as PerformanceMetrics,
          );
        }

        if (entry.entryType === "layout-shift") {
          if (!(entry as any).hadRecentInput) {
            setMetrics(
              (prev) =>
                ({
                  ...prev,
                  cls: (prev?.cls || 0) + (entry as any).value,
                }) as PerformanceMetrics,
            );
          }
        }
      });
    });

    // 監視対象の登録
    try {
      observer.observe({
        entryTypes: ["paint", "largest-contentful-paint", "first-input", "layout-shift"],
      });
    } catch (e) {
      console.warn("Performance Observer not supported");
    }

    // TTFB の取得
    const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming;
    if (navigation) {
      setMetrics(
        (prev) =>
          ({
            ...prev,
            ttfb: navigation.responseStart - navigation.requestStart,
          }) as PerformanceMetrics,
      );
    }

    return () => {
      observer.disconnect();
    };
  }, []);

  // 開発環境でのみ表示
  if (process.env.NODE_ENV !== "development") {
    return null;
  }

  const getScore = (value: number, thresholds: { good: number; poor: number }) => {
    if (value <= thresholds.good) return "good";
    if (value <= thresholds.poor) return "needs-improvement";
    return "poor";
  };

  const getScoreColor = (score: string) => {
    switch (score) {
      case "good":
        return "text-green-600";
      case "needs-improvement":
        return "text-yellow-600";
      case "poor":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  if (!metrics) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-300 rounded-lg shadow-lg p-4 z-50 max-w-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-sm">Performance Monitor</h3>
        <button
          onClick={() => setIsVisible(!isVisible)}
          className="text-gray-500 hover:text-gray-700"
        >
          {isVisible ? "−" : "+"}
        </button>
      </div>

      {isVisible && (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span>FCP:</span>
            <span className={getScoreColor(getScore(metrics.fcp, { good: 1800, poor: 3000 }))}>
              {metrics.fcp.toFixed(0)}ms
            </span>
          </div>
          <div className="flex justify-between">
            <span>LCP:</span>
            <span className={getScoreColor(getScore(metrics.lcp, { good: 2500, poor: 4000 }))}>
              {metrics.lcp.toFixed(0)}ms
            </span>
          </div>
          <div className="flex justify-between">
            <span>FID:</span>
            <span className={getScoreColor(getScore(metrics.fid, { good: 100, poor: 300 }))}>
              {metrics.fid.toFixed(0)}ms
            </span>
          </div>
          <div className="flex justify-between">
            <span>CLS:</span>
            <span className={getScoreColor(getScore(metrics.cls, { good: 0.1, poor: 0.25 }))}>
              {metrics.cls.toFixed(3)}
            </span>
          </div>
          <div className="flex justify-between">
            <span>TTFB:</span>
            <span className={getScoreColor(getScore(metrics.ttfb, { good: 800, poor: 1800 }))}>
              {metrics.ttfb.toFixed(0)}ms
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
