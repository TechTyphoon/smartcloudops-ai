#!/usr/bin/env python3
"""
Inference Engine for ML Anomaly Detection
Handles real-time anomaly detection, severity scoring, and explanations
"""

import pandas as pd
import numpy as np
import joblib
import yaml
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class AnomalyInferenceEngine:
    """Handles real-time anomaly detection and inference."""

    def __init__(
        self,
        model_path: str = "ml_models/models/anomaly_model.pkl",
        config_path: str = "ml_models/config.yaml",
    ):
        """Initialize inference engine with trained model."""
        self.config = self._load_config(config_path)
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.thresholds = self.config.get("thresholds", {})
        self.cache = {}
        self.cache_duration = self.config.get("inference", {}).get(
            "cache_duration_seconds", 300
        )

        # Don't try to load model during initialization to avoid errors in tests
        # Model will be loaded when needed

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is missing."""
        return {
            "thresholds": {
                "anomaly_score": -0.5,
                "severity_levels": {
                    "low": [-0.5, -0.3],
                    "medium": [-0.3, -0.1],
                    "high": [-0.1, 1.0],
                },
            },
            "inference": {"cache_duration_seconds": 300},
        }

    def load_model(self, model_path: str) -> bool:
        """Load the trained model and scaler."""
        try:
            # Load model
            self.model = joblib.load(model_path)

            # Load scaler
            scaler_path = model_path.replace("anomaly_model.pkl", "scaler.pkl")
            self.scaler = joblib.load(scaler_path)

            # Load feature columns
            features_path = model_path.replace("anomaly_model.pkl", "features.pkl")
            self.feature_columns = joblib.load(features_path)

            logger.info(
                f"Model loaded successfully with {len(self.feature_columns)} features"
            )
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def detect_anomalies(self, metrics_data: Dict) -> Tuple[bool, float, str]:
        """
        Detect anomalies in real-time metrics data.

        Args:
            metrics_data: Dictionary containing metric values

        Returns:
            Tuple of (is_anomaly, severity_score, explanation)
        """
        try:
            if self.model is None:
                return False, 0.0, "Model not loaded"

            # Check cache first
            cache_key = self._create_cache_key(metrics_data)
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_duration:
                    return cache_entry["result"]

            # Prepare features
            feature_vector = self._prepare_features(metrics_data)
            if feature_vector is None:
                return False, 0.0, "Invalid feature data"

            # Scale features
            feature_scaled = self.scaler.transform([feature_vector])

            # Make prediction
            start_time = time.time()
            anomaly_score = self.model.decision_function(feature_scaled)[0]
            prediction = self.model.predict(feature_scaled)[0]
            inference_time = (
                time.time() - start_time
            ) * 1000  # Convert to milliseconds

            # Determine if anomaly
            is_anomaly = prediction == -1

            # Calculate severity score (normalize to 0-1 range)
            severity_score = self._calculate_severity_score(anomaly_score)

            # Generate explanation
            explanation = self._explain_anomaly(
                metrics_data, anomaly_score, severity_score, inference_time
            )

            result = (is_anomaly, severity_score, explanation)

            # Cache result
            self.cache[cache_key] = {"result": result, "timestamp": time.time()}

            # Clean old cache entries
            self._clean_cache()

            return result

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return False, 0.0, f"Error during detection: {str(e)}"

    def _prepare_features(self, metrics_data: Dict) -> Optional[np.ndarray]:
        """Prepare feature vector from metrics data."""
        try:
            # Create feature vector with default values
            feature_vector = []

            for feature in self.feature_columns:
                if feature in metrics_data:
                    value = metrics_data[feature]
                    # Handle NaN and infinite values
                    if pd.isna(value) or np.isinf(value):
                        value = 0.0
                    feature_vector.append(float(value))
                else:
                    # Use default value for missing features
                    feature_vector.append(0.0)

            return np.array(feature_vector)

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None

    def _calculate_severity_score(self, anomaly_score: float) -> float:
        """Calculate severity score from anomaly score."""
        # Normalize anomaly score to 0-1 range
        # Isolation Forest scores are typically negative for anomalies
        # We want higher values to indicate higher severity

        # Convert to positive scale and normalize
        normalized_score = max(0, -anomaly_score)  # Make positive

        # Apply sigmoid-like transformation for better scaling
        severity = 1 / (1 + np.exp(-normalized_score * 5))

        return min(1.0, max(0.0, severity))

    def _explain_anomaly(
        self,
        metrics_data: Dict,
        anomaly_score: float,
        severity_score: float,
        inference_time: float,
    ) -> str:
        """Generate human-readable explanation for anomaly detection."""
        try:
            if severity_score == 0.0:
                return "No anomalies detected. System metrics are within normal ranges."

            # Determine severity level
            severity_level = self._get_severity_level(severity_score)

            # Find contributing factors
            contributing_factors = self._identify_contributing_factors(metrics_data)

            explanation_parts = [
                f"Anomaly detected with {severity_level} severity (score: {severity_score:.3f})",
                f"Inference time: {inference_time:.1f}ms",
            ]

            if contributing_factors:
                explanation_parts.append(
                    f"Contributing factors: {', '.join(contributing_factors)}"
                )

            # Add recommendations based on severity
            recommendations = self._get_recommendations(
                severity_level, contributing_factors
            )
            if recommendations:
                explanation_parts.append(f"Recommendations: {recommendations}")

            return ". ".join(explanation_parts)

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Anomaly detected (severity: {severity_score:.3f})"

    def _get_severity_level(self, severity_score: float) -> str:
        """Get severity level based on score."""
        severity_levels = self.thresholds.get("severity_levels", {})

        if severity_score >= severity_levels.get("high", [0.8, 1.0])[0]:
            return "HIGH"
        elif severity_score >= severity_levels.get("medium", [0.4, 0.7])[0]:
            return "MEDIUM"
        else:
            return "LOW"

    def _identify_contributing_factors(self, metrics_data: Dict) -> List[str]:
        """Identify metrics that might be contributing to the anomaly."""
        factors = []

        # Check CPU usage
        if "cpu_usage_avg" in metrics_data:
            cpu_usage = metrics_data["cpu_usage_avg"]
            if cpu_usage > 80:
                factors.append("High CPU usage")
            elif cpu_usage > 60:
                factors.append("Elevated CPU usage")

        # Check memory usage
        if "memory_usage_pct" in metrics_data:
            memory_usage = metrics_data["memory_usage_pct"]
            if memory_usage > 85:
                factors.append("High memory usage")
            elif memory_usage > 70:
                factors.append("Elevated memory usage")

        # Check disk usage
        if "disk_usage_pct" in metrics_data:
            disk_usage = metrics_data["disk_usage_pct"]
            if disk_usage > 90:
                factors.append("High disk usage")
            elif disk_usage > 80:
                factors.append("Elevated disk usage")

        # Check response time
        if "response_time_p95" in metrics_data:
            response_time = metrics_data["response_time_p95"]
            if response_time > 1.0:
                factors.append("High response time")
            elif response_time > 0.5:
                factors.append("Elevated response time")

        return factors

    def _get_recommendations(
        self, severity_level: str, contributing_factors: List[str]
    ) -> str:
        """Get recommendations based on severity level and factors."""
        recommendations = []

        if severity_level == "HIGH":
            recommendations.append("Immediate investigation required")
            if "High CPU usage" in contributing_factors:
                recommendations.append("Consider scaling up CPU resources")
            if "High memory usage" in contributing_factors:
                recommendations.append("Check for memory leaks or increase memory")
            if "High disk usage" in contributing_factors:
                recommendations.append("Clean up disk space or expand storage")

        elif severity_level == "MEDIUM":
            recommendations.append("Monitor closely and investigate if persistent")
            if "Elevated CPU usage" in contributing_factors:
                recommendations.append("Monitor CPU trends")
            if "Elevated memory usage" in contributing_factors:
                recommendations.append("Monitor memory usage patterns")

        else:  # LOW
            recommendations.append("Continue monitoring")

        return "; ".join(recommendations)

    def _create_cache_key(self, metrics_data: Dict) -> str:
        """Create cache key from metrics data."""
        # Create a hash of the metrics data for caching
        sorted_items = sorted(metrics_data.items())
        return str(hash(str(sorted_items)))

    def _clean_cache(self) -> None:
        """Clean old cache entries."""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self.cache.items()
            if current_time - entry["timestamp"] > self.cache_duration
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

    def batch_detect(self, metrics_batch: List[Dict]) -> List[Tuple[bool, float, str]]:
        """Detect anomalies in a batch of metrics."""
        results = []

        for metrics in metrics_batch:
            result = self.detect_anomalies(metrics)
            results.append(result)

        return results

    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if self.model is None:
            return {"status": "No model loaded"}

        return {
            "model_type": type(self.model).__name__,
            "feature_count": len(self.feature_columns),
            "feature_columns": self.feature_columns,
            "cache_size": len(self.cache),
            "cache_duration": self.cache_duration,
        }

    def clear_cache(self) -> None:
        """Clear the inference cache."""
        self.cache.clear()
        logger.info("Inference cache cleared")
