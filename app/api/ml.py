#!/usr/bin/env python3
"""
ML API Endpoints for SmartCloudOps AI
Provides AI-driven anomaly detection and model management
"""

import logging
import os
from typing import List, Dict
import numpy as np
from flask import Blueprint, request, jsonify
from app.auth import require_auth, require_admin

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")


class MLModelManager:
    """Manages ML models for anomaly detection"""

    def __init__(self, models_dir: str = "ml_models"):
        self.models_dir = models_dir
        self.anomaly_model = None
        self.scaler = None
        self.model_metadata = {}
        self._ensure_models_dir()
        self._load_models()

    def _ensure_models_dir(self):
        """Ensure models directory exists"""
        os.makedirs(self.models_dir, exist_ok=True)

    def _load_models(self):
        """Load trained models from disk"""
        try:
            model_path = os.path.join(self.models_dir, "anomaly_model.pkl")
            scaler_path = os.path.join(self.models_dir, "scaler.pkl")
            metadata_path = os.path.join(self.models_dir, "model_metadata.json")

            if os.path.exists(model_path):
                self.anomaly_model = joblib.load(model_path)
                logger.info("Loaded anomaly detection model")

            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded data scaler")

            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)
                logger.info("Loaded model metadata")

        except Exception as e:
            logger.error("Failed to load models: {e}")

    def _save_models(self):
        """Save trained models to disk"""
        try:
            if self.anomaly_model:
                model_path = os.path.join(self.models_dir, "anomaly_model.pkl")
                joblib.dump(self.anomaly_model, model_path)

            if self.scaler:
                scaler_path = os.path.join(self.models_dir, "scaler.pkl")
                joblib.dump(self.scaler, scaler_path)

            metadata_path = os.path.join(self.models_dir, "model_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(self.model_metadata, f, indent=2)

            logger.info("Models saved successfully")

        except Exception as e:
            logger.error("Failed to save models: {e}")
            raise

    def prepare_features(self, metrics_data: List[Dict]) -> np.ndarray:
        """Prepare features from metrics data"""
        if not metrics_data:
            return np.array([])

        # Extract relevant features
        features = []
        for metric in metrics_data:
            feature_vector = [
                metric.get("cpu_usage", 0),
                metric.get("memory_usage", 0),
                metric.get("disk_usage", 0),
                metric.get("network_in", 0),
                metric.get("network_out", 0),
                metric.get("response_time", 0),
                metric.get("error_rate", 0),
                metric.get("active_connections", 0),
            ]
            features.append(feature_vector)

        return np.array(features)

    def train_anomaly_model(self, metrics_data: List[Dict], **kwargs) -> Dict:
        """Train anomaly detection model"""
        logger.info("Starting anomaly model training")

        # Prepare features
        X = self.prepare_features(metrics_data)
        if len(X) == 0:
            raise ValueError("No metrics data available for training")

        # Initialize scaler if not exists
        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)

        # Train Isolation Forest
        contamination = kwargs.get("contamination", 0.1)
        n_estimators = kwargs.get("n_estimators", 100)
        random_state = kwargs.get("random_state", 42)

        self.anomaly_model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
        )

        # Train the model
        self.anomaly_model.fit(X_scaled)

        # Update metadata
        self.model_metadata = {
            "model_type": "IsolationForest",
            "training_date": datetime.now().isoformat(),
            "n_samples": len(X),
            "n_features": X.shape[1],
            "contamination": contamination,
            "n_estimators": n_estimators,
            "feature_names": [
                "cpu_usage",
                "memory_usage",
                "disk_usage",
                "network_in",
                "network_out",
                "response_time",
                "error_rate",
                "active_connections",
            ],
        }

        # Save models
        self._save_models()

        logger.info("Anomaly model trained successfully with {len(X)} samples")

        return {
            "status": "success",
            "message": "Model trained successfully",
            "metadata": self.model_metadata,
        }

    def detect_anomalies(
        self, metrics_data: List[Dict], threshold: float = -0.5
    ) -> List[Dict]:
        """Detect anomalies in metrics data"""
        if self.anomaly_model is None or self.scaler is None:
            raise ValueError("Model not trained. Please train the model first.")

        # Prepare features
        X = self.prepare_features(metrics_data)
        if len(X) == 0:
            return []

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Predict anomalies
        anomaly_scores = self.anomaly_model.decision_function(X_scaled)
        predictions = self.anomaly_model.predict(X_scaled)

        # Identify anomalies
        anomalies = []
        for i, (score, prediction) in enumerate(zip(anomaly_scores, predictions)):
            if score < threshold or prediction == -1:
                anomaly_info = {
                    "timestamp": metrics_data[i].get("timestamp"),
                    "anomaly_score": float(score),
                    "is_anomaly": True,
                    "metrics": metrics_data[i],
                    "severity": self._calculate_severity(score),
                    "features": {
                        "cpu_usage": metrics_data[i].get("cpu_usage", 0),
                        "memory_usage": metrics_data[i].get("memory_usage", 0),
                        "disk_usage": metrics_data[i].get("disk_usage", 0),
                        "response_time": metrics_data[i].get("response_time", 0),
                        "error_rate": metrics_data[i].get("error_rate", 0),
                    },
                }
                anomalies.append(anomaly_info)

        return anomalies

    def _calculate_severity(self, score: float) -> str:
        """Calculate anomaly severity based on score"""
        if score < -0.8:
            return "critical"
        elif score < -0.6:
            return "high"
        elif score < -0.4:
            return "medium"
        else:
            return "low"

    def get_model_info(self) -> Dict:
        """Get information about the trained model"""
        return {
            "model_loaded": self.anomaly_model is not None,
            "scaler_loaded": self.scaler is not None,
            "metadata": self.model_metadata,
        }

    def retrain_model(self, metrics_data: List[Dict], **kwargs) -> Dict:
        """Retrain the model with new data"""
        logger.info("Retraining anomaly detection model")
        return self.train_anomaly_model(metrics_data, **kwargs)


# Initialize ML model manager
ml_manager = MLModelManager()


@ml_bp.route("/anomalies", methods=["POST"])
@require_auth
def detect_anomalies():
    """Detect anomalies in provided metrics data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        metrics_data = data.get("metrics", [])
        threshold = data.get("threshold", -0.5)

        if not metrics_data:
            return (
                jsonify({"status": "error", "message": "No metrics data provided"}),
                400,
            )

        # Detect anomalies
        anomalies = ml_manager.detect_anomalies(metrics_data, threshold)

        # Store anomalies in database
        session = get_db_session()
        try:
            for anomaly_data in anomalies:
                anomaly = Anomaly(
                    timestamp=datetime.fromisoformat(anomaly_data["timestamp"]),
                    severity=anomaly_data["severity"],
                    description="ML detected anomaly with score {anomaly_data['anomaly_score']:.3f}",
                    metrics_data=anomaly_data["metrics"],
                    source="ml_model",
                    status="new",
                )
                session.add(anomaly)

            session.commit()

        except Exception as e:
            session.rollback()
            logger.error("Failed to store anomalies: {e}")

        return jsonify(
            {
                "status": "success",
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
            }
        )

    except Exception as e:
        logger.error("Error in anomaly detection: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/anomalies/realtime", methods=["GET"])
@require_auth
def realtime_anomaly_detection():
    """Perform real-time anomaly detection on recent metrics"""
    try:
        # Get recent metrics from database
        session = get_db_session()
        try:
            # Get metrics from last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = (
                session.query(SystemMetrics)
                .filter(SystemMetrics.timestamp >= one_hour_ago)
                .order_by(SystemMetrics.timestamp.desc())
                .limit(100)
                .all()
            )

            # Convert to list of dictionaries
            metrics_data = []
            for metric in recent_metrics:
                metrics_data.append(
                    {
                        "timestamp": metric.timestamp.isoformat(),
                        "cpu_usage": metric.cpu_usage,
                        "memory_usage": metric.memory_usage,
                        "disk_usage": metric.disk_usage,
                        "network_in": metric.network_in,
                        "network_out": metric.network_out,
                        "response_time": metric.response_time,
                        "error_rate": metric.error_rate,
                        "active_connections": metric.active_connections,
                    }
                )

        except Exception as e:
            session.rollback()
            logger.error("Failed to fetch metrics: {e}")
            return (
                jsonify({"status": "error", "message": "Failed to fetch metrics data"}),
                500,
            )

        if not metrics_data:
            return jsonify(
                {
                    "status": "success",
                    "anomalies_detected": 0,
                    "message": "No recent metrics data available",
                }
            )

        # Detect anomalies
        anomalies = ml_manager.detect_anomalies(metrics_data)

        return jsonify(
            {
                "status": "success",
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "metrics_analyzed": len(metrics_data),
            }
        )

    except Exception as e:
        logger.error("Error in real-time anomaly detection: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/train", methods=["POST"])
@require_admin
def train_model():
    """Train the anomaly detection model"""
    try:
        data = request.get_json() or {}

        # Get training data from database
        session = get_db_session()
        try:
            # Get historical metrics for training
            training_days = data.get("training_days", 7)
            start_date = datetime.now() - timedelta(days=training_days)

            training_metrics = (
                session.query(SystemMetrics)
                .filter(SystemMetrics.timestamp >= start_date)
                .order_by(SystemMetrics.timestamp.asc())
                .all()
            )

            # Convert to list of dictionaries
            metrics_data = []
            for metric in training_metrics:
                metrics_data.append(
                    {
                        "timestamp": metric.timestamp.isoformat(),
                        "cpu_usage": metric.cpu_usage,
                        "memory_usage": metric.memory_usage,
                        "disk_usage": metric.disk_usage,
                        "network_in": metric.network_in,
                        "network_out": metric.network_out,
                        "response_time": metric.response_time,
                        "error_rate": metric.error_rate,
                        "active_connections": metric.active_connections,
                    }
                )

        except Exception as e:
            session.rollback()
            logger.error("Failed to fetch training data: {e}")
            return (
                jsonify(
                    {"status": "error", "message": "Failed to fetch training data"}
                ),
                500,
            )

        if len(metrics_data) < 100:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Insufficient training data. Need at least 100 samples, got {len(metrics_data)}",
                    }
                ),
                400,
            )

        # Train model
        training_params = {
            "contamination": data.get("contamination", 0.1),
            "n_estimators": data.get("n_estimators", 100),
            "random_state": data.get("random_state", 42),
        }

        result = ml_manager.train_anomaly_model(metrics_data, **training_params)

        # Log training event
        try:
            audit_log = AuditLog(
                user_id=request.user.get("id"),
                action="ml_model_training",
                details=f"Trained anomaly detection model with {len(metrics_data)} samples",
                timestamp=datetime.now(),
            )
            session.add(audit_log)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Failed to log training event: {e}")

        return jsonify(result)

    except Exception as e:
        logger.error("Error in model training: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/model/info", methods=["GET"])
@require_auth
def get_model_info():
    """Get information about the trained model"""
    try:
        model_info = ml_manager.get_model_info()
        return jsonify({"status": "success", "model_info": model_info})

    except Exception as e:
        logger.error("Error getting model info: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/model/retrain", methods=["POST"])
@require_admin
def retrain_model():
    """Retrain the model with new data"""
    try:
        data = request.get_json() or {}

        # Get recent data for retraining
        session = get_db_session()
        try:
            retraining_days = data.get("retraining_days", 3)
            start_date = datetime.now() - timedelta(days=retraining_days)

            recent_metrics = (
                session.query(SystemMetrics)
                .filter(SystemMetrics.timestamp >= start_date)
                .order_by(SystemMetrics.timestamp.asc())
                .all()
            )

            # Convert to list of dictionaries
            metrics_data = []
            for metric in recent_metrics:
                metrics_data.append(
                    {
                        "timestamp": metric.timestamp.isoformat(),
                        "cpu_usage": metric.cpu_usage,
                        "memory_usage": metric.memory_usage,
                        "disk_usage": metric.disk_usage,
                        "network_in": metric.network_in,
                        "network_out": metric.network_out,
                        "response_time": metric.response_time,
                        "error_rate": metric.error_rate,
                        "active_connections": metric.active_connections,
                    }
                )

        except Exception as e:
            session.rollback()
            logger.error("Failed to fetch retraining data: {e}")
            return (
                jsonify(
                    {"status": "error", "message": "Failed to fetch retraining data"}
                ),
                500,
            )

        if len(metrics_data) < 50:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Insufficient data for retraining. Need at least 50 samples, got {len(metrics_data)}",
                    }
                ),
                400,
            )

        # Retrain model
        retraining_params = {
            "contamination": data.get("contamination", 0.1),
            "n_estimators": data.get("n_estimators", 100),
            "random_state": data.get("random_state", 42),
        }

        result = ml_manager.retrain_model(metrics_data, **retraining_params)

        # Log retraining event
        try:
            audit_log = AuditLog(
                user_id=request.user.get("id"),
                action="ml_model_retraining",
                details=f"Retrained anomaly detection model with {len(metrics_data)} samples",
                timestamp=datetime.now(),
            )
            session.add(audit_log)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Failed to log retraining event: {e}")

        return jsonify(result)

    except Exception as e:
        logger.error("Error in model retraining: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/predictions", methods=["GET"])
@require_auth
def get_recent_predictions():
    """Get recent anomaly predictions"""
    try:
        session = get_db_session()

        # Get recent ML-detected anomalies
        recent_anomalies = (
            session.query(Anomaly)
            .filter(Anomaly.source == "ml_model")
            .order_by(Anomaly.timestamp.desc())
            .limit(50)
            .all()
        )

        predictions = []
        for anomaly in recent_anomalies:
            predictions.append(
                {
                    "id": anomaly.id,
                    "timestamp": anomaly.timestamp.isoformat(),
                    "severity": anomaly.severity,
                    "description": anomaly.description,
                    "status": anomaly.status,
                    "metrics_data": anomaly.metrics_data,
                }
            )

        return jsonify(
            {
                "status": "success",
                "predictions": predictions,
                "total_predictions": len(predictions),
            }
        )

    except Exception as e:
        logger.error("Error getting predictions: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ml_bp.route("/performance", methods=["GET"])
@require_auth
def get_model_performance():
    """Get model performance metrics"""
    try:
        session = get_db_session()

        # Calculate performance metrics
        total_anomalies = (
            session.query(Anomaly).filter(Anomaly.source == "ml_model").count()
        )

        recent_anomalies = (
            session.query(Anomaly)
            .filter(
                Anomaly.source == "ml_model",
                Anomaly.timestamp >= datetime.now() - timedelta(days=7),
            )
            .count()
        )

        # Get model info
        model_info = ml_manager.get_model_info()

        performance_metrics = {
            "total_anomalies_detected": total_anomalies,
            "anomalies_last_7_days": recent_anomalies,
            "model_loaded": model_info.get("model_loaded", False),
            "last_training": model_info.get("metadata", {}).get("training_date"),
            "training_samples": model_info.get("metadata", {}).get("n_samples", 0),
        }

        return jsonify(
            {"status": "success", "performance_metrics": performance_metrics}
        )

    except Exception as e:
        logger.error("Error getting performance metrics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
