#!/usr/bin/env python3
"""
SQLite Database Optimization Script for AICA-SyS
Phase 7-1: Database optimization and index design for SQLite
"""

import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")
SQLITE_DB_PATH = DATABASE_URL.replace("sqlite:///", "")

# Check if database exists in backend directory
if not os.path.exists(SQLITE_DB_PATH):
    backend_db_path = "backend/aica_sys.db"
    if os.path.exists(backend_db_path):
        SQLITE_DB_PATH = backend_db_path
        print(f"Using database from: {SQLITE_DB_PATH}")
    else:
        print(f"Database not found at {SQLITE_DB_PATH} or {backend_db_path}")
        exit(1)
else:
    print(f"Using database from: {SQLITE_DB_PATH}")

# Verify database has tables
import sqlite3

try:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Found {len(tables)} tables: {[table[0] for table in tables]}")
    conn.close()
except Exception as e:
    print(f"Error verifying database: {e}")
    exit(1)

# Force use of backend database if it has more tables
backend_db_path = "backend/aica_sys.db"
if os.path.exists(backend_db_path):
    conn = sqlite3.connect(backend_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    backend_tables = cursor.fetchall()
    conn.close()
    
    if len(backend_tables) > len(tables):
        SQLITE_DB_PATH = backend_db_path
        print(f"Switching to backend database with {len(backend_tables)} tables: {[table[0] for table in backend_tables]}")

class SQLiteOptimizer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def get_connection(self):
        """Get SQLite connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_sql(self, sql: str, params: tuple = None) -> bool:
        """Execute SQL using SQLite"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                conn.commit()
            logger.info(f"Successfully executed: {sql[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return False
    
    def analyze_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Analyze table statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # Get table size (approximate)
                cursor.execute(f"SELECT COUNT(*) * 100 FROM {table_name}")  # Rough estimate
                estimated_size = cursor.fetchone()[0]
                
                return {
                    "table_name": table_name,
                    "row_count": row_count,
                    "column_count": len(columns),
                    "estimated_size_bytes": estimated_size,
                    "columns": [col[1] for col in columns]
                }
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return {"table_name": table_name, "error": str(e)}
    
    def get_existing_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get existing indexes for a table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                
                result = []
                for index in indexes:
                    index_name = index[1]
                    cursor.execute(f"PRAGMA index_info({index_name})")
                    columns = cursor.fetchall()
                    result.append({
                        "name": index_name,
                        "columns": [col[2] for col in columns]
                    })
                
                return result
        except Exception as e:
            logger.error(f"Error getting indexes for {table_name}: {e}")
            return []
    
    def create_article_indexes(self) -> bool:
        """Create indexes for articles table"""
        indexes = [
            # Composite indexes
            "CREATE INDEX IF NOT EXISTS idx_articles_published_premium ON articles(published_at DESC, is_premium)",
            "CREATE INDEX IF NOT EXISTS idx_articles_author_published ON articles(author, published_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_articles_popularity ON articles(views DESC, likes DESC, published_at DESC)",
            
            # Partial indexes (SQLite supports WHERE clauses)
            "CREATE INDEX IF NOT EXISTS idx_articles_premium ON articles(published_at DESC) WHERE is_premium = 1",
            
            # Single column indexes
            "CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_articles_is_premium ON articles(is_premium)",
            "CREATE INDEX IF NOT EXISTS idx_articles_views ON articles(views DESC)",
            "CREATE INDEX IF NOT EXISTS idx_articles_likes ON articles(likes DESC)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for articles table")
        return success_count == len(indexes)
    
    def create_newsletter_indexes(self) -> bool:
        """Create indexes for newsletters table"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_newsletters_published ON newsletters(published_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_newsletters_subscribers ON newsletters(subscribers DESC, published_at DESC)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for newsletters table")
        return success_count == len(indexes)
    
    def create_trend_indexes(self) -> bool:
        """Create indexes for trends table"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_trends_category_created ON trends(category, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_trends_impact_created ON trends(impact, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_trends_category_impact ON trends(category, impact, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_trends_created_at ON trends(created_at DESC)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for trends table")
        return success_count == len(indexes)
    
    def create_subscription_indexes(self) -> bool:
        """Create indexes for subscriptions table"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions(user_id, status, current_period_end)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_status ON subscriptions(plan, status, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_expiring ON subscriptions(current_period_end, status)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, plan) WHERE status = 'active'",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for subscriptions table")
        return success_count == len(indexes)
    
    def create_audit_indexes(self) -> bool:
        """Create indexes for audit_events table"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_audit_events_user_timestamp ON audit_events(user_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_events_type_timestamp ON audit_events(event_type, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_events_resource_timestamp ON audit_events(resource_type, resource_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_events_session_timestamp ON audit_events(session_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_events_result_timestamp ON audit_events(result, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp DESC)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for audit_events table")
        return success_count == len(indexes)
    
    def create_user_indexes(self) -> bool:
        """Create indexes for users table"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(email) WHERE is_active = 1",
            "CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for users table")
        return success_count == len(indexes)
    
    def optimize_sqlite_settings(self) -> bool:
        """Optimize SQLite settings for better performance"""
        settings = [
            "PRAGMA journal_mode = WAL",  # Write-Ahead Logging
            "PRAGMA synchronous = NORMAL",  # Balance between safety and speed
            "PRAGMA cache_size = 10000",  # Increase cache size
            "PRAGMA temp_store = MEMORY",  # Store temp tables in memory
            "PRAGMA mmap_size = 268435456",  # 256MB memory mapping
            "PRAGMA optimize",  # Optimize the database
        ]
        
        success_count = 0
        for setting in settings:
            if self.execute_sql(setting):
                success_count += 1
        
        logger.info(f"Applied {success_count}/{len(settings)} SQLite optimizations")
        return success_count == len(settings)
    
    def analyze_database(self) -> bool:
        """Analyze database for query optimization"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("ANALYZE")
            logger.info("Database analysis completed")
            return True
        except Exception as e:
            logger.error(f"Error analyzing database: {e}")
            return False
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate performance report after optimization"""
        tables = ["articles", "newsletters", "trends", "subscriptions", "audit_events", "users"]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "database_type": "SQLite",
            "database_path": self.db_path,
            "tables": {},
            "total_indexes": 0,
        }
        
        for table in tables:
            stats = self.analyze_table_stats(table)
            indexes = self.get_existing_indexes(table)
            
            report["tables"][table] = {
                "stats": stats,
                "indexes": indexes,
                "index_count": len(indexes)
            }
            report["total_indexes"] += len(indexes)
        
        return report
    
    def run_optimization(self) -> bool:
        """Run complete database optimization"""
        logger.info("Starting SQLite database optimization...")
        start_time = time.time()
        
        # Create indexes for all tables
        results = []
        results.append(self.create_article_indexes())
        results.append(self.create_newsletter_indexes())
        results.append(self.create_trend_indexes())
        results.append(self.create_subscription_indexes())
        results.append(self.create_audit_indexes())
        results.append(self.create_user_indexes())
        
        # Optimize SQLite settings
        results.append(self.optimize_sqlite_settings())
        
        # Analyze database
        results.append(self.analyze_database())
        
        # Generate report
        report = self.generate_performance_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_count = sum(results)
        total_operations = len(results)
        
        logger.info(f"SQLite database optimization completed in {duration:.2f} seconds")
        logger.info(f"Successfully completed {success_count}/{total_operations} operations")
        
        # Save report
        import json
        with open("docs/sqlite-optimization-report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        return success_count == total_operations

def main():
    """Main function"""
    optimizer = SQLiteOptimizer(SQLITE_DB_PATH)
    
    try:
        success = optimizer.run_optimization()
        if success:
            logger.info("SQLite database optimization completed successfully!")
            return 0
        else:
            logger.error("SQLite database optimization completed with errors!")
            return 1
    except Exception as e:
        logger.error(f"SQLite database optimization failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
