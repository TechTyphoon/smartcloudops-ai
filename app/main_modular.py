#!/usr/bin/env python3
"""
Smart CloudOps AI - Modular Main Application
Production-Ready ML Integration & Auto-Remediation
"""

import logging
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from app.config import get_config as _get_config
except ImportError:
    # Fallback for direct execution
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.config import get_config as _get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Load configuration
    config = _get_config()

    # Register blueprints
    try:
        from app.auth_routes import auth_bp

        app.register_blueprint(auth_bp)
        logger.info("Authentication blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"Authentication module not available: {e}")

    try:
        from app.ml_module import ml_bp

        app.register_blueprint(ml_bp)
        logger.info("ML module blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"ML module not available: {e}")

    try:
        from app.monitoring_module import monitoring_bp

        app.register_blueprint(monitoring_bp)
        logger.info("Monitoring module blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"Monitoring module not available: {e}")

    try:
        from app.chatops_module import chatops_bp

        app.register_blueprint(chatops_bp)
        logger.info("ChatOps module blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"ChatOps module not available: {e}")

    # Register existing blueprints
    try:
        from app.enhanced_ml_api import enhanced_ml_bp

        app.register_blueprint(enhanced_ml_bp)
        logger.info("Enhanced ML API blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"Enhanced ML API not available: {e}")

    try:
        from app.beta_api import beta_api

        if beta_api:
            app.register_blueprint(beta_api)
            logger.info("Beta API blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"Beta API not available: {e}")

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        """Root endpoint with application information."""
        return jsonify(
            {
                "status": "success",
                "message": "Smart CloudOps AI - Modular Application",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "modules": {
                    "authentication": "/auth",
                    "ml_services": "/ml",
                    "monitoring": "/monitoring",
                    "chatops": "/chatops",
                    "enhanced_ml": "/enhanced-ml",
                },
                "health_check": "/monitoring/health",
                "status": "/monitoring/status",
            }
        )

    # Demo endpoint (removed default credentials)
    @app.route("/demo", methods=["GET"])
    def demo():
        """Demo endpoint with application overview."""
        return jsonify(
            {
                "status": "success",
                "message": "Smart CloudOps AI - Production Ready",
                "version": "1.0.0",
                "architecture": "Modular Flask Application",
                "features": {
                    "authentication": "Enterprise JWT system",
                    "ml_anomaly": "IsolationForest ML detection",
                    "chatops": "AI-powered operations",
                    "monitoring": "Prometheus + Grafana",
                    "remediation": "Automated issue resolution",
                },
                "api_endpoints": {
                    "authentication": {
                        "login": "POST /auth/login",
                        "profile": "GET /auth/profile",
                        "logout": "POST /auth/logout",
                    },
                    "ml_detection": {
                        "anomaly": "POST /ml/anomaly",
                        "status": "GET /ml/status",
                        "batch": "POST /ml/batch",
                    },
                    "chatops": {
                        "query": "POST /chatops/query",
                        "logs": "GET /chatops/logs",
                        "context": "GET /chatops/context",
                    },
                    "monitoring": {
                        "status": "GET /monitoring/status",
                        "metrics": "GET /monitoring/metrics",
                        "health": "GET /monitoring/health",
                    },
                },
                "test_instructions": {
                    "1": "GET /demo - This endpoint",
                    "2": "GET /auth/login - See login options",
                    "3": "POST /auth/login with valid credentials",
                    "4": "GET /ml/anomaly - ML service info",
                    "5": "GET /chatops/query - ChatOps info",
                    "6": "GET /monitoring/status - System status",
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
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
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
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
        """Handle any unhandled exceptions."""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Service Temporarily Unavailable",
                    "error": "An unexpected error occurred. The issue has been logged",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": getattr(request, "id", "unknown"),
                }
            ),
            503,
        )

    return app


# Create the application instance
app = create_app()


def get_port() -> int:
    """Get standardized port across all environments."""
    port = os.getenv("FLASK_PORT", "5000")  # Changed default to 5000 to match Docker
    try:
        return int(port)
    except ValueError:
        logger.warning(f"Invalid port '{port}', using default 5000")
        return 5000


if __name__ == "__main__":
    logger.info("Starting Smart CloudOps AI Modular Application")
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv(
        "FLASK_HOST", "0.0.0.0"
    )  # Changed default for container compatibility
    port = get_port()

    logger.info(f"Starting Smart CloudOps AI on {host}:{port}")
    logger.info(f"Environment FLASK_PORT: {os.getenv('FLASK_PORT', 'not set')}")
    app.run(host=host, port=port, debug=debug_mode)
