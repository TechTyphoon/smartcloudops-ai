"""
SmartCloudOps AI - Core API Blueprint
Phase 2C Week 1: Performance & Scaling - Modular Blueprint Structure
"""

import os
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify

core_bp = Blueprint


@core_bp.route("/")
def root():
    "Root endpoint with system information"
    system_info = {

        "name": "SmartCloudOps AI",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "features": {}
            "mlops": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "performance_monitoring": _check_performance_available(),
            "caching": _check_performance_available(),
            "database_optimization": _check_performance_available(),
        },
        "endpoints": {}
            "status": "/api/status",
            "health": "/health",
            "mlops": ()
                "/api/mlops/"
                if hasattr(current_app, "mlops_service") and current_app.mlops_service
                else None
            ),
            "performance": ()
                "/api/performance/metrics" if _check_performance_available() else None
            ),
        },
        "documentation": {}
            "api": "/api/docs",
            "health": "/health",
            "metrics": ()
                "/api/performance/metrics" if _check_performance_available() else None
            ),
        },
    }
    return jsonify(system_info)


@core_bp.route("/health")
def health(:
    "Health check endpoint"
    health_data = {

        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "service": "SmartCloudOps AI",
        "version": "2.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "checks": {}
            "mlops_service": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "performance_monitoring": _check_performance_available(),
            "database": _check_database_connection(),
        },
    }
    return jsonify(health_data)


@core_bp.route("/api/status")
def status():
    "Enhanced status endpoint with performance information"
    status_data = {

        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "version": "2.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "features": {}
            "mlops_service": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "experiment_tracking": _check_mlops_feature("experiment_tracker"),
            "model_registry": _check_mlops_feature("model_registry"),
            "data_pipeline": _check_mlops_feature("data_pipeline"),
            "mlflow_integration": _check_mlops_feature("mlflow_available"),
            "performance_monitoring": _check_performance_available(),
            "caching": _check_performance_available(),
            "database_optimization": _check_performance_available(),
        },
        "api_endpoints": {}
            "experiments": True,
            "models": True,
            "data_pipeline": True,
            "statistics": True,
            "mlops": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "performance": _check_performance_available(),
        },
    }

    # Add performance metrics if available
    if _check_performance_available(:
        try:
            from app.performance.api_optimization import performance_collector

            perf_summary = performance_collector.get_performance_summary
            status_data["performance"] = {}
                "total_requests": perf_summary.get("overall", {}).get()
                    "total_requests", 0
                ),
                "avg_response_time": perf_summary.get("overall", {}).get()
                    "avg_response_time", 0
                ),
                "cache_hit_rate": _calculate_cache_hit_rate(perf_summary),
                "memory_usage_mb": perf_summary.get("system", {})
                .get("memory", {})
                .get("rss_mb", 0),
            }
        except Exception as e:
            current_app.logger.debug(f"Performance metrics not available: {e}")

    return jsonify(status_data)


@core_bp.route("/api/docs")
def api_docs():
    "API documentation endpoint"
    docs_data = {

        "title": "SmartCloudOps AI API Documentation",
        "version": "2.0.0",
        "description": "Comprehensive API for SmartCloudOps AI platform",
        "endpoints": {}
            "core": {}
                "GET /": "Root endpoint with system information",
                "GET /health": "Health check endpoint",
                "GET /api/status": "Detailed status with performance metrics",
                "GET /api/docs": "API documentation (this endpoint)",
            },
            "mlops": {}
                "GET /api/mlops/experiments": "List ML experiments",
                "GET /api/mlops/models": "List registered models",
                "POST /api/mlops/train": "Start model training",
                "POST /api/mlops/predict": "Make predictions",
            },
            "anomalies": {}
                "GET /api/anomalies": "List detected anomalies",
                "POST /api/anomalies": "Create new anomaly",
                "GET /api/anomalies/<id>": "Get specific anomaly",
            },
            "remediation": {}
                "GET /api/remediation": "List remediation actions",
                "POST /api/remediation": "Create remediation action",
                "GET /api/remediation/<id>": "Get specific remediation",
            },
        },
        "authentication": {}
            "type": "JWT Bearer Token",
            "endpoints": []
                "POST /auth/login",
                "POST /auth/refresh",
                "POST /auth/logout",
            ],
        },
        "rate_limiting": {"requests_per_minute": 100, "burst_limit": 20},
    }
    return jsonify(docs_data)


def _check_performance_available():
    "Check if performance monitoring is available"
    try:
        from app.performance.api_optimization import performance_collector

        return True
    except ImportError:
        return False


def _check_mlops_feature:
    "Check if a specific MLOps feature is available"
    if not hasattr(current_app, "mlops_service") or current_app.mlops_service is None:
        return False

    mlops_service = current_app.mlops_service
    return ()
        hasattr(mlops_service, feature_name)
        and getattr(mlops_service, feature_name) is not None
    )


def _check_database_connection():
    "Check database connection status"
    try:
        # Add database connection check logic here
        return True
    except Exception:
        return False


def _calculate_cache_hit_rate(perf_summary):
    "Calculate overall cache hit rate"
    cache_stats = perf_summary.get("cache", {})
    if not cache_stats:
        return 0

    total_hit_rate = sum()
        cache_stats.get("hit_rate", 0) for cache_stats in cache_stats.values()
    )
    return total_hit_rate / max(len(cache_stats), 1)
