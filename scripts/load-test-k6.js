/**
 * K6 Load Testing Script
 * Phase 7-5: Load testing and scalability verification
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// カスタムメトリクス
const errorRate = new Rate('errors');
const articleResponseTime = new Trend('article_response_time');
const trendsResponseTime = new Trend('trends_response_time');
const dashboardResponseTime = new Trend('dashboard_response_time');
const requestCounter = new Counter('request_count');

// テスト設定
export const options = {
  // ロードテスト: 段階的に負荷を増加
  stages: [
    { duration: '1m', target: 50 },   // ウォームアップ: 50ユーザーまで増加
    { duration: '3m', target: 50 },   // 50ユーザーを維持
    { duration: '1m', target: 100 },  // 100ユーザーまで増加
    { duration: '3m', target: 100 },  // 100ユーザーを維持
    { duration: '1m', target: 200 },  // 200ユーザーまで増加
    { duration: '3m', target: 200 },  // 200ユーザーを維持
    { duration: '1m', target: 500 },  // ピーク: 500ユーザーまで増加
    { duration: '2m', target: 500 },  // 500ユーザーを維持
    { duration: '2m', target: 0 },    // クールダウン: 0まで減少
  ],

  // パフォーマンス閾値
  thresholds: {
    // HTTPリクエスト全体
    'http_req_duration': [
      'p(95)<500',   // 95%のリクエストが500ms以下
      'p(99)<1000',  // 99%のリクエストが1000ms以下
    ],
    'http_req_failed': ['rate<0.01'], // エラー率1%未満

    // エンドポイント別
    'article_response_time': ['p(95)<400'],
    'trends_response_time': ['p(95)<400'],
    'dashboard_response_time': ['p(95)<600'],
    
    // エラー率
    'errors': ['rate<0.01'],
  },
};

// ベースURL
const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

// ヘッダー
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// ヘルパー関数: レスポンスチェック
function checkResponse(res, metricName) {
  const success = check(res, {
    'status is 200': (r) => r.status === 200,
    'response has body': (r) => r.body && r.body.length > 0,
    'response time < 1000ms': (r) => r.timings.duration < 1000,
  });

  if (!success) {
    errorRate.add(1);
  } else {
    errorRate.add(0);
  }

  requestCounter.add(1);
  
  return success;
}

// メインテストシナリオ
export default function () {
  // グループ1: コンテンツ取得（70%のトラフィック）
  group('Content APIs', function () {
    // 記事一覧取得
    group('Get Articles', function () {
      const res = http.get(`${BASE_URL}/api/content/articles`, { headers });
      checkResponse(res, 'articles');
      articleResponseTime.add(res.timings.duration);
    });

    sleep(Math.random() * 2 + 1); // 1-3秒のランダム待機

    // トレンド取得
    group('Get Trends', function () {
      const res = http.get(`${BASE_URL}/api/content/trends`, { headers });
      checkResponse(res, 'trends');
      trendsResponseTime.add(res.timings.duration);
    });

    sleep(Math.random() * 2 + 1);

    // ニュースレター取得（30%の確率）
    if (Math.random() < 0.3) {
      group('Get Newsletters', function () {
        const res = http.get(`${BASE_URL}/api/content/newsletters`, { headers });
        checkResponse(res, 'newsletters');
      });
      
      sleep(Math.random() * 2 + 1);
    }
  });

  // グループ2: 最適化されたエンドポイント（20%のトラフィック）
  if (Math.random() < 0.2) {
    group('Optimized APIs', function () {
      // 最適化された記事取得
      group('Get Optimized Articles', function () {
        const res = http.get(`${BASE_URL}/api/optimized/articles`, { headers });
        checkResponse(res, 'optimized_articles');
      });

      sleep(Math.random() * 2 + 1);

      // 最適化されたダッシュボード
      group('Get Optimized Dashboard', function () {
        const res = http.get(`${BASE_URL}/api/optimized/dashboard`, { headers });
        checkResponse(res, 'optimized_dashboard');
        dashboardResponseTime.add(res.timings.duration);
      });

      sleep(Math.random() * 2 + 1);
    });
  }

  // グループ3: ヘルスチェック（10%のトラフィック）
  if (Math.random() < 0.1) {
    group('Health Check', function () {
      const res = http.get(`${BASE_URL}/health`, { headers });
      checkResponse(res, 'health');
    });

    sleep(Math.random() * 1 + 0.5);
  }

  // グループ4: パフォーマンス統計（5%のトラフィック）
  if (Math.random() < 0.05) {
    group('Performance Stats', function () {
      const res = http.get(`${BASE_URL}/api/optimized/performance/stats`, { headers });
      checkResponse(res, 'performance_stats');
    });

    sleep(Math.random() * 1 + 0.5);
  }
}

// テスト終了時のサマリー
export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}

// テキストサマリー生成
function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors !== false;
  
  let summary = '\n';
  summary += `${indent}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
  summary += `${indent}  📊 Load Test Results Summary\n`;
  summary += `${indent}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
  
  // テスト概要
  summary += `${indent}  Test Duration: ${data.state.testRunDurationMs / 1000}s\n`;
  summary += `${indent}  Virtual Users: ${data.metrics.vus.values.max} (max)\n`;
  summary += `${indent}  Iterations: ${data.metrics.iterations.values.count}\n\n`;
  
  // HTTPメトリクス
  summary += `${indent}  HTTP Metrics:\n`;
  summary += `${indent}  ├─ Total Requests: ${data.metrics.http_reqs.values.count}\n`;
  summary += `${indent}  ├─ Failed Requests: ${data.metrics.http_req_failed.values.count}\n`;
  summary += `${indent}  ├─ Request Rate: ${data.metrics.http_reqs.values.rate.toFixed(2)} req/s\n`;
  summary += `${indent}  ├─ Avg Response Time: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
  summary += `${indent}  ├─ P95 Response Time: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
  summary += `${indent}  └─ P99 Response Time: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms\n\n`;
  
  // エラー率
  const errorRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(2);
  summary += `${indent}  Error Rate: ${errorRate}%\n\n`;
  
  // 閾値チェック
  summary += `${indent}  Thresholds:\n`;
  Object.entries(data.metrics).forEach(([name, metric]) => {
    if (metric.thresholds) {
      Object.entries(metric.thresholds).forEach(([threshold, result]) => {
        const status = result.ok ? '✓' : '✗';
        summary += `${indent}  ${status} ${name}: ${threshold}\n`;
      });
    }
  });
  
  summary += `${indent}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
  
  return summary;
}
