#!/bin/bash

# Restore Script for AICA-SyS
# Phase 8-4: Backup and Recovery

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 設定
BACKUP_DIR="./backups"
DB_FILE="backend/aica_sys.db"
RESTORE_TEMP_DIR="./restore_temp"

# 使用方法
usage() {
    echo "Usage: $0 [backup_file]"
    echo ""
    echo "バックアップファイルを指定しない場合、最新のバックアップを使用します"
    echo ""
    echo "利用可能なバックアップ:"
    ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 | nl
    echo ""
    exit 1
}

# バックアップ一覧表示
list_backups() {
    log_info "利用可能なバックアップ:"
    ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -10 | awk '{print "  " $9 " - " $5 " (" $6 " " $7 " " $8 ")"}'
}

# バックアップファイルの選択
select_backup() {
    if [ -n "$1" ]; then
        BACKUP_FILE="$1"
    else
        # 最新のバックアップを選択
        BACKUP_FILE=$(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -1)
    fi
    
    if [ -z "$BACKUP_FILE" ]; then
        log_error "バックアップファイルが見つかりません"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "バックアップファイルが存在しません: $BACKUP_FILE"
        exit 1
    fi
    
    log_info "使用するバックアップ: $BACKUP_FILE"
}

# 現在のデータをバックアップ
backup_current() {
    log_warning "復旧前に現在のデータをバックアップします..."
    
    CURRENT_BACKUP="$BACKUP_DIR/before_restore_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$CURRENT_BACKUP"
    
    if [ -f "$DB_FILE" ]; then
        cp "$DB_FILE" "$CURRENT_BACKUP/"
        log_success "現在のデータベースをバックアップしました"
    fi
}

# バックアップを展開
extract_backup() {
    log_info "バックアップを展開中..."
    
    mkdir -p "$RESTORE_TEMP_DIR"
    tar -xzf "$BACKUP_FILE" -C "$RESTORE_TEMP_DIR"
    
    log_success "バックアップ展開完了"
}

# データベースを復旧
restore_database() {
    log_info "データベースを復旧中..."
    
    # 展開されたDBファイルを探す
    DB_BACKUP=$(find "$RESTORE_TEMP_DIR" -name "*.db" -not -name "*-wal" -not -name "*-shm" | head -1)
    
    if [ -z "$DB_BACKUP" ]; then
        log_error "バックアップ内にデータベースファイルが見つかりません"
        return 1
    fi
    
    # 現在のDBファイルを置き換え
    cp "$DB_BACKUP" "$DB_FILE"
    
    # WALファイルがあれば復元
    if [ -f "${DB_BACKUP}-wal" ]; then
        cp "${DB_BACKUP}-wal" "${DB_FILE}-wal"
    fi
    
    log_success "データベース復旧完了"
}

# アップロードファイルを復旧
restore_files() {
    log_info "アップロードファイルを復旧中..."
    
    UPLOADS_BACKUP=$(find "$RESTORE_TEMP_DIR" -name "*_uploads.tar.gz" | head -1)
    
    if [ -n "$UPLOADS_BACKUP" ]; then
        tar -xzf "$UPLOADS_BACKUP" -C .
        log_success "アップロードファイル復旧完了"
    else
        log_warning "アップロードファイルのバックアップが見つかりません"
    fi
}

# 設定ファイルを復旧
restore_config() {
    log_info "設定ファイルを復旧中..."
    
    CONFIG_BACKUP=$(find "$RESTORE_TEMP_DIR" -name "*.env.production" | head -1)
    
    if [ -n "$CONFIG_BACKUP" ]; then
        cp "$CONFIG_BACKUP" ".env.production.restored"
        log_success "設定ファイル復旧完了（.env.production.restored として保存）"
        log_warning "手動で確認して .env.production にリネームしてください"
    else
        log_warning "設定ファイルのバックアップが見つかりません"
    fi
}

# クリーンアップ
cleanup() {
    log_info "一時ファイルを削除中..."
    
    rm -rf "$RESTORE_TEMP_DIR"
    
    log_success "クリーンアップ完了"
}

# 復旧後の検証
verify_restore() {
    log_info "復旧を検証中..."
    
    if [ ! -f "$DB_FILE" ]; then
        log_error "データベースファイルが見つかりません"
        return 1
    fi
    
    # SQLiteの整合性チェック
    if command -v sqlite3 &> /dev/null; then
        if sqlite3 "$DB_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
            log_success "データベースの整合性チェック: OK"
        else
            log_error "データベースの整合性チェック: NG"
            return 1
        fi
    fi
    
    log_success "復旧検証完了"
}

# メイン処理
main() {
    echo ""
    log_warning "⚠️  データ復旧スクリプト ⚠️"
    echo ""
    
    # バックアップ一覧表示
    list_backups
    echo ""
    
    # バックアップファイル選択
    select_backup "$1"
    
    # 確認
    read -p "このバックアップから復旧しますか？ (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy](es)?$ ]]; then
        log_warning "復旧をキャンセルしました"
        exit 0
    fi
    
    log_info "復旧を開始します..."
    echo ""
    
    # 現在のデータをバックアップ
    backup_current
    
    # 復旧実行
    extract_backup
    restore_database
    restore_files
    restore_config
    
    # 検証
    verify_restore
    
    # クリーンアップ
    cleanup
    
    echo ""
    log_success "復旧が完了しました！"
    log_info "バックエンドを再起動してください:"
    echo "  cd backend && source venv/bin/activate && python3 -m uvicorn main:app --reload"
    echo ""
}

# エラーハンドリング
trap 'log_error "復旧失敗: line $LINENO"; cleanup' ERR

# 引数チェック
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# 実行
main "$@"
