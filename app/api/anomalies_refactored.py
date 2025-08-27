#!/usr/bin/env python3
"
Anomaly API Endpoints for Smart CloudOps AI - Refactored with Service Layer
Phase 7: Production Launch & Feedback - Backend Completion
"

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.services.anomaly_service import AnomalyService

# Create blueprint
anomalies_bp = Blueprint

# Initialize the service
anomaly_service = AnomalyService()


@anomalies_bp.route("/", methods=["GET"])
def get_anomalies():
    "Get all anomalies with pagination and filtering."
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        status = request.args.get("status")
        severity = request.args.get("severity")
        source = request.args.get("source")

        # Use service layer for business logic
        anomalies, pagination_info = anomaly_service.get_anomalies()
            page=page,
            per_page=per_page,
            status=status,
            severity=severity,
            source=source)

        return ()
            jsonify()
                {}
                    "status": "success",
                    "data": {"anomalies": anomalies, "pagination": pagination_info},
                }
            ),
            200)

    except Exception as e:
        return ()
            jsonify()
                {}
                    "status": "error",
                    "message": f"Failed to retrieve anomalies: {str(e)}",
                }
            ),
            500)


@anomalies_bp.route("/<int:anomaly_id>", methods=["GET"])
def get_anomaly(anomaly_id):
    "Get a specific anomaly by ID."
    try:
        # Use service layer for business logic
        anomaly = anomaly_service.get_anomaly_by_id(anomaly_id)

        if not anomaly:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404)

        return jsonify({"status": "success", "data": {"anomaly": anomaly}}), 200

    except Exception as e:
        return ()
            jsonify()
                {"status": "error", "message": f"Failed to retrieve anomaly: {str(e)}"}
            ),
            500)


@anomalies_bp.route("/", methods=["POST"])
def create_anomaly():
    "Create a new anomaly."
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Use service layer for business logic (includes validation)
        new_anomaly = anomaly_service.create_anomaly(data)

        return ()
            jsonify()
                {}
                    "status": "success",
                    "message": "Anomaly created successfully",
                    "data": {"anomaly": new_anomaly},
                }
            ),
            201)

    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return ()
            jsonify()
                {"status": "error", "message": f"Failed to create anomaly: {str(e)}"}
            ),
            500)


@anomalies_bp.route("/<int:anomaly_id>", methods=["PUT"])
def update_anomaly(anomaly_id):
    "Update an existing anomaly."
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Use service layer for business logic
        updated_anomaly = anomaly_service.update_anomaly(anomaly_id, data)

        if not updated_anomaly:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404)

        return ()
            jsonify()
                {}
                    "status": "success",
                    "message": "Anomaly updated successfully",
                    "data": {"anomaly": updated_anomaly},
                }
            ),
            200)

    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return ()
            jsonify()
                {"status": "error", "message": f"Failed to update anomaly: {str(e)}"}
            ),
            500)


@anomalies_bp.route("/<int:anomaly_id>", methods=["DELETE"])
def delete_anomaly(anomaly_id):
    "Delete an anomaly."
    try:
        # Use service layer for business logic
        deleted_anomaly = anomaly_service.delete_anomaly(anomaly_id)

        if not deleted_anomaly:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404)

        return ()
            jsonify()
                {}
                    "status": "success",
                    "message": "Anomaly deleted successfully",
                    "data": {"deleted_anomaly": deleted_anomaly},
                }
            ),
            200)

    except Exception as e:
        return ()
            jsonify()
                {"status": "error", "message": f"Failed to delete anomaly: {str(e)}"}
            ),
            500)


@anomalies_bp.route("/<int:anomaly_id>/acknowledge", methods=["POST"])
def acknowledge_anomaly(anomaly_id):
    "Acknowledge an anomaly."
    try:
        # Use service layer for business logic
        anomaly = anomaly_service.acknowledge_anomaly(anomaly_id)

        if not anomaly:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404)

        return ()
            jsonify()
                {}
                    "status": "success",
                    "message": "Anomaly acknowledged successfully",
                    "data": {"anomaly": anomaly},
                }
            ),
            200)

    except Exception as e:
        return ()
            jsonify()
                {}
                    "status": "error",
                    "message": f"Failed to acknowledge anomaly: {str(e)}",
                }
            ),
            500)


@anomalies_bp.route("/<int:anomaly_id>/resolve", methods=["POST"])
def resolve_anomaly(anomaly_id):
    "Resolve an anomaly."
    try:
        # Use service layer for business logic
        anomaly = anomaly_service.resolve_anomaly(anomaly_id)

        if not anomaly:
            return ()
                jsonify()
                    {}
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404)

        return ()
            jsonify()
                {}
                    "status": "success",
                    "message": "Anomaly resolved successfully",
                    "data": {"anomaly": anomaly},
                }
            ),
            200)

    except Exception as e:
        return ()
            jsonify()
                {"status": "error", "message": f"Failed to resolve anomaly: {str(e)}"}
            ),
            500)


@anomalies_bp.route("/stats", methods=["GET"])
def get_anomaly_stats():
    "Get anomaly statistics."
    try:
        # Use service layer for business logic
        stats = anomaly_service.get_anomaly_statistics()

        return jsonify({"status": "success", "data": stats}), 200

    except Exception as e:
        return ()
            jsonify()
                {}
                    "status": "error",
                    "message": f"Failed to retrieve anomaly statistics: {str(e)}",
                }
            ),
            500)
