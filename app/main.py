#!/usr/bin/env python3
"""
Smart CloudOps AI - Main Application
Phase 5: Production-Ready ML Integration & Auto-Remediation
"""

import os
import sys
import time

# Add the project root to Python path - MUST be first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import logging

# Security: Input validation utilities
import re
from datetime import datetime
from typing import Any, Dict, Union

from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import create_engine, text

from app.chatops.ai_handler import FlexibleAIHandler
from app.chatops.utils import (
    LogRetriever,
    SystemContextGatherer,
    advanced_context_manager,
    conversation_manager,
    format_response,
    intelligent_query_processor,
    validate_query_params,
)

# Import ML anomaly detection
try:
    from ml_models import AnomalyDetector

    ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML models not available: {e}")
    ML_AVAILABLE = False

# Import Phase 4 remediation components
try:
    from app.remediation.engine import RemediationEngine

    REMEDIATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Remediation components not available: {e}")
    REMEDIATION_AVAILABLE = False

# Import beta testing API
from app.beta_api import beta_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Security: Input validation functions
def validate_string_input(
    value: Any, max_length: int = 1000, allow_empty: bool = False
) -> str:
    """Advanced security validation for string input."""
    if value is None:
        if allow_empty:
            return ""
        raise ValueError("String input cannot be None")

    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    # Remove null bytes and control characters (security)
    value = value.replace("\x00", "").strip()

    if not allow_empty and not value:
        raise ValueError("String input cannot be empty")

    if len(value) > max_length:
        raise ValueError(f"String input too long (max {max_length} characters)")

    # Comprehensive XSS and injection prevention
    dangerous_patterns = [
        r"<script[^>]*>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"onload\s*=",  # Event handlers
        r"onerror\s*=",
        r"onclick\s*=",
        r"eval\s*\(",  # JavaScript eval
        r"document\.cookie",  # Cookie access
        r"window\.location",  # Location manipulation
        r"<iframe[^>]*>",  # Iframe injection
        r"<object[^>]*>",  # Object tags
        r"<embed[^>]*>",  # Embed tags
        r"expression\s*\(",  # CSS expressions
        r"url\s*\(",  # CSS URL injection
        r"@import",  # CSS imports
        r"<link[^>]*>",  # Link tags
        r"<meta[^>]*>",  # Meta tags
        r"<base[^>]*>",  # Base tags
        r"vbscript:",  # VBScript URLs
        r"data:text/html",  # Data URLs
        r"<\?php",  # PHP tags
        r"<%",  # ASP tags
        r"\${",  # Template injection
        r"{{",  # Template injection
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(f"Potentially malicious input detected: {pattern}")

    # SQL injection prevention patterns
    sql_patterns = [
        r"union\s+select",
        r"drop\s+table",
        r"delete\s+from",
        r"insert\s+into",
        r"update\s+set",
        r"exec\s*\(",
        r"sp_executesql",
        r"xp_cmdshell",
        r"--\s*$",  # SQL comments
        r"/\*.*\*/",  # SQL block comments
    ]

    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(f"Potential SQL injection detected: {pattern}")

    return value


def validate_numeric_input(
    value: Any, min_val: float = None, max_val: float = None
) -> Union[int, float]:
    """Validate numeric input for security."""
    if value is None:
        raise ValueError("Numeric input cannot be None")

    if isinstance(value, str):
        try:
            # Try int first, then float
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            raise ValueError(f"Invalid numeric input: {value}")

    if not isinstance(value, (int, float)):
        raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    if min_val is not None and value < min_val:
        raise ValueError(f"Value {value} below minimum {min_val}")

    if max_val is not None and value > max_val:
        raise ValueError(f"Value {value} above maximum {max_val}")

    return value


def validate_json_input(data: Any) -> Dict:
    """Validate JSON input for security."""
    if data is None:
        raise ValueError("JSON input cannot be None")

    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary, got {type(data).__name__}")

    # Prevent deeply nested objects (DoS protection)
    def check_depth(obj, max_depth=10, current_depth=0):
        if current_depth > max_depth:
            raise ValueError(f"JSON nesting too deep (max {max_depth} levels)")

        if isinstance(obj, dict):
            for value in obj.values():
                check_depth(value, max_depth, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, max_depth, current_depth + 1)

    check_depth(data)
    return data


# Create Flask app
app = Flask(__name__)

# Load environment and validated config
from app.config import get_config as _get_config

_env = os.getenv("FLASK_ENV", "development").lower()
_ConfigClass = _get_config(_env)
try:
    _app_config = _ConfigClass.from_env()
except Exception:
    _app_config = {}

# Prometheus metrics
REQUEST_COUNT = Counter(
    "flask_requests_total", "Total Flask HTTP requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "flask_request_duration_seconds", "Flask HTTP request latency"
)

# Phase 3: ML metrics
ML_PREDICTIONS = Counter(
    "ml_predictions_total", "Total ML predictions made", ["model_type"]
)
ML_ANOMALIES = Counter(
    "ml_anomalies_detected", "Total anomalies detected", ["severity"]
)
ML_TRAINING_RUNS = Counter(
    "ml_training_runs_total", "Total model training runs", ["status"]
)

# Phase 4: Remediation metrics
REMEDIATION_ACTIONS = Counter(
    "remediation_actions_total",
    "Total remediation actions executed",
    ["action_type", "severity"],
)
REMEDIATION_SUCCESS = Counter(
    "remediation_success_total", "Successful remediation actions", ["action_type"]
)
REMEDIATION_FAILURE = Counter(
    "remediation_failure_total", "Failed remediation actions", ["action_type", "reason"]
)

# Initialize components
config = _ConfigClass
ai_handler = FlexibleAIHandler()
log_retriever = LogRetriever()
system_gatherer = SystemContextGatherer()

# Initialize ML components
if ML_AVAILABLE:
    anomaly_detector = AnomalyDetector()
    # Try to load existing model
    try:
        anomaly_detector.load_model()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load existing ML model: {e}")
else:
    anomaly_detector = None

# Initialize database connection with production-grade pooling
db_engine = None
if _app_config.get("database_url"):
    try:
        # Production-grade connection pooling configuration
        pool_size = int(os.getenv("DATABASE_POOL_SIZE", "20"))
        max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
        pool_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
        pool_recycle = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

        db_engine = create_engine(
            _app_config["database_url"],
            pool_size=pool_size,  # Base connections
            max_overflow=max_overflow,  # Burst capacity
            pool_timeout=pool_timeout,  # Connection timeout
            pool_recycle=pool_recycle,  # Recycle every hour
            pool_pre_ping=True,  # Health checks
            echo=False,  # Disable SQL logging in prod
            connect_args={
                "connect_timeout": 30,  # Connection timeout
                "command_timeout": 60,  # Command timeout
            },
        )

        # Test connection
        with db_engine.connect() as _conn:
            _conn.execute(text("SELECT 1"))
        logger.info(
            f"Database connection established with pool_size={pool_size}, max_overflow={max_overflow}"
        )

        # Ensure conversations table exists
        with db_engine.begin() as _conn:
            _conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        user_query TEXT NOT NULL,
                        ai_response TEXT,
                        context_json TEXT
                    )
                    """
                )
            )
            logger.info("Ensured conversations table exists")
    except Exception as e:
        logger.warning(f"Database not available: {e}")
        db_engine = None

# Initialize Phase 4 components
if REMEDIATION_AVAILABLE:
    remediation_engine = RemediationEngine(_app_config)
else:
    remediation_engine = None


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()

    if hasattr(request, "start_time"):
        REQUEST_LATENCY.observe(time.time() - request.start_time)

    # Add comprehensive security headers
    if os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true":
        # Content Security Policy
        csp = os.getenv(
            "CONTENT_SECURITY_POLICY",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'",
        )
        response.headers["Content-Security-Policy"] = csp

        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Frame Options
        response.headers["X-Frame-Options"] = os.getenv("X_FRAME_OPTIONS", "DENY")

        # Content Type Options
        response.headers["X-Content-Type-Options"] = os.getenv(
            "X_CONTENT_TYPE_OPTIONS", "nosniff"
        )

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (only for HTTPS)
        if request.is_secure:
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"

        # Feature Policy / Permissions Policy
        response.headers[
            "Permissions-Policy"
        ] = "camera=(), microphone=(), geolocation=()"

        # Cache Control for sensitive endpoints
        if request.endpoint in ["query", "logs", "chatops"]:
            response.headers[
                "Cache-Control"
            ] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

    return response


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Smart CloudOps AI - Flask Application",
            "status": "running",
            "version": "1.0.0-phase4",
            "features": {
                "chatops": True,
                "ml_anomaly_detection": ML_AVAILABLE,
                "auto_remediation": REMEDIATION_AVAILABLE,
            },
            "endpoints": {
                "chatops": ["/query", "/logs", "/chatops/history", "/chatops/clear"],
                "ml_anomaly_detection": [
                    "/anomaly",
                    "/anomaly/batch",
                    "/anomaly/status",
                    "/anomaly/train",
                ],
                "remediation": [
                    "/remediation/status",
                    "/remediation/evaluate",
                    "/remediation/execute",
                    "/remediation/test",
                ],
                "monitoring": ["/status", "/metrics"],
            },
        }
    )


@app.route("/status")
def status():
    return jsonify(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": "running",
            "components": {
                "ai_handler": {"status": "operational"} if ai_handler else None,
                "ml_models": {
                    "available": ML_AVAILABLE,
                    "status": (
                        anomaly_detector.get_system_status()
                        if anomaly_detector
                        else None
                    ),
                },
                "database": {"connected": db_engine is not None},
                "remediation_engine": (
                    remediation_engine.get_status() if remediation_engine else None
                ),
            },
        }
    )


@app.route("/health")
def health():
    """Health check endpoint for monitoring."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0-phase4",
            "checks": {
                "ai_handler": ai_handler is not None,
                "ml_models": ML_AVAILABLE,
                "remediation_engine": REMEDIATION_AVAILABLE,
            },
        }
    )


@app.route("/query", methods=["POST"])
def query():
    """ChatOps query endpoint with AI integration."""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="Missing request data",
                        error="No data provided",
                    )
                ),
                400,
            )

        # Security: Validate JSON input structure
        data = validate_json_input(data)

        query_text = data.get("query", "")
        if not query_text:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="Missing query parameter",
                        error="No query provided",
                    )
                ),
                400,
            )

        # Security: Validate and sanitize query text
        query_text = validate_string_input(query_text, max_length=5000)

        # Validate query parameters
        validate_query_params(data)

        # Get system context
        system_context = system_gatherer.get_system_context()

        # Process query with AI
        response = ai_handler.process_query(query_text, system_context)

        # Return the response with proper formatting
        return jsonify(
            format_response(
                status="success", message="Query processed successfully", data=response
            )
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return (
            jsonify(
                format_response(
                    status="error", message="Query processing failed", error=str(e)
                )
            ),
            500,
        )


@app.route("/logs")
def logs():
    """Retrieve system logs."""
    try:
        # Get query parameters with security validation
        hours = request.args.get("hours", 24)
        hours = validate_numeric_input(hours, min_val=1, max_val=720)  # Max 30 days

        level = request.args.get("level", None)
        if level is not None:
            level = validate_string_input(level, max_length=20)
            # Security: Validate log level is one of expected values
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if level.upper() not in valid_levels:
                return (
                    jsonify(
                        format_response(
                            status="error",
                            message="Invalid log level",
                            error=f"Level must be one of: {', '.join(valid_levels)}",
                        )
                    ),
                    400,
                )

        # Retrieve logs
        log_data = log_retriever.get_recent_logs(hours=hours, level=level)

        return jsonify(
            format_response(
                status="success",
                message=f"Retrieved {len(log_data)} log entries",
                data={"logs": log_data, "count": len(log_data)},
            )
        )

    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        return (
            jsonify(
                format_response(
                    status="error", message="Failed to retrieve logs", error=str(e)
                )
            ),
            500,
        )


@app.route("/chatops/history", methods=["GET"])
def chat_history():
    """Get conversation history."""
    try:
        if not ai_handler:
            return (
                jsonify(
                    format_response(
                        {"error": "AI handler not available"},
                        "error",
                        "ChatOps functionality not available",
                    )
                ),
                503,
            )

        history = ai_handler.get_conversation_history()
        return jsonify(
            format_response(
                {"history": history, "count": len(history)},
                "success",
                "Conversation history retrieved",
            )
        )

    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return (
            jsonify(
                format_response(
                    {"error": str(e)},
                    "error",
                    "Failed to retrieve conversation history",
                )
            ),
            500,
        )


@app.route("/chatops/clear", methods=["POST"])
def clear_history():
    """Clear conversation history."""
    try:
        # Clear AI handler history
        if ai_handler:
            ai_handler.clear_history()

        # Clear conversation manager history
        conversation_manager.conversation_history.clear()

        return jsonify(
            format_response(
                status="success",
                message="Conversation history cleared successfully",
                data={"cleared": True},
            )
        )

    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return (
            jsonify(
                format_response(
                    status="error",
                    message="Failed to clear conversation history",
                    error=str(e),
                )
            ),
            500,
        )


# Phase 5: Advanced ChatOps Endpoints


@app.route("/chatops/context", methods=["GET"])
def get_system_context():
    """Get comprehensive system context for ChatOps."""
    try:
        context = advanced_context_manager.get_system_context()

        return jsonify(
            format_response(
                status="success",
                message="System context retrieved successfully",
                data=context,
            )
        )

    except Exception as e:
        logger.error(f"Error getting system context: {e}")
        return (
            jsonify(
                format_response(
                    status="error", message="Failed to get system context", error=str(e)
                )
            ),
            500,
        )


@app.route("/chatops/analyze", methods=["POST"])
def analyze_query():
    """Analyze a query to determine intent and required context."""
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="Query is required",
                        error="Missing query parameter",
                    )
                ),
                400,
            )

        query = data["query"]
        analysis = intelligent_query_processor.analyze_query(query)

        return jsonify(
            format_response(
                status="success", message="Query analyzed successfully", data=analysis
            )
        )

    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        return (
            jsonify(
                format_response(
                    status="error", message="Failed to analyze query", error=str(e)
                )
            ),
            500,
        )


@app.route("/chatops/smart-query", methods=["POST"])
def smart_query():
    """Enhanced query endpoint with intelligent context gathering."""
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="Query is required",
                        error="Missing query parameter",
                    )
                ),
                400,
            )

        query = data["query"]

        # Analyze query intent
        analysis = intelligent_query_processor.analyze_query(query)

        # Get relevant context
        context = conversation_manager.get_context_for_query(query)

        # Process with AI if available
        ai_response = None
        if ai_handler and ai_handler.provider:
            try:
                # Add context to the query
                enhanced_query = f"{query}\n\nContext: {context['system_summary']}"
                ai_result = ai_handler.process_query(enhanced_query, context)
                ai_response = ai_result.get("response", "AI processing failed")
            except Exception as e:
                logger.warning(f"AI processing failed: {e}")
                ai_response = "AI processing unavailable"
        else:
            ai_response = "AI provider not available"

        # Add to conversation history
        conversation_manager.add_exchange(query, ai_response, context)

        # Persist to database if available
        if db_engine is not None:
            try:
                with db_engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO conversations (user_query, ai_response, context_json)
                            VALUES (:user_query, :ai_response, :context_json)
                            """
                        ),
                        {
                            "user_query": query,
                            "ai_response": ai_response,
                            "context_json": json.dumps(context),
                        },
                    )
            except Exception as e:
                logger.warning(f"Failed to persist conversation: {e}")

        return jsonify(
            format_response(
                status="success",
                message="Smart query processed successfully",
                data={
                    "query": query,
                    "analysis": analysis,
                    "context": context,
                    "response": ai_response,
                },
            )
        )

    except Exception as e:
        logger.error(f"Error processing smart query: {e}")
        return (
            jsonify(
                format_response(
                    status="error",
                    message="Failed to process smart query",
                    error=str(e),
                )
            ),
            500,
        )


@app.route("/chatops/conversation-summary", methods=["GET"])
def get_conversation_summary():
    """Get a summary of the conversation history."""
    try:
        summary = conversation_manager.get_conversation_summary()

        return jsonify(
            format_response(
                status="success",
                message="Conversation summary retrieved successfully",
                data={
                    "summary": summary,
                    "total_exchanges": len(conversation_manager.conversation_history),
                },
            )
        )

    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        return (
            jsonify(
                format_response(
                    status="error",
                    message="Failed to get conversation summary",
                    error=str(e),
                )
            ),
            500,
        )


@app.route("/chatops/system-summary", methods=["GET"])
def get_system_summary():
    """Get a human-readable system summary."""
    try:
        summary = advanced_context_manager.get_context_summary()

        return jsonify(
            format_response(
                status="success",
                message="System summary retrieved successfully",
                data={"summary": summary},
            )
        )

    except Exception as e:
        logger.error(f"Error getting system summary: {e}")
        return (
            jsonify(
                format_response(
                    status="error", message="Failed to get system summary", error=str(e)
                )
            ),
            500,
        )


# Phase 3: ML Anomaly Detection Endpoints


@app.route("/anomaly", methods=["POST"])
def detect_anomaly():
    """Detect anomalies in real-time."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="ML models not available",
                        error="ML functionality disabled",
                    )
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="No data provided",
                        error="Request body is required",
                    )
                ),
                400,
            )

        # Security: Validate JSON input structure
        data = validate_json_input(data)

        metrics = data.get("metrics", {})
        if not metrics:
            return (
                jsonify(
                    format_response(
                        status="error",
                        message="No metrics provided",
                        error="Metrics data is required",
                    )
                ),
                400,
            )

        # Security: Validate metrics values
        try:
            validated_metrics = {}
            for key, value in metrics.items():
                if not isinstance(key, str):
                    raise ValueError(
                        f"Metric key must be string, got {type(key).__name__}"
                    )

                key = validate_string_input(key, max_length=100)
                value = validate_numeric_input(value, min_val=-1e6, max_val=1e6)
                validated_metrics[key] = value

            metrics = validated_metrics
        except ValueError as ve:
            logger.warning(f"Input validation error in anomaly detection: {ve}")
            return (
                jsonify(
                    format_response(
                        status="error", message="Invalid input data", error=str(ve)
                    )
                ),
                400,
            )

        # Detect anomaly
        result = anomaly_detector.detect_anomaly(metrics)

        # Update metrics
        ML_PREDICTIONS.labels(model_type="anomaly_detector").inc()
        if result.get("is_anomaly", False):
            severity = result.get("severity", "unknown")
            ML_ANOMALIES.labels(severity=severity).inc()

        return jsonify(
            format_response(
                status="success", message="Anomaly detection completed", data=result
            )
        )

    except ValueError as ve:
        logger.warning(f"Input validation error in anomaly detection: {ve}")
        return (
            jsonify(
                format_response(
                    status="error", message="Invalid input data", error=str(ve)
                )
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Error detecting anomaly: {e}")
        return (
            jsonify(
                format_response(
                    status="error", message="Anomaly detection failed", error=str(e)
                )
            ),
            500,
        )


@app.route("/anomaly/batch", methods=["POST"])
def batch_detect_anomaly():
    """Detect anomalies in batch."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        metrics_batch = data.get("metrics_batch", [])
        if not metrics_batch:
            return jsonify({"error": "No metrics batch provided"}), 400

        # Batch detect anomalies
        results = anomaly_detector.batch_detect(metrics_batch)

        return jsonify({"results": results, "count": len(results)})

    except Exception as e:
        logger.error(f"Error in batch anomaly detection: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/anomaly/status", methods=["GET"])
def ml_status():
    """Get ML system status."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        status = anomaly_detector.get_system_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting ML status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/anomaly/train", methods=["POST"])
def train_model():
    """Train or retrain the ML model."""
    try:
        if not ML_AVAILABLE:
            return (
                jsonify({"error": "ML models not available", "status": "disabled"}),
                503,
            )

        data = request.get_json() or {}
        force_retrain = data.get("force_retrain", False)

        # Train model
        result = anomaly_detector.train_model(force_retrain=force_retrain)

        # Update metrics
        status = result.get("status", "unknown")
        ML_TRAINING_RUNS.labels(status=status).inc()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({"error": str(e)}), 500


# Phase 4: Auto-Remediation Endpoints


@app.route("/remediation/status", methods=["GET"])
def remediation_status():
    """Get status of the remediation engine."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        status = remediation_engine.get_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting remediation status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remediation/evaluate", methods=["POST"])
def evaluate_anomaly():
    """Evaluate an anomaly and determine if remediation is needed."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        anomaly_score = data.get("anomaly_score", 0.0)
        metrics = data.get("metrics", {})

        if not isinstance(anomaly_score, (int, float)) or not 0 <= anomaly_score <= 1:
            return (
                jsonify({"error": "Invalid anomaly score. Must be between 0 and 1"}),
                400,
            )

        # Evaluate the anomaly
        evaluation = remediation_engine.evaluate_anomaly(anomaly_score, metrics)

        return jsonify(evaluation)

    except Exception as e:
        logger.error(f"Error evaluating anomaly: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remediation/execute", methods=["POST"])
def execute_remediation():
    """Execute remediation based on anomaly evaluation."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Execute remediation
        result = remediation_engine.execute_remediation(data)

        # Update metrics
        if result.get("executed", False):
            execution_results = result.get("execution_results", [])
            for exec_result in execution_results:
                action = exec_result.get("action", {})
                action_type = action.get("action", "unknown")
                severity = data.get("severity", "unknown")

                REMEDIATION_ACTIONS.labels(
                    action_type=action_type, severity=severity
                ).inc()

                if exec_result.get("result", {}).get("status") == "success":
                    REMEDIATION_SUCCESS.labels(action_type=action_type).inc()
                else:
                    reason = exec_result.get("result", {}).get("error", "unknown")
                    REMEDIATION_FAILURE.labels(
                        action_type=action_type, reason=reason
                    ).inc()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error executing remediation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remediation/test", methods=["POST"])
def test_remediation():
    """Test remediation with sample data."""
    try:
        if not REMEDIATION_AVAILABLE:
            return (
                jsonify(
                    {"error": "Remediation engine not available", "status": "disabled"}
                ),
                503,
            )

        # Create test anomaly data
        test_anomaly_score = 0.85  # High severity
        test_metrics = {
            "cpu_usage_avg": 95.0,
            "memory_usage_pct": 88.0,
            "disk_usage_pct": 75.0,
            "network_bytes_total": 500000000,
            "response_time_p95": 2.5,
        }

        # Evaluate anomaly
        evaluation = remediation_engine.evaluate_anomaly(
            test_anomaly_score, test_metrics
        )

        # Execute remediation (if needed)
        if evaluation.get("needs_remediation", False):
            result = remediation_engine.execute_remediation(evaluation)
        else:
            result = {
                "executed": False,
                "reason": "No remediation needed for test data",
                "evaluation": evaluation,
            }

        return jsonify(
            {
                "test_data": {
                    "anomaly_score": test_anomaly_score,
                    "metrics": test_metrics,
                },
                "evaluation": evaluation,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error testing remediation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Bad Request",
                "error": "The request was malformed or invalid",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        400,
    )


@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Unauthorized",
                "error": "Authentication required",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        401,
    )


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Forbidden",
                "error": "Access denied",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        403,
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Not Found",
                "error": "The requested endpoint was not found",
                "timestamp": datetime.now().isoformat(),
                "available_endpoints": {
                    "chatops": [
                        "/query",
                        "/logs",
                        "/chatops/history",
                        "/chatops/clear",
                    ],
                    "ml_anomaly_detection": [
                        "/anomaly",
                        "/anomaly/batch",
                        "/anomaly/status",
                        "/anomaly/train",
                    ],
                    "remediation": [
                        "/remediation/status",
                        "/remediation/evaluate",
                        "/remediation/execute",
                    ],
                    "monitoring": ["/status", "/health", "/metrics"],
                },
            }
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Method Not Allowed",
                "error": f"The {request.method} method is not allowed for this endpoint",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        405,
    )


@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle 429 Rate Limit Exceeded errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Rate Limit Exceeded",
                "error": "Too many requests. Please try again later",
                "timestamp": datetime.now().isoformat(),
                "retry_after": "60 seconds",
            }
        ),
        429,
    )


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal server error: {error}")
    return (
        jsonify(
            {
                "status": "error",
                "message": "Internal Server Error",
                "error": "An unexpected error occurred. Please try again later",
                "timestamp": datetime.now().isoformat(),
                "support": "Check logs for details or contact system administrator",
            }
        ),
        500,
    )


@app.errorhandler(ValueError)
def handle_value_error(error):
    """Handle ValueError exceptions from input validation."""
    logger.warning(f"Input validation error: {error}")
    return (
        jsonify(
            {
                "status": "error",
                "message": "Invalid Input",
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
            }
        ),
        400,
    )


@app.errorhandler(Exception)
def handle_generic_exception(error):
    """Handle any unhandled exceptions."""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return (
        jsonify(
            {
                "status": "error",
                "message": "Service Temporarily Unavailable",
                "error": "An unexpected error occurred. The issue has been logged",
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(request, "id", "unknown"),
            }
        ),
        503,
    )


# Register blueprints
app.register_blueprint(beta_api)  # Add beta testing API


# WSGI application object for Gunicorn
def get_port() -> int:
    """Get standardized port across all environments."""
    port = os.getenv("FLASK_PORT", "3003")
    try:
        return int(port)
    except ValueError:
        logger.warning(f"Invalid port '{port}', using default 3003")
        return 3003


if __name__ == "__main__":
    logger.info("Starting Smart CloudOps AI Flask Application (Phase 4)")
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")  # Changed for container compatibility
    port = get_port()

    logger.info(f"Starting Smart CloudOps AI on {host}:{port}")
    logger.info(f"Environment FLASK_PORT: {os.getenv('FLASK_PORT', 'not set')}")
    app.run(host=host, port=port, debug=debug_mode)
