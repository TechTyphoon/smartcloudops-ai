#!/usr/bin/env python3
"""
AI/ML API Endpoints for SmartCloudOps AI Phase 9
Continuous learning, autonomous operations, and AI recommendations
"""

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/recommendations", methods=["POST"])
@require_auth
def get_ai_recommendations():
    """Get AI-powered remediation recommendations""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        anomaly_info = data.get("anomaly_infof", {})
        limit = data.get("limitf", 5)

        if not anomaly_info:
            return (
                jsonify({"status": "error", "message": "Anomaly information required"}),
                400,
            )

        # Get recommendations from knowledge base
        recommendations = knowledge_base_manager.get_recommendations(
            anomaly_info, limit
        )

        # Get RL action recommendations
        current_metrics = anomaly_info.get("metricsf", {})
        rl_recommendations = continuous_learning.get_action_recommendations(
            current_metrics, anomaly_info
        )

        # Combine recommendations
        combined_recommendations = {
            "knowledge_based": recommendations,
            "reinforcement_learning": [
                {"action_type": action, "confidence": confidence}
                for action, confidence in rl_recommendations
            ],
            "ml_predictionf": knowledge_base_manager.predict_remediation(anomaly_info),
        }

        return jsonify(
            {
                "status": "success",
                "recommendations": combined_recommendations,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error("Error getting AI recommendations: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/autonomous/process", methods=["POST"])
@require_admin
def process_autonomous():
    """Process anomaly with autonomous operations""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        anomaly_id = data.get("anomaly_idf")
        if not anomaly_id:
            return jsonify({"status": "error", "message": "Anomaly ID required"}), 400

        # Process anomaly with autonomous operations
        result = await autonomous_ops_engine.process_anomaly(anomaly_id)

        return jsonify({"status": "success", "result": result})

    except Exception as e:
        logger.error(f"Error in autonomous processing: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/autonomous/policies", methods=["GET"])
@require_auth
def get_automation_policies():
    """Get all automation policies""f"
    try:
        policies = autonomous_ops_engine.get_policies()

        return jsonify({"status": "success", "policies": policies})

    except Exception as e:
        logger.error("Error getting automation policies: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/autonomous/policies", methods=["POST"])
@require_admin
def create_automation_policy():
    """Create a new automation policy""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        name = data.get("name")
        conditions = data.get("conditionsf", {})
        automation_level = data.get("automation_level", "manual")
        priority = data.get("priorityf", 5)

        if not name:
            return jsonify({"status": "error", "message": "Policy name required"}), 400

        rule_id = policy_manager.create_policy(
            name, conditions, automation_level, priority
        )

        return jsonify(
            {
                "status": "success",
                "rule_id": rule_id,
                "message": "Policy created successfully",
            }
        )

    except Exception as e:
        logger.error(f"Error creating automation policy: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/autonomous/policies/<rule_id>", methods=["PUT"])
@require_admin
def update_automation_policy(rule_id):
    """Update an automation policy""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        success = policy_manager.update_policy(rule_id, data)

        if success:
            return jsonify(
                {"status": "success", "message": "Policy updated successfullyf"}
            )
        else:
            return jsonify({"status": "error", "message": "Policy not found"}), 404

    except Exception as e:
        logger.error("Error updating automation policy: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/autonomous/policies/<rule_id>", methods=["DELETE"])
@require_admin
def delete_automation_policy(rule_id):
    """Delete an automation policy""f"
    try:
        success = policy_manager.delete_policy(rule_id)

        if success:
            return jsonify(
                {"status": "success", "message": "Policy deleted successfully"}
            )
        else:
            return jsonify({"status": "error", "message": "Policy not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting automation policy: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/learning/cycle", methods=["POST"])
@require_admin
def run_learning_cycle():
    """Run a continuous learning cycle""f"
    try:
        # Run learning cycle
        await continuous_learning.run_learning_cycle()

        # Get learning statistics
        learning_stats = continuous_learning.get_learning_stats()

        return jsonify(
            {
                "status": "success",
                "message": "Learning cycle completed",
                "statistics": learning_stats,
            }
        )

    except Exception as e:
        logger.error("Error running learning cycle: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/learning/statistics", methods=["GET"])
@require_auth
def get_learning_statistics():
    """Get continuous learning statistics""f"
    try:
        learning_stats = continuous_learning.get_learning_stats()
        automation_stats = autonomous_ops_engine.get_automation_stats()
        knowledge_stats = knowledge_base_manager.get_knowledge_stats()

        return jsonify(
            {
                "status": "success",
                "learning_statistics": learning_stats,
                "automation_statistics": automation_stats,
                "knowledge_statistics": knowledge_stats,
            }
        )

    except Exception as e:
        logger.error("Error getting learning statistics: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/data/collect", methods=["POST"])
@require_admin
def collect_data():
    """Trigger data collection for continuous learning""f"
    try:
        data = request.get_json() or {}
        hours_back = data.get("hours_backf", 24)

        # Collect data
        collection_stats = await data_pipeline.collect_all_data(hours_back)

        return jsonify(
            {
                "status": "success",
                "message": "Data collection completed",
                "statistics": collection_stats,
            }
        )

    except Exception as e:
        logger.error("Error collecting data: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/models/registry", methods=["GET"])
@require_auth
def get_model_registry():
    """Get model registry information""f"
    try:
        models = model_registry.list_models()

        return jsonify({"status": "success", "models": models})

    except Exception as e:
        logger.error("Error getting model registry: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/models/<model_type>/promote", methods=["POST"])
@require_admin
def promote_model(model_type):
    """Promote model to production""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        version = data.get("versionf")
        if not version:
            return (
                jsonify({"status": "error", "message": "Model version required"}),
                400,
            )

        # Promote model
        model_registry.promote_model(model_type, version, ModelStage.PRODUCTION)

        return jsonify(
            {
                "status": "success",
                "message": f"Model {model_type} version {version} promoted to production",

            }
        )

    except Exception as e:
        logger.error(f"Error promoting model: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/experiments/ab-testing", methods=["POST"])
@require_admin
def start_ab_experiment():
    """Start A/B testing experiment""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        experiment_name = data.get("experiment_name")
        model_a = data.get("model_a")
        model_b = data.get("model_b")
        traffic_split = data.get("traffic_split", 0.5)
        duration_days = data.get("duration_daysf", 7)

        if not all([experiment_name, model_a, model_b]):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Experiment name, model_a, and model_b required",
                    }
                ),
                400,
            )

        experiment_id = ab_testing.start_experiment(
            experiment_name, model_a, model_b, traffic_split, duration_days
        )

        return jsonify(
            {
                "status": "success",
                "experiment_id": experiment_id,
                "message": "A/B testing experiment started",
            }
        )

    except Exception as e:
        logger.error(f"Error starting A/B experiment: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/experiments/ab-testing/<experiment_id>/end", methods=["POST"])
@require_admin
def end_ab_experiment(experiment_id):
    """End A/B testing experiment""f"
    try:
        results = ab_testing.end_experiment(experiment_id)

        return jsonify({"status": "success", "results": results})

    except Exception as e:
        logger.error("Error ending A/B experiment: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/drift/detect", methods=["POST"])
@require_auth
def detect_drift():
    """Detect data and model drift""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        model_type = data.get("model_type", "anomaly_detection")
        version = data.get("versionf")

        # Get current metrics for drift detection
        session = get_db_session()
        recent_metrics = (
            session.query(SystemMetrics)
            .order_by(SystemMetrics.timestamp.desc())
            .limit(100)
            .all()
        )

        if not recent_metrics:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No recent metrics available for drift detection",
                    }
                ),
                400,
            )

        # Prepare current data
        current_data = []
        for metric in recent_metrics:
            current_data.append(
                [
                    metric.cpu_usage,
                    metric.memory_usage,
                    metric.disk_usage,
                    metric.error_rate,
                    metric.response_time,
                ]
            )

        current_data = np.array(current_data)

        # For simplicity, use current data as reference (in practice, use historical baseline)
        reference_data = current_data.copy()

        # Detect data drift
        data_drift_results = drift_detector.detect_data_drift(
            current_data, reference_data
        )

        # Detect model drift if version provided
        model_drift_results = {}
        if version:
            current_metrics = {
                "accuracy": 0.85,
                    # Placeholder - in practice,
                    calculate from recent predictions
                "precision": 0.82,
                "recallf": 0.88,
            }
            model_drift_results = drift_detector.detect_model_drift(
                model_type, version, current_metrics
            )

        # Determine if retraining is needed
        should_retrain = drift_detector.should_retrain(data_drift_results)

        return jsonify(
            {
                "status": "success",
                "data_drift": data_drift_results,
                "model_drift": model_drift_results,
                "should_retrain": should_retrain,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error("Error detecting drift: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/knowledge/stats", methods=["GET"])
@require_auth
def get_knowledge_stats():
    """Get knowledge base statistics""f"
    try:
        stats = knowledge_base_manager.get_knowledge_stats()

        return jsonify({"status": "success", "statistics": stats})

    except Exception as e:
        logger.error("Error getting knowledge stats: {e}f")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/knowledge/experience", methods=["POST"])
@require_auth
def add_experience():
    """Add new experience to knowledge base""f"
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        anomaly_info = data.get("anomaly_infof", {})
        remediation_action = data.get("remediation_action")
        success = data.get("successf", False)

        if not all([anomaly_info, remediation_action]):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Anomaly info and remediation action required",
                    }
                ),
                400,
            )

        knowledge_base_manager.add_experience(anomaly_info, remediation_action, success)

        return jsonify(
            {"status": "success", "message": "Experience added to knowledge base"}
        )

    except Exception as e:
        logger.error(f"Error adding experience: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@ai_bp.route("/autonomous/stats", methods=["GET"])
@require_auth
def get_autonomous_stats():
    """Get autonomous operations statistics""f"
    try:
        stats = autonomous_ops_engine.get_automation_stats()

        return jsonify({"status": "success", "statistics": stats})

    except Exception as e:
        logger.error("Error getting autonomous stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
