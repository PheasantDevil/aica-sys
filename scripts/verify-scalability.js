const axios = require("axios");
const fs = require("fs");
const path = require("path");
require("dotenv").config({
  path: path.resolve(__dirname, "../.env.production.example"),
});

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Colors
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

class ScalabilityVerifier {
  constructor() {
    this.results = {
      tests: [],
      summary: {},
    };
  }

  async testWithLoad(userCount, duration = 30000) {
    log(`\n🔬 Testing with ${userCount} concurrent users for ${duration / 1000}s`, "blue");

    const startTime = Date.now();
    const endTime = startTime + duration;
    const requests = [];
    const results = {
      userCount: userCount,
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      responseTimes: [],
      errors: [],
    };

    // 同時ユーザーをシミュレート
    const userTasks = [];
    for (let i = 0; i < userCount; i++) {
      userTasks.push(this.simulateUser(i, endTime, results));
    }

    await Promise.all(userTasks);

    const testDuration = (Date.now() - startTime) / 1000;

    // 統計計算
    const avgResponseTime =
      results.responseTimes.length > 0
        ? results.responseTimes.reduce((sum, t) => sum + t, 0) / results.responseTimes.length
        : 0;

    const sortedTimes = results.responseTimes.sort((a, b) => a - b);
    const p95Index = Math.floor(sortedTimes.length * 0.95);
    const p99Index = Math.floor(sortedTimes.length * 0.99);

    const testResult = {
      userCount: userCount,
      duration: testDuration,
      totalRequests: results.totalRequests,
      successfulRequests: results.successfulRequests,
      failedRequests: results.failedRequests,
      successRate: (results.successfulRequests / results.totalRequests) * 100,
      requestsPerSecond: results.totalRequests / testDuration,
      avgResponseTime: avgResponseTime,
      p95ResponseTime: sortedTimes[p95Index] || 0,
      p99ResponseTime: sortedTimes[p99Index] || 0,
      errorCount: results.errors.length,
    };

    this.results.tests.push(testResult);

    // 結果表示
    log(`  Total Requests: ${testResult.totalRequests}`, "cyan");
    log(
      `  Success Rate: ${testResult.successRate.toFixed(2)}%`,
      testResult.successRate >= 99 ? "green" : "yellow",
    );
    log(`  Req/sec: ${testResult.requestsPerSecond.toFixed(2)}`, "cyan");
    log(`  Avg Response: ${testResult.avgResponseTime.toFixed(2)}ms`, "cyan");
    log(
      `  P95 Response: ${testResult.p95ResponseTime.toFixed(2)}ms`,
      testResult.p95ResponseTime < 500 ? "green" : "yellow",
    );
    log(
      `  P99 Response: ${testResult.p99ResponseTime.toFixed(2)}ms`,
      testResult.p99ResponseTime < 1000 ? "green" : "yellow",
    );

    return testResult;
  }

  async simulateUser(userId, endTime, results) {
    const endpoints = [
      "/api/content/articles",
      "/api/content/trends",
      "/api/content/newsletters",
      "/api/optimized/articles",
    ];

    while (Date.now() < endTime) {
      try {
        const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
        const startTime = Date.now();

        const response = await axios.get(`${API_URL}${endpoint}`, {
          timeout: 10000,
          validateStatus: () => true,
        });

        const responseTime = Date.now() - startTime;

        results.totalRequests++;
        results.responseTimes.push(responseTime);

        if (response.status >= 200 && response.status < 400) {
          results.successfulRequests++;
        } else {
          results.failedRequests++;
        }

        // ランダム待機（0.5-1.5秒）
        await this.sleep(Math.random() * 1000 + 500);
      } catch (error) {
        results.failedRequests++;
        results.errors.push({
          userId: userId,
          message: error.message,
          timestamp: new Date().toISOString(),
        });
      }
    }
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async runScalabilityTest() {
    log("\n" + "=".repeat(80), "blue");
    log("🚀 Scalability Verification Test", "blue");
    log("=".repeat(80), "blue");
    log("Testing system performance under increasing load...", "cyan");

    // 段階的に負荷を増加
    const loadLevels = [10, 25, 50, 100, 200];

    for (const userCount of loadLevels) {
      await this.testWithLoad(userCount, 30000); // 各レベル30秒

      // レベル間の休憩
      log("  Cooling down...", "yellow");
      await this.sleep(5000);
    }

    // サマリーを生成
    this.generateSummary();
    this.saveResults();
  }

  generateSummary() {
    log("\n" + "=".repeat(80), "blue");
    log("📊 Scalability Test Summary", "blue");
    log("=".repeat(80), "blue");

    log("\n📈 Performance Trends:", "blue");
    log("  Users | Req/s  | Success% | Avg(ms) | P95(ms) | P99(ms)");
    log("  " + "-".repeat(65));

    this.results.tests.forEach((test) => {
      const users = String(test.userCount).padStart(5);
      const reqPerSec = test.requestsPerSecond.toFixed(1).padStart(6);
      const successRate = test.successRate.toFixed(1).padStart(8);
      const avgTime = test.avgResponseTime.toFixed(0).padStart(7);
      const p95Time = test.p95ResponseTime.toFixed(0).padStart(7);
      const p99Time = test.p99ResponseTime.toFixed(0).padStart(7);

      log(`  ${users} | ${reqPerSec} | ${successRate} | ${avgTime} | ${p95Time} | ${p99Time}`);
    });

    // スケーラビリティ評価
    log("\n🎯 Scalability Assessment:", "blue");

    const firstTest = this.results.tests[0];
    const lastTest = this.results.tests[this.results.tests.length - 1];

    const throughputIncrease =
      ((lastTest.requestsPerSecond - firstTest.requestsPerSecond) / firstTest.requestsPerSecond) *
      100;

    const responseTimeIncrease =
      ((lastTest.avgResponseTime - firstTest.avgResponseTime) / firstTest.avgResponseTime) * 100;

    log(
      `  Throughput Increase: ${throughputIncrease.toFixed(2)}%`,
      throughputIncrease > 100 ? "green" : "yellow",
    );
    log(
      `  Response Time Increase: ${responseTimeIncrease.toFixed(2)}%`,
      responseTimeIncrease < 50 ? "green" : "yellow",
    );

    // 推奨事項
    log("\n💡 Recommendations:", "blue");

    if (lastTest.successRate < 99) {
      log("  ⚠️  Success rate is below 99% under high load", "yellow");
      log("     Consider implementing auto-scaling or load balancing", "yellow");
    }

    if (lastTest.p95ResponseTime > 500) {
      log("  ⚠️  P95 response time exceeds 500ms under high load", "yellow");
      log("     Consider optimizing slow endpoints", "yellow");
    }

    if (responseTimeIncrease > 100) {
      log("  ⚠️  Response time increases significantly under load", "yellow");
      log("     System may not scale linearly", "yellow");
    } else {
      log("  ✅ System scales well with increasing load", "green");
    }

    log("\n" + "=".repeat(80), "blue");
  }

  saveResults() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const filename = path.join(__dirname, "..", "docs", `scalability-test-${timestamp}.json`);

    const report = {
      timestamp: new Date().toISOString(),
      tests: this.results.tests,
      summary: {
        totalTests: this.results.tests.length,
        userLevels: this.results.tests.map((t) => t.userCount),
        overallSuccessRate:
          this.results.tests.reduce((sum, t) => sum + t.successRate, 0) / this.results.tests.length,
      },
    };

    fs.writeFileSync(filename, JSON.stringify(report, null, 2));
    log(`\n💾 Full results saved to: ${filename}`, "green");
  }
}

async function main() {
  const verifier = new ScalabilityVerifier();
  await verifier.runScalabilityTest();
}

if (require.main === module) {
  main().catch((error) => {
    log(`\n❌ Scalability test failed: ${error.message}`, "red");
    console.error(error);
    process.exit(1);
  });
}

module.exports = { ScalabilityVerifier };
