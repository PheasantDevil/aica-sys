/**
 * Error Handling and Logging System
 * Centralized error management with alerting
 */

export interface ErrorLog {
  id: string;
  message: string;
  stack?: string;
  timestamp: number;
  url: string;
  userAgent: string;
  userId?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'javascript' | 'network' | 'api' | 'validation' | 'unknown';
  metadata?: Record<string, any>;
}

export interface AlertConfig {
  enabled: boolean;
  threshold: number; // Number of errors before alerting
  timeWindow: number; // Time window in milliseconds
  endpoints: string[]; // Alert endpoints
}

class ErrorHandler {
  private errors: ErrorLog[] = [];
  private alertConfig: AlertConfig = {
    enabled: true,
    threshold: 5,
    timeWindow: 300000, // 5 minutes
    endpoints: ['/api/alerts/error'],
  };

  constructor() {
    this.initializeErrorHandling();
  }

  private initializeErrorHandling() {
    if (typeof window === 'undefined') return;

    // Global error handler
    window.addEventListener('error', event => {
      this.handleError({
        message: event.message,
        stack: event.error?.stack,
        severity: 'high',
        category: 'javascript',
        metadata: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
        },
      });
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', event => {
      this.handleError({
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack,
        severity: 'high',
        category: 'javascript',
        metadata: {
          reason: event.reason,
        },
      });
    });

    // Network error handler
    this.setupNetworkErrorHandling();
  }

  private setupNetworkErrorHandling() {
    const originalFetch = window.fetch;
    const self = this;

    window.fetch = async function (...args) {
      try {
        const response = await originalFetch.apply(this, args);

        if (!response.ok) {
          self.handleError({
            message: `Network request failed: ${response.status} ${response.statusText}`,
            severity: response.status >= 500 ? 'high' : 'medium',
            category: 'network',
            metadata: {
              url: args[0],
              status: response.status,
              statusText: response.statusText,
            },
          });
        }

        return response;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        const errorStack = error instanceof Error ? error.stack : undefined;
        
        self.handleError({
          message: `Network request error: ${errorMessage}`,
          stack: errorStack,
          severity: 'high',
          category: 'network',
          metadata: {
            url: args[0],
            error: errorMessage,
          },
        });
        throw error;
      }
    };
  }

  public handleError(errorData: Partial<ErrorLog>): void {
    const error: ErrorLog = {
      id: this.generateId(),
      message: errorData.message || 'Unknown error',
      stack: errorData.stack,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      userId: this.getCurrentUserId(),
      severity: errorData.severity || 'medium',
      category: errorData.category || 'unknown',
      metadata: errorData.metadata,
    };

    this.errors.push(error);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('🚨 Error logged:', error);
    }

    // Send to analytics
    this.sendToAnalytics(error);

    // Check for alerts
    this.checkAlerts();

    // Store in localStorage for persistence
    this.persistErrors();
  }

  private generateId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentUserId(): string | undefined {
    // Get user ID from authentication context
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          return user.id;
        } catch {
          return undefined;
        }
      }
    }
    return undefined;
  }

  private async sendToAnalytics(error: ErrorLog) {
    try {
      // Send to Google Analytics 4
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'exception', {
          description: error.message,
          fatal: error.severity === 'critical',
          custom_map: {
            error_category: error.category,
            error_severity: error.severity,
            error_url: error.url,
          },
        });
      }

      // Send to custom analytics endpoint
      await fetch('/api/analytics/error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(error),
      });
    } catch (analyticsError) {
      console.warn('Failed to send error to analytics:', analyticsError);
    }
  }

  private checkAlerts() {
    if (!this.alertConfig.enabled) return;

    const now = Date.now();
    const timeWindow = this.alertConfig.timeWindow;
    const threshold = this.alertConfig.threshold;

    // Count errors in the time window
    const recentErrors = this.errors.filter(
      error => now - error.timestamp < timeWindow
    );

    if (recentErrors.length >= threshold) {
      this.sendAlert(recentErrors);
    }
  }

  private async sendAlert(errors: ErrorLog[]) {
    const alert = {
      timestamp: Date.now(),
      errorCount: errors.length,
      errors: errors.slice(-10), // Last 10 errors
      severity: this.getHighestSeverity(errors),
    };

    try {
      for (const endpoint of this.alertConfig.endpoints) {
        await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(alert),
        });
      }
    } catch (error) {
      console.error('Failed to send alert:', error);
    }
  }

  private getHighestSeverity(errors: ErrorLog[]): string {
    const severities = ['low', 'medium', 'high', 'critical'];
    let highest = 'low';

    for (const error of errors) {
      const currentIndex = severities.indexOf(error.severity);
      const highestIndex = severities.indexOf(highest);
      if (currentIndex > highestIndex) {
        highest = error.severity;
      }
    }

    return highest;
  }

  private persistErrors() {
    if (typeof window === 'undefined') return;

    try {
      const recentErrors = this.errors.slice(-50); // Keep last 50 errors
      localStorage.setItem('error_logs', JSON.stringify(recentErrors));
    } catch (error) {
      console.warn('Failed to persist errors:', error);
    }
  }

  // Public methods
  public getErrors(): ErrorLog[] {
    return [...this.errors];
  }

  public getErrorsBySeverity(severity: ErrorLog['severity']): ErrorLog[] {
    return this.errors.filter(error => error.severity === severity);
  }

  public getErrorsByCategory(category: ErrorLog['category']): ErrorLog[] {
    return this.errors.filter(error => error.category === category);
  }

  public clearErrors() {
    this.errors = [];
    if (typeof window !== 'undefined') {
      localStorage.removeItem('error_logs');
    }
  }

  public setAlertConfig(config: Partial<AlertConfig>) {
    this.alertConfig = { ...this.alertConfig, ...config };
  }

  public getErrorStats() {
    const now = Date.now();
    const last24h = now - 24 * 60 * 60 * 1000;
    const last1h = now - 60 * 60 * 1000;

    const last24hErrors = this.errors.filter(
      error => error.timestamp > last24h
    );
    const last1hErrors = this.errors.filter(error => error.timestamp > last1h);

    return {
      total: this.errors.length,
      last24h: last24hErrors.length,
      last1h: last1hErrors.length,
      bySeverity: {
        low: this.getErrorsBySeverity('low').length,
        medium: this.getErrorsBySeverity('medium').length,
        high: this.getErrorsBySeverity('high').length,
        critical: this.getErrorsBySeverity('critical').length,
      },
      byCategory: {
        javascript: this.getErrorsByCategory('javascript').length,
        network: this.getErrorsByCategory('network').length,
        api: this.getErrorsByCategory('api').length,
        validation: this.getErrorsByCategory('validation').length,
        unknown: this.getErrorsByCategory('unknown').length,
      },
    };
  }
}

// Singleton instance
export const errorHandler = new ErrorHandler();

// Export for use in components
export default errorHandler;
