"""
Beta Testing API Endpoints for SmartCloudOps AI
Provides REST API for beta testers to interact with the system
"""

import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request

from .beta_testing import BetaTestingManager, TestingScenario, UserRole

logger = logging.getLogger(__name__)

# Create Blueprint
beta_api = Blueprint("beta_api", __name__, url_prefix="/api/beta")

# Initialize beta testing manager
beta_manager = BetaTestingManager()


def require_api_key(f):
    """Decorator to require valid API key"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        tester = beta_manager.get_tester_by_api_key(api_key)
        if not tester:
            return jsonify({"error": "Invalid API key"}), 401

        if not tester.is_active:
            return jsonify({"error": "Tester account inactive"}), 403

        # Add tester to request context
        request.tester = tester
        return f(*args, **kwargs)

    return decorated_function


@beta_api.route("/status", methods=["GET"])
@require_api_key
def get_status():
    """Get beta testing status for the authenticated tester"""
    try:
        tester = request.tester
        return jsonify(
            {
                "status": "success",
                "data": {
                    "tester": {
                        "name": tester.name,
                        "email": tester.email,
                        "role": tester.role.value,
                        "access_level": tester.access_level,
                        "testing_scenarios": [
                            s.value for s in tester.testing_scenarios
                        ],
                        "created_at": tester.created_at.isoformat(),
                        "last_active": tester.last_active.isoformat()
                        if tester.last_active
                        else None,
                        "feedback_count": tester.feedback_count,
                        "is_active": tester.is_active,
                    }
                },
            }
        )
    except Exception as e:
        logger.error(f"Error getting tester status: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/scenarios", methods=["GET"])
@require_api_key
def get_scenarios():
    """Get available testing scenarios"""
    try:
        scenarios = [
            {
                "id": scenario.value,
                "name": scenario.value.replace("_", " ").title(),
                "description": _get_scenario_description(scenario),
            }
            for scenario in TestingScenario
        ]

        return jsonify({"status": "success", "data": {"scenarios": scenarios}})
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/session/start", methods=["POST"])
@require_api_key
def start_session():
    """Start a new testing session"""
    try:
        data = request.get_json()
        if not data or "scenario" not in data:
            return jsonify({"error": "Scenario required"}), 400

        scenario = TestingScenario(data["scenario"])
        tester = request.tester

        # Check if tester has access to this scenario
        if scenario not in tester.testing_scenarios:
            return jsonify({"error": "Access denied to this scenario"}), 403

        session = beta_manager.start_session(tester, scenario)
        return jsonify(
            {
                "status": "success",
                "data": {
                    "session_id": session.id,
                    "scenario": session.scenario.value,
                    "started_at": session.started_at.isoformat(),
                    "tester": tester.name,
                },
            }
        )
    except ValueError:
        return jsonify({"error": "Invalid scenario"}), 400
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/session/<session_id>/end", methods=["POST"])
@require_api_key
def end_session(session_id: str):
    """End a testing session"""
    try:
        data = request.get_json() or {}
        tester = request.tester

        session = beta_manager.end_session(session_id, tester, data.get("notes", ""))
        if not session:
            return jsonify({"error": "Session not found or access denied"}), 404

        return jsonify(
            {
                "status": "success",
                "data": {
                    "session_id": session.id,
                    "ended_at": session.ended_at.isoformat(),
                    "duration_minutes": session.duration_minutes,
                    "notes": session.notes,
                },
            }
        )
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/feedback", methods=["POST"])
@require_api_key
def submit_feedback():
    """Submit feedback for a testing session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Feedback data required"}), 400

        required_fields = ["session_id", "rating", "comments"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return (
                jsonify(
                    {"error": f'Missing required fields: {", ".join(missing_fields)}'}
                ),
                400,
            )

        tester = request.tester
        feedback = beta_manager.submit_feedback(
            session_id=data["session_id"],
            tester=tester,
            rating=data["rating"],
            comments=data["comments"],
            category=data.get("category", "general"),
            priority=data.get("priority", "medium"),
        )

        if not feedback:
            return jsonify({"error": "Session not found or access denied"}), 404

        return jsonify(
            {
                "status": "success",
                "data": {
                    "feedback_id": feedback.id,
                    "submitted_at": feedback.submitted_at.isoformat(),
                    "rating": feedback.rating,
                    "category": feedback.category,
                    "priority": feedback.priority,
                },
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/sessions", methods=["GET"])
@require_api_key
def get_sessions():
    """Get testing sessions for the authenticated tester"""
    try:
        tester = request.tester
        sessions = beta_manager.get_tester_sessions(tester)

        return jsonify(
            {
                "status": "success",
                "data": {
                    "sessions": [
                        {
                            "id": session.id,
                            "scenario": session.scenario.value,
                            "started_at": session.started_at.isoformat(),
                            "ended_at": session.ended_at.isoformat()
                            if session.ended_at
                            else None,
                            "duration_minutes": session.duration_minutes,
                            "notes": session.notes,
                        }
                        for session in sessions
                    ]
                },
            }
        )
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/test/notification", methods=["POST"])
@require_api_key
def test_notification():
    """Test notification system for the authenticated tester"""
    try:
        data = request.get_json() or {}
        tester = request.tester

        # Test notification
        success = beta_manager.test_notification(
            tester, data.get("message", "Test notification")
        )

        if success:
            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "message": "Test notification sent successfully",
                        "tester": tester.name,
                        "sent_at": datetime.now().isoformat(),
                    },
                }
            )
        else:
            return jsonify({"error": "Failed to send test notification"}), 500

    except Exception as e:
        logger.error(f"Error testing notification: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for beta API"""
    try:
        # Check if beta manager is working
        testers_count = len(beta_manager.get_all_testers())
        active_sessions = len(beta_manager.get_active_sessions())

        return jsonify(
            {
                "status": "success",
                "data": {
                    "beta_api": "healthy",
                    "testers_count": testers_count,
                    "active_sessions": active_sessions,
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"error": "Health check failed"}), 500


def _get_scenario_description(scenario: TestingScenario) -> str:
    """Get description for a testing scenario"""
    descriptions = {
        TestingScenario.BASIC_CHATOPS: "Basic ChatOps functionality testing",
        TestingScenario.ML_ANOMALY_DETECTION: "ML-based anomaly detection testing",
        TestingScenario.AUTO_REMEDIATION: "Automated remediation testing",
        TestingScenario.ADVANCED_CONTEXT: "Advanced context management testing",
        TestingScenario.LOAD_TESTING: "System performance under load testing",
        TestingScenario.SECURITY_TESTING: "Security and vulnerability testing",
    }
    return descriptions.get(scenario, "No description available")


@beta_api.route("/admin/testers", methods=["GET"])
@require_api_key
def admin_get_testers():
    """Admin endpoint to get all testers (requires admin role)"""
    try:
        tester = request.tester
        if tester.role != UserRole.ADMIN:
            return jsonify({"error": "Admin access required"}), 403

        all_testers = beta_manager.get_all_testers()
        return jsonify(
            {
                "status": "success",
                "data": {
                    "testers": [
                        {
                            "name": t.name,
                            "email": t.email,
                            "role": t.role.value,
                            "access_level": t.access_level,
                            "is_active": t.is_active,
                            "created_at": t.created_at.isoformat(),
                            "last_active": t.last_active.isoformat()
                            if t.last_active
                            else None,
                            "feedback_count": t.feedback_count,
                        }
                        for t in all_testers
                    ]
                },
            }
        )
    except Exception as e:
        logger.error(f"Error getting testers: {e}")
        return jsonify({"error": "Internal server error"}), 500


@beta_api.route("/admin/summary", methods=["GET"])
@require_api_key
def admin_get_summary():
    """Admin endpoint to get beta testing summary (requires admin role)"""
    try:
        tester = request.tester
        if tester.role != UserRole.ADMIN:
            return jsonify({"error": "Admin access required"}), 403

        summary = beta_manager.get_summary()
        return jsonify({"status": "success", "data": summary})
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({"error": "Internal server error"}), 500
