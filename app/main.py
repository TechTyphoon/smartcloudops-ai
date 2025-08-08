#!/usr/bin/env python3
"""
Smart CloudOps AI - Flask Application (Phase 4)
ChatOps application with GPT integration, ML anomaly detection, and auto-remediation
"""

import logging
import os
import sys
import time
from datetime import datetime

from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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

# Import Phase 4 remediation components
try:
    from app.remediation.engine import RemediationEngine

    REMEDIATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Remediation components not available: {e}")
    REMEDIATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "flask_requests_total", "Total Flask HTTP requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "flask_request_duration_seconds", "Flask HTTP request latency"
)

# Phase 3: ML metrics
ML_PREDICTIONS = Counter(
    "ml_predictions_total", "Total ML predictions made", ["model_type"]
)
ML_ANOMALIES = Counter(
    "ml_anomalies_detected", "Total anomalies detected", ["severity"]
)
ML_TRAINING_RUNS = Counter(
    "ml_training_runs_total", "Total model training runs", ["status"]
)

# Phase 4: Remediation metrics
REMEDIATION_ACTIONS = Counter(
    "remediation_actions_total",
    "Total remediation actions executed",
    ["action_type", "severity"],
)
REMEDIATION_SUCCESS = Counter(
    "remediation_success_total", "Successful remediation actions", ["action_type"]
)
REMEDIATION_FAILURE = Counter(
    "remediation_failure_total", "Failed remediation actions", ["action_type", "reason"]
)

# Initialize components
config = get_config()
ai_handler = FlexibleAIHandler()
log_retriever = LogRetriever()
system_gatherer = SystemContextGatherer()

# Initialize ML components
if ML_AVAILABLE:
    anomaly_detector = AnomalyDetector()
    # Try to load existing model
    try:
        anomaly_detector.load_model()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load existing ML model: {e}")
else:
    anomaly_detector = None

# Initialize Phase 4 components
if REMEDIATION_AVAILABLE:
    # Convert config to dict if it's a class
    config_dict = config.__dict__ if hasattr(config, "__dict__") else {}
    remediation_engine = RemediationEngine(config_dict)
else:
    remediation_engine = None


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()

    if hasattr(request, "start_time"):
        REQUEST_LATENCY.observe(time.time() - request.start_time)

    return response


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Smart CloudOps AI - Flask Application",
            "status": "running",
            "version": "1.0.0-phase4",
            "features": {
                "chatops": True,
                "ml_anomaly_detection": ML_AVAILABLE,
                "auto_remediation": REMEDIATION_AVAILABLE,
            },
            "endpoints": {
                "chatops": ["/query", "/logs", "/chatops/history", "/chatops/clear"],
                "ml_anomaly_detection": [
                    "/anomaly",
                    "/anomaly/batch",
                    "/anomaly/status",
                    "/anomaly/train",
                ],
                "remediation": [
                    "/remediation/status",
                    "/remediation/evaluate",
                    "/remediation/execute",
                    "/remediation/test",
                ],
                "monitoring": ["/status", "/metrics"],
            },
        }
    )


@app.route("/status")
def status():
    return jsonify(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": "running",
            "components": {
                "ai_handler": {"status": "operational"} if ai_handler else None,
                "ml_models": {
                    "available": ML_AVAILABLE,
                    "status": anomaly_detector.get_system_status()
                    if anomaly_detector
                    else None,
                },
                "remediation_engine": remediation_engine.get_status()
                if remediation_engine
                else None,
            },
        }
    )


@app.route("/query", methods=["POST"])
def query():
    """ChatOps query endpoint with AI integration."""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify(
                    format_response(
                        {"error": "No data provided"}, "error", "Missing request data"
                    )
                ),
                400,
            )

        query_text = data.get("query", "")
        if not query_text:
            return (
                jsonify(
                    format_response(
                        {"error": "No query provided"},
                        "error",
                        "Missing query parameter",
                    )
                ),
                400,
            )

        # Validate query parameters
        validate_query_params(data)

        # Get system context
        system_context = system_gatherer.get_system_context()

        # Process query with AI
        response = ai_handler.process_query(query_text, system_context)

        # Return the response directly as expected by the test
        return jsonify(format_response(response))

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return (
            jsonify(
                format_response({"error": str(e)}, "error", "Query processing failed")
            ),
            500,
        )


@app.route("/logs")
def logs():
    """Retrieve system logs."""
    try:
        # Get query parameters
        hours = request.args.get("hours", 24, type=int)
        level = request.args.get("level", None)

        # Retrieve logs
        log_data = log_retriever.get_recent_logs(hours=hours, level=level)

        return jsonify(
            format_response(
                {"logs": log_data, "count": len(log_data)},
                "success",
                f"Retrieved {len(log_data)} log entries",
            )
        )

    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        return (
            jsonify(
                format_response({"error": str(e)}, "error", "Failed to retrieve logs")
            ),
            500,
        )


@app.route("/chatops/history", methods=["GET"])
def chat_history():
    """Get conversation history."""
    try:
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        {"error": "AI handler not available"},
                        "error",
                        "ChatOps functionality not available",
                    )
                ),
                503,
            )

        history = ai_handler.get_conversation_history()
        return jsonify(
            format_response(
                {"history": history, "count": len(history)},
                "success",
                "Conversation history retrieved",
            )
        )

    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return (
            jsonify(
                format_response(
                    {"error": str(e)},
                    "error",
                    "Failed to retrieve conversation history",
                )
            ),
            500,
        )


@app.route("/chatops/clear", methods=["POST"])
def clear_history():
    """Clear conversation history."""
    try:
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        {"error": "AI handler not available"},
                        "error",
                        "ChatOps functionality not available",
                    )
                ),
                503,
            )

        success = ai_handler.clear_history()
        return jsonify(
            format_response(
                {"cleared": success}, "success", "Conversation history cleared"
            )
        )

    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        return (
            jsonify(
                format_response(
                    {"error": str(e)}, "error", "Failed to clear conversation history"
                )
            ),
            500,
        )


# Phase 3: ML Anomaly Detection Endpoints


@app.route("/anomaly", methods=["POST"])
def detect_anomaly():
    """Detect anomalies in real-time."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        metrics = data.get("metrics", {})
        if not metrics:
            return jsonify({"error": "No metrics provided"}), 400

        # Detect anomaly
        result = anomaly_detector.detect_anomaly(metrics)

        # Update metrics
        ML_PREDICTIONS.labels(model_type="anomaly_detector").inc()
        if result.get("is_anomaly", False):
            severity = result.get("severity", "unknown")
            ML_ANOMALIES.labels(severity=severity).inc()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error detecting anomaly: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/anomaly/batch", methods=["POST"])
def batch_detect_anomaly():
    """Detect anomalies in batch."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        metrics_batch = data.get("metrics_batch", [])
        if not metrics_batch:
            return jsonify({"error": "No metrics batch provided"}), 400

        # Batch detect anomalies
        results = anomaly_detector.batch_detect(metrics_batch)

        return jsonify({"results": results, "count": len(results)})

    except Exception as e:
        logger.error(f"Error in batch anomaly detection: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/anomaly/status", methods=["GET"])
def ml_status():
    """Get ML system status."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        status = anomaly_detector.get_system_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting ML status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/anomaly/train", methods=["POST"])
def train_model():
    """Train or retrain the ML model."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        data = request.get_json() or {}
        force_retrain = data.get("force_retrain", False)

        # Train model
        result = anomaly_detector.train_model(force_retrain=force_retrain)

        # Update metrics
        status = result.get("status", "unknown")
        ML_TRAINING_RUNS.labels(status=status).inc()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({"error": str(e)}), 500


# Phase 4: Auto-Remediation Endpoints


@app.route("/remediation/status", methods=["GET"])
def remediation_status():
    """Get status of the remediation engine."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        status = remediation_engine.get_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting remediation status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remediation/evaluate", methods=["POST"])
def evaluate_anomaly():
    """Evaluate an anomaly and determine if remediation is needed."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        anomaly_score = data.get("anomaly_score", 0.0)
        metrics = data.get("metrics", {})

        if not isinstance(anomaly_score, (int, float)) or not 0 <= anomaly_score <= 1:
            return (
                jsonify({"error": "Invalid anomaly score. Must be between 0 and 1"}),
                400,
            )

        # Evaluate the anomaly
        evaluation = remediation_engine.evaluate_anomaly(anomaly_score, metrics)

        return jsonify(evaluation)

    except Exception as e:
        logger.error(f"Error evaluating anomaly: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remediation/execute", methods=["POST"])
def execute_remediation():
    """Execute remediation based on anomaly evaluation."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Execute remediation
        result = remediation_engine.execute_remediation(data)

        # Update metrics
        if result.get("executed", False):
            execution_results = result.get("execution_results", [])
            for exec_result in execution_results:
                action = exec_result.get("action", {})
                action_type = action.get("action", "unknown")
                severity = data.get("severity", "unknown")

                REMEDIATION_ACTIONS.labels(
                    action_type=action_type, severity=severity
                ).inc()

                if exec_result.get("result", {}).get("status") == "success":
                    REMEDIATION_SUCCESS.labels(action_type=action_type).inc()
                else:
                    reason = exec_result.get("result", {}).get("error", "unknown")
                    REMEDIATION_FAILURE.labels(
                        action_type=action_type, reason=reason
                    ).inc()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error executing remediation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remediation/test", methods=["POST"])
def test_remediation():
    """Test remediation with sample data."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        # Create test anomaly data
        test_anomaly_score = 0.85  # High severity
        test_metrics = {
            "cpu_usage_avg": 95.0,
            "memory_usage_pct": 88.0,
            "disk_usage_pct": 75.0,
            "network_bytes_total": 500000000,
            "response_time_p95": 2.5,
        }

        # Evaluate anomaly
        evaluation = remediation_engine.evaluate_anomaly(
            test_anomaly_score, test_metrics
        )

        # Execute remediation (if needed)
        if evaluation.get("needs_remediation", False):
            result = remediation_engine.execute_remediation(evaluation)
        else:
            result = {
                "executed": False,
                "reason": "No remediation needed for test data",
                "evaluation": evaluation,
            }

        return jsonify(
            {
                "test_data": {
                    "anomaly_score": test_anomaly_score,
                    "metrics": test_metrics,
                },
                "evaluation": evaluation,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error testing remediation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


# WSGI application object for Gunicorn
if __name__ == "__main__":
    logger.info("Starting Smart CloudOps AI Flask Application (Phase 4)")
    app.run(host="0.0.0.0", port=3000, debug=True)
