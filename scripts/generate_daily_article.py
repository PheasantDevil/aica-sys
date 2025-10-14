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

from datetime import datetime

from database import SessionLocal
from models.automated_content import (AutomatedContentDB, ContentStatus,
                                      ContentType, TrendDataDB, ContentGenerationLogDB)
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

        # Step 3: トレンドデータ保存
        print("💾 Saving trend data...")
        for trend in trends[:5]:
            trend_db = TrendDataDB(
                trend_name=trend['keyword'],
                trend_score=float(trend['score']),
                source_count=trend['source_count'],
                keywords=[trend['keyword']],
                related_topics=[item.get('title', '') for item in trend.get('related_items', [])[:3]],
                data_snapshot=trend,
                detected_at=datetime.utcnow()
            )
            db.add(trend_db)
        db.commit()
        print(f"✅ Saved {len(trends[:5])} trend data")

        # Step 4: 記事生成と保存
        print("✍️  Generating articles...")
        generated_count = 0
        skipped_count = 0
        
        for i, trend in enumerate(trends[:3], 1):  # トップ3記事生成
            print(f"  Generating article {i}/3: {trend['keyword']}")
            
            start_time = datetime.utcnow()
            article = await automation.generate_article(trend)
            
            # 生成ログ保存
            log = ContentGenerationLogDB(
                generation_type="daily_article",
                status="success" if article else "failed",
                api_cost=0.0,  # Groqは無料
                generation_time=article.get('generation_time', 0) if article else 0,
                quality_score=article.get('quality_score', 0) if article else 0
            )
            
            if article and article.get('quality_score', 0) >= 80:
                # スラッグ生成
                slug = article['title'].lower().replace(' ', '-').replace('/', '-')[:100]
                
                # 記事をDBに保存
                article_db = AutomatedContentDB(
                    content_type=ContentType.ARTICLE,
                    title=article['title'],
                    slug=slug,
                    summary=article.get('summary', '')[:500],
                    content=article['content'],
                    metadata={
                        'tags': article.get('tags', []),
                        'read_time': article.get('read_time', 5),
                        **article.get('metadata', {})
                    },
                    seo_data=article.get('seo_data', {}),
                    quality_score=article['quality_score'],
                    status=ContentStatus.PUBLISHED,
                    published_at=datetime.utcnow()
                )
                db.add(article_db)
                db.commit()
                
                log.content_id = article_db.id
                log.status = "success"
                generated_count += 1
                
                print(f"  ✅ Generated & Saved: {article['title']}")
                print(f"     Score: {article['quality_score']:.1f} | ID: {article_db.id}")
            else:
                log.error_message = "Quality score < 80" if article else "Generation failed"
                log.status = "skipped" if article else "failed"
                skipped_count += 1
                print(f"  ⚠️  Skipped (low quality or failed)")
            
            db.add(log)
            db.commit()

        print(f"\n📊 Results: {generated_count} generated, {skipped_count} skipped")

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

