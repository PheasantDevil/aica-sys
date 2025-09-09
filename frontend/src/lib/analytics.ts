// Google Analytics 4 設定
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_ID || '';

// Google Analytics スクリプトの読み込み
export const loadGA = () => {
  if (typeof window === 'undefined' || !GA_TRACKING_ID) return;

  // Google Analytics スクリプトを動的に読み込み
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`;
  document.head.appendChild(script);

  // gtag 関数を初期化
  window.dataLayer = window.dataLayer || [];
  function gtag(...args: any[]) {
    window.dataLayer.push(args);
  }
  window.gtag = gtag;

  gtag('js', new Date());
  gtag('config', GA_TRACKING_ID, {
    page_title: document.title,
    page_location: window.location.href,
  });
};

// ページビュー追跡
export const trackPageView = (url: string, title?: string) => {
  if (typeof window === 'undefined' || !window.gtag) return;

  window.gtag('config', GA_TRACKING_ID, {
    page_path: url,
    page_title: title || document.title,
  });
};

// イベント追跡
export const trackEvent = (
  action: string,
  category: string,
  label?: string,
  value?: number
) => {
  if (typeof window === 'undefined' || !window.gtag) return;

  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  });
};

// カスタムイベント
export const analyticsEvents = {
  // ユーザー登録
  signUp: (method: string) => {
    trackEvent('sign_up', 'engagement', method);
  },

  // ログイン
  signIn: (method: string) => {
    trackEvent('login', 'engagement', method);
  },

  // 記事閲覧
  viewArticle: (articleId: string, title: string) => {
    trackEvent('view_item', 'content', articleId, undefined);
    trackEvent('article_view', 'engagement', title);
  },

  // 記事検索
  searchArticles: (query: string, resultsCount: number) => {
    trackEvent('search', 'engagement', query, resultsCount);
  },

  // ニュースレター購読
  subscribeNewsletter: (newsletterId: string) => {
    trackEvent('subscribe', 'engagement', newsletterId);
  },

  // サブスクリプション開始
  startSubscription: (planId: string, value: number) => {
    trackEvent('purchase', 'ecommerce', planId, value);
  },

  // サブスクリプション変更
  changeSubscription: (fromPlan: string, toPlan: string) => {
    trackEvent('subscription_change', 'ecommerce', `${fromPlan}_to_${toPlan}`);
  },

  // サブスクリプションキャンセル
  cancelSubscription: (planId: string) => {
    trackEvent('subscription_cancel', 'ecommerce', planId);
  },

  // ダウンロード
  download: (fileName: string, fileType: string) => {
    trackEvent('file_download', 'engagement', `${fileName}.${fileType}`);
  },

  // 外部リンククリック
  clickExternalLink: (url: string, linkText: string) => {
    trackEvent('click', 'outbound', linkText);
  },

  // エラー発生
  trackError: (errorType: string, errorMessage: string) => {
    trackEvent('exception', 'error', errorType);
  },

  // パフォーマンス
  trackPerformance: (metric: string, value: number) => {
    trackEvent('timing_complete', 'performance', metric, value);
  },
};

// コンバージョン追跡
export const trackConversion = (
  conversionId: string,
  value?: number,
  currency?: string
) => {
  if (typeof window === 'undefined' || !window.gtag) return;

  window.gtag('event', 'conversion', {
    send_to: conversionId,
    value: value,
    currency: currency || 'JPY',
  });
};

// カスタムディメンション
export const setCustomDimension = (index: number, value: string) => {
  if (typeof window === 'undefined' || !window.gtag) return;

  window.gtag('config', GA_TRACKING_ID, {
    custom_map: {
      [`dimension${index}`]: value,
    },
  });
};

// ユーザープロパティ設定
export const setUserProperties = (properties: Record<string, any>) => {
  if (typeof window === 'undefined' || !window.gtag) return;

  window.gtag('config', GA_TRACKING_ID, {
    user_properties: properties,
  });
};

// ページビュー時間追跡
export const trackPageViewTime = (pageName: string, timeInSeconds: number) => {
  trackEvent('page_view_time', 'engagement', pageName, timeInSeconds);
};

// スクロール深度追跡
export const trackScrollDepth = (depth: number) => {
  trackEvent('scroll_depth', 'engagement', `${depth}%`, depth);
};

// 動的コンテンツ追跡
export const trackDynamicContent = (contentId: string, contentType: string) => {
  trackEvent('dynamic_content_view', 'content', `${contentType}_${contentId}`);
};

// 型定義
declare global {
  interface Window {
    dataLayer: any[];
    gtag: (...args: any[]) => void;
  }
}
