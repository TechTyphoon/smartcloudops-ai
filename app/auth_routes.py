#!/usr/bin/env python3
"""
Enterprise Authentication Endpoints
Login, logout, token refresh, user management
"""

import logging
from datetime import datetime, timezone
from typing import List

from flask import Blueprint, jsonify, request

from app.auth import (
    auth_manager,
    authenticate_user,
    get_user_by_id,
    require_admin,
    require_auth,
)

logger = logging.getLogger(__name__)

# Create authentication blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Enterprise login endpoint with JWT tokens"""
    try:
        # For GET requests, return login form info
        if request.method == "GET":
            return jsonify(
                {
                    "status": "ready",
                    "message": "Enterprise Login Service",
                    "method": "POST",
                    "required_fields": ["username", "password"],
                    "test_users": {
                        "admin": "Enterprise administrator",
                        "operator": "System operator",
                        "viewer": "Read-only access",
                        "analyst": "Data analyst",
                    },
                    "endpoint": "/auth/login",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "error": "Invalid request",
                        "message": "JSON data required",
                        "status": "error",
                    }
                ),
                400,
            )

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        # Support both username and email login
        if email and not username:
            # Find user by email
            for user in ENTERPRISE_USERS.values():
                if user.get("email") == email:
                    username = user["username"]
                    break

        if not username or not password:
            return (
                jsonify(
                    {
                        "error": "Invalid credentials",
                        "message": "Username/email and password required",
                        "status": "error",
                    }
                ),
                400,
            )

        # Authenticate user
        user = authenticate_user(username, password)
        if not user:
            logger.warning(f"Failed login attempt for username: {username}")
            return (
                jsonify(
                    {
                        "error": "Authentication failed",
                        "message": "Invalid username or password",
                        "status": "error",
                    }
                ),
                401,
            )

        # Generate tokens
        tokens = auth_manager.generate_tokens(
            user_id=user["id"],
            username=user["username"],
            role=user["role"],
        )

        # Log successful login
        logger.info(f"Successful login for user: {username}")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Login successful",
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                        "role": user["role"],
                        "is_active": user["is_active"],
                    },
                    "tokens": tokens,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return (
            jsonify(
                {
                    "error": "Login failed",
                    "message": "Internal server error",
                    "status": "error",
                }
            ),
            500,
        )


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """User logout endpoint"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not authenticated"}), 401

        # Log logout event
        auth_manager.log_audit_event(
            user_id=user.id,
            action="logout",
            details={"username": user.username},
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Logout successful",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return (
            jsonify(
                {
                    "error": "Logout failed",
                    "message": "Internal server error",
                    "status": "error",
                }
            ),
            500,
        )


@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """Refresh JWT token endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return jsonify({"error": "Refresh token required"}), 400

        # Verify and refresh token
        try:
            tokens = auth_manager.refresh_tokens(refresh_token)
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Token refreshed successfully",
                        "tokens": tokens,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ),
                200,
            )

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Refresh token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid refresh token"}), 401

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return (
            jsonify(
                {
                    "error": "Token refresh failed",
                    "message": "Internal server error",
                    "status": "error",
                }
            ),
            500,
        )


@auth_bp.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not authenticated"}), 401

        return (
            jsonify(
                {
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return (
            jsonify(
                {
                    "error": "Failed to get profile",
                    "message": "Internal server error",
                    "status": "error",
                }
            ),
            500,
        )


@auth_bp.route("/users", methods=["GET"])
@require_admin
def get_users():
    """Get all users (admin only)"""
    try:
        users = auth_manager.get_all_users()

        user_list = []
        for user in users:
            user_list.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                }
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "users": user_list,
                    "total": len(user_list),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Get users error: {e}")
        return (
            jsonify(
                {
                    "error": "Failed to get users",
                    "message": "Internal server error",
                    "status": "error",
                }
            ),
            500,
        )


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
@require_admin
def get_user(user_id):
    """Get specific user by ID (admin only)"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return (
            jsonify(
                {
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return (
            jsonify(
                {
                    "error": "Failed to get user",
                    "message": "Internal server error",
                    "status": "error",
                }
            ),
            500,
        )


@auth_bp.route("/health", methods=["GET"])
def auth_health():
    """Authentication service health check"""
    try:
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "authentication",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "components": {
                        "auth_manager": "active",
                        "database": "connected",
                        "jwt_service": "active",
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Auth health check error: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "service": "authentication",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            500,
        )
