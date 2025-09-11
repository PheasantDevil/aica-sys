#!/usr/bin/env python3
"""
Database restore script for AICA-SyS
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def restore_sqlite_database(backup_path: str, db_path: str):
    """Restore SQLite database from backup"""
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Copy backup to database location
        shutil.copy2(backup_path, db_path)
        print(f"✅ SQLite database restored from: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ SQLite restore failed: {e}")
        return False

def restore_postgresql_database(backup_path: str, connection_string: str):
    """Restore PostgreSQL database from backup"""
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    try:
        # Run psql to restore database
        cmd = [
            "psql",
            connection_string,
            "--file", backup_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL database restored from: {backup_path}")
            return True
        else:
            print(f"❌ PostgreSQL restore failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ psql not found. Please install PostgreSQL client tools.")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL restore failed: {e}")
        return False

def list_available_backups(backup_dir: str):
    """List available backup files"""
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return []
    
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.endswith(('.db', '.sql')):
            file_path = os.path.join(backup_dir, filename)
            file_size = os.path.getsize(file_path)
            file_time = os.path.getmtime(file_path)
            backup_files.append({
                'filename': filename,
                'path': file_path,
                'size': file_size,
                'time': file_time
            })
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: x['time'], reverse=True)
    
    return backup_files

def main():
    """Main restore function"""
    if len(sys.argv) < 2:
        print("Usage: python restore_database.py <backup_file>")
        print("Available backups:")
        
        backup_dir = os.getenv("BACKUP_DIR", "./backups")
        backups = list_available_backups(backup_dir)
        
        if backups:
            for i, backup in enumerate(backups):
                size_mb = backup['size'] / (1024 * 1024)
                print(f"  {i+1}. {backup['filename']} ({size_mb:.2f} MB)")
        else:
            print("  No backups found")
        
        sys.exit(1)
    
    backup_path = sys.argv[1]
    database_url = os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")
    
    print(f"🚀 Starting database restore...")
    print(f"Backup file: {backup_path}")
    print(f"Database URL: {database_url}")
    
    success = False
    
    if database_url.startswith("sqlite"):
        # SQLite restore
        db_path = database_url.replace("sqlite:///", "")
        success = restore_sqlite_database(backup_path, db_path)
    elif database_url.startswith("postgresql"):
        # PostgreSQL restore
        success = restore_postgresql_database(backup_path, database_url)
    else:
        print(f"❌ Unsupported database type: {database_url}")
        return False
    
    if success:
        print("🎉 Database restore completed successfully!")
    else:
        print("❌ Database restore failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
