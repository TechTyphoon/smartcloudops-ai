#!/usr/bin/env python3
"""
Database Configuration for Smart CloudOps AI
Phase 7: Production Launch & Feedback - Database Setup
"""

import os
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_config

# Get configuration
config = get_config()

# Create declarative base for models
Base = declarative_base()


# Database URL configuration
def get_database_url():
    """Get database URL from environment or config."""
    # Check for environment variable first
    database_url = os.getenv("DATABASE_URL")

    if database_url is not None:
        return database_url

    # Fall back to config DATABASE_URL attribute if available:
    if hasattr(config, "DATABASE_URL") and config.DATABASE_URL:
        return config.DATABASE_URL

    # Default to SQLite for development
    return "sqlite:///smartcloudops.db"


# Create database engine
def create_db_engine():
    """Create database engine with appropriate configuration."""
    database_url = get_database_url()

    # Engine configuration
    engine_kwargs = {
        "echo": getattr(config, "DEBUG", False),  # Log SQL queries in debug mode
    }

    # SQLite specific configuration
    if database_url.startswith("sqlite"):
        engine_kwargs.update({
            "poolclass": StaticPool, 
            "connect_args": {"check_same_thread": False}
        })

    # PostgreSQL specific configuration
    elif database_url.startswith("postgresql"):
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        })

    # MySQL specific configuration
    elif database_url.startswith("mysql"):
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        })

    return create_engine(database_url, **engine_kwargs)


# Create engine and session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)


def init_db():
    """Initialize database tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def close_db_session():
    """Close database session."""
    db_session.remove()


# Database health check
def check_db_health():
    """Check database connectivity and health."""
    try:
        with get_db_session() as session:
            # Try to execute a simple query
            session.execute("SELECT 1")
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# Database migration support
def run_migrations():
    """Run database migrations using Alembic."""
    try:
        from alembic import command
        from alembic.config import Config
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False


# Database backup support
def backup_database():
    """Create a database backup."""
    try:
        database_url = get_database_url()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if database_url.startswith("sqlite"):
            import shutil
            backup_path = f"backup/smartcloudops_{timestamp}.db"
            os.makedirs("backup", exist_ok=True)
            shutil.copy2("smartcloudops.db", backup_path)
            print(f"✅ Database backup created: {backup_path}")
            return backup_path
        else:
            print("⚠️ Database backup not implemented for this database type")
            return None
    except Exception as e:
        print(f"❌ Database backup failed: {e}")
        return None
