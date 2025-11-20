#!/usr/bin/env python3
"""
Daily Trend Analysis Script
Phase 10-2: Execute daily trend analysis workflow
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from database import SessionLocal
from services.trend_analysis_service import TrendAnalysisService
from sqlalchemy.exc import OperationalError, SQLAlchemyError


async def main_async():
    """メイン処理（非同期）"""
    print("🚀 Starting daily trend analysis...")

    db = None
    try:
        db = SessionLocal()
    except OperationalError as exc:
        print(
            "⚠️  Database connection failed while starting trend analysis: "
            f"{exc}. Skipping run."
        )
        return

    try:
        # トレンド分析実行
        print("📊 Analyzing trends...")
        service = TrendAnalysisService(db)
        result = await service.analyze_daily_trends()

        if not result:
            print("⚠️  No trends detected today")
            return

        print(f"✅ Analyzed trends:")
        print(f"  - Top trends: {len(result.get('top_trends', []))}")
        print(f"  - Rising trends: {len(result.get('rising_trends', []))}")
        print(f"  - Categories: {len(result.get('categories', {}))}")
        print(f"  - Total sources: {result.get('total_sources', 0)}")

        # 結果をJSON出力（オプション）
        output_file = Path(__file__).parent.parent / "public" / "trends-latest.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved to {output_file}")

        print("\n🎉 Daily trend analysis completed!")

    except (OperationalError, SQLAlchemyError) as exc:
        print(
            "⚠️  Database operation failed during trend analysis: "
            f"{exc}. Skipping run."
        )
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if db:
            db.close()


def main():
    """エントリーポイント"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
