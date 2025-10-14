#!/usr/bin/env python3
"""
Daily Article Generation Script
Phase 10-1: Execute daily article generation workflow
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from database import SessionLocal
from services.content_automation_service import ContentAutomationService
from services.source_aggregator_service import SourceAggregatorService


async def main_async():
    """メイン処理（非同期）"""
    print("🚀 Starting daily article generation...")

    db = SessionLocal()
    try:
        # Step 1: 情報収集
        print("📡 Collecting data from sources...")
        aggregator = SourceAggregatorService(db)
        source_data = await aggregator.collect_all_sources()
        print(f"✅ Collected {len(source_data)} items")

        # Step 2: トレンド分析
        print("📊 Analyzing trends...")
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        automation = ContentAutomationService(db, groq_api_key)
        trends = await automation.analyze_trends(source_data)
        print(f"✅ Found {len(trends)} trends")

        # Step 3: 記事生成
        print("✍️  Generating articles...")
        for i, trend in enumerate(trends[:3], 1):  # トップ3記事生成
            print(f"  Generating article {i}/3: {trend['keyword']}")
            article = await automation.generate_article(trend)
            if article and article.get('quality_score', 0) >= 80:
                print(f"  ✅ Generated: {article['title']} (Score: {article['quality_score']})")
            else:
                print(f"  ⚠️  Skipped (low quality)")

        print("\n🎉 Daily article generation completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()


def main():
    """エントリーポイント"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

