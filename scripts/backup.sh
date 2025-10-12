#!/bin/bash

# Backup Script for AICA-SyS
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
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${TIMESTAMP}"

# バックアップディレクトリの作成
mkdir -p "$BACKUP_DIR"

# バックアップ実行
backup_database() {
    log_info "データベースをバックアップ中..."
    
    if [ ! -f "$DB_FILE" ]; then
        log_error "データベースファイルが見つかりません: $DB_FILE"
        return 1
    fi
    
    # SQLiteバックアップ
    cp "$DB_FILE" "$BACKUP_DIR/${BACKUP_NAME}.db"
    
    # WALファイルも存在する場合はコピー
    if [ -f "${DB_FILE}-wal" ]; then
        cp "${DB_FILE}-wal" "$BACKUP_DIR/${BACKUP_NAME}.db-wal"
    fi
    
    if [ -f "${DB_FILE}-shm" ]; then
        cp "${DB_FILE}-shm" "$BACKUP_DIR/${BACKUP_NAME}.db-shm"
    fi
    
    log_success "データベースバックアップ完了"
}

backup_files() {
    log_info "アップロードファイルをバックアップ中..."
    
    # publicディレクトリのバックアップ
    if [ -d "public/uploads" ]; then
        tar -czf "$BACKUP_DIR/${BACKUP_NAME}_uploads.tar.gz" public/uploads/
        log_success "アップロードファイルバックアップ完了"
    else
        log_warning "アップロードディレクトリが見つかりません"
    fi
}

backup_config() {
    log_info "設定ファイルをバックアップ中..."
    
    # 環境変数ファイル（機密情報を除く）
    if [ -f ".env.production" ]; then
        cp ".env.production" "$BACKUP_DIR/${BACKUP_NAME}.env.production"
    fi
    
    log_success "設定ファイルバックアップ完了"
}

create_backup_manifest() {
    log_info "バックアップマニフェストを作成中..."
    
    cat > "$BACKUP_DIR/${BACKUP_NAME}_manifest.json" <<EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$TIMESTAMP",
  "date": "$(date -Iseconds)",
  "files": {
    "database": "${BACKUP_NAME}.db",
    "uploads": "${BACKUP_NAME}_uploads.tar.gz",
    "config": "${BACKUP_NAME}.env.production"
  },
  "sizes": {
    "database": "$(du -h "$BACKUP_DIR/${BACKUP_NAME}.db" | cut -f1)",
    "total": "$(du -sh "$BACKUP_DIR/${BACKUP_NAME}"* | awk '{s+=$1}END{print s}')"
  }
}
EOF
    
    log_success "マニフェスト作成完了"
}

cleanup_old_backups() {
    log_info "古いバックアップを削除中..."
    
    # 7日以上前のバックアップを削除
    find "$BACKUP_DIR" -name "backup_*" -mtime +7 -delete
    
    log_success "古いバックアップ削除完了"
}

compress_backup() {
    log_info "バックアップを圧縮中..."
    
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" ${BACKUP_NAME}*
    
    # 元のファイルを削除
    rm -f ${BACKUP_NAME}.db ${BACKUP_NAME}.db-* ${BACKUP_NAME}_* 2>/dev/null || true
    
    cd - > /dev/null
    
    log_success "バックアップ圧縮完了"
}

# メイン処理
main() {
    log_info "バックアップを開始します"
    log_info "タイムスタンプ: $TIMESTAMP"
    echo ""
    
    # バックアップ実行
    backup_database
    backup_files
    backup_config
    create_backup_manifest
    compress_backup
    cleanup_old_backups
    
    # サマリー
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)
    
    echo ""
    log_success "バックアップ完了！"
    log_info "バックアップファイル: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    log_info "サイズ: $BACKUP_SIZE"
    log_info "保存場所: $(pwd)/$BACKUP_DIR"
    
    # バックアップ一覧を表示
    echo ""
    log_info "利用可能なバックアップ:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
}

# エラーハンドリング
trap 'log_error "バックアップ失敗: line $LINENO"' ERR

# 実行
main
