"""
One-shot batch runner for automated content synchronization.

Usage:
  ./venv/bin/python scripts/sync_automated_content.py
"""

from database import SessionLocal
from services.content_sync_service import get_content_sync_service


def main() -> None:
    db = SessionLocal()
    try:
        service = get_content_sync_service()
        stats = service.sync_published_content(db)
        print(
            "sync_completed",
            {
                "scanned": stats["scanned"],
                "article_upserts": stats["article_upserts"],
                "newsletter_upserts": stats["newsletter_upserts"],
                "trend_upserts": stats["trend_upserts"],
                "skipped": stats["skipped"],
            },
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
