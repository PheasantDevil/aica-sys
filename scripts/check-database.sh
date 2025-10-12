#!/bin/bash

# Database Connection Check Script
# Checks if database is accessible and not paused

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "Checking database connection..."

# Pythonで接続チェック
cd backend

python3 << 'EOF'
import os
import sys

try:
    from database import engine
    
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./aica_sys.db')
    
    print(f"Database URL: {db_url[:30]}...")  # 最初の30文字のみ表示
    
    if 'sqlite' in db_url:
        print("✅ Using SQLite (local mode)")
        sys.exit(0)
    
    # PostgreSQL/Supabase接続テスト
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Database connection OK")
        sys.exit(0)
        
except Exception as e:
    error_msg = str(e).lower()
    print(f"❌ Database connection failed: {e}")
    
    if 'paused' in error_msg or 'suspended' in error_msg:
        print("")
        print("⚠️  Your Supabase project appears to be PAUSED.")
        print("")
        print("To fix this:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your AICA-SyS-DB project")
        print("3. Click 'Unpause Project'")
        print("")
        print("Alternative: Switch to Vercel Postgres or Neon for auto-resume")
    elif 'does not exist' in error_msg:
        print("")
        print("⚠️  Database or role does not exist.")
        print("Please check your DATABASE_URL configuration.")
    elif 'connection' in error_msg or 'timeout' in error_msg:
        print("")
        print("⚠️  Cannot connect to database server.")
        print("Check network settings or database status.")
    
    sys.exit(1)
EOF

exit_code=$?

if [ $exit_code -eq 0 ]; then
    log_success "Database check passed"
else
    log_error "Database check failed"
    exit 1
fi

