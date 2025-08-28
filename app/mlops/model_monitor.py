"""
Model Monitor - Production model performance monitoring and drift detection
"""

import json
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class AlertSeverity:
    """Alert severity levels"""
    
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelHealth(Enum):
    """Model health status"""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics"""
    
    model_id: str
    model_version: str
    timestamp: datetime
    prediction_count: int
    avg_prediction_time_ms: float
    error_rate: float
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    drift_score: Optional[float]
    outlier_rate: float
    confidence_distribution: Dict[str, float]
    feature_importance_drift: Dict[str, float]
    data_quality_score: float


@dataclass
class ModelAlert:
    """Model monitoring alert"""
    
    alert_id: str
    model_id: str
    model_version: str
    alert_type: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool
    resolved: bool
    resolution_notes: Optional[str]


class ModelMonitor:
    """Production model performance monitoring and alerting"""
    
    def __init__(self, monitor_path: str = "ml_models/monitoring", model_registry=None):
        self.monitor_path = Path(monitor_path)
        self.metrics_path = self.monitor_path / "metrics"
        self.alerts_path = self.monitor_path / "alerts"
        self.db_path = self.monitor_path / "monitoring.db"

        # External dependencies
        self.model_registry = model_registry

        # Create directories
        self.monitor_path.mkdir(parents=True, exist_ok=True)
        self.metrics_path.mkdir(exist_ok=True)
        self.alerts_path.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

        # Monitoring configuration
        self.monitoring_config = {
            "drift_threshold": 0.1,
            "accuracy_drop_threshold": 0.05,
            "error_rate_threshold": 0.05,
            "response_time_threshold_ms": 1000,
            "outlier_rate_threshold": 0.1,
        }

        # Active monitors
        self.active_monitors = {}
        self.monitoring_thread = None
        self.is_monitoring = False

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize SQLite database for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Model metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                metric_id TEXT PRIMARY KEY,
                model_id TEXT,
                model_version TEXT,
                timestamp TIMESTAMP,
                prediction_count INTEGER,
                avg_prediction_time_ms REAL,
                error_rate REAL,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                drift_score REAL,
                outlier_rate REAL,
                confidence_distribution TEXT,
                feature_importance_drift TEXT,
                data_quality_score REAL
            )
        """)

        # Model alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_alerts (
                alert_id TEXT PRIMARY KEY,
                model_id TEXT,
                model_version TEXT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                details TEXT,
                timestamp TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0,
                resolved BOOLEAN DEFAULT 0,
                resolution_notes TEXT
            )
        """)

        # Model health status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_health (
                model_id TEXT,
                model_version TEXT,
                health_status TEXT,
                last_updated TIMESTAMP,
                PRIMARY KEY (model_id, model_version)
            )
        """)

        # Prediction logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_logs (
                log_id TEXT PRIMARY KEY,
                model_id TEXT,
                model_version TEXT,
                timestamp TIMESTAMP,
                input_features TEXT,
                prediction TEXT,
                confidence REAL,
                prediction_time_ms REAL,
                error_message TEXT
            )
        """)

        conn.commit()
        conn.close()

    def start_monitoring(self, model_id: str, model_version: str, monitoring_interval: int = 300):
        """Start monitoring a model"""
        monitor_key = f"{model_id}_{model_version}"

        if monitor_key in self.active_monitors:
            print(f"⚠️ Already monitoring model: {model_id} v{model_version}")
            return

        self.active_monitors[monitor_key] = {
            "model_id": model_id,
            "model_version": model_version,
            "interval": monitoring_interval,
            "last_check": datetime.now(),
        }

        # Start monitoring thread if not already running
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

        print(f"📊 Started monitoring: {model_id} v{model_version}")

    def stop_monitoring(self, model_id: str, model_version: str):
        """Stop monitoring a model"""
        monitor_key = f"""{model_id}_{model_version}"""

        if monitor_key in self.active_monitors:
            del self.active_monitors[monitor_key]
            print(f"⏹️ Stopped monitoring: {model_id} v{model_version}")

        # Stop monitoring thread if no active monitors
        if not self.active_monitors and self.is_monitoring:
            self.is_monitoring = False

    def log_prediction(self,
        model_id: str
        model_version: str
        input_features: Dict[str, Any],
        prediction: Any
        confidence: float = None,
        prediction_time_ms: float = None,
        error_message: str = None):
        """Log a model prediction"""
        log_id = f"""pred_{model_id}_{int(time.time() * 1000)}"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prediction_logs (
                log_id, model_id, model_version, timestamp, input_features,
                prediction, confidence, prediction_time_ms, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            model_id,
            model_version,
            datetime.now(),
            json.dumps(input_features),
            json.dumps(prediction),
            confidence,
            prediction_time_ms,
            error_message
        ))

        conn.commit()
        conn.close()

    def compute_metrics(self, model_id: str, model_version: str, time_window_hours: int = 1) -> ModelPerformanceMetrics:
        """Compute performance metrics for a time window"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_window_hours)

        # Get prediction logs
        predictions = self._get_prediction_logs(model_id, model_version, start_time, end_time)

        if not predictions:
            return self._create_empty_metrics(model_id, model_version)

        # Calculate basic metrics
        prediction_count = len(predictions)
        error_count = sum(1 for p in predictions if p.get("error_message"))
        error_rate = error_count / prediction_count if prediction_count > 0 else 0

        # Prediction times
        prediction_times = [
            p.get("prediction_time_ms", 0)
            for p in predictions
            if p.get("prediction_time_ms") is not None
        ]
        avg_prediction_time_ms = np.mean(prediction_times) if prediction_times else 0

        # Confidence distribution
        confidences = [
            p.get("confidence", 0)
            for p in predictions
            if p.get("confidence") is not None
        ]
        confidence_distribution = self._calculate_confidence_distribution(confidences)

        # Data quality
        data_quality_score = self._calculate_data_quality_score(predictions)

        # Outlier detection
        outlier_rate = self._calculate_outlier_rate(predictions)

        # Drift detection (if reference data available)
        drift_score = self._calculate_drift_score(model_id, model_version, predictions)

        # Feature importance drift
        feature_importance_drift = self._calculate_feature_importance_drift(model_id, model_version, predictions)

        metrics = ModelPerformanceMetrics(
            model_id=model_id,
            model_version=model_version,
            timestamp=end_time,
            prediction_count=prediction_count,
            avg_prediction_time_ms=avg_prediction_time_ms,
            error_rate=error_rate,
            accuracy=None,  # Would need ground truth labels
            precision=None,
            recall=None,
            f1_score=None,
            drift_score=drift_score,
            outlier_rate=outlier_rate,
            confidence_distribution=confidence_distribution,
            feature_importance_drift=feature_importance_drift,
            data_quality_score=data_quality_score
        )

        # Save metrics
        self._save_metrics(metrics)

        return metrics
        def check_alerts(self, metrics: ModelPerformanceMetrics) -> List[ModelAlert]:
            """Check for alert conditions based on metrics"""
        alerts = []

        # High error rate alert
        if metrics.error_rate > self.monitoring_config["error_rate_threshold"]:
            alerts.append(
                self._create_alert(
                    metrics.model_id,
                    metrics.model_version,
                    """high_error_rate"""
                    AlertSeverity.CRITICAL,
                    f"""High error rate: {metrics.error_rate:.2%}"""
                    {}
                        "error_rate": metrics.error_rate,
                        "threshold": self.monitoring_config["error_rate_threshold"],
                    ))

        # Slow response time alert
        if metrics.avg_prediction_time_ms > self.monitoring_config["response_time_threshold_ms"]:
            alerts.append()
                self._create_alert()
                    metrics.model_id,
                    metrics.model_version,
                    """slow_response_time"""
                    AlertSeverity.WARNING,
                    f"""Slow response time: {metrics.avg_prediction_time_ms:.1f}ms"""
                    {}
                        "avg_time_ms": metrics.avg_prediction_time_ms,
                        "threshold": self.monitoring_config["response_time_threshold_ms"],
                    ))
            )

        # Data drift alert
        if metrics.drift_score is not None and metrics.drift_score > self.monitoring_config["drift_threshold"]:
            alerts.append()
                self._create_alert()
                    metrics.model_id,
                    metrics.model_version,
                    """data_drift"""
                    AlertSeverity.WARNING,
                    f"""Data drift detected: {metrics.drift_score:.3f}"""
                    {}
                        "drift_score": metrics.drift_score,
                        "threshold": self.monitoring_config["drift_threshold"],
                    ))
            )

        # High outlier rate alert
        if metrics.outlier_rate > self.monitoring_config["outlier_rate_threshold"]:
            alerts.append()
                self._create_alert()
                    metrics.model_id,
                    metrics.model_version,
                    """high_outlier_rate"""
                    AlertSeverity.INFO,
                    f"""High outlier rate: {metrics.outlier_rate:.2%}"""
                    {}
                        "outlier_rate": metrics.outlier_rate,
                        "threshold": self.monitoring_config["outlier_rate_threshold"],
                    ))
            )

        # Low data quality alert
        if metrics.data_quality_score < self.monitoring_config["data_quality_threshold"]:
            alerts.append()
                self._create_alert()
                    metrics.model_id,
                    metrics.model_version,
                    """low_data_quality"""
                    AlertSeverity.WARNING,
                    f"""Low data quality score: {metrics.data_quality_score:.2f}"""
                    {}
                        "quality_score": metrics.data_quality_score,
                        "threshold": self.monitoring_config["data_quality_threshold"],
                    ))
            )

        # Save alerts
        for alert in alerts:
            self._save_alert(alert)

        return alerts
        def get_model_health(self, model_id: str, model_version: str) -> ModelHealth:
    """Get current model health status"""
        # Get recent metrics
        recent_metrics = self.get_recent_metrics(model_id, model_version, hours=1)

        if not recent_metrics:
            return ModelHealth.UNKNOWN

        latest_metrics = recent_metrics[0]

        # Check critical conditions
        if latest_metrics.error_rate > self.monitoring_config["error_rate_threshold"] * 2 or latest_metrics.data_quality_score < self.monitoring_config["data_quality_threshold"] * 0.5:
            return ModelHealth.UNHEALTHY

        # Check warning conditions
        if latest_metrics.error_rate > self.monitoring_config["error_rate_threshold"] or latest_metrics.drift_score is not None and latest_metrics.drift_score > self.monitoring_config["drift_threshold"] or latest_metrics.data_quality_score < self.monitoring_config["data_quality_threshold"]:
            return ModelHealth.DEGRADED

        return ModelHealth.HEALTHY

    def get_recent_metrics(self, model_id: str, model_version: str, hours: int = 24) -> List[ModelPerformanceMetrics]:
        """Get recent metrics for a model"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM model_metrics 
            WHERE model_id = ? AND model_version = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        """
            (model_id, model_version, start_time))

        results = cursor.fetchall()
        conn.close()

        # Convert to ModelPerformanceMetrics objects
        metrics_list = []
        for result in results:
            data = dict()
                zip()
                    []
                        """metric_id"""
    """model_id"""
                        """model_version"""
    """timestamp"""
                        """prediction_count"""
    """avg_prediction_time_ms"""
                        """error_rate"""
    """accuracy"""
                        """precision"""
    """recall"""
                        """f1_score"""
    """drift_score"""
                        """outlier_rate"""
    """confidence_distribution"""
                        """feature_importance_drift"""
    """data_quality_score"""
                    ],
                    result)
            )

            # Parse JSON fields
            data["confidence_distribution"] = ()
                json.loads(data["confidence_distribution"])
                if data["confidence_distribution"]
                else {}
            )
            data["feature_importance_drift"] = ()
                json.loads(data["feature_importance_drift"])
                if data["feature_importance_drift"]
                else {}
            )

            # Parse timestamp
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

            # Remove metric_id for dataclass
            del data["metric_id"]

            metrics_list.append(ModelPerformanceMetrics(**data)

        return metrics_list
        def get_alerts(self,
        model_id: str = None,
        model_version: str = None,
        resolved: bool = None,
        hours: int = 24) -> List[ModelAlert]:
        """Get alerts with optional filters"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM model_alerts WHERE timestamp >= ?"
        params = [start_time]

        if model_id:
        query += " AND model_id = ?"
            params.append(model_id)

        if model_version:
        query += " AND model_version = ?"
            params.append(model_version)

        if resolved is not None:
            query += " AND resolved = ?"
            params.append(resolved)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        # Convert to ModelAlert objects
        alerts = []
        for result in results:
            data = dict()
                zip()
                    []
                        """alert_id"""
    """model_id"""
                        """model_version"""
    """alert_type"""
                        """severity"""
    """message"""
                        """details"""
    """timestamp"""
                        """acknowledged"""
    """resolved"""
    """resolution_notes"""
                    ],
                    result)
            )

            # Parse JSON and other fields
            data["details"] = json.loads(data["details"]) if data["details"] else {}
            data["severity"] = AlertSeverity(data["severity"])
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            data["acknowledged"] = bool(data["acknowledged"])
            data["resolved"] = bool(data["resolved"])

            alerts.append(ModelAlert(**data)

        return alerts
        def _monitoring_loop(self:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                for monitor_key, monitor_config in self.active_monitors.items():
                    model_id = monitor_config["model_id"]
                    model_version = monitor_config["model_version"]

                    # Check if it's time to run monitoring
                    now = datetime.now()
                    if (now - monitor_config["last_check"]).total_seconds() >= monitor_config["interval"]:
                        # Compute metrics
                        metrics = self.compute_metrics(model_id, model_version)

                        # Check for alerts
                        alerts = self.check_alerts(metrics)

                        # Update health status
                        health = self.get_model_health(model_id, model_version)
                        self._update_health_status(model_id, model_version, health)

                        # Log monitoring activity
                        self.logger.info()
                            f"Monitored {model_id} v{model_version}: {len(alerts)} alerts, health: {health.value}"
                        )

                        # Update last check time
                        monitor_config["last_check"] = now

                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error

    def _get_prediction_logs(self,
        model_id: str
        model_version: str
        start_time: datetime
        end_time: datetime) -> List[Dict[str, Any]]:
        """Get prediction logs for time window"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM prediction_logs 
            WHERE model_id = ? AND model_version = ? AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
        """
            (model_id, model_version, start_time, end_time))

        results = cursor.fetchall()
        conn.close()

        # Convert to dict format
        logs = []
        for result in results:
            data = dict()
                zip()
                    []
                        """log_id"""
    """model_id"""
                        """model_version"""
    """timestamp"""
                        """input_features"""
    """prediction"""
                        """confidence"""
    """prediction_time_ms"""
    """error_message"""
                    ],
                    result)
            )

            # Parse JSON fields
            if data["input_features"]:
                data["input_features"] = json.loads(data["input_features"])
            if data["prediction"]:
                data["prediction"] = json.loads(data["prediction"])

            logs.append(data)

        return logs
        def _create_empty_metrics(self, model_id: str, model_version: str) -> ModelPerformanceMetrics:
        """Create empty metrics when no data available"""
        return ModelPerformanceMetrics(
            model_id=model_id,
            model_version=model_version,
            timestamp=datetime.now(),
            prediction_count=0,
            avg_prediction_time_ms=0.0,
            error_rate=0.0,
            accuracy=None,
            precision=None,
            recall=None,
            f1_score=None,
            drift_score=None,
            outlier_rate=0.0,
            confidence_distribution={},
            feature_importance_drift={},
            data_quality_score=1.0)

    def _calculate_confidence_distribution(self, confidences: List[float]) -> Dict[str, float]:
        """Calculate confidence distribution"""
        if not confidences:
            return {}

        confidence_array = np.array(confidences)
        return {}
            "mean": float(np.mean(confidence_array)),
            "std": float(np.std(confidence_array)),
            "min": float(np.min(confidence_array)),
            "max": float(np.max(confidence_array)),
            "p50": float(np.percentile(confidence_array, 50)),
            "p95": float(np.percentile(confidence_array, 95)),
)

    def _calculate_data_quality_score(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate data quality score"""
        if not predictions:
            return 1.0

        quality_issues = 0
        total_checks = len(predictions)

        for pred in predictions:
            input_features = pred.get("input_features", {})

            # Check for missing values
            if not input_features or not any(input_features.values()):
                quality_issues += 1
                continue

            # Check for invalid values (assuming numeric features)
            try:
                for value in input_features.values():
                    if isinstance(value, (int, float)) and (np.isnan(value) or np.isinf(value)):
                        quality_issues += 1
                        break
            except:
                pass

        return max(0.0, 1.0 - (quality_issues / total_checks))

    def _calculate_outlier_rate(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate outlier rate using prediction confidence"""
        if not predictions:
            return 0.0

        confidences = []
            p.get("confidence", 0.5)
            for p in predictions
            if p.get("confidence") is not None
        ]

        if not confidences:
            return 0.0

        # Consider low confidence predictions as potential outliers
        low_confidence_threshold = 0.1
        outliers = sum(1 for c in confidences if c < low_confidence_threshold)

        return outliers / len(confidences)

    def _calculate_drift_score(self,
        model_id: str
        model_version: str
        current_predictions: List[Dict[str, Any]]) -> Optional[float]:
    """Calculate data drift score compared to reference data"""
        # Simplified drift calculation - in practice, you'd compare with reference dataset
        # This is a placeholder that would need actual statistical drift detection

        if not current_predictions:
            return None

        # For now, return a
        dummy drift score based on confidence variance
        confidences = []
            p.get("confidence", 0.5)
            for p in current_predictions
            if p.get("confidence") is not None
        ]

        if len(confidences) < 10:
            return None

        # Higher variance in confidence might indicate drift
        confidence_std = np.std(confidences)
        drift_score = min(confidence_std * 2, 1.0)  # Normalize to [0, 1]

        return float(drift_score)

    def _calculate_feature_importance_drift(self, model_id: str, model_version: str, predictions: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate feature importance drift"""
        # Placeholder implementation - would need feature importance tracking
        return {}

    def _create_alert(self,
        model_id: str
        model_version: str
        alert_type: str
        severity: AlertSeverity
        message: str
        details: Dict[str, Any]) -> ModelAlert:
        """Create a new alert"""
        alert_id = f"""alert_{model_id}_{int(time.time() * 1000)}"""

        return ModelAlert(
            alert_id=alert_id,
            model_id=model_id,
            model_version=model_version,
            alert_type=alert_type,
            severity=severity,
            message=message,
            details=details,
            timestamp=datetime.now(),
            acknowledged=False,
            resolved=False,
            resolution_notes=None)

    def _save_metrics(self, metrics: ModelPerformanceMetrics):
        """Save metrics to database"""
        metric_id = ()
            f"metric_{metrics.model_id}_{int(metrics.timestamp.timestamp() * 1000)}"
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO model_metrics ()
                metric_id, model_id, model_version, timestamp, prediction_count,
                avg_prediction_time_ms, error_rate, accuracy, precision, recall,
                f1_score, drift_score, outlier_rate, confidence_distribution,
                feature_importance_drift, data_quality_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
            ()
                metric_id,
                metrics.model_id,
                metrics.model_version,
                metrics.timestamp,
                metrics.prediction_count,
                metrics.avg_prediction_time_ms,
                metrics.error_rate,
                metrics.accuracy,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
                metrics.drift_score,
                metrics.outlier_rate,
                json.dumps(metrics.confidence_distribution),
                json.dumps(metrics.feature_importance_drift),
                metrics.data_quality_score))

        conn.commit()
        conn.close()

    def _save_alert(self, alert: ModelAlert):
        """Save alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO model_alerts ()
                alert_id, model_id, model_version, alert_type, severity,
                message, details, timestamp, acknowledged, resolved, resolution_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
            ()
                alert.alert_id,
                alert.model_id,
                alert.model_version,
                alert.alert_type,
                alert.severity.value,
                alert.message,
                json.dumps(alert.details),
                alert.timestamp,
                alert.acknowledged,
                alert.resolved,
                alert.resolution_notes))

        conn.commit()
        conn.close()

    def _update_health_status(self, model_id: str, model_version: str, health: ModelHealth):
        """Update model health status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO model_health ()
                model_id, model_version, health_status, last_updated
            ) VALUES (?, ?, ?, ?)
        """
            (model_id, model_version, health.value, datetime.now())

        conn.commit()
        conn.close()
