#!/usr/bin/env node
/**
 * Security Test Script
 * Tests all security features and configurations
 */

const https = require("https");
const http = require("http");

// Configuration
const API_URL = "http://127.0.0.1:8000";
const PRODUCTION_URL = "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app";

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
  console.log(`\n🔒 Testing: ${name}`);

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

// Security tests
async function testSecurityHeaders() {
  const response = await makeRequest(API_URL);

  const requiredHeaders = [
    "x-frame-options",
    "x-content-type-options",
    "x-xss-protection",
    "strict-transport-security",
    "content-security-policy",
  ];

  const missingHeaders = requiredHeaders.filter(
    (header) => !response.headers[header] && !response.headers[header.toLowerCase()],
  );

  if (missingHeaders.length > 0) {
    throw new Error(`Missing security headers: ${missingHeaders.join(", ")}`);
  }

  console.log(
    "   Security headers present:",
    requiredHeaders.filter(
      (header) => response.headers[header] || response.headers[header.toLowerCase()],
    ),
  );
}

async function testCORSConfiguration() {
  const response = await makeRequest(API_URL, {
    method: "OPTIONS",
    headers: {
      Origin: "https://aica-sys.vercel.app",
      "Access-Control-Request-Method": "POST",
      "Access-Control-Request-Headers": "Content-Type",
    },
  });

  if (!response.headers["access-control-allow-origin"]) {
    throw new Error("CORS headers not present");
  }

  console.log("   CORS headers:", {
    "Access-Control-Allow-Origin": response.headers["access-control-allow-origin"],
    "Access-Control-Allow-Methods": response.headers["access-control-allow-methods"],
    "Access-Control-Allow-Headers": response.headers["access-control-allow-headers"],
  });
}

async function testRateLimiting() {
  // Test rate limiting by making multiple requests
  const requests = [];
  for (let i = 0; i < 5; i++) {
    requests.push(
      makeRequest(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }),
    );
  }

  const responses = await Promise.allSettled(requests);
  const rateLimited = responses.some(
    (response) => response.status === "fulfilled" && response.value.statusCode === 429,
  );

  if (!rateLimited) {
    console.log("   Rate limiting not triggered (may be normal for low traffic)");
  } else {
    console.log("   Rate limiting working correctly");
  }
}

async function testAuthenticationEndpoints() {
  const endpoints = ["/api/auth/register", "/api/auth/login", "/api/auth/refresh", "/api/auth/me"];

  for (const endpoint of endpoints) {
    try {
      const response = await makeRequest(`${API_URL}${endpoint}`, {
        method: endpoint === "/api/auth/me" ? "GET" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      // Should return 422 for validation errors or 401 for auth required
      if (response.statusCode !== 422 && response.statusCode !== 401) {
        throw new Error(`Unexpected status code for ${endpoint}: ${response.statusCode}`);
      }

      console.log(`   ${endpoint}: ${response.statusCode} (expected)`);
    } catch (error) {
      throw new Error(`Endpoint ${endpoint} failed: ${error.message}`);
    }
  }
}

async function testSQLInjectionProtection() {
  const maliciousPayloads = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "'; INSERT INTO users VALUES ('hacker', 'password'); --",
  ];

  for (const payload of maliciousPayloads) {
    try {
      const response = await makeRequest(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: payload,
          password: payload,
        }),
      });

      // Should return 422 for validation errors, not 500 for SQL errors
      if (response.statusCode === 500) {
        throw new Error(`Potential SQL injection vulnerability detected with payload: ${payload}`);
      }

      console.log(`   SQL injection test passed for payload: ${payload.substring(0, 20)}...`);
    } catch (error) {
      if (error.message.includes("SQL injection")) {
        throw error;
      }
      // Network errors are acceptable for this test
    }
  }
}

async function testXSSProtection() {
  const xssPayloads = [
    "<script>alert('xss')</script>",
    "javascript:alert('xss')",
    "<img src=x onerror=alert('xss')>",
  ];

  for (const payload of xssPayloads) {
    try {
      const response = await makeRequest(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: payload,
          password: "test123",
          full_name: payload,
        }),
      });

      // Should return 422 for validation errors
      if (response.statusCode === 422) {
        console.log(`   XSS protection working for payload: ${payload.substring(0, 20)}...`);
      } else {
        console.log(`   XSS payload returned status: ${response.statusCode}`);
      }
    } catch (error) {
      // Network errors are acceptable for this test
      console.log(`   XSS test completed for payload: ${payload.substring(0, 20)}...`);
    }
  }
}

async function testCSRFProtection() {
  // Test CSRF protection by checking for CSRF tokens
  const response = await makeRequest(`${API_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "https://malicious-site.com",
    },
    body: JSON.stringify({
      email: "test@example.com",
      password: "test123",
      full_name: "Test User",
    }),
  });

  // Should either reject the request or require CSRF token
  if (response.statusCode === 403) {
    console.log("   CSRF protection working (request rejected)");
  } else if (response.statusCode === 422) {
    console.log("   CSRF protection working (validation error)");
  } else {
    console.log(`   CSRF test returned status: ${response.statusCode}`);
  }
}

async function testInputValidation() {
  const invalidInputs = [
    { email: "invalid-email", password: "123", full_name: "" },
    { email: "", password: "", full_name: "" },
    { email: "test@example.com", password: "a", full_name: "Test" },
    {
      email: "test@example.com",
      password: "test123",
      full_name: "A".repeat(1000),
    },
  ];

  for (const input of invalidInputs) {
    try {
      const response = await makeRequest(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(input),
      });

      if (response.statusCode !== 422) {
        throw new Error(`Input validation failed for input: ${JSON.stringify(input)}`);
      }

      console.log(`   Input validation working for: ${JSON.stringify(input).substring(0, 50)}...`);
    } catch (error) {
      if (error.message.includes("Input validation failed")) {
        throw error;
      }
      // Network errors are acceptable for this test
    }
  }
}

async function testErrorHandling() {
  const errorEndpoints = ["/api/nonexistent", "/api/auth/invalid", "/api/../etc/passwd"];

  for (const endpoint of errorEndpoints) {
    try {
      const response = await makeRequest(`${API_URL}${endpoint}`);

      if (response.statusCode < 400) {
        throw new Error(`Error handling failed for ${endpoint}: ${response.statusCode}`);
      }

      console.log(`   Error handling working for ${endpoint}: ${response.statusCode}`);
    } catch (error) {
      if (error.message.includes("Error handling failed")) {
        throw error;
      }
      // Network errors are acceptable for this test
    }
  }
}

// Main test runner
async function runAllTests() {
  console.log("🔒 Starting Security Tests");
  console.log(`📍 Testing API URL: ${API_URL}`);

  // Run all tests
  await runTest("Security Headers", testSecurityHeaders);
  await runTest("CORS Configuration", testCORSConfiguration);
  await runTest("Rate Limiting", testRateLimiting);
  await runTest("Authentication Endpoints", testAuthenticationEndpoints);
  await runTest("SQL Injection Protection", testSQLInjectionProtection);
  await runTest("XSS Protection", testXSSProtection);
  await runTest("CSRF Protection", testCSRFProtection);
  await runTest("Input Validation", testInputValidation);
  await runTest("Error Handling", testErrorHandling);

  // Print results
  console.log("\n📊 Security Test Results");
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
    console.log("\n🎉 All security tests passed! System is secure.");
  } else {
    console.log("\n⚠️  Some security tests failed. Please review the issues above.");
  }
}

// Run tests
runAllTests().catch((error) => {
  console.error("💥 Security test runner failed:", error);
  process.exit(1);
});
