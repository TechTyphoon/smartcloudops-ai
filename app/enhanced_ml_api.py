"""
Phase 1: Enhanced ML API Endpoints
Advanced anomaly detection and predictive analytics features
"""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.config import Config
from ml_models.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)

# Create blueprint for enhanced ML features
enhanced_ml_bp = Blueprint("enhanced_ml", __name__, url_prefix="/api/v1/ml")

# Initialize the enhanced anomaly detector
try:
    anomaly_detector = AnomalyDetector()
    logger.info("Enhanced anomaly detector initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize enhanced anomaly detector: {e}")
    anomaly_detector = None


@enhanced_ml_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for enhanced ML features"""
    config = Config.from_env()

    return jsonify(
        {
            "status": "healthy",
            "service": "enhanced_ml",
            "version": "1.0.0",
            "features": {
                "enhanced_anomaly": config.get("enable_enhanced_anomaly", False),
                "multi_metric_correlation": config.get(
                    "enable_multi_metric_correlation", False
                ),
                "failure_prediction": config.get("enable_failure_prediction", False),
                "anomaly_explanation": config.get("enable_anomaly_explanation", False),
            },
            "detector_available": anomaly_detector is not None,
            "timestamp": datetime.now().isoformat(),
        }
    )


@enhanced_ml_bp.route("/multi-metric-anomaly", methods=["POST"])
def detect_multi_metric_anomaly():
    """
    Detect anomalies across multiple correlated metrics

    Expected payload:
    {
        "metrics": {
            "cpu": [{"value": 75, "timestamp": "2025-08-17T10:00:00Z"}, ...],
            "memory": [{"value": 80, "timestamp": "2025-08-17T10:00:00Z"}, ...],
            "disk": [{"value": 90, "timestamp": "2025-08-17T10:00:00Z"}, ...]
        }
    }
    """
    try:
        config = Config.from_env()

        # Check if feature is enabled
        if not config.get("enable_multi_metric_correlation", False):
            return (
                jsonify(
                    {
                        "status": "feature_disabled",
                        "message": "Multi-metric correlation analysis is disabled",
                        "feature_flag": "ENABLE_MULTI_METRIC_CORRELATION",
                    }
                ),
                403,
            )

        if not anomaly_detector:
            return (
                jsonify(
                    {"status": "error", "message": "Anomaly detector not available"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "metrics" not in data:
            return (
                jsonify(
                    {"status": "error", "message": "Missing 'metrics' in request body"}
                ),
                400,
            )

        metrics_dict = data["metrics"]

        # Validate metrics structure
        if not isinstance(metrics_dict, dict) or not metrics_dict:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Metrics must be a non-empty dictionary",
                    }
                ),
                400,
            )

        # Perform multi-metric anomaly detection
        result = anomaly_detector.detect_multi_metric_anomaly(metrics_dict)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Multi-metric anomaly detection failed: {e}")
        return (
            jsonify({"status": "error", "message": f"Analysis failed: {str(e)}"}),
            500,
        )


@enhanced_ml_bp.route("/failure-prediction", methods=["POST"])
def predict_failure():
    """
    Predict failure probability based on current metrics

    Expected payload:
    {
        "metrics": {
            "cpu_usage_percent": 85,
            "memory_usage_percent": 90,
            "disk_usage_percent": 75,
            "load_avg_1min": 2.5
        },
        "time_horizon": 3600
    }
    """
    try:
        config = Config.from_env()

        # Check if feature is enabled
        if not config.get("enable_failure_prediction", False):
            return (
                jsonify(
                    {
                        "status": "feature_disabled",
                        "message": "Failure prediction is disabled",
                        "feature_flag": "ENABLE_FAILURE_PREDICTION",
                    }
                ),
                403,
            )

        if not anomaly_detector:
            return (
                jsonify(
                    {"status": "error", "message": "Anomaly detector not available"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "metrics" not in data:
            return (
                jsonify(
                    {"status": "error", "message": "Missing 'metrics' in request body"}
                ),
                400,
            )

        metrics = data["metrics"]
        time_horizon = data.get("time_horizon", 3600)  # Default: 1 hour

        # Validate time horizon
        if not isinstance(time_horizon, int) or time_horizon <= 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "time_horizon must be a positive integer (seconds)",
                    }
                ),
                400,
            )

        # Perform failure prediction
        result = anomaly_detector.predict_failure_probability(metrics, time_horizon)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Failure prediction failed: {e}")
        return (
            jsonify({"status": "error", "message": f"Prediction failed: {str(e)}"}),
            500,
        )


@enhanced_ml_bp.route("/anomaly-explanation", methods=["POST"])
def explain_anomaly():
    """
    Get detailed explanation for a detected anomaly

    Expected payload:
    {
        "anomaly_result": {
            "is_anomaly": true,
            "severity": "high",
            "anomaly_score": -0.15,
            "metrics": {
                "cpu_usage_percent": 95,
                "memory_usage_percent": 88,
                "disk_usage_percent": 85
            }
        }
    }
    """
    try:
        config = Config.from_env()

        # Check if feature is enabled
        if not config.get("enable_anomaly_explanation", False):
            return (
                jsonify(
                    {
                        "status": "feature_disabled",
                        "message": "Anomaly explanation is disabled",
                        "feature_flag": "ENABLE_ANOMALY_EXPLANATION",
                    }
                ),
                403,
            )

        if not anomaly_detector:
            return (
                jsonify(
                    {"status": "error", "message": "Anomaly detector not available"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "anomaly_result" not in data:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Missing 'anomaly_result' in request body",
                    }
                ),
                400,
            )

        anomaly_result = data["anomaly_result"]

        # Validate anomaly result structure
        if not isinstance(anomaly_result, dict):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "anomaly_result must be a dictionary",
                    }
                ),
                400,
            )

        # Get explanation
        result = anomaly_detector.get_anomaly_explanation(anomaly_result)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Anomaly explanation failed: {e}")
        return (
            jsonify({"status": "error", "message": f"Explanation failed: {str(e)}"}),
            500,
        )


@enhanced_ml_bp.route("/features/status", methods=["GET"])
def get_feature_status():
    """Get status of all Phase 1 enhanced features"""
    try:
        config = Config.from_env()

        features = {
            "enhanced_anomaly": {
                "enabled": config.get("enable_enhanced_anomaly", False),
                "description": "Enhanced anomaly detection with advanced algorithms",
                "endpoints": ["/api/v1/ml/multi-metric-anomaly"],
            },
            "multi_metric_correlation": {
                "enabled": config.get("enable_multi_metric_correlation", False),
                "description": "Cross-metric correlation analysis for complex anomaly detection",
                "endpoints": ["/api/v1/ml/multi-metric-anomaly"],
            },
            "failure_prediction": {
                "enabled": config.get("enable_failure_prediction", False),
                "description": "Predictive failure analysis with time horizon forecasting",
                "endpoints": ["/api/v1/ml/failure-prediction"],
            },
            "anomaly_explanation": {
                "enabled": config.get("enable_anomaly_explanation", False),
                "description": "Explainable AI for anomaly detection results",
                "endpoints": ["/api/v1/ml/anomaly-explanation"],
            },
        }

        enabled_count = sum(1 for f in features.values() if f["enabled"])

        return (
            jsonify(
                {
                    "status": "success",
                    "phase": "Phase 1: Enhanced Anomaly Detection",
                    "total_features": len(features),
                    "enabled_features": enabled_count,
                    "features": features,
                    "detector_status": {
                        "available": anomaly_detector is not None,
                        "trained": (
                            anomaly_detector.is_trained if anomaly_detector else False
                        ),
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Feature status check failed: {e}")
        return (
            jsonify({"status": "error", "message": f"Status check failed: {str(e)}"}),
            500,
        )


@enhanced_ml_bp.route("/demo", methods=["GET"])
def demo_endpoints():
    """Demo endpoint showing Phase 1 capabilities"""
    try:
        config = Config.from_env()

        return (
            jsonify(
                {
                    "service": "Phase 1: Enhanced ML Features",
                    "version": "1.0.0",
                    "description": "Advanced anomaly detection and predictive analytics",
                    "capabilities": [
                        "Multi-metric correlation analysis",
                        "Predictive failure detection",
                        "Explainable AI for anomalies",
                        "Real-time anomaly scoring",
                    ],
                    "endpoints": {
                        "health": "GET /api/v1/ml/health",
                        "multi_metric_anomaly": "POST /api/v1/ml/multi-metric-anomaly",
                        "failure_prediction": "POST /api/v1/ml/failure-prediction",
                        "anomaly_explanation": "POST /api/v1/ml/anomaly-explanation",
                        "feature_status": "GET /api/v1/ml/features/status",
                    },
                    "feature_flags": {
                        "ENABLE_ENHANCED_ANOMALY": config.get(
                            "enable_enhanced_anomaly", False
                        ),
                        "ENABLE_MULTI_METRIC_CORRELATION": config.get(
                            "enable_multi_metric_correlation", False
                        ),
                        "ENABLE_FAILURE_PREDICTION": config.get(
                            "enable_failure_prediction", False
                        ),
                        "ENABLE_ANOMALY_EXPLANATION": config.get(
                            "enable_anomaly_explanation", False
                        ),
                    },
                    "sample_requests": {
                        "multi_metric_anomaly": {
                            "url": "/api/v1/ml/multi-metric-anomaly",
                            "method": "POST",
                            "body": {
                                "metrics": {
                                    "cpu": [
                                        {
                                            "value": 85,
                                            "timestamp": "2025-08-17T10:00:00Z",
                                        }
                                    ],
                                    "memory": [
                                        {
                                            "value": 90,
                                            "timestamp": "2025-08-17T10:00:00Z",
                                        }
                                    ],
                                }
                            },
                        },
                        "failure_prediction": {
                            "url": "/api/v1/ml/failure-prediction",
                            "method": "POST",
                            "body": {
                                "metrics": {
                                    "cpu_usage_percent": 85,
                                    "memory_usage_percent": 90,
                                    "disk_usage_percent": 75,
                                },
                                "time_horizon": 3600,
                            },
                        },
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Demo endpoint failed: {e}")
        return jsonify({"status": "error", "message": f"Demo failed: {str(e)}"}), 500
