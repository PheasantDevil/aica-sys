#!/usr/bin/env python3
"""
データベースURL確認スクリプト
使用方法: python3 scripts/check_database_url.py
"""

import os
import sys
from pathlib import Path

# backendディレクトリをパスに追加
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_database_url():
    """データベースURLを確認"""
    print("=" * 60)
    print("データベースURL確認")
    print("=" * 60)
    
    # 環境変数から取得
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # セキュリティのため、パスワード部分をマスク
        masked_url = mask_password(database_url)
        print(f"✅ DATABASE_URL is set")
        print(f"   URL (masked): {masked_url}")
        print(f"   Length: {len(database_url)} characters")
        
        # データベースタイプを判定
        if "sqlite" in database_url.lower():
            print("   Type: SQLite")
        elif "postgresql" in database_url.lower() or "postgres" in database_url.lower():
            print("   Type: PostgreSQL")
        else:
            print("   Type: Unknown")
    else:
        print("⚠️  DATABASE_URL is not set")
        print("   Using default SQLite database")
        
        # デフォルトのSQLiteパスを表示
        default_db_path = backend_dir / "aica_sys.db"
        print(f"   Default path: {default_db_path}")
        if default_db_path.exists():
            print(f"   ✅ Default database file exists")
        else:
            print(f"   ⚠️  Default database file does not exist")
    
    print()
    
    # 接続テスト
    print("=" * 60)
    print("データベース接続テスト")
    print("=" * 60)
    
    try:
        from database import DATABASE_URL as db_url
        from database import SessionLocal, engine
        
        print(f"Attempting to connect to: {mask_password(str(db_url))}")
        
        from sqlalchemy import text
        
        db = SessionLocal()
        # 簡単なクエリを実行
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def mask_password(url: str) -> str:
    """URL内のパスワード部分をマスク"""
    if not url:
        return url
    
    # postgresql://user:password@host の形式をマスク
    if "@" in url and "://" in url:
        parts = url.split("@")
        if len(parts) == 2:
            auth_part = parts[0]
            if ":" in auth_part:
                protocol_user = auth_part.split(":")[0]
                masked = f"{protocol_user}:***@{parts[1]}"
                return masked
    
    return url

if __name__ == "__main__":
    success = check_database_url()
    sys.exit(0 if success else 1)

