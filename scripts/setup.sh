#!/bin/bash

# AICA-SyS Setup Script
# AI-driven Content Curation & Automated Sales System

set -e

echo "🚀 Setting up AICA-SyS development environment..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ All requirements are satisfied."
}

# Setup frontend
setup_frontend() {
    echo "🎨 Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    else
        echo "✅ Frontend dependencies already installed."
    fi
    
    cd ..
}

# Setup backend
setup_backend() {
    echo "🐍 Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    echo "📦 Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ..
}

# Setup environment files
setup_env() {
    echo "🔧 Setting up environment files..."
    
    # Frontend .env.local
    if [ ! -f "frontend/.env.local" ]; then
        cat > frontend/.env.local << EOF
# Next.js Environment Variables
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_API_URL=http://localhost:8000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Stripe (optional)
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
EOF
        echo "✅ Created frontend/.env.local"
    fi
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql://aica_user:aica_password@localhost:5432/aica_sys
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333

# AI Services
GOOGLE_AI_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key

# Environment
ENVIRONMENT=development
DEBUG=True

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
EOF
        echo "✅ Created backend/.env"
    fi
}

# Start development services
start_services() {
    echo "🐳 Starting development services..."
    
    # Start databases
    docker-compose up -d postgres redis qdrant
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "✅ Development services are running!"
    echo "📊 Services status:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - Qdrant: localhost:6333"
}

# Main setup function
main() {
    echo "🎯 AICA-SyS Development Environment Setup"
    echo "========================================"
    
    check_requirements
    setup_frontend
    setup_backend
    setup_env
    start_services
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "  1. Update environment variables in frontend/.env.local and backend/.env"
    echo "  2. Start the backend: cd backend && source venv/bin/activate && python main.py"
    echo "  3. Start the frontend: cd frontend && npm run dev"
    echo "  4. Visit http://localhost:3000 to see the application"
    echo ""
    echo "🔧 Useful commands:"
    echo "  - Start all services: docker-compose up -d"
    echo "  - Stop all services: docker-compose down"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Reset databases: docker-compose down -v && docker-compose up -d"
}

# Run main function
main "$@"
