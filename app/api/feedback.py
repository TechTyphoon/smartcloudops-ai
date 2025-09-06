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
        "description": "The system flagged normal CPU usage as high during "
        "maintenance window",
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
        "description": "Would like to customize dashboard layout and add "
        "custom widgets",
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
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to retrieve feedback: {str(e)}",
                }
            ),
            500,
        )


@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
def get_feedback_by_id(feedback_id):
    """Get a specific feedback by ID."""
    try:
        # Find feedback by ID
        feedback = next((f for f in MOCK_FEEDBACK if f["id"] == feedback_id), None)

        if not feedback:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Feedback with ID {feedback_id} not found",
                    }
                ),
                404,
            )

        return jsonify({"status": "success", "data": {"feedback": feedback}}), 200

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to retrieve feedback: {str(e)}"}
            ),
            500,
        )


@feedback_bp.route("/", methods=["POST"])
def create_feedback():
    """Create a new feedback entry."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Validate required fields
        required_fields = ["feedback_type", "title", "description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Missing required field: {field}",
                        }
                    ),
                    400,
                )

        # Create new feedback entry
        new_feedback = {
            "id": len(MOCK_FEEDBACK) + 1,
            "user_id": data.get("user_id", 1),
            "feedback_type": data["feedback_type"],
            "title": data["title"],
            "description": data["description"],
            "rating": data.get("rating", 0),
            "status": data.get("status", "open"),
            "priority": data.get("priority", "medium"),
            "tags": data.get("tags", []),
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
        }

        # Add to mock data (in real app, this would be saved to database)
        MOCK_FEEDBACK.append(new_feedback)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"feedback": new_feedback},
                    "message": "Feedback created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to create feedback: {str(e)}"}
            ),
            500,
        )


@feedback_bp.route("/<int:feedback_id>", methods=["PUT"])
def update_feedback(feedback_id):
    """Update an existing feedback entry."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Find feedback by ID
        feedback_index = next(
            (i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None
        )

        if feedback_index is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Feedback with ID {feedback_id} not found",
                    }
                ),
                404,
            )

        # Update feedback
        MOCK_FEEDBACK[feedback_index].update(data)
        MOCK_FEEDBACK[feedback_index]["updated_at"] = (
            datetime.now(timezone.utc).isoformat() + "Z"
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"feedback": MOCK_FEEDBACK[feedback_index]},
                    "message": "Feedback updated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to update feedback: {str(e)}"}
            ),
            500,
        )


@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
def delete_feedback(feedback_id):
    """Delete a feedback entry."""
    try:
        # Find feedback by ID
        feedback_index = next(
            (i for i, f in enumerate(MOCK_FEEDBACK) if f["id"] == feedback_id), None
        )

        if feedback_index is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Feedback with ID {feedback_id} not found",
                    }
                ),
                404,
            )

        # Remove feedback
        deleted_feedback = MOCK_FEEDBACK.pop(feedback_index)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Feedback with ID {feedback_id} deleted successfully",
                    "data": {"deleted_feedback": deleted_feedback},
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to delete feedback: {str(e)}"}
            ),
            500,
        )


@feedback_bp.route("/stats", methods=["GET"])
def get_feedback_stats():
    """Get feedback statistics."""
    try:
        # Calculate basic statistics
        total_feedback = len(MOCK_FEEDBACK)

        # Count by type
        type_counts = {}
        for feedback in MOCK_FEEDBACK:
            feedback_type = feedback["feedback_type"]
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1

        # Count by status
        status_counts = {}
        for feedback in MOCK_FEEDBACK:
            status = feedback["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by priority
        priority_counts = {}
        for feedback in MOCK_FEEDBACK:
            priority = feedback["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Average rating
        ratings = [f["rating"] for f in MOCK_FEEDBACK if f["rating"] > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        stats = {
            "total_feedback": total_feedback,
            "by_type": type_counts,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "average_rating": round(avg_rating, 2),
        }

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
                {
                    "status": "error",
                    "message": f"Failed to get feedback stats: {str(e)}",
                }
            ),
            500,
        )


@feedback_bp.route("/export", methods=["GET"])
def export_feedback():
    """Export feedback data."""
    try:
        # Get query parameters
        format_type = request.args.get("format", "json")
        feedback_type = request.args.get("type")
        status = request.args.get("status")

        # Filter feedback
        filtered_feedback = MOCK_FEEDBACK.copy()

        if feedback_type:
            filtered_feedback = [
                f for f in filtered_feedback if f["feedback_type"] == feedback_type
            ]
        if status:
            filtered_feedback = [f for f in filtered_feedback if f["status"] == status]

        # Prepare export data
        export_data = {
            "format": format_type,
            "total_records": len(filtered_feedback),
            "exported_at": datetime.now(timezone.utc).isoformat() + "Z",
            "data": filtered_feedback,
        }

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {"export": export_data},
                    "message": f"Feedback exported successfully in "
                    f"{format_type} format",
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to export feedback: {str(e)}"}
            ),
            500,
        )
