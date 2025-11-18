#!/usr/bin/env python3
"""
Twitter API接続テストスクリプト
P1タスク: Twitter API統合確認
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Load environment variables
backend_dir = Path(__file__).parent.parent / "backend"
env_local = backend_dir / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

# Color output
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


def check_environment_variables():
    """環境変数の確認"""
    print_header("環境変数確認")

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    # Check OAuth 2.0 (Bearer Token)
    if bearer_token:
        if bearer_token.startswith("Bearer ") or len(bearer_token) > 50:
            print_success(f"TWITTER_BEARER_TOKEN is set (OAuth 2.0)")
        else:
            print_warning(f"TWITTER_BEARER_TOKEN format may be incorrect")
    else:
        print_warning("TWITTER_BEARER_TOKEN not set")

    # Check OAuth 1.0a credentials
    oauth1_creds = [api_key, api_secret, access_token, access_token_secret]
    if all(oauth1_creds):
        print_success("OAuth 1.0a credentials are set (for media upload)")
    else:
        missing = [
            name
            for name, value in zip(
                [
                    "TWITTER_API_KEY",
                    "TWITTER_API_SECRET",
                    "TWITTER_ACCESS_TOKEN",
                    "TWITTER_ACCESS_TOKEN_SECRET",
                ],
                oauth1_creds,
            )
            if not value
        ]
        if missing:
            print_warning(f"OAuth 1.0a credentials missing: {', '.join(missing)}")
            print_warning("   Media upload will be disabled without OAuth 1.0a")

    # Summary
    has_bearer = bool(bearer_token)
    has_oauth1 = all(oauth1_creds)

    if has_bearer or has_oauth1:
        print_success("Twitter API credentials configured")
        return True
    else:
        print_error("No Twitter API credentials found")
        print("\n📚 Setup instructions:")
        print("   1. Go to https://developer.twitter.com/")
        print("   2. Create a Developer Account")
        print("   3. Create an App and get API keys")
        print("   4. Set environment variables in backend/.env.local")
        return False


def test_twitter_connection():
    """Twitter API接続テスト"""
    print_header("Twitter API接続テスト")

    try:
        from services.twitter_client import TwitterClient

        print("Initializing Twitter client...")
        client = TwitterClient()

        print("Verifying credentials...")
        if client.verify_credentials():
            print_success("Twitter API connection successful!")
            return True
        else:
            print_error("Twitter API credentials verification failed")
            return False
    except ImportError as e:
        print_error(f"Failed to import Twitter client: {e}")
        print_warning("Install tweepy: pip install tweepy>=5.0.0")
        return False
    except ValueError as e:
        print_error(f"Configuration error: {e}")
        return False
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False


def test_tweet_posting():
    """テストツイート投稿（実際には投稿しない）"""
    print_header("ツイート投稿テスト（Dry Run）")

    try:
        from services.social_media_service import SocialMediaService

        service = SocialMediaService()

        # Test tweet formatting
        test_tweet = service.format_article_tweet(
            title="TypeScript 5.6 Released",
            summary="TypeScript 5.6 introduces new decorators and faster incremental builds.",
            url="https://aica-sys.vercel.app/articles/typescript-5-6",
            hashtags=["#TypeScript", "#JavaScript"],
        )

        print("📝 Formatted tweet:")
        print(f"   {test_tweet}")
        print(f"\n   Length: {len(test_tweet)} characters")

        if len(test_tweet) <= 280:
            print_success("Tweet format is valid (within 280 characters)")
        else:
            print_error(f"Tweet exceeds 280 characters: {len(test_tweet)}")

        return True
    except Exception as e:
        print_error(f"Tweet formatting test failed: {e}")
        return False


def main():
    """メイン処理"""
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}Twitter API接続テストスクリプト{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")

    # 環境変数確認
    has_creds = check_environment_variables()

    if not has_creds:
        print("\n⚠️  Please set Twitter API credentials before testing connection")
        sys.exit(1)

    # 接続テスト
    connection_ok = test_twitter_connection()

    # ツイート投稿テスト（Dry Run）
    if connection_ok:
        test_tweet_posting()

    print_header("テスト完了")
    if connection_ok:
        print_success("Twitter API integration is ready!")
    else:
        print_warning("Twitter API integration needs configuration")
        print("\n📚 Next steps:")
        print("   1. Set Twitter API credentials in backend/.env.local")
        print("   2. Run this script again to verify connection")


if __name__ == "__main__":
    main()

