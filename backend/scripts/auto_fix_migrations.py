#!/usr/bin/env python3
"""Automatically detect and fix common migration issues."""

import importlib.util
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path.resolve()))


# Import detection and fix modules dynamically
def import_module_from_file(module_name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scripts_path = backend_path / "scripts"
detect_module = import_module_from_file(
    "detect_migration_issues", scripts_path / "detect_migration_issues.py"
)
fix_dup_module = import_module_from_file(
    "fix_duplicate_revisions", scripts_path / "fix_duplicate_revisions.py"
)
fix_heads_module = import_module_from_file(
    "fix_multiple_heads", scripts_path / "fix_multiple_heads.py"
)
fix_refs_module = import_module_from_file(
    "fix_missing_revision_references",
    scripts_path / "fix_missing_revision_references.py",
)

detect_duplicate_revisions = detect_module.detect_duplicate_revisions
detect_multiple_heads = detect_module.detect_multiple_heads
detect_missing_revision_references = detect_module.detect_missing_revision_references
find_duplicate_revisions = fix_dup_module.find_duplicate_revisions
fix_duplicate_revision = fix_dup_module.fix_duplicate_revision
get_heads = fix_heads_module.get_heads
get_current_revision = fix_heads_module.get_current_revision
create_merge_migration = fix_heads_module.create_merge_migration
fix_missing_revision_reference = fix_refs_module.fix_missing_revision_reference
find_suitable_revision = fix_refs_module.find_suitable_revision
get_available_revisions = fix_refs_module.get_available_revisions


def auto_fix_all():
    """Automatically detect and fix all migration issues."""
    issues_fixed = False

    print("=" * 60)
    print("🔍 Migration Auto-Fix Tool")
    print("=" * 60)

    # Step 1: Check for missing revision references
    print("\n[1/4] Checking for missing revision references...")
    try:
        missing_refs = detect_missing_revision_references()
        if missing_refs:
            print(
                f"❌ Found {len(missing_refs)} file(s) with missing revision references"
            )
            available_revisions = get_available_revisions()
            if not available_revisions:
                print(
                    "⚠️ No available revisions found; cannot auto-fix missing references"
                )
            else:
                versions_path = backend_path / "alembic" / "versions"
                for file_name, missing_revision in missing_refs:
                    file_path = versions_path / file_name
                    replacement = find_suitable_revision(
                        missing_revision, available_revisions
                    )
                    if replacement:
                        if fix_missing_revision_reference(
                            file_path, missing_revision, replacement
                        ):
                            issues_fixed = True
        else:
            print("✅ No missing revision references")
    except (OSError, ImportError) as e:
        print(f"⚠️ Could not process missing revision references: {e}")
        import traceback

        traceback.print_exc()
    except Exception as e:
        print(f"❌ Unexpected error processing missing revision references: {e}")
        import traceback

        traceback.print_exc()
        raise

    # Step 2: Check for duplicate revisions
    print("\n[2/4] Checking for duplicate revision IDs...")
    duplicates = detect_duplicate_revisions()

    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate revision ID(s)")
        for revision_id, files in duplicates.items():
            print(f"   Fixing revision {revision_id}...")
            new_revision = fix_duplicate_revision(files, keep_first=True)
            if new_revision:
                issues_fixed = True
                print(f"   ✅ Fixed: {revision_id} -> {new_revision}")
            else:
                print(f"   ❌ Failed to fix {revision_id}")
                return False
    else:
        print("✅ No duplicate revision IDs")

    # Step 3: Check for multiple heads
    print("\n[3/4] Checking for multiple head revisions...")
    heads = get_heads()

    if len(heads) > 1:
        print(f"❌ Found {len(heads)} head revisions: {', '.join(heads)}")
        current_revisions = get_current_revision()
        print(
            f"📊 Current database revision(s): {', '.join(current_revisions) if current_revisions else 'None'}"
        )

        # Try to create merge migration
        print("🔧 Creating merge migration...")
        if create_merge_migration(heads):
            issues_fixed = True
            print("✅ Merge migration created")
        else:
            print("⚠️  Could not create merge migration automatically")
            print("   This may require manual intervention")
    else:
        print("✅ Single head revision")

    # Step 4: Verify fixes
    print("\n[4/4] Verifying fixes...")
    duplicates_after = detect_duplicate_revisions()
    heads_after = get_heads()
    missing_refs_after = detect_missing_revision_references()

    if duplicates_after:
        print(f"❌ Still have {len(duplicates_after)} duplicate revision ID(s)")
        return False

    if missing_refs_after:
        print(
            f"❌ Still have {len(missing_refs_after)} file(s) with missing revision references"
        )
        return False

    if len(heads_after) > 1:
        print(f"⚠️  Still have {len(heads_after)} head revisions")
        print("   Merge migration may need to be applied first")
        return False

    if issues_fixed:
        print("\n✅ All migration issues fixed!")
        print("⚠️  Next steps:")
        print("   1. Review the changes made")
        print("   2. If merge migration was created, review and apply it")
        print("   3. Run: alembic upgrade head")
    else:
        print("\n✅ No issues found or fixed")

    return True


def main():
    """Main entry point."""
    try:
        success = auto_fix_all()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during auto-fix: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
