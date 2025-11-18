#!/usr/bin/env python3
"""
AlembicマイグレーションをSQLに変換するスクリプト
使用方法: python3 scripts/convert_alembic_to_sql.py
"""

import re
from pathlib import Path

def convert_alembic_to_sql():
    """AlembicマイグレーションをSQLに変換"""
    alembic_file = Path("backend/alembic/versions/223a0ac841bb_initial_migration_with_automated_content.py")
    
    if not alembic_file.exists():
        print(f"❌ Alembic migration file not found: {alembic_file}")
        return None
    
    with open(alembic_file, 'r') as f:
        content = f.read()
    
    sql_statements = []
    sql_statements.append("-- Initial schema migration from Alembic")
    sql_statements.append("-- Converted from: 223a0ac841bb_initial_migration_with_automated_content.py")
    sql_statements.append("")
    
    # テーブル作成のパターンを抽出
    # これは簡易的な変換で、完全な変換にはAlembicの実行が必要
    sql_statements.append("-- Note: This is a template. Manual verification required.")
    sql_statements.append("-- Tables should be created via Alembic or verified in Supabase Dashboard")
    sql_statements.append("")
    sql_statements.append("-- Check if tables exist before creating")
    sql_statements.append("DO $$")
    sql_statements.append("BEGIN")
    sql_statements.append("  -- Add your CREATE TABLE statements here if needed")
    sql_statements.append("  -- Most tables should already exist in Supabase")
    sql_statements.append("END $$;")
    
    return "\n".join(sql_statements)

if __name__ == "__main__":
    sql = convert_alembic_to_sql()
    if sql:
        print(sql)

