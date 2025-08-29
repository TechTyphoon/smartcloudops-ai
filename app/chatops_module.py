#!/usr/bin/env python3
"""
ChatOps Module for Smart CloudOps AI
Extracted from main.py for modularity
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chatops_bp = Blueprint("chatops", __name__, url_prefix="/chatops")

# Import ChatOps components
try:
    from app.chatops.ai_handler import AIHandler
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
        ai_handler = AIHandler()
        logger.info("ChatOps AI Handler initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ChatOps AI Handler: {e}")
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
            return jsonify({"error": f"Invalid query parameters: {e}"}), 400

        # Process query with AI handler
        try:
            response = ai_handler.process_message(query, data)
            formatted_response = format_response(response)

            return jsonify(
                {
                    "status": "success",
                    "query": query,
                    "response": formatted_response,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return (jsonify({"error": "AI processing failed", "message": str(e)}), 500)

    except Exception as e:
        logger.error(f"ChatOps query error: {e}")
        return (jsonify({"error": "Internal server error", "message": str(e)}), 500)


@chatops_bp.route("/logs", methods=["GET"])
def get_logs():
    """Get recent logs."""
    try:
        hours = request.args.get("hours", 24, type=int)
        level = request.args.get("level", None)

        # Validate parameters
        is_valid, error_msg = validate_query_params(hours=hours, level=level)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        if CHATOPS_AVAILABLE:
            log_retriever = LogRetriever()
            logs = log_retriever.get_recent_logs(hours=hours, level=level)
        else:
            # Fallback logs
            logs = [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "INFO",
                    "message": "ChatOps service not available",
                    "source": "chatops",
                }
            ]

        return jsonify(
            {
                "status": "success",
                "logs": logs,
                "count": len(logs),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        return (jsonify({"error": "Failed to retrieve logs", "message": str(e)}), 500)


@chatops_bp.route("/context", methods=["GET"])
def get_context():
    """Get system context."""
    try:
        if CHATOPS_AVAILABLE:
            context_gatherer = SystemContextGatherer()
            context = context_gatherer.get_system_context()
        else:
            # Fallback context
            context = {
                "status": "unavailable",
                "message": "ChatOps service not available",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return jsonify(
            {
                "status": "success",
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return (
            jsonify({"error": "Failed to retrieve context", "message": str(e)}),
            500,
        )


@chatops_bp.route("/health", methods=["GET"])
def chatops_health():
    """ChatOps health check."""
    try:
        health_status = {
            "status": "healthy" if CHATOPS_AVAILABLE else "unavailable",
            "chatops_available": CHATOPS_AVAILABLE,
            "ai_handler_available": ai_handler is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if CHATOPS_AVAILABLE:
            health_status["components"] = {
                "ai_handler": "available",
                "context_manager": "available",
                "log_retriever": "available",
            }
        else:
            health_status["components"] = {
                "ai_handler": "unavailable",
                "context_manager": "unavailable",
                "log_retriever": "unavailable",
            }

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"ChatOps health check error: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            500,
        )
