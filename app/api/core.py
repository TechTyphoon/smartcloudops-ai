#!/usr/bin/env python3
"""
SmartCloudOps AI - Core API Blueprint
Phase 2C Week 1: Performance & Scaling - Modular Blueprint Structure
"""

import os
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def root():
    """Root endpoint with system information"""
    system_info = {
        "name": "SmartCloudOps AI",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "features": {
            "mlops": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "performance_monitoring": _check_performance_available(),
            "caching": _check_performance_available(),
            "database_optimization": _check_performance_available(),
        },
        "endpoints": {
            "status": "/api/status",
            "health": "/health",
            "mlops": (
                "/api/mlops/"
                if hasattr(current_app, "mlops_service") and current_app.mlops_service
                else None
            ),
            "performance": (
                "/api/performance/metrics" if _check_performance_available() else None
            ),
        },
        "documentation": {
            "api": "/api/docs",
            "health": "/health",
            "metrics": (
                "/api/performance/metrics" if _check_performance_available() else None
            ),
        },
    }
    return jsonify(system_info)


@core_bp.route("/health")
def health():
    """Health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "service": "SmartCloudOps AI",
        "version": "2.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "checks": {
            "mlops_service": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "performance_monitoring": _check_performance_available(),
            "database": _check_database_connection(),
        },
    }
    return jsonify(health_data)


@core_bp.route("/api/status")
def status():
    """Enhanced status endpoint with performance information"""
    status_data = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "version": "2.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "features": {
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
        "api_endpoints": {
            "experiments": True,
            "models": True,
            "data_pipeline": True,
            "statistics": True,
            "mlops": hasattr(current_app, "mlops_service")
            and current_app.mlops_service is not None,
            "performance": _check_performance_available(),
        },
    }
    return jsonify(status_data)


@core_bp.route("/api/info")
def info():
    """Detailed system information endpoint"""
    info_data = {
        "name": "SmartCloudOps AI",
        "version": "2.0.0",
        "description": "AI-powered Cloud Operations platform with MLOps capabilities",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "environment": os.getenv("FLASK_ENV", "development"),
        "features": {
            "mlops": {
                "available": hasattr(current_app, "mlops_service")
                and current_app.mlops_service is not None,
                "experiment_tracking": _check_mlops_feature("experiment_tracker"),
                "model_registry": _check_mlops_feature("model_registry"),
                "data_pipeline": _check_mlops_feature("data_pipeline"),
                "mlflow_integration": _check_mlops_feature("mlflow_available"),
            },
            "performance": {
                "monitoring": _check_performance_available(),
                "caching": _check_performance_available(),
                "database_optimization": _check_performance_available(),
            },
            "security": {
                "authentication": True,
                "authorization": True,
                "input_validation": True,
            },
        },
        "endpoints": {
            "core": {
                "root": "/",
                "health": "/health",
                "status": "/api/status",
                "info": "/api/info",
            },
            "mlops": {
                "base": "/api/mlops/",
                "experiments": "/api/mlops/experiments",
                "models": "/api/mlops/models",
                "data_pipeline": "/api/mlops/data-pipeline",
            },
            "performance": {
                "metrics": "/api/performance/metrics",
                "optimization": "/api/performance/optimization",
            },
        },
    }
    return jsonify(info_data)


def _check_performance_available():
    """Check if performance monitoring is available"""
    try:
        # Check if performance modules are available
        from app.performance import api_optimization, caching, database_optimization

        return True
    except ImportError:
        return False


def _check_database_connection():
    """Check database connection status"""
    try:
        from app.database import get_db_session

        with get_db_session() as session:
            session.execute("SELECT 1")
        return True
    except Exception:
        return False


def _check_mlops_feature(feature_name):
    """Check if specific MLOps feature is available"""
    if not hasattr(current_app, "mlops_service") or current_app.mlops_service is None:
        return False

    try:
        mlops_service = current_app.mlops_service

        if feature_name == "experiment_tracker":
            return hasattr(mlops_service, "experiment_tracker")
        elif feature_name == "model_registry":
            return hasattr(mlops_service, "model_registry")
        elif feature_name == "data_pipeline":
            return hasattr(mlops_service, "data_pipeline")
        elif feature_name == "mlflow_available":
            return hasattr(mlops_service, "mlflow_client")
        else:
            return False
    except Exception:
        return False
