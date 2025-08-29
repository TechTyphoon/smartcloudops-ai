"""
Logging Configuration Module
Basic logging setup and correlation ID management
"""

import logging
import uuid
from typing import Optional

from flask import g, request


def setup_logging(log_level: str = "INFO") -> None:
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def correlation_id() -> Optional[str]:
    """Get current correlation ID from Flask context"""
    if hasattr(g, "correlation_id"):
        return g.correlation_id
    return None


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set correlation ID in Flask context"""
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    g.correlation_id = corr_id
    return corr_id


def get_request_correlation_id() -> str:
    """Get correlation ID from request headers or generate new one"""
    if hasattr(g, "correlation_id"):
        return g.correlation_id

    # Try to get from request headers
    corr_id = request.headers.get("X-Correlation-ID")
    if corr_id:
        g.correlation_id = corr_id
        return corr_id

    # Generate new correlation ID
    return set_correlation_id()
