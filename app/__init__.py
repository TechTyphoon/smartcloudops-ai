"""
SmartCloudOps AI - Flask Application Factory
Phase 2C Week 1: Performance & Scaling - Application Factory Pattern
"""

import logging
import os

from flask import Flask
from flask_cors import CORS

# Configure logging
# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def create_app(config=None) -> Flask:
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
        )
        app.config["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")

    # CORS configuration
    CORS(
        app,
        origins=["http://localhost:3000", "https://smartcloudops.netlify.app"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["Content-Type", "X-Total-Count"],
        supports_credentials=True,
    )

    # Initialize Phase 4 Observability components (with error handling)
    _init_enhanced_logging(app)
    _init_opentelemetry(app)
    _init_slo_monitoring(app)

    # Initialize Phase 5 Performance Optimization components (with error handling)
    _init_performance_optimization(app)

    # Initialize request counter for testing
    app.request_count = 0

    # Initialize anomaly detector
    try:
        from ml_models.anomaly_detector import AnomalyDetector

        app.anomaly_detector = AnomalyDetector()
        logger.info("✅ Anomaly detector initialized")
    except Exception as e:
        logger.warning(f"Anomaly detector initialization failed: {e}")
        app.anomaly_detector = None

    # Initialize MLOps service
    _init_mlops_service(app)

    @app.before_request
    def increment_request_count():
        app.request_count += 1

    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Add CORS headers if not already set
        if "Access-Control-Allow-Methods" not in response.headers:
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
        if "Access-Control-Allow-Headers" not in response.headers:
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With"
            )

        return response

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
            enable_structlog=enable_structlog,
        )
        logger.info("✅ Enhanced structured logging enabled")
    except Exception as e:
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
            enable_logging_instrumentation=True,
        )
        logger.info("✅ OpenTelemetry enabled")
    except Exception as e:
        logger.warning(f"OpenTelemetry initialization failed: {e}")


def _init_slo_monitoring(app: Flask):
    """Initialize SLO monitoring and alerting"""
    try:
        from app.observability.slos import setup_slo_monitoring

        setup_slo_monitoring(app)
        logger.info("✅ SLO monitoring enabled")
    except Exception as e:
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
        logger.warning(f"Performance optimization initialization failed: {e}")


def _init_performance_monitoring(app: Flask):
    """Initialize performance monitoring"""
    try:
        # Performance monitoring metrics are now handled in _register_blueprints
        logger.info("✅ Performance monitoring enabled")
    except Exception as e:
        logger.warning(f"Performance monitoring initialization failed: {e}")


def _init_mlops_service(app: Flask):
    """Initialize MLOps service"""
    try:
        # mlops blueprint is defined in app.api.mlops; import from there to avoid
        # circular imports between the api module and the service implementation.
        from app.api import mlops as _mlops_module

        # Register the mlops blueprint and keep a reference to the service on the
        # app object for other modules to inspect availability.
        app.register_blueprint(_mlops_module.mlops_bp)
        # Attach service instance for runtime checks elsewhere
        try:
            app.mlops_service = getattr(_mlops_module, "mlops_service", None)
        except Exception:
            app.mlops_service = None
        logger.info("✅ MLOps service enabled")
    except Exception as e:
        logger.warning(f"MLOps service initialization failed: {e}")


def _register_core_blueprints(app: Flask):
    """Register core application blueprints"""
    import app.api.core as core_module
    from app.auth_routes import auth_bp
    from app.monitoring_module import monitoring_bp

    app.register_blueprint(monitoring_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(core_module.core_bp)


def _register_optional_blueprints(app: Flask):
    """Register optional blueprints with error handling"""
    optional_blueprints = [
        ("app.api.anomalies", "anomalies_bp", "/api/anomalies"),
        ("app.api.remediation", "remediation_bp", "/api/remediation"),
        ("app.api.chatops", "chatops_bp", "/api/chatops"),
        ("app.api.ml", "ml_bp", "/api/ml"),
    ]

    for module_name, bp_name, url_prefix in optional_blueprints:
        try:
            module = __import__(module_name, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        except Exception as e:
            logger.warning(f"Failed to register {bp_name}: {e}")


def _register_chatops_blueprint(app: Flask):
    """Register the main chatops blueprint"""
    try:
        from app.chatops_module import chatops_bp as main_chatops_bp

        app.register_blueprint(
            main_chatops_bp, url_prefix="/chatops", name="main_chatops"
        )
    except Exception as e:
        logger.warning(f"Failed to register main chatops blueprint: {e}")


def _register_blueprints(app: Flask):
    """Register all application blueprints"""
    try:
        _register_core_blueprints(app)
        _register_optional_blueprints(app)
        _register_chatops_blueprint(app)

        logger.info("✅ All blueprints registered")
    except Exception as e:
        logger.warning(f"Blueprint registration failed: {e}")


def _register_error_handlers(app: Flask):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "status": 404}, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {"error": "Method not allowed", "status": 405}, 405

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error", "status": 500}, 500

    logger.info("✅ Error handlers registered")
