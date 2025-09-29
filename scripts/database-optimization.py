#!/usr/bin/env python3
"""
Database Optimization Script for AICA-SyS
Phase 7-1: Database optimization and index design
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aica_sys")

class DatabaseOptimizer:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
    async def create_connection(self):
        """Create asyncpg connection for raw SQL execution"""
        return await asyncpg.connect(self.database_url.replace("postgresql://", "postgresql://"))
    
    async def close_connection(self, conn):
        """Close asyncpg connection"""
        await conn.close()
    
    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> bool:
        """Execute SQL using SQLAlchemy"""
        try:
            with self.engine.connect() as conn:
                if params:
                    conn.execute(text(sql), params)
                else:
                    conn.execute(text(sql))
                conn.commit()
            logger.info(f"Successfully executed: {sql[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return False
    
    async def execute_async_sql(self, conn, sql: str) -> bool:
        """Execute SQL using asyncpg"""
        try:
            await conn.execute(sql)
            logger.info(f"Successfully executed: {sql[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return False
    
    def analyze_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Analyze table statistics"""
        try:
            with self.Session() as session:
                # Get table size
                size_query = text("""
                    SELECT 
                        pg_size_pretty(pg_total_relation_size(:table_name)) as total_size,
                        pg_size_pretty(pg_relation_size(:table_name)) as table_size,
                        pg_size_pretty(pg_total_relation_size(:table_name) - pg_relation_size(:table_name)) as index_size
                """)
                size_result = session.execute(size_query, {"table_name": table_name}).fetchone()
                
                # Get row count
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                row_count = session.execute(count_query).scalar()
                
                return {
                    "table_name": table_name,
                    "total_size": size_result[0] if size_result else "Unknown",
                    "table_size": size_result[1] if size_result else "Unknown",
                    "index_size": size_result[2] if size_result else "Unknown",
                    "row_count": row_count
                }
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return {"table_name": table_name, "error": str(e)}
    
    def get_existing_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get existing indexes for a table"""
        try:
            with self.Session() as session:
                query = text("""
                    SELECT 
                        indexname,
                        indexdef
                    FROM pg_indexes 
                    WHERE tablename = :table_name
                    ORDER BY indexname
                """)
                result = session.execute(query, {"table_name": table_name}).fetchall()
                return [{"name": row[0], "definition": row[1]} for row in result]
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
            
            # GIN indexes for JSON tags
            "CREATE INDEX IF NOT EXISTS idx_articles_tags_gin ON articles USING GIN(tags)",
            
            # Partial indexes
            "CREATE INDEX IF NOT EXISTS idx_articles_premium ON articles(published_at DESC) WHERE is_premium = true",
            
            # Full-text search indexes
            "CREATE INDEX IF NOT EXISTS idx_articles_title_gin ON articles USING GIN(to_tsvector('english', title))",
            "CREATE INDEX IF NOT EXISTS idx_articles_content_gin ON articles USING GIN(to_tsvector('english', content))",
            "CREATE INDEX IF NOT EXISTS idx_articles_summary_gin ON articles USING GIN(to_tsvector('english', summary))",
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
            "CREATE INDEX IF NOT EXISTS idx_newsletters_title_gin ON newsletters USING GIN(to_tsvector('english', title))",
            "CREATE INDEX IF NOT EXISTS idx_newsletters_content_gin ON newsletters USING GIN(to_tsvector('english', content))",
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
            "CREATE INDEX IF NOT EXISTS idx_trends_title_gin ON trends USING GIN(to_tsvector('english', title))",
            "CREATE INDEX IF NOT EXISTS idx_trends_description_gin ON trends USING GIN(to_tsvector('english', description))",
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
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(email) WHERE is_active = true",
            "CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status, created_at DESC)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            if self.execute_sql(index_sql):
                success_count += 1
        
        logger.info(f"Created {success_count}/{len(indexes)} indexes for users table")
        return success_count == len(indexes)
    
    def optimize_autovacuum_settings(self) -> bool:
        """Optimize autovacuum settings for better performance"""
        tables = ["articles", "newsletters", "trends", "subscriptions", "audit_events", "users"]
        
        success_count = 0
        for table in tables:
            sql = f"ALTER TABLE {table} SET (autovacuum_analyze_scale_factor = 0.1)"
            if self.execute_sql(sql):
                success_count += 1
        
        # Special setting for audit_events (more frequent analysis)
        if self.execute_sql("ALTER TABLE audit_events SET (autovacuum_analyze_scale_factor = 0.05)"):
            success_count += 1
        
        logger.info(f"Optimized autovacuum settings for {success_count}/{len(tables) + 1} tables")
        return success_count == len(tables) + 1
    
    def update_table_statistics(self) -> bool:
        """Update table statistics for better query planning"""
        tables = ["articles", "newsletters", "trends", "subscriptions", "audit_events", "users"]
        
        success_count = 0
        for table in tables:
            sql = f"ANALYZE {table}"
            if self.execute_sql(sql):
                success_count += 1
        
        logger.info(f"Updated statistics for {success_count}/{len(tables)} tables")
        return success_count == len(tables)
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate performance report after optimization"""
        tables = ["articles", "newsletters", "trends", "subscriptions", "audit_events", "users"]
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "tables": {},
            "total_indexes": 0,
            "total_size": "0 MB"
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
    
    async def run_optimization(self) -> bool:
        """Run complete database optimization"""
        logger.info("Starting database optimization...")
        start_time = time.time()
        
        # Create indexes for all tables
        results = []
        results.append(self.create_article_indexes())
        results.append(self.create_newsletter_indexes())
        results.append(self.create_trend_indexes())
        results.append(self.create_subscription_indexes())
        results.append(self.create_audit_indexes())
        results.append(self.create_user_indexes())
        
        # Optimize autovacuum settings
        results.append(self.optimize_autovacuum_settings())
        
        # Update statistics
        results.append(self.update_table_statistics())
        
        # Generate report
        report = self.generate_performance_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_count = sum(results)
        total_operations = len(results)
        
        logger.info(f"Database optimization completed in {duration:.2f} seconds")
        logger.info(f"Successfully completed {success_count}/{total_operations} operations")
        
        # Save report
        import json
        with open("docs/database-optimization-report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        return success_count == total_operations

async def main():
    """Main function"""
    optimizer = DatabaseOptimizer(DATABASE_URL)
    
    try:
        success = await optimizer.run_optimization()
        if success:
            logger.info("Database optimization completed successfully!")
            return 0
        else:
            logger.error("Database optimization completed with errors!")
            return 1
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
