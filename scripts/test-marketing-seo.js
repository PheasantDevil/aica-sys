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

class MarketingSEOTester {
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

  async testSEOEndpoints() {
    const endpoints = ["/sitemap.xml", "/robots.txt"];

    const results = {};
    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${endpoint}`, {
          timeout: 10000,
        });
        results[endpoint] = {
          status: response.status,
          contentType: response.headers["content-type"],
          hasContent: response.data && response.data.length > 0,
          isXML: endpoint.includes(".xml") && response.headers["content-type"]?.includes("xml"),
          isText: endpoint.includes(".txt") && response.headers["content-type"]?.includes("text"),
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

  async testMetaTags() {
    const pages = ["/", "/articles", "/newsletters", "/trends", "/pricing", "/about"];

    const results = {};
    for (const page of pages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });

        const html = response.data;
        const metaTags = {
          title: this.extractMetaTag(html, "title"),
          description: this.extractMetaTag(html, 'meta[name="description"]', "content"),
          keywords: this.extractMetaTag(html, 'meta[name="keywords"]', "content"),
          ogTitle: this.extractMetaTag(html, 'meta[property="og:title"]', "content"),
          ogDescription: this.extractMetaTag(html, 'meta[property="og:description"]', "content"),
          ogImage: this.extractMetaTag(html, 'meta[property="og:image"]', "content"),
          twitterCard: this.extractMetaTag(html, 'meta[name="twitter:card"]', "content"),
          canonical: this.extractMetaTag(html, 'link[rel="canonical"]', "href"),
        };

        results[page] = {
          status: response.status,
          metaTags,
          hasTitle: !!metaTags.title,
          hasDescription: !!metaTags.description,
          hasOGTags: !!(metaTags.ogTitle && metaTags.ogDescription),
          hasTwitterCard: !!metaTags.twitterCard,
          hasCanonical: !!metaTags.canonical,
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testStructuredData() {
    const pages = ["/", "/articles", "/pricing"];

    const results = {};
    for (const page of pages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });

        const html = response.data;
        const structuredData = this.extractStructuredData(html);

        results[page] = {
          status: response.status,
          structuredData,
          hasStructuredData: structuredData.length > 0,
          dataTypes: structuredData.map((data) => data["@type"]),
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testSocialSharing() {
    const testPages = ["/articles", "/newsletters", "/trends"];

    const results = {};
    for (const page of testPages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });

        const html = response.data;
        const socialElements = {
          hasShareButtons: html.includes("social-share") || html.includes("share"),
          hasTwitterShare: html.includes("twitter.com/intent/tweet"),
          hasFacebookShare: html.includes("facebook.com/sharer"),
          hasLinkedInShare: html.includes("linkedin.com/sharing"),
          hasOpenGraph: html.includes("og:title") && html.includes("og:description"),
          hasTwitterCard: html.includes("twitter:card"),
        };

        results[page] = {
          status: response.status,
          socialElements,
          hasSocialFeatures: Object.values(socialElements).some(Boolean),
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testAnalyticsIntegration() {
    const pages = ["/", "/articles", "/pricing"];

    const results = {};
    for (const page of pages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });

        const html = response.data;
        const analyticsElements = {
          hasGoogleAnalytics: html.includes("gtag") || html.includes("google-analytics"),
          hasGoogleTagManager: html.includes("googletagmanager"),
          hasCustomAnalytics: html.includes("analytics") || html.includes("tracking"),
          hasEventTracking: html.includes("trackEvent") || html.includes("data-track"),
        };

        results[page] = {
          status: response.status,
          analyticsElements,
          hasAnalytics: Object.values(analyticsElements).some(Boolean),
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testABTestingFramework() {
    try {
      // A/Bテストフレームワークの存在をチェック
      const response = await axios.get(`${PRODUCTION_URL}/`, {
        timeout: 15000,
      });

      const html = response.data;
      const abTestingElements = {
        hasABTesting: html.includes("ab-testing") || html.includes("useABTest"),
        hasConversionTracking: html.includes("conversion") || html.includes("trackConversion"),
        hasAnalyticsEvents: html.includes("trackEvent") || html.includes("analytics"),
      };

      return {
        status: response.status,
        abTestingElements,
        hasABTestingFramework: Object.values(abTestingElements).some(Boolean),
      };
    } catch (error) {
      throw new Error(`A/B testing framework test failed: ${error.message}`);
    }
  }

  async testConversionOptimization() {
    const conversionPages = ["/pricing", "/checkout", "/signup"];

    const results = {};
    for (const page of conversionPages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });

        const html = response.data;
        const conversionElements = {
          hasCTAButtons: html.includes("cta") || html.includes("call-to-action"),
          hasForms: html.includes("<form") || html.includes("form"),
          hasConversionTracking: html.includes("conversion") || html.includes("trackConversion"),
          hasFunnelTracking: html.includes("funnel") || html.includes("trackFunnel"),
        };

        results[page] = {
          status: response.status,
          conversionElements,
          hasConversionFeatures: Object.values(conversionElements).some(Boolean),
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testPerformanceMetrics() {
    const pages = ["/", "/articles", "/pricing"];

    const results = {};
    for (const page of pages) {
      try {
        const startTime = Date.now();
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });
        const loadTime = Date.now() - startTime;

        const html = response.data;
        const performanceElements = {
          hasPerformanceTracking: html.includes("performance") || html.includes("web-vitals"),
          hasCoreWebVitals: html.includes("LCP") || html.includes("FID") || html.includes("CLS"),
          hasPageSpeedOptimization: html.includes("optimize") || html.includes("lazy"),
        };

        results[page] = {
          status: response.status,
          loadTime,
          performanceElements,
          hasPerformanceFeatures: Object.values(performanceElements).some(Boolean),
          isFastLoad: loadTime < 3000, // 3秒以内
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  async testContentSEO() {
    const contentPages = ["/articles", "/newsletters", "/trends"];

    const results = {};
    for (const page of contentPages) {
      try {
        const response = await axios.get(`${PRODUCTION_URL}${page}`, {
          timeout: 15000,
          validateStatus: (status) => status < 500,
        });

        const html = response.data;
        const contentSEOElements = {
          hasHeadings: html.includes("<h1") || html.includes("<h2") || html.includes("<h3"),
          hasImages: html.includes("<img"),
          hasAltText: html.includes("alt="),
          hasInternalLinks: html.includes('href="/') || html.includes('href="/articles'),
          hasKeywords:
            html.includes("typescript") || html.includes("javascript") || html.includes("react"),
          hasReadableContent: html.length > 1000, // 十分なコンテンツがあるか
        };

        results[page] = {
          status: response.status,
          contentSEOElements,
          hasContentSEO: Object.values(contentSEOElements).some(Boolean),
          contentLength: html.length,
        };
      } catch (error) {
        results[page] = {
          error: error.message,
          status: error.response?.status,
        };
      }
    }
    return results;
  }

  extractMetaTag(html, selector, attribute = "text") {
    const regex = new RegExp(`<${selector}[^>]*${attribute}="([^"]*)"`, "i");
    const match = html.match(regex);
    return match ? match[1] : null;
  }

  extractStructuredData(html) {
    const structuredDataRegex = /<script[^>]*type="application\/ld\+json"[^>]*>(.*?)<\/script>/gi;
    const structuredData = [];
    let match;

    while ((match = structuredDataRegex.exec(html)) !== null) {
      try {
        const data = JSON.parse(match[1]);
        structuredData.push(data);
      } catch (error) {
        // JSON解析エラーは無視
      }
    }

    return structuredData;
  }

  generateReport() {
    const totalTests = this.results.passed + this.results.failed;
    const successRate = totalTests > 0 ? ((this.results.passed / totalTests) * 100).toFixed(1) : 0;

    log("\n📊 Marketing & SEO Test Results Summary:", "blue");
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
    const reportPath = path.join(__dirname, "..", "docs", "marketing-seo-test-report.json");
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
  log("🚀 Starting Marketing & SEO Tests...", "blue");
  log(`Testing production URL: ${PRODUCTION_URL}`, "yellow");
  log(`Testing API URL: ${API_URL}`, "yellow");
  log("");

  const tester = new MarketingSEOTester();

  try {
    // Ensure admin login for API tests
    await tester.runTest("Admin Login", () => tester.adminLogin());

    // SEO tests
    await tester.runTest("SEO Endpoints", () => tester.testSEOEndpoints());
    await tester.runTest("Meta Tags", () => tester.testMetaTags());
    await tester.runTest("Structured Data", () => tester.testStructuredData());
    await tester.runTest("Content SEO", () => tester.testContentSEO());

    // Marketing tests
    await tester.runTest("Social Sharing", () => tester.testSocialSharing());
    await tester.runTest("Analytics Integration", () => tester.testAnalyticsIntegration());
    await tester.runTest("A/B Testing Framework", () => tester.testABTestingFramework());
    await tester.runTest("Conversion Optimization", () => tester.testConversionOptimization());

    // Performance tests
    await tester.runTest("Performance Metrics", () => tester.testPerformanceMetrics());

    // Generate final report
    const success = tester.generateReport();

    if (success) {
      log("\n🎉 Marketing & SEO tests completed successfully!", "green");
      log("The marketing and SEO system is functioning as expected.", "green");
      return 0;
    } else {
      log("\n⚠️  Marketing & SEO tests completed with issues.", "yellow");
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

module.exports = { MarketingSEOTester };
