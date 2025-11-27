#!/usr/bin/env node
/**
 * Production Environment Test Script
 * Tests all critical functionality in production
 */

const https = require("https");
const http = require("http");

// Configuration
const PRODUCTION_URL = "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app";
const SUPABASE_URL = "https://ndetbklyymekcifheqaj.supabase.co";

// Test results
const testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  details: [],
};

// Utility function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith("https") ? https : http;

    const req = protocol.request(url, options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data,
        });
      });
    });

    req.on("error", reject);
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error("Request timeout"));
    });

    req.end();
  });
}

// Test function
async function runTest(name, testFn) {
  testResults.total++;
  console.log(`\n🧪 Testing: ${name}`);

  try {
    await testFn();
    testResults.passed++;
    testResults.details.push({ name, status: "PASS", message: "Test passed" });
    console.log(`✅ ${name}: PASSED`);
  } catch (error) {
    testResults.failed++;
    testResults.details.push({ name, status: "FAIL", message: error.message });
    console.log(`❌ ${name}: FAILED - ${error.message}`);
  }
}

// Individual tests
async function testHomepage() {
  const response = await makeRequest(PRODUCTION_URL);

  if (response.statusCode !== 200) {
    throw new Error(`Expected status 200, got ${response.statusCode}`);
  }

  if (!response.data.includes("AICA-SyS")) {
    throw new Error("Homepage does not contain expected content");
  }
}

async function testHealthCheck() {
  const response = await makeRequest(`${PRODUCTION_URL}/api/health`);

  if (response.statusCode !== 200) {
    throw new Error(`Health check failed with status ${response.statusCode}`);
  }

  const healthData = JSON.parse(response.data);
  if (healthData.status !== "healthy") {
    throw new Error(`Health check returned status: ${healthData.status}`);
  }
}

async function testSupabaseConnection() {
  const response = await makeRequest(`${SUPABASE_URL}/rest/v1/`, {
    headers: {
      apikey: process.env.SUPABASE_ANON_KEY || "test-key",
    },
  });

  if (response.statusCode !== 200) {
    throw new Error(`Supabase connection failed with status ${response.statusCode}`);
  }
}

async function testAPIEndpoints() {
  const endpoints = ["/api/articles", "/api/trends", "/api/newsletters"];

  for (const endpoint of endpoints) {
    try {
      const response = await makeRequest(`${PRODUCTION_URL}${endpoint}`);

      // API endpoints should return 200 or 404 (if no data)
      if (response.statusCode !== 200 && response.statusCode !== 404) {
        throw new Error(`Endpoint ${endpoint} returned status ${response.statusCode}`);
      }
    } catch (error) {
      throw new Error(`Endpoint ${endpoint} failed: ${error.message}`);
    }
  }
}

async function testStaticAssets() {
  const assets = ["/favicon.ico", "/robots.txt", "/sitemap.xml"];

  for (const asset of assets) {
    try {
      const response = await makeRequest(`${PRODUCTION_URL}${asset}`);

      if (response.statusCode !== 200) {
        throw new Error(`Asset ${asset} returned status ${response.statusCode}`);
      }
    } catch (error) {
      throw new Error(`Asset ${asset} failed: ${error.message}`);
    }
  }
}

async function testPerformance() {
  const startTime = Date.now();
  const response = await makeRequest(PRODUCTION_URL);
  const endTime = Date.now();

  const responseTime = endTime - startTime;

  if (responseTime > 5000) {
    throw new Error(`Response time too slow: ${responseTime}ms`);
  }

  console.log(`   Response time: ${responseTime}ms`);
}

async function testSecurityHeaders() {
  const response = await makeRequest(PRODUCTION_URL);

  const securityHeaders = [
    "x-frame-options",
    "x-content-type-options",
    "x-xss-protection",
    "referrer-policy",
  ];

  const missingHeaders = securityHeaders.filter(
    (header) => !response.headers[header] && !response.headers[header.toLowerCase()],
  );

  if (missingHeaders.length > 0) {
    throw new Error(`Missing security headers: ${missingHeaders.join(", ")}`);
  }
}

// Main test runner
async function runAllTests() {
  console.log("🚀 Starting Production Environment Tests");
  console.log(`📍 Testing URL: ${PRODUCTION_URL}`);
  console.log(`📍 Supabase URL: ${SUPABASE_URL}`);

  // Run all tests
  await runTest("Homepage Loading", testHomepage);
  await runTest("Health Check", testHealthCheck);
  await runTest("Supabase Connection", testSupabaseConnection);
  await runTest("API Endpoints", testAPIEndpoints);
  await runTest("Static Assets", testStaticAssets);
  await runTest("Performance", testPerformance);
  await runTest("Security Headers", testSecurityHeaders);

  // Print results
  console.log("\n📊 Test Results Summary");
  console.log("========================");
  console.log(`Total Tests: ${testResults.total}`);
  console.log(`Passed: ${testResults.passed}`);
  console.log(`Failed: ${testResults.failed}`);
  console.log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);

  if (testResults.failed > 0) {
    console.log("\n❌ Failed Tests:");
    testResults.details
      .filter((test) => test.status === "FAIL")
      .forEach((test) => console.log(`   - ${test.name}: ${test.message}`));
  }

  if (testResults.failed === 0) {
    console.log("\n🎉 All tests passed! Production environment is healthy.");
  } else {
    console.log("\n⚠️  Some tests failed. Please check the issues above.");
    process.exit(1);
  }
}

// Run tests
runAllTests().catch((error) => {
  console.error("💥 Test runner failed:", error);
  process.exit(1);
});
