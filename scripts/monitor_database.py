#!/usr/bin/env python3
"""
Database monitoring script for AICA-SyS
"""

import os
import sys
import time
import psutil
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def check_database_connection(database_url: str):
    """Check database connection"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Database connection successful"
    except SQLAlchemyError as e:
        return False, f"Database connection failed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def get_database_stats(database_url: str):
    """Get database statistics"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            stats = {}
            
            if database_url.startswith("sqlite"):
                # SQLite specific stats
                result = conn.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
                stats['table_count'] = result.scalar()
                
                result = conn.execute(text("PRAGMA page_count"))
                stats['page_count'] = result.scalar()
                
                result = conn.execute(text("PRAGMA page_size"))
                stats['page_size'] = result.scalar()
                
                stats['database_size'] = stats['page_count'] * stats['page_size']
                
            elif database_url.startswith("postgresql"):
                # PostgreSQL specific stats
                result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                stats['table_count'] = result.scalar()
                
                result = conn.execute(text("SELECT pg_database_size(current_database())"))
                stats['database_size'] = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM pg_stat_activity"))
                stats['active_connections'] = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'"))
                stats['active_queries'] = result.scalar()
            
            return True, stats
    except Exception as e:
        return False, f"Failed to get database stats: {e}"

def get_table_sizes(database_url: str):
    """Get table sizes"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            if database_url.startswith("sqlite"):
                # SQLite table sizes
                result = conn.execute(text("""
                    SELECT name, 
                           (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as row_count
                    FROM sqlite_master m 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """))
                return True, result.fetchall()
            elif database_url.startswith("postgresql"):
                # PostgreSQL table sizes
                result = conn.execute(text("""
                    SELECT schemaname, tablename, 
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                           pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """))
                return True, result.fetchall()
    except Exception as e:
        return False, f"Failed to get table sizes: {e}"

def check_database_health(database_url: str):
    """Comprehensive database health check"""
    print("🔍 Checking database health...")
    
    # Connection check
    success, message = check_database_connection(database_url)
    if not success:
        print(f"❌ {message}")
        return False
    print(f"✅ {message}")
    
    # Database stats
    success, stats = get_database_stats(database_url)
    if success:
        print("\n📊 Database Statistics:")
        for key, value in stats.items():
            if key == 'database_size':
                size_mb = value / (1024 * 1024)
                print(f"  {key}: {size_mb:.2f} MB")
            else:
                print(f"  {key}: {value}")
    else:
        print(f"⚠️  {stats}")
    
    # Table sizes
    success, table_sizes = get_table_sizes(database_url)
    if success:
        print("\n📋 Table Sizes:")
        for row in table_sizes:
            print(f"  {row[0]}: {row[1] if len(row) > 1 else 'N/A'}")
    else:
        print(f"⚠️  {table_sizes}")
    
    return True

def monitor_database_performance(database_url: str, duration: int = 60):
    """Monitor database performance for specified duration"""
    print(f"📈 Monitoring database performance for {duration} seconds...")
    
    start_time = time.time()
    query_times = []
    
    try:
        engine = create_engine(database_url)
        
        while time.time() - start_time < duration:
            query_start = time.time()
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            query_time = time.time() - query_start
            query_times.append(query_time)
            
            time.sleep(1)  # Check every second
        
        if query_times:
            avg_time = sum(query_times) / len(query_times)
            max_time = max(query_times)
            min_time = min(query_times)
            
            print(f"\n📊 Performance Results:")
            print(f"  Average query time: {avg_time:.4f}s")
            print(f"  Max query time: {max_time:.4f}s")
            print(f"  Min query time: {min_time:.4f}s")
            print(f"  Total queries: {len(query_times)}")
            
            if avg_time > 0.1:  # More than 100ms average
                print("⚠️  Warning: Average query time is high")
            else:
                print("✅ Database performance is good")
    
    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}")

def main():
    """Main monitoring function"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")
    
    print(f"🚀 Starting database monitoring...")
    print(f"Database URL: {database_url}")
    
    # Health check
    if not check_database_health(database_url):
        sys.exit(1)
    
    # Performance monitoring (if requested)
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor_database_performance(database_url, duration)
    
    print("\n🎉 Database monitoring completed!")

if __name__ == "__main__":
    main()
