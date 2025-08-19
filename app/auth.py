#!/usr/bin/env python3
"""
Enterprise Authentication & Authorization System
JWT-based authentication with role-based access control
"""

import logging
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Union

import bcrypt
import jwt
import redis
from flask import jsonify, request, current_app
from app.security.input_validation import validator, SecurityValidationError

logger = logging.getLogger(__name__)

# Redis client for token blacklisting
try:
    # Try Docker service name first, then localhost
    redis_host = os.getenv("REDIS_HOST", "redis-cache-server")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "1"))
    redis_password = os.getenv("REDIS_PASSWORD")

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    # Test connection
    redis_client.ping()
    logger.info(f"✅ Redis connected: {redis_host}:{redis_port}")
except Exception as e:
    redis_client = None
    logger.warning(f"⚠️ Redis not available for token blacklisting: {e}")


class AuthManager:
    """Enterprise-grade authentication and authorization manager"""

    def __init__(self, secret_key: Optional[str] = None, algorithm: str = "HS256"):
        """Initialize authentication manager with secure defaults."""
        # Use environment variable or generate secure key
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            # Generate a secure key if none provided
            self.secret_key = secrets.token_urlsafe(64)
            logger.warning("No JWT_SECRET_KEY provided, generated temporary key")

        # Validate secret key strength
        if len(self.secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

        self.algorithm = algorithm
        self.token_expiry = timedelta(
            hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRY_HOURS", "24"))
        )
        self.refresh_expiry = timedelta(
            days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRY_DAYS", "7"))
        )

        # Enterprise user roles and permissions
        self.roles = {
            "admin": {
                "permissions": [
                    "read",
                    "write",
                    "admin",
                    "ml_train",
                    "system_config",
                    "user_management",
                ],
                "description": "Full system access",
                "level": 4,
            },
            "operator": {
                "permissions": ["read", "write", "ml_query", "remediation_execute"],
                "description": "Operations and monitoring",
                "level": 3,
            },
            "analyst": {
                "permissions": ["read", "ml_query", "ml_train", "remediation_view"],
                "description": "ML analysis and training",
                "level": 2,
            },
            "viewer": {
                "permissions": ["read"],
                "description": "Read-only access",
                "level": 1,
            },
        }

        # Rate limiting configuration
        self.max_login_attempts = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.lockout_duration = timedelta(
            minutes=int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
        )

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with secure configuration."""
        try:
            # Validate password strength
            validator.validate_password(password, min_length=8)

            # Use high cost factor for enterprise security
            cost_factor = int(os.getenv("BCRYPT_COST_FACTOR", "12"))
            salt = bcrypt.gensalt(rounds=cost_factor)
            return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        except SecurityValidationError as e:
            logger.error(f"Password validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash with timing attack protection."""
        try:
            if not password or not hashed:
                return False

            # Use constant time comparison to prevent timing attacks
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    def generate_tokens(
        self,
        user_id: str,
        username: str,
        role: str,
        tenant_id: Optional[str] = None,
        additional_claims: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Generate JWT access and refresh tokens with security best practices."""
        try:
            # Validate inputs
            user_id = validator.validate_string(user_id, max_length=100)
            username = validator.validate_string(username, max_length=100)
            role = validator.validate_string(role, max_length=50)

            if tenant_id:
                tenant_id = validator.validate_string(tenant_id, max_length=100)

            now = datetime.utcnow()
            jti = secrets.token_urlsafe(32)  # Unique token ID

            # Access token payload
            access_payload = {
                "user_id": user_id,
                "username": username,
                "role": role,
                "tenant_id": tenant_id,
                "permissions": self.roles.get(role, {}).get("permissions", []),
                "level": self.roles.get(role, {}).get("level", 0),
                "jti": jti,  # Token ID for blacklisting
                "iat": now,
                "exp": now + self.token_expiry,
                "type": "access",
                "iss": "smartcloudops-ai",  # Issuer
                "aud": "smartcloudops-frontend",  # Audience
            }

            # Add additional claims if provided
            if additional_claims:
                access_payload.update(additional_claims)

            # Refresh token payload (minimal for security)
            refresh_payload = {
                "user_id": user_id,
                "jti": secrets.token_urlsafe(32),
                "iat": now,
                "exp": now + self.refresh_expiry,
                "type": "refresh",
                "iss": "smartcloudops-ai",
                "aud": "smartcloudops-frontend",
            }

            # Generate tokens
            access_token = jwt.encode(
                access_payload, self.secret_key, algorithm=self.algorithm
            )
            refresh_token = jwt.encode(
                refresh_payload, self.secret_key, algorithm=self.algorithm
            )

            # Store refresh token in Redis for revocation capability
            if redis_client:
                try:
                    redis_client.setex(
                        f"refresh_token:{refresh_payload['jti']}",
                        int(self.refresh_expiry.total_seconds()),
                        user_id,
                    )
                except Exception as e:
                    logger.warning(f"Failed to store refresh token in Redis: {e}")

            logger.info(f"Generated tokens for user {username} (role: {role})")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": int(self.token_expiry.total_seconds()),
            }

        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict]:
        """Verify JWT token with comprehensive validation."""
        try:
            if not token:
                return None

            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "iss", "aud", "type"],
                },
            )

            # Validate token type
            if payload.get("type") != token_type:
                logger.warning(
                    f"Token type mismatch: expected {token_type}, got {payload.get('type')}"
                )
                return None

            # Validate issuer and audience
            if payload.get("iss") != "smartcloudops-ai":
                logger.warning("Invalid token issuer")
                return None

            if payload.get("aud") != "smartcloudops-frontend":
                logger.warning("Invalid token audience")
                return None

            # Check if token is blacklisted
            if self.is_token_blacklisted(payload.get("jti")):
                logger.warning("Token is blacklisted")
                return None

            # Validate user still exists and role is valid
            if not self._validate_user_permissions(payload):
                logger.warning("User permissions validation failed")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.info("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token, "refresh")
            if not payload:
                return None

            # Check if refresh token exists in Redis
            if redis_client:
                stored_user_id = redis_client.get(f"refresh_token:{payload.get('jti')}")
                if not stored_user_id or stored_user_id != payload.get("user_id"):
                    logger.warning("Refresh token not found in Redis")
                    return None

            # Get user information
            user = get_user_by_id(payload.get("user_id"))
            if not user:
                logger.warning("User not found during token refresh")
                return None

            # Generate new access token
            return self.generate_tokens(
                user_id=user["id"],
                username=user["username"],
                role=user["role"],
                tenant_id=user.get("tenant_id"),
            )

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding it to blacklist."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")

            if not jti:
                return False

            # Add to blacklist in Redis
            if redis_client:
                # Blacklist until token expires
                exp = payload.get("exp", 0)
                ttl = max(0, exp - int(datetime.utcnow().timestamp()))

                if ttl > 0:
                    redis_client.setex(f"blacklist:{jti}", ttl, "revoked")
                    logger.info(f"Token {jti} blacklisted")
                    return True

            return False

        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False

    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted."""
        if not jti or not redis_client:
            return False

        try:
            return redis_client.exists(f"blacklist:{jti}") > 0
        except Exception as e:
            logger.error(f"Blacklist check failed: {e}")
            return False

    def _validate_user_permissions(self, payload: Dict) -> bool:
        """Validate user permissions and role."""
        try:
            user_id = payload.get("user_id")
            role = payload.get("role")

            if not user_id or not role:
                return False

            # Check if role is valid
            if role not in self.roles:
                return False

            # Check if user still exists (implement user lookup)
            user = get_user_by_id(user_id)
            if not user:
                return False

            # Check if user role matches token role
            if user.get("role") != role:
                return False

            return True

        except Exception as e:
            logger.error(f"User permissions validation failed: {e}")
            return False

    def check_permission(
        self, user_permissions: List[str], required_permission: str
    ) -> bool:
        """Check if user has required permission."""
        return required_permission in user_permissions

    def get_user_level(self, role: str) -> int:
        """Get user security level for role."""
        return self.roles.get(role, {}).get("level", 0)


# Global auth manager instance
auth_manager = AuthManager()


# Enterprise user database (replace with actual database)
ENTERPRISE_USERS = {
    "admin": {
        "id": "admin-001",
        "username": "admin",
        "password_hash": bcrypt.hashpw(
            "admin123".encode("utf-8"), bcrypt.gensalt(12)
        ).decode("utf-8"),
        "role": "admin",
        "email": "admin@smartcloudops.ai",
        "tenant_id": "enterprise-001",
        "created_at": datetime.utcnow(),
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
    },
    "operator": {
        "id": "operator-001",
        "username": "operator",
        "password_hash": bcrypt.hashpw(
            "operator123".encode("utf-8"), bcrypt.gensalt(12)
        ).decode("utf-8"),
        "role": "operator",
        "email": "operator@smartcloudops.ai",
        "tenant_id": "enterprise-001",
        "created_at": datetime.utcnow(),
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
    },
    "analyst": {
        "id": "analyst-001",
        "username": "analyst",
        "password_hash": bcrypt.hashpw(
            "analyst123".encode("utf-8"), bcrypt.gensalt(12)
        ).decode("utf-8"),
        "role": "analyst",
        "email": "analyst@smartcloudops.ai",
        "tenant_id": "enterprise-001",
        "created_at": datetime.utcnow(),
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
    },
    "viewer": {
        "id": "viewer-001",
        "username": "viewer",
        "password_hash": bcrypt.hashpw(
            "viewer123".encode("utf-8"), bcrypt.gensalt(12)
        ).decode("utf-8"),
        "role": "viewer",
        "email": "viewer@smartcloudops.ai",
        "tenant_id": "enterprise-001",
        "created_at": datetime.utcnow(),
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
    },
}


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID (replace with database lookup)."""
    for user in ENTERPRISE_USERS.values():
        if user["id"] == user_id:
            return user
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with rate limiting and security checks."""
    try:
        # Validate inputs
        username = validator.validate_string(username, max_length=100)
        password = validator.validate_string(password, max_length=100)

        # Get user
        user = ENTERPRISE_USERS.get(username)
        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return None

        # Check if account is locked
        if user.get("locked_until") and datetime.utcnow() < user["locked_until"]:
            logger.warning(f"Account locked for user {username}")
            return None

        # Verify password
        if not auth_manager.verify_password(password, user["password_hash"]):
            # Increment failed attempts
            user["failed_attempts"] = user.get("failed_attempts", 0) + 1

            # Lock account if too many failed attempts
            if user["failed_attempts"] >= auth_manager.max_login_attempts:
                user["locked_until"] = datetime.utcnow() + auth_manager.lockout_duration
                logger.warning(
                    f"Account locked for user {username} due to too many failed attempts"
                )

            logger.warning(
                f"Authentication failed: invalid password for user {username}"
            )
            return None

        # Reset failed attempts on successful login
        user["failed_attempts"] = 0
        user["locked_until"] = None
        user["last_login"] = datetime.utcnow()

        logger.info(f"Successful authentication for user {username}")
        return user

    except SecurityValidationError as e:
        logger.error(f"Input validation failed during authentication: {e}")
        return None
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


def require_auth(f):
    """Decorator to require authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return (
                    jsonify({"error": "Missing or invalid authorization header"}),
                    401,
                )

            token = auth_header.split(" ")[1]

            # Verify token
            payload = auth_manager.verify_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401

            # Add user info to request
            request.user = payload
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Authentication decorator error: {e}")
            return jsonify({"error": "Authentication failed"}), 401

    return decorated_function


def require_permission(permission: str):
    """Decorator to require specific permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check if user is authenticated
                if not hasattr(request, "user"):
                    return jsonify({"error": "Authentication required"}), 401

                user_permissions = request.user.get("permissions", [])

                # Check permission
                if not auth_manager.check_permission(user_permissions, permission):
                    return jsonify({"error": "Insufficient permissions"}), 403

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Permission check error: {e}")
                return jsonify({"error": "Permission check failed"}), 403

        return decorated_function

    return decorator


def require_admin(f):
    """Decorator to require admin role."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if user is authenticated
            if not hasattr(request, "user"):
                return jsonify({"error": "Authentication required"}), 401

            # Check if user is admin
            if request.user.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Admin check error: {e}")
            return jsonify({"error": "Admin check failed"}), 403

    return decorated_function


def get_current_user() -> Optional[Dict]:
    """Get current authenticated user."""
    if hasattr(request, "user"):
        return request.user
    return None


def logout_user(token: str) -> bool:
    """Logout user by revoking token."""
    try:
        return auth_manager.revoke_token(token)
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return False
