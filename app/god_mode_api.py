#!/usr/bin/env python3
"""
GOD MODE: Advanced API Endpoints
Enterprise-grade APIs for ML versioning, centralized logging, real-time analytics, and advanced features
"""

import json
import logging
import time
from dataclasses import asdict
from datetime import datetime
from datetime import timedelta
from typing import Dict

from flask import Blueprint, jsonify, request
from prometheus_client import Counter, Histogram

# Import GOD MODE systems
try:
    from app.analytics.real_time_dashboard import analytics_dashboard
    from app.logging.centralized_logging import CentralizedLogger, centralized_logging
    from ml_models.model_versioning import ModelVersion, model_versioning

    GOD_MODE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"GOD MODE systems not available: {e}")
    GOD_MODE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create GOD MODE blueprint
god_mode_bp = Blueprint("god_mode", __name__, url_prefix="/god-mode")

# Prometheus metrics for GOD MODE
GOD_MODE_REQUESTS = Counter(
    "god_mode_requests_total", "Total GOD MODE API requests", ["endpoint", "method"]
)
GOD_MODE_LATENCY = Histogram(
    "god_mode_request_duration_seconds", "GOD MODE API request latency"
)

# Initialize centralized logger
if GOD_MODE_AVAILABLE:
    god_logger = CentralizedLogger("god_mode_api")
else:
    god_logger = None


@god_mode_bp.route("/status", methods=["GET"])
def god_mode_status():
    """Get GOD MODE system status"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="status", method="GET").inc()
        start_time = time.time()

        status = {
            "god_mode_enabled": GOD_MODE_AVAILABLE,
            "timestamp": datetime.now().isoformat(),
            "version": "4.0.0-god-mode",
            "features": {
                "ml_versioning": GOD_MODE_AVAILABLE,
                "centralized_logging": GOD_MODE_AVAILABLE,
                "real_time_analytics": GOD_MODE_AVAILABLE,
                "advanced_security": True,
                "predictive_analytics": True,
                "distributed_tracing": True,
            },
        }

        if GOD_MODE_AVAILABLE:
            # Add system statuses
            status["systems"] = {
                "ml_versioning": model_versioning.get_system_status(),
                "centralized_logging": centralized_logging.get_system_status(),
                "analytics_dashboard": {
                    "running": analytics_dashboard.running,
                    "active_clients": len(analytics_dashboard.clients),
                    "metrics_count": len(analytics_dashboard.metrics_history),
                },
            }

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info("GOD MODE status requested", endpoint="/god-mode/status")

        return jsonify(
            {"status": "success", "message": "GOD MODE system status", "data": status}
        )

    except Exception as e:
        logger.error(f"Error getting GOD MODE status: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get GOD MODE status",
                    "error": str(e),
                }
            ),
            500,
        )


# ML Model Versioning APIs
@god_mode_bp.route("/ml/versions", methods=["GET"])
def list_model_versions():
    """List all model versions"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="ml_versions", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "ML versioning system not available"}
                ),
                503,
            )

        model_name = request.args.get("model_name")
        if model_name:
            versions = model_versioning.get_model_history(model_name)
        else:
            # Get all versions from database
            with model_versioning.db_path.open() as conn:
                cursor = conn.execute(
                    "SELECT * FROM model_versions ORDER BY created_at DESC"
                )
                versions = []
                for row in cursor.fetchall():
                    version = ModelVersion(
                        version_id=row[0],
                        model_name=row[1],
                        model_type=row[2],
                        created_at=datetime.fromisoformat(row[3]),
                        created_by=row[4],
                        description=row[5],
                        hyperparameters=json.loads(row[6]),
                        feature_columns=json.loads(row[7]),
                        performance_metrics=json.loads(row[8]),
                        file_path=row[9],
                        file_size=row[10],
                        checksum=row[11],
                        status=row[12],
                        parent_version=row[13],
                        tags=json.loads(row[14]) if row[14] else [],
                        deployment_config=json.loads(row[15]) if row[15] else {},
                    )
                    versions.append(version)

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Model versions listed: {len(versions)} versions",
                endpoint="/god-mode/ml/versions",
            )

        return jsonify(
            {
                "status": "success",
                "message": f"Retrieved {len(versions)} model versions",
                "data": {
                    "versions": [asdict(v) for v in versions],
                    "count": len(versions),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error listing model versions: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to list model versions",
                    "error": str(e),
                }
            ),
            500,
        )


@god_mode_bp.route("/ml/versions/<version_id>", methods=["GET"])
def get_model_version(version_id: str):
    """Get specific model version details"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="ml_version_detail", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "ML versioning system not available"}
                ),
                503,
            )

        model, version = model_versioning.load_model_version(version_id)

        # Get performance trends
        trends = model_versioning.get_performance_trends(version_id, days=30)

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Model version details retrieved: {version_id}",
                endpoint="/god-mode/ml/versions/{version_id}",
            )

        return jsonify(
            {
                "status": "success",
                "message": "Model version details retrieved",
                "data": {
                    "version": asdict(version),
                    "performance_trends": [asdict(t) for t in trends],
                    "model_info": {
                        "type": type(model).__name__,
                        "available": model is not None,
                    },
                },
            }
        )

    except ValueError as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Model version not found",
                    "error": str(e),
                }
            ),
            404,
        )
    except Exception as e:
        logger.error(f"Error getting model version {version_id}: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get model version",
                    "error": str(e),
                }
            ),
            500,
        )


@god_mode_bp.route("/ml/deploy", methods=["POST"])
def deploy_model():
    """Deploy a model version"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="ml_deploy", method="POST").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "ML versioning system not available"}
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request data required"}), 400

        version_id = data.get("version_id")
        environment = data.get("environment", "production")
        traffic_percentage = data.get("traffic_percentage", 100.0)
        deployed_by = data.get("deployed_by", "api")

        if not version_id:
            return (
                jsonify({"status": "error", "message": "version_id is required"}),
                400,
            )

        deployment_id = model_versioning.deploy_model(
            version_id, environment, traffic_percentage, deployed_by
        )

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Model deployed: {version_id} to {environment}",
                endpoint="/god-mode/ml/deploy",
            )

        return jsonify(
            {
                "status": "success",
                "message": f"Model {version_id} deployed to {environment}",
                "data": {
                    "deployment_id": deployment_id,
                    "version_id": version_id,
                    "environment": environment,
                    "traffic_percentage": traffic_percentage,
                    "deployed_by": deployed_by,
                    "deployed_at": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to deploy model",
                    "error": str(e),
                }
            ),
            500,
        )


@god_mode_bp.route("/ml/rollback", methods=["POST"])
def rollback_model():
    """Rollback model deployment"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="ml_rollback", method="POST").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "ML versioning system not available"}
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request data required"}), 400

        deployment_id = data.get("deployment_id")
        rollback_version_id = data.get("rollback_version_id")
        rolled_back_by = data.get("rolled_back_by", "api")

        if not deployment_id or not rollback_version_id:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "deployment_id and rollback_version_id are required",
                    }
                ),
                400,
            )

        success = model_versioning.rollback_model(
            deployment_id, rollback_version_id, rolled_back_by
        )

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Model rolled back: {deployment_id} to {rollback_version_id}",
                endpoint="/god-mode/ml/rollback",
            )

        return jsonify(
            {
                "status": "success" if success else "error",
                "message": f"Model rolled back from {deployment_id} to {rollback_version_id}",
                "data": {
                    "deployment_id": deployment_id,
                    "rollback_version_id": rollback_version_id,
                    "rolled_back_by": rolled_back_by,
                    "success": success,
                    "rolled_back_at": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error rolling back model: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to rollback model",
                    "error": str(e),
                }
            ),
            500,
        )


# Centralized Logging APIs
@god_mode_bp.route("/logs/search", methods=["GET"])
def search_logs():
    """Search logs using advanced filters"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="logs_search", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Centralized logging system not available",
                    }
                ),
                503,
            )

        # Get search parameters
        query = request.args.get("query")
        level = request.args.get("level")
        component = request.args.get("component")
        start_time_str = request.args.get("start_time")
        end_time_str = request.args.get("end_time")
        limit = int(request.args.get("limit", 100))

        # Parse timestamps
        start_time_dt = None
        end_time_dt = None
        if start_time_str:
            start_time_dt = datetime.fromisoformat(start_time_str)
        if end_time_str:
            end_time_dt = datetime.fromisoformat(end_time_str)

        # Search logs
        results = centralized_logging.search_logs(
            query=query,
            level=level,
            component=component,
            start_time=start_time_dt,
            end_time=end_time_dt,
            limit=limit,
        )

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Logs searched: {len(results)} results",
                endpoint="/god-mode/logs/search",
            )

        return jsonify(
            {
                "status": "success",
                "message": f"Found {len(results)} log entries",
                "data": {
                    "logs": results,
                    "count": len(results),
                    "search_params": {
                        "query": query,
                        "level": level,
                        "component": component,
                        "start_time": start_time_str,
                        "end_time": end_time_str,
                        "limit": limit,
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"Error searching logs: {e}")
        return (
            jsonify(
                {"status": "error", "message": "Failed to search logs", "error": str(e)}
            ),
            500,
        )


@god_mode_bp.route("/logs/metrics", methods=["GET"])
def get_log_metrics():
    """Get logging system metrics"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="logs_metrics", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Centralized logging system not available",
                    }
                ),
                503,
            )

        metrics = centralized_logging.get_metrics()

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info("Log metrics retrieved", endpoint="/god-mode/logs/metrics")

        return jsonify(
            {
                "status": "success",
                "message": "Logging metrics retrieved",
                "data": metrics,
            }
        )

    except Exception as e:
        logger.error(f"Error getting log metrics: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get log metrics",
                    "error": str(e),
                }
            ),
            500,
        )


# Real-Time Analytics APIs
@god_mode_bp.route("/analytics/current", methods=["GET"])
def get_current_analytics():
    """Get current analytics data"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="analytics_current", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "Analytics dashboard not available"}
                ),
                503,
            )

        data = {
            "metrics": analytics_dashboard._get_current_metrics(),
            "alerts": analytics_dashboard._get_recent_alerts(),
            "insights": analytics_dashboard._get_recent_insights(),
            "system_status": analytics_dashboard._get_system_status(),
        }

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                "Current analytics retrieved", endpoint="/god-mode/analytics/current"
            )

        return jsonify(
            {
                "status": "success",
                "message": "Current analytics data retrieved",
                "data": data,
            }
        )

    except Exception as e:
        logger.error(f"Error getting current analytics: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get current analytics",
                    "error": str(e),
                }
            ),
            500,
        )


@god_mode_bp.route("/analytics/history", methods=["GET"])
def get_analytics_history():
    """Get historical analytics data"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="analytics_history", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "Analytics dashboard not available"}
                ),
                503,
            )

        # Get parameters
        hours = int(request.args.get("hours", 24))
        limit = int(request.args.get("limit", 100))

        # Get historical data from database
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with analytics_dashboard.db_path.open() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (cutoff_time.isoformat(), limit),
            )

            history = []
            for row in cursor.fetchall():
                history.append(
                    {
                        "timestamp": row[1],
                        "cpu_usage": row[2],
                        "memory_usage": row[3],
                        "disk_usage": row[4],
                        "network_io": json.loads(row[5]),
                        "active_connections": row[6],
                        "response_time_avg": row[7],
                        "error_rate": row[8],
                        "throughput": row[9],
                        "queue_depth": row[10],
                    }
                )

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Analytics history retrieved: {len(history)} data points",
                endpoint="/god-mode/analytics/history",
            )

        return jsonify(
            {
                "status": "success",
                "message": f"Retrieved {len(history)} historical data points",
                "data": {
                    "history": history,
                    "count": len(history),
                    "time_range_hours": hours,
                    "limit": limit,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting analytics history: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get analytics history",
                    "error": str(e),
                }
            ),
            500,
        )


@god_mode_bp.route("/analytics/insights", methods=["GET"])
def get_analytics_insights():
    """Get predictive insights"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="analytics_insights", method="GET").inc()
        start_time = time.time()

        if not GOD_MODE_AVAILABLE:
            return (
                jsonify(
                    {"status": "error", "message": "Analytics dashboard not available"}
                ),
                503,
            )

        insight_type = request.args.get("type", "all")
        insights = analytics_dashboard._get_insights_by_type(insight_type)

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"Analytics insights retrieved: {len(insights)} insights",
                endpoint="/god-mode/analytics/insights",
            )

        return jsonify(
            {
                "status": "success",
                "message": f"Retrieved {len(insights)} insights",
                "data": {
                    "insights": insights,
                    "count": len(insights),
                    "type": insight_type,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting analytics insights: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get analytics insights",
                    "error": str(e),
                }
            ),
            500,
        )


# Advanced System APIs
@god_mode_bp.route("/system/health", methods=["GET"])
def get_system_health():
    """Get comprehensive system health status"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="system_health", method="GET").inc()
        start_time = time.time()

        import psutil

        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()

        # GOD MODE systems health
        god_mode_health = {
            "ml_versioning": {
                "status": "healthy" if GOD_MODE_AVAILABLE else "unavailable",
                "available": GOD_MODE_AVAILABLE,
            },
            "centralized_logging": {
                "status": "healthy" if GOD_MODE_AVAILABLE else "unavailable",
                "available": GOD_MODE_AVAILABLE,
            },
            "analytics_dashboard": {
                "status": "healthy" if GOD_MODE_AVAILABLE else "unavailable",
                "available": GOD_MODE_AVAILABLE,
                "running": analytics_dashboard.running if GOD_MODE_AVAILABLE else False,
            },
        }

        # Overall health assessment
        health_score = 100
        issues = []

        if cpu_usage > 90:
            health_score -= 20
            issues.append("Critical CPU usage")
        elif cpu_usage > 80:
            health_score -= 10
            issues.append("High CPU usage")

        if memory.percent > 95:
            health_score -= 20
            issues.append("Critical memory usage")
        elif memory.percent > 85:
            health_score -= 10
            issues.append("High memory usage")

        if disk.percent > 95:
            health_score -= 15
            issues.append("Critical disk usage")
        elif disk.percent > 85:
            health_score -= 5
            issues.append("High disk usage")

        if not GOD_MODE_AVAILABLE:
            health_score -= 30
            issues.append("GOD MODE systems unavailable")

        health_status = (
            "critical"
            if health_score < 50
            else "warning" if health_score < 80 else "healthy"
        )

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                f"System health checked: {health_status} ({health_score}/100)",
                endpoint="/god-mode/system/health",
            )

        return jsonify(
            {
                "status": "success",
                "message": "System health status retrieved",
                "data": {
                    "health_score": health_score,
                    "health_status": health_status,
                    "issues": issues,
                    "timestamp": datetime.now().isoformat(),
                    "system_metrics": {
                        "cpu_usage": cpu_usage,
                        "memory_usage": memory.percent,
                        "memory_available": memory.available,
                        "disk_usage": disk.percent,
                        "disk_free": disk.free,
                        "network_bytes_sent": network.bytes_sent,
                        "network_bytes_recv": network.bytes_recv,
                    },
                    "god_mode_systems": god_mode_health,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get system health",
                    "error": str(e),
                }
            ),
            500,
        )


@god_mode_bp.route("/system/performance", methods=["GET"])
def get_system_performance():
    """Get detailed system performance metrics"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="system_performance", method="GET").inc()
        start_time = time.time()

        import psutil

        # Detailed performance metrics
        cpu_times = psutil.cpu_times_percent()
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        # Process information
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by CPU usage
        processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
        top_processes = processes[:10]

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                "System performance metrics retrieved",
                endpoint="/god-mode/system/performance",
            )

        return jsonify(
            {
                "status": "success",
                "message": "System performance metrics retrieved",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "cpu": {
                        "usage_percent": psutil.cpu_percent(interval=1),
                        "times_percent": cpu_times._asdict(),
                        "count": psutil.cpu_count(),
                        "freq": (
                            psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                        ),
                    },
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "used": memory.used,
                        "free": memory.free,
                        "percent": memory.percent,
                    },
                    "disk": {
                        "io_counters": disk_io._asdict() if disk_io else None,
                        "partitions": [
                            {
                                "device": part.device,
                                "mountpoint": part.mountpoint,
                                "fstype": part.fstype,
                                "usage": psutil.disk_usage(part.mountpoint)._asdict(),
                            }
                            for part in psutil.disk_partitions()
                        ],
                    },
                    "network": {
                        "io_counters": network_io._asdict(),
                        "connections": len(psutil.net_connections()),
                    },
                    "top_processes": top_processes,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting system performance: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get system performance",
                    "error": str(e),
                }
            ),
            500,
        )


# GOD MODE Dashboard endpoint
@god_mode_bp.route("/dashboard", methods=["GET"])
def god_mode_dashboard():
    """Get GOD MODE dashboard data"""
    try:
        GOD_MODE_REQUESTS.labels(endpoint="dashboard", method="GET").inc()
        start_time = time.time()

        # Collect all GOD MODE data
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "god_mode_enabled": GOD_MODE_AVAILABLE,
            "version": "4.0.0-god-mode",
        }

        if GOD_MODE_AVAILABLE:
            # ML Versioning data
            ml_status = model_versioning.get_system_status()

            # Logging data
            log_metrics = centralized_logging.get_metrics()

            # Analytics data
            analytics_status = analytics_dashboard._get_system_status()
            current_metrics = analytics_dashboard._get_current_metrics()
            recent_alerts = analytics_dashboard._get_recent_alerts()
            recent_insights = analytics_dashboard._get_recent_insights()

            dashboard_data.update(
                {
                    "ml_versioning": ml_status,
                    "centralized_logging": log_metrics,
                    "analytics": {
                        "status": analytics_status,
                        "current_metrics": current_metrics,
                        "recent_alerts": recent_alerts,
                        "recent_insights": recent_insights,
                    },
                }
            )

        GOD_MODE_LATENCY.observe(time.time() - start_time)

        if god_logger:
            god_logger.info(
                "GOD MODE dashboard data retrieved", endpoint="/god-mode/dashboard"
            )

        return jsonify(
            {
                "status": "success",
                "message": "GOD MODE dashboard data retrieved",
                "data": dashboard_data,
            }
        )

    except Exception as e:
        logger.error(f"Error getting GOD MODE dashboard: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to get GOD MODE dashboard",
                    "error": str(e),
                }
            ),
            500,
        )


# Register the blueprint
def init_god_mode_api(app):
    """Initialize GOD MODE API with Flask app"""
    if GOD_MODE_AVAILABLE:
        app.register_blueprint(god_mode_bp)
        logger.info("✅ GOD MODE API blueprint registered successfully")
    else:
        logger.warning("⚠️ GOD MODE API not available - skipping blueprint registration")
