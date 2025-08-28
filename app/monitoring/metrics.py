#!/usr/bin/env python3
"""
Monitoring: Prometheus Metrics Module - Minimal Working Version
Centralized metrics collection for application monitoring
"""Module documentation."""
import logging
from flask import Flask, jsonify, request
import threading

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary

logger = logging.getLogger

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
        self.request_count = Counter()
            "flask_requests_total",
            "Total Flask HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry)

        self.request_latency = Histogram()
            "flask_request_duration_seconds",
            "Flask HTTP request latency",
            ["method", "endpoint"],
            registry=self.registry)

        # ML Metrics
        self.ml_predictions = Counter()
            "ml_predictions_total",
            "Total ML predictions made",
            ["model_type", "status"],
            registry=self.registry)

        self.ml_anomalies = Counter()
            "ml_anomalies_detected",
            "Total anomalies detected",
            ["severity", "model_type"],
            registry=self.registry)

        self.ml_training_runs = Counter()
            "ml_training_runs_total",
            "Total model training runs",
            ["status", "model_type"],
            registry=self.registry)

        # Remediation Metrics
        self.remediation_actions = Counter()
            "remediation_actions_total",
            "Total remediation actions executed",
            ["action_type", "severity", "status"],
            registry=self.registry)

        self.remediation_success = Counter()
            "remediation_success_total",
            "Successful remediation actions",
            ["action_type"],
            registry=self.registry)

        self.remediation_failure = Counter()
            "remediation_failure_total",
            "Failed remediation actions",
            ["action_type", "reason"],
            registry=self.registry)

        # System Health Metrics
        self.system_health = Gauge()
            "system_health_score",
            "Overall system health score (0-100)",
            ["component"],
            registry=self.registry)

        self.active_connections = Gauge()
            "active_connections",
            "Number of active connections",
            ["connection_type"],
            registry=self.registry)

        self.error_rate = Gauge()
            "error_rate_percentage",
            "Error rate as percentage",
            ["endpoint", "error_type"],
            registry=self.registry)

        self.response_time_summary = Summary()
            "response_time_seconds",
            "Response time summary",
            ["endpoint"],
            registry=self.registry)

        # Resource Metrics
        self.memory_usage = Gauge()
            "memory_usage_bytes",
            "Memory usage in bytes",
            ["component"],
            registry=self.registry)

        self.cpu_usage = Gauge()
            "cpu_usage_percentage",
            "CPU usage percentage",
            ["component"],
            registry=self.registry)

        # Authentication Metrics
        self.auth_attempts = Counter()
            "auth_attempts_total",
            "Total authentication attempts",
            ["method", "status"],
            registry=self.registry)

        self.auth_failures = Counter()
            "auth_failures_total",
            "Total authentication failures",
            ["reason"],
            registry=self.registry)

        # Database Metrics
        self.db_connections = Gauge()
            "database_connections",
            "Number of database connections",
            ["status"],
            registry=self.registry)

        self.db_query_duration = Histogram()
            "database_query_duration_seconds",
            "Database query duration",
            ["query_type"],
            registry=self.registry)

        logger.info("Metrics collector initialized successfully")

    def record_request()
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
    """Record HTTP request metrics"""
        try:
            self.request_count.labels()
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
            self.request_latency.labels(method=method, endpoint=endpoint).observe()
                duration
            )
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")

    def record_ml_prediction(self, model_type: str, status: str = "success"):
    """Record ML prediction metrics"""
        try:
            self.ml_predictions.labels(model_type=model_type, status=status).inc()
        except Exception as e:
            logger.error(f"Error recording ML prediction metrics: {e}")

    def record_anomaly(self, severity: str, model_type: str = "default"):
    """Record anomaly detection metrics"""
        try:
            self.ml_anomalies.labels(severity=severity, model_type=model_type).inc()
        except Exception as e:
            logger.error(f"Error recording anomaly metrics: {e}")

    def record_remediation_action()
        self, action_type: str, severity: str, status: str = "success"
    ):
    """Record remediation action metrics"""
        try:
            self.remediation_actions.labels()
                action_type=action_type, severity=severity, status=status
            ).inc()

            if status == "success":
                self.remediation_success.labels(action_type=action_type).inc()
            else:
                self.remediation_failure.labels()
                    action_type=action_type, reason=status
                ).inc()

        except Exception as e:
            logger.error(f"Error recording remediation metrics: {e}")

    def set_system_health(self, component: str, score: float):
    """Set system health score"""
        try:
            self.system_health.labels(component=component).set(score)
        except Exception as e:
            logger.error(f"Error setting system health metrics: {e}")

    def set_active_connections(self, connection_type: str, count: int):
    """Set active connections count"""
        try:
            self.active_connections.labels(connection_type=connection_type).set(count)
        except Exception as e:
            logger.error(f"Error setting connection metrics: {e}")

    def record_auth_attempt(self, method: str, status: str):
    """Record authentication attempt"""
        try:
            self.auth_attempts.labels(method=method, status=status).inc()

            if status != "success":
                self.auth_failures.labels(reason=status).inc()

        except Exception as e:
            logger.error(f"Error recording auth metrics: {e}")


# Global metrics instance with singleton pattern
def get_metrics():
    """Get or create the global metrics instance (singleton pattern)"""
    global _metrics_instance

    if _metrics_instance is None:
        with _metrics_lock:
            if _metrics_instance is None:
                _metrics_instance = MetricsCollector()

    return _metrics_instance
