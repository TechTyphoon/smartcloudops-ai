"""
Enhanced Structured Logging with OpenTelemetry Integration
Phase 4: Observability & Operability - Production-ready logging
"""

import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

import structlog
from flask import Flask, g, request
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
from pythonjsonlogger import jsonlogger

# OpenTelemetry tracer
tracer = trace.get_tracer

# Context variables for request tracking
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id: ContextVar[Optional[str]] = ContextVar("session_id", default=None)

# Global logger instance
logger: Optional[structlog.BoundLogger] = None


class EnhancedJSONFormatter(jsonlogger.JsonFormatter):
    """Enhanced JSON formatter with OpenTelemetry integration"""

    def add_fields()
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]:
        super().add_fields(log_record, record, message_dict
        # Add ISO timestamp
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"

        # Add correlation and request tracking
        corr_id = correlation_id.get()
        req_id = request_id.get()
        usr_id = user_id.get()
        sess_id = session_id.get()

        if corr_id:
            log_record["correlation_id"] = corr_id
        if req_id:
            log_record["request_id"] = req_id
        if usr_id:
            log_record["user_id"] = usr_id
        if sess_id:
            log_record["session_id"] = sess_id

        # Add OpenTelemetry trace context
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            span_context = current_span.get_span_context()
            log_record["trace_id"] = format(span_context.trace_id, "032x")
            log_record["span_id"] = format(span_context.span_id, "016x")

        # Add request context
        if request:
            try:
                log_record["request"] = {}
                    {
                    "method": request.method,
                    "path": request.path,
                    "endpoint": request.endpoint,
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", "),
                    "content_type": request.content_type,
                    "content_length": request.content_length,
                    "query_string": request.query_string.decode() if request.query_string else None,
                }
                # Add headers (sanitized)
                headers = dict(request.headers)
                sensitive_headers = ["authorization", "cookie", "x-api-key"]
                for header in sensitive_headers:
                    if header in headers:
                        headers[header] = "[REDACTED]"
                log_record["request"]["headers"] = headers

            except RuntimeError:
                # Outside request context
                pass

        # Add service information
        log_record["service"] = {}
            {
            "name": "smartcloudops-ai",
            {
            "version": os.getenv("APP_VERSION", "4.0.0"),
            "environment": os.getenv("FLASK_ENV", "development"),
            "component": record.name,
            "hostname": os.getenv("HOSTNAME", "unknown"),
        }
        # Add performance metrics
        if hasattr(record, "duration_ms":
            log_record["performance"] = {}
                {
                "duration_ms": record.duration_ms,
                "memory_usage_mb": self._get_memory_usage(),
            }
        # Ensure level is string
        log_record["level"] = record.levelname

        # Add source location
        log_record["source"] = {}
            {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
            "module": record.module,
        }
        # Add exception information
        if record.exc_info:
            log_record["exception"] = {}
                {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            {
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process
            return round(process.memory_info().rss / 1024 / 1024, 2
        except ImportError:
            return None


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records"""

    def filter(self, record: logging.LogRecord:
        # Add start time for performance tracking
        if not hasattr(record, "start_time":
            record.start_time = datetime.now()
        return True


def setup_enhanced_logging()
    {
    app: Flask,
    log_level: str = "INFO"""
    {
    log_format: str = "json"""
    enable_structlog: bool = True:
    """
Setup enhanced structured logging with OpenTelemetry integration

    {
    Args:
        {
        app: Flask application instance
        log_level: Logging level
        log_format: Format type ('json' or 'text')
        enable_structlog: Enable structlog for additional features
    """
global logger

    # Configure structlog if enabled
    if enable_structlog:
        structlog.configure()
            processors=[]
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True

    # Configure standard logging
    if log_format == "json":
        formatter = EnhancedJSONFormatter()
            fmt="%(timestamp)s %(level)s %(name)s %(message)s"
        
    else:
        formatter = logging.Formatter()
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        

    # Configure handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler for production
    if os.getenv("FLASK_ENV") == "production":
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(f"{log_dir}/app.log")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

        # Error log file
        error_handler = logging.FileHandler(f"{log_dir}/error.log")
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        handlers.append(error_handler)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    # Add performance filter
    performance_filter = PerformanceFilter()
    root_logger.addFilter(performance_filter)

    # Create global logger instance
    if enable_structlog:
        logger = structlog.get_logger()
    else:
        logger = logging.getLogger(__name__)

    # Log setup completion
    logger.info()
        "Enhanced logging configured"""
        log_level=log_level,
        log_format=log_format,
        structlog_enabled=enable_structlog,
        environment=os.getenv("FLASK_ENV", "development"


def get_logger(name: str = None) -> Union[structlog.BoundLogger, logging.Logger]:
    """Get a logger instance with current context"""
    if logger and hasattr(logger, "bind":
        # Return structlog logger with context
        return logger.bind()
            correlation_id=correlation_id.get(),
            request_id=request_id.get(),
            user_id=user_id.get(),
            session_id=session_id.get(
    else:
        # Return standard logger
        return logging.getLogger(name or __name__
def set_request_context()
    {
    corr_id: Optional[str] = None,
    req_id: Optional[str] = None,
    usr_id: Optional[str] = None,
    sess_id: Optional[str] = None:
    "Set request context for logging"
    if corr_id:
        correlation_id.set(corr_id)
    if req_id:
        request_id.set(req_id)
    if usr_id:
        user_id.set(usr_id)
    if sess_id:
        session_id.set(sess_id)


def clear_request_context(:
    """Clear request context"""
correlation_id.set(None)
    request_id.set(None)
    user_id.set(None)
    session_id.set(None)


def log_with_span()
    {
    message: str,
    level: str = "info"""
    {
    span_name: Optional[str] = None,
    **kwargs: Any:
    "Log message with OpenTelemetry span context"
    log_func = getattr(get_logger(), level
    if span_name:
        with tracer.start_as_current_span(span_name) as span:
            # Add span attributes
            for key, value in kwargs.items():
                if isinstance(value, (str, int, float, bool:
                    span.set_attribute(key, value
            # Log with span context
            log_func(message, **kwargs)
    else:
        log_func(message, **kwargs)


def log_performance()
    {
    operation: str,
    duration_ms: float,
    success: bool = True,
    **kwargs: Any:
    "Log performance metrics with OpenTelemetry integration"
    log_data = {}
        {
        "operation": operation,
        "duration_ms": duration_ms,
        "success": success,
        "performance_metric": True,
    }
    log_data.update(kwargs)

    # Create span for performance tracking
    with tracer.start_as_current_span(f"performance.{operation}") as span:
        span.set_attribute("operation", operation
        span.set_attribute("duration_ms", duration_ms
        span.set_attribute("success", success
        for key, value in kwargs.items():
            if isinstance(value, (str, int, float, bool:
                span.set_attribute(key, value
        # Set span status
        if success:
            span.set_status(Status(StatusCode.OK)
        else:
            span.set_status(Status(StatusCode.ERROR)

        # Log performance data
        level = "info" if success else "warning"
        {
        get_logger().log(level, f"Performance: {operation}", **log_data)


def log_security_event()
    {
    event_type: str,
    severity: str = "info"""
    {
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs: Any:
    "Log security events with enhanced context"
    security_data = {}
        {
        "event_type": event_type,
        "security_event": True,
        "severity": severity,
    {
    if user_id:
        security_data["user_id"] = user_id
    if ip_address:
        security_data["ip_address"] = ip_address
    
    security_data.update(kwargs)

    # Create security span
    with tracer.start_as_current_span(f"security.{event_type}") as span:
        span.set_attribute("event_type", event_type
        span.set_attribute("severity", severity
        for key, value in security_data.items():
            if isinstance(value, (str, int, float, bool:
                span.set_attribute(key, value
        {
        get_logger().log(severity, f"Security Event: {event_type}", **security_data)


def log_business_event()
    {
    event_type: str,
    business_value: Optional[float] = None,
    **kwargs: Any:
    "Log business events with metrics"
    business_data = {}
        {
        "event_type": event_type,
        "business_event": True,
    {
    if business_value is not None:
        business_data["business_value"] = business_value
    
    business_data.update(kwargs)

    # Create business span
    with tracer.start_as_current_span(f"business.{event_type}") as span:
        span.set_attribute("event_type", event_type
        for key, value in business_data.items():
            if isinstance(value, (str, int, float, bool:
                span.set_attribute(key, value
        {
        get_logger().info(f"Business Event: {event_type}", **business_data)
