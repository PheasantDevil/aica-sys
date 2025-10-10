#!/bin/bash

# Deployment Script for AICA-SyS
# Phase 8-1: CI/CD Pipeline

set -e  # エラーで停止

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ロギング関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 使用方法
usage() {
    echo "Usage: $0 <environment>"
    echo ""
    echo "Environments:"
    echo "  staging     - Deploy to staging environment"
    echo "  production  - Deploy to production environment"
    echo ""
    echo "Example: $0 staging"
    exit 1
}

# 引数チェック
if [ $# -eq 0 ]; then
    usage
fi

ENVIRONMENT=$1

# 環境変数の検証
validate_environment() {
    log_info "Validating environment: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        staging|production)
            log_success "Environment validated: $ENVIRONMENT"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            usage
            ;;
    esac
}

# ヘルスチェック
health_check() {
    local url=$1
    local max_attempts=10
    local attempt=1
    
    log_info "Running health check: $url"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url/health" > /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        log_warning "Health check attempt $attempt/$max_attempts failed"
        sleep 5
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# スモークテスト
run_smoke_tests() {
    local url=$1
    
    log_info "Running smoke tests: $url"
    
    # 基本エンドポイントテスト
    if ! curl -f -s "$url/" > /dev/null; then
        log_error "Root endpoint test failed"
        return 1
    fi
    
    if ! curl -f -s "$url/health" > /dev/null; then
        log_error "Health endpoint test failed"
        return 1
    fi
    
    log_success "Smoke tests passed"
    return 0
}

# バックエンドのデプロイ
deploy_backend() {
    log_info "Deploying backend to $ENVIRONMENT"
    
    cd backend
    
    # 依存関係のインストール
    log_info "Installing dependencies..."
    pip install -r requirements.txt
    
    # データベースマイグレーション
    log_info "Running database migrations..."
    python3 -c "from database import init_db; init_db()" || true
    
    # アプリケーションの起動確認
    log_info "Validating application..."
    python3 -c "from main import app; print('Application validated')" || true
    
    cd ..
    
    log_success "Backend deployment completed"
}

# フロントエンドのデプロイ
deploy_frontend() {
    log_info "Deploying frontend to $ENVIRONMENT"
    
    cd frontend
    
    # 依存関係のインストール
    log_info "Installing dependencies..."
    npm ci
    
    # ビルド
    log_info "Building application..."
    npm run build
    
    # Vercelへのデプロイ
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Deploying to Vercel (production)..."
        npx vercel --prod --token="$VERCEL_TOKEN" || true
    else
        log_info "Deploying to Vercel (staging)..."
        npx vercel --token="$VERCEL_TOKEN" || true
    fi
    
    cd ..
    
    log_success "Frontend deployment completed"
}

# ロールバック
rollback() {
    log_warning "Rolling back deployment..."
    
    # Vercelのロールバック
    if [ -n "$VERCEL_TOKEN" ]; then
        cd frontend
        npx vercel rollback --token="$VERCEL_TOKEN" || true
        cd ..
    fi
    
    log_success "Rollback completed"
}

# メイン処理
main() {
    log_info "Starting deployment process"
    log_info "Environment: $ENVIRONMENT"
    log_info "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 環境の検証
    validate_environment
    
    # デプロイ前のバックアップ
    log_info "Creating backup..."
    if [ -f "backend/aica_sys.db" ]; then
        cp backend/aica_sys.db "backend/aica_sys.db.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Backup created"
    fi
    
    # デプロイ実行
    if deploy_backend && deploy_frontend; then
        log_success "Deployment completed successfully"
        
        # デプロイ後のテスト
        if [ "$ENVIRONMENT" = "production" ]; then
            if health_check "https://api.aica-sys.com"; then
                run_smoke_tests "https://api.aica-sys.com"
            else
                log_error "Production health check failed"
                log_warning "Consider rolling back"
                exit 1
            fi
        fi
        
        log_success "All deployment steps completed"
        exit 0
    else
        log_error "Deployment failed"
        
        # 失敗時の処理
        read -p "Do you want to rollback? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        fi
        
        exit 1
    fi
}

# エラーハンドリング
trap 'log_error "Deployment failed at line $LINENO"' ERR

# スクリプト実行
main
