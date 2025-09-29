'use client';

import { performanceMonitor } from '@/lib/performance';
import { createContext, ReactNode, useContext, useEffect } from 'react';

interface PerformanceContextType {
  getMetrics: () => any[];
  getMetricsByName: (name: string) => any[];
  getAverageMetric: (name: string) => number;
  getLatestMetric: (name: string) => any;
  clearMetrics: () => void;
}

const PerformanceContext = createContext<PerformanceContextType | undefined>(
  undefined
);

interface PerformanceProviderProps {
  children: ReactNode;
}

export function PerformanceProvider({ children }: PerformanceProviderProps) {
  useEffect(() => {
    // Initialize performance monitoring
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // Page became visible, record metric
        // performanceMonitor.recordMetric('PageVisibility', Date.now());
      }
    };

    const handleBeforeUnload = () => {
      // Record session duration
      const sessionStart = performance.timing?.navigationStart || Date.now();
      const sessionDuration = Date.now() - sessionStart;
      // performanceMonitor.recordMetric('SessionDuration', sessionDuration);
    };

    // Add event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Record page load metrics
    if (document.readyState === 'complete') {
      // performanceMonitor.recordMetric('PageLoadComplete', performance.now());
    } else {
      window.addEventListener('load', () => {
        // performanceMonitor.recordMetric('PageLoadComplete', performance.now());
      });
    }

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const contextValue: PerformanceContextType = {
    getMetrics: () => performanceMonitor.getMetrics(),
    getMetricsByName: (name: string) =>
      performanceMonitor.getMetricsByName(name),
    getAverageMetric: (name: string) =>
      performanceMonitor.getAverageMetric(name),
    getLatestMetric: (name: string) => performanceMonitor.getLatestMetric(name),
    clearMetrics: () => performanceMonitor.clearMetrics(),
  };

  return (
    <PerformanceContext.Provider value={contextValue}>
      {children}
    </PerformanceContext.Provider>
  );
}

export function usePerformance() {
  const context = useContext(PerformanceContext);
  if (context === undefined) {
    throw new Error('usePerformance must be used within a PerformanceProvider');
  }
  return context;
}
