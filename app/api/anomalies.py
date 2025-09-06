#!/usr/bin/env python3
"""
Anomaly API Endpoints for Smart CloudOps AI - Refactored with Service Layer
Phase 7: Production Launch & Feedback - Backend Completion
"""

from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.services.anomaly_service import AnomalyService

# Create blueprint
anomalies_bp = Blueprint("anomalies", __name__)

# Initialize the service
anomaly_service = AnomalyService()


@anomalies_bp.route("", methods=["GET"])
@require_auth
def get_anomalies():
    """Get all anomalies with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        # Accept both `limit` and `per_page` query params (tests use `limit`)
        limit = request.args.get("limit", None, type=int)
        if limit is not None:
            per_page = min(limit, 100)
        else:
            per_page = min(request.args.get("per_page", 20, type=int), 100)
        # Validate pagination params
        if page is None or page < 1:
            return jsonify({"status": "error", "message": "Invalid page number"}), 400
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

        # Map service anomaly fields to API contract (title -> metric)
        def _map_anomaly(a: dict) -> dict:
            mapped = a.copy()
            if "title" in mapped and "metric" not in mapped:
                mapped["metric"] = mapped.get("title")
            return mapped

        anomalies_mapped = [_map_anomaly(a) for a in anomalies]

        response = {
            "status": "success",
            "data": anomalies_mapped,
            # Provide top-level total for tests that expect it
            "total": pagination_info.get("total", len(anomalies_mapped)),
            "pagination": pagination_info,
        }

        return jsonify(response), 200

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

        # Map to contract
        mapped = anomaly.copy()
        if "title" in mapped and "metric" not in mapped:
            mapped["metric"] = mapped.get("title")

        return jsonify({"status": "success", "data": mapped}), 200

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to retrieve anomaly: {str(e)}"}
            ),
            500,
        )


@anomalies_bp.route("", methods=["POST"])
@require_auth
def create_anomaly():
    """Create a new anomaly."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Accept `metric` in payload and map to service's `title` field
        if "metric" in data and "title" not in data:
            data["title"] = data.get("metric")

        # Use service layer for business logic (includes validation)
        new_anomaly = anomaly_service.create_anomaly(data)

        # Map response back to contract
        resp = new_anomaly.copy()
        if "title" in resp and "metric" not in resp:
            resp["metric"] = resp.get("title")

        return (
            jsonify(
                {
                    "status": "success",
                    "data": resp,
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
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Accept `metric` in payload and map to service's `title` if present
        if "metric" in data and "title" not in data:
            data["title"] = data.get("metric")

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

        resp = updated_anomaly.copy()
        if "title" in resp and "metric" not in resp:
            resp["metric"] = resp.get("title")

        return (
            jsonify(
                {
                    "status": "success",
                    "data": resp,
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


@anomalies_bp.route("/batch", methods=["POST"])
@require_auth
def create_anomaly_batch():
    """Create anomalies in batch."""
    try:
        payload = request.get_json(silent=True)
        if not payload or "anomalies" not in payload:
            return jsonify({"status": "error", "message": "No anomalies provided"}), 400

        anomalies_list = payload.get("anomalies")
        if not isinstance(anomalies_list, list):
            return (
                jsonify({"status": "error", "message": "Anomalies must be a list"}),
                400,
            )

        created = []
        for item in anomalies_list:
            try:
                # Map `metric` to `title` if needed
                if "metric" in item and "title" not in item:
                    item["title"] = item.get("metric")

                created_anomaly = anomaly_service.create_anomaly(item)
                # Map response back to contract
                mapped = created_anomaly.copy()
                if "title" in mapped and "metric" not in mapped:
                    mapped["metric"] = mapped.get("title")
                created.append(mapped)
            except ValueError:
                # Invalid item - skip or abort depending on policy
                return (
                    jsonify({"status": "error", "message": "Invalid anomaly in batch"}),
                    400,
                )

        return jsonify({"status": "success", "data": created}), 201
    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to create batch: {str(e)}"}
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
        data = request.get_json(silent=True) or {}
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
                    "message": f"Anomaly with ID {anomaly_id} "
                    "acknowledged successfully",
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
        data = request.get_json(silent=True) or {}
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
        # days = request.args.get("days", 7, type=int)  # TODO: Implement
        # time-based filtering
        request.args.get("source")

        # Use service layer for business logic
        stats = anomaly_service.get_anomaly_statistics()

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
