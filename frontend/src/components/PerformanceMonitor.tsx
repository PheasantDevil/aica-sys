"use client";

import { useEffect, useState } from "react";
import { onCLS, onFCP, onLCP, onTTFB } from "web-vitals";

interface PerformanceMetrics {
  CLS: number | null;
  FCP: number | null;
  LCP: number | null;
  TTFB: number | null;
}

interface PerformanceMonitorProps {
  onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
  enabled?: boolean;
}

const PerformanceMonitor = ({ onMetricsUpdate, enabled = true }: PerformanceMonitorProps) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    CLS: null,
    FCP: null,
    LCP: null,
    TTFB: null,
  });

  useEffect(() => {
    if (!enabled) return;

    const updateMetrics = (metric: any) => {
      setMetrics((prev) => {
        const newMetrics = {
          ...prev,
          [metric.name]: metric.value,
        };

        if (onMetricsUpdate) {
          onMetricsUpdate(newMetrics);
        }

        return newMetrics;
      });
    };

    // Collect Core Web Vitals
    onCLS(updateMetrics);
    onFCP(updateMetrics);
    onLCP(updateMetrics);
    onTTFB(updateMetrics);

    // Collect additional performance metrics
    if (typeof window !== "undefined") {
      // First Contentful Paint
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === "paint") {
            updateMetrics({
              name: entry.name === "first-contentful-paint" ? "FCP" : entry.name,
              value: entry.startTime,
            });
          }
        }
      });

      observer.observe({ entryTypes: ["paint"] });

      // Resource timing
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === "resource") {
            const resource = entry as PerformanceResourceTiming;
            if (resource.transferSize > 0) {
              console.log(`Resource loaded: ${resource.name} (${resource.transferSize} bytes)`);
            }
          }
        }
      });

      resourceObserver.observe({ entryTypes: ["resource"] });

      return () => {
        observer.disconnect();
        resourceObserver.disconnect();
      };
    }
  }, [enabled, onMetricsUpdate]);

  // Log performance metrics to console in development
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("Performance Metrics:", metrics);
    }
  }, [metrics]);

  return null; // This component doesn't render anything
};

export default PerformanceMonitor;
