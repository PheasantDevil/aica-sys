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

class DatabaseOptimizationTester {
  constructor() {
    this.results = {
      passed: 0,
      failed: 0,
      tests: [],
    };
    this.performanceMetrics = {
      queryTimes: [],
      responseSizes: [],
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

      this.performanceMetrics.queryTimes.push(duration);

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

  async testDatabaseHealth() {
    const response = await axios.get(`${API_URL}/health`, {
      timeout: 5000,
    });

    if (response.status !== 200) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return response.data;
  }

  async testArticlesPerformance() {
    const startTime = Date.now();

    // Test articles endpoint with various filters
    const tests = [
      { name: "All articles", url: `${API_URL}/api/content/articles` },
      {
        name: "Premium articles",
        url: `${API_URL}/api/content/articles?is_premium=true`,
      },
      {
        name: "Recent articles",
        url: `${API_URL}/api/content/articles?limit=10&offset=0`,
      },
      {
        name: "Popular articles",
        url: `${API_URL}/api/content/articles?sort_by=views`,
      },
    ];

    const results = {};

    for (const test of tests) {
      const testStart = Date.now();
      const response = await axios.get(test.url, { timeout: 10000 });
      const testDuration = Date.now() - testStart;

      if (response.status !== 200) {
        throw new Error(`${test.name} failed: ${response.status}`);
      }

      results[test.name] = {
        duration: testDuration,
        status: response.status,
        dataSize: JSON.stringify(response.data).length,
        articleCount: response.data.articles?.length || 0,
      };

      this.performanceMetrics.responseSizes.push(JSON.stringify(response.data).length);
    }

    const totalDuration = Date.now() - startTime;
    results.totalDuration = totalDuration;

    return results;
  }

  async testNewslettersPerformance() {
    const startTime = Date.now();

    const response = await axios.get(`${API_URL}/api/content/newsletters`, {
      timeout: 10000,
    });

    if (response.status !== 200) {
      throw new Error(`Newsletters endpoint failed: ${response.status}`);
    }

    const duration = Date.now() - startTime;

    return {
      duration: duration,
      status: response.status,
      dataSize: JSON.stringify(response.data).length,
      newsletterCount: response.data.newsletters?.length || 0,
    };
  }

  async testTrendsPerformance() {
    const startTime = Date.now();

    const response = await axios.get(`${API_URL}/api/content/trends`, {
      timeout: 10000,
    });

    if (response.status !== 200) {
      throw new Error(`Trends endpoint failed: ${response.status}`);
    }

    const duration = Date.now() - startTime;

    return {
      duration: duration,
      status: response.status,
      dataSize: JSON.stringify(response.data).length,
      trendCount: response.data.trends?.length || 0,
    };
  }

  async testAuditEventsPerformance() {
    const startTime = Date.now();

    const response = await axios.get(`${API_URL}/api/audit/events`, {
      timeout: 10000,
    });

    if (response.status !== 200) {
      throw new Error(`Audit events endpoint failed: ${response.status}`);
    }

    const duration = Date.now() - startTime;

    return {
      duration: duration,
      status: response.status,
      dataSize: JSON.stringify(response.data).length,
      eventCount: response.data.length || 0,
    };
  }

  async testConcurrentRequests() {
    const concurrentRequests = 10;
    const requestPromises = [];

    const startTime = Date.now();

    // Create concurrent requests
    for (let i = 0; i < concurrentRequests; i++) {
      requestPromises.push(
        axios
          .get(`${API_URL}/api/content/articles`, { timeout: 15000 })
          .then((response) => ({
            success: true,
            duration: Date.now() - startTime,
            status: response.status,
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
    const averageDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;

    return {
      totalRequests: concurrentRequests,
      successCount: successCount,
      failureCount: failureCount,
      successRate: (successCount / concurrentRequests) * 100,
      totalDuration: totalDuration,
      averageDuration: averageDuration,
      results: results,
    };
  }

  async testDatabaseConnectionPool() {
    // Test multiple rapid requests to check connection pool
    const rapidRequests = 20;
    const requestPromises = [];

    const startTime = Date.now();

    for (let i = 0; i < rapidRequests; i++) {
      requestPromises.push(
        axios
          .get(`${API_URL}/health`, { timeout: 5000 })
          .then((response) => ({
            success: true,
            duration: Date.now() - startTime,
            status: response.status,
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
    const averageDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;

    return {
      totalRequests: rapidRequests,
      successCount: successCount,
      successRate: (successCount / rapidRequests) * 100,
      totalDuration: totalDuration,
      averageDuration: averageDuration,
    };
  }

  calculatePerformanceMetrics() {
    const queryTimes = this.performanceMetrics.queryTimes;
    const responseSizes = this.performanceMetrics.responseSizes;
    const errorRates = this.performanceMetrics.errorRates;

    if (queryTimes.length === 0) {
      return {
        averageQueryTime: 0,
        minQueryTime: 0,
        maxQueryTime: 0,
        averageResponseSize: 0,
        totalErrors: 0,
        errorRate: 0,
      };
    }

    return {
      averageQueryTime: queryTimes.reduce((sum, time) => sum + time, 0) / queryTimes.length,
      minQueryTime: Math.min(...queryTimes),
      maxQueryTime: Math.max(...queryTimes),
      averageResponseSize:
        responseSizes.reduce((sum, size) => sum + size, 0) / responseSizes.length,
      totalErrors: errorRates.length,
      errorRate: (errorRates.length / (queryTimes.length + errorRates.length)) * 100,
    };
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate = totalTests > 0 ? ((this.results.passed / totalTests) * 100).toFixed(1) : 0;
    const performanceMetrics = this.calculatePerformanceMetrics();

    log("\n📊 Database Optimization Test Results:", "blue");
    log(`Total Tests: ${totalTests}`, "reset");
    log(`Passed: ${this.results.passed}`, "green");
    log(`Failed: ${this.results.failed}`, "red");
    log(`Success Rate: ${successRate}%`, successRate >= 80 ? "green" : "yellow");

    log("\n⚡ Performance Metrics:", "blue");
    log(`Average Query Time: ${performanceMetrics.averageQueryTime.toFixed(2)}ms`, "reset");
    log(`Min Query Time: ${performanceMetrics.minQueryTime}ms`, "reset");
    log(`Max Query Time: ${performanceMetrics.maxQueryTime}ms`, "reset");
    log(
      `Average Response Size: ${(performanceMetrics.averageResponseSize / 1024).toFixed(2)}KB`,
      "reset",
    );
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
    const reportPath = path.join(__dirname, "..", "docs", "database-optimization-test-report.json");
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
  log("🚀 Starting Database Optimization Tests...", "blue");
  log(`Testing API URL: ${API_URL}`, "yellow");
  log(`Testing Frontend URL: ${PRODUCTION_URL}`, "yellow");
  log("");

  const tester = new DatabaseOptimizationTester();

  try {
    // Basic connectivity tests
    await tester.runTest("Database Health Check", () => tester.testDatabaseHealth());

    // Performance tests
    await tester.runTest("Articles Performance Test", () => tester.testArticlesPerformance());
    await tester.runTest("Newsletters Performance Test", () => tester.testNewslettersPerformance());
    await tester.runTest("Trends Performance Test", () => tester.testTrendsPerformance());
    await tester.runTest("Audit Events Performance Test", () =>
      tester.testAuditEventsPerformance(),
    );

    // Concurrency tests
    await tester.runTest("Concurrent Requests Test", () => tester.testConcurrentRequests());
    await tester.runTest("Database Connection Pool Test", () =>
      tester.testDatabaseConnectionPool(),
    );

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log("\n🎉 Database optimization tests completed successfully!", "green");
      log("The database optimization is functioning as expected.", "green");
      return 0;
    } else {
      log("\n⚠️  Database optimization tests completed with issues.", "yellow");
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

module.exports = { DatabaseOptimizationTester };
