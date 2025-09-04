#!/usr/bin/env python3
"""
Error Handling System for Smart CloudOps AI - Minimal Working Version
Enterprise-grade error handling with structured logging and monitoring
"""

import logging
import traceback
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, List, Optional

try:
    from flask import current_app, jsonify, request
except ImportError:
    # Handle case where Flask is not available
    request = None

    def jsonify(x):
        return x

    current_app = None

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

            return {
                "method": request.method,
                "url": str(request.url),
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
            if not request:
                return {}

            # Get user info from request if available
            user_info = {}
            if hasattr(request, "user"):
                user_info = {
                    "user_id": getattr(request.user, "id", None),
                    "username": getattr(request.user, "username", None),
                    "role": getattr(request.user, "role", None),
                }

            return user_info

        except Exception:
            return {}

    def _format_error_message(self, error_record: Dict[str, Any]) -> str:
        """Format error message for logging."""
        try:
            message_parts = [
                f"Error: {error_record['error_type']}",
                f"Message: {error_record['error_message']}",
            ]

            if error_record.get("context"):
                message_parts.append(f"Context: {error_record['context']}")

            if error_record.get("request_info", {}).get("url"):
                message_parts.append(f"URL: {error_record['request_info']['url']}")

            return " | ".join(message_parts)

        except Exception:
            return f"Error: {error_record.get('error_type', 'Unknown')}"

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        try:
            return {
                "total_errors": sum(self.error_counts.values()),
                "error_counts": self.error_counts.copy(),
                "recent_errors": len(self.error_history),
                "max_history_size": self.max_history_size,
            }
        except Exception as e:
            logger.error(f"Failed to get error stats: {e}")
            return {}

    def clear_history(self) -> bool:
        """Clear error history."""
        try:
            self.error_history.clear()
            self.error_counts.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear error history: {e}")
            return False

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors."""
        try:
            return self.error_history[-limit:] if self.error_history else []
        except Exception as e:
            logger.error(f"Failed to get recent errors: {e}")
            return []


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(func):
    """Decorator to handle errors in functions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            error_handler.log_error(e, context={"function": func.__name__})

            # Return error response if in Flask context
            if jsonify and request:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "An error occurred while processing your request",
                            "error_type": type(e).__name__,
                        }
                    ),
                    500,
                )

            # Re-raise the exception if not in Flask context
            raise

    return wrapper


def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    severity: str = "INFO",
    user_id: Optional[str] = None,
) -> bool:
    """Log security-related events."""
    try:
        security_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "user_id": user_id,
            "request_info": error_handler._get_request_info(),
        }

        log_message = (
            f"Security Event: {event_type} | Severity: {severity} | Details: {details}"
        )

        if severity == "CRITICAL":
            logger.critical(log_message, extra={"security_record": security_record})
        elif severity == "ERROR":
            logger.error(log_message, extra={"security_record": security_record})
        elif severity == "WARNING":
            logger.warning(log_message, extra={"security_record": security_record})
        else:
            logger.info(log_message, extra={"security_record": security_record})

        return True

    except Exception as e:
        logger.error(f"Failed to log security event: {e}")
        return False


def validate_error_response(response: Dict[str, Any]) -> bool:
    """Validate error response structure."""
    try:
        required_fields = ["status", "message"]

        for field in required_fields:
            if field not in response:
                return False

        if response["status"] != "error":
            return False

        return True

    except Exception:
        return False


def create_error_response(
    message: str,
    error_type: str = "GeneralError",
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create standardized error response."""
    try:
        response = {
            "status": "error",
            "message": message,
            "error_type": error_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if details:
            response["details"] = details

        # Log the error
        error_handler.log_error(
            Exception(message),
            context={
                "error_type": error_type,
                "status_code": status_code,
                "details": details,
            },
            level="ERROR",
        )

        return response

    except Exception as e:
        logger.error(f"Failed to create error response: {e}")
        return {
            "status": "error",
            "message": "Failed to create error response",
            "error_type": "ErrorHandlerError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def handle_database_errors(func):
    """Decorator to handle database-specific errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            type(e).__name__

            # Handle specific database errors
            if "connection" in str(e).lower():
                error_handler.log_error(
                    e, context={"error_category": "database_connection"}, level="ERROR"
                )
                return create_error_response(
                    "Database connection error", "DatabaseConnectionError", 503
                )
            elif "timeout" in str(e).lower():
                error_handler.log_error(
                    e, context={"error_category": "database_timeout"}, level="WARNING"
                )
                return create_error_response(
                    "Database operation timeout", "DatabaseTimeoutError", 408
                )
            elif "constraint" in str(e).lower():
                error_handler.log_error(
                    e,
                    context={"error_category": "database_constraint"},
                    level="WARNING",
                )
                return create_error_response(
                    "Data validation error", "DataValidationError", 400
                )
            else:
                error_handler.log_error(
                    e, context={"error_category": "database_general"}, level="ERROR"
                )
                return create_error_response(
                    "Database operation failed", "DatabaseError", 500
                )

    return wrapper


def handle_authentication_errors(func):
    """Decorator to handle authentication-specific errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            type(e).__name__

            # Handle specific authentication errors
            if "token" in str(e).lower():
                error_handler.log_error(
                    e,
                    context={"error_category": "authentication_token"},
                    level="WARNING",
                )
                return create_error_response(
                    "Invalid authentication token", "AuthenticationError", 401
                )
            elif "permission" in str(e).lower():
                error_handler.log_error(
                    e,
                    context={"error_category": "authentication_permission"},
                    level="WARNING",
                )
                return create_error_response(
                    "Insufficient permissions", "PermissionError", 403
                )
            else:
                error_handler.log_error(
                    e,
                    context={"error_category": "authentication_general"},
                    level="ERROR",
                )
                return create_error_response(
                    "Authentication failed", "AuthenticationError", 401
                )

    return wrapper
