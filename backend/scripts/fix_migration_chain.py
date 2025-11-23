#!/usr/bin/env python3
"""Fix broken migration chain by stamping to appropriate revision."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from database import engine
from sqlalchemy import inspect, text

try:
    with engine.begin() as conn:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Check which tables from migrations exist
        has_4741_tables = all(
            table in existing_tables
            for table in [
                "source_data",
                "trend_data",
                "automated_contents",
                "content_generation_logs",
            ]
        )
        has_1cf2_table = "social_post_logs" in existing_tables

        # Determine the appropriate revision to stamp
        if has_4741_tables and has_1cf2_table:
            # All tables exist, stamp to 1cf2ab5a8998 (before 2a3b4c5d6e7f)
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(
                text(
                    "INSERT INTO alembic_version (version_num) VALUES ('1cf2ab5a8998')"
                )
            )
            print("✅ Stamped alembic_version to 1cf2ab5a8998 (all tables exist)")
        elif has_4741_tables:
            # Only 4741 tables exist, stamp to 4741adeef488
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(
                text(
                    "INSERT INTO alembic_version (version_num) VALUES ('4741adeef488')"
                )
            )
            print("✅ Stamped alembic_version to 4741adeef488")
        else:
            # Base tables exist, stamp to 223a0ac841bb
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(
                text(
                    "INSERT INTO alembic_version (version_num) VALUES ('223a0ac841bb')"
                )
            )
            print("✅ Stamped alembic_version to 223a0ac841bb")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
