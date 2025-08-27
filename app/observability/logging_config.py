"""
Structured JSON Logging with Correlation IDs
Production-ready logging configuration for SmartCloudOps AI
"""

import logging
import logging.config
import os
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import g, request
from pythonjsonlogger import jsonlogger

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes correlation ID and request context"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"

        # Add correlation ID
        corr_id = correlation_id.get()
        if corr_id:
            log_record["correlation_id"] = corr_id

        # Add request context if available
        if request:
            try:
                log_record["request"] = {
                    "method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", ""),
                    "content_type": request.content_type,
                }

                # Add user context if available
                if hasattr(g, "current_user") and g.current_user:
                    log_record["user"] = {
                        "id": g.current_user.get("id"),
                        "email": g.current_user.get("email"),
                    }
            except RuntimeError:
                # Outside request context
                pass

        # Add service information
        log_record["service"] = {
            "name": "smartcloudops-ai",
            "version": "3.3.0",
            "component": record.name,
        }

        # Ensure level is string
        log_record["level"] = record.levelname

        # Add source location
        log_record["source"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        # Add correlation ID if not already present
        if not hasattr(record, "correlation_id"):
            corr_id = correlation_id.get()
            if corr_id:
                record.correlation_id = corr_id
        return True


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Setup structured logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' or 'text')
    """

    if log_format == "json":
        formatter_class = CorrelationJSONFormatter
        format_string = "%(message)s"
    else:
        formatter_class = logging.Formatter
        format_string = (
            "[%(asctime)s] %(levelname)s [%(correlation_id)s] in %(name)s: %(message)s"
        )

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {"()": formatter_class, "format": format_string},
            "simple": {"format": "%(levelname)s - %(name)s - %(message)s"},
        },
        "filters": {
            "request_id": {
                "()": RequestIDFilter,
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filters": ["request_id"],
                "filename": "/var/log/smartcloudops/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "mode": "a",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filters": ["request_id"],
                "filename": "/var/log/smartcloudops/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "mode": "a",
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app.api": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app.ml": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app.remediation": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "werkzeug": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "urllib3": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # Create log directories
    os.makedirs("/var/log/smartcloudops", exist_ok=True)

    logging.config.dictConfig(config)


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name, defaults to caller module name

    Returns:
        Configured logger instance
    """
    if name is None:
        import inspect

        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__", "app")

    return logging.getLogger(name)


def set_correlation_id(corr_id: str = None) -> str:
    """
    Set correlation ID for current context

    Args:
        corr_id: Correlation ID, generates new UUID if None

    Returns:
        The correlation ID that was set
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())

    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id.get()


def log_performance(
    logger: logging.Logger, operation: str, duration_ms: float, **kwargs
) -> None:
    """
    Log performance metrics in structured format

    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        **kwargs: Additional context
    """
    logger.info(
        "Performance metric recorded",
        extra={
            "metric_type": "performance",
            "operation": operation,
            "duration_ms": duration_ms,
            "context": kwargs,
        },
    )


def log_business_event(
    logger: logging.Logger, event_type: str, entity_type: str, entity_id: str, **kwargs
) -> None:
    """
    Log business events in structured format

    Args:
        logger: Logger instance
        event_type: Type of event (created, updated, deleted, etc.)
        entity_type: Type of entity (anomaly, user, remediation, etc.)
        entity_id: Entity identifier
        **kwargs: Additional event data
    """
    logger.info(
        f"{entity_type.title()} {event_type}",
        extra={
            "event_type": "business",
            "action": event_type,
            "entity": {"type": entity_type, "id": entity_id},
            "data": kwargs,
        },
    )


def log_security_event(
    logger: logging.Logger, event_type: str, severity: str, **kwargs
) -> None:
    """
    Log security events in structured format

    Args:
        logger: Logger instance
        event_type: Type of security event
        severity: Severity level (low, medium, high, critical)
        **kwargs: Additional security context
    """
    log_level = {
        "low": logging.INFO,
        "medium": logging.WARNING,
        "high": logging.ERROR,
        "critical": logging.CRITICAL,
    }.get(severity, logging.WARNING)

    logger.log(
        log_level,
        f"Security event: {event_type}",
        extra={
            "event_type": "security",
            "security_event": event_type,
            "severity": severity,
            "context": kwargs,
        },
    )
