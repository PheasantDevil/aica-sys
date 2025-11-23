#!/usr/bin/env python3
"""Fix broken migration chain by stamping to 223a0ac841bb."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from database import engine
from sqlalchemy import text

try:
    with engine.begin() as conn:
        # Remove all existing versions
        conn.execute(text("DELETE FROM alembic_version"))
        # Stamp to 223a0ac841bb (the base migration that already has tables)
        conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES ('223a0ac841bb')")
        )
        print("✅ Stamped alembic_version to 223a0ac841bb")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

