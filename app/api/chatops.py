from datetime import datetime

from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.chatops.gpt_handler import GPTHandler

chatops_bp = Blueprint("chatops", __name__)


@chatops_bp.route("", methods=["POST"])
@chatops_bp.route("/query", methods=["POST"])
@require_auth
def query_chatops():
    """ChatOps query endpoint with GPT integration."""
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "").strip()
    context = payload.get("context", {})

    # Validate query length
    if len(query) > 1000:
        return (
            jsonify(
                {
                    "error": "Query too long. Maximum 1000 characters allowed.",
                    "status": "error",
                }
            ),
            400,
        )

    if not query:
        return jsonify({"error": "No query provided", "status": "error"}), 400

    try:
        # Initialize GPT handler
        handler = GPTHandler()

        # Process the query
        result = handler.process_query(query, context)

        # Check if GPT handler returned an error
        if result.get("status") == "error":
            return (
                jsonify(
                    {
                        "error": result.get("error", "Processing failed"),
                        "status": "error",
                    }
                ),
                500,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "response": result.get("response", ""),
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "model": "gpt-4",
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e), "status": "error"}), 400
    except Exception as e:
        return (
            jsonify({"error": f"Internal server error: {str(e)}", "status": "error"}),
            500,
        )
