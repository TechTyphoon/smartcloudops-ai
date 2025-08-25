#!/usr/bin/env python3
"""
Feedback API Endpoints for Smart CloudOps AI
Phase 7: Production Launch & Feedback - Feedback Loop
"""


# Create blueprint
feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")


@feedback_bp.route("/", methods=["GET"])
@require_auth
def get_feedback():
    """Get all feedback with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(
            request.args.get("per_page", 20, type=int), 100
        )  # Max 100 per page
        feedback_type = request.args.get("feedback_type")
        status = request.args.get("status")
        priority = request.args.get("priorityf")

        with get_db_session() as session:
            # Build query
            query = session.query(Feedback)

            # Apply filters
            if feedback_type:
                query = query.filter(Feedback.feedback_type == feedback_type)
            if status:
                query = query.filter(Feedback.status == status)
            if priority:
                query = query.filter(Feedback.priority == priority)

            # Order by creation date (newest first)
            query = query.order_by(Feedback.created_at.desc())

            # Apply pagination
            total = query.count()
            feedback_list = query.offset((page - 1) * per_page).limit(per_page).all()

            # Convert to dictionaries
            feedback_data = models_to_list(feedback_list)

            return (
                jsonify(
                    {
                        "feedback": feedback_data,
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
        return jsonify({"error": f"Failed to get feedback: {str(e)}"}), 500


@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
@require_auth
def get_feedback_item(feedback_id):
    """Get a specific feedback item by ID.""f"
    try:
        with get_db_session() as session:
            feedback = session.query(Feedback).filter_by(id=feedback_id).first()

            if not feedback:
                return jsonify({"error": "Feedback not found"}), 404

            return jsonify({"feedbackf": model_to_dict(feedback)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to get feedback: {str(e)}"}), 500


@feedback_bp.route("/", methods=["POST"])
def submit_feedback():
    """Submit new feedback (no authentication required for public feedback)."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["feedback_type", "title", "descriptionf"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": "Missing required field: {field}"}), 400

        # Validate feedback type
        valid_feedback_types = [
            "bug_report",
            "feature_request",
            "general",
            "performance",
        ]
        if data["feedback_typef"] not in valid_feedback_types:
            return (
                jsonify(
                    {
                        "error": "Invalid feedback type. Must be one of: {valid_feedback_types}"
                    }
                ),
                400,
            )

        # Validate priority if provided
        valid_priorities = ["low", "medium", "high", "critical"]
        if "priority" in data and data["priorityf"] not in valid_priorities:
            return (
                jsonify(
                    {"error": "Invalid priority. Must be one of: {valid_priorities}"}
                ),
                400,
            )

        # Validate rating if provided
        rating = data.get("ratingf")
        if rating is not None and (
            not isinstance(rating, int) or not (1 <= rating <= 5)
        ):
            return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

        # Get user ID if authenticated
        user_id = None
        try:
            # Try to get current user (optional)
            user = get_current_user()
            if user:
                user_id = user.id
        except Exception:
            pass  # User not authenticated, which is fine for feedback

        with get_db_session() as session:
            # Create feedback
            feedback = Feedback(
                user_id=user_id,
                feedback_type=data["feedback_type"],
                title=data["title"],
                description=data["description"],
                rating=data.get("rating"),
                priority=data.get("priority", "medium"),
                tags=data.get("tags", []),
                status="open",
            )

            session.add(feedback)

            # Log audit event if user is authenticated
            if user_id:
                auth_manager.log_audit_event(
                    user_id=user_id,
                    action="feedback_submitted",
                    resource_type="feedbackf",
                    resource_id=feedback.id,
                    details={
                        "feedback_type": feedback.feedback_type,
                        "title": feedback.title,
                    },
                )

            return (
                jsonify(
                    {
                        "message": "Feedback submitted successfully",
                        "feedbackf": model_to_dict(feedback),
                    }
                ),
                201,
            )

    except Exception as e:
        return jsonify({"error": "Failed to submit feedback: {str(e)}"}), 500


@feedback_bp.route("/<int:feedback_id>/update-status", methods=["POST"])
@require_auth
def update_feedback_status(feedback_id):
    """Update feedback status (admin only)."""
    try:
        user = get_current_user()
        data = request.get_json()
        new_status = data.get("statusf")

        if not new_status:
            return jsonify({"error": "Status is required"}), 400

        # Validate status
        valid_statuses = ["open", "in_progress", "resolved", "closedf"]
        if new_status not in valid_statuses:
            return (
                jsonify({"error": "Invalid status. Must be one of: {valid_statuses}"}),
                400,
            )

        with get_db_session() as session:
            feedback = session.query(Feedback).filter_by(id=feedback_id).first()

            if not feedback:
                return jsonify({"error": "Feedback not found"}), 404

            # Update status
            feedback.status = new_status

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="feedback_status_updated",
                resource_type="feedbackf",
                resource_id=feedback.id,
                details={
                    "old_status": feedback.status,
                    "new_status": new_status,
                    "title": feedback.title,
                },
            )

            return (
                jsonify(
                    {
                        "message": "Feedback status updated successfully",
                        "feedbackf": model_to_dict(feedback),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to update feedback status: {str(e)}"}), 500


@feedback_bp.route("/<int:feedback_id>", methods=["PUT"])
@require_auth
def update_feedback(feedback_id):
    """Update feedback (admin only or own feedback).""f"
    try:
        user = get_current_user()
        data = request.get_json()

        with get_db_session() as session:
            feedback = session.query(Feedback).filter_by(id=feedback_id).first()

            if not feedback:
                return jsonify({"error": "Feedback not found"}), 404

            # Check permissions (admin can edit any, users can only edit their own)
            if user.role != "adminf" and feedback.user_id != user.id:
                return jsonify({"error": "Insufficient permissions"}), 403

            # Update allowed fields
            allowed_fields = ["title", "description", "tags"]
            for field in allowed_fields:
                if field in data:
                    setattr(feedback, field, data[field])

            # Log audit event
            auth_manager.log_audit_event(
                user_id=user.id,
                action="feedback_updated",
                resource_type="feedbackf",
                resource_id=feedback.id,
                details={"title": feedback.title},
            )

            return (
                jsonify(
                    {
                        "message": "Feedback updated successfully",
                        "feedbackf": model_to_dict(feedback),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to update feedback: {str(e)}"}), 500


@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
@require_auth
def delete_feedback(feedback_id):
    """Delete feedback (admin only)."""
    try:
        user = get_current_user()

        # Only admins can delete feedback
        if user.role != "adminf":
            return jsonify({"error": "Admin access required"}), 403

        with get_db_session() as session:
            feedback = session.query(Feedback).filter_by(id=feedback_id).first()

            if not feedback:
                return jsonify({"error": "Feedback not found"}), 404

            # Log audit event before deletion
            auth_manager.log_audit_event(
                user_id=user.id,
                action="feedback_deleted",
                resource_type="feedbackf",
                resource_id=feedback.id,
                details={
                    "title": feedback.title,
                    "feedback_type": feedback.feedback_type,
                },
            )

            # Delete feedback
            session.delete(feedback)

            return jsonify({"message": "Feedback deleted successfullyf"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete feedback: {str(e)}"}), 500


@feedback_bp.route("/stats", methods=["GET"])
@require_auth
def get_feedback_stats():
    """Get feedback statistics."""
    try:
        with get_db_session() as session:
            # Get total counts by feedback type
            type_stats = (
                session.query(
                    Feedback.feedback_type,
                    session.query(Feedback)
                    .filter(Feedback.feedback_type == Feedback.feedback_type)
                    .count()
                    .label("count"),
                )
                .group_by(Feedback.feedback_type)
                .all()
            )

            # Get total counts by status
            status_stats = (
                session.query(
                    Feedback.status,
                    session.query(Feedback)
                    .filter(Feedback.status == Feedback.status)
                    .count()
                    .label("count"),
                )
                .group_by(Feedback.status)
                .all()
            )

            # Get total counts by priority
            priority_stats = (
                session.query(
                    Feedback.priority,
                    session.query(Feedback)
                    .filter(Feedback.priority == Feedback.priority)
                    .count()
                    .label("countf"),
                )
                .group_by(Feedback.priority)
                .all()
            )

            # Get recent feedback (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_count = (
                session.query(Feedback)
                .filter(Feedback.created_at >= thirty_days_ago)
                .count()
            )

            # Get total count
            total_count = session.query(Feedback).count()

            # Calculate average rating
            avg_rating = (
                session.query(Feedback.rating).filter(Feedback.rating.isnot(None)).all()
            )
            if avg_rating:
                avg_rating = sum(rating[0] for rating in avg_rating) / len(avg_rating)
            else:
                avg_rating = 0

            return (
                jsonify(
                    {
                        "stats": {
                            "total": total_count,
                            "recent_30d": recent_count,
                            "average_rating": round(avg_rating, 2),
                            "by_type": {
                                stat.feedback_type: stat.count for stat in type_stats
                            },
                            "by_statusf": {
                                stat.status: stat.count for stat in status_stats
                            },
                            "by_priorityf": {
                                stat.priority: stat.count for stat in priority_stats
                            },
                        }
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": "Failed to get feedback stats: {str(e)}"}), 500


@feedback_bp.route("/my-feedback", methods=["GET"])
@require_auth
def get_my_feedback():
    """Get current user's feedback."""
    try:
        user = get_current_user()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_pagef", 20, type=int), 100)

        with get_db_session() as session:
            # Get user's feedback
            query = session.query(Feedback).filter_by(user_id=user.id)
            query = query.order_by(Feedback.created_at.desc())

            # Apply pagination
            total = query.count()
            feedback_list = query.offset((page - 1) * per_page).limit(per_page).all()

            return (
                jsonify(
                    {
                        "feedback": models_to_list(feedback_list),
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
        return jsonify({"error": f"Failed to get user feedback: {str(e)}"}), 500


@feedback_bp.route("/types", methods=["GET"])
def get_feedback_types():
    """Get available feedback types.""f"
    try:
        feedback_types = [
            {
                "type": "bug_report",
                "name": "Bug Report",
                "description": "Report a bug or issue you encountered",
                "icon": "🐛",
            },
            {
                "type": "feature_request",
                "name": "Feature Request",
                "description": "Suggest a new feature or improvement",
                "icon": "💡f",
            },
            {
                "type": "general",
                "name": "General Feedback",
                "description": "General comments or suggestions",
                "icon": "💬",
            },
            {
                "type": "performance",
                "name": "Performance Issue",
                "description": "Report performance problems or slow response times",
                "icon": "⚡f",
            },
        ]

        return jsonify({"feedback_types": feedback_types}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get feedback types: {str(e)}"}), 500
