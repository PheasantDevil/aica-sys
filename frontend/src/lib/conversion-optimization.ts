export interface ConversionGoal {
  id: string;
  name: string;
  type: 'signup' | 'purchase' | 'download' | 'contact' | 'custom';
  value?: number;
  isActive: boolean;
}

export interface ConversionEvent {
  goalId: string;
  userId?: string;
  sessionId: string;
  value?: number;
  metadata?: Record<string, any>;
  timestamp: Date;
}

export interface ConversionFunnel {
  id: string;
  name: string;
  steps: ConversionStep[];
  isActive: boolean;
}

export interface ConversionStep {
  id: string;
  name: string;
  type: 'page_view' | 'click' | 'form_submit' | 'custom';
  selector?: string; // CSS selector for tracking
  url?: string; // URL pattern for page view tracking
  isRequired: boolean;
  order: number;
}

export interface FunnelAnalytics {
  funnelId: string;
  totalUsers: number;
  steps: Array<{
    stepId: string;
    users: number;
    conversionRate: number;
    dropOffRate: number;
  }>;
  overallConversionRate: number;
}

class ConversionOptimizationService {
  private goals: Map<string, ConversionGoal> = new Map();
  private funnels: Map<string, ConversionFunnel> = new Map();
  private events: ConversionEvent[] = [];
  private sessionId: string;
  private userId?: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.loadData();
  }

  /**
   * コンバージョン目標を設定
   */
  setGoal(goal: ConversionGoal): void {
    this.goals.set(goal.id, goal);
    this.saveData();
  }

  /**
   * コンバージョンファネルを設定
   */
  setFunnel(funnel: ConversionFunnel): void {
    this.funnels.set(funnel.id, funnel);
    this.saveData();
  }

  /**
   * ユーザーIDを設定
   */
  setUserId(userId: string): void {
    this.userId = userId;
  }

  /**
   * コンバージョンイベントを記録
   */
  recordConversion(goalId: string, value?: number, metadata?: Record<string, any>): void {
    const goal = this.goals.get(goalId);
    if (!goal || !goal.isActive) {
      return;
    }

    const event: ConversionEvent = {
      goalId,
      userId: this.userId,
      sessionId: this.sessionId,
      value,
      metadata,
      timestamp: new Date(),
    };

    this.events.push(event);
    this.saveData();

    // アナリティクスに送信
    this.sendToAnalytics(event);
  }

  /**
   * ファネルステップを記録
   */
  recordFunnelStep(funnelId: string, stepId: string, metadata?: Record<string, any>): void {
    const funnel = this.funnels.get(funnelId);
    if (!funnel || !funnel.isActive) {
      return;
    }

    const step = funnel.steps.find(s => s.id === stepId);
    if (!step) {
      return;
    }

    // ステップを記録
    this.recordConversion(`funnel_${funnelId}_${stepId}`, undefined, {
      ...metadata,
      funnelId,
      stepId,
      stepName: step.name,
    });
  }

  /**
   * ファネル分析を取得
   */
  getFunnelAnalytics(funnelId: string): FunnelAnalytics | null {
    const funnel = this.funnels.get(funnelId);
    if (!funnel) {
      return null;
    }

    const funnelEvents = this.events.filter(e => 
      e.goalId.startsWith(`funnel_${funnelId}_`)
    );

    const stepAnalytics = funnel.steps.map(step => {
      const stepEvents = funnelEvents.filter(e => 
        e.goalId === `funnel_${funnelId}_${step.id}`
      );
      
      const uniqueUsers = new Set(stepEvents.map(e => e.userId || e.sessionId));
      const users = uniqueUsers.size;

      return {
        stepId: step.id,
        users,
        conversionRate: 0, // 後で計算
        dropOffRate: 0, // 後で計算
      };
    });

    // コンバージョン率とドロップオフ率を計算
    for (let i = 0; i < stepAnalytics.length; i++) {
      const currentStep = stepAnalytics[i];
      const previousStep = i > 0 ? stepAnalytics[i - 1] : null;

      if (previousStep) {
        currentStep.conversionRate = previousStep.users > 0 
          ? (currentStep.users / previousStep.users) * 100 
          : 0;
        currentStep.dropOffRate = previousStep.users > 0 
          ? ((previousStep.users - currentStep.users) / previousStep.users) * 100 
          : 0;
      } else {
        currentStep.conversionRate = 100;
        currentStep.dropOffRate = 0;
      }
    }

    const totalUsers = stepAnalytics[0]?.users || 0;
    const finalStepUsers = stepAnalytics[stepAnalytics.length - 1]?.users || 0;
    const overallConversionRate = totalUsers > 0 
      ? (finalStepUsers / totalUsers) * 100 
      : 0;

    return {
      funnelId,
      totalUsers,
      steps: stepAnalytics,
      overallConversionRate,
    };
  }

  /**
   * コンバージョン率を取得
   */
  getConversionRate(goalId: string, timeRange?: { start: Date; end: Date }): number {
    const goal = this.goals.get(goalId);
    if (!goal) {
      return 0;
    }

    let events = this.events.filter(e => e.goalId === goalId);
    
    if (timeRange) {
      events = events.filter(e => 
        e.timestamp >= timeRange.start && e.timestamp <= timeRange.end
      );
    }

    const uniqueUsers = new Set(events.map(e => e.userId || e.sessionId));
    const totalSessions = this.getTotalSessions(timeRange);
    
    return totalSessions > 0 ? (uniqueUsers.size / totalSessions) * 100 : 0;
  }

  /**
   * コンバージョン価値を取得
   */
  getConversionValue(goalId: string, timeRange?: { start: Date; end: Date }): number {
    let events = this.events.filter(e => e.goalId === goalId);
    
    if (timeRange) {
      events = events.filter(e => 
        e.timestamp >= timeRange.start && e.timestamp <= timeRange.end
      );
    }

    return events.reduce((total, event) => total + (event.value || 0), 0);
  }

  /**
   * 最適化提案を生成
   */
  generateOptimizationSuggestions(funnelId: string): string[] {
    const analytics = this.getFunnelAnalytics(funnelId);
    if (!analytics) {
      return [];
    }

    const suggestions: string[] = [];

    // ドロップオフ率が高いステップを特定
    analytics.steps.forEach((step, index) => {
      if (step.dropOffRate > 50) {
        suggestions.push(
          `ステップ「${step.stepId}」でドロップオフ率が${step.dropOffRate.toFixed(1)}%と高いです。UI/UXの改善を検討してください。`
        );
      }
    });

    // 全体的なコンバージョン率が低い場合
    if (analytics.overallConversionRate < 10) {
      suggestions.push(
        `ファネルの全体的なコンバージョン率が${analytics.overallConversionRate.toFixed(1)}%と低いです。ファネル全体の見直しを検討してください。`
      );
    }

    // 特定のステップでの改善提案
    const firstStep = analytics.steps[0];
    if (firstStep && firstStep.users < 100) {
      suggestions.push(
        'ファネルの流入数が少ないです。トラフィック獲得の改善を検討してください。'
      );
    }

    return suggestions;
  }

  /**
   * 自動トラッキングを開始
   */
  startAutoTracking(): void {
    // ページビューの自動トラッキング
    this.trackPageViews();

    // クリックイベントの自動トラッキング
    this.trackClicks();

    // フォーム送信の自動トラッキング
    this.trackFormSubmissions();
  }

  private trackPageViews(): void {
    if (typeof window === 'undefined') return;

    const trackPageView = () => {
      const url = window.location.pathname;
      
      // ファネルのステップをチェック
      this.funnels.forEach(funnel => {
        funnel.steps.forEach(step => {
          if (step.type === 'page_view' && step.url && url.includes(step.url)) {
            this.recordFunnelStep(funnel.id, step.id, { url });
          }
        });
      });
    };

    // 初期ページビュー
    trackPageView();

    // ページ遷移を監視
    window.addEventListener('popstate', trackPageView);
    
    // Next.jsのルーターイベントを監視
    if (typeof window !== 'undefined' && (window as any).next) {
      (window as any).next.router.events.on('routeChangeComplete', trackPageView);
    }
  }

  private trackClicks(): void {
    if (typeof window === 'undefined') return;

    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      
      // ファネルのステップをチェック
      this.funnels.forEach(funnel => {
        funnel.steps.forEach(step => {
          if (step.type === 'click' && step.selector) {
            if (target.matches(step.selector) || target.closest(step.selector)) {
              this.recordFunnelStep(funnel.id, step.id, {
                element: target.tagName,
                text: target.textContent?.slice(0, 50),
              });
            }
          }
        });
      });
    });
  }

  private trackFormSubmissions(): void {
    if (typeof window === 'undefined') return;

    document.addEventListener('submit', (event) => {
      const form = event.target as HTMLFormElement;
      
      // ファネルのステップをチェック
      this.funnels.forEach(funnel => {
        funnel.steps.forEach(step => {
          if (step.type === 'form_submit' && step.selector) {
            if (form.matches(step.selector)) {
              this.recordFunnelStep(funnel.id, step.id, {
                formId: form.id,
                formAction: form.action,
              });
            }
          }
        });
      });
    });
  }

  private sendToAnalytics(event: ConversionEvent): void {
    // Google Analytics 4に送信
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'conversion', {
        event_category: 'conversion',
        event_label: event.goalId,
        value: event.value,
        custom_map: event.metadata,
      });
    }

    // カスタムアナリティクスに送信
    if (typeof window !== 'undefined' && (window as any).analytics) {
      (window as any).analytics.track('Conversion', {
        goalId: event.goalId,
        value: event.value,
        metadata: event.metadata,
      });
    }
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getTotalSessions(timeRange?: { start: Date; end: Date }): number {
    // 簡易的なセッション数計算
    // 実際の実装では、より詳細なセッション管理が必要
    return 1000; // 仮の値
  }

  private loadData(): void {
    try {
      const savedGoals = localStorage.getItem('conversion_goals');
      if (savedGoals) {
        const goals = JSON.parse(savedGoals);
        goals.forEach((goal: ConversionGoal) => {
          this.goals.set(goal.id, goal);
        });
      }

      const savedFunnels = localStorage.getItem('conversion_funnels');
      if (savedFunnels) {
        const funnels = JSON.parse(savedFunnels);
        funnels.forEach((funnel: ConversionFunnel) => {
          this.funnels.set(funnel.id, funnel);
        });
      }

      const savedEvents = localStorage.getItem('conversion_events');
      if (savedEvents) {
        const events = JSON.parse(savedEvents);
        this.events = events.map((event: any) => ({
          ...event,
          timestamp: new Date(event.timestamp),
        }));
      }
    } catch (error) {
      console.error('Error loading conversion data:', error);
    }
  }

  private saveData(): void {
    try {
      localStorage.setItem('conversion_goals', JSON.stringify(Array.from(this.goals.values())));
      localStorage.setItem('conversion_funnels', JSON.stringify(Array.from(this.funnels.values())));
      localStorage.setItem('conversion_events', JSON.stringify(this.events));
    } catch (error) {
      console.error('Error saving conversion data:', error);
    }
  }
}

// グローバルインスタンス
const conversionOptimizationService = new ConversionOptimizationService();

/**
 * コンバージョン最適化用のReactフック
 */
export function useConversionOptimization() {
  const recordConversion = (goalId: string, value?: number, metadata?: Record<string, any>) => {
    conversionOptimizationService.recordConversion(goalId, value, metadata);
  };

  const recordFunnelStep = (funnelId: string, stepId: string, metadata?: Record<string, any>) => {
    conversionOptimizationService.recordFunnelStep(funnelId, stepId, metadata);
  };

  const getConversionRate = (goalId: string, timeRange?: { start: Date; end: Date }) => {
    return conversionOptimizationService.getConversionRate(goalId, timeRange);
  };

  const getFunnelAnalytics = (funnelId: string) => {
    return conversionOptimizationService.getFunnelAnalytics(funnelId);
  };

  return {
    recordConversion,
    recordFunnelStep,
    getConversionRate,
    getFunnelAnalytics,
  };
}

export default conversionOptimizationService;
