import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()

    def _setup_engine(self):
        """Setup database engine with optimized settings"""
        engine_kwargs = {
            "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true",
            "future": True,
        }

        # Configure connection pool based on database type
        if self.database_url.startswith("sqlite"):
            # SQLite configuration
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 20,
                },
                "pool_pre_ping": True,
            })
        else:
            # PostgreSQL/MySQL configuration
            engine_kwargs.update({
                "poolclass": QueuePool,
                "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
                "pool_pre_ping": True,
                "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
                "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            })

        self.engine = create_engine(self.database_url, **engine_kwargs)
        
        # Setup session factory
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False,
            )
        )

        # Add connection event listeners
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup database event listeners for monitoring"""
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance"""
            if self.database_url.startswith("sqlite"):
                cursor = dbapi_connection.cursor()
                # Enable WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode=WAL")
                # Set synchronous mode to NORMAL for better performance
                cursor.execute("PRAGMA synchronous=NORMAL")
                # Set cache size to 10MB
                cursor.execute("PRAGMA cache_size=10000")
                # Set temp store to memory
                cursor.execute("PRAGMA temp_store=MEMORY")
                # Set mmap size to 256MB
                cursor.execute("PRAGMA mmap_size=268435456")
                cursor.close()

        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log slow queries"""
            context._query_start_time = time.time()

        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log slow queries"""
            if hasattr(context, '_query_start_time'):
                total = time.time() - context._query_start_time
                if total > 1.0:  # Log queries taking more than 1 second
                    logger.warning(f"Slow query ({total:.2f}s): {statement[:100]}...")

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    @contextmanager
    def get_session_context(self):
        """Get database session with context manager"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close_all_sessions(self):
        """Close all database sessions"""
        self.SessionLocal.remove()

    def get_connection_info(self):
        """Get database connection information"""
        if self.engine:
            return {
                "url": str(self.engine.url).replace(self.engine.url.password or "", "***"),
                "pool_size": getattr(self.engine.pool, 'size', lambda: 0)(),
                "checked_in": getattr(self.engine.pool, 'checkedin', lambda: 0)(),
                "checked_out": getattr(self.engine.pool, 'checkedout', lambda: 0)(),
                "overflow": getattr(self.engine.pool, 'overflow', lambda: 0)(),
            }
        return {}

# Global database manager
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db():
    """FastAPI dependency for database session"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

# Database utilities
def execute_query(query, params=None):
    """Execute raw SQL query with connection pooling"""
    with db_manager.get_session_context() as session:
        result = session.execute(query, params or {})
        return result.fetchall()

def bulk_insert(table_name, data_list, batch_size=1000):
    """Bulk insert data with batching"""
    with db_manager.get_session_context() as session:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            session.execute(f"INSERT INTO {table_name} VALUES {','.join(['?' for _ in batch])}", batch)
            session.commit()

# Query optimization utilities
class QueryOptimizer:
    @staticmethod
    def add_indexes(session, table_name, columns):
        """Add database indexes for better query performance"""
        for column in columns:
            try:
                index_name = f"idx_{table_name}_{column}"
                session.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column})")
                session.commit()
            except Exception as e:
                logger.warning(f"Failed to create index {index_name}: {e}")

    @staticmethod
    def analyze_query_plan(session, query):
        """Analyze query execution plan"""
        try:
            if "sqlite" in str(session.bind.url):
                result = session.execute(f"EXPLAIN QUERY PLAN {query}")
            else:
                result = session.execute(f"EXPLAIN {query}")
            return result.fetchall()
        except Exception as e:
            logger.error(f"Failed to analyze query plan: {e}")
            return []

# Performance monitoring
class DatabasePerformanceMonitor:
    def __init__(self):
        self.query_times = []
        self.slow_queries = []

    def log_query_time(self, query, execution_time):
        """Log query execution time"""
        self.query_times.append({
            'query': query[:100],
            'time': execution_time,
            'timestamp': time.time()
        })
        
        if execution_time > 1.0:  # Slow query threshold
            self.slow_queries.append({
                'query': query,
                'time': execution_time,
                'timestamp': time.time()
            })

    def get_performance_stats(self):
        """Get database performance statistics"""
        if not self.query_times:
            return {}
        
        times = [q['time'] for q in self.query_times]
        return {
            'total_queries': len(self.query_times),
            'average_time': sum(times) / len(times),
            'max_time': max(times),
            'min_time': min(times),
            'slow_queries_count': len(self.slow_queries),
            'slow_queries': self.slow_queries[-10:]  # Last 10 slow queries
        }

# Global performance monitor
db_performance_monitor = DatabasePerformanceMonitor()

import time
