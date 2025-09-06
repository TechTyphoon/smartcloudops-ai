#!/usr/bin/env python3
"""
Anomaly API Endpoints for Smart CloudOps AI - Refactored with Service Layer
Phase 7: Production Launch & Feedback - Backend Completion
"""


from flask import Blueprint, jsonify, request

from app.services.anomaly_service import AnomalyService

# Create blueprint
anomalies_bp = Blueprint("anomalies", __name__)

# Initialize the service
anomaly_service = AnomalyService()


@anomalies_bp.route("/", methods=["GET"])
def get_anomalies():
    """Get all anomalies with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        status = request.args.get("status")
        severity = request.args.get("severity")
        source = request.args.get("source")

        # Use service layer for business logic
        anomalies, pagination_info = anomaly_service.get_anomalies(
            page=page,
            per_page=per_page,
            status=status,
            severity=severity,
            source=source,
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"anomalies": anomalies, "pagination": pagination_info},
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to retrieve anomalies: {str(e)}",
                }
            ),
            500,
        )


@anomalies_bp.route("/<int:anomaly_id>", methods=["GET"])
def get_anomaly(anomaly_id):
    """Get a specific anomaly by ID."""
    try:
        # Use service layer for business logic
        anomaly = anomaly_service.get_anomaly_by_id(anomaly_id)

        if not anomaly:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404,
            )

        return jsonify({"status": "success", "data": {"anomaly": anomaly}}), 200

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to retrieve anomaly: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("/", methods=["POST"])
def create_anomaly():
    """Create a new anomaly."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Use service layer for business logic (includes validation)
        new_anomaly = anomaly_service.create_anomaly(data)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"anomaly": new_anomaly},
                    "message": "Anomaly created successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to create anomaly: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("/<int:anomaly_id>", methods=["PUT"])
def update_anomaly(anomaly_id):
    """Update an existing anomaly."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Use service layer for business logic
        updated_anomaly = anomaly_service.update_anomaly(anomaly_id, data)

        if not updated_anomaly:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"anomaly": updated_anomaly},
                    "message": "Anomaly updated successfully",
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to update anomaly: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("/<int:anomaly_id>", methods=["DELETE"])
def delete_anomaly(anomaly_id):
    """Delete an anomaly."""
    try:
        # Use service layer for business logic
        success = anomaly_service.delete_anomaly(anomaly_id)

        if not success:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Anomaly with ID {anomaly_id} deleted successfully",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to delete anomaly: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("/<int:anomaly_id>/acknowledge", methods=["POST"])
def acknowledge_anomaly(anomaly_id):
    """Acknowledge an anomaly."""
    try:
        data = request.get_json() or {}
        acknowledged_by = data.get("acknowledged_by", "system")

        # Use service layer for business logic
        success = anomaly_service.acknowledge_anomaly(anomaly_id, acknowledged_by)

        if not success:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Anomaly with ID {anomaly_id} acknowledged "
                    "successfully",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to acknowledge anomaly: {str(e)}",
                }
            ),
            500,
        )


@anomalies_bp.route("/<int:anomaly_id>/resolve", methods=["POST"])
def resolve_anomaly(anomaly_id):
    """Resolve an anomaly."""
    try:
        data = request.get_json() or {}
        resolution_notes = data.get("resolution_notes", "")

        # Use service layer for business logic
        success = anomaly_service.resolve_anomaly(anomaly_id, resolution_notes)

        if not success:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Anomaly with ID {anomaly_id} not found",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Anomaly with ID {anomaly_id} resolved successfully",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to resolve anomaly: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("/stats", methods=["GET"])
def get_anomaly_stats():
    """Get anomaly statistics."""
    try:
        # Get query parameters for time range
        days = request.args.get("days", 7, type=int)
        source = request.args.get("source")

        # Use service layer for business logic
        stats = anomaly_service.get_anomaly_stats(days=days, source=source)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"stats": stats},
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to get anomaly stats: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("/export", methods=["GET"])
def export_anomalies():
    """Export anomalies to CSV."""
    try:
        # Get query parameters
        format_type = request.args.get("format", "csv")
        days = request.args.get("days", 30, type=int)
        status = request.args.get("status")

        # Use service layer for business logic
        export_data = anomaly_service.export_anomalies(
            format_type=format_type, days=days, status=status
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"export": export_data},
                    "message": f"Anomalies exported successfully in "
                    f"{format_type} format",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to export anomalies: {str(e)}"}
            ),
            500,
        )
