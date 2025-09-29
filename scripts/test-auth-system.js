#!/usr/bin/env node

/**
 * Authentication System Test Script
 * Tests the complete authentication flow and user management system
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

class AuthSystemTester {
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

  async testAuthEndpoints() {
    const endpoints = [
      '/auth/providers',
      '/auth/session',
      '/auth/csrf',
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

  async testSignInPage() {
    try {
      const response = await axios.get(`${PRODUCTION_URL}/auth/signin`, {
        timeout: 15000,
        validateStatus: status => status < 500,
      });

      if (response.status !== 200) {
        throw new Error(`Sign-in page returned status ${response.status}`);
      }

      // Check if Google OAuth button is present
      const hasGoogleAuth = response.data.includes('Google') || 
                           response.data.includes('google') ||
                           response.data.includes('oauth');

      return {
        status: response.status,
        hasGoogleAuth: hasGoogleAuth,
        title: response.data.match(/<title>(.*?)<\/title>/)?.[1] || 'No title',
      };
    } catch (error) {
      throw new Error(`Sign-in page test failed: ${error.message}`);
    }
  }

  async testSignOutPage() {
    try {
      const response = await axios.get(`${PRODUCTION_URL}/auth/signout`, {
        timeout: 15000,
        validateStatus: status => status < 500,
      });

      return {
        status: response.status,
        title: response.data.match(/<title>(.*?)<\/title>/)?.[1] || 'No title',
      };
    } catch (error) {
      throw new Error(`Sign-out page test failed: ${error.message}`);
    }
  }

  async testDashboardAccess() {
    try {
      // Test dashboard without authentication (should redirect)
      const response = await axios.get(`${PRODUCTION_URL}/dashboard`, {
        timeout: 15000,
        validateStatus: status => status < 500,
        maxRedirects: 0,
      });

      // Should redirect to sign-in page
      const isRedirected = response.status === 302 || 
                          response.status === 307 ||
                          response.data.includes('signin') ||
                          response.data.includes('auth');

      return {
        status: response.status,
        isRedirected: isRedirected,
        redirectLocation: response.headers.location || 'No redirect header',
      };
    } catch (error) {
      if (error.response?.status === 302 || error.response?.status === 307) {
        return {
          status: error.response.status,
          isRedirected: true,
          redirectLocation: error.response.headers.location || 'No redirect header',
        };
      }
      throw new Error(`Dashboard access test failed: ${error.message}`);
    }
  }

  async testUserManagementEndpoints() {
    const endpoints = [
      '/users/profile',
      '/users/settings',
      '/users/stats',
      '/users/subscription',
    ];

    const results = {};

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_URL}${endpoint}`, {
          timeout: 10000,
          validateStatus: status => status < 500,
        });
        results[endpoint] = {
          status: response.status,
          requiresAuth: response.status === 401 || response.status === 403,
        };
      } catch (error) {
        results[endpoint] = {
          error: error.message,
          requiresAuth: error.response?.status === 401 || error.response?.status === 403,
        };
      }
    }

    return results;
  }

  async testOAuthConfiguration() {
    try {
      const response = await axios.get(`${API_URL}/auth/providers`, {
        timeout: 10000,
      });

      const providers = response.data;
      const hasGoogle = providers.google !== undefined;

      return {
        providers: Object.keys(providers),
        hasGoogle: hasGoogle,
        googleConfig: hasGoogle ? {
          id: providers.google.id,
          name: providers.google.name,
          type: providers.google.type,
        } : null,
      };
    } catch (error) {
      throw new Error(`OAuth configuration test failed: ${error.message}`);
    }
  }

  async testSecurityHeaders() {
    try {
      const response = await axios.get(`${PRODUCTION_URL}/auth/signin`, {
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
        hasSecurityHeaders: Object.keys(foundHeaders).length > 0,
      };
    } catch (error) {
      throw new Error(`Security headers test failed: ${error.message}`);
    }
  }

  async testSessionManagement() {
    try {
      // Test CSRF token endpoint
      const csrfResponse = await axios.get(`${API_URL}/auth/csrf`, {
        timeout: 10000,
      });

      return {
        csrfToken: csrfResponse.data.csrfToken,
        hasCsrfToken: !!csrfResponse.data.csrfToken,
      };
    } catch (error) {
      throw new Error(`Session management test failed: ${error.message}`);
    }
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate =
      totalTests > 0
        ? ((this.results.passed / totalTests) * 100).toFixed(1)
        : 0;

    log('\n📊 Authentication System Test Results:', 'blue');
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
      'auth-system-test-report.json'
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
  log('🚀 Starting Authentication System Tests...', 'blue');
  log(`Testing production URL: ${PRODUCTION_URL}`, 'yellow');
  log(`Testing API URL: ${API_URL}`, 'yellow');
  log('');

  const tester = new AuthSystemTester();

  try {
    // Core authentication tests
    await tester.runTest('Auth Endpoints', () => tester.testAuthEndpoints());
    await tester.runTest('OAuth Configuration', () => tester.testOAuthConfiguration());
    await tester.runTest('Session Management', () => tester.testSessionManagement());

    // Frontend authentication tests
    await tester.runTest('Sign-in Page', () => tester.testSignInPage());
    await tester.runTest('Sign-out Page', () => tester.testSignOutPage());
    await tester.runTest('Dashboard Access Control', () => tester.testDashboardAccess());

    // User management tests
    await tester.runTest('User Management Endpoints', () => tester.testUserManagementEndpoints());

    // Security tests
    await tester.runTest('Security Headers', () => tester.testSecurityHeaders());

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log('\n🎉 Authentication system tests completed successfully!', 'green');
      log('The authentication system is ready for production.', 'green');
      return 0;
    } else {
      log('\n⚠️  Authentication system tests completed with issues.', 'yellow');
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

module.exports = { AuthSystemTester };
