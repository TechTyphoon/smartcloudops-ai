#!/usr/bin/env python3
"""
Smart CloudOps AI - Refactored Main Application
Production-ready application with modular architecture
"""

import os
import sys
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import modular components
from app.config import get_config as _get_config
from app.database import db_manager
from app.logging import setup_logging, get_logger, log_request_info, log_error
from app.monitoring import metrics
from app.security import validate_string_input, validate_json_input

# Import ML components
try:
    from ml_models import AnomalyDetector

    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False

# Import remediation components
try:
    from app.remediation.engine import RemediationEngine

    REMEDIATION_AVAILABLE = True
except ImportError as e:
    REMEDIATION_AVAILABLE = False

# Import ChatOps components
try:
    from app.chatops.ai_handler import FlexibleAIHandler
    from app.chatops.utils import (
        LogRetriever,
        SystemContextGatherer,
        validate_query_params,
    )

    CHATOPS_AVAILABLE = True
except ImportError as e:
    CHATOPS_AVAILABLE = False

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/smartcloudops.log"),
    enable_json=os.getenv("LOG_JSON", "true").lower() == "true",
    enable_console=True,
)

logger = get_logger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application"""

    # Load configuration
    env = os.getenv("FLASK_ENV", "development").lower()
    config_class = _get_config(env)

    try:
        app_config = config_class.from_env()
        logger.info(f"Configuration loaded for environment: {env}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        app_config = {}

    # Create Flask app
    app = Flask(__name__)
    app.config.update(app_config)

    # Initialize components
    _initialize_components(app)

    # Register blueprints
    _register_blueprints(app)

    # Register middleware
    _register_middleware(app)

    # Register routes
    _register_routes(app)

    # Register error handlers
    _register_error_handlers(app)

    logger.info("Flask application created successfully")
    return app


def _initialize_components(app: Flask) -> None:
    """Initialize application components"""

    # Initialize AI handler
    if CHATOPS_AVAILABLE:
        app.ai_handler = FlexibleAIHandler(provider=os.getenv("AI_PROVIDER", "auto"))
        app.log_retriever = LogRetriever()
        app.system_gatherer = SystemContextGatherer()
        logger.info("ChatOps components initialized")

    # Initialize ML components
    if ML_AVAILABLE:
        app.anomaly_detector = AnomalyDetector()
        try:
            app.anomaly_detector.load_model()
            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load existing ML model: {e}")
    else:
        app.anomaly_detector = None

    # Initialize remediation engine
    if REMEDIATION_AVAILABLE:
        app.remediation_engine = RemediationEngine()
        logger.info("Remediation engine initialized")
    else:
        app.remediation_engine = None

    # Test database connection
    if db_manager.test_connection():
        logger.info("Database connection successful")
    else:
        logger.warning("Database connection failed")


def _register_blueprints(app: Flask) -> None:
    """Register Flask blueprints"""

    # Register authentication blueprint
    try:
        from app.auth_routes import auth_bp

        app.register_blueprint(auth_bp)
        logger.info("Authentication blueprint registered")
    except ImportError as e:
        logger.warning(f"Authentication blueprint not available: {e}")

    # Register GOD MODE API blueprint
    try:
        from app.god_mode_api import init_god_mode_api

        init_god_mode_api(app)
        logger.info("GOD MODE API blueprint registered")
    except ImportError as e:
        logger.warning(f"GOD MODE API blueprint not available: {e}")


def _register_middleware(app: Flask) -> None:
    """Register application middleware"""

    @app.before_request
    def before_request():
        """Middleware executed before each request"""
        request.start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": request.url,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
            },
        )

    @app.after_request
    def after_request(response):
        """Middleware executed after each request"""
        duration = time.time() - getattr(request, "start_time", 0)

        # Record metrics
        metrics.record_request(
            method=request.method,
            endpoint=request.endpoint or "unknown",
            status_code=response.status_code,
            duration=duration,
        )

        # Log request completion
        log_request_info(logger, request, response, duration)

        return response


def _register_routes(app: Flask) -> None:
    """Register application routes"""

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "3.1.0",
                "components": {
                    "database": db_manager.test_connection(),
                    "ml_model": ML_AVAILABLE and app.anomaly_detector is not None,
                    "remediation": REMEDIATION_AVAILABLE,
                    "chatops": CHATOPS_AVAILABLE,
                },
                "metrics": {
                    "uptime": (
                        time.time() - app.start_time
                        if hasattr(app, "start_time")
                        else 0
                    ),
                    "memory_usage": _get_memory_usage(),
                },
            }

            # Set system health metrics
            overall_health = sum(health_status["components"].values()) / len(
                health_status["components"]
            )
            metrics.set_system_health("overall", overall_health * 100)

            return jsonify(health_status), 200

        except Exception as e:
            log_error(logger, e, {"endpoint": "/health"})
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.route("/metrics", methods=["GET"])
    def metrics_endpoint():
        """Prometheus metrics endpoint"""
        try:
            return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
        except Exception as e:
            log_error(logger, e, {"endpoint": "/metrics"})
            return jsonify({"error": "Failed to generate metrics"}), 500

    @app.route("/anomaly", methods=["POST"])
    def detect_anomaly():
        """ML anomaly detection endpoint"""
        try:
            # Validate input
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            data = validate_json_input(data)

            # Extract metrics
            metrics_data = data.get("metrics", {})
            if not metrics_data:
                return jsonify({"error": "No metrics provided"}), 400

            # Perform anomaly detection
            if app.anomaly_detector:
                result = app.anomaly_detector.detect_anomaly(metrics_data)

                # Record metrics
                if result.get("is_anomaly"):
                    metrics.record_anomaly(
                        severity=result.get("severity", "medium"),
                        model_type="anomaly_detector",
                    )

                metrics.record_ml_prediction("anomaly_detector", "success")

                return (
                    jsonify(
                        {
                            "status": "success",
                            "data": result,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"error": "ML model not available"}), 503

        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            log_error(logger, e, {"endpoint": "/anomaly"})
            metrics.record_ml_prediction("anomaly_detector", "error")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/query", methods=["POST"])
    def process_query():
        """ChatOps query processing endpoint"""
        try:
            # Validate input
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            data = validate_json_input(data)
            query = data.get("query", "")

            if not query:
                return jsonify({"error": "No query provided"}), 400

            query = validate_string_input(query, max_length=1000)

            # Process query
            if CHATOPS_AVAILABLE:
                result = app.ai_handler.process_query(query)
                return (
                    jsonify(
                        {
                            "status": "success",
                            "data": result,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"error": "ChatOps not available"}), 503

        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            log_error(logger, e, {"endpoint": "/query"})
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/demo", methods=["GET"])
    def demo_endpoint():
        """Demo endpoint showing system capabilities"""
        try:
            demo_data = {
                "message": "SmartCloudOps.AI is running!",
                "version": "3.1.0",
                "features": {
                    "ml_anomaly_detection": ML_AVAILABLE,
                    "chatops": CHATOPS_AVAILABLE,
                    "remediation": REMEDIATION_AVAILABLE,
                    "authentication": True,
                    "monitoring": True,
                },
                "endpoints": {
                    "health": "GET /health",
                    "metrics": "GET /metrics",
                    "anomaly": "POST /anomaly",
                    "query": "POST /query",
                    "demo": "GET /demo",
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            return jsonify(demo_data), 200

        except Exception as e:
            log_error(logger, e, {"endpoint": "/demo"})
            return jsonify({"error": "Internal server error"}), 500


def _register_error_handlers(app: Flask) -> None:
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Endpoint not found",
                    "error": "The requested endpoint does not exist",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        log_error(logger, error, {"endpoint": request.endpoint})
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Internal server error",
                    "error": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exceptions"""
        log_error(logger, error, {"endpoint": request.endpoint})
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Service Temporarily Unavailable",
                    "error": "An unexpected error occurred. The issue has been logged",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            503,
        )


def _get_memory_usage() -> Dict[str, Any]:
    """Get memory usage information"""
    try:
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2),
        }
    except ImportError:
        return {"error": "psutil not available"}


# Create the application instance
app = create_app()
app.start_time = time.time()


# Get port configuration
def get_port() -> int:
    """Get standardized port across all environments"""
    port = os.getenv("FLASK_PORT", "5000")
    try:
        return int(port)
    except ValueError:
        logger.warning(f"Invalid port '{port}', using default 5000")
        return 5000


if __name__ == "__main__":
    logger.info("Starting Smart CloudOps AI Refactored Application")

    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = get_port()

    logger.info(f"Starting Smart CloudOps AI on {host}:{port}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"Debug mode: {debug_mode}")

    app.run(host=host, port=port, debug=debug_mode)
