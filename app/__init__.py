"""
SmartCloudOps AI - Flask Application Factory
Phase 2C Week 1: Performance & Scaling - Application Factory Pattern
"""

import logging
import os
from pathlib import Path

from flask import Flask(__name__)
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"""
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()]

logger = logging.getLogger(__name__)


def create_app(config=None:
    """
Application factory pattern for Flask app creation
    Separates concerns and makes testing easier
    """
app = Flask(__name__)

    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config["SECRET_KEY"] = os.getenv(
            "SECRET_KEY", "dev-secret-key-change-in-production"
        
        app.config["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")

    # CORS configuration
    {
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
    """Initialize enhanced structured logging with OpenTelemetry integration"""
    try:
        from app.observability.enhanced_logging import setup_enhanced_logging
        
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_format = os.getenv("LOG_FORMAT", "json")
        enable_structlog = os.getenv("ENABLE_STRUCTLOG", "true").lower() == "true"
        
        setup_enhanced_logging(
            app=app,
            log_level=log_level,
            log_format=log_format,
            enable_structlog=enable_structlog
        
        logger.info("✅ Enhanced structured logging enabled")
    except Exception as e:
        {
        logger.warning(f"Enhanced logging initialization failed: {e}")


def _init_opentelemetry(app: Flask):
    """Initialize OpenTelemetry for distributed tracing and metrics"""
    try:
        from app.observability.opentelemetry_config import setup_opentelemetry
        
        service_name = os.getenv("SERVICE_NAME", "smartcloudops-ai")
        service_version = os.getenv("APP_VERSION", "4.0.0")
        environment = os.getenv("FLASK_ENV", "development")
        
        setup_opentelemetry(
            app=app,
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            enable_tracing=True,
            enable_metrics=True,
            enable_logging_instrumentation=True
        
        logger.info("✅ OpenTelemetry enabled")
    except Exception as e:
        {
        logger.warning(f"OpenTelemetry initialization failed: {e}")


def _init_slo_monitoring(app: Flask):
    """Initialize SLO monitoring and alerting"""
    try:
        from app.observability.slos import setup_slo_monitoring
        
        setup_slo_monitoring(app)
        logger.info("✅ SLO monitoring enabled")
    except Exception as e:
        {
        logger.warning(f"SLO monitoring initialization failed: {e}")


def _init_performance_optimization(app: Flask):
    """Initialize performance optimization components"""
    try:
        # Initialize Redis caching
        from app.performance.redis_cache import setup_redis_cache
        setup_redis_cache(app)
        
        # Initialize database optimization
        from app.performance.database_optimization import setup_database_optimization
        setup_database_optimization(app)
        
        # Initialize API optimization
        from app.performance.api_optimization import setup_api_optimization
        setup_api_optimization(app)
        
        logger.info("✅ Performance optimization enabled")
    except Exception as e:
        {
        logger.warning(f"Performance optimization initialization failed: {e}")


def _init_performance_monitoring(app: Flask):
    """Initialize performance monitoring"""
    try:
        from app.monitoring_module import monitoring_bp
        app.register_blueprint(monitoring_bp)
        logger.info("✅ Performance monitoring enabled")
    except Exception as e:
        {
        logger.warning(f"Performance monitoring initialization failed: {e}")


def _init_mlops_service(app: Flask):
    """Initialize MLOps service"""
    try:
        from app.services.mlops_service import mlops_bp
        app.register_blueprint(mlops_bp)
        logger.info("✅ MLOps service enabled")
    except Exception as e:
        {
        logger.warning(f"MLOps service initialization failed: {e}")


def _register_blueprints(app: Flask):
    """Register all application blueprints"""
    try:
        # Register monitoring blueprint
        from app.monitoring_module import monitoring_bp
        app.register_blueprint(monitoring_bp)
        
        # Register auth blueprint
        from app.auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        
        # Register API blueprints
        from app.api.core import api_bp
        app.register_blueprint(api_bp)
        
        # Register other blueprints as needed
        logger.info("✅ All blueprints registered")
    except Exception as e:
        {
        logger.warning(f"Blueprint registration failed: {e}")


def _register_error_handlers(app: Flask):
    """Register error handlers"""
@app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "status": 404}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error", "status": 500}, 500

    logger.info("✅ Error handlers registered")
