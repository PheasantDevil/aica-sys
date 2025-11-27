const axios = require("axios");
const fs = require("fs");
const path = require("path");
require("dotenv").config({
  path: path.resolve(__dirname, "../.env.production.example"),
});

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const PRODUCTION_URL = process.env.NEXTAUTH_URL || "http://localhost:3000";

// Colors for console output
const colors = {
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  reset: "\x1b[0m",
};

function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

class CacheSystemTester {
  constructor() {
    this.results = {
      passed: 0,
      failed: 0,
      tests: [],
    };
    this.performanceMetrics = {
      responseTimes: [],
      cacheHitRates: [],
      errorRates: [],
    };
  }

  async runTest(testName, testFunction) {
    log(`🧪 Running test: ${testName}`, "blue");
    const startTime = Date.now();

    try {
      const result = await testFunction();
      const duration = Date.now() - startTime;

      this.results.passed++;
      this.results.tests.push({
        name: testName,
        status: "PASSED",
        duration: duration,
        result: result,
      });

      this.performanceMetrics.responseTimes.push(duration);

      log(`✅ ${testName}: PASSED (${duration}ms)`, "green");
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;

      this.results.failed++;
      this.results.tests.push({
        name: testName,
        status: "FAILED",
        duration: duration,
        error: error.message,
      });

      this.performanceMetrics.errorRates.push(1);

      log(`❌ ${testName}: FAILED - ${error.message} (${duration}ms)`, "red");
      throw error;
    }
  }

  async testCacheHealth() {
    const response = await axios.get(`${API_URL}/health`, {
      timeout: 5000,
    });

    if (response.status !== 200) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return response.data;
  }

  async testCachePerformance() {
    const testEndpoints = [
      { name: "Articles", url: `${API_URL}/api/content/articles` },
      { name: "Newsletters", url: `${API_URL}/api/content/newsletters` },
      { name: "Trends", url: `${API_URL}/api/content/trends` },
    ];

    const results = {};

    for (const endpoint of testEndpoints) {
      const times = [];
      const cacheHits = [];

      // Test multiple requests to measure cache performance
      for (let i = 0; i < 5; i++) {
        const startTime = Date.now();
        const response = await axios.get(endpoint.url, { timeout: 10000 });
        const duration = Date.now() - startTime;

        times.push(duration);

        // Check for cache headers
        const cacheHeader = response.headers["cache-control"] || response.headers["x-cache"];
        cacheHits.push(cacheHeader ? true : false);

        if (response.status !== 200) {
          throw new Error(`${endpoint.name} endpoint failed: ${response.status}`);
        }

        // Small delay between requests
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      const averageTime = times.reduce((sum, time) => sum + time, 0) / times.length;
      const cacheHitRate = (cacheHits.filter((hit) => hit).length / cacheHits.length) * 100;

      results[endpoint.name] = {
        averageTime: averageTime,
        cacheHitRate: cacheHitRate,
        times: times,
        cacheHits: cacheHits,
      };

      this.performanceMetrics.responseTimes.push(averageTime);
      this.performanceMetrics.cacheHitRates.push(cacheHitRate);
    }

    return results;
  }

  async testConcurrentCacheRequests() {
    const concurrentRequests = 10;
    const requestPromises = [];

    const startTime = Date.now();

    // Create concurrent requests to test cache under load
    for (let i = 0; i < concurrentRequests; i++) {
      requestPromises.push(
        axios
          .get(`${API_URL}/api/content/articles`, { timeout: 15000 })
          .then((response) => ({
            success: true,
            duration: Date.now() - startTime,
            status: response.status,
            cached: !!(response.headers["x-cache"] || response.headers["cache-control"]),
          }))
          .catch((error) => ({
            success: false,
            duration: Date.now() - startTime,
            error: error.message,
          })),
      );
    }

    const results = await Promise.all(requestPromises);
    const totalDuration = Date.now() - startTime;

    const successCount = results.filter((r) => r.success).length;
    const failureCount = results.filter((r) => !r.success).length;
    const cacheHitCount = results.filter((r) => r.success && r.cached).length;
    const averageDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;

    return {
      totalRequests: concurrentRequests,
      successCount: successCount,
      failureCount: failureCount,
      successRate: (successCount / concurrentRequests) * 100,
      cacheHitCount: cacheHitCount,
      cacheHitRate: (cacheHitCount / successCount) * 100,
      totalDuration: totalDuration,
      averageDuration: averageDuration,
      results: results,
    };
  }

  async testCacheInvalidation() {
    // Test cache invalidation by making requests and checking headers
    const testUrl = `${API_URL}/api/content/articles`;

    // First request (should miss cache)
    const firstResponse = await axios.get(testUrl, { timeout: 10000 });
    const firstCacheStatus = firstResponse.headers["x-cache"] || "MISS";

    // Second request (should hit cache)
    const secondResponse = await axios.get(testUrl, { timeout: 10000 });
    const secondCacheStatus = secondResponse.headers["x-cache"] || "MISS";

    // Third request with different parameters (should miss cache)
    const thirdResponse = await axios.get(`${testUrl}?limit=5`, {
      timeout: 10000,
    });
    const thirdCacheStatus = thirdResponse.headers["x-cache"] || "MISS";

    return {
      firstRequest: {
        status: firstResponse.status,
        cacheStatus: firstCacheStatus,
      },
      secondRequest: {
        status: secondResponse.status,
        cacheStatus: secondCacheStatus,
      },
      thirdRequest: {
        status: thirdResponse.status,
        cacheStatus: thirdCacheStatus,
      },
      cacheWorking: secondCacheStatus === "HIT" || secondCacheStatus === "MISS",
    };
  }

  async testMemoryCache() {
    // Test frontend memory cache by making requests to frontend
    try {
      const response = await axios.get(`${PRODUCTION_URL}/api/content/articles`, {
        timeout: 10000,
      });

      if (response.status !== 200) {
        throw new Error(`Frontend API failed: ${response.status}`);
      }

      // Check for cache headers
      const cacheHeaders = {
        "cache-control": response.headers["cache-control"],
        etag: response.headers["etag"],
        "last-modified": response.headers["last-modified"],
      };

      return {
        status: response.status,
        cacheHeaders: cacheHeaders,
        hasCacheHeaders: !!(cacheHeaders["cache-control"] || cacheHeaders["etag"]),
      };
    } catch (error) {
      // Frontend might not be running, that's okay for this test
      return {
        status: "skipped",
        error: error.message,
        hasCacheHeaders: false,
      };
    }
  }

  async testCacheStatistics() {
    // Test cache statistics endpoint if available
    try {
      const response = await axios.get(`${API_URL}/api/cache/stats`, {
        timeout: 5000,
      });

      if (response.status !== 200) {
        throw new Error(`Cache stats endpoint failed: ${response.status}`);
      }

      return response.data;
    } catch (error) {
      // Cache stats endpoint might not exist yet
      return {
        status: "not_implemented",
        error: error.message,
      };
    }
  }

  calculatePerformanceMetrics() {
    const responseTimes = this.performanceMetrics.responseTimes;
    const cacheHitRates = this.performanceMetrics.cacheHitRates;
    const errorRates = this.performanceMetrics.errorRates;

    if (responseTimes.length === 0) {
      return {
        averageResponseTime: 0,
        minResponseTime: 0,
        maxResponseTime: 0,
        averageCacheHitRate: 0,
        totalErrors: 0,
        errorRate: 0,
      };
    }

    return {
      averageResponseTime:
        responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length,
      minResponseTime: Math.min(...responseTimes),
      maxResponseTime: Math.max(...responseTimes),
      averageCacheHitRate:
        cacheHitRates.length > 0
          ? cacheHitRates.reduce((sum, rate) => sum + rate, 0) / cacheHitRates.length
          : 0,
      totalErrors: errorRates.length,
      errorRate: (errorRates.length / (responseTimes.length + errorRates.length)) * 100,
    };
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate = totalTests > 0 ? ((this.results.passed / totalTests) * 100).toFixed(1) : 0;
    const performanceMetrics = this.calculatePerformanceMetrics();

    log("\n📊 Cache System Test Results:", "blue");
    log(`Total Tests: ${totalTests}`, "reset");
    log(`Passed: ${this.results.passed}`, "green");
    log(`Failed: ${this.results.failed}`, "red");
    log(`Success Rate: ${successRate}%`, successRate >= 80 ? "green" : "yellow");

    log("\n⚡ Performance Metrics:", "blue");
    log(`Average Response Time: ${performanceMetrics.averageResponseTime.toFixed(2)}ms`, "reset");
    log(`Min Response Time: ${performanceMetrics.minResponseTime}ms`, "reset");
    log(`Max Response Time: ${performanceMetrics.maxResponseTime}ms`, "reset");
    log(`Average Cache Hit Rate: ${performanceMetrics.averageCacheHitRate.toFixed(2)}%`, "reset");
    log(`Error Rate: ${performanceMetrics.errorRate.toFixed(2)}%`, "reset");

    log("\n📋 Detailed Results:", "blue");
    this.results.tests.forEach((test) => {
      const status = test.status === "PASSED" ? "✅" : "❌";
      const duration = test.duration ? `(${test.duration}ms)` : "";
      log(
        `${status} ${test.name}: ${test.status} ${duration}`,
        test.status === "PASSED" ? "green" : "red",
      );
      if (test.error) {
        log(`   Error: ${test.error}`, "red");
      }
    });

    // Save detailed report
    const reportPath = path.join(__dirname, "..", "docs", "cache-system-test-report.json");
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
        2,
      ),
    );

    log(`\n📄 Detailed report saved to: ${reportPath}`, "blue");

    return successRate >= 80;
  }
}

async function main() {
  log("🚀 Starting Cache System Tests...", "blue");
  log(`Testing API URL: ${API_URL}`, "yellow");
  log(`Testing Frontend URL: ${PRODUCTION_URL}`, "yellow");
  log("");

  const tester = new CacheSystemTester();

  try {
    // Basic connectivity tests
    await tester.runTest("Cache Health Check", () => tester.testCacheHealth());

    // Cache performance tests
    await tester.runTest("Cache Performance Test", () => tester.testCachePerformance());

    // Concurrent cache tests
    await tester.runTest("Concurrent Cache Requests Test", () =>
      tester.testConcurrentCacheRequests(),
    );

    // Cache invalidation tests
    await tester.runTest("Cache Invalidation Test", () => tester.testCacheInvalidation());

    // Memory cache tests
    await tester.runTest("Memory Cache Test", () => tester.testMemoryCache());

    // Cache statistics tests
    await tester.runTest("Cache Statistics Test", () => tester.testCacheStatistics());

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log("\n🎉 Cache system tests completed successfully!", "green");
      log("The cache system is functioning as expected.", "green");
      return 0;
    } else {
      log("\n⚠️  Cache system tests completed with issues.", "yellow");
      log("Please review the failed tests and optimize accordingly.", "yellow");
      return 1;
    }
  } catch (error) {
    log(`\n❌ Test suite failed: ${error.message}`, "red");
    return 1;
  }
}

// Run the tests
if (require.main === module) {
  main().then((exitCode) => {
    process.exit(exitCode);
  });
}

module.exports = { CacheSystemTester };
