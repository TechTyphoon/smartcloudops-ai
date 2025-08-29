#!/usr/bin/env python3
"""
MLOps API Endpoints for Smart CloudOps AI
Phase 2A Week 4: MLOps API Integration
Provides comprehensive MLOps experiment tracking, model registry, and data pipeline endpoints
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

from app.services.mlops_service import MLOpsService
from app.services.security_validation import SecurityValidation

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
mlops_bp = Blueprint("mlops", __name__, url_prefix="/api/mlops")

# Initialize services
try:
    mlops_service = MLOpsService()
    security_validation = SecurityValidation()
    logger.info("MLOps services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MLOps services: {e}")
    mlops_service = None
    security_validation = None


def validate_service_availability():
    """Validate that MLOps service is available."""
    if not mlops_service:
        return (
            jsonify(
                {"status": "error", "error": "MLOps service unavailable", "data": None}
            ),
            503,
        )
    return None


def validate_security(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate input data for security threats."""
    if not security_validation:
        return None

    validation_result = security_validation.validate_input(data)
    if not validation_result["is_valid"]:
        return {
            "status": "error",
            "error": f"Security validation failed: {validation_result['issues']}",
            "data": None,
        }
    return None


# ================================
# EXPERIMENT TRACKING ENDPOINTS
# ================================


@mlops_bp.route("/experiments", methods=["GET"])
def get_experiments():
    """Get all experiments with pagination and filtering."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        status = request.args.get("status")

        experiments, pagination = mlops_service.get_experiments(
            page=page, per_page=per_page, status=status
        )

        return jsonify(
            {
                "status": "success",
                "data": {"experiments": experiments, "pagination": pagination},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting experiments: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/experiments", methods=["POST"])
def create_experiment():
    """Create a new experiment."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400,
            )

        # Validate security
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Create experiment
        experiment = mlops_service.create_experiment(data)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"experiment": experiment},
                    "error": None,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/experiments/<experiment_id>", methods=["GET"])
def get_experiment(experiment_id):
    """Get a specific experiment by ID."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        experiment = mlops_service.get_experiment(experiment_id)

        if not experiment:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Experiment with ID {experiment_id} not found",
                        "data": None,
                    }
                ),
                404,
            )

        return jsonify(
            {
                "status": "success",
                "data": {"experiment": experiment},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting experiment: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/experiments/<experiment_id>", methods=["PUT"])
def update_experiment(experiment_id):
    """Update an experiment."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400,
            )

        # Validate security
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Update experiment
        experiment = mlops_service.update_experiment(experiment_id, data)

        if not experiment:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Experiment with ID {experiment_id} not found",
                        "data": None,
                    }
                ),
                404,
            )

        return jsonify(
            {
                "status": "success",
                "data": {"experiment": experiment},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error updating experiment: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# MODEL REGISTRY ENDPOINTS
# ================================


@mlops_bp.route("/models", methods=["GET"])
def get_models():
    """Get all models with pagination and filtering."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        status = request.args.get("status")

        models, pagination = mlops_service.get_models(
            page=page, per_page=per_page, status=status
        )

        return jsonify(
            {
                "status": "success",
                "data": {"models": models, "pagination": pagination},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/models", methods=["POST"])
def register_model():
    """Register a new model."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400,
            )

        # Validate security
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Register model
        model = mlops_service.register_model(data)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"model": model},
                    "error": None,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error registering model: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/models/<model_id>", methods=["GET"])
def get_model(model_id):
    """Get a specific model by ID."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        model = mlops_service.get_model(model_id)

        if not model:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Model with ID {model_id} not found",
                        "data": None,
                    }
                ),
                404,
            )

        return jsonify(
            {
                "status": "success",
                "data": {"model": model},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting model: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/models/<model_id>/deploy", methods=["POST"])
def deploy_model(model_id):
    """Deploy a model."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json() or {}

        # Deploy model
        deployment = mlops_service.deploy_model(model_id, data)

        if not deployment:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Model with ID {model_id} not found",
                        "data": None,
                    }
                ),
                404,
            )

        return jsonify(
            {
                "status": "success",
                "data": {"deployment": deployment},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# DATA PIPELINE ENDPOINTS
# ================================


@mlops_bp.route("/data-pipeline", methods=["GET"])
def get_data_pipelines():
    """Get all data pipelines."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        pipelines = mlops_service.get_data_pipelines()

        return jsonify(
            {
                "status": "success",
                "data": {"pipelines": pipelines},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting data pipelines: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/data-pipeline", methods=["POST"])
def create_data_pipeline():
    """Create a new data pipeline."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400,
            )

        # Validate security
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Create pipeline
        pipeline = mlops_service.create_data_pipeline(data)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"pipeline": pipeline},
                    "error": None,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating data pipeline: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/data-pipeline/<pipeline_id>/run", methods=["POST"])
def run_data_pipeline(pipeline_id):
    """Run a data pipeline."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json() or {}

        # Run pipeline
        result = mlops_service.run_data_pipeline(pipeline_id, data)

        if not result:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": f"Pipeline with ID {pipeline_id} not found",
                        "data": None,
                    }
                ),
                404,
            )

        return jsonify(
            {
                "status": "success",
                "data": {"result": result},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error running data pipeline: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# STATISTICS ENDPOINTS
# ================================


@mlops_bp.route("/stats", methods=["GET"])
def get_mlops_stats():
    """Get MLOps statistics."""
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        stats = mlops_service.get_statistics()

        return jsonify(
            {
                "status": "success",
                "data": {"stats": stats},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting MLOps stats: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/health", methods=["GET"])
def mlops_health():
    """Health check for MLOps service."""
    try:
        health_status = {
            "status": "healthy" if mlops_service else "unhealthy",
            "service": "mlops",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "components": {
                "mlops_service": mlops_service is not None,
                "security_validation": security_validation is not None,
            },
        }

        return jsonify(health_status), 200 if mlops_service else 503

    except Exception as e:
        logger.error(f"Error checking MLOps health: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "service": "mlops",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                }
            ),
            500,
        )
