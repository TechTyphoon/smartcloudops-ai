"""
Enhanced Structured Logging with OpenTelemetry Integration
Phase 4: Observability & Operability
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog
from flask import Flask, g, request


def setup_enhanced_logging(
    app: Flask,
    log_level: str = "INFO",
    log_format: str = "json",
    enable_structlog: bool = True,
) -> None:
    """
    Setup enhanced structured logging with correlation IDs and OpenTelemetry integration

    Args:
        app: Flask application instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, text)
        enable_structlog: Enable structured logging
    """
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    if enable_structlog:
        _setup_structlog(log_format)

    # Add correlation ID middleware
    app.before_request(_add_correlation_id)
    app.after_request(_log_request)

    # Configure Flask logging
    app.logger.setLevel(getattr(logging, log_level.upper()))


def _setup_structlog(log_format: str) -> None:
    """Setup structured logging with structlog"""
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _add_correlation_id_processor,
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _add_correlation_id_processor(logger, method_name, event_dict):
    """Add correlation ID to log entries"""
    if hasattr(g, "correlation_id"):
        event_dict["correlation_id"] = g.correlation_id
    return event_dict


def _add_correlation_id():
    """Add correlation ID to request context"""
    g.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    g.request_start_time = datetime.now(timezone.utc)


def _log_request(response):
    """Log request details after processing"""
    if hasattr(g, "request_start_time"):
        duration = (datetime.now(timezone.utc) - g.request_start_time).total_seconds()

        log_data = {
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "correlation_id": g.correlation_id,
            "user_agent": request.headers.get("User-Agent", ""),
            "remote_addr": request.remote_addr,
        }

        logger = structlog.get_logger(__name__)
        logger.info("Request processed", **log_data)

    return response


def get_logger(name: str) -> structlog.BoundLogger:
    """Get structured logger instance"""
    return structlog.get_logger(name)


def log_business_event(event_type: str, business_value: float, **kwargs) -> None:
    """
    Log business events with structured data

    Args:
        event_type: Type of business event
        business_value: Business value metric
        **kwargs: Additional event data
    """
    logger = structlog.get_logger(__name__)

    event_data = {
        "event_type": event_type,
        "business_value": business_value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }

    logger.info("Business event", **event_data)


def log_performance_metric(
    metric_name: str, value: float, unit: str = "ms", **kwargs
) -> None:
    """
    Log performance metrics

    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        **kwargs: Additional metric data
    """
    logger = structlog.get_logger(__name__)

    metric_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }

    logger.info("Performance metric", **metric_data)


def log_security_event(event_type: str, severity: str = "info", **kwargs) -> None:
    """
    Log security events

    Args:
        event_type: Type of security event
        severity: Event severity (info, warning, error, critical)
        **kwargs: Additional event data
    """
    logger = structlog.get_logger(__name__)

    security_data = {
        "event_type": event_type,
        "severity": severity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }

    logger.warning("Security event", **security_data)
