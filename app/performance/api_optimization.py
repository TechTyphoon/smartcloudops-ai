"""
API Performance Optimization Module
Response time monitoring and optimization
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import Flask, g, request


class PerformanceCollector:
    """Collects and tracks API performance metrics"""

    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "total_response_time": 0.0,
            "min_response_time": float("inf"),
            "max_response_time": 0.0,
            "error_count": 0,
        }
        self.start_time = datetime.now(timezone.utc)

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record a request metric"""
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += duration

        if duration < self.metrics["min_response_time"]:
            self.metrics["min_response_time"] = duration

        if duration > self.metrics["max_response_time"]:
            self.metrics["max_response_time"] = duration

        if status_code >= 400:
            self.metrics["error_count"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if self.metrics["request_count"] == 0:
            return {
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
                "request_count": 0,
                "error_rate": 0.0,
                "uptime_seconds": 0,
            }

        avg_response_time = (
            self.metrics["total_response_time"] / self.metrics["request_count"]
        )
        error_rate = (self.metrics["error_count"] / self.metrics["request_count"]) * 100
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        return {
            "avg_response_time": round(avg_response_time * 1000, 2),  # Convert to ms
            "min_response_time": round(self.metrics["min_response_time"] * 1000, 2),
            "max_response_time": round(self.metrics["max_response_time"] * 1000, 2),
            "request_count": self.metrics["request_count"],
            "error_rate": round(error_rate, 2),
            "uptime_seconds": round(uptime, 2),
        }


# Global performance collector
performance_collector = PerformanceCollector()


def init_performance_monitoring(app: Flask) -> None:
    """Initialize performance monitoring for the Flask app"""

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def record_request_metrics(response):
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time

            # Record metrics
            performance_collector.record_request(
                method=request.method,
                endpoint=request.endpoint,
                status_code=response.status_code,
                duration=duration,
            )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"
            response.headers["X-Request-ID"] = getattr(g, "correlation_id", "unknown")

        return response

    app.logger.info("Performance monitoring initialized")


def setup_api_optimization(app: Flask) -> None:
    """Setup API optimization features"""
    # Enable response compression
    app.config["COMPRESS_MIMETYPES"] = [
        "text/html",
        "text/css",
        "text/xml",
        "application/json",
        "application/javascript",
    ]

    # Enable response caching
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300  # 5 minutes

    app.logger.info("API optimization features enabled")


def shutdown_performance_monitoring() -> None:
    """Shutdown performance monitoring"""
    # This would clean up any resources
    pass


def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    return performance_collector.get_stats()


def record_api_metric(method: str, endpoint: str, status: int, duration: float) -> None:
    """Record API request metrics"""
    performance_collector.record_request(method, endpoint, status, duration)
