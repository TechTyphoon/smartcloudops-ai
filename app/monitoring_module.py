#!/usr/bin/env python3
from datetime import datetime, timezone

"""
Monitoring Module for Smart CloudOps AI
Extracted from main.py for modularity
"""

import logging
import os

import psutil
from flask import Blueprint, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/monitoring")

# Prometheus metrics - Using unique names to avoid conflicts
REQUEST_COUNT = Counter(
    "monitoring_http_requests_total",
    "Total HTTP requests (monitoring)",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "monitoring_http_request_duration_seconds", "HTTP request latency (monitoring)"
)

# Database-specific metrics for tests
DATABASE_CONNECTED = Counter(
    "smartcloudops_database_connected",
    "Database connection status (1=connected, 0=disconnected)",
)
TRAINING_RECORDS = Counter(
    "smartcloudops_training_records", "Number of training records in database"
)
SECURITY_ISSUES = Counter(
    "smartcloudops_security_issues", "Number of security issues detected"
)

# Standard system metrics
CPU_USAGE = Histogram("smartcloudops_cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Histogram(
    "smartcloudops_memory_usage_percent", "Memory usage percentage"
)

# System metrics
SYSTEM_METRICS = {
    "cpu_percent": 0.0,
    "memory_percent": 0.0,
    "disk_percent": 0.0,
    "last_updated": None,
}


def update_system_metrics():
    """Update system metrics."""
    try:
        SYSTEM_METRICS["cpu_percent"] = psutil.cpu_percent(interval=1)
        SYSTEM_METRICS["memory_percent"] = psutil.virtual_memory().percent
        SYSTEM_METRICS["disk_percent"] = psutil.disk_usage("/").percent
        SYSTEM_METRICS["last_updated"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")


@monitoring_bp.route("/metrics", methods=["GET"])
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    try:
        # Update database-specific metrics
        try:
            from app.database import get_db_session
            from app.models import SystemMetrics

            # Check database connection
            db_connected = False
            try:
                with get_db_session() as session:
                    session.execute("SELECT 1")
                    db_connected = True
                    # Count training records (mock for now)
                    training_count = session.query(SystemMetrics).count()
                    TRAINING_RECORDS._value.set(training_count)
            except Exception:
                db_connected = False

            # Set database connection status
            DATABASE_CONNECTED._value.set(1 if db_connected else 0)

            # Mock security issues count
            SECURITY_ISSUES._value.set(0)

        except Exception as e:
            logger.warning(f"Database metrics update failed: {e}")
            DATABASE_CONNECTED._value.set(0)

        # Update system metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            CPU_USAGE.observe(cpu_percent)
            MEMORY_USAGE.observe(memory_percent)
        except Exception as e:
            logger.warning(f"System metrics update failed: {e}")

        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return jsonify({"error": "Metrics generation failed"}), 500


@monitoring_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        # Update system metrics
        update_system_metrics()

        # Check critical services
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": {
                "app": "healthy",
                "database": "unknown",  # Will be checked if DB connection available
                "ml_service": "unknown",  # Will be checked if ML available
            },
            "system": {
                "cpu_percent": SYSTEM_METRICS["cpu_percent"],
                "memory_percent": SYSTEM_METRICS["memory_percent"],
                "disk_percent": SYSTEM_METRICS["disk_percent"],
            },
        }

        # Check database connection if available
        try:
            import psycopg2

            # Get database configuration from environment
            db_host = os.getenv("POSTGRES_HOST", "localhost")
            db_port = os.getenv("POSTGRES_PORT", "5434")
            db_name = os.getenv("POSTGRES_DB", "cloudops")
            db_user = os.getenv("POSTGRES_USER", "cloudops")
            db_password = os.getenv("POSTGRES_PASSWORD", "cloudops")

            # Test direct connection
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
            )
            conn.close()
            health_status["services"]["database"] = "healthy"
        except Exception as db_error:
            logger.warning(f"Database connection failed: {db_error}")
            health_status["services"]["database"] = "unhealthy"

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return (
            jsonify(
                {
                    "error": "Health check failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            503,
        )


@monitoring_bp.route("/status", methods=["GET"])
def system_status():
    "System status endpoint."
    try:
        # Update system metrics
        update_system_metrics()

        status = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {
                "cpu_percent": SYSTEM_METRICS["cpu_percent"],
                "memory_percent": SYSTEM_METRICS["memory_percent"],
                "disk_percent": SYSTEM_METRICS["disk_percent"],
                "last_updated": SYSTEM_METRICS["last_updated"],
            },
            "application": {
                "name": "Smart CloudOps AI",
                "version": "1.0.0",
                "environment": os.getenv("FLASK_ENV", "development"),
                "port": os.getenv("FLASK_PORT", "3003"),
            },
            "endpoints": {
                "health": "/monitoring/health",
                "metrics": "/monitoring/metrics",
                "status": "/monitoring/status",
            },
        }

        return jsonify(status)

    except Exception as e:
        logger.error(f"System status error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@monitoring_bp.route("/logs", methods=["GET"])
def get_logs():
    "Get application logs endpoint."
    try:
        # This is a simplified log retrieval
        # In production, you'd want to integrate with a proper logging system
        log_file = os.getenv("LOG_FILE", "logs/app.log")

        if not os.path.exists(log_file):
            return jsonify(
                {"status": "success", "message": "No log file found", "logs": []}
            )

        # Read last 100 lines
        with open(log_file, "r") as f:
            lines = f.readlines()
            recent_logs = lines[-100:] if len(lines) > 100 else lines

        return jsonify(
            {
                "status": "success",
                "log_file": log_file,
                "total_lines": len(lines),
                "recent_lines": len(recent_logs),
                "logs": recent_logs,
            }
        )

    except Exception as e:
        logger.error(f"Log retrieval error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@monitoring_bp.route("/alerts", methods=["GET", "POST"])
def alerts():
    "Alerts endpoint."
    if request.method == "GET":
        return jsonify(
            {
                "status": "success",
                "message": "Alerts endpoint",
                "endpoints": {
                    "get_alerts": "GET /monitoring/alerts",
                    "create_alert": "POST /monitoring/alerts",
                },
            }
        )
    else:
        # POST - Create new alert
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            # In a real implementation, you'd save this to a database
            alert = {
                "id": f"alert_{datetime.now().timestamp()}",
                "severity": data.get("severity", "info"),
                "message": data.get("message", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": data.get("source", "manual"),
            }

            logger.info(f"Alert created: {alert['id']} - {alert['message']}")

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Alert created successfully",
                        "alert": alert,
                    }
                ),
                201,
            )

        except Exception as e:
            logger.error(f"Alert creation error: {e}")
            return jsonify({"error": "Failed to create alert"}), 500
