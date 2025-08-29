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
        "email": "admin@smartcloudops.ai",
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
    """Verify JWT token and return payload."""
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
        if not auth_header or not auth_header.startswith("Bearer "):
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
                    "password": "use environment variable DEFAULT_ADMIN_PASSWORD",
                },
            }
        )

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        # Check if user exists
        if username not in USERS_DB:
            return jsonify({"error": "Invalid credentials"}), 401

        user = USERS_DB[username]

        # Verify password
        if not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create JWT token
        token = create_jwt_token(username, user["role"])

        logger.info(f"User {username} logged in successfully")

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "username": username,
                        "role": user["role"],
                        "email": user["email"],
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """User logout endpoint."""
    try:
        # In a real application, you might want to blacklist the token
        # For now, we'll just return a success message
        logger.info(f"User {request.user['user_id']} logged out")
        return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "Logout failed"}), 500


@auth_bp.route("/verify", methods=["GET"])
@require_auth
def verify_token():
    """Verify JWT token endpoint."""
    try:
        return (
            jsonify(
                {
                    "message": "Token is valid",
                    "user": {
                        "user_id": request.user["user_id"],
                        "role": request.user["role"],
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({"error": "Token verification failed"}), 500


@auth_bp.route("/refresh", methods=["POST"])
@require_auth
def refresh_token():
    """Refresh JWT token endpoint."""
    try:
        # Create new token with extended expiration
        new_token = create_jwt_token(request.user["user_id"], request.user["role"])

        logger.info(f"Token refreshed for user {request.user['user_id']}")

        return (
            jsonify(
                {
                    "message": "Token refreshed successfully",
                    "token": new_token,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"error": "Token refresh failed"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not username or not password or not email:
            return jsonify({"error": "Username, password, and email required"}), 400

        # Check if user already exists
        if username in USERS_DB:
            return jsonify({"error": "Username already exists"}), 409

        # Create new user
        USERS_DB[username] = {
            "password_hash": generate_password_hash(password),
            "role": "user",
            "email": email,
        }

        logger.info(f"New user registered: {username}")

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": {
                        "username": username,
                        "role": "user",
                        "email": email,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/users", methods=["GET"])
@require_auth
def get_users():
    """Get all users (admin only)."""
    try:
        # Check if user is admin
        if request.user["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403

        # Return user list (without password hashes)
        users = []
        for username, user_data in USERS_DB.items():
            users.append(
                {
                    "username": username,
                    "role": user_data["role"],
                    "email": user_data["email"],
                }
            )

        return jsonify({"users": users}), 200

    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({"error": "Failed to get users"}), 500
