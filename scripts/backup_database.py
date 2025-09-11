#!/usr/bin/env python3
"""
Database backup script for AICA-SyS
"""

import os
import sys
import subprocess
import datetime
import shutil
from pathlib import Path

def backup_sqlite_database(db_path: str, backup_dir: str):
    """Backup SQLite database"""
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"aica_sys_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy database file
        shutil.copy2(db_path, backup_path)
        print(f"✅ SQLite backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ SQLite backup failed: {e}")
        return False

def backup_postgresql_database(connection_string: str, backup_dir: str):
    """Backup PostgreSQL database using pg_dump"""
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"aica_sys_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Run pg_dump
        cmd = [
            "pg_dump",
            connection_string,
            "--verbose",
            "--clean",
            "--if-exists",
            "--create",
            "--format=plain",
            "--file", backup_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL backup created: {backup_path}")
            return True
        else:
            print(f"❌ PostgreSQL backup failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ pg_dump not found. Please install PostgreSQL client tools.")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL backup failed: {e}")
        return False

def cleanup_old_backups(backup_dir: str, keep_days: int = 30):
    """Clean up old backup files"""
    if not os.path.exists(backup_dir):
        return
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
    
    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        
        if os.path.isfile(file_path):
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_time < cutoff_date:
                try:
                    os.remove(file_path)
                    print(f"🗑️  Removed old backup: {filename}")
                except Exception as e:
                    print(f"⚠️  Failed to remove old backup {filename}: {e}")

def main():
    """Main backup function"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")
    backup_dir = os.getenv("BACKUP_DIR", "./backups")
    keep_days = int(os.getenv("BACKUP_KEEP_DAYS", "30"))
    
    print(f"🚀 Starting database backup...")
    print(f"Database URL: {database_url}")
    print(f"Backup directory: {backup_dir}")
    
    success = False
    
    if database_url.startswith("sqlite"):
        # SQLite backup
        db_path = database_url.replace("sqlite:///", "")
        success = backup_sqlite_database(db_path, backup_dir)
    elif database_url.startswith("postgresql"):
        # PostgreSQL backup
        success = backup_postgresql_database(database_url, backup_dir)
    else:
        print(f"❌ Unsupported database type: {database_url}")
        return False
    
    if success:
        # Clean up old backups
        cleanup_old_backups(backup_dir, keep_days)
        print("🎉 Database backup completed successfully!")
    else:
        print("❌ Database backup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
