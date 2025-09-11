'use client';

declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}

export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_ID || '';

export class Analytics {
  private static isInitialized = false;

  static init() {
    if (typeof window === 'undefined' || this.isInitialized) return;

    // Load Google Analytics script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`;
    document.head.appendChild(script);

    // Initialize gtag
    window.gtag = function() {
      (window as any).dataLayer = (window as any).dataLayer || [];
      (window as any).dataLayer.push(arguments);
    };

    window.gtag('js', new Date());
    window.gtag('config', GA_TRACKING_ID, {
      page_title: document.title,
      page_location: window.location.href,
    });

    this.isInitialized = true;
  }

  static pageview(url: string, title?: string) {
    if (typeof window === 'undefined' || !window.gtag) return;

    window.gtag('config', GA_TRACKING_ID, {
      page_path: url,
      page_title: title || document.title,
    });
  }

  static event(action: string, parameters?: Record<string, any>) {
    if (typeof window === 'undefined' || !window.gtag) return;

    window.gtag('event', action, {
      event_category: parameters?.category || 'general',
      event_label: parameters?.label,
      value: parameters?.value,
      ...parameters,
    });
  }

  static trackPageView(url: string, title?: string) {
    this.event('page_view', {
      page_title: title || document.title,
      page_location: url,
    });
  }

  static trackUserEngagement(action: string, contentId?: string, contentType?: string) {
    this.event('user_engagement', {
      engagement_type: action,
      content_id: contentId,
      content_type: contentType,
    });
  }

  static trackContentInteraction(action: string, contentId: string, contentType: string) {
    this.event('content_interaction', {
      interaction_type: action,
      content_id: contentId,
      content_type: contentType,
    });
  }

  static trackSubscription(action: string, planType: string, value?: number) {
    this.event('subscription', {
      subscription_action: action,
      plan_type: planType,
      value: value,
      currency: 'JPY',
    });
  }

  static trackSearch(searchTerm: string, resultsCount?: number) {
    this.event('search', {
      search_term: searchTerm,
      results_count: resultsCount,
    });
  }

  static trackError(errorType: string, errorMessage: string, fatal: boolean = false) {
    this.event('exception', {
      description: errorMessage,
      fatal: fatal,
      error_type: errorType,
    });
  }

  static trackConversion(conversionType: string, value?: number, currency: string = 'JPY') {
    this.event('conversion', {
      conversion_type: conversionType,
      value: value,
      currency: currency,
    });
  }

  static trackCustomEvent(eventName: string, parameters?: Record<string, any>) {
    this.event(eventName, parameters);
  }

  // E-commerce tracking
  static trackPurchase(transactionId: string, value: number, currency: string = 'JPY', items?: any[]) {
    this.event('purchase', {
      transaction_id: transactionId,
      value: value,
      currency: currency,
      items: items,
    });
  }

  static trackAddToCart(itemId: string, itemName: string, category: string, value: number) {
    this.event('add_to_cart', {
      currency: 'JPY',
      value: value,
      items: [{
        item_id: itemId,
        item_name: itemName,
        item_category: category,
        price: value,
        quantity: 1,
      }],
    });
  }

  // User properties
  static setUserProperties(properties: Record<string, any>) {
    if (typeof window === 'undefined' || !window.gtag) return;

    window.gtag('config', GA_TRACKING_ID, {
      user_properties: properties,
    });
  }

  static setUserId(userId: string) {
    if (typeof window === 'undefined' || !window.gtag) return;

    window.gtag('config', GA_TRACKING_ID, {
      user_id: userId,
    });
  }

  // Performance tracking
  static trackWebVitals(metric: any) {
    this.event('web_vitals', {
      metric_name: metric.name,
      metric_value: Math.round(metric.value),
      metric_delta: Math.round(metric.delta),
      metric_id: metric.id,
    });
  }

  // A/B testing
  static trackExperiment(experimentId: string, variant: string) {
    this.event('experiment', {
      experiment_id: experimentId,
      variant: variant,
    });
  }
}

// React hooks for analytics
export function useAnalytics() {
  const trackEvent = (action: string, parameters?: Record<string, any>) => {
    Analytics.event(action, parameters);
  };

  const trackPageView = (url: string, title?: string) => {
    Analytics.trackPageView(url, title);
  };

  const trackContentInteraction = (action: string, contentId: string, contentType: string) => {
    Analytics.trackContentInteraction(action, contentId, contentType);
  };

  const trackUserEngagement = (action: string, contentId?: string, contentType?: string) => {
    Analytics.trackUserEngagement(action, contentId, contentType);
  };

  const trackSearch = (searchTerm: string, resultsCount?: number) => {
    Analytics.trackSearch(searchTerm, resultsCount);
  };

  const trackError = (errorType: string, errorMessage: string, fatal?: boolean) => {
    Analytics.trackError(errorType, errorMessage, fatal);
  };

  const trackConversion = (conversionType: string, value?: number, currency?: string) => {
    Analytics.trackConversion(conversionType, value, currency);
  };

  return {
    trackEvent,
    trackPageView,
    trackContentInteraction,
    trackUserEngagement,
    trackSearch,
    trackError,
    trackConversion,
  };
}

// Performance monitoring integration
export function trackWebVitals() {
  if (typeof window === 'undefined') return;

  // Track Core Web Vitals
  const trackCLS = () => {
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
        Analytics.trackWebVitals({
          name: 'CLS',
          value: clsValue,
          delta: clsValue,
          id: 'cls-' + Date.now(),
        });
        observer.disconnect();
      }
    });
  };

  const trackLCP = () => {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        Analytics.trackWebVitals({
          name: 'LCP',
          value: entry.startTime,
          delta: entry.startTime,
          id: 'lcp-' + Date.now(),
        });
      }
    });
    
    observer.observe({ entryTypes: ['largest-contentful-paint'] });
  };

  const trackFID = () => {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        Analytics.trackWebVitals({
          name: 'FID',
          value: (entry as any).processingStart - entry.startTime,
          delta: (entry as any).processingStart - entry.startTime,
          id: 'fid-' + Date.now(),
        });
      }
    });
    
    observer.observe({ entryTypes: ['first-input'] });
  };

  trackCLS();
  trackLCP();
  trackFID();
}