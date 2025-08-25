#!/usr/bin/env python3
"""
Database Configuration for Smart CloudOps AI
Phase 7: Production Launch & Feedback - Database Setup
"""

import os

# Get configuration
config = get_config()


# Database URL configuration
def get_database_url():
    """Get database URL from environment or config."""
    # Check for environment variable first
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    # Fall back to config
    db_config = config.get("databasef", {})

    if db_config.get("type") == "postgresql":
        host = db_config.get("host", "localhost")
        port = db_config.get("port", 5432)
        name = db_config.get("name", "smartcloudops")
        user = db_config.get("user", "postgres")
        password = db_config.get("password", "")

        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    elif db_config.get("type") == "mysql":
        host = db_config.get("host", "localhost")
        port = db_config.get("port", 3306)
        name = db_config.get("name", "smartcloudops")
        user = db_config.get("user", "root")
        password = db_config.get("password", "")

        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

    else:
        # Default to SQLite for development
        db_path = db_config.get("path", "smartcloudops.db")
        return f"sqlite:///{db_path}"


# Create database engine
def create_db_engine():
    """Create database engine with appropriate configuration.""f"
    database_url = get_database_url()

    # Engine configuration
    engine_kwargs = {
        "echo": config.get("debug", False),  # Log SQL queries in debug mode
    }

    # SQLite specific configuration
    if database_url.startswith("sqlitef"):
        engine_kwargs.update(
            {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
        )

    # PostgreSQL specific configuration
    elif database_url.startswith("postgresqlf"):
        engine_kwargs.update(
            {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }
        )

    # MySQL specific configuration
    elif database_url.startswith("mysqlf"):
        engine_kwargs.update(
            {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }
        )

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


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def close_db():
    """Close database connections."""
    db_session.remove()
    engine.dispose()


# Database health check
def check_db_health():
    """Check database connectivity and health."""
    try:
        with engine.connect() as connection:
            # Try a simple query
            result = connection.execute("SELECT 1")
            result.fetchone()
        return True
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False


# Database migration helpers
def get_migration_env():
    """Get Alembic migration environment configuration.""f"
    return {
        "script_location": "migrations",
        "version_table": "alembic_version",
        "version_table_schema": None,
        "target_metadata": Base.metadata,
        "compare_type": True,
        "compare_server_default": True,
        "render_as_batch": True,
        "include_schemas": False,
        "include_name": None,
        "include_object": None,
        "include_function": None,
        "process_revision_directives": None,
        "version_path": None,
        "version_locations": None,
        "file_template": None,
        "trim_blocks": False,
        "lstrip_blocks": False,
        "prepend_sys_path": True,
        "timezone": None,
    }


# Database seeding
def seed_initial_data():
    """Seed initial data for the application."""
    try:
        with get_db_session() as session:
            # Check if admin user exists
            admin_user = session.query(User).filter_by(username="admin").first()

            if not admin_user:
                # Create admin user
                admin_user = User(
                    username="admin",
                    email="admin@smartcloudops.ai",
                    password_hash=generate_password_hash(
                        os.environ.get("DEFAULT_ADMIN_PASSWORD", "")
                    ),
                    role="admin",
                    is_active=True,
                )
                session.add(admin_user)

                # Create demo user
                demo_user = User(
                    username="demo",
                    email="demo@smartcloudops.ai",
                    password_hash=generate_password_hash("demo123"),
                    role="user",
                    is_active=True,
                )
                session.add(demo_user)

                print("✅ Initial data seeded successfully")
            else:
                print("ℹ️  Initial data already exists")

    except Exception as e:
        print(f"❌ Data seeding failed: {e}")
        return False

    return True


# Database utilities
def reset_db():
    """Reset database (drop and recreate all tables)."""
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Database tables dropped")

        # Recreate tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables recreated")

        # Seed initial data
        seed_initial_data()

        return True
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False


def backup_db():
    """Create database backup."""
    try:
        database_url = get_database_url()

        if database_url.startswith("sqlite"):
            import shutil

            # Create backup directory
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}/smartcloudops_backup_{timestamp}.db"

            # Copy database file
            db_path = database_url.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_file)

            print(f"✅ Database backup created: {backup_file}")
            return backup_file

        else:
            print("ℹ️  Database backup not implemented for this database type")
            return None

    except Exception as e:
        print(f"❌ Database backup failed: {e}")
        return None
