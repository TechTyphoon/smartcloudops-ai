"""
Database Optimization and Query Performance
Phase 2C Week 1: Performance & Scaling - Database Layer
"""

import json
import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


@dataclass
class QueryStats:
    """Database query statistics"""

    query_hash: str
    query_type: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    parameters: Dict[str, Any]


class DatabaseMetrics:
    """Database performance metrics collector"""

    def __init__(self):
        self.query_stats: List[QueryStats] = []
        self.connection_pool_stats = {
            "active_connections": 0,
            "total_connections": 0,
            "max_connections": 0,
            "failed_connections": 0,
        }
        self._lock = threading.Lock()

    def record_query(self, stats: QueryStats):
        with self._lock:
            self.query_stats.append(stats)
            # Keep only last 1000 queries
            if len(self.query_stats) > 1000:
                self.query_stats = self.query_stats[-1000:]

    def get_slow_queries(self, threshold: float = 1.0) -> List[QueryStats]:
        """Get queries slower than threshold (seconds)"""
        return [q for q in self.query_stats if q.execution_time > threshold]

    def get_query_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.query_stats:
            return {}

        execution_times = [q.execution_time for q in self.query_stats]
        return {
            "total_queries": len(self.query_stats),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
            "slow_query_count": len(self.get_slow_queries()),
            "queries_by_type": self._group_by_type(),
        }

    def _group_by_type(self) -> Dict[str, int]:
        """Group queries by type"""
        type_counts = {}
        for query in self.query_stats:
            type_counts[query.query_type] = type_counts.get(query.query_type, 0) + 1
        return type_counts


class ConnectionPool:
    """Simple SQLite connection pool"""

    def __init__(self, database_path: str, max_connections: int = 10):
        self.database_path = database_path
        self.max_connections = max_connections
        self._pool: List[sqlite3.Connection] = []
        self._lock = threading.Semaphore(max_connections)
        self._pool_lock = threading.Lock()
        self.metrics = DatabaseMetrics()

        # Initialize pool
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            for _ in range(self.max_connections):
                conn = self._create_connection()
                self._pool.append(conn)

            self.metrics.connection_pool_stats["total_connections"] = len(self._pool)
            self.metrics.connection_pool_stats["max_connections"] = self.max_connections
            logger.info(
                f"Initialized connection pool with {len(self._pool)} connections"
            )

        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    def _create_connection(self) -> sqlite3.Connection:
        """Create optimized SQLite connection"""
        conn = sqlite3.connect(self.database_path, check_same_thread=False)

        # SQLite optimization settings
        conn.execute("PRAGMA synchronous = NORMAL")  # Balance safety/performance
        conn.execute("PRAGMA cache_size = 10000")  # 10MB cache
        conn.execute("PRAGMA temp_store = MEMORY")  # Use memory for temp tables
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory map
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys

        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row

        return conn

    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic return"""
        self._lock.acquire()
        try:
            with self._pool_lock:
                if self._pool:
                    conn = self._pool.pop()
                    self.metrics.connection_pool_stats["active_connections"] += 1
                else:
                    # Create new connection if pool is empty
                    conn = self._create_connection()
                    self.metrics.connection_pool_stats["total_connections"] += 1

            yield conn

        except Exception as e:
            logger.error(f"Database connection error: {e}")
            self.metrics.connection_pool_stats["failed_connections"] += 1
            raise
        finally:
            # Return connection to pool
            with self._pool_lock:
                self._pool.append(conn)
                self.metrics.connection_pool_stats["active_connections"] -= 1

            self._lock.release()

    def close_all(self):
        """Close all connections"""
        with self._pool_lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()


class QueryOptimizer:
    """Query optimization utilities"""

    @staticmethod
    def analyze_query_plan(
        conn: sqlite3.Connection, query: str, params: Tuple = ()
    ) -> List[Dict]:
        """Analyze query execution plan"""
        try:
            cursor = conn.cursor()
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            cursor.execute(explain_query, params)

            plan = []
            for row in cursor.fetchall():
                plan.append(
                    {
                        "id": row[0],
                        "parent": row[1],
                        "notused": row[2],
                        "detail": row[3],
                    }
                )

            return plan
        except Exception as e:
            logger.warning(f"Failed to analyze query plan: {e}")
            return []

    @staticmethod
    def suggest_indexes(conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Suggest indexes for table based on query patterns"""
        suggestions = []

        try:
            # Get table info
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]

            # Get existing indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            existing_indexes = [row[1] for row in cursor.fetchall()]

            # Suggest common index patterns
            id_columns = [col for col in columns if "id" in col.lower()]
            date_columns = [
                col
                for col in columns
                if any(
                    date_word in col.lower()
                    for date_word in ["date", "time", "created", "updated"]
                )
            ]
            status_columns = [col for col in columns if "status" in col.lower()]

            # Suggest indexes for ID columns
            for col in id_columns:
                index_name = f"idx_{table_name}_{col}"
                if index_name not in existing_indexes:
                    suggestions.append(
                        f"CREATE INDEX {index_name} ON {table_name}({col})"
                    )

            # Suggest indexes for date columns
            for col in date_columns:
                index_name = f"idx_{table_name}_{col}"
                if index_name not in existing_indexes:
                    suggestions.append(
                        f"CREATE INDEX {index_name} ON {table_name}({col})"
                    )

            # Suggest indexes for status columns
            for col in status_columns:
                index_name = f"idx_{table_name}_{col}"
                if index_name not in existing_indexes:
                    suggestions.append(
                        f"CREATE INDEX {index_name} ON {table_name}({col})"
                    )

        except Exception as e:
            logger.error(f"Failed to suggest indexes: {e}")

        return suggestions


class OptimizedDatabase:
    """Optimized database interface with performance monitoring"""

    def __init__(self, database_path: str, max_connections: int = 10):
        self.pool = ConnectionPool(database_path, max_connections)
        self.metrics = self.pool.metrics
        self.query_cache = {}
        self._setup_tables()

    def _setup_tables(self):
        """Setup optimized database tables"""
        with self.pool.get_connection() as conn:
            # Create performance metrics table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    rows_affected INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    parameters TEXT
                )
            """
            )

            # Create indexes for metrics table
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_query_metrics_timestamp 
                ON query_metrics(timestamp)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_query_metrics_type 
                ON query_metrics(query_type)
            """
            )

            conn.commit()

    def execute_query(
        self, query: str, params: Tuple = (), fetch: str = "none"
    ) -> Union[List[Dict], Dict, None]:
        """Execute optimized query with performance monitoring"""
        start_time = time.time()
        query_hash = str(hash(query))
        query_type = query.strip().upper().split()[0]

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)

                result = None
                rows_affected = cursor.rowcount

                if fetch == "all":
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]
                elif fetch == "one":
                    row = cursor.fetchone()
                    result = dict(row) if row else None

                if query_type in ["INSERT", "UPDATE", "DELETE"]:
                    conn.commit()

                execution_time = time.time() - start_time

                # Record query statistics
                stats = QueryStats(
                    query_hash=query_hash,
                    query_type=query_type,
                    execution_time=execution_time,
                    rows_affected=rows_affected,
                    timestamp=datetime.now(),
                    parameters=dict(enumerate(params)),
                )

                self.metrics.record_query(stats)

                # Log slow queries
                if execution_time > 1.0:
                    logger.warning(
                        f"Slow query detected: {execution_time:.3f}s - {query[:100]}..."
                    )

                return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query failed after {execution_time:.3f}s: {e}")
            raise

    def bulk_insert(
        self,
        table: str,
        columns: List[str],
        data: List[List[Any]],
        batch_size: int = 1000,
    ) -> int:
        """Optimized bulk insert with batching"""
        total_inserted = 0
        placeholders = ",".join(["?" for _ in columns])
        column_names = ",".join(columns)
        query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()

                # Process in batches
                for i in range(0, len(data), batch_size):
                    batch = data[i : i + batch_size]
                    cursor.executemany(query, batch)
                    total_inserted += len(batch)

                conn.commit()
                logger.info(f"Bulk inserted {total_inserted} rows into {table}")

        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise

        return total_inserted

    def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Optimize table performance"""
        optimization_results = {
            "table": table_name,
            "actions_taken": [],
            "suggestions": [],
        }

        try:
            with self.pool.get_connection() as conn:
                # Analyze table
                cursor = conn.cursor()
                cursor.execute(f"ANALYZE {table_name}")
                optimization_results["actions_taken"].append("ANALYZE executed")

                # Get index suggestions
                suggestions = QueryOptimizer.suggest_indexes(conn, table_name)
                optimization_results["suggestions"] = suggestions

                # Get table stats
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                optimization_results["row_count"] = row_count

                conn.commit()

        except Exception as e:
            logger.error(f"Table optimization failed: {e}")
            optimization_results["error"] = str(e)

        return optimization_results

    def vacuum_database(self) -> Dict[str, Any]:
        """Vacuum database to reclaim space and optimize"""
        start_time = time.time()

        try:
            with self.pool.get_connection() as conn:
                # Get database size before vacuum
                cursor = conn.cursor()
                cursor.execute("PRAGMA page_count")
                pages_before = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                size_before = pages_before * page_size

                # Perform vacuum
                conn.execute("VACUUM")

                # Get database size after vacuum
                cursor.execute("PRAGMA page_count")
                pages_after = cursor.fetchone()[0]
                size_after = pages_after * page_size

                execution_time = time.time() - start_time
                space_saved = size_before - size_after

                result = {
                    "execution_time": execution_time,
                    "size_before": size_before,
                    "size_after": size_after,
                    "space_saved": space_saved,
                    "space_saved_mb": space_saved / (1024 * 1024),
                }

                logger.info(
                    f"Database vacuum completed: saved {result['space_saved_mb']:.2f}MB"
                )
                return result

        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            raise

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            "query_summary": self.metrics.get_query_summary(),
            "slow_queries": [
                {
                    "query_type": q.query_type,
                    "execution_time": q.execution_time,
                    "timestamp": q.timestamp.isoformat(),
                    "rows_affected": q.rows_affected,
                }
                for q in self.metrics.get_slow_queries()
            ],
            "connection_pool": self.metrics.connection_pool_stats,
            "cache_stats": {"cached_queries": len(self.query_cache)},
        }

    def close(self):
        """Close database connections"""
        self.pool.close_all()


# Global database instance (will be initialized by service)
optimized_db: Optional[OptimizedDatabase] = None


def init_optimized_database(database_path: str, max_connections: int = 10):
    """Initialize global optimized database"""
    global optimized_db
    optimized_db = OptimizedDatabase(database_path, max_connections)
    return optimized_db


def get_database() -> OptimizedDatabase:
    """Get global database instance"""
    if optimized_db is None:
        raise RuntimeError(
            "Database not initialized. Call init_optimized_database() first."
        )
    return optimized_db
