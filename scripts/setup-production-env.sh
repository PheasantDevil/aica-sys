#!/bin/bash

# Production Environment Setup Script for AICA-SyS
# This script helps set up production environment variables

set -e

echo "🚀 Setting up AICA-SyS Production Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local is_secret="${3:-false}"
    
    if [ "$is_secret" = "true" ]; then
        read -s -p "$prompt: " input
        echo
    else
        read -p "$prompt: " input
    fi
    
    echo "$input"
}

# Function to generate random secret
generate_secret() {
    openssl rand -base64 32
}

echo -e "${YELLOW}📋 Production Environment Setup${NC}"
echo "This script will help you configure production environment variables."
echo ""

# Check if .env.production already exists
if [ -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️  .env.production already exists. Do you want to overwrite it? (y/N)${NC}"
    read -p "> " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo -e "${GREEN}🔧 Generating production environment file...${NC}"

# Generate secrets
SECRET_KEY=$(generate_secret)
JWT_SECRET_KEY=$(generate_secret)
NEXTAUTH_SECRET=$(generate_secret)
CSRF_SECRET=$(generate_secret)

# Create .env.production file
cat > .env.production << EOF
# Production Environment Variables for AICA-SyS
# Generated on $(date)

# Supabase Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@[YOUR_PROJECT_REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR_PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
SUPABASE_SERVICE_KEY=[YOUR_SERVICE_KEY]

# Application Configuration
ENVIRONMENT=production
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
CORS_ORIGINS=https://aica-sys.vercel.app,https://www.aica-sys.vercel.app

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://aica-sys-backend.vercel.app
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR_PROJECT_REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
NEXTAUTH_URL=https://aica-sys.vercel.app
NEXTAUTH_SECRET=$NEXTAUTH_SECRET

# OAuth Configuration
GOOGLE_CLIENT_ID=[YOUR_GOOGLE_CLIENT_ID]
GOOGLE_CLIENT_SECRET=[YOUR_GOOGLE_CLIENT_SECRET]

# Payment Configuration (Stripe Live Keys)
STRIPE_PUBLISHABLE_KEY=pk_live_[YOUR_STRIPE_PUBLISHABLE_KEY]
STRIPE_SECRET_KEY=sk_live_[YOUR_STRIPE_SECRET_KEY]
STRIPE_WEBHOOK_SECRET=whsec_[YOUR_STRIPE_WEBHOOK_SECRET]

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=[YOUR_EMAIL]
SMTP_PASSWORD=[YOUR_APP_PASSWORD]
SMTP_FROM=noreply@aica-sys.com

# Security Configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
CSRF_SECRET=$CSRF_SECRET

# Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json

# Performance Configuration
WORKERS=4
MAX_CONNECTIONS=1000
TIMEOUT=30

# AI Configuration
GOOGLE_AI_API_KEY=[YOUR_GOOGLE_AI_API_KEY]

# Monitoring Configuration
PROMETHEUS_RETENTION_TIME=200h
GRAFANA_PASSWORD=[YOUR_GRAFANA_PASSWORD]
EOF

echo -e "${GREEN}✅ .env.production file created successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Update the placeholder values in .env.production with your actual production values"
echo "2. Set up your Supabase project and update the database configuration"
echo "3. Configure your Stripe account with live keys"
echo "4. Set up Google OAuth credentials"
echo "5. Configure your email settings"
echo ""
echo -e "${YELLOW}🔒 Security Note:${NC}"
echo "The following secrets have been automatically generated:"
echo "- SECRET_KEY"
echo "- JWT_SECRET_KEY"
echo "- NEXTAUTH_SECRET"
echo "- CSRF_SECRET"
echo ""
echo -e "${RED}⚠️  Important: Never commit .env.production to version control!${NC}"
echo ""

# Create Vercel environment setup script
cat > scripts/setup-vercel-env.sh << 'EOF'
#!/bin/bash

# Vercel Environment Variables Setup Script
# This script helps set up environment variables in Vercel

echo "🚀 Setting up Vercel environment variables..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Please install it first:"
    echo "npm i -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "❌ Please log in to Vercel first:"
    echo "vercel login"
    exit 1
fi

echo "📋 Setting up environment variables in Vercel..."

# Read .env.production and set variables in Vercel
if [ -f ".env.production" ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^[[:space:]]*# ]] && [[ -n "$key" ]]; then
            # Remove leading/trailing whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            if [[ -n "$value" ]] && [[ "$value" != "[YOUR_"* ]]; then
                echo "Setting $key..."
                vercel env add "$key" production <<< "$value"
            fi
        fi
    done < .env.production
else
    echo "❌ .env.production file not found. Please run setup-production-env.sh first."
    exit 1
fi

echo "✅ Vercel environment variables set up successfully!"
EOF

chmod +x scripts/setup-vercel-env.sh

echo -e "${GREEN}✅ Production environment setup completed!${NC}"
echo ""
echo -e "${YELLOW}📋 To complete the setup:${NC}"
echo "1. Update .env.production with your actual values"
echo "2. Run: ./scripts/setup-vercel-env.sh (to set up Vercel environment variables)"
echo "3. Set up your Supabase project"
echo "4. Configure Stripe with live keys"
echo ""
