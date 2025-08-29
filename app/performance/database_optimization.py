"""
Database Optimization Module
Connection pooling and query optimization
"""

import sqlite3
from typing import Any, Dict, Optional


class OptimizedDatabase:
    """Optimized database connection manager"""

    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connection_pool = []
        self.active_connections = 0

    def get_connection(self):
        """Get a database connection from the pool"""
        if self.connection_pool:
            return self.connection_pool.pop()
        else:
            return sqlite3.connect(self.db_path)

    def return_connection(self, connection):
        """Return a connection to the pool"""
        if len(self.connection_pool) < self.max_connections:
            self.connection_pool.append(connection)
        else:
            connection.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "pool_size": len(self.connection_pool),
            "active_connections": self.active_connections,
            "max_connections": self.max_connections,
            "db_path": self.db_path,
        }


# Global database instance
_database = None


def init_optimized_database(
    db_path: str, max_connections: int = 10
) -> OptimizedDatabase:
    """Initialize optimized database"""
    global _database
    _database = OptimizedDatabase(db_path, max_connections)
    return _database


def get_database() -> Optional[OptimizedDatabase]:
    """Get the global database instance"""
    return _database


def setup_database_optimization(app) -> None:
    """Setup database optimization for the application"""
    # Initialize database with optimized settings
    db_path = app.config.get("DATABASE_PATH", "data/mlops_optimized.db")
    max_connections = app.config.get("DATABASE_MAX_CONNECTIONS", 15)

    init_optimized_database(db_path, max_connections)
    app.logger.info(f"Database optimization initialized: {db_path}")
