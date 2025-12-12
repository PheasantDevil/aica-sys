#!/usr/bin/env python3
"""Fix migration files that reference non-existent revisions."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from detect_migration_issues import detect_missing_revision_references


def get_available_revisions():
    """Get all available revision IDs from migration files."""
    backend_path = Path(__file__).parent.parent
    versions_path = backend_path / "alembic" / "versions"

    if not versions_path.exists():
        return set()

    revisions = set()
    for file_path in versions_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            match = re.search(r'revision\s*[:=]\s*["\']([a-f0-9]+)["\']', content)
            if match:
                revisions.add(match.group(1))
        except Exception:
            pass

    return revisions


def find_suitable_revision(missing_revision, available_revisions):
    """Find a suitable revision to replace the missing one."""
    # Common revision IDs that are likely to exist
    common_revisions = ["223a0ac841bb", "4741adeef488", "1cf2ab5a8998"]

    # Try common revisions first
    for rev in common_revisions:
        if rev in available_revisions:
            return rev

    # If no common revision found, return the first available (usually the base)
    if available_revisions:
        return sorted(available_revisions)[0]

    return None


def fix_missing_revision_reference(file_path, missing_revision, replacement_revision):
    """Fix a migration file that references a missing revision."""
    try:
        content = file_path.read_text(encoding="utf-8")

        # Replace down_revision
        content = re.sub(
            rf'down_revision\s*:\s*Union\[str,\s*Sequence\[str\],\s*None\]\s*=\s*["\']{missing_revision}["\']',
            f'down_revision: Union[str, Sequence[str], None] = "{replacement_revision}"',
            content,
        )
        content = re.sub(
            rf'down_revision\s*=\s*["\']{missing_revision}["\']',
            f'down_revision = "{replacement_revision}"',
            content,
        )

        # Also update in docstring if present
        content = re.sub(
            rf"Revises:\s*{missing_revision}",
            f"Revises: {replacement_revision}",
            content,
        )

        file_path.write_text(content, encoding="utf-8")
        print(f"✅ Fixed {file_path.name}: {missing_revision} -> {replacement_revision}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function to fix missing revision references."""
    print("🔍 Checking for missing revision references...")
    missing_refs = detect_missing_revision_references()

    if not missing_refs:
        print("✅ No missing revision references found")
        return

    print(f"❌ Found {len(missing_refs)} file(s) with missing revision references")

    available_revisions = get_available_revisions()
    if not available_revisions:
        print("❌ No available revisions found")
        sys.exit(1)

    fixed_count = 0
    backend_path = Path(__file__).parent.parent
    versions_path = backend_path / "alembic" / "versions"

    for file_name, missing_revision in missing_refs:
        file_path = versions_path / file_name
        replacement = find_suitable_revision(missing_revision, available_revisions)

        if not replacement:
            print(f"⚠️ Could not find suitable replacement for {file_name}")
            continue

        if fix_missing_revision_reference(file_path, missing_revision, replacement):
            fixed_count += 1

    if fixed_count > 0:
        print(f"\n✅ Fixed {fixed_count} file(s)")
    else:
        print("\n❌ Could not fix any files")
        sys.exit(1)


if __name__ == "__main__":
    main()

