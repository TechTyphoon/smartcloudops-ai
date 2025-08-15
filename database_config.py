# database_config.py - Production Database Configuration
# Smart CloudOps AI Database Layer

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool


# Database Configuration
class DatabaseConfig:
    """Production-grade database configuration"""

    # PostgreSQL Connection Settings
    POSTGRES_USER = os.getenv("POSTGRES_USER", "smartcloudops")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cloudops123")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "smartcloudops_production")

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": QueuePool,
        "pool_size": 10,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
        "pool_pre_ping": True,  # Validate connections before use
        "connect_args": {"connect_timeout": 10, "application_name": "SmartCloudOps_AI"},
    }

    # Migration Configuration
    ALEMBIC_CONFIG = {
        "script_location": "migrations",
        "version_locations": "migrations/versions",
    }


# Database Extensions
db = SQLAlchemy()
migrate = Migrate()


def init_database(app):
    """Initialize database with Flask application"""
    app.config.from_object(DatabaseConfig)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables in application context
    with app.app_context():
        try:
            # Test connection using SQLAlchemy 2.0 syntax
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                print(
                    f"✅ Database connection successful: {DatabaseConfig.POSTGRES_DB}"
                )

            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise


def get_connection_info():
    """Get database connection information"""
    return {
        "host": DatabaseConfig.POSTGRES_HOST,
        "port": DatabaseConfig.POSTGRES_PORT,
        "database": DatabaseConfig.POSTGRES_DB,
        "user": DatabaseConfig.POSTGRES_USER,
        "uri": DatabaseConfig.SQLALCHEMY_DATABASE_URI.replace(
            DatabaseConfig.POSTGRES_PASSWORD, "****"
        ),
    }


def check_database_health():
    """Check database connectivity and performance"""
    try:
        start_time = datetime.now()
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT version(), now(), current_user"))
            row = result.fetchone()
        end_time = datetime.now()

        return {
            "status": "healthy",
            "version": row[0] if row else "unknown",
            "server_time": row[1].isoformat() if row and row[1] else "unknown",
            "user": row[2] if row else "unknown",
            "response_time_ms": int((end_time - start_time).total_seconds() * 1000),
            "connection_pool": {
                "size": db.engine.pool.size(),
                "checked_in": db.engine.pool.checkedin(),
                "checked_out": db.engine.pool.checkedout(),
                "overflow": db.engine.pool.overflow(),
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "response_time_ms": -1}
