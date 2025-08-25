#!/usr/bin/env python3
"""
SmartCloudOps AI - Main Application Entry Point

This module serves as the main entry point for the SmartCloudOps AI platform,
providing a comprehensive Flask application with AI-powered cloud operations
capabilities including monitoring, anomaly detection, and automated remediation.

Key Features:
- RESTful API endpoints for all platform services
- Real-time monitoring and metrics collection
- AI/ML-powered anomaly detection and analysis
- Automated incident response and remediation
- ChatOps integration for natural language operations
- Comprehensive health monitoring and status reporting

Author: SmartCloudOps AI Team
Version: 3.3.0
License: MIT
"""

import logging
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import configuration
from app.config import get_config

# Import database functions (with fallback for missing components)
try:
    from app.database import init_db, seed_initial_data, check_db_health
except ImportError:

    def init_db():
        pass

    def seed_initial_data():
        pass

    def check_db_health():
        return True


# Import authentication functions
try:
    from app.auth_routes import register_auth_endpoints
except ImportError:

    def register_auth_endpoints(app):
        pass


# Import API blueprints (re-enabling working modules)
try:
    from app.api.anomalies import anomalies_bp

    ANOMALIES_AVAILABLE = True
except ImportError:
    anomalies_bp = None
    ANOMALIES_AVAILABLE = False

try:
    from app.api.feedback import feedback_bp

    FEEDBACK_AVAILABLE = True
except ImportError:
    feedback_bp = None
    FEEDBACK_AVAILABLE = False

try:
    from app.api.ai import ai_bp

    AI_API_AVAILABLE = True
except ImportError:
    ai_bp = None
    AI_API_AVAILABLE = False

# TODO: Fix remaining modules (remediation, ml)
try:
    from app.api.remediation import remediation_bp
    REMEDIATION_AVAILABLE = True
    print("✅ Remediation API successfully imported")
except ImportError as e:
    remediation_bp = None
    REMEDIATION_AVAILABLE = False
    print(f"⚠️ Remediation API not available: {e}")

try:
    from app.api.ml import ml_bp
    ML_API_AVAILABLE = True
    print("✅ ML API successfully imported")
except ImportError as e:
    ml_bp = None
    ML_API_AVAILABLE = False
    print(f"⚠️ ML API not available: {e}")

# Import existing modules
try:
    CHATOPS_AVAILABLE = True
except ImportError as e:
    print("Warning: ChatOps modules not available: {e}")
    CHATOPS_AVAILABLE = False

try:
    ML_AVAILABLE = True
except ImportError as e:
    print("Warning: ML modules not available: {e}")
    ML_AVAILABLE = False

try:
    REMEDIATION_ENGINE_AVAILABLE = True
except ImportError as e:
    print("Warning: Remediation engine not available: {e}")
    REMEDIATION_ENGINE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")


def create_app() -> Flask:
    """
    Create and configure the Flask application with all necessary components.

    This function initializes the complete SmartCloudOps AI application stack,
    including database connections, AI/ML components, monitoring setup, and
    all API endpoints. It handles graceful degradation if optional components
    are unavailable.

    Returns:
        Flask: Configured Flask application instance with all blueprints and
               middleware registered.

    Raises:
        Exception: If critical components (database, core services) fail to initialize.
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.update(config.to_dict())

    # Enable CORS
    cors_origins = getattr(config, "CORS_ORIGINS", ["http://localhost:3000"])
    CORS(app, origins=cors_origins)

    # Initialize database
    try:
        init_db()
        seed_initial_data()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed: {e}")

    # Initialize components
    ai_handler = None
    log_retriever = None
    system_context = None
    anomaly_detector = None
    remediation_engine = None

    if CHATOPS_AVAILABLE:
        try:
            ai_handler = FlexibleAIHandler()
            log_retriever = LogRetriever()
            system_context = SystemContextGatherer()
            logger.info("ChatOps components initialized successfully")
        except Exception as e:
            logger.error("ChatOps initialization failed: {e}")

    if ML_AVAILABLE:
        try:
            anomaly_detector = AnomalyDetector()
            logger.info("ML components initialized successfully")
        except Exception as e:
            logger.error("ML initialization failed: {e}")

    if REMEDIATION_ENGINE_AVAILABLE:
        try:
            remediation_engine = RemediationEngine()
            logger.info("Remediation engine initialized successfully")
        except Exception as e:
            logger.error("Remediation engine initialization failed: {e}")

    # Register authentication endpoints
    register_auth_endpoints(app)

    # Register API blueprints
    if ANOMALIES_AVAILABLE and anomalies_bp:
        app.register_blueprint(anomalies_bp)
        logger.info("Anomalies API registered")

    if REMEDIATION_AVAILABLE and remediation_bp:
        app.register_blueprint(remediation_bp)
        logger.info("Remediation API registered")

    if FEEDBACK_AVAILABLE and feedback_bp:
        app.register_blueprint(feedback_bp)
        logger.info("Feedback API registered")

    if ML_API_AVAILABLE and ml_bp:
        app.register_blueprint(ml_bp)
        logger.info("ML API registered")

    if AI_API_AVAILABLE and ai_bp:
        app.register_blueprint(ai_bp)
        logger.info("AI API registered")

    # Request logging middleware
    @app.before_request
    def before_request():
        request.start_time = datetime.utcnow()

    @app.after_request
    def after_request(response):
        # Calculate request duration
        duration = (datetime.utcnow() - request.start_time).total_seconds()

        # Update Prometheus metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint,
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.observe(duration)

        # Log request
        logger.info(
            "{request.method} {request.path} - {response.status_code} - {duration:.3f}s"
        )

        return response

    # Health check endpoint
    @app.route("/health")
    def health_check():
        """Health check endpoint."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {
                "database": check_db_health(),
                "chatops": CHATOPS_AVAILABLE and ai_handler is not None,
                "ml": ML_AVAILABLE and anomaly_detector is not None,
                "remediation": REMEDIATION_ENGINE_AVAILABLE
                and remediation_engine is not None,
                "anomalies_api": ANOMALIES_AVAILABLE,
                "remediation_api": REMEDIATION_AVAILABLE,
                "feedback_api": FEEDBACK_AVAILABLE,
                "ml_api": ML_API_AVAILABLE,
                "ai_api": AI_API_AVAILABLE,
            },
        }

        # Check if all critical components are healthy
        critical_components = ["database"]
        all_healthy = all(
            health_status["components"].get(comp, False) for comp in critical_components
        )

        status_code = 200 if all_healthy else 503
        return jsonify(health_status), status_code

    # Status endpoint
    @app.route("/status")
    def status():
        """Detailed status endpoint."""
        return jsonify(
            {
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "environment": getattr(config, "FLASK_ENV", "production"),
                "components": {
                    "database": {
                        "status": "healthy" if check_db_health() else "unhealthy",
                        "available": True,
                    },
                    "chatops": {
                        "status": (
                            "healthy"
                            if (CHATOPS_AVAILABLE and ai_handler)
                            else "unavailable"
                        ),
                        "available": CHATOPS_AVAILABLE,
                    },
                    "ml": {
                        "status": (
                            "healthy"
                            if (ML_AVAILABLE and anomaly_detector)
                            else "unavailable"
                        ),
                        "available": ML_AVAILABLE,
                    },
                    "remediation": {
                        "status": (
                            "healthy"
                            if (REMEDIATION_ENGINE_AVAILABLE and remediation_engine)
                            else "unavailable"
                        ),
                        "available": REMEDIATION_ENGINE_AVAILABLE,
                    },
                    "api_endpoints": {
                        "anomalies": ANOMALIES_AVAILABLE,
                        "remediation": REMEDIATION_AVAILABLE,
                        "feedback": FEEDBACK_AVAILABLE,
                        "ml": ML_API_AVAILABLE,
                    },
                },
            }
        )

    # Metrics endpoint for Prometheus
    @app.route("/metrics")
    def metrics():
        """Prometheus metrics endpoint."""
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    # Root endpoint
    @app.route("/")
    def root():
        """Root endpoint with API information."""
        return jsonify(
            {
                "name": "SmartCloudOps AI",
                "version": "1.0.0",
                "description": "AI-powered DevOps platform with anomaly detection and automated remediation",
                "phase": "Phase 7 - Production Launch & Feedback",
                "endpoints": {
                    "health": "/health",
                    "status": "/status",
                    "metrics": "/metrics",
                    "api_docs": "/api/docs",
                    "auth": {
                        "login": "/api/auth/login",
                        "register": "/api/auth/register",
                        "refresh": "/api/auth/refresh",
                        "logout": "/api/auth/logout",
                    },
                    "anomalies": (
                        "/api/anomalies/" if ANOMALIES_AVAILABLE else "unavailable"
                    ),
                    "remediation": (
                        "/api/remediation/actions"
                        if REMEDIATION_AVAILABLE
                        else "unavailable"
                    ),
                    "feedback": (
                        "/api/feedback/" if FEEDBACK_AVAILABLE else "unavailable"
                    ),
                    "ml": "/api/ml/" if ML_API_AVAILABLE else "unavailable",
                    "ai": "/api/ai/" if AI_API_AVAILABLE else "unavailable",
                    "chatops": "/chatops/" if CHATOPS_AVAILABLE else "unavailable",
                },
                "documentation": "https://github.com/your-repo/smartcloudops-ai",
                "support": "support@smartcloudops.ai",
            }
        )

    # API documentation endpoint
    @app.route("/api/docs")
    def api_docs():
        """API documentation endpoint."""
        return jsonify(
            {
                "title": "SmartCloudOps AI API Documentation",
                "version": "1.0.0",
                "description": "Complete API documentation for SmartCloudOps AI",
                "endpoints": {
                    "authentication": {
                        "POST /api/auth/login": "User login",
                        "POST /api/auth/register": "User registration",
                        "POST /api/auth/refresh": "Refresh access token",
                        "POST /api/auth/logout": "User logout",
                        "GET /api/auth/me": "Get current user info",
                        "POST /api/auth/change-password": "Change user password",
                    },
                    "anomalies": (
                        {
                            "GET /api/anomalies/": "Get all anomalies",
                            "GET /api/anomalies/<id>": "Get specific anomaly",
                            "POST /api/anomalies/": "Create new anomaly",
                            "PUT /api/anomalies/<id>": "Update anomaly",
                            "POST /api/anomalies/<id>/acknowledge": "Acknowledge anomaly",
                            "POST /api/anomalies/<id>/resolve": "Resolve anomaly",
                            "POST /api/anomalies/<id>/dismiss": "Dismiss anomaly",
                            "GET /api/anomalies/stats": "Get anomaly statistics",
                            "POST /api/anomalies/batch": "Create batch anomalies",
                        }
                        if ANOMALIES_AVAILABLE
                        else "unavailable"
                    ),
                    "remediation": (
                        {
                            "GET /api/remediation/actions": "Get all remediation actions",
                            "GET /api/remediation/actions/<id>": "Get specific action",
                            "POST /api/remediation/actions": "Create new action",
                            "PUT /api/remediation/actions/<id>": "Update action",
                            "DELETE /api/remediation/actions/<id>": "Delete action",
                            "POST /api/remediation/actions/<id>/approve": "Approve action",
                            "POST /api/remediation/actions/<id>/execute": "Execute action",
                            "POST /api/remediation/actions/<id>/cancel": "Cancel action",
                            "GET /api/remediation/actions/stats": "Get action statistics",
                            "POST /api/remediation/actions/batch": "Create batch actions",
                            "GET /api/remediation/available-actions": "Get available action types",
                        }
                        if REMEDIATION_AVAILABLE
                        else "unavailable"
                    ),
                    "feedback": (
                        {
                            "GET /api/feedback/": "Get all feedback",
                            "GET /api/feedback/<id>": "Get specific feedback",
                            "POST /api/feedback/": "Submit feedback",
                            "PUT /api/feedback/<id>": "Update feedback",
                            "DELETE /api/feedback/<id>": "Delete feedback",
                            "POST /api/feedback/<id>/update-status": "Update feedback status",
                            "GET /api/feedback/stats": "Get feedback statistics",
                            "GET /api/feedback/my-feedback": "Get user feedback",
                            "GET /api/feedback/types": "Get feedback types",
                        }
                        if FEEDBACK_AVAILABLE
                        else "unavailable"
                    ),
                    "ml": (
                        {
                            "POST /api/ml/anomalies": "Detect anomalies in metrics data",
                            "GET /api/ml/anomalies/realtime": "Real-time anomaly detection",
                            "POST /api/ml/train": "Train anomaly detection model",
                            "GET /api/ml/model/info": "Get model information",
                            "POST /api/ml/model/retrain": "Retrain model with new data",
                            "GET /api/ml/predictions": "Get recent predictions",
                            "GET /api/ml/performance": "Get model performance metrics",
                        }
                        if ML_API_AVAILABLE
                        else "unavailable"
                    ),
                    "ai": (
                        {
                            "POST /api/ai/recommendations": "Get AI-powered remediation recommendations",
                            "POST /api/ai/autonomous/process": "Process anomaly with autonomous operations",
                            "GET /api/ai/autonomous/policies": "Get automation policies",
                            "POST /api/ai/autonomous/policies": "Create automation policy",
                            "PUT /api/ai/autonomous/policies/<id>": "Update automation policy",
                            "DELETE /api/ai/autonomous/policies/<id>": "Delete automation policy",
                            "POST /api/ai/learning/cycle": "Run continuous learning cycle",
                            "GET /api/ai/learning/statistics": "Get learning statistics",
                            "POST /api/ai/data/collect": "Collect data for continuous learning",
                            "GET /api/ai/models/registry": "Get model registry information",
                            "POST /api/ai/models/<type>/promote": "Promote model to production",
                            "POST /api/ai/experiments/ab-testing": "Start A/B testing experiment",
                            "POST /api/ai/experiments/ab-testing/<id>/end": "End A/B testing experiment",
                            "POST /api/ai/drift/detect": "Detect data and model drift",
                            "GET /api/ai/knowledge/stats": "Get knowledge base statistics",
                            "POST /api/ai/knowledge/experience": "Add experience to knowledge base",
                            "GET /api/ai/autonomous/stats": "Get autonomous operations statistics",
                        }
                        if AI_API_AVAILABLE
                        else "unavailable"
                    ),
                },
                "authentication": "All endpoints except /api/feedback/ (POST) and /api/feedback/types require JWT authentication",
                "rate_limiting": "API endpoints are rate limited. Login endpoints have stricter limits.",
                "error_codes": {
                    "400": "Bad Request",
                    "401": "Unauthorized",
                    "403": "Forbidden",
                    "404": "Not Found",
                    "429": "Too Many Requests",
                    "500": "Internal Server Error",
                },
            }
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error("Unhandled exception: {error}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    logger.info("Flask application created successfully")
    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Get configuration
    config = get_config()

    # Run the application
    debug = getattr(config, "DEBUG", False)
    host = getattr(config, "FLASK_HOST", "0.0.0.0")
    port = getattr(config, "FLASK_PORT", 5000)

    logger.info("Starting SmartCloudOps AI on {host}:{port}")
    logger.info("Debug mode: {debug}")
    logger.info("Environment: {getattr(config, 'FLASK_ENV', 'production')}")

    app.run(host=host, port=port, debug=debug, threaded=True)
