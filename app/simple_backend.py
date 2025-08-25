#!/usr/bin/env python3
"""
Simple Backend for SmartCloudOps AI Frontend
Provides basic API endpoints to fix frontend connection issues
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random
import time

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    )


@app.route("/system/health")
def system_health():
    """System health endpoint for monitoring page."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": [
                {"name": "Database", "status": "healthy", "response_time": 45},
                {"name": "API Gateway", "status": "healthy", "response_time": 12},
                {"name": "ML Service", "status": "healthy", "response_time": 78},
                {"name": "Monitoring", "status": "healthy", "response_time": 23},
            ],
        }
    )


@app.route("/system/metrics")
def system_metrics():
    """System metrics endpoint for monitoring page."""
    return jsonify(
        {
            "cpu_usage": random.uniform(20, 80),
            "memory_usage": random.uniform(30, 90),
            "disk_usage": random.uniform(40, 85),
            "network_io": {
                "bytes_sent": random.randint(1000000, 5000000),
                "bytes_recv": random.randint(2000000, 8000000),
            },
            "system_status": "healthy",
            "services": [
                {"name": "web-server", "status": "running", "uptime": 86400},
                {"name": "database", "status": "running", "uptime": 172800},
                {"name": "cache", "status": "running", "uptime": 43200},
            ],
        }
    )


@app.route("/api/chatops", methods=["POST"])
def chatops():
    """ChatOps endpoint for AI chat interface."""
    data = request.get_json()
    query = data.get("query", "")

    # Simple AI response simulation
    responses = [
        "I can help you with that! Let me check the system status.",
        "Based on the current metrics, everything looks good.",
        "I've analyzed your request and here's what I found.",
        "The system is operating within normal parameters.",
        "I can assist you with monitoring and remediation tasks.",
    ]

    return jsonify(
        {
            "id": str(int(time.time())),
            "content": random.choice(responses),
            "role": "assistant",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/api/anomalies")
def anomalies():
    """Anomalies endpoint."""
    return jsonify(
        [
            {
                "id": "1",
                "type": "high_cpu",
                "severity": "medium",
                "status": "active",
                "service": "web-server",
                "timestamp": datetime.utcnow().isoformat(),
                "description": "CPU usage above normal threshold",
            },
            {
                "id": "2",
                "type": "memory_leak",
                "severity": "low",
                "status": "active",
                "service": "database",
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Gradual memory increase detected",
            },
        ]
    )


@app.route("/api/anomalies/<id>/acknowledge", methods=["POST"])
def acknowledge_anomaly(id):
    """Acknowledge an anomaly."""
    return jsonify({"message": "Anomaly {id} acknowledged"})


@app.route("/api/anomalies/<id>/resolve", methods=["POST"])
def resolve_anomaly(id):
    """Resolve an anomaly."""
    return jsonify({"message": "Anomaly {id} resolved"})


@app.route("/api/anomalies/<id>/dismiss", methods=["POST"])
def dismiss_anomaly(id):
    """Dismiss an anomaly."""
    return jsonify({"message": "Anomaly {id} dismissed"})


@app.route("/api/remediation/actions")
def remediation_actions():
    """Remediation actions endpoint."""
    return jsonify(
        [
            {
                "id": "1",
                "type": "scale_up",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Scaled up CPU resources",
            },
            {
                "id": "2",
                "type": "restart_service",
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat(),
                "description": "Restart web service",
            },
        ]
    )


@app.route("/auth/login", methods=["POST"])
def login():
    """Simple login endpoint."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # Simple authentication
    if username == "admin" and password == "admin123":
        return jsonify(
            {
                "token": "fake-jwt-token",
                "user": {"id": 1, "username": "admin", "role": "admin"},
            }
        )
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/auth/logout", methods=["POST"])
def logout():
    """Logout endpoint."""
    return jsonify({"message": "Logged out successfully"})


if __name__ == "__main__":
    print("Starting Simple SmartCloudOps AI Backend...")
    print("Frontend should now be able to connect!")
    app.run(host="0.0.0.0", port=8000, debug=True)
