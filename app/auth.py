#!/usr/bin/env python3
"""
Enterprise Authentication & Authorization System
JWT-based authentication with role-based access control
"""

import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
import redis
from flask import current_app, jsonify, request

logger = logging.getLogger(__name__)

# Redis client for token blacklisting
try:
    # Try Docker service name first, then localhost
    redis_host = os.getenv("REDIS_HOST", "redis-cache-server")
    redis_client = redis.Redis(host=redis_host, port=6379, db=1, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info(f"✅ Redis connected: {redis_host}:6379")
except Exception as e:
    redis_client = None
    logger.warning(f"⚠️ Redis not available for token blacklisting: {e}")


class AuthManager:
    """Enterprise-grade authentication and authorization manager"""

    def __init__(self, secret_key, algorithm="HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry = timedelta(hours=24)  # Enterprise: 24-hour sessions
        self.refresh_expiry = timedelta(days=7)  # 7-day refresh tokens

        # Enterprise user roles and permissions
        self.roles = {
            "admin": {
                "permissions": ["read", "write", "admin", "ml_train", "system_config"],
                "description": "Full system access",
            },
            "operator": {
                "permissions": ["read", "write", "ml_query"],
                "description": "Operations and monitoring",
            },
            "viewer": {"permissions": ["read"], "description": "Read-only access"},
            "analyst": {
                "permissions": ["read", "ml_query", "ml_train"],
                "description": "ML analysis and training",
            },
        }

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt (enterprise security standard)"""
        salt = bcrypt.gensalt(rounds=12)  # High cost factor for enterprise
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def generate_tokens(
        self, user_id: str, username: str, role: str, tenant_id: str = None
    ) -> dict:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()

        # Access token payload
        access_payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "tenant_id": tenant_id,
            "permissions": self.roles.get(role, {}).get("permissions", []),
            "iat": now,
            "exp": now + self.token_expiry,
            "type": "access",
        }

        # Refresh token payload
        refresh_payload = {
            "user_id": user_id,
            "username": username,
            "iat": now,
            "exp": now + self.refresh_expiry,
            "type": "refresh",
        }

        access_token = jwt.encode(
            access_payload, self.secret_key, algorithm=self.algorithm
        )
        refresh_token = jwt.encode(
            refresh_payload, self.secret_key, algorithm=self.algorithm
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(self.token_expiry.total_seconds()),
            "role": role,
            "permissions": access_payload["permissions"],
        }

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            # Check if token is blacklisted
            if redis_client and redis_client.get(f"blacklist:{token}"):
                raise jwt.InvalidTokenError("Token has been revoked")

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token hasn't expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise jwt.ExpiredSignatureError("Token has expired")

            return payload

        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    def revoke_token(self, token: str):
        """Blacklist a token (enterprise logout/security)"""
        if redis_client:
            try:
                payload = jwt.decode(
                    token,
                    self.secret_key,
                    algorithms=[self.algorithm],
                    options={"verify_exp": False},
                )
                exp_time = datetime.fromtimestamp(payload["exp"])
                ttl = int((exp_time - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    redis_client.setex(f"blacklist:{token}", ttl, "revoked")
            except Exception as e:
                logger.error(f"Error revoking token: {e}")

    def has_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        user_permissions = self.roles.get(user_role, {}).get("permissions", [])
        return required_permission in user_permissions or "admin" in user_permissions


# Global auth manager instance
auth_manager = AuthManager(secret_key="your-super-secret-enterprise-key-change-this")


def require_auth(required_permission: str = None):
    """Decorator to require authentication and optional permission"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None

            # Get token from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            # Get token from query parameter (for WebSocket/SSE)
            if not token:
                token = request.args.get("token")

            if not token:
                return (
                    jsonify(
                        {
                            "error": "Authentication required",
                            "message": "Access token missing",
                            "status": "unauthorized",
                        }
                    ),
                    401,
                )

            try:
                payload = auth_manager.verify_token(token)

                # Check permission if required
                if required_permission:
                    user_role = payload.get("role", "viewer")
                    if not auth_manager.has_permission(user_role, required_permission):
                        return (
                            jsonify(
                                {
                                    "error": "Permission denied",
                                    "message": f"Requires {required_permission} permission",
                                    "status": "forbidden",
                                }
                            ),
                            403,
                        )

                # Add user context to request
                request.user = {
                    "id": payload["user_id"],
                    "username": payload["username"],
                    "role": payload["role"],
                    "tenant_id": payload.get("tenant_id"),
                    "permissions": payload.get("permissions", []),
                }

            except jwt.InvalidTokenError as e:
                return (
                    jsonify(
                        {
                            "error": "Authentication failed",
                            "message": str(e),
                            "status": "unauthorized",
                        }
                    ),
                    401,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_admin(f):
    """Decorator to require admin role"""
    return require_auth("admin")(f)


def require_operator(f):
    """Decorator to require operator or admin role"""
    return require_auth("write")(f)


def require_ml_access(f):
    """Decorator to require ML access"""
    return require_auth("ml_query")(f)


# Enterprise user management (in-memory for now, move to database later)
ENTERPRISE_USERS = {
    "admin": {
        "id": "admin-001",
        "username": "admin",
        "password_hash": auth_manager.hash_password("SmartCloudOps2025!"),
        "role": "admin",
        "email": "admin@company.com",
        "tenant_id": "default",
        "created_at": datetime.utcnow().isoformat(),
        "active": True,
    },
    "operator": {
        "id": "op-001",
        "username": "operator",
        "password_hash": auth_manager.hash_password("CloudOps2025!"),
        "role": "operator",
        "email": "operator@company.com",
        "tenant_id": "default",
        "created_at": datetime.utcnow().isoformat(),
        "active": True,
    },
    "demo": {
        "id": "demo-001",
        "username": "demo",
        "password_hash": auth_manager.hash_password("demo123"),
        "role": "viewer",
        "email": "demo@company.com",
        "tenant_id": "demo",
        "created_at": datetime.utcnow().isoformat(),
        "active": True,
    },
}


def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user credentials"""
    user = ENTERPRISE_USERS.get(username)
    if not user or not user["active"]:
        return None

    if auth_manager.verify_password(password, user["password_hash"]):
        return user

    return None


def get_user_by_id(user_id: str) -> dict:
    """Get user by ID"""
    for user in ENTERPRISE_USERS.values():
        if user["id"] == user_id:
            return user
    return None
