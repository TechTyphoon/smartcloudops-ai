#!/usr/bin/env python3
"""
ChatOps Module for Smart CloudOps AI
Extracted from main.py for modularity
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chatops_bp = Blueprint("chatops", __name__, url_prefix="/chatops")

# Import ChatOps components
try:
    from app.chatops.utils import (
        LogRetriever,
        SystemContextGatherer,
        conversation_manager,
        format_response,
        validate_query_params,
    )

    CHATOPS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ChatOps components not available: {e}")
    CHATOPS_AVAILABLE = False

# Initialize ChatOps components
ai_handler = None
if CHATOPS_AVAILABLE:
    try:
        ai_handler = FlexibleAIHandler()
        logger.info("ChatOps AI Handler initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize ChatOps AI Handler: {e}")
        CHATOPS_AVAILABLE = False


@chatops_bp.route("/query", methods=["GET", "POST"])
def chatops_query():
    """ChatOps query endpoint."""
    if request.method == "GET":
        return jsonify(
            {
                "status": "success",
                "message": "ChatOps Query Service",
                "chatops_available": CHATOPS_AVAILABLE,
                "endpoints": {
                    "query": "POST /chatops/query",
                    "logs": "GET /chatops/logs",
                    "context": "GET /chatops/context",
                },
            }
        )

    try:
        if not CHATOPS_AVAILABLE or not ai_handler:
            return (
                jsonify(
                    {
                        "error": "ChatOps service not available",
                        "message": "AI handler not loaded",
                    }
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        query = data.get("query", "")
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Validate query parameters
        try:
            validate_query_params(data)
        except ValueError as e:
            return jsonify({"error": "Invalid query parameters: {e}"}), 400

        # Process query with AI handler
        try:
            response = ai_handler.process_query(query, data)
            formatted_response = format_response(response)

            return jsonify(
                {
                    "status": "success",
                    "query": query,
                    "response": formatted_response,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error("AI processing error: {e}")
            return (
                jsonify(
                    {
                        "error": "AI processing failed",
                        "message": "Unable to process query with AI",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error("ChatOps query error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@chatops_bp.route("/logs", methods=["GET"])
def get_chatops_logs():
    """Get ChatOps logs endpoint."""
    try:
        if not CHATOPS_AVAILABLE:
            return (
                jsonify(
                    {
                        "error": "ChatOps service not available",
                        "message": "Log retrieval not available",
                    }
                ),
                503,
            )

        # Get logs using LogRetriever
        try:
            log_retriever = LogRetriever()
            logs = log_retriever.get_recent_logs(limit=50)

            return jsonify(
                {
                    "status": "success",
                    "logs": logs,
                    "count": len(logs),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error("Log retrieval error: {e}")
            return (
                jsonify(
                    {
                        "error": "Log retrieval failed",
                        "message": "Unable to retrieve logs",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error("ChatOps logs error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@chatops_bp.route("/context", methods=["GET"])
def get_system_context():
    """Get system context endpoint."""
    try:
        if not CHATOPS_AVAILABLE:
            return (
                jsonify(
                    {
                        "error": "ChatOps service not available",
                        "message": "Context retrieval not available",
                    }
                ),
                503,
            )

        # Get system context using SystemContextGatherer
        try:
            context_gatherer = SystemContextGatherer()
            context = context_gatherer.get_system_context()

            return jsonify(
                {
                    "status": "success",
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error("Context retrieval error: {e}")
            return (
                jsonify(
                    {
                        "error": "Context retrieval failed",
                        "message": "Unable to retrieve system context",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error("System context error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@chatops_bp.route("/conversation", methods=["GET", "POST"])
def manage_conversation():
    """Manage conversation endpoint."""
    if request.method == "GET":
        return jsonify(
            {
                "status": "success",
                "message": "Conversation Management",
                "endpoints": {
                    "get_conversation": "GET /chatops/conversation",
                    "add_message": "POST /chatops/conversation",
                },
            }
        )

    try:
        if not CHATOPS_AVAILABLE:
            return (
                jsonify(
                    {
                        "error": "ChatOps service not available",
                        "message": "Conversation management not available",
                    }
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        message = data.get("message", "")
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Add message to conversation
        try:
            conversation_manager.add_message(message)

            return jsonify(
                {
                    "status": "success",
                    "message": "Message added to conversation",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error("Conversation management error: {e}")
            return (
                jsonify(
                    {
                        "error": "Conversation management failed",
                        "message": "Unable to add message to conversation",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error("Conversation error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@chatops_bp.route("/status", methods=["GET"])
def chatops_status():
    """ChatOps service status endpoint."""
    try:
        status = {
            "status": "success",
            "chatops_available": CHATOPS_AVAILABLE,
            "ai_handler_loaded": ai_handler is not None,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "query": "/chatops/query",
                "logs": "/chatops/logs",
                "context": "/chatops/context",
                "conversation": "/chatops/conversation",
                "status": "/chatops/status",
            },
        }

        if CHATOPS_AVAILABLE and ai_handler:
            status["ai_provider"] = ai_handler.current_provider
            status["model_info"] = {
                "provider": ai_handler.current_provider,
                "model": ai_handler.current_model,
            }

        return jsonify(status)

    except Exception as e:
        logger.error("ChatOps status error: {e}")
        return jsonify({"error": "Internal server error"}), 500
