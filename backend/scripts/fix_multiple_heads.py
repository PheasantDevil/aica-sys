#!/usr/bin/env python3
"""Fix multiple head revisions by creating a merge migration or selecting the correct head."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

try:
    from alembic.script import ScriptDirectory
    from alembic.config import Config
    from alembic import command
except ImportError:
    print("❌ Alembic not installed")
    sys.exit(1)


def get_heads():
    """Get all head revisions."""
    backend_path = Path(__file__).parent.parent
    alembic_cfg = Config(str(backend_path / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_path / "alembic"))
    
    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_revisions("heads")
    return [str(head.revision) for head in heads]


def get_current_revision():
    """Get current database revision."""
    from sqlalchemy import text
    from database import engine
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            rows = result.fetchall()
            if rows:
                return [row[0] for row in rows]
            return []
    except Exception as e:
        print(f"⚠️ Error getting current revision: {e}")
        return []


def create_merge_migration(heads):
    """Create a merge migration for multiple heads."""
    backend_path = Path(__file__).parent.parent
    alembic_cfg = Config(str(backend_path / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_path / "alembic"))
    
    # Create merge migration
    heads_str = " ".join(heads)
    print(f"🔧 Creating merge migration for heads: {heads_str}")
    
    try:
        command.revision(
            alembic_cfg,
            message="merge multiple heads",
            head=heads,
            branch_label=None,
        )
        print("✅ Merge migration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create merge migration: {e}")
        import traceback
        traceback.print_exc()
        return False


def select_primary_head(heads, current_revisions):
    """Select the primary head based on current database state."""
    # If database has one of the heads, use that
    for head in heads:
        if head in current_revisions:
            print(f"✅ Database is at {head}, using as primary head")
            return head
    
    # Otherwise, use the first head (could be improved with more logic)
    if heads:
        print(f"⚠️  No matching head in database, using first head: {heads[0]}")
        return heads[0]
    
    return None


def main():
    """Main function to fix multiple heads."""
    print("🔍 Checking for multiple head revisions...")
    heads = get_heads()
    
    if len(heads) <= 1:
        print("✅ Single head revision (no fix needed)")
        return
    
    print(f"❌ Found {len(heads)} head revisions: {', '.join(heads)}")
    
    current_revisions = get_current_revision()
    print(f"📊 Current database revision(s): {', '.join(current_revisions) if current_revisions else 'None'}")
    
    # Try to create a merge migration
    print("\n🔧 Attempting to create merge migration...")
    if create_merge_migration(heads):
        print("✅ Merge migration created successfully")
        print("⚠️  Next step: Review and apply the merge migration")
    else:
        print("❌ Failed to create merge migration automatically")
        print("\n💡 Manual fix required:")
        print("   1. Identify which head should be the primary")
        print("   2. Create merge migration manually:")
        print(f"      alembic revision --autogenerate -m 'merge heads' --head {heads[0]} --head {heads[1]}")
        print("   3. Or stamp to the correct head if one is already applied:")
        primary = select_primary_head(heads, current_revisions)
        if primary:
            print(f"      alembic stamp {primary}")
        sys.exit(1)


if __name__ == "__main__":
    main()

