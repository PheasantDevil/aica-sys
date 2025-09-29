import { useState, useEffect } from 'react';

export interface ABTestConfig {
  id: string;
  name: string;
  description: string;
  variants: ABTestVariant[];
  trafficAllocation: number; // 0-100 (percentage of users who see this test)
  startDate: Date;
  endDate?: Date;
  isActive: boolean;
  targetAudience?: {
    userTypes?: string[];
    countries?: string[];
    devices?: string[];
  };
}

export interface ABTestVariant {
  id: string;
  name: string;
  weight: number; // 0-100 (percentage of traffic for this variant)
  config: Record<string, any>;
}

export interface ABTestResult {
  testId: string;
  variantId: string;
  userId?: string;
  sessionId: string;
  timestamp: Date;
  conversionEvents: string[];
  metadata?: Record<string, any>;
}

export interface ConversionEvent {
  eventType: string;
  value?: number;
  metadata?: Record<string, any>;
  timestamp: Date;
}

class ABTestingService {
  private tests: Map<string, ABTestConfig> = new Map();
  private results: ABTestResult[] = [];
  private sessionId: string;
  private userId?: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.loadTests();
    this.loadResults();
  }

  /**
   * A/Bテストを登録
   */
  registerTest(test: ABTestConfig): void {
    this.tests.set(test.id, test);
    this.saveTests();
  }

  /**
   * ユーザーIDを設定
   */
  setUserId(userId: string): void {
    this.userId = userId;
  }

  /**
   * テストのバリアントを取得
   */
  getVariant(testId: string): string | null {
    const test = this.tests.get(testId);
    if (!test || !test.isActive) {
      return null;
    }

    // トラフィック配分をチェック
    if (!this.isUserInTrafficAllocation(test)) {
      return null;
    }

    // ターゲットオーディエンスをチェック
    if (!this.isUserInTargetAudience(test)) {
      return null;
    }

    // 日付範囲をチェック
    if (!this.isTestInDateRange(test)) {
      return null;
    }

    // バリアントを決定
    const variant = this.selectVariant(test);
    
    // 結果を記録
    this.recordTestAssignment(testId, variant.id);

    return variant.id;
  }

  /**
   * コンバージョンイベントを記録
   */
  recordConversion(testId: string, event: ConversionEvent): void {
    const result = this.results.find(r => 
      r.testId === testId && 
      r.sessionId === this.sessionId
    );

    if (result) {
      result.conversionEvents.push(event.eventType);
      this.saveResults();
    }
  }

  /**
   * テスト結果を取得
   */
  getTestResults(testId: string): {
    totalUsers: number;
    variants: Array<{
      variantId: string;
      users: number;
      conversions: number;
      conversionRate: number;
    }>;
  } {
    const testResults = this.results.filter(r => r.testId === testId);
    const variantStats = new Map<string, { users: Set<string>, conversions: number }>();

    testResults.forEach(result => {
      const userKey = result.userId || result.sessionId;
      
      if (!variantStats.has(result.variantId)) {
        variantStats.set(result.variantId, { users: new Set(), conversions: 0 });
      }

      const stats = variantStats.get(result.variantId)!;
      stats.users.add(userKey);
      stats.conversions += result.conversionEvents.length;
    });

    const variants = Array.from(variantStats.entries()).map(([variantId, stats]) => ({
      variantId,
      users: stats.users.size,
      conversions: stats.conversions,
      conversionRate: stats.users.size > 0 ? (stats.conversions / stats.users.size) * 100 : 0,
    }));

    return {
      totalUsers: testResults.length,
      variants,
    };
  }

  /**
   * 統計的有意性を計算
   */
  calculateStatisticalSignificance(testId: string): {
    isSignificant: boolean;
    confidenceLevel: number;
    pValue: number;
  } {
    const results = this.getTestResults(testId);
    
    if (results.variants.length < 2) {
      return { isSignificant: false, confidenceLevel: 0, pValue: 1 };
    }

    // 簡易的な統計的有意性計算（実際の実装ではより詳細な統計テストが必要）
    const [variantA, variantB] = results.variants;
    const totalUsers = variantA.users + variantB.users;
    const totalConversions = variantA.conversions + variantB.conversions;

    if (totalUsers < 100) {
      return { isSignificant: false, confidenceLevel: 0, pValue: 1 };
    }

    // 簡易的なZ-test
    const p1 = variantA.conversions / variantA.users;
    const p2 = variantB.conversions / variantB.users;
    const pooledP = totalConversions / totalUsers;
    
    const se = Math.sqrt(pooledP * (1 - pooledP) * (1/variantA.users + 1/variantB.users));
    const z = Math.abs(p1 - p2) / se;
    
    // 95%信頼区間での有意性
    const isSignificant = z > 1.96;
    const confidenceLevel = isSignificant ? 95 : 0;
    const pValue = Math.max(0, 1 - (z / 1.96));

    return { isSignificant, confidenceLevel, pValue };
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private isUserInTrafficAllocation(test: ABTestConfig): boolean {
    const hash = this.hashString(`${this.userId || this.sessionId}_${test.id}`);
    return (hash % 100) < test.trafficAllocation;
  }

  private isUserInTargetAudience(test: ABTestConfig): boolean {
    if (!test.targetAudience) {
      return true;
    }

    // 簡易的なターゲットオーディエンスチェック
    // 実際の実装では、より詳細なユーザー属性をチェック
    return true;
  }

  private isTestInDateRange(test: ABTestConfig): boolean {
    const now = new Date();
    return now >= test.startDate && (!test.endDate || now <= test.endDate);
  }

  private selectVariant(test: ABTestConfig): ABTestVariant {
    const hash = this.hashString(`${this.userId || this.sessionId}_${test.id}_variant`);
    const randomValue = hash % 100;
    
    let cumulativeWeight = 0;
    for (const variant of test.variants) {
      cumulativeWeight += variant.weight;
      if (randomValue < cumulativeWeight) {
        return variant;
      }
    }

    // フォールバック
    return test.variants[0];
  }

  private recordTestAssignment(testId: string, variantId: string): void {
    const result: ABTestResult = {
      testId,
      variantId,
      userId: this.userId,
      sessionId: this.sessionId,
      timestamp: new Date(),
      conversionEvents: [],
    };

    this.results.push(result);
    this.saveResults();
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  private loadTests(): void {
    try {
      const saved = localStorage.getItem('ab_tests');
      if (saved) {
        const tests = JSON.parse(saved);
        tests.forEach((test: ABTestConfig) => {
          this.tests.set(test.id, {
            ...test,
            startDate: new Date(test.startDate),
            endDate: test.endDate ? new Date(test.endDate) : undefined,
          });
        });
      }
    } catch (error) {
      console.error('Error loading A/B tests:', error);
    }
  }

  private saveTests(): void {
    try {
      const tests = Array.from(this.tests.values());
      localStorage.setItem('ab_tests', JSON.stringify(tests));
    } catch (error) {
      console.error('Error saving A/B tests:', error);
    }
  }

  private loadResults(): void {
    try {
      const saved = localStorage.getItem('ab_test_results');
      if (saved) {
        const results = JSON.parse(saved);
        this.results = results.map((result: any) => ({
          ...result,
          timestamp: new Date(result.timestamp),
        }));
      }
    } catch (error) {
      console.error('Error loading A/B test results:', error);
    }
  }

  private saveResults(): void {
    try {
      localStorage.setItem('ab_test_results', JSON.stringify(this.results));
    } catch (error) {
      console.error('Error saving A/B test results:', error);
    }
  }
}

// グローバルインスタンス
const abTestingService = new ABTestingService();

/**
 * A/Bテスト用のReactフック
 */
export function useABTest(testId: string) {
  const [variant, setVariant] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const testVariant = abTestingService.getVariant(testId);
    setVariant(testVariant);
    setIsLoading(false);
  }, [testId]);

  const recordConversion = (eventType: string, value?: number, metadata?: Record<string, any>) => {
    abTestingService.recordConversion(testId, {
      eventType,
      value,
      metadata,
      timestamp: new Date(),
    });
  };

  return {
    variant,
    isLoading,
    recordConversion,
  };
}

/**
 * A/Bテスト管理用のフック
 */
export function useABTestManagement() {
  const [tests, setTests] = useState<ABTestConfig[]>([]);

  useEffect(() => {
    // テスト一覧を取得
    const testList = Array.from(abTestingService['tests'].values());
    setTests(testList);
  }, []);

  const createTest = (test: ABTestConfig) => {
    abTestingService.registerTest(test);
    setTests(prev => [...prev, test]);
  };

  const getTestResults = (testId: string) => {
    return abTestingService.getTestResults(testId);
  };

  const getStatisticalSignificance = (testId: string) => {
    return abTestingService.calculateStatisticalSignificance(testId);
  };

  return {
    tests,
    createTest,
    getTestResults,
    getStatisticalSignificance,
  };
}

export default abTestingService;
