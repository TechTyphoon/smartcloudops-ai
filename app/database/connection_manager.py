#!/usr/bin/env python3
"""
Database: Connection Manager
Centralized database connection management with connection pooling
"""

import logging
import os
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.monitoring.metrics import metrics

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages database connections with pooling and monitoring"""

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection manager.

        Args:
            database_url: Database connection URL. If None, reads from environment.
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.engine: Optional[Engine] = None
        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with production-grade configuration"""
        if not self.database_url:
            logger.warning(
                "No database URL provided, database features will be disabled"
            )
            return

        try:
            # Production-grade connection pooling configuration
            pool_size = int(os.getenv("DATABASE_POOL_SIZE", "20"))
            max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
            pool_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
            pool_recycle = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

            self.engine = create_engine(
                self.database_url,
                pool_size=pool_size,  # Base connections
                max_overflow=max_overflow,  # Burst capacity
                pool_timeout=pool_timeout,  # Connection timeout
                pool_recycle=pool_recycle,  # Recycle every hour
                pool_pre_ping=True,  # Health checks
                echo=False,  # Disable SQL logging in prod
                connect_args={
                    "connect_timeout": 30,  # Connection timeout
                    "command_timeout": 60,  # Command timeout
                },
            )

            logger.info(f"Database engine initialized with pool_size={pool_size}")
            metrics.set_active_connections("database", pool_size)

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            self.engine = None

    @contextmanager
    def get_connection(self):
        """
        Get a database connection with automatic cleanup.

        Yields:
            Database connection

        Raises:
            SQLAlchemyError: If connection fails
        """
        if not self.engine:
            raise SQLAlchemyError("Database engine not initialized")

        connection = None
        try:
            connection = self.engine.connect()
            logger.debug("Database connection acquired")
            yield connection

        except SQLAlchemyError as e:
            logger.error(f"Database connection error: {e}")
            metrics.record_remediation_action(
                "database_connection", "error", "connection_failed"
            )
            raise

        finally:
            if connection:
                connection.close()
                logger.debug("Database connection closed")

    def execute_query(
        self, query: str, params: Optional[dict] = None
    ) -> Optional[list]:
        """
        Execute a database query safely.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query results or None if failed
        """
        if not self.engine:
            logger.warning("Database not available, skipping query")
            return None

        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                return [dict(row) for row in result]

        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            metrics.record_remediation_action("database_query", "error", "query_failed")
            return None

    def test_connection(self) -> bool:
        """
        Test database connectivity.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.engine:
            return False

        try:
            with self.get_connection() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                metrics.set_system_health("database", 100.0)
                return True

        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            metrics.set_system_health("database", 0.0)
            return False

    def get_connection_info(self) -> dict:
        """
        Get database connection information.

        Returns:
            Connection information dictionary
        """
        if not self.engine:
            return {"status": "not_configured"}

        try:
            pool = self.engine.pool
            return {
                "status": "connected",
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }

        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"status": "error", "error": str(e)}

    def close(self) -> None:
        """Close all database connections"""
        if self.engine:
            try:
                self.engine.dispose()
                logger.info("Database engine disposed")
                metrics.set_active_connections("database", 0)
            except Exception as e:
                logger.error(f"Error disposing database engine: {e}")


# Global database manager instance
db_manager = DatabaseConnectionManager()
