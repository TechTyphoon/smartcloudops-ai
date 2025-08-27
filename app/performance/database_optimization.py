"""
Database Optimization and Query Performance Enhancement
Phase 5: Performance & Cost Optimization - Database Optimization
"""

import os
import time
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import json

try:
    import psycopg2
    from psycopg2 import pool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    psycopg2 = None
    pool = None

from .redis_cache import get_redis_cache, cached

logger = logging.getLogger


@dataclass
class DatabaseConfig:
    """Database optimization configuration"""
    database_path: str = "data/optimized.db"
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    query_timeout: int = 60
    enable_query_cache: bool = True
    enable_connection_pooling: bool = True
    enable_query_logging: bool = True
    enable_slow_query_logging: bool = True
    slow_query_threshold: float = 1.0  # seconds
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 1000


class QueryCache:
    """Query result caching"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.cache = get_redis_cache()
        self._lock = threading.RLock()
        
    def get(self, query: str, params: tuple = None) -> Optional[Any]:
        """Get cached query result"""
        if not self.config.enable_query_cache or not self.cache:
            return None
        
        cache_key = self._generate_cache_key(query, params)
        return self.cache.get(cache_key, "query_cache")
    
    def set(self, query: str, params: tuple, result: Any):
        """Cache query result"""
        if not self.config.enable_query_cache or not self.cache:
            return
        
        cache_key = self._generate_cache_key(query, params)
        self.cache.set(cache_key, result, self.config.cache_ttl, "query_cache")
    
    def _generate_cache_key(self, query: str, params: tuple = None) -> str:
        """Generate cache key for query"""
        import hashlib
        
        key_data = query
        if params:
            key_data += str
        
        return hashlib.md5(key_data.encode().hexdigest()


class QueryLogger:
    """Query performance logging"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.slow_queries = []
        self.query_stats = {}
            'total_queries': 0,
            'slow_queries': 0,
            'cached_queries': 0,
            'total_time': 0.0,
            'avg_time': 0.0
        }
        self._lock = threading.RLock()
    
    def log_query(self, query: str, execution_time: float, cached: bool = False):
        """Log query execution"""
        with self._lock:
            self.query_stats['total_queries'] += 1
            self.query_stats['total_time'] += execution_time
            self.query_stats['avg_time'] = self.query_stats['total_time'] / self.query_stats['total_queries']
            
            if cached:
                self.query_stats['cached_queries'] += 1
            
            # Log slow queries
            if execution_time > self.config.slow_query_threshold:
                self.query_stats['slow_queries'] += 1
                self.slow_queries.append({}
                    'query': query,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Keep only recent slow queries
                if len(self.slow_queries) > 100:
                    self.slow_queries = self.slow_queries[-100:]
                
                logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        with self._lock:
            stats = self.query_stats.copy()
            stats['slow_queries_list'] = self.slow_queries[-10:]  # Last 10 slow queries
            return stats


class OptimizedDatabase:
    """Optimized database connection and query management"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.query_cache = QueryCache(config)
        self.query_logger = QueryLogger(config)
        self.connection_pool = None
        self._lock = threading.RLock()
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(config.database_path), exist_ok=True)
        
        # Initialize connection pool
        self._init_connection_pool()
        
        # Create indexes for common queries
        self._create_indexes()
        
        logger.info(f"✅ Optimized database initialized: {config.database_path}")
    
    def _init_connection_pool(self):
        """Initialize connection pool"""
        if not self.config.enable_connection_pooling:
            return
        
        try:
            if POSTGRES_AVAILABLE and self.config.database_path.startswith('postgresql://'):
                # PostgreSQL connection pool
                self.connection_pool = pool.ThreadedConnectionPool()
                    minconn=self.config.min_connections,
                    maxconn=self.config.max_connections,
                    dsn=self.config.database_path
                )
                logger.info("✅ PostgreSQL connection pool initialized")
            else:
                # SQLite doesn't need connection pooling, but we can implement a simple one
                logger.info("✅ Using SQLite database")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create indexes for common queries
                indexes = []
                    "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(type)",
                    "CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity)",
                    "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)",
                ]
                
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                    except Exception as e:
                        logger.warning(f"Failed to create index: {e}")
                
                conn.commit()
                logger.info("✅ Database indexes created")
                
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
    
    def get_connection(self):
        """Get database connection"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        else:
            # SQLite connection
            return sqlite3.connect(self.config.database_path)
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
        else:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Execute query with optimization"""
        start_time = time.time()
        
        # Try cache first
        if use_cache:
            cached_result = self.query_cache.get(query, params)
            if cached_result is not None:
                execution_time = time.time() - start_time
                self.query_logger.log_query(query, execution_time, cached=True)
                return cached_result
        
        # Execute query
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results
                if query.strip().upper().startswith('SELECT':
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row) for row in cursor.fetchall()]
                else:
                    results = [{'affected_rows': cursor.rowcount}]
                
                conn.commit()
                
                execution_time = time.time() - start_time
                self.query_logger.log_query(query, execution_time, cached=False)
                
                # Cache result
                if use_cache and query.strip().upper().startswith('SELECT':
                    self.query_cache.set(query, params, results)
                
                return results
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.query_logger.log_query(query, execution_time, cached=False)
            logger.error(f"Query execution error: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries efficiently"""
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                affected_rows = cursor.rowcount
                conn.commit()
                
                execution_time = time.time() - start_time
                self.query_logger.log_query(f"BATCH: {query}", execution_time, cached=False)
                
                return affected_rows
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.query_logger.log_query(f"BATCH: {query}", execution_time, cached=False)
            logger.error(f"Batch execution error: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
            'config': asdict(self.config),
            'query_stats': self.query_logger.get_stats(),
            'cache_enabled': self.config.enable_query_cache,
            'pooling_enabled': self.config.enable_connection_pooling,
        }
        
        if self.query_cache.cache:
            stats['cache_stats'] = self.query_cache.cache.get_stats()
        
        return stats
    
    def optimize_tables(self):
        """Optimize database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # SQLite optimization
                if not POSTGRES_AVAILABLE or not self.config.database_path.startswith('postgresql://'):
                    cursor.execute("VACUUM")
                    cursor.execute("ANALYZE")
                    conn.commit()
                    logger.info("✅ SQLite tables optimized")
                else:
                    # PostgreSQL optimization
                    cursor.execute("VACUUM ANALYZE")
                    conn.commit()
                    logger.info("✅ PostgreSQL tables optimized")
                    
        except Exception as e:
            logger.error(f"❌ Table optimization failed: {e}")
    
    def close(self):
        """Close database connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ Database connections closed")


# Global database instance
_optimized_db = None
_db_lock = threading.Lock()


def init_optimized_database(database_path: str, max_connections: int = 20) -> OptimizedDatabase:
    """Initialize optimized database"""
    global _optimized_db
    
    config = DatabaseConfig()
        database_path=database_path,
        max_connections=max_connections
    )
    
    with _db_lock:
        if _optimized_db is None:
            _optimized_db = OptimizedDatabase(config)
            logger.info("✅ Optimized database initialized")
    
    return _optimized_db


def get_optimized_database() -> Optional[OptimizedDatabase]:
    """Get optimized database instance"""
    return _optimized_db


def execute_query(query: str, params: tuple = None, use_cache: bool = True) -> List[Dict[str, Any]]:
    """Execute optimized query"""
    db = get_optimized_database()
    if db:
        return db.execute_query(query, params, use_cache)
    else:
        # Fallback to direct SQLite
        conn = sqlite3.connect("smartcloudops.db")
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT':
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row) for row in cursor.fetchall()]
        else:
            results = [{'affected_rows': cursor.rowcount}]
        
        conn.commit()
        conn.close()
        return results


# Decorator for query optimization
def optimized_query(use_cache: bool = True):
    """Decorator for query optimization"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would integrate with the query optimization system
            # For now, just execute the function
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decorator for caching query results
def cached_query(ttl: Optional[int] = None):
    """Decorator for caching query results"""
    return cached(ttl or 300, "query_cache")
