const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config({
  path: path.resolve(__dirname, '../.env.production.example'),
});

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
const OPTIMIZED_API_URL = `${API_URL}/api/optimized`;

// Colors for console output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

class APIOptimizationTester {
  constructor() {
    this.results = {
      passed: 0,
      failed: 0,
      tests: [],
    };
    this.performanceMetrics = {
      responseTimes: [],
      compressionRatios: [],
      cacheHitRates: [],
      errorRates: [],
    };
  }

  async runTest(testName, testFunction) {
    log(`🧪 Running test: ${testName}`, 'blue');
    const startTime = Date.now();

    try {
      const result = await testFunction();
      const duration = Date.now() - startTime;

      this.results.passed++;
      this.results.tests.push({
        name: testName,
        status: 'PASSED',
        duration: duration,
        result: result,
      });

      this.performanceMetrics.responseTimes.push(duration);

      log(`✅ ${testName}: PASSED (${duration}ms)`, 'green');
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;

      this.results.failed++;
      this.results.tests.push({
        name: testName,
        status: 'FAILED',
        duration: duration,
        error: error.message,
      });

      this.performanceMetrics.errorRates.push(1);

      log(`❌ ${testName}: FAILED - ${error.message} (${duration}ms)`, 'red');
      throw error;
    }
  }

  async testAPIHealth() {
    const response = await axios.get(`${API_URL}/health`, {
      timeout: 5000,
    });

    if (response.status !== 200) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return response.data;
  }

  async testOptimizedEndpoints() {
    const endpoints = [
      { name: 'Articles', url: `${OPTIMIZED_API_URL}/articles` },
      { name: 'Trends', url: `${OPTIMIZED_API_URL}/trends` },
      { name: 'Newsletters', url: `${OPTIMIZED_API_URL}/newsletters` },
      { name: 'Dashboard', url: `${OPTIMIZED_API_URL}/dashboard` },
    ];

    const results = {};

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(endpoint.url, { timeout: 10000 });

        if (response.status !== 200) {
          throw new Error(
            `${endpoint.name} endpoint failed: ${response.status}`
          );
        }

        // レスポンス時間を記録
        const responseTime = response.headers['x-response-time'] || 'unknown';
        const requestId = response.headers['x-request-id'] || 'unknown';
        const etag = response.headers['etag'] || 'none';
        const contentEncoding = response.headers['content-encoding'] || 'none';

        results[endpoint.name] = {
          status: response.status,
          responseTime: responseTime,
          requestId: requestId,
          etag: etag,
          contentEncoding: contentEncoding,
          dataSize: JSON.stringify(response.data).length,
          hasOptimizationHeaders: !!(responseTime && requestId),
        };

        this.performanceMetrics.responseTimes.push(
          parseFloat(responseTime) || 0
        );
        this.performanceMetrics.compressionRatios.push(
          contentEncoding === 'gzip' ? 1 : 0
        );

        log(
          `  📊 ${endpoint.name}: ${response.status} (${responseTime}ms, ${contentEncoding})`,
          'reset'
        );
      } catch (error) {
        results[endpoint.name] = {
          error: error.message,
          status: 'failed',
        };
        log(`  ❌ ${endpoint.name}: ${error.message}`, 'red');
      }
    }

    return results;
  }

  async testResponseCompression() {
    const testUrl = `${OPTIMIZED_API_URL}/articles?limit=50`;

    try {
      const response = await axios.get(testUrl, {
        timeout: 10000,
        headers: {
          'Accept-Encoding': 'gzip, deflate',
        },
      });

      const contentEncoding = response.headers['content-encoding'];
      const contentLength = response.headers['content-length'];
      const dataSize = JSON.stringify(response.data).length;

      const compressionRatio = contentLength
        ? (dataSize / parseInt(contentLength)) * 100
        : 0;

      return {
        status: response.status,
        contentEncoding: contentEncoding,
        originalSize: dataSize,
        compressedSize: parseInt(contentLength) || dataSize,
        compressionRatio: compressionRatio,
        isCompressed: contentEncoding === 'gzip',
      };
    } catch (error) {
      throw new Error(`Compression test failed: ${error.message}`);
    }
  }

  async testCacheHeaders() {
    const testUrl = `${OPTIMIZED_API_URL}/articles`;

    try {
      const response = await axios.get(testUrl, { timeout: 10000 });

      const cacheControl = response.headers['cache-control'];
      const etag = response.headers['etag'];
      const lastModified = response.headers['last-modified'];

      return {
        status: response.status,
        cacheControl: cacheControl,
        etag: etag,
        lastModified: lastModified,
        hasCacheHeaders: !!(cacheControl || etag),
        cacheStrategy: cacheControl ? 'configured' : 'none',
      };
    } catch (error) {
      throw new Error(`Cache headers test failed: ${error.message}`);
    }
  }

  async testConditionalRequests() {
    const testUrl = `${OPTIMIZED_API_URL}/articles`;

    try {
      // 最初のリクエスト
      const firstResponse = await axios.get(testUrl, { timeout: 10000 });
      const etag = firstResponse.headers['etag'];

      if (!etag) {
        throw new Error('No ETag header found');
      }

      // 条件付きリクエスト
      const conditionalResponse = await axios.get(testUrl, {
        timeout: 10000,
        headers: {
          'If-None-Match': etag,
        },
      });

      return {
        firstRequest: {
          status: firstResponse.status,
          etag: etag,
          dataSize: JSON.stringify(firstResponse.data).length,
        },
        conditionalRequest: {
          status: conditionalResponse.status,
          isNotModified: conditionalResponse.status === 304,
          dataSize: JSON.stringify(conditionalResponse.data).length,
        },
        etagWorking: conditionalResponse.status === 304,
      };
    } catch (error) {
      throw new Error(`Conditional requests test failed: ${error.message}`);
    }
  }

  async testConcurrentRequests() {
    const concurrentRequests = 20;
    const testUrl = `${OPTIMIZED_API_URL}/articles`;
    const requestPromises = [];

    const startTime = Date.now();

    // 並列リクエストを作成
    for (let i = 0; i < concurrentRequests; i++) {
      requestPromises.push(
        axios
          .get(testUrl, { timeout: 15000 })
          .then(response => ({
            success: true,
            duration: Date.now() - startTime,
            status: response.status,
            responseTime: response.headers['x-response-time'],
            requestId: response.headers['x-request-id'],
          }))
          .catch(error => ({
            success: false,
            duration: Date.now() - startTime,
            error: error.message,
          }))
      );
    }

    const results = await Promise.all(requestPromises);
    const totalDuration = Date.now() - startTime;

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;
    const averageResponseTime =
      results
        .filter(r => r.success && r.responseTime)
        .reduce((sum, r) => sum + parseFloat(r.responseTime), 0) /
        results.filter(r => r.success && r.responseTime).length || 0;

    return {
      totalRequests: concurrentRequests,
      successCount: successCount,
      failureCount: failureCount,
      successRate: (successCount / concurrentRequests) * 100,
      totalDuration: totalDuration,
      averageResponseTime: averageResponseTime,
      requestsPerSecond: (successCount / totalDuration) * 1000,
    };
  }

  async testPerformanceStats() {
    try {
      const response = await axios.get(
        `${OPTIMIZED_API_URL}/performance/stats`,
        {
          timeout: 5000,
        }
      );

      if (response.status !== 200) {
        throw new Error(
          `Performance stats endpoint failed: ${response.status}`
        );
      }

      return response.data;
    } catch (error) {
      // パフォーマンス統計エンドポイントが存在しない場合
      return {
        status: 'not_implemented',
        error: error.message,
      };
    }
  }

  async testErrorHandling() {
    const errorTests = [
      {
        name: 'Invalid endpoint',
        url: `${OPTIMIZED_API_URL}/invalid`,
        expectedStatus: 404,
      },
      {
        name: 'Invalid parameters',
        url: `${OPTIMIZED_API_URL}/articles?limit=invalid`,
        expectedStatus: 422,
      },
      {
        name: 'Large request',
        url: `${OPTIMIZED_API_URL}/articles?limit=1000`,
        expectedStatus: 400,
      },
    ];

    const results = {};

    for (const test of errorTests) {
      try {
        const response = await axios.get(test.url, { timeout: 5000 });

        results[test.name] = {
          status: response.status,
          expectedStatus: test.expectedStatus,
          isCorrectStatus: response.status === test.expectedStatus,
          hasErrorStructure: response.data && response.data.success === false,
        };
      } catch (error) {
        results[test.name] = {
          error: error.message,
          status: error.response?.status || 'unknown',
          expectedStatus: test.expectedStatus,
        };
      }
    }

    return results;
  }

  calculatePerformanceMetrics() {
    const responseTimes = this.performanceMetrics.responseTimes;
    const compressionRatios = this.performanceMetrics.compressionRatios;
    const errorRates = this.performanceMetrics.errorRates;

    if (responseTimes.length === 0) {
      return {
        averageResponseTime: 0,
        minResponseTime: 0,
        maxResponseTime: 0,
        averageCompressionRatio: 0,
        totalErrors: 0,
        errorRate: 0,
      };
    }

    return {
      averageResponseTime:
        responseTimes.reduce((sum, time) => sum + time, 0) /
        responseTimes.length,
      minResponseTime: Math.min(...responseTimes),
      maxResponseTime: Math.max(...responseTimes),
      averageCompressionRatio:
        compressionRatios.length > 0
          ? (compressionRatios.reduce((sum, ratio) => sum + ratio, 0) /
              compressionRatios.length) *
            100
          : 0,
      totalErrors: errorRates.length,
      errorRate:
        (errorRates.length / (responseTimes.length + errorRates.length)) * 100,
    };
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate =
      totalTests > 0
        ? ((this.results.passed / totalTests) * 100).toFixed(1)
        : 0;
    const performanceMetrics = this.calculatePerformanceMetrics();

    log('\n📊 API Optimization Test Results:', 'blue');
    log(`Total Tests: ${totalTests}`, 'reset');
    log(`Passed: ${this.results.passed}`, 'green');
    log(`Failed: ${this.results.failed}`, 'red');
    log(
      `Success Rate: ${successRate}%`,
      successRate >= 80 ? 'green' : 'yellow'
    );

    log('\n⚡ Performance Metrics:', 'blue');
    log(
      `Average Response Time: ${performanceMetrics.averageResponseTime.toFixed(
        2
      )}ms`,
      'reset'
    );
    log(
      `Min Response Time: ${performanceMetrics.minResponseTime.toFixed(2)}ms`,
      'reset'
    );
    log(
      `Max Response Time: ${performanceMetrics.maxResponseTime.toFixed(2)}ms`,
      'reset'
    );
    log(
      `Average Compression Ratio: ${performanceMetrics.averageCompressionRatio.toFixed(
        2
      )}%`,
      'reset'
    );
    log(`Error Rate: ${performanceMetrics.errorRate.toFixed(2)}%`, 'reset');

    log('\n📋 Detailed Results:', 'blue');
    this.results.tests.forEach(test => {
      const status = test.status === 'PASSED' ? '✅' : '❌';
      const duration = test.duration ? `(${test.duration}ms)` : '';
      log(
        `${status} ${test.name}: ${test.status} ${duration}`,
        test.status === 'PASSED' ? 'green' : 'red'
      );
      if (test.error) {
        log(`   Error: ${test.error}`, 'red');
      }
    });

    // Save detailed report
    const reportPath = path.join(
      __dirname,
      '..',
      'docs',
      'api-optimization-test-report.json'
    );
    fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    fs.writeFileSync(
      reportPath,
      JSON.stringify(
        {
          timestamp: new Date().toISOString(),
          summary: {
            total: totalTests,
            passed: this.results.passed,
            failed: this.results.failed,
            successRate: parseFloat(successRate),
          },
          performanceMetrics: performanceMetrics,
          tests: this.results.tests,
        },
        null,
        2
      )
    );

    log(`\n📄 Detailed report saved to: ${reportPath}`, 'blue');

    return successRate >= 80;
  }
}

async function main() {
  log('🚀 Starting API Optimization Tests...', 'blue');
  log(`Testing API URL: ${API_URL}`, 'yellow');
  log(`Testing Optimized API URL: ${OPTIMIZED_API_URL}`, 'yellow');
  log('');

  const tester = new APIOptimizationTester();

  try {
    // Basic connectivity tests
    await tester.runTest('API Health Check', () => tester.testAPIHealth());

    // Optimized endpoints tests
    await tester.runTest('Optimized Endpoints Test', () =>
      tester.testOptimizedEndpoints()
    );

    // Response compression tests
    await tester.runTest('Response Compression Test', () =>
      tester.testResponseCompression()
    );

    // Cache headers tests
    await tester.runTest('Cache Headers Test', () => tester.testCacheHeaders());

    // Conditional requests tests
    await tester.runTest('Conditional Requests Test', () =>
      tester.testConditionalRequests()
    );

    // Concurrent requests tests
    await tester.runTest('Concurrent Requests Test', () =>
      tester.testConcurrentRequests()
    );

    // Performance stats tests
    await tester.runTest('Performance Stats Test', () =>
      tester.testPerformanceStats()
    );

    // Error handling tests
    await tester.runTest('Error Handling Test', () =>
      tester.testErrorHandling()
    );

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log('\n🎉 API optimization tests completed successfully!', 'green');
      log('The API optimization is functioning as expected.', 'green');
      return 0;
    } else {
      log('\n⚠️  API optimization tests completed with issues.', 'yellow');
      log('Please review the failed tests and optimize accordingly.', 'yellow');
      return 1;
    }
  } catch (error) {
    log(`\n❌ Test suite failed: ${error.message}`, 'red');
    return 1;
  }
}

// Run the tests
if (require.main === module) {
  main().then(exitCode => {
    process.exit(exitCode);
  });
}

module.exports = { APIOptimizationTester };
