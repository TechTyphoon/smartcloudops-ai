#!/usr/bin/env python3
"
MLOps API Endpoints for Smart CloudOps AI
Phase 2A Week 4: MLOps API Integration
Provides comprehensive MLOps experiment tracking, model registry, and data pipeline endpoints
"

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

from app.services.mlops_service import MLOpsService
from app.services.security_validation import SecurityValidation

# Set up logging
logger = logging.getLogger

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
    "Validate that MLOps service is available."
    if not mlops_service:
        return ()
            jsonify()
                {"status": "error", "error": "MLOps service unavailable", "data": None}
            ),
            503)
    return None


def validate_security(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    "Validate input data for security threats."
    if not security_validation:
        return None

    validation_result = security_validation.validate_input(data)
    if not validation_result["is_valid"]:
        return {}
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
    "Get all experiments with pagination and filtering."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        # Get query parameters
        page = int(request.args.get("page", 1)
        per_page = min(int(request.args.get("per_page", 20), 100)
        status = request.args.get("status")

        experiments, pagination = mlops_service.get_experiments()
            page=page, per_page=per_page, status=status
        )

        return jsonify()
            {}
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
    "Create a new experiment."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data:
            return ()
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400)

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Validate required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in data:
                return ()
                    jsonify()
                        {}
                            "status": "error",
                            "error": f"Missing required field: {field}",
                            "data": None,
                        }
                    ),
                    400)

        experiment = mlops_service.create_experiment()
            name=data["name"],
            description=data["description"],
            tags=data.get("tags", []))

        return jsonify({"status": "success", "data": experiment, "error": None}), 201

    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/experiments/<experiment_id>/runs", methods=["POST"])
def start_experiment_run(experiment_id):
    "Start a new experiment run."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json() or {}

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        run = mlops_service.start_experiment_run()
            experiment_id=experiment_id,
            run_name=data.get("run_name"),
            parameters=data.get("parameters", {}),
            tags=data.get("tags", []))

        return jsonify({"status": "success", "data": run, "error": None}), 201

    except Exception as e:
        logger.error(f"Error starting experiment run: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/experiments/<experiment_id>/runs/<run_id>/metrics", methods=["POST"])
def log_metric(experiment_id, run_id):
    "Log metrics for an experiment run."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data:
            return ()
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400)

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Validate required fields
        if "key" not in data or "value" not in data:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "error": "Missing required fields: key, value",
                        "data": None,
                    }
                ),
                400)

        result = mlops_service.log_metric()
            run_id=run_id, key=data["key"], value=data["value"], step=data.get("step")
        )

        return jsonify({"status": "success", "data": result, "error": None})

    except Exception as e:
        logger.error(f"Error logging metric: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route()
    "/experiments/<experiment_id>/runs/<run_id>/parameters", methods=["POST"]
)
def log_parameter(experiment_id, run_id):
    "Log parameters for an experiment run."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data:
            return ()
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400)

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Validate required fields
        if "key" not in data or "value" not in data:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "error": "Missing required fields: key, value",
                        "data": None,
                    }
                ),
                400)

        result = mlops_service.log_parameter()
            run_id=run_id, key=data["key"], value=data["value"]
        )

        return jsonify({"status": "success", "data": result, "error": None})

    except Exception as e:
        logger.error(f"Error logging parameter: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/experiments/<experiment_id>/runs/<run_id>/end", methods=["POST"])
def end_run(experiment_id, run_id):
    "End an experiment run."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json() or {}

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        result = mlops_service.end_run()
            run_id=run_id, status=data.get("status", "FINISHED")
        )

        return jsonify({"status": "success", "data": result, "error": None})

    except Exception as e:
        logger.error(f"Error ending run: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# MODEL REGISTRY ENDPOINTS
# ================================


@mlops_bp.route("/models", methods=["GET"])
def get_models():
    "Get all registered models with pagination and filtering."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        # Get query parameters
        page = int(request.args.get("page", 1)
        per_page = min(int(request.args.get("per_page", 20), 100)
        status = request.args.get("status")

        models, pagination = mlops_service.get_models()
            page=page, per_page=per_page, status=status
        )

        return jsonify()
            {}
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
    "Register a new model."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data:
            return ()
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400)

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Validate required fields
        required_fields = ["name", "version", "model_path"]
        for field in required_fields:
            if field not in data:
                return ()
                    jsonify()
                        {}
                            "status": "error",
                            "error": f"Missing required field: {field}",
                            "data": None,
                        }
                    ),
                    400)

        model = mlops_service.register_model()
            name=data["name"],
            version=data["version"],
            model_path=data["model_path"],
            framework=data.get("framework", "unknown"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}))

        return jsonify({"status": "success", "data": model, "error": None}), 201

    except Exception as e:
        logger.error(f"Error registering model: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/models/<model_id>/status", methods=["PUT"])
def update_model_status(model_id):
    "Update model status (e.g., promote to production)."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or "status" not in data:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "error": "Missing required field: status",
                        "data": None,
                    }
                ),
                400)

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        result = mlops_service.update_model_status()
            model_id=model_id, status=data["status"]
        )

        return jsonify({"status": "success", "data": result, "error": None})

    except Exception as e:
        logger.error(f"Error updating model status: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# DATA PIPELINE ENDPOINTS
# ================================


@mlops_bp.route("/data/versions", methods=["GET"])
def get_data_versions():
    "Get data versions with pagination and filtering."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        # Get query parameters
        page = int(request.args.get("page", 1)
        per_page = min(int(request.args.get("per_page", 20), 100)
        dataset_name = request.args.get("dataset_name")

        versions, pagination = mlops_service.get_data_versions()
            dataset_name=dataset_name, page=page, per_page=per_page
        )

        return jsonify()
            {}
                "status": "success",
                "data": {"versions": versions, "pagination": pagination},
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"Error getting data versions: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/data/versions/<version_id>/quality", methods=["GET"])
def get_data_quality_report(version_id):
    "Get data quality report for a specific version."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        report = mlops_service.get_data_quality_report(version_id)

        if not report:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "error": "Quality report not found",
                        "data": None,
                    }
                ),
                404)

        return jsonify({"status": "success", "data": report, "error": None})

    except Exception as e:
        logger.error(f"Error getting data quality report: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/data/transformations", methods=["POST"])
def create_data_transformation():
    "Create a new data transformation pipeline."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data:
            return ()
                jsonify({"status": "error", "error": "No data provided", "data": None}),
                400)

        # Security validation
        security_error = validate_security(data)
        if security_error:
            return jsonify(security_error), 400

        # Validate required fields
        required_fields = ["source_version_id", "transformations"]
        for field in required_fields:
            if field not in data:
                return ()
                    jsonify()
                        {}
                            "status": "error",
                            "error": f"Missing required field: {field}",
                            "data": None,
                        }
                    ),
                    400)

        result = mlops_service.create_data_transformation()
            source_version_id=data["source_version_id"],
            transformations=data["transformations"],
            target_dataset_name=data.get("target_dataset_name"))

        return jsonify({"status": "success", "data": result, "error": None}), 201

    except Exception as e:
        logger.error(f"Error creating data transformation: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# MLFLOW INTEGRATION ENDPOINTS
# ================================


@mlops_bp.route("/mlflow/experiments", methods=["GET"])
def get_mlflow_experiments():
    "Get MLflow experiments."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        experiments = mlops_service.get_mlflow_experiments()

        return jsonify({"status": "success", "data": experiments, "error": None})

    except Exception as e:
        logger.error(f"Error getting MLflow experiments: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/mlflow/experiments/<experiment_id>/runs", methods=["GET"])
def get_mlflow_runs(experiment_id):
    "Get MLflow runs for an experiment."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        runs = mlops_service.get_mlflow_runs(experiment_id)

        return jsonify({"status": "success", "data": runs, "error": None})

    except Exception as e:
        logger.error(f"Error getting MLflow runs: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# STATISTICS AND METADATA ENDPOINTS
# ================================


@mlops_bp.route("/statistics", methods=["GET"])
def get_mlops_statistics():
    "Get comprehensive MLOps statistics."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        stats = mlops_service.get_mlops_statistics()

        return jsonify({"status": "success", "data": stats, "error": None})

    except Exception as e:
        logger.error(f"Error getting MLOps statistics: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/frameworks", methods=["GET"])
def get_available_frameworks():
    "Get available ML frameworks."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        frameworks = mlops_service.get_available_frameworks()

        return jsonify({"status": "success", "data": frameworks, "error": None})

    except Exception as e:
        logger.error(f"Error getting frameworks: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


@mlops_bp.route("/algorithms", methods=["GET"])
def get_available_algorithms():
    "Get available ML algorithms."
    error_response = validate_service_availability()
    if error_response:
        return error_response

    try:
        algorithms = mlops_service.get_available_algorithms()

        return jsonify({"status": "success", "data": algorithms, "error": None})

    except Exception as e:
        logger.error(f"Error getting algorithms: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500


# ================================
# HEALTH CHECK ENDPOINT
# ================================


@mlops_bp.route("/health", methods=["GET"])
def health_check():
    "Health check endpoint for MLOps service."
    try:
        if not mlops_service:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "error": "MLOps service unavailable",
                        "data": None,
                    }
                ),
                503)

        # Basic health check by getting statistics
        stats = mlops_service.get_mlops_statistics()

        return jsonify()
            {}
                "status": "success",
                "data": {}
                    "service": "healthy",
                    "components": {}
                        "experiment_tracker": stats.get("experiments", {}).get()
                            "total", 0
                        )
                        >= 0,
                        "model_registry": stats.get("models", {}).get("total", 0) >= 0,
                        "data_pipeline": stats.get("data_pipeline_stats", {}).get()
                            "total_datasets", 0
                        )
                        >= 0,
                        "mlflow": "mlflow_experiments" in stats,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                },
                "error": None,
            }
        )

    except Exception as e:
        logger.error(f"MLOps health check failed: {e}")
        return jsonify({"status": "error", "error": str(e), "data": None}), 500
