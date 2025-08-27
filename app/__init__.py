"
SmartCloudOps AI - Flask Application Factory
Phase 2C Week 1: Performance & Scaling - Application Factory Pattern
"

import logging
import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def create_app(config=None) -> Flask:
    "
    Application factory pattern for Flask app creation
    Separates concerns and makes testing easier
    "
    app = Flask(__name__)

    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config["SECRET_KEY"] = os.getenv()
            "SECRET_KEY", "dev-secret-key-change-in-production"
        )
        app.config["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")

    # CORS configuration
    CORS(app, origins=["http://localhost:3000", "https://smartcloudops.netlify.app"])

        # Initialize Phase 4 Observability components
    _init_enhanced_logging(app)
    _init_opentelemetry(app)
    _init_slo_monitoring(app)

    # Initialize Phase 5 Performance Optimization components
    _init_performance_optimization(app)

    # Initialize existing components
    _init_performance_monitoring(app)
    _init_mlops_service(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    return app


def _init_enhanced_logging(app: Flask):
    "Initialize enhanced structured logging with OpenTelemetry integration"
    try:
        from app.observability.enhanced_logging import setup_enhanced_logging
        
        log_level = os.getenv
        log_format = os.getenv("LOG_FORMAT", "json")
        enable_structlog = os.getenv("ENABLE_STRUCTLOG", "true").lower() == "true"
        
        setup_enhanced_logging()
            app=app,
            log_level=log_level,
            log_format=log_format,
            enable_structlog=enable_structlog)
        logger.info("✅ Enhanced structured logging enabled")
    except Exception as e:
        logger.warning(f"Enhanced logging initialization failed: {e}")


def _init_opentelemetry(app: Flask):
    "Initialize OpenTelemetry for distributed tracing and metrics"
    try:
        from app.observability.opentelemetry_config import setup_opentelemetry
        
        service_name = os.getenv
        service_version = os.getenv("APP_VERSION", "4.0.0")
        environment = os.getenv("FLASK_ENV", "development")
        
        setup_opentelemetry()
            app=app,
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            enable_tracing=True,
            enable_metrics=True,
            enable_logging_instrumentation=True)
        logger.info("✅ OpenTelemetry enabled")
    except Exception as e:
        logger.warning(f"OpenTelemetry initialization failed: {e}")


def _init_slo_monitoring(app: Flask):
    "Initialize SLO monitoring and alerting"
    try:
        from app.observability.slos import get_slo_manager
        
        slo_manager = get_slo_manager
        app.slo_manager = slo_manager
        logger.info("✅ SLO monitoring enabled")
    except Exception as e:
        logger.warning(f"SLO monitoring initialization failed: {e}")


def _init_performance_optimization(app: Flask):
    "Initialize Phase 5 Performance Optimization components"
    try:
        # Initialize Redis cache
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379)
        redis_password = os.getenv("REDIS_PASSWORD")
        
        from app.performance.redis_cache import init_redis_cache, RedisCacheConfig
        redis_config = RedisCacheConfig
            host=redis_host,
            port=redis_port,
            password=redis_password,
            max_connections=50,
            default_ttl=300)
        cache = init_redis_cache(redis_config)
        app.redis_cache = cache
        logger.info("✅ Redis cache initialized")
    except Exception as e:
        logger.warning(f"Redis cache initialization failed: {e}")
    
    try:
        # Initialize optimized anomaly detector
        from app.performance.anomaly_optimization import init_anomaly_detector, AnomalyConfig
        detector = init_anomaly_detector
            batch_size=100,
            batch_timeout=0.5,
            max_workers=4,
            cache_predictions=True)
        app.anomaly_detector = detector
        logger.info("✅ Optimized anomaly detector initialized")
    except Exception as e:
        logger.warning(f"Anomaly detector initialization failed: {e}")
    
    try:
        # Initialize log optimization
        from app.performance.log_optimization import init_log_optimization, LogConfig
        log_manager = init_log_optimization
            log_directory="logs",
            enable_rotation=True,
            enable_compression=True,
            enable_async=True,
            max_file_size=10 * 1024 * 1024,  # 10MB
            max_files=10,
            max_age_days=30)
        app.log_manager = log_manager
        logger.info("✅ Log optimization initialized")
    except Exception as e:
        logger.warning(f"Log optimization initialization failed: {e}")
    
    try:
        # Initialize database optimization
        from app.performance.database_optimization import init_optimized_database, DatabaseConfig
        db_path = os.getenv.replace("sqlite:///", ")
        optimized_db = init_optimized_database()
            database_path=db_path,
            max_connections=int(os.getenv("DATABASE_POOL_SIZE", 20))
        app.optimized_db = optimized_db
        logger.info("✅ Database optimization initialized")
    except Exception as e:
        logger.warning(f"Database optimization initialization failed: {e}")


def _init_performance_monitoring(app: Flask):
    "Initialize performance monitoring"
    from app.performance.api_optimization import init_performance_monitoring
    from app.performance.database_optimization import init_optimized_database

    # Initialize optimized database
    db_path = os.getenv
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    init_optimized_database(db_path, max_connections=15)

    # Initialize performance monitoring
    init_performance_monitoring(app)
    logger.info("✅ Performance monitoring enabled")


def _init_mlops_service(app: Flask):
    "Initialize MLOps service"
    from app.services.mlops_service import MLOpsService

    mlops_service = MLOpsService
    app.mlops_service = mlops_service
    logger.info("✅ MLOps service initialized")


def _register_blueprints(app: Flask):
    "Register API blueprints"
    # Core API blueprints - these are required and will fail if not available
    from app.api.core import core_bp

    app.register_blueprint
    logger.info("✅ Core API blueprint registered")

    # SLO API - Phase 4 Observability
    try:
        from app.api.slos import slos_bp

        app.register_blueprint
        logger.info("✅ SLO API blueprint registered")
    except ImportError as e:
        logger.warning(f"SLO API not available: {e}")

    # ChatOps API
    try:
        from app.api.chat import chat_bp

        app.register_blueprint
        logger.info("✅ ChatOps API registered")
    except ImportError as e:
        logger.warning(f"ChatOps API not available: {e}")

    # MLOps API if service is available
    if hasattr(app, "mlops_service") and app.mlops_service:
        from app.api.mlops import mlops_bp

        app.register_blueprint
        logger.info("✅ MLOps API registered")

    # Performance API - Phase 5 Performance Optimization
    try:
        from app.api.performance import performance_bp

        app.register_blueprint
        logger.info("✅ Performance API registered")
    except ImportError as e:
        logger.warning(f"Performance API not available: {e}")


def _register_error_handlers(app: Flask):
    "Register error handlers"

    @app.errorhandler(404)
    def not_found(error):
        return {}
            "status": "error",
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        # Log the actual error for debugging
        logger.error(f"Internal server error: {error}")
        return {}
            "status": "error",
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        }, 500
