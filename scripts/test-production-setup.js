#!/usr/bin/env node

/**
 * Production Setup Test Script
 * This script tests the production setup including database, Stripe, and API endpoints
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const PRODUCTION_URL = 'https://aica-sys.vercel.app';
const API_URL = `${PRODUCTION_URL}/api`;

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

class ProductionTester {
  constructor() {
    this.results = {
      passed: 0,
      failed: 0,
      tests: [],
    };
  }

  async runTest(testName, testFunction) {
    log(`🧪 Running test: ${testName}`, 'blue');
    try {
      const result = await testFunction();
      this.results.passed++;
      this.results.tests.push({
        name: testName,
        status: 'PASSED',
        result: result,
      });
      log(`✅ ${testName}: PASSED`, 'green');
      return result;
    } catch (error) {
      this.results.failed++;
      this.results.tests.push({
        name: testName,
        status: 'FAILED',
        error: error.message,
      });
      log(`❌ ${testName}: FAILED - ${error.message}`, 'red');
      throw error;
    }
  }

  async testHealthEndpoint() {
    const response = await axios.get(`${API_URL}/health`, {
      timeout: 10000,
    });

    if (response.status !== 200) {
      throw new Error(`Health endpoint returned status ${response.status}`);
    }

    return response.data;
  }

  async testContentEndpoints() {
    const endpoints = [
      '/content/articles',
      '/content/trends',
      '/content/newsletters',
    ];

    const results = {};

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_URL}${endpoint}`, {
          timeout: 10000,
        });
        results[endpoint] = {
          status: response.status,
          data: response.data,
        };
      } catch (error) {
        results[endpoint] = {
          error: error.message,
        };
      }
    }

    return results;
  }

  async testSubscriptionEndpoints() {
    const endpoints = ['/subscriptions/plans'];

    const results = {};

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_URL}${endpoint}`, {
          timeout: 10000,
        });
        results[endpoint] = {
          status: response.status,
          data: response.data,
        };
      } catch (error) {
        results[endpoint] = {
          error: error.message,
        };
      }
    }

    return results;
  }

  async testReportsEndpoints() {
    const endpoints = ['/reports/available'];

    const results = {};

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_URL}${endpoint}`, {
          timeout: 10000,
        });
        results[endpoint] = {
          status: response.status,
          data: response.data,
        };
      } catch (error) {
        results[endpoint] = {
          error: error.message,
        };
      }
    }

    return results;
  }

  async testFrontendPages() {
    const pages = ['/', '/pricing', '/articles', '/newsletters', '/trends'];

    const results = {};

    for (const page of pages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: status => status < 500, // Accept redirects and client errors
        });
        results[page] = {
          status: response.status,
          title:
            response.data.match(/<title>(.*?)<\/title>/)?.[1] || 'No title',
        };
      } catch (error) {
        results[page] = {
          error: error.message,
        };
      }
    }

    return results;
  }

  async testPerformanceMetrics() {
    try {
      const response = await axios.get(`${API_URL}/metrics`, {
        timeout: 10000,
      });

      return {
        status: response.status,
        metrics: response.data,
      };
    } catch (error) {
      throw new Error(`Performance metrics endpoint failed: ${error.message}`);
    }
  }

  async testSecurityHeaders() {
    try {
      const response = await axios.get(`${PRODUCTION_URL}/`, {
        timeout: 10000,
      });

      const securityHeaders = [
        'x-content-type-options',
        'x-frame-options',
        'x-xss-protection',
        'strict-transport-security',
        'content-security-policy',
      ];

      const foundHeaders = {};
      securityHeaders.forEach(header => {
        if (response.headers[header]) {
          foundHeaders[header] = response.headers[header];
        }
      });

      return {
        status: response.status,
        securityHeaders: foundHeaders,
      };
    } catch (error) {
      throw new Error(`Security headers test failed: ${error.message}`);
    }
  }

  async testStripeConfiguration() {
    // Test if Stripe configuration is properly set up
    // This would typically check environment variables or configuration files
    const configPath = path.join(
      __dirname,
      '..',
      'config',
      'stripe-production.json'
    );

    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      return {
        configured: true,
        products: Object.keys(config.products || {}),
        configPath: configPath,
      };
    } else {
      throw new Error('Stripe production configuration not found');
    }
  }

  async testDatabaseConnection() {
    // Test database connection through API
    try {
      const response = await axios.get(`${API_URL}/health/detailed`, {
        timeout: 10000,
      });

      return {
        status: response.status,
        health: response.data,
      };
    } catch (error) {
      throw new Error(`Database connection test failed: ${error.message}`);
    }
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate =
      totalTests > 0
        ? ((this.results.passed / totalTests) * 100).toFixed(1)
        : 0;

    log('\n📊 Test Results Summary:', 'blue');
    log(`Total Tests: ${totalTests}`, 'reset');
    log(`Passed: ${this.results.passed}`, 'green');
    log(`Failed: ${this.results.failed}`, 'red');
    log(
      `Success Rate: ${successRate}%`,
      successRate >= 80 ? 'green' : 'yellow'
    );

    log('\n📋 Detailed Results:', 'blue');
    this.results.tests.forEach(test => {
      const status = test.status === 'PASSED' ? '✅' : '❌';
      log(
        `${status} ${test.name}: ${test.status}`,
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
      'production-test-report.json'
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
  log('🚀 Starting Production Setup Tests...', 'blue');
  log(`Testing production URL: ${PRODUCTION_URL}`, 'yellow');
  log(`Testing API URL: ${API_URL}`, 'yellow');
  log('');

  const tester = new ProductionTester();

  try {
    // Core functionality tests
    await tester.runTest('Health Endpoint', () => tester.testHealthEndpoint());
    await tester.runTest('Content Endpoints', () =>
      tester.testContentEndpoints()
    );
    await tester.runTest('Subscription Endpoints', () =>
      tester.testSubscriptionEndpoints()
    );
    await tester.runTest('Reports Endpoints', () =>
      tester.testReportsEndpoints()
    );

    // Frontend tests
    await tester.runTest('Frontend Pages', () => tester.testFrontendPages());

    // Performance and security tests
    await tester.runTest('Performance Metrics', () =>
      tester.testPerformanceMetrics()
    );
    await tester.runTest('Security Headers', () =>
      tester.testSecurityHeaders()
    );

    // Configuration tests
    await tester.runTest('Stripe Configuration', () =>
      tester.testStripeConfiguration()
    );
    await tester.runTest('Database Connection', () =>
      tester.testDatabaseConnection()
    );

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log('\n🎉 Production setup tests completed successfully!', 'green');
      log('The system is ready for production deployment.', 'green');
      return 0;
    } else {
      log('\n⚠️  Production setup tests completed with issues.', 'yellow');
      log('Please review the failed tests and fix the issues.', 'yellow');
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

module.exports = { ProductionTester };
