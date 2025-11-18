#!/usr/bin/env python3
"""
本番環境デプロイ確認スクリプト
P0タスク: 本番環境デプロイ確認
"""

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

# カラー出力用
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str):
    """ヘッダーを表示"""
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")


def print_success(text: str):
    """成功メッセージを表示"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text: str):
    """警告メッセージを表示"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text: str):
    """エラーメッセージを表示"""
    print(f"{RED}❌ {text}{RESET}")


def check_url(url: str, timeout: int = 5) -> tuple[bool, str]:
    """URLのアクセス確認"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True, f"Status: {response.status_code}"
        else:
            return False, f"Status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def check_vercel_deployment():
    """Vercelデプロイ確認"""
    print_header("Vercel デプロイ確認")
    
    vercel_url = "https://aica-sys.vercel.app"
    
    # URL確認
    print(f"📡 Checking: {vercel_url}")
    success, message = check_url(vercel_url)
    if success:
        print_success(f"Vercel is accessible: {message}")
    else:
        print_error(f"Vercel is not accessible: {message}")
    
    # ヘルスチェック
    health_url = f"{vercel_url}/api/health"
    print(f"📡 Checking health: {health_url}")
    success, message = check_url(health_url)
    if success:
        print_success(f"Health check passed: {message}")
    else:
        print_warning(f"Health check failed: {message}")
    
    # Vercel CLI確認
    try:
        result = subprocess.run(
            ["vercel", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Vercel CLI installed: {result.stdout.strip()}")
        else:
            print_warning("Vercel CLI not working properly")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("Vercel CLI not found or not working")
    
    print_warning("⚠️  Environment variables need to be set manually in Vercel Dashboard")
    print("   See: docs/production-deployment-checklist.md")


def check_render_deployment():
    """Renderデプロイ確認"""
    print_header("Render デプロイ確認")
    
    render_url = "https://aica-sys-backend.onrender.com"
    
    # URL確認
    print(f"📡 Checking: {render_url}")
    success, message = check_url(render_url, timeout=10)  # Renderは起動に時間がかかる
    if success:
        print_success(f"Render is accessible: {message}")
    else:
        print_warning(f"Render may be sleeping or not accessible: {message}")
        print_warning("   Note: Free tier services sleep after 15 minutes of inactivity")
    
    # ヘルスチェック
    health_url = f"{render_url}/health"
    print(f"📡 Checking health: {health_url}")
    success, message = check_url(health_url, timeout=10)
    if success:
        print_success(f"Health check passed: {message}")
    else:
        print_warning(f"Health check failed: {message}")
    
    # APIヘルスチェック
    api_health_url = f"{render_url}/api/health"
    print(f"📡 Checking API health: {api_health_url}")
    success, message = check_url(api_health_url, timeout=10)
    if success:
        print_success(f"API health check passed: {message}")
    else:
        print_warning(f"API health check failed: {message}")
    
    print_warning("⚠️  Environment variables need to be set manually in Render Dashboard")
    print("   See: docs/production-deployment-checklist.md")


def check_environment_variables():
    """環境変数確認"""
    print_header("環境変数確認")
    
    # 必要な環境変数リスト
    required_vars = {
        "Vercel": [
            "DATABASE_URL",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_KEY",
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "NEXTAUTH_URL",
            "NEXT_PUBLIC_BASE_URL",
            "NEXT_PUBLIC_API_URL",
        ],
        "Render": [
            "DATABASE_URL",
            "GROQ_API_KEY",
            "ENVIRONMENT",
            "CORS_ORIGINS",
        ],
    }
    
    print_warning("⚠️  Environment variables must be set in deployment platforms:")
    print("\n📋 Vercel (Frontend):")
    for var in required_vars["Vercel"]:
        print(f"   - {var}")
    
    print("\n📋 Render (Backend):")
    for var in required_vars["Render"]:
        print(f"   - {var}")
    
    print("\n📚 See: docs/production-deployment-checklist.md for details")


def check_database_connection():
    """データベース接続確認"""
    print_header("データベース接続確認")
    
    # check_database_url.pyを実行
    script_path = Path(__file__).parent.parent / "scripts" / "check_database_url.py"
    if script_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print_success("Database connection check script executed")
                print(result.stdout)
            else:
                print_warning("Database connection check script failed")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print_warning("Database connection check timed out")
        except Exception as e:
            print_warning(f"Could not run database check: {e}")
    else:
        print_warning("Database check script not found")


def main():
    """メイン処理"""
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}本番環境デプロイ確認スクリプト{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    
    # Vercel確認
    check_vercel_deployment()
    
    # Render確認
    check_render_deployment()
    
    # 環境変数確認
    check_environment_variables()
    
    # データベース接続確認
    check_database_connection()
    
    print_header("確認完了")
    print("📚 詳細は docs/production-deployment-checklist.md を参照してください")


if __name__ == "__main__":
    main()

