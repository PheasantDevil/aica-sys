"""
Social Media Posting Script
P1タスク: SNS自動投稿ワークフロー用スクリプト
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add backend directory to path
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Load environment variables (.env.local は任意)
# GitHub Actionsなどでは環境変数が直接設定されるため、.env.localは任意
env_local = BACKEND_DIR / ".env.local"
if env_local.exists():
    load_dotenv(
        env_local, override=False
    )  # override=Falseで既存の環境変数を上書きしない

from database import SessionLocal
from services.social_media_service import SocialMediaService
from sqlalchemy.exc import SQLAlchemyError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Social media posting utility")
    parser.add_argument(
        "--type",
        choices=["service", "trend", "article", "custom"],
        default="service",
        help="Type of social message to post",
    )
    parser.add_argument("--title", help="Article or trend title")
    parser.add_argument("--summary", help="Article or trend summary / message body")
    parser.add_argument("--url", help="URL to include in the post")
    parser.add_argument(
        "--message",
        help="Custom message (used for service/custom posts). "
        "If omitted, a default message is used.",
    )
    parser.add_argument(
        "--hashtags",
        help="Comma-separated hashtags (e.g. #TypeScript,#AI). "
        "Default hashtags will be used if omitted.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the formatted post without publishing",
    )
    return parser.parse_args()


def parse_hashtags(raw: str | None):
    if not raw:
        return None
    tags = []
    for item in raw.split(","):
        tag = item.strip()
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = f"#{tag}"
        tags.append(tag)
    return tags or None


def get_db_session():
    """Get database session, returning None if connection fails."""
    try:
        return SessionLocal()
    except SQLAlchemyError as exc:
        error_str = str(exc).lower()
        if "no such table" in error_str or "does not exist" in error_str:
            print(f"⚠️  Database table not found (migrations may not have run): {exc}")
        else:
            print(f"⚠️  Failed to initialize database session: {exc}")
        return None
    except Exception as exc:
        print(f"⚠️  Unexpected error initializing database session: {exc}")
        return None


def main():
    args = parse_args()

    # 環境変数の確認 (デバッグ用)
    twitter_vars = {
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    }

    # Check if values are set and not empty
    twitter_vars_status = {
        key: bool(value and value.strip()) for key, value in twitter_vars.items()
    }

    if not any(twitter_vars_status.values()):
        print("⚠️  Warning: No Twitter credentials found in environment variables")
        print(
            "   Set TWITTER_BEARER_TOKEN or TWITTER_API_KEY/SECRET/ACCESS_TOKEN/SECRET"
        )
        if not args.dry_run:
            raise SystemExit("Cannot post without Twitter credentials")
    else:
        print("✅ Twitter credentials found in environment")
        for key, is_set in twitter_vars_status.items():
            if is_set:
                value = twitter_vars[key]
                # Show length but not the actual value for security
                print(f"   - {key}: set (length: {len(value)})")
            else:
                value = twitter_vars[key]
                if value is None:
                    print(f"   - {key}: not set")
                else:
                    print(f"   - {key}: empty or whitespace only")

    db_session = get_db_session()
    service = SocialMediaService(db_session=db_session)
    hashtags = parse_hashtags(args.hashtags)

    if args.type == "article":
        if not all([args.title, args.summary, args.url]):
            raise ValueError("Article posts require --title, --summary, and --url")
        if args.dry_run:
            preview = service.format_article_tweet(
                args.title, args.summary, args.url, hashtags=hashtags
            )
            print("📝 Tweet preview:\n", preview)
            return
        result = service.post_article(
            title=args.title,
            summary=args.summary,
            url=args.url,
            hashtags=hashtags,
        )
    elif args.type == "trend":
        if not args.title or not args.summary:
            raise ValueError("Trend posts require --title and --summary")
        if args.dry_run:
            tweet = service.format_article_tweet(
                args.title, args.summary, args.url or "", hashtags=hashtags
            )
            print("📊 Trend tweet preview:\n", tweet)
            return
        result = service.post_trend_info(
            trend_title=args.title,
            trend_summary=args.summary,
            url=args.url,
        )
    elif args.type == "custom":
        if not args.message:
            raise ValueError("Custom posts require --message")
        if args.dry_run:
            preview = f"{args.message}\n\n{' '.join(hashtags or [])}".strip()
            print("✏️ Custom tweet preview:\n", preview)
            return
        result = service.post_service_introduction(
            message=args.message,
            hashtags=hashtags,
        )
    else:  # service
        default_message = (
            "🚀 AICA-SyS は TypeScript エコシステムの最新トレンドを "
            "AI が自動収集・記事化。技術者向けの高品質な知見を毎日配信中！"
        )
        message = args.message or default_message
        if args.dry_run:
            preview = f"{message}\n\n{' '.join(hashtags or [])}".strip()
            print("💬 Service intro tweet preview:\n", preview)
            return
        result = service.post_service_introduction(
            message=message,
            hashtags=hashtags,
        )

    status = result.get("platforms", {}).get("twitter", {})
    try:
        if result.get("success") and status.get("success", True):
            print("✅ Twitter post successful")
        else:
            print("⚠️ Twitter post failed")
            errors = result.get("errors", [])
            if status.get("error"):
                errors.append(status["error"])
            for err in errors:
                print(f"  - {err}")
            raise SystemExit(1)
    finally:
        if db_session:
            db_session.close()


if __name__ == "__main__":
    main()
