"""
Database initialization script for AICA-SyS
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.user import User
from models.content import Article, Newsletter, Trend
from models.collection import CollectionJob, AnalysisResult
from models.subscription import Subscription

def create_database_tables(database_url: str):
    """Create all database tables"""
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    return engine

def create_database_indexes(engine):
    """Create database indexes for better performance"""
    with engine.connect() as conn:
        # User table indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)"))
        
        # Article table indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)"))
        
        # Newsletter table indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_newsletters_slug ON newsletters(slug)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_newsletters_published_at ON newsletters(published_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_newsletters_status ON newsletters(status)"))
        
        # Trend table indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_published_at ON trends(published_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_category ON trends(category)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_trends_status ON trends(status)"))
        
        # Collection job indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_collection_jobs_status ON collection_jobs(status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_collection_jobs_created_at ON collection_jobs(created_at)"))
        
        # Analysis result indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analysis_results_job_id ON analysis_results(job_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at)"))
        
        # Subscription indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_subscriptions_created_at ON subscriptions(created_at)"))
        
        conn.commit()
        print("✅ Database indexes created successfully")

def create_sample_data(engine):
    """Create sample data for development"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Check if data already exists
        if session.query(User).first():
            print("ℹ️  Sample data already exists, skipping...")
            return
        
        # Create sample users
        sample_users = [
            User(
                email="admin@aica-sys.com",
                name="Admin User",
                subscription_status="premium",
                is_active=True
            ),
            User(
                email="user@example.com",
                name="Test User",
                subscription_status="free",
                is_active=True
            )
        ]
        
        for user in sample_users:
            session.add(user)
        
        session.commit()
        print("✅ Sample data created successfully")

def setup_database_optimizations(engine):
    """Setup database optimizations for PostgreSQL"""
    if not engine.url.drivername.startswith('postgresql'):
        print("ℹ️  Skipping PostgreSQL optimizations (not using PostgreSQL)")
        return
    
    with engine.connect() as conn:
        # Enable extensions
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\""))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"btree_gin\""))
        
        # Set connection parameters
        conn.execute(text("SET default_statistics_target = 100"))
        conn.execute(text("SET random_page_cost = 1.1"))
        conn.execute(text("SET effective_cache_size = '1GB'"))
        
        conn.commit()
        print("✅ PostgreSQL optimizations applied successfully")

def main():
    """Main initialization function"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")
    
    print(f"🚀 Initializing database: {database_url}")
    
    try:
        # Create tables
        engine = create_database_tables(database_url)
        
        # Create indexes
        create_database_indexes(engine)
        
        # Setup optimizations
        setup_database_optimizations(engine)
        
        # Create sample data (only for development)
        if os.getenv("ENVIRONMENT", "development") == "development":
            create_sample_data(engine)
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
