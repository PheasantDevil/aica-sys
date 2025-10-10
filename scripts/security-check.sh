#!/bin/bash

# Security Check Script for AICA-SyS
# Phase 8-5: Security Operations

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

# レポートディレクトリ
REPORT_DIR="security-reports"
mkdir -p "$REPORT_DIR"

# Python依存関係スキャン
check_python_dependencies() {
    log_info "Pythonパッケージの脆弱性をスキャン中..."
    
    cd backend
    
    if command -v safety &> /dev/null; then
        safety check --json > "../$REPORT_DIR/python-vulnerabilities.json" 2>&1 || true
        safety check || log_warning "Pythonパッケージに脆弱性が見つかりました"
    else
        log_warning "Safety がインストールされていません: pip install safety"
    fi
    
    cd ..
    log_success "Pythonスキャン完了"
}

# npm依存関係スキャン
check_npm_dependencies() {
    log_info "npmパッケージの脆弱性をスキャン中..."
    
    cd frontend
    npm audit --json > "../$REPORT_DIR/npm-vulnerabilities.json" 2>&1 || true
    npm audit || log_warning "npmパッケージに脆弱性が見つかりました"
    
    cd ..
    log_success "npmスキャン完了"
}

# コードセキュリティスキャン
check_code_security() {
    log_info "コードのセキュリティをスキャン中..."
    
    cd backend
    
    if command -v bandit &> /dev/null; then
        bandit -r . -f json -o "../$REPORT_DIR/bandit-report.json" 2>&1 || true
        bandit -r . -ll || log_warning "セキュリティ問題が見つかりました"
    else
        log_warning "Bandit がインストールされていません: pip install bandit"
    fi
    
    cd ..
    log_success "コードスキャン完了"
}

# 環境変数チェック
check_environment_variables() {
    log_info "環境変数とシークレットをチェック中..."
    
    # 機密情報がコミットされていないかチェック
    if grep -r "sk-" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" backend/ frontend/ 2>/dev/null; then
        log_error "コード内にAPIキーらしき文字列が見つかりました"
    else
        log_success "コード内にAPIキーは見つかりませんでした"
    fi
    
    # .envファイルがgit管理されていないか確認
    if git ls-files | grep -q "\.env$"; then
        log_error ".envファイルがgit管理されています"
    else
        log_success ".envファイルは適切に除外されています"
    fi
}

# ファイル権限チェック
check_file_permissions() {
    log_info "ファイル権限をチェック中..."
    
    # 実行権限が不要なファイルをチェック
    find . -type f -name "*.py" -executable -not -path "./venv/*" -not -path "./backend/venv/*" 2>/dev/null | while read file; do
        log_warning "実行権限が設定されています: $file"
    done
    
    log_success "権限チェック完了"
}

# SSL/TLS証明書チェック
check_ssl_certificates() {
    log_info "SSL/TLS証明書をチェック中..."
    
    # 本番環境のSSL証明書をチェック（実装時に追加）
    log_info "本番環境の証明書チェックは実装時に追加します"
}

# セキュリティヘッダーチェック
check_security_headers() {
    log_info "セキュリティヘッダーをチェック中..."
    
    # バックエンドが起動している場合のみチェック
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        log_info "セキュリティヘッダーを確認:"
        curl -I http://localhost:8000/ 2>/dev/null | grep -i "x-frame-options\|x-content-type-options\|strict-transport-security" || log_warning "一部のセキュリティヘッダーが見つかりません"
    else
        log_warning "バックエンドが起動していないため、ヘッダーチェックをスキップします"
    fi
}

# レポート生成
generate_report() {
    log_info "セキュリティレポートを生成中..."
    
    REPORT_FILE="$REPORT_DIR/security-report-$(date +%Y%m%d).md"
    
    cat > "$REPORT_FILE" <<EOF
# Security Scan Report

**Date**: $(date -Iseconds)
**Environment**: Development

## Summary

- Python Dependencies: Scanned
- npm Dependencies: Scanned
- Code Security: Scanned
- Environment Variables: Checked
- File Permissions: Checked

## Details

レポートの詳細は \`$REPORT_DIR\` ディレクトリ内のJSONファイルを参照してください。

## Recommendations

1. 定期的に依存関係を更新
2. セキュリティアップデートを優先的に適用
3. 環境変数とシークレットの管理を徹底
4. SSL/TLS証明書の有効期限を監視

EOF
    
    log_success "レポート生成完了: $REPORT_FILE"
}

# メイン処理
main() {
    log_info "セキュリティチェックを開始します"
    log_info "タイムスタンプ: $(date -Iseconds)"
    echo ""
    
    check_python_dependencies
    check_npm_dependencies
    check_code_security
    check_environment_variables
    check_file_permissions
    check_ssl_certificates
    check_security_headers
    generate_report
    
    echo ""
    log_success "セキュリティチェック完了"
    log_info "レポート: $REPORT_DIR/"
    ls -lh "$REPORT_DIR"/ | tail -n +2
}

# エラーハンドリング
trap 'log_error "セキュリティチェック失敗: line $LINENO"' ERR

# 実行
main
