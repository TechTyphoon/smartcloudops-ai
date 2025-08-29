#!/usr/bin/env python3
"""
Monitoring: Prometheus Metrics Module - Minimal Working Version
Centralized metrics collection for application monitoring
"""

import logging
import threading

from flask import Flask, jsonify, request
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)

# Global lock for thread-safe singleton
_metrics_lock = threading.Lock()
_metrics_instance = None


class MetricsCollector:
    """Centralized metrics collector for SmartCloudOps.AI"""

    def __init__(self, registry=None):
        """Initialize all Prometheus metrics with optional custom registry"""
        self.registry = registry or CollectorRegistry()
        self._init_metrics()

    def _init_metrics(self):
        """Initialize all Prometheus metrics with custom registry"""

        # HTTP Request Metrics
        self.request_count = Counter(
            "flask_requests_total",
            "Total Flask HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.request_latency = Histogram(
            "flask_request_duration_seconds",
            "Flask HTTP request latency",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # ML Metrics
        self.ml_predictions = Counter(
            "ml_predictions_total",
            "Total ML predictions made",
            ["model_type", "status"],
            registry=self.registry,
        )

        self.ml_anomalies = Counter(
            "ml_anomalies_detected",
            "Total anomalies detected",
            ["severity", "model_type"],
            registry=self.registry,
        )

        self.ml_training_runs = Counter(
            "ml_training_runs_total",
            "Total model training runs",
            ["status", "model_type"],
            registry=self.registry,
        )

        # Remediation Metrics
        self.remediation_actions = Counter(
            "remediation_actions_total",
            "Total remediation actions executed",
            ["action_type", "severity", "status"],
            registry=self.registry,
        )

        self.remediation_success = Counter(
            "remediation_success_total",
            "Successful remediation actions",
            ["action_type"],
            registry=self.registry,
        )

        self.remediation_failure = Counter(
            "remediation_failure_total",
            "Failed remediation actions",
            ["action_type", "reason"],
            registry=self.registry,
        )

        # System Health Metrics
        self.system_health = Gauge(
            "system_health_score",
            "Overall system health score (0-100)",
            ["component"],
            registry=self.registry,
        )

        self.active_connections = Gauge(
            "active_connections",
            "Number of active connections",
            ["connection_type"],
            registry=self.registry,
        )

        self.error_rate = Gauge(
            "error_rate_percentage",
            "Error rate as percentage",
            ["endpoint", "error_type"],
            registry=self.registry,
        )

        # Performance Metrics
        self.cpu_usage = Gauge(
            "cpu_usage_percentage",
            "CPU usage percentage",
            ["instance"],
            registry=self.registry,
        )

        self.memory_usage = Gauge(
            "memory_usage_percentage",
            "Memory usage percentage",
            ["instance"],
            registry=self.registry,
        )

        self.disk_usage = Gauge(
            "disk_usage_percentage",
            "Disk usage percentage",
            ["instance", "mount_point"],
            registry=self.registry,
        )

        # Business Metrics
        self.active_users = Gauge(
            "active_users",
            "Number of active users",
            ["user_type"],
            registry=self.registry,
        )

        self.api_calls = Counter(
            "api_calls_total",
            "Total API calls",
            ["endpoint", "method", "status"],
            registry=self.registry,
        )

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics"""
        try:
            self.request_count.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
            self.request_latency.labels(method=method, endpoint=endpoint).observe(
                duration
            )
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")

    def record_ml_prediction(self, model_type: str, status: str):
        """Record ML prediction metrics"""
        try:
            self.ml_predictions.labels(model_type=model_type, status=status).inc()
        except Exception as e:
            logger.error(f"Error recording ML prediction metrics: {e}")

    def record_anomaly(self, severity: str, model_type: str):
        """Record anomaly detection metrics"""
        try:
            self.ml_anomalies.labels(severity=severity, model_type=model_type).inc()
        except Exception as e:
            logger.error(f"Error recording anomaly metrics: {e}")

    def record_remediation_action(self, action_type: str, severity: str, status: str):
        """Record remediation action metrics"""
        try:
            self.remediation_actions.labels(
                action_type=action_type, severity=severity, status=status
            ).inc()

            if status == "success":
                self.remediation_success.labels(action_type=action_type).inc()
            elif status == "failure":
                self.remediation_failure.labels(
                    action_type=action_type, reason="unknown"
                ).inc()
        except Exception as e:
            logger.error(f"Error recording remediation metrics: {e}")

    def set_system_health(self, component: str, score: float):
        """Set system health score for a component"""
        try:
            self.system_health.labels(component=component).set(score)
        except Exception as e:
            logger.error(f"Error setting system health: {e}")

    def set_active_connections(self, connection_type: str, count: int):
        """Set active connections count"""
        try:
            self.active_connections.labels(connection_type=connection_type).set(count)
        except Exception as e:
            logger.error(f"Error setting active connections: {e}")

    def set_error_rate(self, endpoint: str, error_type: str, rate: float):
        """Set error rate for an endpoint"""
        try:
            self.error_rate.labels(endpoint=endpoint, error_type=error_type).set(rate)
        except Exception as e:
            logger.error(f"Error setting error rate: {e}")

    def set_resource_usage(self, cpu: float, memory: float, disk: float):
        """Set resource usage metrics"""
        try:
            self.cpu_usage.labels(instance="main").set(cpu)
            self.memory_usage.labels(instance="main").set(memory)
            self.disk_usage.labels(instance="main", mount_point="/").set(disk)
        except Exception as e:
            logger.error(f"Error setting resource usage: {e}")

    def record_api_call(self, endpoint: str, method: str, status: str):
        """Record API call metrics"""
        try:
            self.api_calls.labels(endpoint=endpoint, method=method, status=status).inc()
        except Exception as e:
            logger.error(f"Error recording API call metrics: {e}")

    def get_metrics_summary(self) -> dict:
        """Get a summary of current metrics"""
        try:
            return {
                "request_count": self.request_count._value.sum(),
                "ml_predictions": self.ml_predictions._value.sum(),
                "anomalies_detected": self.ml_anomalies._value.sum(),
                "remediation_actions": self.remediation_actions._value.sum(),
                "system_health": {
                    "overall": self.system_health._value.sum(),
                    "components": len(self.system_health._value),
                },
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}

    def reset_metrics(self):
        """Reset all metrics (for testing purposes)"""
        try:
            # Reset counters and gauges
            for metric in self.registry.collect():
                if hasattr(metric, "samples"):
                    for sample in metric.samples:
                        if hasattr(sample, "value"):
                            sample.value = 0
            logger.info("Metrics reset successfully")
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector instance"""
    global _metrics_instance

    if _metrics_instance is None:
        with _metrics_lock:
            if _metrics_instance is None:
                _metrics_instance = MetricsCollector()
                logger.info("Metrics collector initialized")

    return _metrics_instance


# Global metrics instance
metrics = get_metrics_collector()
