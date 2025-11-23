#!/usr/bin/env python3
"""Fix broken migration chain by dropping conflicting tables and stamping."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from database import engine
from sqlalchemy import inspect, text

# Tables created by 4741adeef488 and 1cf2ab5a8998 that might conflict
TABLES_TO_DROP = [
    "social_post_logs",
    "source_data",
    "trend_data",
    "automated_contents",
    "content_generation_logs",
]

try:
    with engine.begin() as conn:
        # Check which tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Drop conflicting tables if they exist
        dropped_tables = []
        for table in TABLES_TO_DROP:
            if table in existing_tables:
                # Drop indexes first
                indexes = inspector.get_indexes(table)
                for index in indexes:
                    if index["name"].startswith("ix_"):
                        try:
                            conn.execute(text(f'DROP INDEX IF EXISTS "{index["name"]}"'))
                        except Exception:
                            pass  # Index might not exist or already dropped
                
                # Drop table
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                dropped_tables.append(table)
                print(f"✅ Dropped table: {table}")
        
        if dropped_tables:
            print(f"✅ Dropped {len(dropped_tables)} conflicting tables")
        else:
            print("ℹ️  No conflicting tables to drop")
        
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

