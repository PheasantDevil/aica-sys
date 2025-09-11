'use client';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  type: 'navigation' | 'paint' | 'measure' | 'custom';
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observers: PerformanceObserver[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      this.initializeObservers();
    }
  }

  private initializeObservers(): void {
    // Observe navigation timing
    if ('PerformanceObserver' in window) {
      const navObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.recordMetric('navigation', {
              name: 'page_load_time',
              value: navEntry.loadEventEnd - navEntry.loadEventStart,
              timestamp: Date.now(),
              type: 'navigation',
            });
          }
        }
      });
      navObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navObserver);

      // Observe paint timing
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'paint') {
            this.recordMetric('paint', {
              name: entry.name,
              value: entry.startTime,
              timestamp: Date.now(),
              type: 'paint',
            });
          }
        }
      });
      paintObserver.observe({ entryTypes: ['paint'] });
      this.observers.push(paintObserver);

      // Observe largest contentful paint
      const lcpObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric('lcp', {
            name: 'largest_contentful_paint',
            value: entry.startTime,
            timestamp: Date.now(),
            type: 'paint',
          });
        }
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);

      // Observe first input delay
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric('fid', {
            name: 'first_input_delay',
            value: (entry as any).processingStart - entry.startTime,
            timestamp: Date.now(),
            type: 'measure',
          });
        }
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);
    }
  }

  private recordMetric(category: string, metric: PerformanceMetric): void {
    this.metrics.push(metric);
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${category}:`, metric);
    }

    // Send to analytics in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToAnalytics(category, metric);
    }
  }

  private sendToAnalytics(category: string, metric: PerformanceMetric): void {
    // Send to Google Analytics or other analytics service
    if (typeof gtag !== 'undefined') {
      gtag('event', 'performance_metric', {
        event_category: category,
        event_label: metric.name,
        value: Math.round(metric.value),
        custom_map: {
          metric_type: metric.type,
        },
      });
    }
  }

  // Custom performance measurement
  measure(name: string, fn: () => void): void {
    const start = performance.now();
    fn();
    const end = performance.now();
    
    this.recordMetric('custom', {
      name,
      value: end - start,
      timestamp: Date.now(),
      type: 'measure',
    });
  }

  // Measure async operations
  async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    try {
      const result = await fn();
      const end = performance.now();
      
      this.recordMetric('custom', {
        name,
        value: end - start,
        timestamp: Date.now(),
        type: 'measure',
      });
      
      return result;
    } catch (error) {
      const end = performance.now();
      
      this.recordMetric('custom', {
        name: `${name}_error`,
        value: end - start,
        timestamp: Date.now(),
        type: 'measure',
      });
      
      throw error;
    }
  }

  // Get performance metrics
  getMetrics(category?: string): PerformanceMetric[] {
    if (category) {
      return this.metrics.filter(m => m.name.includes(category));
    }
    return [...this.metrics];
  }

  // Get performance summary
  getSummary(): {
    totalMetrics: number;
    averageLoadTime: number;
    averagePaintTime: number;
    slowestOperations: PerformanceMetric[];
  } {
    const loadTimes = this.metrics.filter(m => m.name === 'page_load_time');
    const paintTimes = this.metrics.filter(m => m.type === 'paint');
    
    const averageLoadTime = loadTimes.length > 0 
      ? loadTimes.reduce((sum, m) => sum + m.value, 0) / loadTimes.length 
      : 0;
    
    const averagePaintTime = paintTimes.length > 0 
      ? paintTimes.reduce((sum, m) => sum + m.value, 0) / paintTimes.length 
      : 0;
    
    const slowestOperations = [...this.metrics]
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
    
    return {
      totalMetrics: this.metrics.length,
      averageLoadTime,
      averagePaintTime,
      slowestOperations,
    };
  }

  // Cleanup
  destroy(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    this.metrics = [];
  }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

// Performance utilities
export function measurePerformance(name: string, fn: () => void): void {
  performanceMonitor.measure(name, fn);
}

export async function measureAsyncPerformance<T>(
  name: string, 
  fn: () => Promise<T>
): Promise<T> {
  return performanceMonitor.measureAsync(name, fn);
}

// Web Vitals measurement
export function measureWebVitals(): void {
  if (typeof window === 'undefined') return;

  // Measure Core Web Vitals
  const measureCLS = () => {
    let clsValue = 0;
    let clsEntries: any[] = [];
    
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsEntries.push(entry);
          clsValue += (entry as any).value;
        }
      }
    });
    
    observer.observe({ entryTypes: ['layout-shift'] });
    
    // Report CLS when page is hidden
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        performanceMonitor.recordMetric('web-vitals', {
          name: 'cumulative_layout_shift',
          value: clsValue,
          timestamp: Date.now(),
          type: 'paint',
        });
        observer.disconnect();
      }
    });
  };

  measureCLS();
}

// Initialize performance monitoring
if (typeof window !== 'undefined') {
  measureWebVitals();
}
