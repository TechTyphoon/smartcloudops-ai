#!/usr/bin/env python3
"""
Smart CloudOps AI - Flask Application (Phase 2)
ChatOps application with GPT integration and comprehensive monitoring
"""

import logging
import os
import sys
import time

from flask import Flask, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.chatops.ai_handler import FlexibleAIHandler
from app.chatops.utils import (
    LogRetriever,
    SystemContextGatherer,
    format_response,
    validate_query_params,
)
from app.config import get_config

# Import ML anomaly detection
try:
    from ml_models import AnomalyDetector

    ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML models not available: {e}")
    ML_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "flask_requests_total", "Total Flask requests", ["method", "endpoint"]
)
REQUEST_DURATION = Histogram("flask_request_duration_seconds", "Flask request duration")
SYSTEM_HEALTH = Gauge(
    "system_health_status", "System health status (1=healthy, 0=unhealthy)"
)
GPT_REQUESTS = Counter("gpt_requests_total", "Total GPT API requests", ["status"])
GPT_RESPONSE_TIME = Histogram("gpt_response_time_seconds", "GPT API response time")

# ML Anomaly Detection metrics
ANOMALY_DETECTIONS = Counter(
    "anomaly_detections_total", "Total anomaly detections", ["severity"]
)
ANOMALY_INFERENCE_TIME = Histogram(
    "anomaly_inference_time_seconds", "Anomaly detection inference time"
)


def create_app(config_name="development"):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.update(config.from_env())

    # Set system health to healthy by default
    SYSTEM_HEALTH.set(1)

    # Initialize ChatOps components
    try:
        ai_handler = FlexibleAIHandler(provider="auto")
        context_gatherer = SystemContextGatherer()
        log_retriever = LogRetriever()
        logger.info("ChatOps components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ChatOps components: {str(e)}")
        ai_handler = None
        context_gatherer = None
        log_retriever = None

    # Initialize ML Anomaly Detection
    anomaly_detector = None
    if ML_AVAILABLE:
        try:
            anomaly_detector = AnomalyDetector()
            # Try to load existing model
            if anomaly_detector.load_model():
                logger.info("ML anomaly detection model loaded successfully")
            else:
                logger.info("No existing ML model found, will train on first use")
        except Exception as e:
            logger.error(f"Failed to initialize ML anomaly detection: {str(e)}")
            anomaly_detector = None
    else:
        logger.warning("ML anomaly detection not available")

    # Log AI handler status
    if ai_handler and ai_handler.provider:
        provider_info = ai_handler.get_provider_info()
        logger.info(f"AI integration: ENABLED ({provider_info['provider']})")
    else:
        logger.warning("AI integration: DISABLED (No API keys configured)")

    @app.before_request
    def before_request():
        """Record request metrics."""
        request.start_time = time.time()
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.endpoint or "unknown"
        ).inc()

    @app.after_request
    def after_request(response):
        """Record request duration."""
        if hasattr(request, "start_time"):
            REQUEST_DURATION.observe(time.time() - request.start_time)
        return response

    @app.route("/health")
    def health_check():
        """Health check endpoint."""
        try:
            return (
                jsonify(
                    {
                        "status": "healthy",
                        "service": config.APP_NAME,
                        "version": config.VERSION,
                        "timestamp": time.time(),
                    }
                ),
                200,
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            SYSTEM_HEALTH.set(0)
            return (
                jsonify(
                    {"status": "unhealthy", "error": str(e), "timestamp": time.time()}
                ),
                500,
            )

    @app.route("/metrics")
    def metrics():
        """Prometheus metrics endpoint."""
        try:
            # Update system health metric
            SYSTEM_HEALTH.set(1)

            # Generate Prometheus metrics
            return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {str(e)}")
            return jsonify({"error": "Failed to generate metrics"}), 500

    @app.route("/")
    def index():
        """Root endpoint."""
        return jsonify(
            {
                "service": config.APP_NAME,
                "version": config.VERSION,
                "status": "running",
                "phase": "Phase 2 - ChatOps Implementation",
                "chatops_ready": ai_handler is not None,
                "endpoints": {
                    "health": "/health",
                    "status": "/status",
                    "metrics": "/metrics",
                    "query": "/query (POST)",
                    "logs": "/logs (GET)",
                    "chat_history": "/chatops/history (GET)",
                    "clear_history": "/chatops/clear (POST)",
                    "ai_info": "/chatops/info (GET)",
                },
            }
        )

    @app.route("/status")
    def status():
        """System status endpoint with comprehensive health information."""
        try:
            if context_gatherer:
                system_context = context_gatherer.get_system_context()
                return jsonify(
                    format_response(
                        data=system_context,
                        message="System status retrieved successfully",
                    )
                )
            else:
                return jsonify(
                    format_response(
                        data={
                            "system": "operational",
                            "monitoring": "active",
                            "prometheus_ready": True,
                            "phase": "Phase 2 - ChatOps Implementation",
                            "chatops_ready": ai_handler is not None,
                        },
                        message="Basic system status",
                    )
                )
        except Exception as e:
            logger.error(f"Status endpoint error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to retrieve system status",
                    )
                ),
                500,
            )

    @app.route("/query", methods=["POST"])
    def query():
        """ChatOps query endpoint with AI integration."""
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        data={"error": "AI handler not available"},
                        status="error",
                        message="ChatOps functionality not available",
                    )
                ),
                503,
            )

        try:
            # Get request data
            request_data = request.get_json()
            if not request_data or "query" not in request_data:
                return (
                    jsonify(
                        format_response(
                            data={"error": "Query parameter required"},
                            status="error",
                            message="Missing query parameter",
                        )
                    ),
                    400,
                )

            query_text = request_data["query"]
            context = request_data.get("context", {})

            # Record start time for metrics
            start_time = time.time()

            # Process query with AI
            result = ai_handler.process_query(query_text, context)

            # Record metrics
            response_time = time.time() - start_time
            GPT_RESPONSE_TIME.observe(response_time)

            if result["status"] == "success":
                GPT_REQUESTS.labels(status="success").inc()
                return jsonify(
                    format_response(data=result, message="Query processed successfully")
                )
            else:
                GPT_REQUESTS.labels(status="error").inc()
                return (
                    jsonify(
                        format_response(
                            data=result,
                            status="error",
                            message="Query processing failed",
                        )
                    ),
                    400,
                )

        except Exception as e:
            logger.error(f"Query endpoint error: {str(e)}")
            GPT_REQUESTS.labels(status="error").inc()
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Internal server error",
                    )
                ),
                500,
            )

    @app.route("/logs", methods=["GET"])
    def logs():
        """Log retrieval endpoint with filtering."""
        if not log_retriever:
            return (
                jsonify(
                    format_response(
                        data={"error": "Log retriever not available"},
                        status="error",
                        message="Log functionality not available",
                    )
                ),
                503,
            )

        try:
            # Validate and sanitize query parameters
            params = validate_query_params(request.args.to_dict())

            # Get logs based on parameters
            hours = params.get("hours", 24)
            level = params.get("level")
            service = params.get("service")

            if service:
                logs_data = log_retriever.get_logs_by_service(service, hours)
            elif level:
                logs_data = log_retriever.get_recent_logs(hours, level)
            else:
                logs_data = log_retriever.get_recent_logs(hours)

            return jsonify(
                format_response(
                    data={
                        "logs": logs_data,
                        "count": len(logs_data),
                        "filters": {"hours": hours, "level": level, "service": service},
                    },
                    message=f"Retrieved {len(logs_data)} log entries",
                )
            )

        except Exception as e:
            logger.error(f"Logs endpoint error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to retrieve logs",
                    )
                ),
                500,
            )

    @app.route("/chatops/history", methods=["GET"])
    def chat_history():
        """Get conversation history."""
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        data={"error": "AI handler not available"},
                        status="error",
                        message="ChatOps functionality not available",
                    )
                ),
                503,
            )

        try:
            history = ai_handler.get_conversation_history()
            return jsonify(
                format_response(
                    data={"history": history, "count": len(history)},
                    message="Conversation history retrieved",
                )
            )
        except Exception as e:
            logger.error(f"History endpoint error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to retrieve conversation history",
                    )
                ),
                500,
            )

    @app.route("/chatops/clear", methods=["POST"])
    def clear_history():
        """Clear conversation history."""
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        data={"error": "AI handler not available"},
                        status="error",
                        message="ChatOps functionality not available",
                    )
                ),
                503,
            )

        try:
            success = ai_handler.clear_history()
            return jsonify(
                format_response(
                    data={"cleared": success}, message="Conversation history cleared"
                )
            )
        except Exception as e:
            logger.error(f"Clear history error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to clear conversation history",
                    )
                ),
                500,
            )

    @app.route("/chatops/info", methods=["GET"])
    def ai_info():
        """Get AI provider information."""
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        data={"error": "AI handler not available"},
                        status="error",
                        message="ChatOps functionality not available",
                    )
                ),
                503,
            )

        try:
            provider_info = ai_handler.get_provider_info()
            return jsonify(
                format_response(
                    data=provider_info, message="AI provider information retrieved"
                )
            )
        except Exception as e:
            logger.error(f"AI info endpoint error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to retrieve AI provider information",
                    )
                ),
                500,
            )

    # ML Anomaly Detection Endpoints
    @app.route("/anomaly", methods=["POST"])
    def detect_anomaly():
        """Detect anomalies in real-time metrics."""
        if not anomaly_detector:
            return (
                jsonify(
                    format_response(
                        data={"error": "Anomaly detection not available"},
                        status="error",
                        message="ML anomaly detection not available",
                    )
                ),
                503,
            )

        try:
            # Get metrics from request
            data = request.get_json()
            if not data:
                return (
                    jsonify(
                        format_response(
                            data={"error": "No metrics data provided"},
                            status="error",
                            message="Please provide metrics data in JSON format",
                        )
                    ),
                    400,
                )

            # Validate metrics
            is_valid, issues = anomaly_detector.validate_metrics(data)
            if not is_valid:
                return (
                    jsonify(
                        format_response(
                            data={"error": "Invalid metrics data", "issues": issues},
                            status="error",
                            message="Metrics validation failed",
                        )
                    ),
                    400,
                )

            # Perform anomaly detection
            start_time = time.time()
            result = anomaly_detector.detect_anomaly(data)
            inference_time = time.time() - start_time

            # Record metrics
            ANOMALY_INFERENCE_TIME.observe(inference_time)
            if result["status"] == "success" and result["is_anomaly"]:
                severity = (
                    "high"
                    if result["severity_score"] > 0.7
                    else "medium"
                    if result["severity_score"] > 0.4
                    else "low"
                )
                ANOMALY_DETECTIONS.labels(severity=severity).inc()
                # Trigger auto-remediation asynchronously (Phase 4)
                try:
                    from app.remediation import RemediationEngine

                    RemediationEngine().handle_anomaly_async(result)
                except Exception as rem_exc:
                    logger.warning(f"Remediation trigger failed: {rem_exc}")

            return jsonify(
                format_response(data=result, message="Anomaly detection completed")
            )

        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to perform anomaly detection",
                    )
                ),
                500,
            )

    @app.route("/anomaly/batch", methods=["POST"])
    def batch_detect_anomalies():
        """Detect anomalies in a batch of metrics."""
        if not anomaly_detector:
            return (
                jsonify(
                    format_response(
                        data={"error": "Anomaly detection not available"},
                        status="error",
                        message="ML anomaly detection not available",
                    )
                ),
                503,
            )

        try:
            # Get batch metrics from request
            data = request.get_json()
            if not data or not isinstance(data, list):
                return (
                    jsonify(
                        format_response(
                            data={"error": "No batch metrics data provided"},
                            status="error",
                            message="Please provide batch metrics data as JSON array",
                        )
                    ),
                    400,
                )

            # Validate each metrics entry
            for i, metrics in enumerate(data):
                is_valid, issues = anomaly_detector.validate_metrics(metrics)
                if not is_valid:
                    return (
                        jsonify(
                            format_response(
                                data={
                                    "error": f"Invalid metrics at index {i}",
                                    "issues": issues,
                                },
                                status="error",
                                message="Batch metrics validation failed",
                            )
                        ),
                        400,
                    )

            # Perform batch anomaly detection
            start_time = time.time()
            results = anomaly_detector.batch_detect(data)
            inference_time = time.time() - start_time

            # Record metrics
            ANOMALY_INFERENCE_TIME.observe(inference_time)
            anomaly_count = sum(
                1 for r in results if r["status"] == "success" and r["is_anomaly"]
            )
            if anomaly_count > 0:
                ANOMALY_DETECTIONS.labels(severity="batch").inc()

            return jsonify(
                format_response(
                    data={
                        "results": results,
                        "batch_size": len(data),
                        "anomaly_count": anomaly_count,
                        "inference_time": inference_time,
                    },
                    message="Batch anomaly detection completed",
                )
            )

        except Exception as e:
            logger.error(f"Batch anomaly detection error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to perform batch anomaly detection",
                    )
                ),
                500,
            )

    @app.route("/anomaly/train", methods=["POST"])
    def train_anomaly_model():
        """Train or retrain the anomaly detection model."""
        if not anomaly_detector:
            return (
                jsonify(
                    format_response(
                        data={"error": "Anomaly detection not available"},
                        status="error",
                        message="ML anomaly detection not available",
                    )
                ),
                503,
            )

        try:
            # Get training parameters from request
            data = request.get_json() or {}
            force_retrain = data.get("force_retrain", False)

            # Train model
            start_time = time.time()
            result = anomaly_detector.train_model(force_retrain=force_retrain)
            training_time = time.time() - start_time

            result["training_time"] = training_time

            return jsonify(
                format_response(data=result, message="Model training completed")
            )

        except Exception as e:
            logger.error(f"Model training error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to train model",
                    )
                ),
                500,
            )

    @app.route("/anomaly/status", methods=["GET"])
    def anomaly_status():
        """Get anomaly detection system status."""
        if not anomaly_detector:
            return (
                jsonify(
                    format_response(
                        data={"error": "Anomaly detection not available"},
                        status="error",
                        message="ML anomaly detection not available",
                    )
                ),
                503,
            )

        try:
            status = anomaly_detector.get_system_status()
            return jsonify(
                format_response(
                    data=status, message="Anomaly detection status retrieved"
                )
            )

        except Exception as e:
            logger.error(f"Status endpoint error: {str(e)}")
            return (
                jsonify(
                    format_response(
                        data={"error": str(e)},
                        status="error",
                        message="Failed to retrieve anomaly detection status",
                    )
                ),
                500,
            )

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal error: {str(error)}")
        SYSTEM_HEALTH.set(0)
        return jsonify({"error": "Internal server error"}), 500

    logger.info(
        f"Flask application created successfully - {config.APP_NAME} v{config.VERSION}"
    )
    return app


# Expose WSGI application instance for servers like Gunicorn (app.main:app)
app = create_app(os.getenv("FLASK_ENV", "development"))


def main():
    """Main entry point for the application."""
    # Determine environment
    env = os.getenv("FLASK_ENV", "development")
    config = get_config(env)

    # Create Flask app
    app = create_app(env)

    # Start the application
    port = int(os.getenv("PORT", 3000))
    debug = config.DEBUG

    logger.info("Starting Smart CloudOps AI Flask Application")
    logger.info(f"Environment: {env}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Port: {port}")
    logger.info(f"Metrics endpoint: http://localhost:{port}/metrics")

    try:
        app.run(host="0.0.0.0", port=port, debug=debug)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
