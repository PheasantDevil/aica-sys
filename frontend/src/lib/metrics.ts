export interface MetricData {
  name: string;
  value: number;
  timestamp: Date;
  tags?: Record<string, string>;
  metadata?: Record<string, any>;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: Date;
  context?: Record<string, any>;
}

export interface UserMetric {
  userId: string;
  action: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface BusinessMetric {
  event: string;
  value: number;
  timestamp: Date;
  context?: Record<string, any>;
}

class MetricsCollector {
  private metrics: MetricData[] = [];
  private performanceMetrics: PerformanceMetric[] = [];
  private userMetrics: UserMetric[] = [];
  private businessMetrics: BusinessMetric[] = [];
  private isEnabled: boolean = true;
  private batchSize: number = 100;
  private flushInterval: number = 30000; // 30 seconds
  private flushTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.startFlushTimer();
  }

  // Enable/disable metrics collection
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    if (enabled) {
      this.startFlushTimer();
    } else {
      this.stopFlushTimer();
    }
  }

  // Start automatic flushing
  private startFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    
    this.flushTimer = setInterval(() => {
      this.flush();
    }, this.flushInterval);
  }

  // Stop automatic flushing
  private stopFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }

  // Add a general metric
  addMetric(name: string, value: number, tags?: Record<string, string>, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const metric: MetricData = {
      name,
      value,
      timestamp: new Date(),
      tags,
      metadata,
    };

    this.metrics.push(metric);
    this.checkFlushThreshold();
  }

  // Add a performance metric
  addPerformanceMetric(name: string, value: number, unit: string, context?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const metric: PerformanceMetric = {
      name,
      value,
      unit,
      timestamp: new Date(),
      context,
    };

    this.performanceMetrics.push(metric);
    this.checkFlushThreshold();
  }

  // Add a user metric
  addUserMetric(userId: string, action: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const metric: UserMetric = {
      userId,
      action,
      timestamp: new Date(),
      metadata,
    };

    this.userMetrics.push(metric);
    this.checkFlushThreshold();
  }

  // Add a business metric
  addBusinessMetric(event: string, value: number, context?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const metric: BusinessMetric = {
      event,
      value,
      timestamp: new Date(),
      context,
    };

    this.businessMetrics.push(metric);
    this.checkFlushThreshold();
  }

  // Check if we need to flush metrics
  private checkFlushThreshold(): void {
    const totalMetrics = this.metrics.length + this.performanceMetrics.length + 
                        this.userMetrics.length + this.businessMetrics.length;
    
    if (totalMetrics >= this.batchSize) {
      this.flush();
    }
  }

  // Flush all metrics to external services
  async flush(): Promise<void> {
    if (this.metrics.length === 0 && this.performanceMetrics.length === 0 && 
        this.userMetrics.length === 0 && this.businessMetrics.length === 0) {
      return;
    }

    const payload = {
      metrics: [...this.metrics],
      performanceMetrics: [...this.performanceMetrics],
      userMetrics: [...this.userMetrics],
      businessMetrics: [...this.businessMetrics],
      timestamp: new Date().toISOString(),
    };

    try {
      // Send to analytics service
      await this.sendToAnalytics(payload);
      
      // Send to monitoring service
      await this.sendToMonitoring(payload);
      
      // Clear metrics after successful send
      this.clearMetrics();
    } catch (error) {
      console.error('Failed to flush metrics:', error);
    }
  }

  // Send metrics to analytics service
  private async sendToAnalytics(payload: any): Promise<void> {
    // Google Analytics 4
    if (typeof window !== 'undefined' && (window as any).gtag) {
      payload.metrics.forEach((metric: MetricData) => {
        (window as any).gtag('event', 'metric', {
          metric_name: metric.name,
          metric_value: metric.value,
          metric_tags: metric.tags,
        });
      });
    }

    // Custom analytics endpoint
    try {
      await fetch('/api/analytics/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
    } catch (error) {
      console.error('Failed to send metrics to analytics:', error);
    }
  }

  // Send metrics to monitoring service
  private async sendToMonitoring(payload: any): Promise<void> {
    try {
      await fetch('/api/monitoring/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
    } catch (error) {
      console.error('Failed to send metrics to monitoring:', error);
    }
  }

  // Clear all metrics
  private clearMetrics(): void {
    this.metrics = [];
    this.performanceMetrics = [];
    this.userMetrics = [];
    this.businessMetrics = [];
  }

  // Get current metrics (for debugging)
  getMetrics(): {
    metrics: MetricData[];
    performanceMetrics: PerformanceMetric[];
    userMetrics: UserMetric[];
    businessMetrics: BusinessMetric[];
  } {
    return {
      metrics: [...this.metrics],
      performanceMetrics: [...this.performanceMetrics],
      userMetrics: [...this.userMetrics],
      businessMetrics: [...this.businessMetrics],
    };
  }

  // Get metrics summary
  getMetricsSummary(): {
    totalMetrics: number;
    performanceMetrics: number;
    userMetrics: number;
    businessMetrics: number;
  } {
    return {
      totalMetrics: this.metrics.length,
      performanceMetrics: this.performanceMetrics.length,
      userMetrics: this.userMetrics.length,
      businessMetrics: this.businessMetrics.length,
    };
  }
}

// Global metrics collector instance
export const metricsCollector = new MetricsCollector();

// Convenience functions
export function trackMetric(name: string, value: number, tags?: Record<string, string>, metadata?: Record<string, any>): void {
  metricsCollector.addMetric(name, value, tags, metadata);
}

export function trackPerformance(name: string, value: number, unit: string, context?: Record<string, any>): void {
  metricsCollector.addPerformanceMetric(name, value, unit, context);
}

export function trackUserAction(userId: string, action: string, metadata?: Record<string, any>): void {
  metricsCollector.addUserMetric(userId, action, metadata);
}

export function trackBusinessEvent(event: string, value: number, context?: Record<string, any>): void {
  metricsCollector.addBusinessMetric(event, value, context);
}

// Performance monitoring utilities
export function measurePerformance<T>(name: string, fn: () => T): T {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  
  trackPerformance(name, end - start, 'ms');
  return result;
}

export async function measureAsyncPerformance<T>(name: string, fn: () => Promise<T>): Promise<T> {
  const start = performance.now();
  const result = await fn();
  const end = performance.now();
  
  trackPerformance(name, end - start, 'ms');
  return result;
}

// Web Vitals tracking
export function trackWebVitals(): void {
  if (typeof window === 'undefined') return;

  // Track LCP (Largest Contentful Paint)
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const lastEntry = entries[entries.length - 1];
    trackPerformance('lcp', lastEntry.startTime, 'ms');
  }).observe({ entryTypes: ['largest-contentful-paint'] });

  // Track FID (First Input Delay) - Note: FID is deprecated, using INP instead
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    entries.forEach((entry) => {
      // FID is calculated as the time between first input and when the browser can process it
      // Since processingStart is not available, we'll track the startTime as a proxy
      trackPerformance('fid', entry.startTime, 'ms');
    });
  }).observe({ entryTypes: ['first-input'] });

  // Track CLS (Cumulative Layout Shift)
  let clsValue = 0;
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    entries.forEach((entry) => {
      if (!(entry as any).hadRecentInput) {
        clsValue += (entry as any).value;
      }
    });
    trackPerformance('cls', clsValue, 'score');
  }).observe({ entryTypes: ['layout-shift'] });

  // Track FCP (First Contentful Paint)
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    entries.forEach((entry) => {
      trackPerformance('fcp', entry.startTime, 'ms');
    });
  }).observe({ entryTypes: ['paint'] });
}

// Error tracking
export function trackError(error: Error, context?: Record<string, any>): void {
  trackMetric('error', 1, { 
    error_type: error.name,
    error_message: error.message,
  }, context);
}

// API call tracking
export function trackApiCall(method: string, url: string, statusCode: number, duration: number, context?: Record<string, any>): void {
  trackMetric('api_call', 1, {
    method,
    url,
    status_code: statusCode.toString(),
  }, {
    duration,
    ...context,
  });
}

// Page view tracking
export function trackPageView(page: string, context?: Record<string, any>): void {
  trackMetric('page_view', 1, { page }, context);
}

// User engagement tracking
export function trackUserEngagement(action: string, element: string, context?: Record<string, any>): void {
  trackUserAction('current-user', action, {
    element,
    ...context,
  });
}

// Business metrics tracking
export function trackConversion(event: string, value: number, context?: Record<string, any>): void {
  trackBusinessEvent(event, value, context);
}

// Initialize metrics collection
export function initializeMetrics(): void {
  // Track Web Vitals
  trackWebVitals();
  
  // Track page views
  if (typeof window !== 'undefined') {
    trackPageView(window.location.pathname);
  }
  
  // Track errors
  if (typeof window !== 'undefined') {
    window.addEventListener('error', (event) => {
      trackError(event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });
    
    window.addEventListener('unhandledrejection', (event) => {
      trackError(new Error(event.reason), {
        type: 'unhandledrejection',
      });
    });
  }
}
