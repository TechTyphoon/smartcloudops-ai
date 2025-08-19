#!/usr/bin/env python3
"""
Error Handling System for Smart CloudOps AI
Enterprise-grade error handling with structured logging and monitoring
"""

import logging
import traceback
import sys
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Union, Callable
from flask import request, jsonify, current_app
from app.security.input_validation import sanitize_log_message

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Enterprise-grade error handler with structured logging."""

    def __init__(self):
        """Initialize error handler."""
        self.error_counts = {}
        self.error_history = []
        self.max_history_size = 1000

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "ERROR",
        include_traceback: bool = True,
    ) -> Dict[str, Any]:
        """Log error with structured context."""
        try:
            # Sanitize error message
            error_message = sanitize_log_message(str(error))

            # Create error record
            error_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "error_message": error_message,
                "level": level,
                "context": context or {},
                "request_info": self._get_request_info(),
                "user_info": self._get_user_info(),
                "traceback": traceback.format_exc() if include_traceback else None,
            }

            # Update error counts
            error_type = type(error).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

            # Add to history
            self.error_history.append(error_record)
            if len(self.error_history) > self.max_history_size:
                self.error_history.pop(0)

            # Log with appropriate level
            log_message = self._format_error_message(error_record)
            if level == "CRITICAL":
                logger.critical(log_message, extra={"error_record": error_record})
            elif level == "ERROR":
                logger.error(log_message, extra={"error_record": error_record})
            elif level == "WARNING":
                logger.warning(log_message, extra={"error_record": error_record})
            else:
                logger.info(log_message, extra={"error_record": error_record})

            return error_record

        except Exception as e:
            # Fallback logging if error handling fails
            logger.error(f"Error in error handler: {e}")
            return {"error": "Error handling failed", "original_error": str(error)}

    def _get_request_info(self) -> Dict[str, Any]:
        """Get request information for error context."""
        try:
            if not request:
                return {}

            return {
                "method": request.method,
                "url": request.url,
                "endpoint": request.endpoint,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
                "content_type": request.headers.get("Content-Type", ""),
                "content_length": request.content_length,
                "query_string": (
                    request.query_string.decode() if request.query_string else ""
                ),
                "headers": dict(request.headers) if request.headers else {},
            }
        except Exception:
            return {}

    def _get_user_info(self) -> Dict[str, Any]:
        """Get user information for error context."""
        try:
            if hasattr(request, "user") and request.user:
                return {
                    "user_id": request.user.get("user_id"),
                    "username": request.user.get("username"),
                    "role": request.user.get("role"),
                    "permissions": request.user.get("permissions", []),
                }
            return {}
        except Exception:
            return {}

    def _format_error_message(self, error_record: Dict[str, Any]) -> str:
        """Format error message for logging."""
        parts = [
            f"[{error_record['error_type']}] {error_record['error_message']}",
            f"Context: {error_record['context']}",
            f"Request: {error_record['request_info'].get('method', 'N/A')} {error_record['request_info'].get('url', 'N/A')}",
        ]

        if error_record["user_info"]:
            parts.append(f"User: {error_record['user_info'].get('username', 'N/A')}")

        return " | ".join(parts)

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-10:] if self.error_history else [],
            "error_types": list(self.error_counts.keys()),
        }

    def clear_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()


# Global error handler instance
error_handler = ErrorHandler()


class StructuredException(Exception):
    """Base class for structured exceptions."""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.context = context or {}
        self.include_traceback = include_traceback

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
            "timestamp": datetime.utcnow().isoformat(),
        }


class ValidationError(StructuredException):
    """Validation error exception."""

    def __init__(self, message: str, field: str = None, value: Any = None):
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)

        super().__init__(message, "VALIDATION_ERROR", 400, context)


class AuthenticationError(StructuredException):
    """Authentication error exception."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class AuthorizationError(StructuredException):
    """Authorization error exception."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)


class ResourceNotFoundError(StructuredException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str = None,
        resource_id: str = None,
    ):
        context = {}
        if resource_type:
            context["resource_type"] = resource_type
        if resource_id:
            context["resource_id"] = resource_id

        super().__init__(message, "RESOURCE_NOT_FOUND", 404, context)


class RateLimitError(StructuredException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message, "RATE_LIMIT_EXCEEDED", 429, {"retry_after": retry_after}
        )


class DatabaseError(StructuredException):
    """Database error exception."""

    def __init__(
        self, message: str = "Database operation failed", operation: str = None
    ):
        context = {"operation": operation} if operation else {}
        super().__init__(message, "DATABASE_ERROR", 500, context)


class ExternalServiceError(StructuredException):
    """External service error exception."""

    def __init__(self, message: str = "External service error", service: str = None):
        context = {"service": service} if service else {}
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, context)


class ConfigurationError(StructuredException):
    """Configuration error exception."""

    def __init__(self, message: str = "Configuration error", config_key: str = None):
        context = {"config_key": config_key} if config_key else {}
        super().__init__(message, "CONFIGURATION_ERROR", 500, context)


def handle_errors(
    include_traceback: bool = True,
    log_level: str = "ERROR",
    return_error_details: bool = False,
):
    """
    Decorator for handling errors in Flask endpoints.

    Args:
        include_traceback: Whether to include traceback in logs
        log_level: Log level for errors
        return_error_details: Whether to return error details in response
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except StructuredException as e:
                # Log structured exception
                error_handler.log_error(e, e.context, log_level, include_traceback)

                # Return structured error response
                response_data = e.to_dict()
                if not return_error_details:
                    response_data.pop("context", None)

                return jsonify(response_data), e.status_code

            except Exception as e:
                # Log unexpected exception
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                }
                error_handler.log_error(e, context, log_level, include_traceback)

                # Return generic error response
                response_data = {
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                if return_error_details:
                    response_data["error_type"] = type(e).__name__

                return jsonify(response_data), 500

        return wrapper

    return decorator


def handle_validation_errors(func):
    """Decorator for handling validation errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            error_handler.log_error(e, e.context, "WARNING")
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            # Convert other exceptions to validation errors if appropriate
            if "validation" in str(e).lower() or "invalid" in str(e).lower():
                validation_error = ValidationError(str(e))
                error_handler.log_error(validation_error, {}, "WARNING")
                return jsonify(validation_error.to_dict()), validation_error.status_code
            raise

    return wrapper


def handle_auth_errors(func):
    """Decorator for handling authentication errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AuthenticationError, AuthorizationError) as e:
            error_handler.log_error(e, e.context, "WARNING")
            return jsonify(e.to_dict()), e.status_code

    return wrapper


def handle_database_errors(func):
    """Decorator for handling database errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            error_handler.log_error(e, e.context, "ERROR")
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            # Convert database-related exceptions
            if any(
                db_error in str(e).lower()
                for db_error in ["database", "sql", "connection", "timeout"]
            ):
                db_error = DatabaseError(f"Database operation failed: {str(e)}")
                error_handler.log_error(db_error, {"original_error": str(e)}, "ERROR")
                return jsonify(db_error.to_dict()), db_error.status_code
            raise

    return wrapper


def handle_external_service_errors(func):
    """Decorator for handling external service errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ExternalServiceError as e:
            error_handler.log_error(e, e.context, "ERROR")
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            # Convert network/HTTP errors
            if any(
                net_error in str(e).lower()
                for net_error in ["connection", "timeout", "http", "api"]
            ):
                service_error = ExternalServiceError(
                    f"External service error: {str(e)}"
                )
                error_handler.log_error(
                    service_error, {"original_error": str(e)}, "ERROR"
                )
                return jsonify(service_error.to_dict()), service_error.status_code
            raise

    return wrapper


# Error monitoring and alerting
class ErrorMonitor:
    """Monitor errors and generate alerts."""

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "critical_errors": 5,  # 5 critical errors per hour
            "consecutive_errors": 3,  # 3 consecutive errors
        }
        self.consecutive_error_count = 0
        self.last_error_time = None

    def check_error_rate(self, total_requests: int) -> Dict[str, Any]:
        """Check if error rate exceeds threshold."""
        error_stats = self.error_handler.get_error_stats()
        total_errors = error_stats["total_errors"]

        if total_requests == 0:
            error_rate = 0
        else:
            error_rate = total_errors / total_requests

        threshold_exceeded = error_rate > self.alert_thresholds["error_rate"]

        return {
            "error_rate": error_rate,
            "threshold": self.alert_thresholds["error_rate"],
            "threshold_exceeded": threshold_exceeded,
            "total_errors": total_errors,
            "total_requests": total_requests,
        }

    def check_critical_errors(self, hours: int = 1) -> Dict[str, Any]:
        """Check for critical errors in time period."""
        recent_errors = [
            error
            for error in self.error_handler.error_history
            if error["level"] == "CRITICAL"
            and datetime.fromisoformat(error["timestamp"])
            > datetime.utcnow() - timedelta(hours=hours)
        ]

        count = len(recent_errors)
        threshold_exceeded = count >= self.alert_thresholds["critical_errors"]

        return {
            "critical_error_count": count,
            "threshold": self.alert_thresholds["critical_errors"],
            "threshold_exceeded": threshold_exceeded,
            "recent_critical_errors": recent_errors,
        }

    def check_consecutive_errors(self) -> Dict[str, Any]:
        """Check for consecutive errors."""
        return {
            "consecutive_error_count": self.consecutive_error_count,
            "threshold": self.alert_thresholds["consecutive_errors"],
            "threshold_exceeded": self.consecutive_error_count
            >= self.alert_thresholds["consecutive_errors"],
        }

    def record_error(self, error: Exception) -> None:
        """Record error and update consecutive count."""
        current_time = datetime.utcnow()

        if self.last_error_time:
            time_diff = (current_time - self.last_error_time).total_seconds()
            if time_diff < 60:  # Within 1 minute
                self.consecutive_error_count += 1
            else:
                self.consecutive_error_count = 1
        else:
            self.consecutive_error_count = 1

        self.last_error_time = current_time

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts."""
        alerts = []

        # Check error rate (would need total request count from metrics)
        # error_rate_check = self.check_error_rate(total_requests)
        # if error_rate_check["threshold_exceeded"]:
        #     alerts.append({
        #         "type": "error_rate",
        #         "message": f"Error rate {error_rate_check['error_rate']:.2%} exceeds threshold {error_rate_check['threshold']:.2%}",
        #         "severity": "high"
        #     })

        # Check critical errors
        critical_check = self.check_critical_errors()
        if critical_check["threshold_exceeded"]:
            alerts.append(
                {
                    "type": "critical_errors",
                    "message": f"{critical_check['critical_error_count']} critical errors in last hour",
                    "severity": "critical",
                }
            )

        # Check consecutive errors
        consecutive_check = self.check_consecutive_errors()
        if consecutive_check["threshold_exceeded"]:
            alerts.append(
                {
                    "type": "consecutive_errors",
                    "message": f"{consecutive_check['consecutive_error_count']} consecutive errors",
                    "severity": "medium",
                }
            )

        return alerts


# Global monitor instance
error_monitor = ErrorMonitor(error_handler)


# Flask error handlers
def register_error_handlers(app):
    """Register Flask error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        error_handler.log_error(error, {"status_code": 400}, "WARNING")
        return (
            jsonify(
                {
                    "error": "BAD_REQUEST",
                    "message": "Invalid request",
                    "status_code": 400,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            400,
        )

    @app.errorhandler(401)
    def unauthorized(error):
        error_handler.log_error(error, {"status_code": 401}, "WARNING")
        return (
            jsonify(
                {
                    "error": "UNAUTHORIZED",
                    "message": "Authentication required",
                    "status_code": 401,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            401,
        )

    @app.errorhandler(403)
    def forbidden(error):
        error_handler.log_error(error, {"status_code": 403}, "WARNING")
        return (
            jsonify(
                {
                    "error": "FORBIDDEN",
                    "message": "Access denied",
                    "status_code": 403,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            403,
        )

    @app.errorhandler(404)
    def not_found(error):
        error_handler.log_error(error, {"status_code": 404}, "INFO")
        return (
            jsonify(
                {
                    "error": "NOT_FOUND",
                    "message": "Resource not found",
                    "status_code": 404,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            404,
        )

    @app.errorhandler(429)
    def too_many_requests(error):
        error_handler.log_error(error, {"status_code": 429}, "WARNING")
        return (
            jsonify(
                {
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests",
                    "status_code": 429,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            429,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        error_handler.log_error(error, {"status_code": 500}, "ERROR")
        return (
            jsonify(
                {
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        error_handler.log_error(error, {"status_code": 500}, "ERROR")
        return (
            jsonify(
                {
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )
