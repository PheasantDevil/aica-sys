#!/usr/bin/env python3
"""
Generate SNS posting analytics report.

This script aggregates the last N days of social post logs, refreshes
tweet engagement metrics (optional), and stores a summary report.
"""

import argparse
import asyncio
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

env_local = BACKEND_DIR / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

from database import SessionLocal  # noqa: E402
from models.analytics import SocialPostLogDB  # noqa: E402
from services.analytics_service import AnalyticsService  # noqa: E402
from services.social_media_service import SocialMediaService  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SNS posting report")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to include in the report window (default: 7)",
    )
    parser.add_argument(
        "--update-metrics",
        action="store_true",
        help="Refresh tweet engagement metrics before generating the report",
    )
    parser.add_argument(
        "--created-by",
        default="automation",
        help="Report creator identifier (default: automation)",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the report summary as JSON",
    )
    return parser.parse_args()


def summarize_logs(logs: List[SocialPostLogDB]) -> Dict[str, Any]:
    total = len(logs)
    successes = sum(1 for log in logs if log.status == "success")
    failures = total - successes

    posts_by_type = Counter(log.post_type for log in logs)
    tags = Counter()
    for log in logs:
        if log.hashtags:
            tags.update(log.hashtags)

    metrics_available = [
        log for log in logs if log.tweet_metrics and log.status == "success"
    ]

    def engagement_score(log: SocialPostLogDB) -> int:
        metrics = log.tweet_metrics or {}
        return int(
            metrics.get("retweet_count", 0)
            + metrics.get("reply_count", 0)
            + metrics.get("like_count", 0)
            + metrics.get("quote_count", 0)
        )

    top_posts = sorted(
        metrics_available,
        key=engagement_score,
        reverse=True,
    )[:5]

    return {
        "total_posts": total,
        "success": successes,
        "failed": failures,
        "success_rate": round((successes / total) * 100, 2) if total else 0.0,
        "posts_by_type": posts_by_type,
        "top_hashtags": tags.most_common(10),
        "top_posts": [
            {
                "id": log.id,
                "post_type": log.post_type,
                "title": log.title,
                "tweet_id": log.tweet_id,
                "url": log.url,
                "metrics": log.tweet_metrics,
                "engagement_score": engagement_score(log),
            }
            for log in top_posts
        ],
    }


def main():
    args = parse_args()
    db = SessionLocal()
    try:
        social_service = SocialMediaService(db_session=db)
        if args.update_metrics:
            updated = social_service.refresh_post_metrics(hours=args.days * 24)
            print(f"🔄 Refreshed metrics for {len(updated)} posts")

        now = datetime.now(timezone.utc)
        start = now - timedelta(days=args.days)

        logs = (
            db.query(SocialPostLogDB)
            .filter(SocialPostLogDB.posted_at >= start)
            .order_by(SocialPostLogDB.posted_at.desc())
            .all()
        )

        summary = summarize_logs(logs)
        period = {"start": start.isoformat(), "end": now.isoformat()}

        analytics = AnalyticsService(db)

        report = asyncio.run(
            analytics.save_social_post_report(
                title=f"SNS投稿レポート ({period['start'][:10]} ~ {period['end'][:10]})",
                period=period,
                summary=summary,
                created_by=args.created_by,
            )
        )

        print("📄 Social post report stored:")
        print(f"   ID: {report.id}")
        print(f"   Period: {period['start']} -> {period['end']}")
        print(f"   Total Posts: {summary['total_posts']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Top hashtags: {summary['top_hashtags'][:3]}")

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(
                json.dumps(
                    {"period": period, "summary": summary}, ensure_ascii=False, indent=2
                ),
                encoding="utf-8",
            )
            print(f"📝 Summary written to {output_path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
