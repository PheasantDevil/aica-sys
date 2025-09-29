/**
 * Performance Monitoring Utilities
 * Tracks Core Web Vitals and custom metrics
 */

export interface PerformanceMetric {
  name: string;
  value: number;
  delta: number;
  id: string;
  navigationType: string;
}

export interface CustomMetric {
  name: string;
  value: number;
  timestamp: number;
  metadata?: Record<string, any>;
}

class PerformanceMonitor {
  private metrics: CustomMetric[] = [];
  private observers: PerformanceObserver[] = [];

  constructor() {
    this.initializeWebVitals();
    this.initializeCustomMetrics();
  }

  private initializeWebVitals() {
    if (typeof window === 'undefined') return;

    // LCP (Largest Contentful Paint)
    this.observeMetric('largest-contentful-paint', (entry) => {
      this.recordMetric('LCP', entry.startTime);
    });

    // FID (First Input Delay) - Note: FID is deprecated, using INP instead
    this.observeMetric('first-input', (entry) => {
      // FID is calculated as the time between first input and when the browser can process it
      // Since processingStart is not available, we'll track the startTime as a proxy
      this.recordMetric('FID', entry.startTime);
    });

    // CLS (Cumulative Layout Shift)
    this.observeMetric('layout-shift', (entry) => {
      if (!(entry as any).hadRecentInput) {
        this.recordMetric('CLS', (entry as any).value);
      }
    });

    // FCP (First Contentful Paint)
    this.observeMetric('paint', (entry) => {
      if (entry.name === 'first-contentful-paint') {
        this.recordMetric('FCP', entry.startTime);
      }
    });

    // TTFB (Time to First Byte)
    this.observeMetric('navigation', (entry) => {
      const navEntry = entry as PerformanceNavigationTiming;
      this.recordMetric('TTFB', navEntry.responseStart - navEntry.requestStart);
    });
  }

  private observeMetric(type: string, callback: (entry: PerformanceEntry) => void) {
    if (typeof window === 'undefined') return;

    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          callback(entry);
        }
      });

      observer.observe({ type, buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn(`Failed to observe ${type}:`, error);
    }
  }

  private initializeCustomMetrics() {
    if (typeof window === 'undefined') return;

    // Page load time
    window.addEventListener('load', () => {
      const loadTime = performance.now();
      this.recordMetric('PageLoad', loadTime);
    });

    // DOM content loaded
    document.addEventListener('DOMContentLoaded', () => {
      const domTime = performance.now();
      this.recordMetric('DOMContentLoaded', domTime);
    });

    // Memory usage (if available)
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        this.recordMetric('MemoryUsed', memory.usedJSHeapSize, {
          total: memory.totalJSHeapSize,
          limit: memory.jsHeapSizeLimit,
        });
      }, 30000); // Every 30 seconds
    }
  }

  private recordMetric(name: string, value: number, metadata?: Record<string, any>) {
    const metric: CustomMetric = {
      name,
      value,
      timestamp: Date.now(),
      metadata,
    };

    this.metrics.push(metric);

    // Send to analytics (if available)
    this.sendToAnalytics(metric);

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`📊 Performance Metric: ${name} = ${value}ms`, metadata);
    }
  }

  private sendToAnalytics(metric: CustomMetric) {
    // Send to Google Analytics 4
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'performance_metric', {
        metric_name: metric.name,
        metric_value: Math.round(metric.value),
        metric_timestamp: metric.timestamp,
        ...metric.metadata,
      });
    }

    // Send to custom analytics endpoint
    this.sendToCustomAnalytics(metric);
  }

  private async sendToCustomAnalytics(metric: CustomMetric) {
    try {
      await fetch('/api/analytics/performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metric),
      });
    } catch (error) {
      console.warn('Failed to send performance metric:', error);
    }
  }

  // Public methods
  public getMetrics(): CustomMetric[] {
    return [...this.metrics];
  }

  public getMetricsByName(name: string): CustomMetric[] {
    return this.metrics.filter(metric => metric.name === name);
  }

  public getAverageMetric(name: string): number {
    const metrics = this.getMetricsByName(name);
    if (metrics.length === 0) return 0;
    
    const sum = metrics.reduce((acc, metric) => acc + metric.value, 0);
    return sum / metrics.length;
  }

  public getLatestMetric(name: string): CustomMetric | undefined {
    const metrics = this.getMetricsByName(name);
    return metrics[metrics.length - 1];
  }

  public clearMetrics() {
    this.metrics = [];
  }

  public destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Export for use in components
export default performanceMonitor;