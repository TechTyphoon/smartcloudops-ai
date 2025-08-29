#!/usr/bin/env python3
"""
Flask Middleware for Observability Integration
"""

import time

from flask import Flask, g, has_request_context, request, response
from werkzeug.serving import WSGIRequestHandler

from .logging_config import get_correlation_id, get_logger, set_correlation_id
from .metrics import metrics_collector
from .tracing import get_span_id, get_trace_id

logger = get_logger(__name__)


class ObservabilityMiddleware:
    """Middleware to integrate observability features with Flask"""

    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize observability middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)

        # Add metrics endpoint
        @app.route("/metrics")
        def metrics_endpoint():
            """Prometheus metrics endpoint"""
            return response.Response(
                metrics_collector.get_metrics(),
                mimetype="text/plain; version=0.0.4; charset=utf-8",
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
        logger.info(
            "Request started",
            extra={
                "event_type": "request_start",
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
                "content_length": request.content_length or 0,
            },
        )

    def after_request(self, response):
        """Called after each request"""
        if not has_request_context():
            return response

        # Calculate request duration
        duration = time.time() - getattr(g, "request_start_time", time.time())

        # Get request/response sizes
        request_size = request.content_length or 0
        response_size = len(response.get_data() if response.get_data() else 0)

        # Record metrics
        metrics_collector.record_http_request(
            method=request.method,
            endpoint=self._get_endpoint_name(),
            status_code=response.status_code,
            duration=duration,
            request_size=request_size,
            response_size=response_size,
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = get_correlation_id()
        response.headers["X-Trace-ID"] = get_trace_id() or ""
        response.headers["X-Span-ID"] = get_span_id() or ""

        # Log request completion
        logger.info(
            "Request completed",
            extra={
                "event_type": "request_complete",
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration": duration,
                "request_size": request_size,
                "response_size": response_size,
            },
        )

        return response

    def teardown_request(self, exception=None):
        """Called after request is processed"""
        if exception:
            logger.error(
                "Request failed",
                extra={
                    "event_type": "request_error",
                    "method": request.method,
                    "path": request.path,
                    "error": str(exception),
                    "error_type": type(exception).__name__,
                },
            )

    def _get_endpoint_name(self) -> str:
        """Get endpoint name for metrics"""
        if request.endpoint:
            return request.endpoint
        return request.path

    def _get_request_id(self) -> str:
        """Get unique request ID"""
        return get_correlation_id() or "unknown"


class RequestLoggingMiddleware:
    """Simple request logging middleware"""

    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize request logging middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """Log request start"""
        g.start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
            },
        )

    def after_request(self, response):
        """Log request completion"""
        duration = time.time() - getattr(g, "start_time", 0)
        logger.info(
            f"Response: {response.status_code} ({duration:.3f}s)",
            extra={
                "status_code": response.status_code,
                "duration": duration,
            },
        )
        return response


class ErrorHandlingMiddleware:
    """Error handling middleware"""

    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize error handling middleware"""
        app.register_error_handler(404, self.handle_404)
        app.register_error_handler(500, self.handle_500)
        app.register_error_handler(Exception, self.handle_exception)

    def handle_404(self, error):
        """Handle 404 errors"""
        logger.warning(
            "404 Not Found",
            extra={
                "path": request.path,
                "method": request.method,
                "remote_addr": request.remote_addr,
            },
        )
        return {"error": "Not Found", "status_code": 404}, 404

    def handle_500(self, error):
        """Handle 500 errors"""
        logger.error(
            "500 Internal Server Error",
            extra={
                "path": request.path,
                "method": request.method,
                "error": str(error),
            },
        )
        return {"error": "Internal Server Error", "status_code": 500}, 500

    def handle_exception(self, error):
        """Handle general exceptions"""
        logger.error(
            f"Unhandled exception: {error}",
            extra={
                "path": request.path,
                "method": request.method,
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )
        return {"error": "Internal Server Error", "status_code": 500}, 500


# Global middleware instances
observability_middleware = ObservabilityMiddleware()
request_logging_middleware = RequestLoggingMiddleware()
error_handling_middleware = ErrorHandlingMiddleware()
