"""
OpenTelemetry Configuration Module
Distributed tracing and metrics configuration
"""

import os
from typing import Optional


def setup_opentelemetry(
    app,
    service_name: str = "smartcloudops-ai",
    service_version: str = "4.0.0",
    environment: str = "development",
    enable_tracing: bool = True,
    enable_metrics: bool = True,
    enable_logging_instrumentation: bool = True,
) -> None:
    """
    Setup OpenTelemetry for distributed tracing and metrics

    Args:
        app: Flask application instance
        service_name: Name of the service
        service_version: Version of the service
        environment: Environment (development, staging, production)
        enable_tracing: Enable distributed tracing
        enable_metrics: Enable metrics collection
        enable_logging_instrumentation: Enable logging instrumentation
    """
    # For now, we'll use a simple implementation
    # In production, this would initialize OpenTelemetry SDK

    # Set environment variables for OpenTelemetry
    os.environ.setdefault("OTEL_SERVICE_NAME", service_name)
    os.environ.setdefault("OTEL_SERVICE_VERSION", service_version)
    os.environ.setdefault("OTEL_RESOURCE_ATTRIBUTES", f"environment={environment}")

    if enable_tracing:
        os.environ.setdefault("OTEL_TRACES_SAMPLER", "always_on")
        os.environ.setdefault("OTEL_TRACES_SAMPLER_ARG", "1.0")

    if enable_metrics:
        os.environ.setdefault("OTEL_METRICS_EXPORTER", "prometheus")

    if enable_logging_instrumentation:
        os.environ.setdefault("OTEL_LOGS_EXPORTER", "otlp")

    # Log configuration
    app.logger.info(f"OpenTelemetry configured for {service_name} v{service_version}")
    app.logger.info(f"Environment: {environment}")
    app.logger.info(f"Tracing: {'enabled' if enable_tracing else 'disabled'}")
    app.logger.info(f"Metrics: {'enabled' if enable_metrics else 'disabled'}")
    app.logger.info(
        f"Logging instrumentation: {'enabled' if enable_logging_instrumentation else 'disabled'}"
    )


def get_trace_id() -> Optional[str]:
    """Get current trace ID"""
    # This would return the actual trace ID from OpenTelemetry context
    # For now, return None
    return None


def get_span_id() -> Optional[str]:
    """Get current span ID"""
    # This would return the actual span ID from OpenTelemetry context
    # For now, return None
    return None


def is_tracing_enabled() -> bool:
    """Check if tracing is enabled"""
    return os.getenv("OTEL_TRACES_SAMPLER") == "always_on"


def is_metrics_enabled() -> bool:
    """Check if metrics are enabled"""
    return os.getenv("OTEL_METRICS_EXPORTER") == "prometheus"
