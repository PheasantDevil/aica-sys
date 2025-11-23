#!/usr/bin/env python3
"""Fix broken migration chain by removing later migrations."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from sqlalchemy import text
from database import engine

try:
    with engine.begin() as conn:
        conn.execute(
            text(
                "DELETE FROM alembic_version WHERE version_num IN ('2a3b4c5d6e7f', '1cf2ab5a8998')"
            )
        )
        print("✅ Removed later migrations from alembic_version")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

