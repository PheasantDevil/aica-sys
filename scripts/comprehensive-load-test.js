const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');
require('dotenv').config({
  path: path.resolve(__dirname, '../.env.production.example'),
});

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Colors for console output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

class ComprehensiveLoadTester {
  constructor() {
    this.results = {
      startTime: new Date(),
      endTime: null,
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      responseTimes: [],
      endpoints: {},
      errors: [],
    };
  }

  async runLoadTest(config) {
    log('\n🚀 Starting Comprehensive Load Test', 'blue');
    log(`Target: ${API_URL}`, 'cyan');
    log(`Duration: ${config.duration}s`, 'cyan');
    log(`Concurrent Users: ${config.users}`, 'cyan');
    log(`Requests per User: ${config.requestsPerUser}`, 'cyan');
    log('');

    const startTime = performance.now();
    const endTime = startTime + config.duration * 1000;

    // 同時実行するユーザーを作成
    const userPromises = [];
    for (let i = 0; i < config.users; i++) {
      userPromises.push(this.simulateUser(i, endTime, config.requestsPerUser));
    }

    // 全ユーザーのテストを実行
    await Promise.all(userPromises);

    this.results.endTime = new Date();
    
    return this.generateReport();
  }

  async simulateUser(userId, endTime, requestsPerUser) {
    const endpoints = [
      { url: '/api/content/articles', weight: 40, name: 'articles' },
      { url: '/api/content/trends', weight: 30, name: 'trends' },
      { url: '/api/content/newsletters', weight: 20, name: 'newsletters' },
      { url: '/api/optimized/articles', weight: 15, name: 'optimized_articles' },
      { url: '/api/optimized/dashboard', weight: 10, name: 'optimized_dashboard' },
      { url: '/health', weight: 5, name: 'health' },
    ];

    let requestCount = 0;

    while (performance.now() < endTime && requestCount < requestsPerUser) {
      try {
        // ランダムにエンドポイントを選択
        const endpoint = this.selectEndpoint(endpoints);
        
        const requestStart = performance.now();
        const response = await axios.get(`${API_URL}${endpoint.url}`, {
          timeout: 10000,
          validateStatus: () => true, // すべてのステータスコードを許可
        });
        const responseTime = performance.now() - requestStart;

        // 結果を記録
        this.recordRequest(endpoint.name, response.status, responseTime);

        requestCount++;

        // ランダムな待機時間（0.5-2秒）
        await this.sleep(Math.random() * 1500 + 500);

      } catch (error) {
        this.recordError(error.message);
      }
    }
  }

  selectEndpoint(endpoints) {
    const totalWeight = endpoints.reduce((sum, e) => sum + e.weight, 0);
    let random = Math.random() * totalWeight;

    for (const endpoint of endpoints) {
      random -= endpoint.weight;
      if (random <= 0) {
        return endpoint;
      }
    }

    return endpoints[0];
  }

  recordRequest(endpointName, statusCode, responseTime) {
    this.results.totalRequests++;

    if (statusCode >= 200 && statusCode < 400) {
      this.results.successfulRequests++;
    } else {
      this.results.failedRequests++;
    }

    this.results.responseTimes.push(responseTime);

    if (!this.results.endpoints[endpointName]) {
      this.results.endpoints[endpointName] = {
        count: 0,
        successCount: 0,
        failCount: 0,
        responseTimes: [],
        statusCodes: {},
      };
    }

    const endpoint = this.results.endpoints[endpointName];
    endpoint.count++;
    endpoint.responseTimes.push(responseTime);
    endpoint.statusCodes[statusCode] = (endpoint.statusCodes[statusCode] || 0) + 1;

    if (statusCode >= 200 && statusCode < 400) {
      endpoint.successCount++;
    } else {
      endpoint.failCount++;
    }
  }

  recordError(errorMessage) {
    this.results.failedRequests++;
    this.results.errors.push({
      message: errorMessage,
      timestamp: new Date().toISOString(),
    });
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  calculatePercentile(values, percentile) {
    if (values.length === 0) return 0;
    const sorted = values.slice().sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  generateReport() {
    const durationSeconds =
      (this.results.endTime - this.results.startTime) / 1000;

    const responseTimes = this.results.responseTimes;

    const report = {
      test_id: `load-test-${this.results.startTime.toISOString()}`,
      test_type: 'comprehensive_load_test',
      start_time: this.results.startTime.toISOString(),
      end_time: this.results.endTime.toISOString(),
      duration_seconds: durationSeconds,
      
      summary: {
        total_requests: this.results.totalRequests,
        successful_requests: this.results.successfulRequests,
        failed_requests: this.results.failedRequests,
        success_rate:
          (this.results.successfulRequests / this.results.totalRequests) * 100,
        requests_per_second: this.results.totalRequests / durationSeconds,
      },

      response_times: {
        average: responseTimes.reduce((sum, t) => sum + t, 0) / responseTimes.length,
        min: Math.min(...responseTimes),
        max: Math.max(...responseTimes),
        p50: this.calculatePercentile(responseTimes, 50),
        p95: this.calculatePercentile(responseTimes, 95),
        p99: this.calculatePercentile(responseTimes, 99),
      },

      endpoints: Object.entries(this.results.endpoints).map(([name, data]) => ({
        name: name,
        count: data.count,
        success_count: data.successCount,
        fail_count: data.failCount,
        success_rate: (data.successCount / data.count) * 100,
        avg_response_time:
          data.responseTimes.reduce((sum, t) => sum + t, 0) / data.responseTimes.length,
        p95_response_time: this.calculatePercentile(data.responseTimes, 95),
        status_codes: data.statusCodes,
      })),

      errors: this.results.errors.slice(0, 100), // 最初の100個のエラー
    };

    // コンソール出力
    this.displayReport(report);

    // ファイルに保存
    this.saveReport(report);

    return report;
  }

  displayReport(report) {
    log('\n' + '='.repeat(80), 'blue');
    log('📊 Load Test Results Summary', 'blue');
    log('='.repeat(80), 'blue');

    log(`\nTest Duration: ${report.duration_seconds.toFixed(2)}s`, 'cyan');
    log(`Total Requests: ${report.summary.total_requests}`, 'cyan');
    log(
      `Success Rate: ${report.summary.success_rate.toFixed(2)}%`,
      report.summary.success_rate >= 99 ? 'green' : 'yellow'
    );
    log(
      `Requests/sec: ${report.summary.requests_per_second.toFixed(2)}`,
      'cyan'
    );

    log(`\n⏱️  Response Times:`, 'blue');
    log(`  Average: ${report.response_times.average.toFixed(2)}ms`);
    log(`  Min: ${report.response_times.min.toFixed(2)}ms`);
    log(`  Max: ${report.response_times.max.toFixed(2)}ms`);
    log(`  P50: ${report.response_times.p50.toFixed(2)}ms`);
    log(
      `  P95: ${report.response_times.p95.toFixed(2)}ms`,
      report.response_times.p95 < 500 ? 'green' : 'yellow'
    );
    log(
      `  P99: ${report.response_times.p99.toFixed(2)}ms`,
      report.response_times.p99 < 1000 ? 'green' : 'yellow'
    );

    log(`\n🎯 Endpoint Performance:`, 'blue');
    report.endpoints.forEach(endpoint => {
      log(`  ${endpoint.name}:`);
      log(`    Requests: ${endpoint.count}`);
      log(`    Success Rate: ${endpoint.success_rate.toFixed(2)}%`);
      log(`    Avg Response: ${endpoint.avg_response_time.toFixed(2)}ms`);
      log(`    P95 Response: ${endpoint.p95_response_time.toFixed(2)}ms`);
    });

    if (report.errors.length > 0) {
      log(`\n❌ Errors (showing first 10):`, 'red');
      report.errors.slice(0, 10).forEach((error, i) => {
        log(`  ${i + 1}. ${error.message}`, 'red');
      });
    }

    log('\n' + '='.repeat(80), 'blue');
  }

  saveReport(report) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = path.join(
      __dirname,
      '..',
      'docs',
      `load-test-report-${timestamp}.json`
    );

    fs.mkdirSync(path.dirname(filename), { recursive: true });
    fs.writeFileSync(filename, JSON.stringify(report, null, 2));

    log(`\n💾 Detailed report saved to: ${filename}`, 'green');
  }
}

async function main() {
  // テスト設定
  const config = {
    duration: 60,           // 60秒間のテスト
    users: 50,              // 50同時ユーザー
    requestsPerUser: 100,   // ユーザーあたり100リクエスト
  };

  // コマンドライン引数から設定を上書き
  const args = process.argv.slice(2);
  args.forEach(arg => {
    const [key, value] = arg.split('=');
    if (key === '--duration') config.duration = parseInt(value);
    if (key === '--users') config.users = parseInt(value);
    if (key === '--requests') config.requestsPerUser = parseInt(value);
  });

  const tester = new ComprehensiveLoadTester();
  const report = await tester.runLoadTest(config);

  // 成功基準のチェック
  const meetsThresholds =
    report.summary.success_rate >= 99 &&
    report.response_times.p95 < 500 &&
    report.response_times.p99 < 1000;

  if (meetsThresholds) {
    log('\n✅ Load test PASSED - All thresholds met!', 'green');
    return 0;
  } else {
    log('\n⚠️  Load test completed with warnings', 'yellow');
    log('Some thresholds were not met. Please review the results.', 'yellow');
    return 1;
  }
}

// 実行
if (require.main === module) {
  main()
    .then(exitCode => {
      process.exit(exitCode);
    })
    .catch(error => {
      log(`\n❌ Test failed: ${error.message}`, 'red');
      console.error(error);
      process.exit(1);
    });
}

module.exports = { ComprehensiveLoadTester };
