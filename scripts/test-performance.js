#!/usr/bin/env node
/**
 * Performance Test Script
 * Comprehensive performance testing for AICA-SyS
 */

const https = require('https');
const http = require('http');
const { performance } = require('perf_hooks');

// Configuration
const API_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:3000';
const CONCURRENT_USERS = 10;
const TEST_DURATION = 30000; // 30 seconds
const REQUEST_INTERVAL = 100; // 100ms

// Test results
const testResults = {
  totalRequests: 0,
  successfulRequests: 0,
  failedRequests: 0,
  responseTimes: [],
  errors: [],
  startTime: 0,
  endTime: 0,
  throughput: 0,
  averageResponseTime: 0,
  p95ResponseTime: 0,
  p99ResponseTime: 0,
};

// Test scenarios
const testScenarios = [
  {
    name: 'Homepage Load',
    url: FRONTEND_URL,
    method: 'GET',
    weight: 30,
  },
  {
    name: 'API Health Check',
    url: `${API_URL}/health`,
    method: 'GET',
    weight: 20,
  },
  {
    name: 'API Root',
    url: `${API_URL}/`,
    method: 'GET',
    weight: 15,
  },
  {
    name: 'API Auth Endpoints',
    url: `${API_URL}/api/auth/register`,
    method: 'POST',
    weight: 10,
    body: JSON.stringify({
      email: 'test@example.com',
      password: 'test123',
      full_name: 'Test User',
    }),
  },
  {
    name: 'API Content Endpoints',
    url: `${API_URL}/api/content/articles`,
    method: 'GET',
    weight: 15,
  },
  {
    name: 'API Analysis Endpoints',
    url: `${API_URL}/api/analysis/trends`,
    method: 'GET',
    weight: 10,
  },
];

// Utility functions
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const startTime = performance.now();

    const req = protocol.request(url, options, res => {
      let data = '';
      res.on('data', chunk => (data += chunk));
      res.on('end', () => {
        const endTime = performance.now();
        const responseTime = endTime - startTime;

        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data,
          responseTime: responseTime,
        });
      });
    });

    req.on('error', error => {
      const endTime = performance.now();
      const responseTime = endTime - startTime;

      reject({
        error: error.message,
        responseTime: responseTime,
      });
    });

    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    if (options.body) {
      req.write(options.body);
    }

    req.end();
  });
}

function selectRandomScenario() {
  const totalWeight = testScenarios.reduce(
    (sum, scenario) => sum + scenario.weight,
    0
  );
  let random = Math.random() * totalWeight;

  for (const scenario of testScenarios) {
    random -= scenario.weight;
    if (random <= 0) {
      return scenario;
    }
  }

  return testScenarios[0];
}

async function runSingleRequest() {
  const scenario = selectRandomScenario();
  const options = {
    method: scenario.method,
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'Performance-Test/1.0',
    },
  };

  if (scenario.body) {
    options.body = scenario.body;
  }

  try {
    const response = await makeRequest(scenario.url, options);

    testResults.totalRequests++;
    testResults.responseTimes.push(response.responseTime);

    if (response.statusCode >= 200 && response.statusCode < 400) {
      testResults.successfulRequests++;
    } else {
      testResults.failedRequests++;
      testResults.errors.push({
        scenario: scenario.name,
        statusCode: response.statusCode,
        responseTime: response.responseTime,
      });
    }
  } catch (error) {
    testResults.totalRequests++;
    testResults.failedRequests++;
    testResults.errors.push({
      scenario: scenario.name,
      error: error.error || error.message,
      responseTime: error.responseTime || 0,
    });
  }
}

function calculateMetrics() {
  if (testResults.responseTimes.length === 0) {
    return;
  }

  const sortedTimes = testResults.responseTimes.sort((a, b) => a - b);
  const totalTime = (testResults.endTime - testResults.startTime) / 1000; // seconds

  testResults.averageResponseTime =
    testResults.responseTimes.reduce((a, b) => a + b, 0) /
    testResults.responseTimes.length;
  testResults.throughput = testResults.totalRequests / totalTime;

  // Calculate percentiles
  const p95Index = Math.floor(sortedTimes.length * 0.95);
  const p99Index = Math.floor(sortedTimes.length * 0.99);

  testResults.p95ResponseTime = sortedTimes[p95Index] || 0;
  testResults.p99ResponseTime = sortedTimes[p99Index] || 0;
}

function printResults() {
  console.log('\n📊 Performance Test Results');
  console.log('============================');
  console.log(
    `Test Duration: ${(
      (testResults.endTime - testResults.startTime) /
      1000
    ).toFixed(2)}s`
  );
  console.log(`Total Requests: ${testResults.totalRequests}`);
  console.log(`Successful Requests: ${testResults.successfulRequests}`);
  console.log(`Failed Requests: ${testResults.failedRequests}`);
  console.log(
    `Success Rate: ${(
      (testResults.successfulRequests / testResults.totalRequests) *
      100
    ).toFixed(2)}%`
  );
  console.log(
    `Throughput: ${testResults.throughput.toFixed(2)} requests/second`
  );
  console.log(
    `Average Response Time: ${testResults.averageResponseTime.toFixed(2)}ms`
  );
  console.log(`95th Percentile: ${testResults.p95ResponseTime.toFixed(2)}ms`);
  console.log(`99th Percentile: ${testResults.p99ResponseTime.toFixed(2)}ms`);

  if (testResults.errors.length > 0) {
    console.log('\n❌ Errors:');
    testResults.errors.slice(0, 10).forEach((error, index) => {
      console.log(
        `  ${index + 1}. ${error.scenario}: ${
          error.error || error.statusCode
        } (${error.responseTime.toFixed(2)}ms)`
      );
    });

    if (testResults.errors.length > 10) {
      console.log(`  ... and ${testResults.errors.length - 10} more errors`);
    }
  }

  // Performance assessment
  console.log('\n🎯 Performance Assessment:');

  if (testResults.averageResponseTime < 200) {
    console.log('✅ Average response time: EXCELLENT (< 200ms)');
  } else if (testResults.averageResponseTime < 500) {
    console.log('✅ Average response time: GOOD (< 500ms)');
  } else if (testResults.averageResponseTime < 1000) {
    console.log('⚠️  Average response time: ACCEPTABLE (< 1000ms)');
  } else {
    console.log('❌ Average response time: POOR (> 1000ms)');
  }

  if (testResults.p95ResponseTime < 500) {
    console.log('✅ 95th percentile: EXCELLENT (< 500ms)');
  } else if (testResults.p95ResponseTime < 1000) {
    console.log('✅ 95th percentile: GOOD (< 1000ms)');
  } else if (testResults.p95ResponseTime < 2000) {
    console.log('⚠️  95th percentile: ACCEPTABLE (< 2000ms)');
  } else {
    console.log('❌ 95th percentile: POOR (> 2000ms)');
  }

  if (testResults.throughput > 100) {
    console.log('✅ Throughput: EXCELLENT (> 100 req/s)');
  } else if (testResults.throughput > 50) {
    console.log('✅ Throughput: GOOD (> 50 req/s)');
  } else if (testResults.throughput > 20) {
    console.log('⚠️  Throughput: ACCEPTABLE (> 20 req/s)');
  } else {
    console.log('❌ Throughput: POOR (< 20 req/s)');
  }

  const successRate =
    (testResults.successfulRequests / testResults.totalRequests) * 100;
  if (successRate > 99) {
    console.log('✅ Success rate: EXCELLENT (> 99%)');
  } else if (successRate > 95) {
    console.log('✅ Success rate: GOOD (> 95%)');
  } else if (successRate > 90) {
    console.log('⚠️  Success rate: ACCEPTABLE (> 90%)');
  } else {
    console.log('❌ Success rate: POOR (< 90%)');
  }
}

async function runLoadTest() {
  console.log('🚀 Starting Performance Test');
  console.log(`📍 Testing: ${API_URL} and ${FRONTEND_URL}`);
  console.log(`👥 Concurrent Users: ${CONCURRENT_USERS}`);
  console.log(`⏱️  Test Duration: ${TEST_DURATION / 1000}s`);
  console.log(`🔄 Request Interval: ${REQUEST_INTERVAL}ms`);

  testResults.startTime = performance.now();

  // Create concurrent users
  const userPromises = [];
  for (let i = 0; i < CONCURRENT_USERS; i++) {
    userPromises.push(runUserSimulation());
  }

  // Wait for test duration
  await new Promise(resolve => setTimeout(resolve, TEST_DURATION));

  testResults.endTime = performance.now();

  // Wait for all requests to complete
  await Promise.all(userPromises);

  calculateMetrics();
  printResults();
}

async function runUserSimulation() {
  while (performance.now() - testResults.startTime < TEST_DURATION) {
    await runSingleRequest();
    await new Promise(resolve => setTimeout(resolve, REQUEST_INTERVAL));
  }
}

// Run the test
runLoadTest().catch(error => {
  console.error('💥 Performance test failed:', error);
  process.exit(1);
});
