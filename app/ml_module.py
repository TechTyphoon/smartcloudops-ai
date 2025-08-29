#!/usr/bin/env python3
"""
ML Module for Smart CloudOps AI
Extracted from main.py for modularity
"""

import logging
import os
from datetime import datetime, timezone

import numpy as np
from flask import Blueprint, jsonify, request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
ml_bp = Blueprint("ml", __name__, url_prefix="/ml")

# Import ML anomaly detection
try:
    from ml_models.anomaly_detector import AnomalyDetector

    ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML models not available: {e}")
    ML_AVAILABLE = False

# ML Configuration
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "ml_models/models/anomaly_model.pkl")
ML_FEATURE_COUNT = int(os.getenv("ML_FEATURE_COUNT", "18"))

# Initialize ML components
anomaly_detector = None
if ML_AVAILABLE:
    try:
        anomaly_detector = AnomalyDetector()
        logger.info("ML Anomaly Detector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ML Anomaly Detector: {e}")
        ML_AVAILABLE = False


@ml_bp.route("/anomaly", methods=["GET", "POST"])
def anomaly_detection():
    """ML Anomaly Detection endpoint."""
    if request.method == "GET":
        return jsonify(
            {
                "status": "success",
                "message": "ML Anomaly Detection Service",
                "ml_available": ML_AVAILABLE,
                "model_path": ML_MODEL_PATH,
                "feature_count": ML_FEATURE_COUNT,
                "endpoints": {
                    "detect": "POST /ml/anomaly",
                    "status": "GET /ml/status",
                    "batch": "POST /ml/batch",
                },
            }
        )

    try:
        if not ML_AVAILABLE or not anomaly_detector:
            return (
                jsonify(
                    {
                        "error": "ML service not available",
                        "message": "Anomaly detection model not loaded",
                    }
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract metrics from request
        metrics = data.get("metrics", {})
        if not metrics:
            return jsonify({"error": "No metrics provided"}), 400

        # Convert metrics to feature vector
        features = []
        for i in range(ML_FEATURE_COUNT):
            feature_name = f"feature_{i}"
            features.append(metrics.get(feature_name, 0.0))

        # Perform anomaly detection
        features_array = np.array(features).reshape(1, -1)
        anomaly_score = anomaly_detector.detect_anomaly(features_array)
        is_anomaly = anomaly_score > 0.5  # Threshold

        return jsonify(
            {
                "status": "success",
                "anomaly_detected": bool(is_anomaly),
                "anomaly_score": float(anomaly_score),
                "threshold": 0.5,
                "features_used": len(features),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        return (jsonify({"error": "Anomaly detection failed", "message": str(e)}), 500)


@ml_bp.route("/status", methods=["GET"])
def ml_status():
    """ML service status endpoint."""
    try:
        status = {
            "status": "success",
            "ml_available": ML_AVAILABLE,
            "model_loaded": anomaly_detector is not None,
            "model_path": ML_MODEL_PATH,
            "feature_count": ML_FEATURE_COUNT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if ML_AVAILABLE and anomaly_detector:
            status["model_info"] = {
                "type": "anomaly_detection",
                "algorithm": "isolation_forest",
                "features": ML_FEATURE_COUNT,
                "threshold": 0.5,
            }

        return jsonify(status)

    except Exception as e:
        logger.error(f"ML status error: {e}")
        return (jsonify({"error": "Failed to get ML status", "message": str(e)}), 500)


@ml_bp.route("/batch", methods=["POST"])
def batch_anomaly_detection():
    """Batch anomaly detection endpoint."""
    try:
        if not ML_AVAILABLE or not anomaly_detector:
            return (
                jsonify(
                    {
                        "error": "ML service not available",
                        "message": "Anomaly detection model not loaded",
                    }
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract batch metrics
        batch_metrics = data.get("batch_metrics", [])
        if not batch_metrics:
            return jsonify({"error": "No batch metrics provided"}), 400

        results = []
        for i, metrics in enumerate(batch_metrics):
            try:
                # Convert metrics to feature vector
                features = []
                for j in range(ML_FEATURE_COUNT):
                    feature_name = f"feature_{j}"
                    features.append(metrics.get(feature_name, 0.0))

                # Perform anomaly detection
                features_array = np.array(features).reshape(1, -1)
                anomaly_score = anomaly_detector.detect_anomaly(features_array)
                is_anomaly = anomaly_score > 0.5

                results.append(
                    {
                        "index": i,
                        "anomaly_detected": bool(is_anomaly),
                        "anomaly_score": float(anomaly_score),
                        "features_used": len(features),
                    }
                )

            except Exception as e:
                logger.error(f"Error processing batch item {i}: {e}")
                results.append(
                    {
                        "index": i,
                        "error": str(e),
                        "anomaly_detected": False,
                        "anomaly_score": 0.0,
                    }
                )

        return jsonify(
            {
                "status": "success",
                "results": results,
                "total_processed": len(results),
                "anomalies_found": sum(
                    1 for r in results if r.get("anomaly_detected", False)
                ),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Batch anomaly detection error: {e}")
        return (
            jsonify({"error": "Batch anomaly detection failed", "message": str(e)}),
            500,
        )


@ml_bp.route("/health", methods=["GET"])
def ml_health():
    """ML service health check."""
    try:
        health_status = {
            "status": "healthy" if ML_AVAILABLE else "unavailable",
            "ml_available": ML_AVAILABLE,
            "model_loaded": anomaly_detector is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if ML_AVAILABLE:
            health_status["components"] = {
                "anomaly_detector": "available" if anomaly_detector else "unavailable",
                "model_file": (
                    "available" if os.path.exists(ML_MODEL_PATH) else "missing"
                ),
            }
        else:
            health_status["components"] = {
                "anomaly_detector": "unavailable",
                "model_file": "unknown",
            }

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"ML health check error: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            500,
        )
