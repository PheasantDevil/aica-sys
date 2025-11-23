#!/usr/bin/env python3
"""Check if migration 4741adeef488 is applied."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = [row[0] for row in result]
        if "4741adeef488" in versions:
            print("✅ Migration 4741adeef488 already recorded")
            sys.exit(0)
        else:
            print("⚠️ Migration 4741adeef488 not recorded")
            sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
