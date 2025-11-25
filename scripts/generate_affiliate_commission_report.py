#!/usr/bin/env python3
"""
Generate affiliate commission report and store it in analytics.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

env_local = BACKEND_DIR / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

from database import SessionLocal
from services.affiliate_service import AffiliateService
from services.analytics_service import AnalyticsService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate affiliate commission report")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to include in the report window (default: 30)",
    )
    parser.add_argument(
        "--affiliate-id",
        type=int,
        help="Optional affiliate ID to generate a report for",
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
    parser.add_argument(
        "--settle-min-balance",
        type=float,
        help="Automatically create payout requests for affiliates above this balance",
    )
    parser.add_argument(
        "--payment-method",
        default="bank_transfer",
        help="Payment method when auto-settling commissions",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        service = AffiliateService(db)
        analytics = AnalyticsService(db)

        now = datetime.now(timezone.utc)
        start = now - timedelta(days=args.days)

        report = asyncio.run(
            service.get_commission_report(
                start_date=start, end_date=now, affiliate_id=args.affiliate_id
            )
        )

        saved_report = asyncio.run(
            analytics.save_affiliate_commission_report(
                title=f"Affiliate commission report ({start.date()} ~ {now.date()})",
                summary=report,
                created_by=args.created_by,
            )
        )

        print("📄 Affiliate commission report stored:")
        print(f"   ID: {saved_report.id}")
        print(f"   Period: {report['period']['start']} -> {report['period']['end']}")
        print(
            "   Total commission:",
            report["summary"]["total_commission"],
        )

        if args.settle_min_balance:
            payouts = asyncio.run(
                service.settle_commissions(
                    min_balance=args.settle_min_balance,
                    payment_method=args.payment_method,
                )
            )
            print(f"💸 Auto-settled payouts: {len(payouts)} entries")

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"📝 Report summary written to {output_path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()