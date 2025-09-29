"""
Database Configuration and Connection Pool Settings
Optimized for Phase 7-1: Database optimization
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aica_sys")

# Connection pool configuration
POOL_CONFIG = {
    "poolclass": QueuePool,
    "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),          # Base connection pool size
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),    # Maximum additional connections
    "pool_pre_ping": True,                                      # Connection health check
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),  # Connection recycle time (1 hour)
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),    # Connection timeout
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",   # SQL query logging
}

# Create optimized engine
engine: Engine = create_engine(DATABASE_URL, **POOL_CONFIG)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_engine() -> Engine:
    """Get database engine"""
    return engine

def get_session_factory():
    """Get session factory"""
    return SessionLocal

# Database optimization settings
OPTIMIZATION_SETTINGS = {
    "autovacuum_analyze_scale_factor": {
        "articles": 0.1,
        "newsletters": 0.1,
        "trends": 0.1,
        "subscriptions": 0.1,
        "audit_events": 0.05,  # More frequent analysis for audit logs
        "users": 0.1,
    },
    "autovacuum_vacuum_scale_factor": {
        "articles": 0.2,
        "newsletters": 0.2,
        "trends": 0.2,
        "subscriptions": 0.2,
        "audit_events": 0.1,   # More frequent vacuum for audit logs
        "users": 0.2,
    },
    "work_mem": "256MB",           # Working memory for queries
    "maintenance_work_mem": "1GB", # Memory for maintenance operations
    "shared_buffers": "256MB",     # Shared buffer size
    "effective_cache_size": "1GB", # Effective cache size
}

# Query optimization hints
QUERY_HINTS = {
    "enable_seqscan": False,       # Disable sequential scans when possible
    "enable_indexscan": True,      # Enable index scans
    "enable_bitmapscan": True,     # Enable bitmap scans
    "enable_hashjoin": True,       # Enable hash joins
    "enable_mergejoin": True,      # Enable merge joins
    "enable_nestloop": True,       # Enable nested loop joins
}

def apply_optimization_settings():
    """Apply database optimization settings"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Apply work memory settings
        conn.execute(text(f"SET work_mem = '{OPTIMIZATION_SETTINGS['work_mem']}'"))
        conn.execute(text(f"SET maintenance_work_mem = '{OPTIMIZATION_SETTINGS['maintenance_work_mem']}'"))
        conn.execute(text(f"SET shared_buffers = '{OPTIMIZATION_SETTINGS['shared_buffers']}'"))
        conn.execute(text(f"SET effective_cache_size = '{OPTIMIZATION_SETTINGS['effective_cache_size']}'"))
        
        # Apply query hints
        for hint, value in QUERY_HINTS.items():
            conn.execute(text(f"SET {hint} = {str(value).lower()}"))
        
        conn.commit()

def get_connection_info():
    """Get connection pool information"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid(),
    }

# Health check function
def check_database_health() -> dict:
    """Check database health and performance"""
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute("SELECT 1").scalar()
            
            # Get connection pool info
            pool_info = get_connection_info()
            
            # Get database size
            size_result = conn.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """).fetchone()
            
            return {
                "status": "healthy",
                "connected": result == 1,
                "pool_info": pool_info,
                "database_size": size_result[0] if size_result else "Unknown",
                "timestamp": "2024-01-01T00:00:00Z"  # This would be actual timestamp
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"  # This would be actual timestamp
        }
