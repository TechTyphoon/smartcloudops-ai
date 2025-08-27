#!/usr/bin/env python3
"""
Authentication Module for Smart CloudOps AI
Extracted from main.py for modularity
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Get admin password from environment
DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD")
if not DEFAULT_ADMIN_PASSWORD:
    raise ValueError("DEFAULT_ADMIN_PASSWORD environment variable is required")

# In-memory user store (replace with database in production)
USERS_DB = {
    "admin": {
        "password_hash": generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        "role": "admin",
        "email": "admin@smartcloudops.ai"
    }
}


def create_jwt_token(user_id: str, role: str) -> str:
    """Create JWT token for user."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[Dict]:
    "Verify JWT token and return payload."
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None
def require_auth(f):
    """Decorator to require authentication."""

    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer"):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.split(" ")[1]
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = payload
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login endpoint."""
    if request.method == "GET":
        return jsonify(
            {
                "message": "Login endpoint",
                "method": "POST",
                "required_fields": ["username", "password"],
                "example": {
                    "username": "admin",
                    "password": "use environment variable DEFAULT_ADMIN_PASSWORD"
                },
            }
        )

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        # Validate user
        user = USERS_DB.get(username)
        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create token
        token = create_jwt_token(username, user["role"])

        return jsonify(
            {
                "status": "success",
                "message": "Login successful",
                "token": token,
                "user": {
                    "username": username,
                    "role": user["role"],
                    "email": user["email"],
                },
                "expires_in": JWT_EXPIRATION_HOURS * 3600,
            }
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/profile", methods=["GET"])
@require_auth
def profile():
    "Get user profile."
    try:
        user_id = request.user["user_id"]
        user = USERS_DB.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify()
            {}
                "status": "success",
                "user": {}
                    "username": user_id,
                    "role": user["role"],
                    "email": user["email"],
                },
            }
        )

    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    "User logout endpoint."
    # In a real implementation, you might blacklist the token
    return jsonify({"status": "success", "message": "Logout successful"})


@auth_bp.route("/register", methods=["POST"])
def register():
    "User registration endpoint (disabled in production)."
    return ()
        jsonify()
            {}
                "error": "Registration disabled in production",
                "message": "Contact administrator for account creation"
            }
        ),
        403)
