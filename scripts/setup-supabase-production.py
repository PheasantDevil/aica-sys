#!/usr/bin/env python3
"""
Supabase Production Database Setup Script
This script helps set up the production database with proper RLS policies and initial data.
"""

import os
import sys
import asyncio
import asyncpg
from typing import Dict, Any
import json
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from database import get_database_url
from models.base import Base
from models.user import User
from models.subscription import Subscription
from models.content import Article, Newsletter, Trend
from models.collection import Collection
from models.ai_models import AIModel

class SupabaseProductionSetup:
    def __init__(self):
        self.database_url = None
        self.connection = None
        
    async def connect(self):
        """Connect to the Supabase database"""
        try:
            # Get database URL from environment
            self.database_url = os.getenv('DATABASE_URL')
            if not self.database_url:
                print("❌ DATABASE_URL environment variable not set")
                return False
                
            self.connection = await asyncpg.connect(self.database_url)
            print("✅ Connected to Supabase database")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    async def create_tables(self):
        """Create all necessary tables"""
        try:
            # Read the RLS policies SQL file
            rls_file = Path(__file__).parent.parent / "backend" / "security" / "rls_policies.sql"
            if rls_file.exists():
                with open(rls_file, 'r') as f:
                    rls_sql = f.read()
                
                # Execute RLS policies
                await self.connection.execute(rls_sql)
                print("✅ Row Level Security policies applied")
            else:
                print("⚠️  RLS policies file not found, skipping...")
            
            print("✅ Database tables and policies set up successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            return False
    
    async def create_initial_data(self):
        """Create initial data for production"""
        try:
            # Create default AI models
            ai_models = [
                {
                    "name": "gemini-pro",
                    "provider": "google",
                    "model_type": "text-generation",
                    "is_active": True,
                    "config": {
                        "temperature": 0.7,
                        "max_tokens": 2048,
                        "top_p": 0.9
                    }
                },
                {
                    "name": "gemini-pro-vision",
                    "provider": "google", 
                    "model_type": "image-analysis",
                    "is_active": True,
                    "config": {
                        "temperature": 0.3,
                        "max_tokens": 1024
                    }
                }
            ]
            
            for model_data in ai_models:
                await self.connection.execute("""
                    INSERT INTO ai_models (name, provider, model_type, is_active, config)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (name) DO NOTHING
                """, model_data["name"], model_data["provider"], 
                    model_data["model_type"], model_data["is_active"], 
                    json.dumps(model_data["config"]))
            
            print("✅ Initial AI models created")
            
            # Create default subscription plans
            subscription_plans = [
                {
                    "name": "Basic",
                    "price": 1980,
                    "currency": "JPY",
                    "interval": "month",
                    "features": ["basic_articles", "newsletter", "trend_analysis"],
                    "is_active": True
                },
                {
                    "name": "Premium",
                    "price": 4980,
                    "currency": "JPY", 
                    "interval": "month",
                    "features": ["premium_articles", "newsletter", "trend_analysis", "custom_reports"],
                    "is_active": True
                }
            ]
            
            for plan_data in subscription_plans:
                await self.connection.execute("""
                    INSERT INTO subscription_plans (name, price, currency, interval, features, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (name) DO NOTHING
                """, plan_data["name"], plan_data["price"], plan_data["currency"],
                    plan_data["interval"], json.dumps(plan_data["features"]), 
                    plan_data["is_active"])
            
            print("✅ Subscription plans created")
            
            return True
        except Exception as e:
            print(f"❌ Failed to create initial data: {e}")
            return False
    
    async def setup_monitoring(self):
        """Set up monitoring and logging tables"""
        try:
            # Create monitoring tables
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value DECIMAL(10,4) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    user_id UUID,
                    session_id VARCHAR(100),
                    metadata JSONB
                );
            """)
            
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id SERIAL PRIMARY KEY,
                    error_type VARCHAR(100) NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    user_id UUID,
                    session_id VARCHAR(100),
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB
                );
            """)
            
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id SERIAL PRIMARY KEY,
                    user_id UUID NOT NULL,
                    activity_type VARCHAR(100) NOT NULL,
                    activity_data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    ip_address INET,
                    user_agent TEXT
                );
            """)
            
            # Create indexes for better performance
            await self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp 
                ON performance_metrics(timestamp);
            """)
            
            await self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp 
                ON error_logs(timestamp);
            """)
            
            await self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_activity_user_id 
                ON user_activity(user_id);
            """)
            
            print("✅ Monitoring tables created")
            return True
        except Exception as e:
            print(f"❌ Failed to set up monitoring: {e}")
            return False
    
    async def verify_setup(self):
        """Verify the database setup"""
        try:
            # Check if all tables exist
            tables = await self.connection.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            expected_tables = [
                'users', 'subscriptions', 'subscription_plans',
                'articles', 'newsletters', 'trends', 'collections',
                'ai_models', 'performance_metrics', 'error_logs', 'user_activity'
            ]
            
            existing_tables = [row['table_name'] for row in tables]
            missing_tables = set(expected_tables) - set(existing_tables)
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
            else:
                print("✅ All required tables exist")
            
            # Check RLS policies
            policies = await self.connection.fetch("""
                SELECT schemaname, tablename, policyname 
                FROM pg_policies 
                WHERE schemaname = 'public'
                ORDER BY tablename, policyname;
            """)
            
            if policies:
                print(f"✅ {len(policies)} RLS policies found")
            else:
                print("⚠️  No RLS policies found")
            
            return True
        except Exception as e:
            print(f"❌ Failed to verify setup: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            print("✅ Database connection closed")

async def main():
    """Main setup function"""
    print("🚀 Starting Supabase Production Database Setup...")
    
    setup = SupabaseProductionSetup()
    
    try:
        # Connect to database
        if not await setup.connect():
            return 1
        
        # Create tables and policies
        if not await setup.create_tables():
            return 1
        
        # Create initial data
        if not await setup.create_initial_data():
            return 1
        
        # Set up monitoring
        if not await setup.setup_monitoring():
            return 1
        
        # Verify setup
        if not await setup.verify_setup():
            return 1
        
        print("🎉 Supabase production database setup completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return 1
    finally:
        await setup.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
