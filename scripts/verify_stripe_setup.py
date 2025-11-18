#!/usr/bin/env python3
"""
Stripe本番設定確認スクリプト
P0タスク: Stripe本番設定確認
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

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


def check_stripe_keys():
    """Stripe APIキーの確認"""
    print_header("Stripe APIキー確認")
    
    # 環境変数から読み込み
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    env_local = backend_dir / ".env.local"
    if env_local.exists():
        load_dotenv(env_local)
    
    publishable_key = os.getenv("NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY", "")
    secret_key = os.getenv("STRIPE_SECRET_KEY", "")
    premium_price_id = os.getenv("NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Publishable key確認
    if publishable_key:
        if publishable_key.startswith("pk_live_"):
            print_success(f"Publishable key (Production): {publishable_key[:20]}...")
        elif publishable_key.startswith("pk_test_"):
            print_warning(f"Publishable key (Test): {publishable_key[:20]}...")
            print_warning("   ⚠️  Test key detected. Use production key for production.")
        else:
            print_error(f"Invalid publishable key format: {publishable_key[:20]}...")
    else:
        print_error("NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY not set")
    
    # Secret key確認
    if secret_key:
        if secret_key.startswith("sk_live_"):
            print_success(f"Secret key (Production): {secret_key[:20]}...")
        elif secret_key.startswith("sk_test_"):
            print_warning(f"Secret key (Test): {secret_key[:20]}...")
            print_warning("   ⚠️  Test key detected. Use production key for production.")
        else:
            print_error(f"Invalid secret key format: {secret_key[:20]}...")
    else:
        print_error("STRIPE_SECRET_KEY not set")
    
    # Premium Price ID確認
    if premium_price_id:
        if premium_price_id.startswith("price_"):
            print_success(f"Premium Price ID: {premium_price_id}")
        else:
            print_error(f"Invalid price ID format: {premium_price_id}")
    else:
        print_error("NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID not set")
    
    # Webhook secret確認
    if webhook_secret:
        if webhook_secret.startswith("whsec_"):
            print_success(f"Webhook secret: {webhook_secret[:20]}...")
        else:
            print_error(f"Invalid webhook secret format: {webhook_secret[:20]}...")
    else:
        print_warning("STRIPE_WEBHOOK_SECRET not set (may be set in deployment platform)")
    
    print("\n📋 環境変数設定状況:")
    print(f"   - Publishable Key: {'✅' if publishable_key else '❌'}")
    print(f"   - Secret Key: {'✅' if secret_key else '❌'}")
    print(f"   - Premium Price ID: {'✅' if premium_price_id else '❌'}")
    print(f"   - Webhook Secret: {'✅' if webhook_secret else '⚠️ '}")


def check_environment_variables():
    """環境変数設定確認"""
    print_header("環境変数設定確認")
    
    required_vars = {
        "Vercel (Frontend)": [
            "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
            "STRIPE_SECRET_KEY",
            "NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID",
            "STRIPE_WEBHOOK_SECRET",
        ],
        "Render (Backend)": [
            "STRIPE_SECRET_KEY",
            "STRIPE_PUBLISHABLE_KEY",
            "STRIPE_PREMIUM_PRICE_ID",
            "STRIPE_WEBHOOK_SECRET",
        ],
    }
    
    print_warning("⚠️  Environment variables must be set in deployment platforms:")
    print("\n📋 Vercel (Frontend):")
    for var in required_vars["Vercel (Frontend)"]:
        print(f"   - {var}")
    
    print("\n📋 Render (Backend):")
    for var in required_vars["Render (Backend)"]:
        print(f"   - {var}")
    
    print("\n📚 See: docs/stripe-production-checklist.md for details")


def check_webhook_endpoint():
    """Webhookエンドポイント確認"""
    print_header("Webhookエンドポイント確認")
    
    webhook_url = "https://aica-sys.vercel.app/api/webhooks/stripe"
    print(f"📡 Webhook URL: {webhook_url}")
    print_warning("⚠️  Verify webhook endpoint in Stripe Dashboard:")
    print("   1. Stripe Dashboard → Developers → Webhooks")
    print("   2. Add endpoint: https://aica-sys.vercel.app/api/webhooks/stripe")
    print("   3. Select events:")
    print("      - customer.subscription.created")
    print("      - customer.subscription.updated")
    print("      - customer.subscription.deleted")
    print("      - invoice.payment_succeeded")
    print("      - invoice.payment_failed")
    print("      - checkout.session.completed")
    print("   4. Copy signing secret (whsec_...)")
    print("   5. Set STRIPE_WEBHOOK_SECRET in Vercel/Render")


def check_test_cards():
    """テストカード情報表示"""
    print_header("テストカード情報")
    
    print("📋 Stripe提供のテストカード:")
    print("\n   Success Card:")
    print("   - カード番号: 4242 4242 4242 4242")
    print("   - 有効期限: 任意の未来の日付（例: 12/25）")
    print("   - CVC: 任意の3桁（例: 123）")
    print("   - 郵便番号: 任意（例: 123-4567）")
    print("\n   Decline Card:")
    print("   - カード番号: 4000 0000 0000 0002")
    print("\n   📚 詳細: https://stripe.com/docs/testing")


def main():
    """メイン処理"""
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}Stripe本番設定確認スクリプト{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    
    # Stripe APIキー確認
    check_stripe_keys()
    
    # 環境変数設定確認
    check_environment_variables()
    
    # Webhookエンドポイント確認
    check_webhook_endpoint()
    
    # テストカード情報表示
    check_test_cards()
    
    print_header("確認完了")
    print("📚 詳細は docs/stripe-production-checklist.md を参照してください")
    print("\n⚠️  注意事項:")
    print("   - Secret keyは絶対に公開しない")
    print("   - 本番環境では必ず本番キー（pk_live_, sk_live_）を使用")
    print("   - Webhook署名検証を必ず実施")


if __name__ == "__main__":
    main()

