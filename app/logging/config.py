#!/usr/bin/env python3
"""
Logging: Configuration Module
Centralized logging configuration for the application
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp if not present
        if not log_record.get("timestamp"):
            log_record["timestamp"] = record.created

        # Add log level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add module and function info
        if record.module:
            log_record["module"] = record.module
        if record.funcName:
            log_record["function"] = record.funcName
        if record.lineno:
            log_record["line"] = record.lineno


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json: bool = True,
    enable_console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Setup centralized logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_json: Enable JSON formatting
        enable_console: Enable console output
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatters
    if enable_json:
        json_formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(module)s %(function)s %(line)s %(message)s"
        )
        console_formatter = json_formatter
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(numeric_level)

        if enable_json:
            file_handler.setFormatter(json_formatter)
        else:
            file_handler.setFormatter(console_formatter)

        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_file": log_file,
            "enable_json": enable_json,
            "enable_console": enable_console,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request_info(logger: logging.Logger, request, response=None, duration=None):
    """
    Log HTTP request information.

    Args:
        logger: Logger instance
        request: Flask request object
        response: Flask response object (optional)
        duration: Request duration in seconds (optional)
    """
    log_data = {
        "method": request.method,
        "url": request.url,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
        "content_length": request.content_length,
    }

    if response:
        log_data["status_code"] = response.status_code
        log_data["response_size"] = (
            len(response.get_data()) if response.get_data() else 0
        )

    if duration:
        log_data["duration_ms"] = round(duration * 1000, 2)

    logger.info("HTTP Request", extra=log_data)


def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log error information with context.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if context:
        log_data.update(context)

    logger.error("Application Error", extra=log_data, exc_info=True)
