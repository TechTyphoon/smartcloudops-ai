#!/usr/bin/env python3
"""
Remediation Actions API Endpoints for Smart CloudOps AI
Phase 7: Production Launch & Feedback - Backend Completion
"""

from flask import Blueprint, request, jsonify
from app.auth import require_auth


# Create blueprint
remediation_bp = Blueprint("remediation", __name__, url_prefix="/api/remediation")

# Initialize remediation engine (with fallback for missing component)
try:
    from app.remediation.engine import RemediationEngine
    remediation_engine = RemediationEngine()
except ImportError:
    remediation_engine = None


@remediation_bp.route("/actions", methods=["GET"])
@require_auth
def get_remediation_actions():
    """Get all remediation actions with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(
            request.args.get("per_page", 20, type=int), 100
        )  # Max 100 per page
        status = request.args.get("status")
        action_type = request.args.get("action_type")
        priority = request.args.get("priority")
        anomaly_id = request.args.get("anomaly_id", type=int)

        with get_db_session() as session:
            # Build query
            query = session.query(RemediationAction)

            # Apply filters
            if status:
                query = query.filter(RemediationAction.status == status)
            if action_type:
                query = query.filter(RemediationAction.action_type == action_type)
            if priority:
                query = query.filter(RemediationAction.priority == priority)
            if anomaly_id:
                query = query.filter(RemediationAction.anomaly_id == anomaly_id)

            # Order by creation date (newest first)
            query = query.order_by(RemediationAction.created_at.desc())

            # Apply pagination
            total = query.count()
            actions = query.offset((page - 1) * per_page).limit(per_page).all()

            # Convert to dictionaries
            actions_data = models_to_list(actions)

            return (
                jsonify(
                    {
                        "actions": actions_data,
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
        return jsonify({"error": "Failed to get remediation actions: {str(e)}"}), 500


@remediation_bp.route("/actions/<int:action_id>", methods=["GET"])
@require_auth
def get_remediation_action(action_id):
    """Get a specific remediation action by ID."""
    try:
        with get_db_session() as session:
            action = session.query(RemediationAction).filter_by(id=action_id).first()

            if not action:
                return jsonify({"error": "Remediation action not found"}), 404

            return jsonify({"action": model_to_dict(action)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get remediation action: {str(e)}"}), 500


@remediation_bp.route("/actions", methods=["POST"])
@require_auth
def create_remediation_action():
    """Create a new remediation action."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["action_type", "action_name", "description"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": "Missing required field: {field}"}), 400

        # Validate action type
        valid_action_types = [
            "scale_up",
            "scale_down",
            "restart_service",
            "cleanup_disk",
            "custom",
        ]
        if data["action_type"] not in valid_action_types:
            return (
                jsonify(
                    {
                        "error": "Invalid action type. Must be one of: {valid_action_types}"
                    }
                ),
                400,
            )

        # Validate priority
        valid_priorities = ["low", "medium", "high", "critical"]
        if "priority" in data and data["priority"] not in valid_priorities:
            return (
                jsonify(
                    {"error": "Invalid priority. Must be one of: {valid_priorities}"}
                ),
                400,
            )

        # Validate anomaly_id if provided
        anomaly_id = data.get("anomaly_id")
        if anomaly_id:
            with get_db_session() as session:
                anomaly = session.query(Anomaly).filter_by(id=anomaly_id).first()
                if not anomaly:
                    return jsonify({"error": "Referenced anomaly not found"}), 404

        with get_db_session() as session:
            # Create remediation action
            action = RemediationAction(
                anomaly_id=data.get("anomaly_id"),
                action_type=data["action_type"],
                action_name=data["action_name"],
                description=data["description"],
                priority=data.get("priority", "medium"),
                parameters=data.get("parameters"),
                status="pending",
            )

            session.add(action)

            # Log audit event
            user = get_current_user()
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_action_created",
                resource_type="remediation_action",
                resource_id=action.id,
                details={
                    "action_name": action.action_name,
                    "action_type": action.action_type,
                },
            )

            return (
                jsonify(
                    {
                        "message": "Remediation action created successfully",
                        "action": model_to_dict(action),
                    }
                ),
                201,
            )

    except Exception as e:
        return jsonify({"error": "Failed to create remediation action: {str(e)}"}), 500


@remediation_bp.route("/actions/<int:action_id>/approve", methods=["POST"])
@require_auth
def approve_remediation_action(action_id):
    """Approve a remediation action."""
    try:
        user = get_current_user()

        with get_db_session() as session:
            action = session.query(RemediationAction).filter_by(id=action_id).first()

            if not action:
                return jsonify({"error": "Remediation action not found"}), 404

            if action.status != "pending":
                return jsonify({"error": "Only pending actions can be approved"}), 400

            # Update action
            action.status = "approved"
            action.approved_by = user.id
            action.approved_at = datetime.utcnow()

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_action_approved",
                resource_type="remediation_action",
                resource_id=action.id,
                details={
                    "action_name": action.action_name,
                    "action_type": action.action_type,
                },
            )

            return (
                jsonify(
                    {
                        "message": "Remediation action approved successfully",
                        "action": model_to_dict(action),
                    }
                ),
                200,
            )

    except Exception as e:
        return (
            jsonify({"error": "Failed to approve remediation action: {str(e)}"}),
            500,
        )


@remediation_bp.route("/actions/<int:action_id>/execute", methods=["POST"])
@require_auth
def execute_remediation_action(action_id):
    """Execute a remediation action."""
    try:
        user = get_current_user()
        data = request.get_json() or {}

        with get_db_session() as session:
            action = session.query(RemediationAction).filter_by(id=action_id).first()

            if not action:
                return jsonify({"error": "Remediation action not found"}), 404

            if action.status not in ["pending", "approved"]:
                return (
                    jsonify({"error": "Action must be pending or approved to execute"}),
                    400,
                )

            # Update action status to running
            action.status = "running"
            action.executed_by = user.id
            action.executed_at = datetime.utcnow()

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_action_executed",
                resource_type="remediation_action",
                resource_id=action.id,
                details={
                    "action_name": action.action_name,
                    "action_type": action.action_type,
                },
            )

            # Execute the remediation action
            try:
                result = remediation_engine.execute_action(
                    action_type=action.action_type,
                    parameters=action.parameters or {},
                    user_id=user.id,
                )

                # Update action with execution result
                action.status = "success" if result.get("success") else "failed"
                action.execution_result = result
                action.error_message = (
                    result.get("error") if not result.get("success") else None
                )

                return (
                    jsonify(
                        {
                            "message": "Remediation action executed successfully",
                            "action": model_to_dict(action),
                            "execution_result": result,
                        }
                    ),
                    200,
                )

            except Exception as execution_error:
                # Update action with error
                action.status = "failed"
                action.error_message = str(execution_error)
                action.execution_result = {
                    "success": False,
                    "error": str(execution_error),
                }

                return (
                    jsonify(
                        {
                            "message": "Remediation action execution failed",
                            "action": model_to_dict(action),
                            "execution_result": {
                                "success": False,
                                "error": str(execution_error),
                            },
                        }
                    ),
                    500,
                )

    except Exception as e:
        return (
            jsonify({"error": "Failed to execute remediation action: {str(e)}"}),
            500,
        )


@remediation_bp.route("/actions/<int:action_id>/cancel", methods=["POST"])
@require_auth
def cancel_remediation_action(action_id):
    """Cancel a remediation action."""
    try:
        user = get_current_user()

        with get_db_session() as session:
            action = session.query(RemediationAction).filter_by(id=action_id).first()

            if not action:
                return jsonify({"error": "Remediation action not found"}), 404

            if action.status not in ["pending", "approved", "running"]:
                return (
                    jsonify({"error": "Action cannot be cancelled in current status"}),
                    400,
                )

            # Update action
            action.status = "cancelled"

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_action_cancelled",
                resource_type="remediation_action",
                resource_id=action.id,
                details={
                    "action_name": action.action_name,
                    "action_type": action.action_type,
                },
            )

            return (
                jsonify(
                    {
                        "message": "Remediation action cancelled successfully",
                        "action": model_to_dict(action),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to cancel remediation action: {str(e)}"}), 500


@remediation_bp.route("/actions/<int:action_id>", methods=["PUT"])
@require_auth
def update_remediation_action(action_id):
    """Update a remediation action."""
    try:
        data = request.get_json()
        user = get_current_user()

        with get_db_session() as session:
            action = session.query(RemediationAction).filter_by(id=action_id).first()

            if not action:
                return jsonify({"error": "Remediation action not found"}), 404

            # Only allow updates if action is pending
            if action.status != "pending":
                return jsonify({"error": "Only pending actions can be updated"}), 400

            # Update allowed fields
            allowed_fields = ["action_name", "description", "priority", "parameters"]
            for field in allowed_fields:
                if field in data:
                    setattr(action, field, data[field])

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_action_updated",
                resource_type="remediation_action",
                resource_id=action.id,
                details={"action_name": action.action_name},
            )

            return (
                jsonify(
                    {
                        "message": "Remediation action updated successfully",
                        "action": model_to_dict(action),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to update remediation action: {str(e)}"}), 500


@remediation_bp.route("/actions/<int:action_id>", methods=["DELETE"])
@require_auth
def delete_remediation_action(action_id):
    """Delete a remediation action."""
    try:
        user = get_current_user()

        with get_db_session() as session:
            action = session.query(RemediationAction).filter_by(id=action_id).first()

            if not action:
                return jsonify({"error": "Remediation action not found"}), 404

            # Only allow deletion if action is pending
            if action.status != "pending":
                return jsonify({"error": "Only pending actions can be deleted"}), 400

            # Log audit event before deletion
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_action_deleted",
                resource_type="remediation_action",
                resource_id=action.id,
                details={
                    "action_name": action.action_name,
                    "action_type": action.action_type,
                },
            )

            # Delete action
            session.delete(action)

            return jsonify({"message": "Remediation action deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete remediation action: {str(e)}"}), 500


@remediation_bp.route("/actions/stats", methods=["GET"])
@require_auth
def get_remediation_stats():
    """Get remediation action statistics."""
    try:
        with get_db_session() as session:
            # Get total counts by status
            status_stats = (
                session.query(
                    RemediationAction.status,
                    session.query(RemediationAction)
                    .filter(RemediationAction.status == RemediationAction.status)
                    .count()
                    .label("count"),
                )
                .group_by(RemediationAction.status)
                .all()
            )

            # Get total counts by action type
            type_stats = (
                session.query(
                    RemediationAction.action_type,
                    session.query(RemediationAction)
                    .filter(
                        RemediationAction.action_type == RemediationAction.action_type
                    )
                    .count()
                    .label("count"),
                )
                .group_by(RemediationAction.action_type)
                .all()
            )

            # Get recent actions (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_count = (
                session.query(RemediationAction)
                .filter(RemediationAction.created_at >= yesterday)
                .count()
            )

            # Get total count
            total_count = session.query(RemediationAction).count()

            # Get success rate
            success_count = (
                session.query(RemediationAction)
                .filter(RemediationAction.status == "success")
                .count()
            )
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0

            return (
                jsonify(
                    {
                        "stats": {
                            "total": total_count,
                            "recent_24h": recent_count,
                            "success_rate": round(success_rate, 2),
                            "by_status": {
                                stat.status: stat.count for stat in status_stats
                            },
                            "by_type": {
                                stat.action_type: stat.count for stat in type_stats
                            },
                        }
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to get remediation stats: {str(e)}"}), 500


@remediation_bp.route("/actions/batch", methods=["POST"])
@require_auth
def create_batch_remediation_actions():
    """Create multiple remediation actions in batch."""
    try:
        data = request.get_json()
        actions_data = data.get("actions", [])

        if not actions_data:
            return jsonify({"error": "No remediation actions provided"}), 400

        if len(actions_data) > 50:  # Limit batch size
            return (
                jsonify({"error": "Batch size cannot exceed 50 remediation actions"}),
                400,
            )

        created_actions = []
        user = get_current_user()

        with get_db_session() as session:
            for action_data in actions_data:
                # Validate required fields
                required_fields = ["action_type", "action_name", "description"]
                for field in required_fields:
                    if field not in action_data:
                        return (
                            jsonify(
                                {
                                    "error": "Missing required field: {field} in remediation action"
                                }
                            ),
                            400,
                        )

                # Create action
                action = RemediationAction(
                    anomaly_id=action_data.get("anomaly_id"),
                    action_type=action_data["action_type"],
                    action_name=action_data["action_name"],
                    description=action_data["description"],
                    priority=action_data.get("priority", "medium"),
                    parameters=action_data.get("parameters"),
                    status="pending",
                )

                session.add(action)
                created_actions.append(action)

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="remediation_actions_batch_created",
                details={"count": len(created_actions)},
            )

            return (
                jsonify(
                    {
                        "message": f"{len(created_actions)} remediation actions created successfully",
                        "actions": models_to_list(created_actions),
                    }
                ),
                201,
            )

    except Exception as e:
        return (
            jsonify({"error": "Failed to create batch remediation actions: {str(e)}"}),
            500,
        )


@remediation_bp.route("/available-actions", methods=["GET"])
@require_auth
def get_available_actions():
    """Get list of available remediation action types."""
    try:
        available_actions = [
            {
                "type": "scale_up",
                "name": "Scale Up Service",
                "description": "Increase the number of service instances",
                "parameters": ["service_name", "instance_count"],
                "estimated_duration": "2-3 minutes",
            },
            {
                "type": "scale_down",
                "name": "Scale Down Service",
                "description": "Decrease the number of service instances",
                "parameters": ["service_name", "instance_count"],
                "estimated_duration": "2-3 minutes",
            },
            {
                "type": "restart_service",
                "name": "Restart Service",
                "description": "Restart a specific service",
                "parameters": ["service_name"],
                "estimated_duration": "1-2 minutes",
            },
            {
                "type": "cleanup_disk",
                "name": "Cleanup Disk Space",
                "description": "Clean up temporary files and logs",
                "parameters": ["disk_path", "cleanup_size_mb"],
                "estimated_duration": "30 seconds",
            },
            {
                "type": "custom",
                "name": "Custom Action",
                "description": "Execute a custom remediation script",
                "parameters": ["script_path", "arguments"],
                "estimated_duration": "Variable",
            },
        ]

        return jsonify({"available_actions": available_actions}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get available actions: {str(e)}"}), 500
