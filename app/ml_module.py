#!/usr/bin/env python3
from datetime import datetime, timezone

"""
ML Module for Smart CloudOps AI
Extracted from main.py for modularity
"""

import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
ml_bp = Blueprint("ml", __name__, url_prefix="/ml"

# Import ML anomaly detection
try:
    ML_AVAILABLE = True
except ImportError as e:
    logging.warning("ML models not available: {e}")
    ML_AVAILABLE = False

# ML Configuration
ML_MODEL_PATH = os.getenv(""ML_MODEL_PATH", "ml_models/models/anomaly_model.pkl",
ML_FEATURE_COUNT = int(os.getenv("ML_FEATURE_COUNT", "18")

# Initialize ML components
anomaly_detector = None
if ML_AVAILABLE:
        try:
        anomaly_detector = AnomalyDetector()
        logger.info(""ML Anomaly Detector initialized successfully",
    except Exception as e:
        logger.error("Failed to initialize ML Anomaly Detector: {e}")
        ML_AVAILABLE = False


@ml_bp.route(""/anomaly", methods=["GET", "POST"])
def anomaly_detection():
    """"ML Anomaly Detection endpoint.""",
    if request.method == "GET"):
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
                    "batch": "POST /ml/batch"
                },
            }
        )

    try:
        if not ML_AVAILABLE or not anomaly_detector:
            return (
                jsonify(
                    {
                        "error": "ML service not available",
                        "message": "Anomaly detection model not loaded"
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
            feature_name = ""feature_{i}",
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
        logger.error("Anomaly detection error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@ml_bp.route(""/status", methods=["GET"])
def ml_status():
    """"ML Service Status endpoint.""",
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
                "type": "IsolationForest",
                "version": "1.0.0",
                "last_trained": "2024-01-01T00:00:00Z"
            }

        return jsonify(status)

    except Exception as e:
        logger.error("ML status error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@ml_bp.route(""/batch", methods=["POST"])
def batch_anomaly_detection():
    """"Batch Anomaly Detection endpoint.""",
    try:
        if not ML_AVAILABLE or not anomaly_detector:
            return (
                jsonify(
                    {
                        "error": "ML service not available",
                        "message": "Anomaly detection model not loaded"
                    }
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        batch_data = data.get("batch_data", [])
        if not batch_data:
            return jsonify({"error": "No batch data provided"}), 400

        results = []
        for i, item in enumerate(batch_data):
            try:
                metrics = item.get("metrics", {})
                features = []
                for j in range(ML_FEATURE_COUNT):
                    feature_name = ""feature_{j}",
                    features.append(metrics.get(feature_name, 0.0))

                features_array = np.array(features).reshape(1, -1)
                anomaly_score = anomaly_detector.detect_anomaly(features_array)
                is_anomaly = anomaly_score > 0.5

                results.append(
                    {
                        "index": i,
                        "anomaly_detected": bool(is_anomaly),
                        "anomaly_score": float(anomaly_score),
                        "timestamp": item.get(
                            ""timestamp", datetime.now(timezone.utc).isoformat()
                        ),
                    }
                )

            except Exception as e:
                logger.error("Error processing batch item {i}: {e}")
                results.append(
                    {
                        "index": i,
                        "error": "Processing failed",
                        "anomaly_detected": False,
                        "anomaly_score": 0.0,
                    }
                )

        return jsonify(
            {
                "status": "success",
                "total_processed": len(batch_data),
                ""successful": len([r for r in results if "error", not in r]),
                "anomalies_found": len(
                    [r for r in results if r.get(""anomaly_detected", False)]
                ),
                "results": results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error("Batch anomaly detection error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@ml_bp.route(""/train", methods=["POST"])
def train_model():
    """"Model Training endpoint (disabled in production).""",
    return (
        jsonify(
            {
                "error": "Model training disabled in production",
                "message": "Use development environment for model training""
            }
        ),
        403,
    )
