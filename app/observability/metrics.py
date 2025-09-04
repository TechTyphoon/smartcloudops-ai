"""
Metrics Collection Module
Business and performance metrics collection
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict

from prometheus_client import Counter, Gauge, Histogram


class MetricsCollector:
    """Metrics collector for business and performance metrics"""

    def __init__(self):
        # Performance metrics
        self.request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint", "status"],
        )

        self.request_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
        )

        self.active_requests = Gauge(
            "http_active_requests",
            "Number of active HTTP requests",
            ["method", "endpoint"],
        )

        # Business metrics
        self.anomalies_detected = Counter(
            "anomalies_detected_total", "Total anomalies detected", ["severity", "type"]
        )

        self.remediation_actions = Counter(
            "remediation_actions_total",
            "Total remediation actions executed",
            ["action_type", "status"],
        )

        self.ml_predictions = Counter(
            "ml_predictions_total",
            "Total ML predictions made",
            ["model_type", "accuracy_bucket"],
        )

        # System metrics
        self.memory_usage = Gauge(
            "memory_usage_bytes", "Memory usage in bytes", ["component"]
        )

        self.cpu_usage = Gauge(
            "cpu_usage_percent", "CPU usage percentage", ["component"]
        )


# Global metrics collector instance
metrics_collector = MetricsCollector()


def business_metrics() -> Dict[str, Any]:
    """Get current business metrics"""
    return {
        "anomalies_detected": {
            "total": 0,  # Would be populated from actual data
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_type": {"cpu": 0, "memory": 0, "disk": 0, "network": 0},
        },
        "remediation_actions": {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "by_type": {"scale_up": 0, "restart": 0, "alert": 0},
        },
        "ml_predictions": {
            "total": 0,
            "accuracy_avg": 0.0,
            "by_model": {"anomaly_detection": 0, "forecasting": 0},
        },
    }


def performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics"""
    return {
        "response_times": {"avg_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0},
        "throughput": {"requests_per_second": 0.0, "active_requests": 0},
        "system": {
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0,
            "disk_usage_percent": 0.0,
        },
    }


def record_request_metric(
    method: str, endpoint: str, status: int, duration: float
) -> None:
    """Record HTTP request metrics"""
    metrics_collector.request_duration.labels(
        method=method, endpoint=endpoint, status=status
    ).observe(duration)
    metrics_collector.request_total.labels(
        method=method, endpoint=endpoint, status=status
    ).inc()


def record_anomaly_metric(severity: str, anomaly_type: str) -> None:
    """Record anomaly detection metrics"""
    metrics_collector.anomalies_detected.labels(
        severity=severity, type=anomaly_type
    ).inc()


def record_remediation_metric(action_type: str, status: str) -> None:
    """Record remediation action metrics"""
    metrics_collector.remediation_actions.labels(
        action_type=action_type, status=status
    ).inc()


def record_ml_prediction_metric(model_type: str, accuracy: float) -> None:
    """Record ML prediction metrics"""
    # Bucket accuracy for better metrics
    if accuracy >= 0.95:
        bucket = "0.95-1.0"
    elif accuracy >= 0.90:
        bucket = "0.90-0.95"
    elif accuracy >= 0.80:
        bucket = "0.80-0.90"
    else:
        bucket = "0.00-0.80"

    metrics_collector.ml_predictions.labels(
        model_type=model_type, accuracy_bucket=bucket
    ).inc()


def record_system_metric(component: str, memory_bytes: int, cpu_percent: float) -> None:
    """Record system metrics"""
    metrics_collector.memory_usage.labels(component=component).set(memory_bytes)
    metrics_collector.cpu_usage.labels(component=component).set(cpu_percent)


def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "business": business_metrics(),
        "performance": performance_metrics(),
        "system": {
            "uptime_seconds": time.time(),  # Would be actual uptime
            "version": "4.0.0",
            "environment": "development",
        },
    }
