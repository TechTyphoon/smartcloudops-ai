#!/usr/bin/env python3
"""
Anomaly API Endpoints for Smart CloudOps AI
Phase 7: Production Launch & Feedback - Backend Completion
"""

from functools import wraps
from flask import Blueprint, request, jsonify
from app.auth import require_auth


# Create blueprint
anomalies_bp = Blueprint("anomalies", __name__, url_prefix="/api/anomalies")


@anomalies_bp.route("/", methods=["GET"])
@require_auth
def get_anomalies():
    """Get all anomalies with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(
            request.args.get("per_page", 20, type=int), 100
        )  # Max 100 per page
        status = request.args.get("status")
        severity = request.args.get("severity")
        source = request.args.get("source")

        with get_db_session() as session:
            # Build query
            query = session.query(Anomaly)

            # Apply filters
            if status:
                query = query.filter(Anomaly.status == status)
            if severity:
                query = query.filter(Anomaly.severity == severity)
            if source:
                query = query.filter(Anomaly.source == source)

            # Order by creation date (newest first)
            query = query.order_by(Anomaly.created_at.desc())

            # Apply pagination
            total = query.count()
            anomalies = query.offset((page - 1) * per_page).limit(per_page).all()

            # Convert to dictionaries
            anomalies_data = models_to_list(anomalies)

            return (
                jsonify(
                    {
                        "anomalies": anomalies_data,
                        "pagination": {
                            "page": page,
                            "per_page": per_page,
                            "total": total,
                            "pages": (total + per_page - 1) // per_page,
                        },
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to get anomalies: {str(e)}"}), 500


@anomalies_bp.route("/<int:anomaly_id>", methods=["GET"])
@require_auth
def get_anomaly(anomaly_id):
    """Get a specific anomaly by ID."""
    try:
        with get_db_session() as session:
            anomaly = session.query(Anomaly).filter_by(id=anomaly_id).first()

            if not anomaly:
                return jsonify({"error": "Anomaly not found"}), 404

            return jsonify({"anomaly": model_to_dict(anomaly)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get anomaly: {str(e)}"}), 500


@anomalies_bp.route("/", methods=["POST"])
@require_auth
def create_anomaly():
    """Create a new anomaly."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["title", "severity", "source", "anomaly_score", "confidence"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": "Missing required field: {field}"}), 400

        # Validate severity
        valid_severities = ["low", "medium", "high", "critical"]
        if data["severity"] not in valid_severities:
            return (
                jsonify(
                    {"error": "Invalid severity. Must be one of: {valid_severities}"}
                ),
                400,
            )

        # Validate anomaly score
        if (
            not isinstance(data["anomaly_score"], (int, float))
            or data["anomaly_score"] < 0
        ):
            return jsonify({"error": "Anomaly score must be a positive number"}), 400

        # Validate confidence
        if not isinstance(data["confidence"], (int, float)) or not (
            0 <= data["confidence"] <= 1
        ):
            return (
                jsonify({"error": "Confidence must be a number between 0 and 1"}),
                400,
            )

        with get_db_session() as session:
            # Create anomaly
            anomaly = Anomaly(
                title=data["title"],
                description=data.get("description"),
                severity=data["severity"],
                source=data["source"],
                anomaly_score=data["anomaly_score"],
                confidence=data["confidence"],
                metrics_data=data.get("metrics_data"),
                explanation=data.get("explanation"),
            )

            session.add(anomaly)

            # Log audit event
            user = get_current_user()
            auth_manager.log_audit_event(
                user_id=user.id,
                action="anomaly_created",
                resource_type="anomaly",
                resource_id=anomaly.id,
                details={"title": anomaly.title, "severity": anomaly.severity},
            )

            return (
                jsonify(
                    {
                        "message": "Anomaly created successfully",
                        "anomaly": model_to_dict(anomaly),
                    }
                ),
                201,
            )

    except Exception as e:
        return jsonify({"error": "Failed to create anomaly: {str(e)}"}), 500


@anomalies_bp.route("/<int:anomaly_id>/acknowledge", methods=["POST"])
@require_auth
def acknowledge_anomaly(anomaly_id):
    """Acknowledge an anomaly."""
    try:
        user = get_current_user()

        with get_db_session() as session:
            anomaly = session.query(Anomaly).filter_by(id=anomaly_id).first()

            if not anomaly:
                return jsonify({"error": "Anomaly not found"}), 404

            if anomaly.status != "open":
                return (
                    jsonify({"error": "Only open anomalies can be acknowledged"}),
                    400,
                )

            # Update anomaly
            anomaly.status = "acknowledged"
            anomaly.acknowledged_by = user.id
            anomaly.acknowledged_at = datetime.utcnow()

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="anomaly_acknowledged",
                resource_type="anomaly",
                resource_id=anomaly.id,
                details={"title": anomaly.title, "severity": anomaly.severity},
            )

            return (
                jsonify(
                    {
                        "message": "Anomaly acknowledged successfully",
                        "anomaly": model_to_dict(anomaly),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to acknowledge anomaly: {str(e)}"}), 500


@anomalies_bp.route("/<int:anomaly_id>/resolve", methods=["POST"])
@require_auth
def resolve_anomaly(anomaly_id):
    """Resolve an anomaly."""
    try:
        user = get_current_user()
        data = request.get_json() or {}

        with get_db_session() as session:
            anomaly = session.query(Anomaly).filter_by(id=anomaly_id).first()

            if not anomaly:
                return jsonify({"error": "Anomaly not found"}), 404

            if anomaly.status == "resolved":
                return jsonify({"error": "Anomaly is already resolved"}), 400

            # Update anomaly
            anomaly.status = "resolved"
            anomaly.resolved_by = user.id
            anomaly.resolved_at = datetime.utcnow()

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="anomaly_resolved",
                resource_type="anomaly",
                resource_id=anomaly.id,
                details={
                    "title": anomaly.title,
                    "severity": anomaly.severity,
                    "resolution_notes": data.get("resolution_notes"),
                },
            )

            return (
                jsonify(
                    {
                        "message": "Anomaly resolved successfully",
                        "anomaly": model_to_dict(anomaly),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to resolve anomaly: {str(e)}"}), 500


@anomalies_bp.route("/<int:anomaly_id>/dismiss", methods=["POST"])
@require_auth
def dismiss_anomaly(anomaly_id):
    """Dismiss an anomaly."""
    try:
        user = get_current_user()
        data = request.get_json() or {}

        with get_db_session() as session:
            anomaly = session.query(Anomaly).filter_by(id=anomaly_id).first()

            if not anomaly:
                return jsonify({"error": "Anomaly not found"}), 404

            if anomaly.status == "dismissed":
                return jsonify({"error": "Anomaly is already dismissed"}), 400

            # Update anomaly
            anomaly.status = "dismissed"
            anomaly.dismissed_by = user.id
            anomaly.dismissed_at = datetime.utcnow()

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="anomaly_dismissed",
                resource_type="anomaly",
                resource_id=anomaly.id,
                details={
                    "title": anomaly.title,
                    "severity": anomaly.severity,
                    "dismissal_reason": data.get("dismissal_reason"),
                },
            )

            return (
                jsonify(
                    {
                        "message": "Anomaly dismissed successfully",
                        "anomaly": model_to_dict(anomaly),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to dismiss anomaly: {str(e)}"}), 500


@anomalies_bp.route("/<int:anomaly_id>", methods=["PUT"])
@require_auth
def update_anomaly(anomaly_id):
    """Update an anomaly."""
    try:
        data = request.get_json()
        user = get_current_user()

        with get_db_session() as session:
            anomaly = session.query(Anomaly).filter_by(id=anomaly_id).first()

            if not anomaly:
                return jsonify({"error": "Anomaly not found"}), 404

            # Update allowed fields
            allowed_fields = ["title", "description", "explanation"]
            for field in allowed_fields:
                if field in data:
                    setattr(anomaly, field, data[field])

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="anomaly_updated",
                resource_type="anomaly",
                resource_id=anomaly.id,
                details={"title": anomaly.title},
            )

            return (
                jsonify(
                    {
                        "message": "Anomaly updated successfully",
                        "anomaly": model_to_dict(anomaly),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to update anomaly: {str(e)}"}), 500


@anomalies_bp.route("/stats", methods=["GET"])
@require_auth
def get_anomaly_stats():
    """Get anomaly statistics."""
    try:
        with get_db_session() as session:
            # Get total counts by status
            status_stats = (
                session.query(
                    Anomaly.status,
                    session.query(Anomaly)
                    .filter(Anomaly.status == Anomaly.status)
                    .count()
                    .label("count"),
                )
                .group_by(Anomaly.status)
                .all()
            )

            # Get total counts by severity
            severity_stats = (
                session.query(
                    Anomaly.severity,
                    session.query(Anomaly)
                    .filter(Anomaly.severity == Anomaly.severity)
                    .count()
                    .label("count"),
                )
                .group_by(Anomaly.severity)
                .all()
            )

            # Get recent anomalies (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_count = (
                session.query(Anomaly).filter(Anomaly.created_at >= yesterday).count()
            )

            # Get total count
            total_count = session.query(Anomaly).count()

            return (
                jsonify(
                    {
                        "stats": {
                            "total": total_count,
                            "recent_24h": recent_count,
                            "by_status": {
                                stat.status: stat.count for stat in status_stats
                            },
                            "by_severity": {
                                stat.severity: stat.count for stat in severity_stats
                            },
                        }
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to get anomaly stats: {str(e)}"}), 500


@anomalies_bp.route("/batch", methods=["POST"])
@require_auth
def create_batch_anomalies():
    """Create multiple anomalies in batch."""
    try:
        data = request.get_json()
        anomalies_data = data.get("anomalies", [])

        if not anomalies_data:
            return jsonify({"error": "No anomalies provided"}), 400

        if len(anomalies_data) > 100:  # Limit batch size
            return jsonify({"error": "Batch size cannot exceed 100 anomalies"}), 400

        created_anomalies = []
        user = get_current_user()

        with get_db_session() as session:
            for anomaly_data in anomalies_data:
                # Validate required fields
                required_fields = [
                    "title",
                    "severity",
                    "source",
                    "anomaly_score",
                    "confidence",
                ]
                for field in required_fields:
                    if field not in anomaly_data:
                        return (
                            jsonify(
                                {"error": "Missing required field: {field} in anomaly"}
                            ),
                            400,
                        )

                # Create anomaly
                anomaly = Anomaly(
                    title=anomaly_data["title"],
                    description=anomaly_data.get("description"),
                    severity=anomaly_data["severity"],
                    source=anomaly_data["source"],
                    anomaly_score=anomaly_data["anomaly_score"],
                    confidence=anomaly_data["confidence"],
                    metrics_data=anomaly_data.get("metrics_data"),
                    explanation=anomaly_data.get("explanation"),
                )

                session.add(anomaly)
                created_anomalies.append(anomaly)

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="anomalies_batch_created",
                details={"count": len(created_anomalies)},
            )

            return (
                jsonify(
                    {
                        "message": f"{len(created_anomalies)} anomalies created successfully",
                        "anomalies": models_to_list(created_anomalies),
                    }
                ),
                201,
            )

    except Exception as e:
        return jsonify({"error": "Failed to create batch anomalies: {str(e)}"}), 500
