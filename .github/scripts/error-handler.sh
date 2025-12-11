#!/bin/bash
# 汎用的なエラーハンドリングスクリプト
# すべてのワークフローで使用可能なエラーハンドリング機能を提供

set -euo pipefail

# エラー発生時の処理
trap 'error_handler $? $LINENO "$BASH_COMMAND"' ERR

error_handler() {
    local exit_code=$1
    local line_number=$2
    local command=$3
    
    echo "::error::Step failed at line $line_number with exit code $exit_code"
    echo "::error::Command: $command"
    
    # エラータイプを判定
    ERROR_TYPE=$(detect_error_type "$command" "$exit_code")
    echo "ERROR_TYPE=$ERROR_TYPE" >> $GITHUB_ENV
    
    # エラーログを出力
    echo "::error::Error type: $ERROR_TYPE"
    
    exit $exit_code
}

detect_error_type() {
    local command=$1
    local exit_code=$2
    
    # コマンドとエラーコードからエラータイプを判定
    if echo "$command" | grep -qE "(alembic|migration)"; then
        echo "migration"
    elif echo "$command" | grep -qE "(pip install|npm install)"; then
        echo "dependency"
    elif echo "$command" | grep -qE "(black|isort|prettier)"; then
        echo "format"
    elif echo "$command" | grep -qE "(flake8|eslint|lint)"; then
        echo "lint"
    else
        echo "unknown"
    fi
}

# コマンド実行のラッパー関数
run_with_error_handling() {
    local command="$@"
    local output
    local exit_code
    
    set +e
    output=$(eval "$command" 2>&1)
    exit_code=$?
    set -e
    
    # 出力を必ず表示
    echo "$output"
    
    if [ $exit_code -ne 0 ]; then
        ERROR_TYPE=$(detect_error_type "$command" "$exit_code")
        echo "::error::Command failed with error type: $ERROR_TYPE"
        echo "ERROR_TYPE=$ERROR_TYPE" >> $GITHUB_ENV
        echo "ERROR_MESSAGE<<EOF" >> $GITHUB_ENV
        echo "$output" >> $GITHUB_ENV
        echo "EOF" >> $GITHUB_ENV
        exit $exit_code
    fi
    
    return 0
}

