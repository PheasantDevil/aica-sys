import { useAnalytics } from '@/lib/analytics';

export interface AnalyticsEvent {
  eventName: string;
  parameters?: Record<string, any>;
  userId?: string;
  sessionId?: string;
  timestamp?: Date;
}

export interface UserProperties {
  userId?: string;
  email?: string;
  name?: string;
  subscription?: string;
  signupDate?: Date;
  lastActive?: Date;
  country?: string;
  device?: string;
  browser?: string;
  referrer?: string;
}

export interface PageViewEvent {
  pageTitle: string;
  pagePath: string;
  pageUrl: string;
  referrer?: string;
  userAgent?: string;
  viewport?: {
    width: number;
    height: number;
  };
  timestamp?: Date;
}

export interface ConversionEvent {
  conversionType: 'signup' | 'purchase' | 'download' | 'contact' | 'custom';
  value?: number;
  currency?: string;
  items?: Array<{
    id: string;
    name: string;
    category?: string;
    quantity?: number;
    price?: number;
  }>;
  metadata?: Record<string, any>;
}

export interface EcommerceEvent {
  eventType: 'purchase' | 'add_to_cart' | 'remove_from_cart' | 'view_item' | 'begin_checkout';
  transactionId?: string;
  value?: number;
  currency?: string;
  items?: Array<{
    id: string;
    name: string;
    category?: string;
    quantity?: number;
    price?: number;
  }>;
}

class EnhancedAnalyticsService {
  private analytics = useAnalytics();
  private sessionId: string;
  private userId?: string;
  private userProperties: UserProperties = {};
  private pageViews: PageViewEvent[] = [];
  private events: AnalyticsEvent[] = [];

  constructor() {
    this.sessionId = this.generateSessionId();
    this.loadUserData();
    this.initializeTracking();
  }

  /**
   * ユーザープロパティを設定
   */
  setUserProperties(properties: UserProperties): void {
    this.userProperties = { ...this.userProperties, ...properties };
    this.userId = properties.userId;
    this.saveUserData();

    // Google Analytics 4に送信
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('config', 'GA_MEASUREMENT_ID', {
        user_id: this.userId,
        custom_map: {
          user_properties: this.userProperties,
        },
      });
    }
  }

  /**
   * ページビューを追跡
   */
  trackPageView(pageData: Omit<PageViewEvent, 'timestamp'>): void {
    const pageView: PageViewEvent = {
      ...pageData,
      timestamp: new Date(),
    };

    this.pageViews.push(pageView);

    // Google Analytics 4に送信
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'page_view', {
        page_title: pageData.pageTitle,
        page_location: pageData.pageUrl,
        page_path: pageData.pagePath,
        referrer: pageData.referrer,
      });
    }

    // カスタムアナリティクスに送信
    this.analytics.trackPageView(pageData.pagePath, {
      title: pageData.pageTitle,
      url: pageData.pageUrl,
      referrer: pageData.referrer,
    });
  }

  /**
   * カスタムイベントを追跡
   */
  trackEvent(eventName: string, parameters?: Record<string, any>): void {
    const event: AnalyticsEvent = {
      eventName,
      parameters,
      userId: this.userId,
      sessionId: this.sessionId,
      timestamp: new Date(),
    };

    this.events.push(event);

    // Google Analytics 4に送信
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', eventName, {
        ...parameters,
        user_id: this.userId,
        session_id: this.sessionId,
      });
    }

    // カスタムアナリティクスに送信
    this.analytics.trackEvent(eventName, parameters);
  }

  /**
   * コンバージョンを追跡
   */
  trackConversion(conversion: ConversionEvent): void {
    this.trackEvent('conversion', {
      conversion_type: conversion.conversionType,
      value: conversion.value,
      currency: conversion.currency,
      items: conversion.items,
      ...conversion.metadata,
    });

    // Google Analytics 4のコンバージョンイベント
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'conversion', {
        event_category: 'conversion',
        event_label: conversion.conversionType,
        value: conversion.value,
        currency: conversion.currency,
      });
    }
  }

  /**
   * 電子商取引イベントを追跡
   */
  trackEcommerce(ecommerce: EcommerceEvent): void {
    this.trackEvent('ecommerce', {
      event_type: ecommerce.eventType,
      transaction_id: ecommerce.transactionId,
      value: ecommerce.value,
      currency: ecommerce.currency,
      items: ecommerce.items,
    });

    // Google Analytics 4の電子商取引イベント
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', ecommerce.eventType, {
        transaction_id: ecommerce.transactionId,
        value: ecommerce.value,
        currency: ecommerce.currency,
        items: ecommerce.items,
      });
    }
  }

  /**
   * ユーザーエンゲージメントを追跡
   */
  trackEngagement(action: string, element?: string, metadata?: Record<string, any>): void {
    this.trackEvent('engagement', {
      action,
      element,
      ...metadata,
    });
  }

  /**
   * エラーを追跡
   */
  trackError(error: Error, context?: string, metadata?: Record<string, any>): void {
    this.trackEvent('error', {
      error_message: error.message,
      error_stack: error.stack,
      context,
      ...metadata,
    });
  }

  /**
   * パフォーマンスを追跡
   */
  trackPerformance(metric: string, value: number, metadata?: Record<string, any>): void {
    this.trackEvent('performance', {
      metric,
      value,
      ...metadata,
    });

    // Google Analytics 4のカスタムメトリクス
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'custom_metric', {
        metric_name: metric,
        metric_value: value,
        ...metadata,
      });
    }
  }

  /**
   * セッション情報を取得
   */
  getSessionInfo(): {
    sessionId: string;
    userId?: string;
    startTime: Date;
    pageViews: number;
    events: number;
  } {
    return {
      sessionId: this.sessionId,
      userId: this.userId,
      startTime: new Date(), // 実際の実装では、セッション開始時刻を記録
      pageViews: this.pageViews.length,
      events: this.events.length,
    };
  }

  /**
   * ユーザージャーニーを分析
   */
  analyzeUserJourney(): {
    totalPageViews: number;
    uniquePages: number;
    averageTimeOnPage: number;
    bounceRate: number;
    conversionEvents: number;
  } {
    const uniquePages = new Set(this.pageViews.map(pv => pv.pagePath)).size;
    const conversionEvents = this.events.filter(e => 
      e.eventName === 'conversion'
    ).length;

    // 簡易的な分析（実際の実装では、より詳細な分析が必要）
    return {
      totalPageViews: this.pageViews.length,
      uniquePages,
      averageTimeOnPage: 0, // 実際の実装では、ページ滞在時間を計算
      bounceRate: 0, // 実際の実装では、直帰率を計算
      conversionEvents,
    };
  }

  /**
   * リアルタイム分析データを取得
   */
  getRealtimeData(): {
    activeUsers: number;
    currentPage: string;
    topPages: Array<{ path: string; views: number }>;
    recentEvents: AnalyticsEvent[];
  } {
    const pageViewCounts = new Map<string, number>();
    this.pageViews.forEach(pv => {
      pageViewCounts.set(pv.pagePath, (pageViewCounts.get(pv.pagePath) || 0) + 1);
    });

    const topPages = Array.from(pageViewCounts.entries())
      .map(([path, views]) => ({ path, views }))
      .sort((a, b) => b.views - a.views)
      .slice(0, 5);

    return {
      activeUsers: 1, // 現在のユーザー
      currentPage: this.pageViews[this.pageViews.length - 1]?.pagePath || '',
      topPages,
      recentEvents: this.events.slice(-10),
    };
  }

  /**
   * データをエクスポート
   */
  exportData(): {
    sessionInfo: any;
    pageViews: PageViewEvent[];
    events: AnalyticsEvent[];
    userProperties: UserProperties;
  } {
    return {
      sessionInfo: this.getSessionInfo(),
      pageViews: this.pageViews,
      events: this.events,
      userProperties: this.userProperties,
    };
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeTracking(): void {
    if (typeof window === 'undefined') return;

    // ページビューの自動追跡
    this.trackPageView({
      pageTitle: document.title,
      pagePath: window.location.pathname,
      pageUrl: window.location.href,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
    });

    // ページ遷移の監視
    window.addEventListener('popstate', () => {
      this.trackPageView({
        pageTitle: document.title,
        pagePath: window.location.pathname,
        pageUrl: window.location.href,
        referrer: document.referrer,
      });
    });

    // エラーの監視
    window.addEventListener('error', (event) => {
      this.trackError(new Error(event.message), 'window_error', {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });

    // パフォーマンスの監視
    if ('performance' in window) {
      window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (perfData) {
          this.trackPerformance('page_load_time', perfData.loadEventEnd - perfData.loadEventStart);
          this.trackPerformance('dom_content_loaded', perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart);
          this.trackPerformance('first_paint', perfData.responseEnd - perfData.requestStart);
        }
      });
    }
  }

  private loadUserData(): void {
    try {
      const saved = localStorage.getItem('analytics_user_data');
      if (saved) {
        const data = JSON.parse(saved);
        this.userProperties = data.userProperties || {};
        this.userId = data.userId;
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }

  private saveUserData(): void {
    try {
      localStorage.setItem('analytics_user_data', JSON.stringify({
        userProperties: this.userProperties,
        userId: this.userId,
      }));
    } catch (error) {
      console.error('Error saving user data:', error);
    }
  }
}

// グローバルインスタンス
const enhancedAnalyticsService = new EnhancedAnalyticsService();

/**
 * 高度なアナリティクス用のReactフック
 */
export function useEnhancedAnalytics() {
  const setUserProperties = (properties: UserProperties) => {
    enhancedAnalyticsService.setUserProperties(properties);
  };

  const trackPageView = (pageData: Omit<PageViewEvent, 'timestamp'>) => {
    enhancedAnalyticsService.trackPageView(pageData);
  };

  const trackEvent = (eventName: string, parameters?: Record<string, any>) => {
    enhancedAnalyticsService.trackEvent(eventName, parameters);
  };

  const trackConversion = (conversion: ConversionEvent) => {
    enhancedAnalyticsService.trackConversion(conversion);
  };

  const trackEcommerce = (ecommerce: EcommerceEvent) => {
    enhancedAnalyticsService.trackEcommerce(ecommerce);
  };

  const trackEngagement = (action: string, element?: string, metadata?: Record<string, any>) => {
    enhancedAnalyticsService.trackEngagement(action, element, metadata);
  };

  const trackError = (error: Error, context?: string, metadata?: Record<string, any>) => {
    enhancedAnalyticsService.trackError(error, context, metadata);
  };

  const trackPerformance = (metric: string, value: number, metadata?: Record<string, any>) => {
    enhancedAnalyticsService.trackPerformance(metric, value, metadata);
  };

  const getSessionInfo = () => {
    return enhancedAnalyticsService.getSessionInfo();
  };

  const analyzeUserJourney = () => {
    return enhancedAnalyticsService.analyzeUserJourney();
  };

  const getRealtimeData = () => {
    return enhancedAnalyticsService.getRealtimeData();
  };

  const exportData = () => {
    return enhancedAnalyticsService.exportData();
  };

  return {
    setUserProperties,
    trackPageView,
    trackEvent,
    trackConversion,
    trackEcommerce,
    trackEngagement,
    trackError,
    trackPerformance,
    getSessionInfo,
    analyzeUserJourney,
    getRealtimeData,
    exportData,
  };
}

export default enhancedAnalyticsService;
