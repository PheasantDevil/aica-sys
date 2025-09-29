#!/usr/bin/env node

/**
 * Google OAuth Production Setup Script
 * This script helps set up Google OAuth for production deployment
 */

const fs = require('fs');
const path = require('path');

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

function generateGoogleOAuthSetupGuide() {
  log('🚀 Google OAuth Production Setup Guide', 'blue');
  log('', 'reset');
  
  log('📋 Step 1: Google Cloud Console Setup', 'yellow');
  log('1. Go to Google Cloud Console: https://console.cloud.google.com/', 'reset');
  log('2. Create a new project or select existing project', 'reset');
  log('3. Enable Google+ API and Google OAuth2 API', 'reset');
  log('', 'reset');
  
  log('📋 Step 2: OAuth Consent Screen Configuration', 'yellow');
  log('1. Go to APIs & Services > OAuth consent screen', 'reset');
  log('2. Choose "External" user type', 'reset');
  log('3. Fill in the required information:', 'reset');
  log('   - App name: AICA-SyS', 'reset');
  log('   - User support email: your-email@domain.com', 'reset');
  log('   - Developer contact information: your-email@domain.com', 'reset');
  log('4. Add scopes:', 'reset');
  log('   - ../auth/userinfo.email', 'reset');
  log('   - ../auth/userinfo.profile', 'reset');
  log('   - openid', 'reset');
  log('5. Add test users (for testing phase)', 'reset');
  log('', 'reset');
  
  log('📋 Step 3: OAuth Client ID Creation', 'yellow');
  log('1. Go to APIs & Services > Credentials', 'reset');
  log('2. Click "Create Credentials" > "OAuth client ID"', 'reset');
  log('3. Choose "Web application"', 'reset');
  log('4. Set authorized JavaScript origins:', 'reset');
  log('   - https://aica-sys.vercel.app', 'reset');
  log('   - https://www.aica-sys.vercel.app', 'reset');
  log('5. Set authorized redirect URIs:', 'reset');
  log('   - https://aica-sys.vercel.app/api/auth/callback/google', 'reset');
  log('   - https://www.aica-sys.vercel.app/api/auth/callback/google', 'reset');
  log('6. Copy the Client ID and Client Secret', 'reset');
  log('', 'reset');
  
  log('📋 Step 4: Environment Variables Setup', 'yellow');
  log('Add the following environment variables to your production environment:', 'reset');
  log('', 'reset');
  log('GOOGLE_CLIENT_ID=your-google-client-id', 'green');
  log('GOOGLE_CLIENT_SECRET=your-google-client-secret', 'green');
  log('NEXTAUTH_URL=https://aica-sys.vercel.app', 'green');
  log('NEXTAUTH_SECRET=your-nextauth-secret', 'green');
  log('', 'reset');
  
  log('📋 Step 5: Domain Verification (Optional)', 'yellow');
  log('1. Go to Google Search Console', 'reset');
  log('2. Add your domain: aica-sys.vercel.app', 'reset');
  log('3. Verify domain ownership', 'reset');
  log('4. This helps with OAuth consent screen approval', 'reset');
  log('', 'reset');
  
  log('📋 Step 6: Production Testing', 'yellow');
  log('1. Test OAuth flow in production', 'reset');
  log('2. Verify user data is correctly retrieved', 'reset');
  log('3. Test sign-in and sign-out functionality', 'reset');
  log('4. Check session management', 'reset');
  log('', 'reset');
  
  log('⚠️  Important Security Notes:', 'red');
  log('- Never commit OAuth credentials to version control', 'red');
  log('- Use environment variables for all sensitive data', 'red');
  log('- Regularly rotate OAuth credentials', 'red');
  log('- Monitor OAuth usage in Google Cloud Console', 'red');
  log('', 'reset');
}

function createOAuthTestScript() {
  const testScript = `#!/usr/bin/env node

/**
 * Google OAuth Test Script
 * Tests OAuth configuration and endpoints
 */

const axios = require('axios');

const PRODUCTION_URL = 'https://aica-sys.vercel.app';

async function testOAuthEndpoints() {
  console.log('🧪 Testing Google OAuth endpoints...');
  
  try {
    // Test OAuth configuration endpoint
    const configResponse = await axios.get(\`\${PRODUCTION_URL}/api/auth/providers\`);
    console.log('✅ OAuth providers configured:', Object.keys(configResponse.data));
    
    // Test sign-in page
    const signInResponse = await axios.get(\`\${PRODUCTION_URL}/auth/signin\`);
    console.log('✅ Sign-in page accessible:', signInResponse.status === 200);
    
    // Test sign-out page
    const signOutResponse = await axios.get(\`\${PRODUCTION_URL}/auth/signout\`);
    console.log('✅ Sign-out page accessible:', signOutResponse.status === 200);
    
    console.log('🎉 OAuth endpoints test completed successfully!');
    
  } catch (error) {
    console.error('❌ OAuth test failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  testOAuthEndpoints();
}

module.exports = { testOAuthEndpoints };
`;

  const testScriptPath = path.join(__dirname, 'test-google-oauth.js');
  fs.writeFileSync(testScriptPath, testScript);
  log(`✅ OAuth test script created: ${testScriptPath}`, 'green');
}

function createEnvironmentTemplate() {
  const envTemplate = `# Google OAuth Production Environment Variables
# Copy these to your production environment

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# NextAuth Configuration
NEXTAUTH_URL=https://aica-sys.vercel.app
NEXTAUTH_SECRET=your-nextauth-secret-here

# Optional: Custom OAuth Scopes
GOOGLE_OAUTH_SCOPES=openid,email,profile

# Optional: OAuth Consent Screen Configuration
GOOGLE_OAUTH_APP_NAME=AICA-SyS
GOOGLE_OAUTH_APP_DOMAIN=aica-sys.vercel.app
`;

  const envPath = path.join(__dirname, '..', '.env.google-oauth.example');
  fs.writeFileSync(envPath, envTemplate);
  log(`✅ Google OAuth environment template created: ${envPath}`, 'green');
}

function main() {
  log('🎯 Starting Google OAuth Production Setup...', 'blue');
  log('', 'reset');
  
  generateGoogleOAuthSetupGuide();
  createOAuthTestScript();
  createEnvironmentTemplate();
  
  log('🎉 Google OAuth production setup guide completed!', 'green');
  log('', 'reset');
  log('📋 Next steps:', 'yellow');
  log('1. Follow the setup guide above', 'yellow');
  log('2. Configure Google Cloud Console', 'yellow');
  log('3. Set up environment variables', 'yellow');
  log('4. Test OAuth flow: node scripts/test-google-oauth.js', 'yellow');
  log('5. Deploy to production', 'yellow');
  log('', 'reset');
}

// Run the setup
if (require.main === module) {
  main();
}

module.exports = {
  generateGoogleOAuthSetupGuide,
  createOAuthTestScript,
  createEnvironmentTemplate,
};
