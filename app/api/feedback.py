#!/usr/bin/env python3
"""
Feedback API Endpoints for Smart CloudOps AI - Minimal Working Version
User feedback collection and management system
"""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

# Create blueprint
feedback_bp = Blueprint("feedback", __name__)
# Mock data for testing
MOCK_FEEDBACK = [
    {
        "id": 1,
        "user_id": 1,
        "feedback_type": "bug_report",
        "title": "High CPU Alert False Positive",
        "description": "The system flagged normal CPU usage as high during maintenance window",
        "rating": 3,
        "status": "open",
        "priority": "medium",
        "tags": ["false-positive", "cpu", "alerting"],
        "created_at": "2024-01-15T08:30:00Z",
        "updated_at": "2024-01-15T08:30:00Z",
    },
    {
        "id": 2,
        "user_id": 2,
        "feedback_type": "feature_request",
        "title": "Dashboard Customization",
        "description": "Would like to customize dashboard layout and add custom widgets",
        "rating": 5,
        "status": "in_progress",
        "priority": "low",
        "tags": ["dashboard", "customization", "ui"],
        "created_at": "2024-01-14T15:20:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
    },
]


@feedback_bp.route("/", methods=["GET"])
def get_feedback():
    """Get all feedback with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        feedback_type = request.args.get("type")
        status = request.args.get("status")
        priority = request.args.get("priority")
        user_id = request.args.get("user_id", type=int)

        # Filter feedback based on query parameters
        filtered_feedback = MOCK_FEEDBACK.copy()

        if feedback_type:
            filtered_feedback = [
                f for f in filtered_feedback if f["feedback_type"] == feedback_type
            ]
        if status:
            filtered_feedback = [f for f in filtered_feedback if f["status"] == status]
        if priority:
            filtered_feedback = [
                f for f in filtered_feedback if f["priority"] == priority
            ]
        if user_id:
            filtered_feedback = [
                f for f in filtered_feedback if f["user_id"] == user_id
            ]

        # Calculate pagination
        total = len(filtered_feedback)
        start = (page - 1) * per_page
        end = start + per_page
        feedback_page = filtered_feedback[start:end]

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "feedback": feedback_page,
                        "pagination": {
                            "page": page,
                            "per_page": per_page,
                            "total": total,
                            "pages": (total + per_page - 1) // per_page,
                        },
                    },
                }
            ),
            200
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to retrieve feedback: {str(e)}"}
            ),
            500
        )


@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
def get_feedback_item(feedback_id):
    """Get a specific feedback item by ID."""
    try:
        # Find feedback by ID
        feedback_item = next(
            (f for f in MOCK_FEEDBACK if f["id"] == feedback_id), None
        )

        if not feedback_item:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Feedback with ID {feedback_id} not found",
                    }
                ),
                404
            )

        return jsonify({"status": "success", "data": {"feedback": feedback_item}}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to retrieve feedback: {str(e)}",
                }
            ),
            500
        )


@feedback_bp.route("/", methods=["POST"])
def create_feedback():
    """Create a new feedback item."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Validate required fields
        required_fields = ["user_id", "feedback_type", "title", "description"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Missing required field: {field}",
                        }
                    ),
                    400
                )

        # Create new feedback item
        new_feedback = {
            "id": len(MOCK_FEEDBACK) + 1,
            "user_id": data["user_id"],
            "feedback_type": data["feedback_type"],
            "title": data["title"],
            "description": data["description"],
            "rating": data.get("rating"),
            "status": data.get("status", "open"),
            "priority": data.get("priority", "medium"),
            "tags": data.get("tags", []),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Add to mock data (in real app, this would be saved to database)
        MOCK_FEEDBACK.append(new_feedback)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Feedback created successfully",
                    "data": {"feedback": new_feedback},
                }
            ),
            201
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to create feedback: {str(e)}",
                }
            ),
            500
        )


@feedback_bp.route("/<int:feedback_id>", methods=["PUT"])
def update_feedback(feedback_id):
    """Update an existing feedback item."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Find feedback by ID
        feedback_item = next(
            (f for f in MOCK_FEEDBACK if f["id"] == feedback_id), None
        )

        if not feedback_item:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Feedback with ID {feedback_id} not found",
                    }
                ),
                404
            )

        # Update feedback item
        for key, value in data.items():
            if key in feedback_item:
                feedback_item[key] = value

        feedback_item["updated_at"] = datetime.now(timezone.utc).isoformat()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Feedback updated successfully",
                    "data": {"feedback": feedback_item},
                }
            ),
            200
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to update feedback: {str(e)}",
                }
            ),
            500
        )


@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
def delete_feedback(feedback_id):
    """Delete a feedback item."""
    try:
        # Find feedback by ID
        feedback_item = next(
            (f for f in MOCK_FEEDBACK if f["id"] == feedback_id), None
        )

        if not feedback_item:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Feedback with ID {feedback_id} not found",
                    }
                ),
                404
            )

        # Remove from mock data (in real app, this would be deleted from database)
        MOCK_FEEDBACK.remove(feedback_item)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Feedback deleted successfully",
                }
            ),
            200
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to delete feedback: {str(e)}",
                }
            ),
            500
        )


@feedback_bp.route("/stats", methods=["GET"])
def get_feedback_stats():
    """Get feedback statistics."""
    try:
        # Calculate statistics
        total_feedback = len(MOCK_FEEDBACK)
        feedback_by_type = {}
        feedback_by_status = {}
        feedback_by_priority = {}

        for feedback in MOCK_FEEDBACK:
            # Count by type
            feedback_type = feedback["feedback_type"]
            feedback_by_type[feedback_type] = feedback_by_type.get(feedback_type, 0) + 1

            # Count by status
            status = feedback["status"]
            feedback_by_status[status] = feedback_by_status.get(status, 0) + 1

            # Count by priority
            priority = feedback["priority"]
            feedback_by_priority[priority] = feedback_by_priority.get(priority, 0) + 1

        stats = {
            "total_feedback": total_feedback,
            "by_type": feedback_by_type,
            "by_status": feedback_by_status,
            "by_priority": feedback_by_priority,
        }

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"stats": stats},
                }
            ),
            200
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to retrieve feedback stats: {str(e)}",
                }
            ),
            500
        )
