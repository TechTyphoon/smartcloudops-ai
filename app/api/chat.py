#!/usr/bin/env python3
"""
SmartCloudOps AI - ChatOps API Endpoint
AI-powered chat interface for operational assistance
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.route("/query", methods=["POST"])
def process_chat_query():
    """
    Process user chat queries and return AI responses
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400

        data = request.get_json()

        if not data or "query" not in data:
            return (
                jsonify(
                    {"status": "error", "message": "Missing 'query' field in request"}
                ),
                400,
            )

        query = data["query"]

        if not query or not query.strip():
            return jsonify({"status": "error", "message": "Query cannot be empty"}), 400

        # Process query through AI handler
        try:
            from app.ai_handler import AIHandler

            ai_handler = AIHandler()
            response = ai_handler.process_query(query)

            return jsonify(
                {
                    "status": "success",
                    "response": response.get(
                        "response", "I'm sorry, I couldn't process your query."
                    ),
                    "suggestions": response.get("suggestions", []),
                    "confidence": response.get("confidence", 0.0),
                    "query_type": response.get("query_type", "general"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        except ImportError:
            logger.error("AI handler not available")
            return (
                jsonify(
                    {"status": "error", "message": "AI service temporarily unavailable"}
                ),
                503,
            )

        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return (
                jsonify({"status": "error", "message": "Failed to process query"}),
                500,
            )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@chat_bp.route("/health", methods=["GET"])
def chat_health():
    """
    Health check for chat service
    """
    try:
        # Check if AI handler is available
        from app.ai_handler import AIHandler

        AIHandler()

        return jsonify(
            {
                "status": "healthy",
                "service": "chat",
                "ai_handler_available": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except ImportError:
        return jsonify(
            {
                "status": "degraded",
                "service": "chat",
                "ai_handler_available": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Chat health check error: {e}")
        return jsonify(
            {
                "status": "unhealthy",
                "service": "chat",
                "ai_handler_available": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


@chat_bp.route("/history", methods=["GET"])
def get_chat_history():
    """
    Get chat history for the current session
    """
    try:
        # Get query parameters
        limit = request.args.get("limit", 50, type=int)
        session_id = request.args.get("session_id")

        # TODO: Implement chat history retrieval
        # For now, return empty history
        return jsonify(
            {
                "status": "success",
                "data": {
                    "history": [],
                    "session_id": session_id,
                    "limit": limit,
                },
            }
        )

    except Exception as e:
        logger.error(f"Chat history error: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to get chat history"}),
            500,
        )


@chat_bp.route("/clear", methods=["POST"])
def clear_chat_history():
    """
    Clear chat history for the current session
    """
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")

        # TODO: Implement chat history clearing
        # For now, return success
        return jsonify(
            {
                "status": "success",
                "message": "Chat history cleared successfully",
                "session_id": session_id,
            }
        )

    except Exception as e:
        logger.error(f"Clear chat history error: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to clear chat history"}),
            500,
        )
