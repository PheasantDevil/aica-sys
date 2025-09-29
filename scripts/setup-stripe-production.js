#!/usr/bin/env node

/**
 * Stripe Production Setup Script
 * This script helps set up Stripe products, prices, and webhooks for production
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

async function setupStripeProducts() {
    log('🚀 Setting up Stripe products and prices for production...', 'blue');
    
    try {
        // Check if Stripe secret key is set
        if (!process.env.STRIPE_SECRET_KEY) {
            log('❌ STRIPE_SECRET_KEY environment variable not set', 'red');
            log('Please set your Stripe secret key:', 'yellow');
            log('export STRIPE_SECRET_KEY=sk_live_your_secret_key', 'yellow');
            return false;
        }
        
        // Create Basic Subscription Product
        const basicProduct = await stripe.products.create({
            name: 'AICA-SyS Basic Subscription',
            description: 'Monthly subscription for TypeScript ecosystem insights and curated content',
            metadata: {
                type: 'subscription',
                tier: 'basic'
            }
        });
        
        const basicPrice = await stripe.prices.create({
            product: basicProduct.id,
            unit_amount: 1980, // ¥19.80 (¥1,980)
            currency: 'jpy',
            recurring: {
                interval: 'month'
            },
            metadata: {
                tier: 'basic',
                features: 'basic_articles,newsletter,trend_analysis'
            }
        });
        
        log(`✅ Basic subscription product created: ${basicProduct.id}`, 'green');
        log(`✅ Basic subscription price created: ${basicPrice.id}`, 'green');
        
        // Create Premium Subscription Product
        const premiumProduct = await stripe.products.create({
            name: 'AICA-SyS Premium Subscription',
            description: 'Premium monthly subscription with advanced features and custom reports',
            metadata: {
                type: 'subscription',
                tier: 'premium'
            }
        });
        
        const premiumPrice = await stripe.prices.create({
            product: premiumProduct.id,
            unit_amount: 4980, // ¥49.80 (¥4,980)
            currency: 'jpy',
            recurring: {
                interval: 'month'
            },
            metadata: {
                tier: 'premium',
                features: 'premium_articles,newsletter,trend_analysis,custom_reports'
            }
        });
        
        log(`✅ Premium subscription product created: ${premiumProduct.id}`, 'green');
        log(`✅ Premium subscription price created: ${premiumPrice.id}`, 'green');
        
        // Create Premium Report Product (one-time purchase)
        const reportProduct = await stripe.products.create({
            name: 'AICA-SyS Premium Report',
            description: 'In-depth analysis report on TypeScript ecosystem trends and insights',
            metadata: {
                type: 'one_time',
                category: 'report'
            }
        });
        
        const reportPrice = await stripe.prices.create({
            product: reportProduct.id,
            unit_amount: 4980, // ¥49.80 (¥4,980)
            currency: 'jpy',
            metadata: {
                type: 'report',
                category: 'premium_analysis'
            }
        });
        
        log(`✅ Premium report product created: ${reportProduct.id}`, 'green');
        log(`✅ Premium report price created: ${reportPrice.id}`, 'green');
        
        // Save product IDs to configuration file
        const config = {
            products: {
                basic_subscription: {
                    product_id: basicProduct.id,
                    price_id: basicPrice.id,
                    amount: 1980,
                    currency: 'jpy',
                    interval: 'month'
                },
                premium_subscription: {
                    product_id: premiumProduct.id,
                    price_id: premiumPrice.id,
                    amount: 4980,
                    currency: 'jpy',
                    interval: 'month'
                },
                premium_report: {
                    product_id: reportProduct.id,
                    price_id: reportPrice.id,
                    amount: 4980,
                    currency: 'jpy',
                    type: 'one_time'
                }
            },
            created_at: new Date().toISOString()
        };
        
        const configPath = path.join(__dirname, '..', 'config', 'stripe-production.json');
        fs.mkdirSync(path.dirname(configPath), { recursive: true });
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        
        log(`✅ Stripe configuration saved to: ${configPath}`, 'green');
        
        return true;
        
    } catch (error) {
        log(`❌ Failed to set up Stripe products: ${error.message}`, 'red');
        return false;
    }
}

async function setupWebhooks() {
    log('🔗 Setting up Stripe webhooks...', 'blue');
    
    try {
        // Create webhook endpoint
        const webhook = await stripe.webhookEndpoints.create({
            url: 'https://aica-sys.vercel.app/api/webhooks/stripe',
            enabled_events: [
                'customer.subscription.created',
                'customer.subscription.updated',
                'customer.subscription.deleted',
                'invoice.payment_succeeded',
                'invoice.payment_failed',
                'payment_intent.succeeded',
                'payment_intent.payment_failed',
                'checkout.session.completed'
            ],
            metadata: {
                environment: 'production',
                application: 'aica-sys'
            }
        });
        
        log(`✅ Webhook endpoint created: ${webhook.id}`, 'green');
        log(`✅ Webhook URL: ${webhook.url}`, 'green');
        log(`✅ Webhook secret: ${webhook.secret}`, 'yellow');
        
        log('📝 Add this webhook secret to your environment variables:', 'yellow');
        log(`STRIPE_WEBHOOK_SECRET=${webhook.secret}`, 'yellow');
        
        return webhook.secret;
        
    } catch (error) {
        log(`❌ Failed to set up webhook: ${error.message}`, 'red');
        return null;
    }
}

async function setupTaxSettings() {
    log('💰 Setting up tax settings for Japan...', 'blue');
    
    try {
        // Note: Tax settings need to be configured in Stripe Dashboard
        // This is just informational
        log('📋 Tax settings to configure in Stripe Dashboard:', 'yellow');
        log('1. Go to Settings > Tax settings', 'yellow');
        log('2. Enable automatic tax calculation', 'yellow');
        log('3. Add Japan as a tax region', 'yellow');
        log('4. Set up tax rates for Japan (10% consumption tax)', 'yellow');
        log('5. Configure tax behavior for subscriptions', 'yellow');
        
        return true;
        
    } catch (error) {
        log(`❌ Failed to set up tax settings: ${error.message}`, 'red');
        return false;
    }
}

async function main() {
    log('🎯 Starting Stripe Production Setup...', 'blue');
    
    try {
        // Set up products and prices
        const productsSetup = await setupStripeProducts();
        if (!productsSetup) {
            log('❌ Product setup failed', 'red');
            return 1;
        }
        
        // Set up webhooks
        const webhookSecret = await setupWebhooks();
        if (!webhookSecret) {
            log('❌ Webhook setup failed', 'red');
            return 1;
        }
        
        // Set up tax settings (informational)
        await setupTaxSettings();
        
        log('🎉 Stripe production setup completed successfully!', 'green');
        log('', 'reset');
        log('📋 Next steps:', 'yellow');
        log('1. Update your environment variables with the webhook secret', 'yellow');
        log('2. Configure tax settings in Stripe Dashboard', 'yellow');
        log('3. Test the webhook endpoints', 'yellow');
        log('4. Set up customer portal settings', 'yellow');
        
        return 0;
        
    } catch (error) {
        log(`❌ Setup failed: ${error.message}`, 'red');
        return 1;
    }
}

// Run the setup
if (require.main === module) {
    main().then(exitCode => {
        process.exit(exitCode);
    });
}

module.exports = {
    setupStripeProducts,
    setupWebhooks,
    setupTaxSettings
};
