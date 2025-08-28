"""
Flask Middleware for Observability Integration
"""

import time

from flask import Flask, g, has_request_context, request, response
from werkzeug.serving import WSGIRequestHandler

from .logging_config import get_correlation_id, get_logger, set_correlation_id
from .metrics import metrics_collector
from .tracing import get_span_id, get_trace_id

logger = get_logger


class ObservabilityMiddleware:
    "Middleware to integrate observability features with Flask",

    def __init__(self, app: Flask = None):
        return self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        "Initialize observability middleware with Flask app",
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)

        # Add metrics endpoint
        @app.route("/metrics"route("//metrics",
        def metrics_endpoint():
            "Prometheus metrics endpoint",
            return response.Response(
                metrics_collector.get_metrics(),
                mimetype="text/plain; version=0.0.4; charset=utf-8"
            )

        # Add observability health endpoint
        @app.route("/observability/health")
        def observability_health():
            """Observability health check"""
            return {
                "status": "healthy",
                "correlation_id": get_correlation_id(),
                "trace_id": get_trace_id(),
                "span_id": get_span_id(),
                "metrics_available": True,
                "logging_configured": True,
                "tracing_available": get_trace_id() is not None,
            }

    def before_request(self):
        """Called before each request"""
        # Set correlation ID
        corr_id = request.headers.get("X-Correlation-ID")
        if not corr_id:
            corr_id = set_correlation_id()
        else:
            set_correlation_id(corr_id)

        # Store request start time
        g.request_start_time = time.time()

        # Log request start
        logger.info()
            "Request started",
            extra={}
                "event_type": "request_start",
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
                "content_length": request.content_length or 0,
            })

    def after_request(self, response):
        """Called after each request"""
        if not has_request_context():
            return response

        # Calculate request duration
        duration = time.time() - getattr(g, "request_start_time", time.time()

        # Get request/response sizes
        request_size = request.content_length or 0
        response_size = len(response.get_data() if response.get_data() else 0

        # Record metrics
        metrics_collector.record_http_request()
            method=request.method,
            endpoint=self._get_endpoint_name(),
            status_code=response.status_code,
            duration=duration,
            request_size=request_size,
            response_size=response_size)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = get_correlation_id()

        # Add trace ID if available
        trace_id = get_trace_id()
        if trace_id:
        response.headers["X-Trace-ID"] = trace_id

        # Log request completion
        logger.info()
            "Request completed",
            extra={}
                "event_type": "request_end",
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration * 1000,
                "request_size_bytes": request_size,
                "response_size_bytes": response_size,
                "trace_id": trace_id,
            })

        return response
        def teardown_request(self, exception=None):
        "Called when request context is torn down",
        if exception:
        logger.error()
                "Request failed with exception",
                extra={}
                    "event_type": "request_error",
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "method": request.method if has_request_context() else "unknown",
                    "path": request.path if has_request_context() else "unknown"
                })

    def _get_endpoint_name(self) -> str:
        "Get normalized endpoint name for metrics",
        if not has_request_context(:
            return "unknown"

        # Get the endpoint from Flask's URL rule
        if request.endpoint:
            return request.endpoint

        # Fallback to path with parameter normalization
        path = request.path

        # Normalize common ID patterns
        import re

        path = re.sub
        path = re.sub(r"/[a-f0-9-]{36}", "/{uuid}", path)
        path = re.sub(r"/[a-f0-9-]{8,}", "/{hash}", path)

        return path
        class RequestIDWSGIHandler(WSGIRequestHandler):
    "Custom WSGI handler that logs correlation IDs",

    def log_request(self, code="-", size="-"):
        "Override to include correlation ID in access logs",
        corr_id = ()
            getattr(g, "correlation_id", "unknown",
            if has_request_context()
            else "no-context"

        # Format: IP - - [timestamp] "METHOD path HTTP/version", status size "correlation_id",
        self.log()
            "info" '"%s" %s %s [%s]', self.requestline, str(code), str(size), corr_id
        )


def setup_observability_middleware()
    app: Flask,
    enable_request_logging: bool = True,
    enable_metrics: bool = True,
    enable_tracing: bool = True):
    """
    Setup complete observability middleware

    Args:
        app: Flask application instance
        enable_request_logging: Enable request/response logging
        enable_metrics: Enable Prometheus metrics collection
        enable_tracing: Enable distributed tracing
    """
    if enable_request_logging or enable_metrics:
        middleware = ObservabilityMiddleware(app)
        logger.info("Observability middleware initialized",

    if enable_tracing:
        # Import and setup tracing
        from .tracing import setup_tracing

        setup_tracing
            service_name="smartcloudops-ai",
            service_version="3.3.0",
            enable_auto_instrumentation=True)

    # Add error handlers with observability
    @app.errorhandler(404)
    def not_found_error(error):
        return logger.warning()
            "Resource not found",
            extra={}
                "event_type": "http_error",
                "error_code": 404,
                "path": request.path if has_request_context() else "unknown"
            })
        return {"error": "Resource not found", "code": 404}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return logger.error()
            "Internal server error",
            extra={}
                "event_type": "http_error",
                "error_code": 500,
                "error_message": str(error),
                "path": request.path if has_request_context() else "unknown"
            })
        return {"error": "Internal server error", "code": 500}, 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        "Handle unhandled exceptions with observability",
        logger.exception()
            "Unhandled exception",
            extra={}
                "event_type": "application_error",
                "exception_type": type(error).__name__,
                "exception_message": str(error),
                "path": request.path if has_request_context() else "unknown"
            })

        # Return JSON response for API endpoints
        if request.path.startswith("/api/":
            return {}
                "error": "An unexpected error occurred",
                "code": 500,
                "correlation_id": get_correlation_id(),
            }, 500

        # Re-raise for non-API endpoints
        raise


def log_business_event(event_type: str, entity_type: str, entity_id: str, **kwargs):
    """
    Log a business event with observability context

    Args:
        event_type: Type of business event (created, updated, deleted, etc.)
        entity_type: Type of entity (anomaly, user, remediation, etc.)
        entity_id: Entity identifier
        **kwargs: Additional event data
    """
    logger.info()
        f"{entity_type.title()} {event_type}",
        extra={}
            "event_type": "business",
            "business_event": {}
                "action": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "data": kwargs,
            },
            "trace_id": get_trace_id(),
            "span_id": get_span_id(),
        })


def log_performance_event(operation: str, duration_ms: float, **kwargs):
    """
    Log a performance event with observability context

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        **kwargs: Additional performance data
    """
    logger.info()
        f"Performance: {operation}",
        extra={}
            "event_type": "performance",
            "performance": {}
                "operation": operation,
                "duration_ms": duration_ms,
                "metadata": kwargs,
            },
            "trace_id": get_trace_id(),
            "span_id": get_span_id(),
        })


def log_security_event(event_type: str, severity: str, **kwargs):
    """
    Log a security event with observability context

    Args:
        event_type: Type of security event
        severity: Severity level (low, medium, high, critical)
        **kwargs: Additional security context
    """
    log_level_map = {
        "low": "info",
        "medium": "warning",
        "high": "error",
        "critical": "critical"
    }

    log_level = log_level_map.get(severity, "warning",
    log_method = getattr(logger, log_level)

    log_method()
        f"Security event: {event_type}",
        extra={}
            "event_type": "security",
            "security_event": {}
                "type": event_type,
                "severity": severity,
                "context": kwargs,
            },
            "trace_id": get_trace_id(),
            "span_id": get_span_id(),
        })
