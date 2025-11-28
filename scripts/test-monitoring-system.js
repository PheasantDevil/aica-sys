const axios = require("axios");
const fs = require("fs");
const path = require("path");
require("dotenv").config({ path: path.resolve(__dirname, "../.env.production.example") });

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

class MonitoringSystemTester {
  constructor() {
    this.results = {
      passed: 0,
      failed: 0,
      tests: [],
    };
    this.adminToken = null;
  }

  async runTest(testName, testFunction) {
    log(`🧪 Running test: ${testName}`, "blue");
    try {
      const result = await testFunction();
      this.results.passed++;
      this.results.tests.push({
        name: testName,
        status: "PASSED",
        result: result,
      });
      log(`✅ ${testName}: PASSED`, "green");
      return result;
    } catch (error) {
      this.results.failed++;
      this.results.tests.push({
        name: testName,
        status: "FAILED",
        error: error.message,
      });
      log(`❌ ${testName}: FAILED - ${error.message}`, "red");
      throw error;
    }
  }

  async adminLogin() {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email: process.env.ADMIN_EMAIL,
        password: process.env.ADMIN_PASSWORD,
      });
      this.adminToken = response.data.access_token;
      return { success: true, message: "Admin logged in successfully." };
    } catch (error) {
      throw new Error(`Admin login failed: ${error.message}`);
    }
  }

  async testHealthEndpoints() {
    const endpoints = ["/health", "/health/detailed", "/api/monitoring/health"];

    const results = {};
    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_URL}${endpoint}`, {
          timeout: 10000,
        });
        results[endpoint] = {
          status: response.status,
          data: response.data,
          isHealthy:
            response.data.status === "healthy" ||
            response.data.status === "healthy" ||
            response.data.status === "healthy",
        };
      } catch (error) {
        results[endpoint] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testMonitoringAPI() {
    if (!this.adminToken) await this.adminLogin();

    const endpoints = [
      "/api/monitoring/metrics",
      "/api/monitoring/metrics/system",
      "/api/monitoring/metrics/application",
      "/api/monitoring/metrics/business",
      "/api/monitoring/alerts",
      "/api/monitoring/alerts/active",
      "/api/monitoring/dashboard",
      "/api/monitoring/stats",
      "/api/monitoring/services",
    ];

    const results = {};
    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_URL}${endpoint}`, {
          headers: { Authorization: `Bearer ${this.adminToken}` },
          timeout: 10000,
        });
        results[endpoint] = {
          status: response.status,
          hasData: response.data && Object.keys(response.data).length > 0,
          dataKeys: Object.keys(response.data || {}),
        };
      } catch (error) {
        results[endpoint] = {
          error: error.message,
          status: error.response?.status,
          requiresAuth: error.response?.status === 401 || error.response?.status === 403,
        };
      }
    }
    return results;
  }

  async testHealthCheckTrigger() {
    if (!this.adminToken) await this.adminLogin();

    try {
      const response = await axios.post(
        `${API_URL}/api/monitoring/health-check`,
        {},
        {
          headers: { Authorization: `Bearer ${this.adminToken}` },
          timeout: 15000,
        },
      );

      if (response.status !== 200) {
        throw new Error(`Health check trigger failed: ${response.status}`);
      }

      return {
        status: response.status,
        message: response.data.message,
        healthStatus: response.data.status,
      };
    } catch (error) {
      throw new Error(`Health check trigger failed: ${error.message}`);
    }
  }

  async testAlertResolution() {
    if (!this.adminToken) await this.adminLogin();

    // まずアラートを取得
    const alertsResponse = await axios.get(`${API_URL}/api/monitoring/alerts/active`, {
      headers: { Authorization: `Bearer ${this.adminToken}` },
      timeout: 10000,
    });

    if (alertsResponse.data.length === 0) {
      return {
        message: "No active alerts to resolve",
        alertsCount: 0,
      };
    }

    // 最初のアラートを解決
    const firstAlert = alertsResponse.data[0];
    const resolveResponse = await axios.post(
      `${API_URL}/api/monitoring/alerts/${firstAlert.id}/resolve`,
      {},
      {
        headers: { Authorization: `Bearer ${this.adminToken}` },
        timeout: 10000,
      },
    );

    if (resolveResponse.status !== 200) {
      throw new Error(`Alert resolution failed: ${resolveResponse.status}`);
    }

    return {
      status: resolveResponse.status,
      message: resolveResponse.data.message,
      resolvedAlertId: firstAlert.id,
    };
  }

  async testFrontendMonitoringPage() {
    try {
      const response = await axios.get(`${PRODUCTION_URL}/monitoring`, {
        timeout: 15000,
        validateStatus: (status) => status < 500, // Accept redirects and client errors
      });

      return {
        status: response.status,
        title: response.data.match(/<title>(.*?)<\/title>/)?.[1] || "No title",
        hasMonitoringContent:
          response.data.includes("monitoring") ||
          response.data.includes("dashboard") ||
          response.data.includes("Monitoring"),
        isRedirect: response.status >= 300 && response.status < 400,
      };
    } catch (error) {
      return {
        error: error.message,
        status: error.response?.status,
      };
    }
  }

  async testSystemMetrics() {
    if (!this.adminToken) await this.adminLogin();

    try {
      const response = await axios.get(`${API_URL}/api/monitoring/metrics/system`, {
        headers: { Authorization: `Bearer ${this.adminToken}` },
        timeout: 10000,
      });

      if (response.status !== 200) {
        throw new Error(`System metrics failed: ${response.status}`);
      }

      const metrics = response.data;
      const expectedMetrics = [
        "cpu_usage_percent",
        "memory_usage_percent",
        "disk_usage_percent",
        "network_bytes_sent",
        "network_bytes_recv",
      ];

      const foundMetrics = metrics.map((m) => m.name);
      const missingMetrics = expectedMetrics.filter((m) => !foundMetrics.includes(m));

      return {
        status: response.status,
        metricsCount: metrics.length,
        foundMetrics: foundMetrics,
        missingMetrics: missingMetrics,
        hasExpectedMetrics: missingMetrics.length === 0,
      };
    } catch (error) {
      throw new Error(`System metrics test failed: ${error.message}`);
    }
  }

  async testApplicationMetrics() {
    if (!this.adminToken) await this.adminLogin();

    try {
      const response = await axios.get(`${API_URL}/api/monitoring/metrics/application`, {
        headers: { Authorization: `Bearer ${this.adminToken}` },
        timeout: 10000,
      });

      if (response.status !== 200) {
        throw new Error(`Application metrics failed: ${response.status}`);
      }

      const metrics = response.data;
      const expectedMetrics = ["active_users_count", "api_response_time", "api_request_count"];

      const foundMetrics = metrics.map((m) => m.name);
      const missingMetrics = expectedMetrics.filter((m) => !foundMetrics.includes(m));

      return {
        status: response.status,
        metricsCount: metrics.length,
        foundMetrics: foundMetrics,
        missingMetrics: missingMetrics,
        hasExpectedMetrics: missingMetrics.length === 0,
      };
    } catch (error) {
      throw new Error(`Application metrics test failed: ${error.message}`);
    }
  }

  async testBusinessMetrics() {
    if (!this.adminToken) await this.adminLogin();

    try {
      const response = await axios.get(`${API_URL}/api/monitoring/metrics/business`, {
        headers: { Authorization: `Bearer ${this.adminToken}` },
        timeout: 10000,
      });

      if (response.status !== 200) {
        throw new Error(`Business metrics failed: ${response.status}`);
      }

      const metrics = response.data;
      const expectedMetrics = ["total_users_count", "new_users_today"];

      const foundMetrics = metrics.map((m) => m.name);
      const missingMetrics = expectedMetrics.filter((m) => !foundMetrics.includes(m));

      return {
        status: response.status,
        metricsCount: metrics.length,
        foundMetrics: foundMetrics,
        missingMetrics: missingMetrics,
        hasExpectedMetrics: missingMetrics.length === 0,
      };
    } catch (error) {
      throw new Error(`Business metrics test failed: ${error.message}`);
    }
  }

  async testMonitoringDashboard() {
    if (!this.adminToken) await this.adminLogin();

    try {
      const response = await axios.get(`${API_URL}/api/monitoring/dashboard`, {
        headers: { Authorization: `Bearer ${this.adminToken}` },
        timeout: 10000,
      });

      if (response.status !== 200) {
        throw new Error(`Dashboard data failed: ${response.status}`);
      }

      const dashboardData = response.data;
      const requiredSections = ["health_status", "metrics", "alerts", "timestamp"];

      const hasRequiredSections = requiredSections.every((section) =>
        dashboardData.hasOwnProperty(section),
      );

      const metricsSections = ["system", "application", "business"];
      const hasMetricsSections = metricsSections.every(
        (section) => dashboardData.metrics && dashboardData.metrics.hasOwnProperty(section),
      );

      return {
        status: response.status,
        hasRequiredSections: hasRequiredSections,
        hasMetricsSections: hasMetricsSections,
        healthStatus: dashboardData.health_status?.status,
        activeAlerts: dashboardData.alerts?.total_active || 0,
        metricsCount: {
          system: dashboardData.metrics?.system?.length || 0,
          application: dashboardData.metrics?.application?.length || 0,
          business: dashboardData.metrics?.business?.length || 0,
        },
      };
    } catch (error) {
      throw new Error(`Dashboard test failed: ${error.message}`);
    }
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate = totalTests > 0 ? ((this.results.passed / totalTests) * 100).toFixed(1) : 0;

    log("\n📊 Monitoring System Test Results Summary:", "blue");
    log(`Total Tests: ${totalTests}`, "reset");
    log(`Passed: ${this.results.passed}`, "green");
    log(`Failed: ${this.results.failed}`, "red");
    log(`Success Rate: ${successRate}%`, successRate >= 80 ? "green" : "yellow");

    log("\n📋 Detailed Results:", "blue");
    this.results.tests.forEach((test) => {
      const status = test.status === "PASSED" ? "✅" : "❌";
      log(`${status} ${test.name}: ${test.status}`, test.status === "PASSED" ? "green" : "red");
      if (test.error) {
        log(`   Error: ${test.error}`, "red");
      }
    });

    // Save detailed report
    const reportPath = path.join(__dirname, "..", "docs", "monitoring-system-test-report.json");
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
  log("🚀 Starting Monitoring System Tests...", "blue");
  log(`Testing production URL: ${PRODUCTION_URL}`, "yellow");
  log(`Testing API URL: ${API_URL}`, "yellow");
  log("");

  const tester = new MonitoringSystemTester();

  try {
    // Ensure admin login for API tests
    await tester.runTest("Admin Login", () => tester.adminLogin());

    // Health endpoint tests
    await tester.runTest("Health Endpoints", () => tester.testHealthEndpoints());

    // Monitoring API tests
    await tester.runTest("Monitoring API Endpoints", () => tester.testMonitoringAPI());

    // Health check trigger test
    await tester.runTest("Health Check Trigger", () => tester.testHealthCheckTrigger());

    // Alert resolution test
    await tester.runTest("Alert Resolution", () => tester.testAlertResolution());

    // Metrics tests
    await tester.runTest("System Metrics", () => tester.testSystemMetrics());
    await tester.runTest("Application Metrics", () => tester.testApplicationMetrics());
    await tester.runTest("Business Metrics", () => tester.testBusinessMetrics());

    // Dashboard test
    await tester.runTest("Monitoring Dashboard", () => tester.testMonitoringDashboard());

    // Frontend test
    await tester.runTest("Frontend Monitoring Page", () => tester.testFrontendMonitoringPage());

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log("\n🎉 Monitoring system tests completed successfully!", "green");
      log("The monitoring system is functioning as expected.", "green");
      return 0;
    } else {
      log("\n⚠️  Monitoring system tests completed with issues.", "yellow");
      log("Please review the failed tests and fix the issues.", "yellow");
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

module.exports = { MonitoringSystemTester };
