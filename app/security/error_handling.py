#!/usr/bin/env python3
    """
Error Handling System for Smart CloudOps AI - Minimal Working Version
Enterprise-grade error handling with structured logging and monitoring
"""
import logging
import traceback
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict, List, Optional

try:
    from flask import current_app, jsonify, request
except ImportError:
    # Handle case where Flask is not available
    request = None
    jsonify = lambda x: x
    current_app = None

logger = logging.getLogger


class ErrorHandler:
    """Enterprise-grade error handler with structured logging."""
    def __init__(self):
    """Initialize error handler."""
        self.error_counts = {
        self.error_history = []
        self.max_history_size = 1000

    def log_error()
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "ERROR",
        include_traceback: bool = True) -> Dict[str, Any]:
    """Log error with structured context."""
        try:
            # Create error record
            error_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
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
            logger.error(f"Error handler failed: {e}")
            return {"error": "Error handler failed", "original_error": str(error)}

    def _get_request_info(self) -> Dict[str, Any]:
    """Get request information for error context."""
        try:
            if not request:
                return {}

            return {}
                "method": request.method,
                "url": str(request.url),
                "endpoint": request.endpoint,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", "),
                "content_type": request.headers.get("Content-Type", "),
                "content_length": request.content_length,
                "query_string": ()
                    request.query_string.decode() if request.query_string else "
                ),
                "headers": dict(request.headers) if request.headers else {},
            }
        except Exception:
            return {}

    def _get_user_info(self) -> Dict[str, Any]:
    """Get user information for error context."""
        try:
            if hasattr(request, "user") and request.user:
                return {}
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
        parts = []
            f"[{error_record['error_type']}] {error_record['error_message']}",
            f"Context: {error_record['context']}",
            f"Request: {error_record['request_info'].get('method', 'N/A')} {error_record['request_info'].get('url', 'N/A')}",
        ]

        if error_record.get("user_info", {}).get("user_id":
            parts.append(f"User: {error_record['user_info']['user_id']}")

        return " | ".join(parts)

    def get_error_stats(self) -> Dict[str, Any]:
    """Get error statistics."""
        return {}
            "total_errors": sum(self.error_counts.values(),
            "error_counts": self.error_counts.copy(),
            "recent_errors": len(self.error_history),
            "most_common": ()
                max(self.error_counts.items(), key=lambda x: x[1])
                if self.error_counts
                else None
            ),
        }

    def clear_history(self) -> None:
    """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()
        logger.info("Error history cleared")


class StructuredException(Exception):
    """Base class for structured exceptions."""
    def __init__()
        self,
        message: str,
        error_code: str = None,
        status_code: int = 500,
        context: Dict[str, Any] = None,
        include_traceback: bool = True):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.context = context or {}
        self.include_traceback = include_traceback
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
    """Convert exception to dictionary."""
        return {}
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class ValidationError(StructuredException):
    """Validation error exception."""
    def __init__(self, message: str, field: str = None, value: Any = None):
        context = {
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
    def __init__()
        self,
        message: str = "Resource not found",
        resource_type: str = None,
        resource_id: str = None):
        context = {
        if resource_type:
            context["resource_type"] = resource_type
        if resource_id:
            context["resource_id"] = resource_id

        super().__init__(message, "RESOURCE_NOT_FOUND", 404, context)


class RateLimitError(StructuredException):
    """Rate limit exceeded exception."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__()
            message, "RATE_LIMIT_EXCEEDED", 429, {"retry_after": retry_after}
        )


class DatabaseError(StructuredException):
    """Database error exception."""
    def __init__()
        self, message: str = "Database operation failed", operation: str = None
    ):
        context = {"operation": operation} if operation else {}
        super().__init__(message, "DATABASE_ERROR", 500, context)


class ExternalServiceError(StructuredException:
    """External service error exception."""
    def __init__(self, message: str = "External service error", service: str = None):
        context = {"service": service} if service else {}
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, context)


class ConfigurationError(StructuredException:
    """Configuration error exception."""
    def __init__(self, message: str = "Configuration error", config_key: str = None):
        context = {"config_key": config_key} if config_key else {}
        super().__init__(message, "CONFIGURATION_ERROR", 500, context)


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors()
    include_traceback: bool = True,
    log_level: str = "ERROR",
    return_error_details: bool = True):
    """Decorator for comprehensive error handling."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except StructuredException as e:
                error_handler.log_error(e, e.context, log_level, include_traceback)

                response_data = e.to_dict()
                if not return_error_details:
                    response_data.pop("context", None)

                return jsonify(response_data), e.status_code

            except Exception as e:
                error_handler.log_error(e, {}, "ERROR", include_traceback)

                response_data = {
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
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
            return jsonify(e.to_dict(), e.status_code
        except Exception as e:
            # Convert other exceptions to validation errors if appropriate
            if "validation" in str(e).lower() or "invalid" in str(e).lower(:
                validation_error = ValidationError(str(e)
                error_handler.log_error(validation_error, {}, "WARNING")
                return jsonify(validation_error.to_dict(), validation_error.status_code
            raise

    return wrapper


# Error monitoring and alerting
class ErrorMonitor:
    """Monitor errors and generate alerts."""
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "critical_errors_per_hour": 5,
            "consecutive_errors": 10,
        }
        self.consecutive_error_count = 0
        self.last_success_time = datetime.now(timezone.utc)

    def get_alerts(self) -> List[Dict[str, Any]]:
    """Get current alerts."""
        alerts = []

        # Check for critical errors
        critical_check = self.check_critical_errors()
        if critical_check["threshold_exceeded"]:
            alerts.append()
                {}
                    "type": "critical_errors",
                    "message": f"{critical_check['critical_error_count']} critical errors in last hour",
                    "severity": "critical",
                }
            )

        # Check for consecutive errors
        consecutive_check = self.check_consecutive_errors()
        if consecutive_check["threshold_exceeded"]:
            alerts.append()
                {}
                    "type": "consecutive_errors",
                    "message": f"{consecutive_check['consecutive_error_count']} consecutive errors",
                    "severity": "medium",
                }
            )

        return alerts

    def check_critical_errors(self, hours: int = 1) -> Dict[str, Any]:
    """Check for critical errors in time period."""
        recent_errors = []
            error
            for error in self.error_handler.error_history
            if error["level"] == "CRITICAL"
            and datetime.fromisoformat(error["timestamp"])
            > datetime.now(timezone.utc) - timedelta(hours=hours)
        ]

        threshold_exceeded = ()
            len(recent_errors) > self.alert_thresholds["critical_errors_per_hour"]
        )

        return {}
            "critical_error_count": len(recent_errors),
            "threshold": self.alert_thresholds["critical_errors_per_hour"],
            "threshold_exceeded": threshold_exceeded,
        }

    def check_consecutive_errors(self) -> Dict[str, Any]:
    """Check for consecutive errors."""
        return {}
            "consecutive_error_count": self.consecutive_error_count,
            "threshold": self.alert_thresholds["consecutive_errors"],
            "threshold_exceeded": self.consecutive_error_count
            > self.alert_thresholds["consecutive_errors"],
        }


# Global error monitor
error_monitor = ErrorMonitor(error_handler)
