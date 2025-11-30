#!/usr/bin/env python3
"""Fix duplicate revision IDs by renaming one of them."""
import re
import secrets
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))


def generate_revision_id():
    """Generate a new unique revision ID."""
    return secrets.token_hex(6)


def find_duplicate_revisions():
    """Find duplicate revision IDs and return mapping."""
    backend_path = Path(__file__).parent.parent
    versions_path = backend_path / "alembic" / "versions"
    
    if not versions_path.exists():
        return {}
    
    revision_to_files = defaultdict(list)
    
    for file_path in versions_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8")
            match = re.search(r'revision\s*[:=]\s*["\']([a-f0-9]+)["\']', content)
            if match:
                revision_id = match.group(1)
                revision_to_files[revision_id].append(file_path)
            else:
                # Try alternative pattern
                match = re.search(r'Revision ID:\s*([a-f0-9]+)', content)
                if match:
                    revision_id = match.group(1)
                    revision_to_files[revision_id].append(file_path)
        except Exception as e:
            print(f"⚠️ Error reading {file_path.name}: {e}")
    
    duplicates = {
        rev: files for rev, files in revision_to_files.items() if len(files) > 1
    }
    
    return duplicates


def fix_duplicate_revision(duplicate_files, keep_first=True):
    """Fix duplicate revision by renaming one file's revision ID."""
    if len(duplicate_files) < 2:
        return None
    
    # Sort files by modification time (keep the older one)
    files_sorted = sorted(duplicate_files, key=lambda p: p.stat().st_mtime)
    
    if keep_first:
        file_to_fix = files_sorted[1]  # Fix the newer one
        reference_file = files_sorted[0]  # Keep the older one
    else:
        file_to_fix = files_sorted[0]  # Fix the older one
        reference_file = files_sorted[1]  # Keep the newer one
    
    try:
        content = file_to_fix.read_text(encoding="utf-8")
        
        # Extract current revision ID - try multiple patterns
        match = re.search(r'revision\s*[:=]\s*["\']([a-f0-9]+)["\']', content)
        if not match:
            # Try alternative pattern
            match = re.search(r'Revision ID:\s*([a-f0-9]+)', content)
        if not match:
            print(f"⚠️ Could not find revision ID in {file_to_fix.name}")
            return None
        
        old_revision = match.group(1)
        new_revision = generate_revision_id()
        
        # Replace revision ID in code (revision: str = "..." or revision = "...")
        content = re.sub(
            rf'revision\s*:\s*str\s*=\s*["\']{old_revision}["\']',
            f'revision: str = "{new_revision}"',
            content
        )
        content = re.sub(
            rf'revision\s*=\s*["\']{old_revision}["\']',
            f'revision = "{new_revision}"',
            content
        )
        
        # Also update in the docstring if present
        content = re.sub(
            rf'Revision ID:\s*{old_revision}',
            f'Revision ID: {new_revision}',
            content
        )
        
        file_to_fix.write_text(content, encoding="utf-8")
        
        print(f"✅ Fixed {file_to_fix.name}: {old_revision} -> {new_revision}")
        return new_revision
    
    except Exception as e:
        print(f"❌ Error fixing {file_to_fix.name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to fix duplicate revisions."""
    print("🔍 Searching for duplicate revision IDs...")
    duplicates = find_duplicate_revisions()
    
    if not duplicates:
        print("✅ No duplicate revision IDs found")
        return
    
    print(f"❌ Found {len(duplicates)} duplicate revision ID(s)")
    
    for revision_id, files in duplicates.items():
        print(f"\n🔧 Fixing duplicate revision {revision_id}...")
        print(f"   Found in {len(files)} files:")
        for f in files:
            print(f"     - {f.name}")
        
        new_revision = fix_duplicate_revision(files, keep_first=True)
        if new_revision:
            print(f"   ✅ Renamed to {new_revision}")
        else:
            print(f"   ❌ Failed to fix")
            sys.exit(1)
    
    print("\n✅ All duplicate revisions fixed")
    print("⚠️  Note: You may need to create a merge migration if these were separate branches")


if __name__ == "__main__":
    main()

