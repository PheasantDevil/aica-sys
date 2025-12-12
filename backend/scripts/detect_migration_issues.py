#!/usr/bin/env python3
"""Detect migration issues like duplicate revision IDs and multiple heads."""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

try:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False


def detect_duplicate_revisions():
    """Detect duplicate revision IDs in migration files."""
    backend_path = Path(__file__).parent.parent
    versions_path = backend_path / "alembic" / "versions"

    if not versions_path.exists():
        print("❌ Migration versions directory not found")
        return []

    revision_to_files = defaultdict(list)

    # Scan all migration files
    for file_path in versions_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            # Extract revision ID - handle both 'revision: str = "..."' and 'revision = "..."'
            match = re.search(r'revision\s*[:=]\s*["\']([a-f0-9]+)["\']', content)
            if match:
                revision_id = match.group(1)
                revision_to_files[revision_id].append(file_path.name)
            else:
                # Try alternative pattern
                match = re.search(r"Revision ID:\s*([a-f0-9]+)", content)
                if match:
                    revision_id = match.group(1)
                    revision_to_files[revision_id].append(file_path.name)
        except Exception as e:
            print(f"⚠️ Error reading {file_path.name}: {e}")

    duplicates = {
        rev: files for rev, files in revision_to_files.items() if len(files) > 1
    }

    return duplicates


def detect_missing_revision_references():
    """Detect migration files that reference non-existent revisions."""
    backend_path = Path(__file__).parent.parent
    versions_path = backend_path / "alembic" / "versions"

    if not versions_path.exists():
        print("❌ Migration versions directory not found")
        return []

    existing_revisions = set()
    down_revision_map = {}  # file_name -> down_revision

    for file_path in versions_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            # Extract revision ID
            match = re.search(r'revision\s*[:=]\s*["\']([a-f0-9]+)["\']', content)
            if match:
                existing_revisions.add(match.group(1))

            # Extract down_revision
            down_match = re.search(
                r'down_revision\s*[:=]\s*["\']([a-f0-9]+)["\']', content
            )
            if down_match:
                down_revision_map[file_path.name] = down_match.group(1)
        except (OSError, UnicodeDecodeError) as e:
            print(f"⚠️ Error reading {file_path.name}: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error reading {file_path.name}: {e}")

    return [
        (fname, down_rev)
        for fname, down_rev in down_revision_map.items()
        if down_rev not in existing_revisions
    ]


def detect_multiple_heads():
    """Detect multiple head revisions using Alembic."""
    if not ALEMBIC_AVAILABLE:
        return []

    backend_path = Path(__file__).parent.parent
    alembic_cfg = Config(str(backend_path / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_path / "alembic"))

    try:
        script = ScriptDirectory.from_config(alembic_cfg)
        heads = script.get_revisions("heads")

        if len(heads) > 1:
            return [str(head.revision) for head in heads]
        return []
    except Exception as e:
        print(f"⚠️ Error detecting heads: {e}")
        return []


def main():
    """Main function to detect all migration issues."""
    issues_found = False

    print("🔍 Checking for duplicate revision IDs...")
    duplicates = detect_duplicate_revisions()

    if duplicates:
        issues_found = True
        print("❌ Found duplicate revision IDs:")
        for revision_id, files in duplicates.items():
            print(f"   Revision {revision_id} appears in:")
            for file in files:
                print(f"     - {file}")
    else:
        print("✅ No duplicate revision IDs found")

    print("\n🔍 Checking for missing revision references...")
    missing_refs = detect_missing_revision_references()

    if missing_refs:
        issues_found = True
        print("❌ Found migration files referencing non-existent revisions:")
        for file_name, missing_revision in missing_refs:
            print(f"   {file_name} references missing revision: {missing_revision}")
    else:
        print("✅ No missing revision references found")

    print("\n🔍 Checking for multiple head revisions...")
    if not ALEMBIC_AVAILABLE:
        print("⚠️ Alembic not available, skipping head detection")
    else:
        multiple_heads = detect_multiple_heads()

        if multiple_heads:
            issues_found = True
            print(f"❌ Found {len(multiple_heads)} head revisions:")
            for head in multiple_heads:
                print(f"   - {head}")
        else:
            print("✅ Single head revision (no branching)")

    if issues_found:
        print("\n⚠️ Migration issues detected!")
        sys.exit(1)
    else:
        print("\n✅ No migration issues detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
