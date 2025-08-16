#!/usr/bin/env python3
"""
Smart CloudOps AI - ML Models Implementation (Phase 3)
Anomaly Detection and Machine Learning Components
"""

import logging
import os
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Machine Learning-based anomaly detection for system metrics.
    Uses Isolation Forest algorithm for real-time anomaly detection.
    """

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize the anomaly detector.

        Args:
            contamination: Expected proportion of anomalies in the data
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination, random_state=random_state, n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            "cpu_usage_percent",
            "memory_usage_percent",
            "disk_usage_percent",
            "load_avg_1min",
            "network_bytes_sent_rate",
            "network_bytes_recv_rate",
        ]
        self.model_path = "ml_models/anomaly_detector.pkl"
        self.scaler_path = "ml_models/scaler.pkl"

        # Ensure model directory exists
        os.makedirs(
            (
                os.path.dirname(self.model_path)
                if os.path.dirname(self.model_path)
                else "ml_models"
            ),
            exist_ok=True,
        )

        logger.info("AnomalyDetector initialized")

    def prepare_features(self, metrics_data: List[Dict]) -> pd.DataFrame:
        """
        Prepare features from raw metrics data.

        Args:
            metrics_data: List of metric dictionaries

        Returns:
            DataFrame with prepared features
        """
        try:
            df = pd.DataFrame(metrics_data)

            # Map common metric names to expected feature columns
            mapping = {
                "cpu_usage": "cpu_usage_percent",
                "memory_usage": "memory_usage_percent",
                "disk_usage": "disk_usage_percent",
                "network_io": "network_bytes_sent_rate",
            }

            # Apply mapping
            for old_name, new_name in mapping.items():
                if old_name in df.columns:
                    df[new_name] = df[old_name]

            # Ensure all required columns exist with default values
            for col in self.feature_columns:
                if col not in df.columns:
                    if col.endswith("_rate"):
                        # Calculate rate columns if missing
                        base_col = col.replace("_rate", "")
                        if base_col in df.columns:
                            df[col] = df[base_col].diff().fillna(df[base_col])
                        else:
                            df[col] = 50  # Default network rate
                    elif col == "load_avg_1min":
                        df[col] = 1.0  # Default load average
                    else:
                        df[col] = 0

            # Fill any NaN values and ensure reasonable ranges
            df[self.feature_columns] = df[self.feature_columns].fillna(50)

            # Ensure percentage values are in 0-100 range
            percentage_cols = [
                "cpu_usage_percent",
                "memory_usage_percent",
                "disk_usage_percent",
            ]
            for col in percentage_cols:
                if col in df.columns:
                    df[col] = df[col].clip(0, 100)

            return df[self.feature_columns]

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            # Return dummy dataframe with default values
            default_data = {
                "cpu_usage_percent": [50],
                "memory_usage_percent": [60],
                "disk_usage_percent": [40],
                "load_avg_1min": [1.5],
                "network_bytes_sent_rate": [1000000],
                "network_bytes_recv_rate": [2000000],
            }
            return pd.DataFrame(default_data)

    def train(self, training_data: List[Dict]) -> Dict[str, Any]:
        """
        Train the anomaly detection model.

        Args:
            training_data: Historical metrics data for training

        Returns:
            Training results and metrics
        """
        try:
            logger.info(f"Training anomaly detector with {len(training_data)} samples")

            # Prepare features
            features_df = self.prepare_features(training_data)

            if features_df.empty or len(features_df) < 10:
                # Generate synthetic training data if insufficient real data
                features_df = self._generate_synthetic_data(100)
                logger.warning(
                    "Using synthetic training data due to insufficient real data"
                )

            # Scale features
            features_scaled = self.scaler.fit_transform(features_df)

            # Train the model
            self.model.fit(features_scaled)
            self.is_trained = True

            # Save model and scaler
            self._save_model()

            # Calculate training metrics
            train_scores = self.model.decision_function(features_scaled)
            train_predictions = self.model.predict(features_scaled)

            anomaly_count = np.sum(train_predictions == -1)
            normal_count = np.sum(train_predictions == 1)

            results = {
                "status": "success",
                "samples_trained": len(features_df),
                "anomalies_detected": int(anomaly_count),
                "normal_samples": int(normal_count),
                "contamination_rate": float(anomaly_count / len(features_df)),
                "model_path": self.model_path,
                "feature_columns": self.feature_columns,
            }

            logger.info(f"Model training completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {"status": "error", "error": str(e), "samples_trained": 0}

    def detect_anomaly(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomaly for a single metric sample.

        Args:
            metrics: Current system metrics

        Returns:
            Anomaly prediction results
        """
        try:
            if not self.is_trained:
                # Try to load existing model
                if not self._load_model():
                    # Train with synthetic data if no model exists
                    synthetic_data = self._generate_synthetic_data(100)
                    self.train(synthetic_data.to_dict("records"))

            # Prepare features
            features_df = self.prepare_features([metrics])

            if features_df.empty:
                return {
                    "is_anomaly": False,
                    "anomaly_score": 0.0,
                    "confidence": 0.0,
                    "status": "error",
                    "error": "Failed to prepare features",
                }

            # Scale features
            features_scaled = self.scaler.transform(features_df)

            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            decision_score = self.model.decision_function(features_scaled)[0]

            # Convert to probability-like score (0-1)
            anomaly_score = max(0, min(1, (0.5 - decision_score) / 0.5))

            is_anomaly = prediction == -1
            confidence = abs(decision_score)

            return {
                "is_anomaly": bool(is_anomaly),
                "anomaly_score": float(anomaly_score),
                "confidence": float(confidence),
                "decision_score": float(decision_score),
                "status": "success",
                "model_version": "1.0",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Anomaly prediction failed: {e}")
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "status": "error",
                "error": str(e),
            }

    def batch_detect(self, metrics_list: List[Dict]) -> List[Dict]:
        """
        Detect anomalies for multiple metric samples.

        Args:
            metrics_list: List of system metrics

        Returns:
            List of anomaly predictions
        """
        try:
            results = []
            for metrics in metrics_list:
                result = self.detect_anomaly(metrics)
                results.append(result)
            return results

        except Exception as e:
            logger.error(f"Batch detection failed: {e}")
            return [{"status": "error", "error": str(e)} for _ in metrics_list]

    def _generate_synthetic_data(self, n_samples: int) -> pd.DataFrame:
        """Generate synthetic training data for testing purposes."""
        np.random.seed(self.random_state)

        # Normal operating ranges
        normal_data = {
            "cpu_usage_percent": np.random.normal(30, 15, int(n_samples * 0.85)),
            "memory_usage_percent": np.random.normal(60, 20, int(n_samples * 0.85)),
            "disk_usage_percent": np.random.normal(40, 15, int(n_samples * 0.85)),
            "load_avg_1min": np.random.normal(1.5, 0.5, int(n_samples * 0.85)),
            "network_bytes_sent_rate": np.random.normal(
                1000000, 500000, int(n_samples * 0.85)
            ),
            "network_bytes_recv_rate": np.random.normal(
                2000000, 800000, int(n_samples * 0.85)
            ),
        }

        # Anomalous data
        anomaly_samples = n_samples - int(n_samples * 0.85)
        anomaly_data = {
            "cpu_usage_percent": np.random.uniform(85, 100, anomaly_samples),
            "memory_usage_percent": np.random.uniform(90, 100, anomaly_samples),
            "disk_usage_percent": np.random.uniform(85, 100, anomaly_samples),
            "load_avg_1min": np.random.uniform(8, 15, anomaly_samples),
            "network_bytes_sent_rate": np.random.uniform(
                10000000, 50000000, anomaly_samples
            ),
            "network_bytes_recv_rate": np.random.uniform(
                20000000, 100000000, anomaly_samples
            ),
        }

        # Combine normal and anomaly data
        combined_data = {}
        for col in normal_data.keys():
            combined_data[col] = np.concatenate([normal_data[col], anomaly_data[col]])

        # Ensure no negative values and reasonable bounds
        df = pd.DataFrame(combined_data)
        df = df.clip(lower=0)
        df["cpu_usage_percent"] = df["cpu_usage_percent"].clip(upper=100)
        df["memory_usage_percent"] = df["memory_usage_percent"].clip(upper=100)
        df["disk_usage_percent"] = df["disk_usage_percent"].clip(upper=100)

        return df

    def _save_model(self):
        """Save trained model and scaler to disk."""
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, "wb") as f:
                pickle.dump(self.scaler, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def _load_model(self) -> bool:
        """Load trained model and scaler from disk."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                logger.info(f"Model loaded from {self.model_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and information."""
        return {
            "is_trained": self.is_trained,
            "model_type": "IsolationForest",
            "contamination": self.contamination,
            "feature_columns": self.feature_columns,
            "model_path": self.model_path,
            "model_exists": os.path.exists(self.model_path),
            "scaler_exists": os.path.exists(self.scaler_path),
            "version": "1.0",
        }


class TimeSeriesAnalyzer:
    """
    Time series analysis for trend detection and forecasting.
    """

    def __init__(self):
        """Initialize the time series analyzer."""
        self.window_size = 10
        logger.info("TimeSeriesAnalyzer initialized")

    def detect_trends(self, metrics_history: List[Dict]) -> Dict[str, Any]:
        """
        Detect trends in metrics over time.

        Args:
            metrics_history: Historical metrics data

        Returns:
            Trend analysis results
        """
        try:
            if len(metrics_history) < 5:
                return {
                    "status": "insufficient_data",
                    "message": "Need at least 5 data points for trend analysis",
                }

            df = pd.DataFrame(metrics_history)
            trends = {}

            numeric_columns = df.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                if col in df.columns and not df[col].empty:
                    values = df[col].dropna()
                    if len(values) >= 3:
                        # Simple linear trend detection
                        x = np.arange(len(values))
                        slope = np.polyfit(x, values, 1)[0]

                        # Categorize trend
                        if abs(slope) < 0.1:
                            trend = "stable"
                        elif slope > 0:
                            trend = "increasing"
                        else:
                            trend = "decreasing"

                        trends[col] = {
                            "trend": trend,
                            "slope": float(slope),
                            "current_value": float(values.iloc[-1]),
                            "change_rate": (
                                float(slope / values.mean())
                                if values.mean() != 0
                                else 0
                            ),
                        }

            return {
                "status": "success",
                "trends": trends,
                "analysis_window": len(metrics_history),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"status": "error", "error": str(e)}


# Factory function for creating anomaly detector
def create_anomaly_detector(**kwargs) -> AnomalyDetector:
    """Create and return an AnomalyDetector instance."""
    return AnomalyDetector(**kwargs)


# Export main classes
__all__ = ["AnomalyDetector", "TimeSeriesAnalyzer", "create_anomaly_detector"]


if __name__ == "__main__":
    # Test the implementation
    print("Testing ML Models Implementation...")

    detector = AnomalyDetector()

    # Test with sample data
    sample_metrics = {
        "cpu_usage_percent": 75.5,
        "memory_usage_percent": 85.2,
        "disk_usage_percent": 45.0,
        "load_avg_1min": 2.1,
        "network_bytes_sent_rate": 1500000,
        "network_bytes_recv_rate": 3000000,
    }

    result = detector.predict(sample_metrics)
    print(f"Anomaly Detection Result: {result}")

    print("✅ ML Models implementation test completed!")
