#!/usr/bin/env python3
"""
Weekly Newsletter Generation Script
Phase 10-3: Execute weekly newsletter generation workflow
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from database import SessionLocal
from models.automated_content import AutomatedContentDB, TrendDataDB


async def main_async():
    """メイン処理（非同期）"""
    print("🚀 Starting weekly newsletter generation...")

    db = SessionLocal()
    try:
        # 前週のデータ取得
        week_ago = datetime.utcnow() - timedelta(days=7)

        # トップトレンド取得
        print("📊 Fetching top trends...")
        top_trends = db.query(TrendDataDB).filter(
            TrendDataDB.detected_at >= week_ago
        ).order_by(TrendDataDB.trend_score.desc()).limit(5).all()

        # 人気記事取得
        print("📚 Fetching popular articles...")
        popular_articles = db.query(AutomatedContentDB).filter(
            AutomatedContentDB.created_at >= week_ago,
            AutomatedContentDB.status == "published"
        ).order_by(AutomatedContentDB.quality_score.desc()).limit(5).all()

        # ニュースレター生成
        print("✍️  Generating newsletter...")
        newsletter_content = generate_newsletter_content(
            top_trends,
            popular_articles,
            week_ago
        )

        # データベースに保存
        newsletter = AutomatedContentDB(
            content_type="newsletter",
            title=f"週刊ニュースレター {datetime.utcnow().strftime('%Y/%m/%d')}",
            slug=f"newsletter-{datetime.utcnow().strftime('%Y-%m-%d')}",
            summary="今週のトップトレンドと人気記事をお届けします",
            content=newsletter_content,
            status="published",
            published_at=datetime.utcnow()
        )
        db.add(newsletter)
        db.commit()

        print(f"✅ Newsletter created: {newsletter.title}")
        print(f"  - Top trends: {len(top_trends)}")
        print(f"  - Popular articles: {len(popular_articles)}")
        print("\n🎉 Weekly newsletter generation completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


def generate_newsletter_content(
    trends,
    articles,
    week_start
) -> str:
    """ニュースレターコンテンツを生成"""
    content = f"""# AICA-SyS 週刊ニュースレター
## Week of {week_start.strftime('%Y/%m/%d')}

---

## 📈 今週のトップトレンド

"""

    # トレンド追加
    for i, trend in enumerate(trends, 1):
        content += f"""
### {i}. {trend.trend_name.title()} - {trend.trend_score:.1f}pt
{trend.source_count}つのソースで言及された注目トレンド
"""

    content += "\n---\n\n## 📚 今週の人気記事\n\n"

    # 記事追加
    for i, article in enumerate(articles, 1):
        content += f"""
### {i}. {article.title}
{article.summary}

[記事を読む](/articles/{article.slug})
"""

    content += "\n---\n\n## 🔮 来週の注目ポイント\n\n"
    content += "トレンドデータから予測される、来週注目すべき技術や話題をお届けします。\n"

    return content


def main():
    """エントリーポイント"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

