#!/usr/bin/env node
/**
 * Monitoring Setup Script
 * Sets up monitoring and alerting for production environment
 */

const https = require("https");
const http = require("http");

// Configuration
const PRODUCTION_URL = "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app";
const SUPABASE_URL = "https://ndetbklyymekcifheqaj.supabase.co";

// Monitoring configuration
const monitoringConfig = {
  checkInterval: 300000, // 5 minutes
  timeout: 10000, // 10 seconds
  retries: 3,
  alertThresholds: {
    responseTime: 5000, // 5 seconds
    errorRate: 0.1, // 10%
    uptime: 0.99, // 99%
  },
};

// Monitoring data
const monitoringData = {
  checks: [],
  alerts: [],
  uptime: 0,
  totalChecks: 0,
  successfulChecks: 0,
  failedChecks: 0,
};

// Utility function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith("https") ? https : http;

    const req = protocol.request(url, options, (res) => {
      let data = "";

      res.on("data", (chunk) => {
        data += chunk;
      });

      res.on("end", () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data,
          responseTime: Date.now() - req.startTime,
        });
      });
    });

    req.on("error", reject);
    req.setTimeout(options.timeout || monitoringConfig.timeout, () => {
      req.destroy();
      reject(new Error("Request timeout"));
    });

    req.startTime = Date.now();
    req.end();
  });
}

// Health check function
async function performHealthCheck() {
  const check = {
    timestamp: new Date().toISOString(),
    url: PRODUCTION_URL,
    status: "unknown",
    responseTime: 0,
    error: null,
  };

  try {
    const response = await makeRequest(PRODUCTION_URL);
    check.status = response.statusCode === 401 ? "healthy" : "unhealthy";
    check.responseTime = response.responseTime;

    if (response.statusCode !== 200 && response.statusCode !== 401) {
      check.error = `Unexpected status code: ${response.statusCode}`;
    }
  } catch (error) {
    check.status = "unhealthy";
    check.error = error.message;
  }

  monitoringData.checks.push(check);
  monitoringData.totalChecks++;

  if (check.status === "healthy") {
    monitoringData.successfulChecks++;
  } else {
    monitoringData.failedChecks++;
  }

  // Calculate uptime
  monitoringData.uptime = monitoringData.successfulChecks / monitoringData.totalChecks;

  return check;
}

// Alert function
function checkAlerts(check) {
  const alerts = [];

  // Response time alert
  if (check.responseTime > monitoringConfig.alertThresholds.responseTime) {
    alerts.push({
      type: "performance",
      message: `Response time too slow: ${check.responseTime}ms`,
      severity: "warning",
    });
  }

  // Error rate alert
  const recentChecks = monitoringData.checks.slice(-10); // Last 10 checks
  const errorRate =
    recentChecks.filter((c) => c.status === "unhealthy").length / recentChecks.length;

  if (errorRate > monitoringConfig.alertThresholds.errorRate) {
    alerts.push({
      type: "reliability",
      message: `High error rate: ${(errorRate * 100).toFixed(1)}%`,
      severity: "critical",
    });
  }

  // Uptime alert
  if (monitoringData.uptime < monitoringConfig.alertThresholds.uptime) {
    alerts.push({
      type: "uptime",
      message: `Low uptime: ${(monitoringData.uptime * 100).toFixed(1)}%`,
      severity: "warning",
    });
  }

  alerts.forEach((alert) => {
    monitoringData.alerts.push({
      ...alert,
      timestamp: new Date().toISOString(),
    });
    console.log(`🚨 ALERT: ${alert.message}`);
  });

  return alerts;
}

// Generate monitoring report
function generateReport() {
  const report = {
    timestamp: new Date().toISOString(),
    uptime: monitoringData.uptime,
    totalChecks: monitoringData.totalChecks,
    successfulChecks: monitoringData.successfulChecks,
    failedChecks: monitoringData.failedChecks,
    averageResponseTime: 0,
    recentAlerts: monitoringData.alerts.slice(-5),
    status: monitoringData.uptime > 0.95 ? "healthy" : "unhealthy",
  };

  // Calculate average response time
  const recentChecks = monitoringData.checks.slice(-10);
  if (recentChecks.length > 0) {
    report.averageResponseTime =
      recentChecks.reduce((sum, check) => sum + check.responseTime, 0) / recentChecks.length;
  }

  return report;
}

// Main monitoring function
async function startMonitoring() {
  console.log("🔍 Starting Production Monitoring");
  console.log(`📍 Monitoring URL: ${PRODUCTION_URL}`);
  console.log(`⏰ Check Interval: ${monitoringConfig.checkInterval / 1000} seconds`);
  console.log(`🚨 Alert Thresholds:`);
  console.log(`   - Response Time: ${monitoringConfig.alertThresholds.responseTime}ms`);
  console.log(`   - Error Rate: ${monitoringConfig.alertThresholds.errorRate * 100}%`);
  console.log(`   - Uptime: ${monitoringConfig.alertThresholds.uptime * 100}%`);

  // Perform initial check
  console.log("\n🧪 Performing initial health check...");
  const initialCheck = await performHealthCheck();
  console.log(`✅ Initial check: ${initialCheck.status} (${initialCheck.responseTime}ms)`);

  // Check for alerts
  checkAlerts(initialCheck);

  // Set up interval monitoring
  const intervalId = setInterval(async () => {
    console.log(`\n🔍 Health check at ${new Date().toISOString()}`);

    const check = await performHealthCheck();
    console.log(`   Status: ${check.status}`);
    console.log(`   Response Time: ${check.responseTime}ms`);
    console.log(`   Uptime: ${(monitoringData.uptime * 100).toFixed(1)}%`);

    if (check.error) {
      console.log(`   Error: ${check.error}`);
    }

    // Check for alerts
    checkAlerts(check);

    // Generate and display report every 10 checks
    if (monitoringData.totalChecks % 10 === 0) {
      const report = generateReport();
      console.log("\n📊 Monitoring Report");
      console.log("==================");
      console.log(`Status: ${report.status}`);
      console.log(`Uptime: ${(report.uptime * 100).toFixed(1)}%`);
      console.log(`Total Checks: ${report.totalChecks}`);
      console.log(`Average Response Time: ${report.averageResponseTime.toFixed(0)}ms`);
      console.log(`Recent Alerts: ${report.recentAlerts.length}`);
    }
  }, monitoringConfig.checkInterval);

  // Handle graceful shutdown
  process.on("SIGINT", () => {
    console.log("\n🛑 Shutting down monitoring...");
    clearInterval(intervalId);

    const finalReport = generateReport();
    console.log("\n📊 Final Monitoring Report");
    console.log("==========================");
    console.log(`Final Status: ${finalReport.status}`);
    console.log(`Final Uptime: ${(finalReport.uptime * 100).toFixed(1)}%`);
    console.log(`Total Checks: ${finalReport.totalChecks}`);
    console.log(`Average Response Time: ${finalReport.averageResponseTime.toFixed(0)}ms`);
    console.log(`Total Alerts: ${monitoringData.alerts.length}`);

    process.exit(0);
  });
}

// Run monitoring
startMonitoring().catch((error) => {
  console.error("💥 Monitoring failed:", error);
  process.exit(1);
});
