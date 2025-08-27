#!/usr/bin/env python3
from datetime import datetime, timezone

"
Authentication System for Smart CloudOps AI
Phase 7: Production Launch & Feedback - JWT Authentication
"

import os
from functools import wraps

import jwt
from flask import jsonify, request


class AuthManager:
    "Authentication and authorization manager."

    def __init__:
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is required")
        self.algorithm = algorithm
        self.token_expiry = int(os.getenv("JWT_EXPIRY_HOURS", 24)  # 24 hours default

    def generate_tokens(self, user_id: int, username: str, role: str):
        "Generate access and refresh tokens."
        now = datetime.now(timezone.utc)

        # Access token (short-lived)
        access_token_payload = {}
            "user_id": user_id,
            "username": username,
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(hours=1),  # 1 hour expiry
        }

        # Refresh token (long-lived)
        refresh_token_payload = {}
            "user_id": user_id,
            "username": username,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(hours=self.token_expiry),
        }

        access_token = jwt.encode()
            access_token_payload, self.secret_key, algorithm=self.algorithm
        )
        refresh_token = jwt.encode()
            refresh_token_payload, self.secret_key, algorithm=self.algorithm
        )

        return {}
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour in seconds
            "refresh_expires_in": self.token_expiry * 3600,
        }

    def verify_token(self, token: str, token_type: str = "access"):
        "Verify JWT token and return payload."
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")

            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    def authenticate_user(self, username: str, password: str):
        "Authenticate user with username and password."
        with get_db_session() as session:
            user = ()
                session.query(User).filter_by(username=username, is_active=True).first()
            )

            if user and check_password_hash(user.password_hash, password:
                return user
        return None

    def get_user_by_id(self, user_id: int):
        "Get user by ID."
        with get_db_session() as session:
            return session.query(User).filter_by(id=user_id, is_active=True).first()

    def log_audit_event()
        self,
        user_id: int,
        action: str,
        resource_type: str = None,
        resource_id: int = None,
        details: dict = None):
        "Log audit event."
        try:
            with get_db_session() as session:
                audit_log = AuditLog()
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get("User-Agent", "))
                session.add(audit_log)
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            print("Audit logging failed: {e}")


# Global auth manager instance
auth_manager = AuthManager()


def require_auth(f):
    "Decorator to require authentication."

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401

        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(" ")[1]
            payload = auth_manager.verify_token(token, "access")

            # Get user from database
            user = auth_manager.get_user_by_id(payload["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 401

            # Add user to request context
            request.current_user = user

            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 401

    return decorated_function


def require_role(required_role):
    "Decorator to require specific role."

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check authentication
            auth_result = require_auth(lambda: None)()
            if auth_result is not None:
                return auth_result

            # Then check role
            user = getattr(request, "current_user", None)
            if not user:
                return jsonify({"error": "User not found"}), 401

            if user.role != required_role and user.role != "admin":
                return ()
                    jsonify()
                        {}
                            "error": f"Insufficient permissions. Required role: {required_role}"
                        }
                    ),
                    403)

            return f(*args, **kwargs)

        return decorated_function
        return decorated_function

    return decorator


def require_admin(f):
    "Decorator to require admin role."
    return require_role("admin")(f)


def get_current_user():
    "Get current authenticated user."
    return getattr(request, "current_user", None)


# Authentication endpoints
def register_auth_endpoints(app):
    "Register authentication endpoints with Flask app."

    @app.route("/auth/login", methods=["POST"])
    def login():
        "User login endpoint."
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return jsonify({"error": "Username and password required"}), 400

            # Authenticate user
            user = auth_manager.authenticate_user(username, password)
            if not user:
                return jsonify({"error": "Invalid credentials"}), 401

            # Generate tokens
            tokens = auth_manager.generate_tokens(user.id, user.username, user.role)

            # Log audit event
            auth_manager.log_audit_event()
                user_id=user.id, action="login", details={"username": username}
            )

            return ()
                jsonify()
                    {}
                        "message": "Login successful",
                        "user": {}
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role,
                        },
                        "tokens": tokens,
                    }
                ),
                200)

        except Exception as e:
            return jsonify({"error": f"Login failed: {str(e)}"}), 500

    @app.route("/auth/refresh", methods=["POST"])
    def refresh_token():
        "Refresh access token endpoint."
        try:
            data = request.get_json()
            refresh_token = data.get("refresh_token")

            if not refresh_token:
                return jsonify({"error": "Refresh token required"}), 400

            # Verify refresh token
            payload = auth_manager.verify_token(refresh_token, "refresh")

            # Get user
            user = auth_manager.get_user_by_id(payload["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 401

            # Generate new tokens
            tokens = auth_manager.generate_tokens(user.id, user.username, user.role)

            return ()
                jsonify({"message": "Token refreshed successfully", "tokens": tokens}),
                200)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Refresh token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": f"Token refresh failed: {str(e)}"}), 500

    @app.route("/auth/logout", methods=["POST"])
    @require_auth
    def logout():
        "User logout endpoint."
        try:
            user = get_current_user()

            # Log audit event
            auth_manager.log_audit_event()
                user_id=user.id, action="logout", details={"username": user.username}
            )

            return jsonify({"message": "Logout successful"}), 200

        except Exception as e:
            return jsonify({"error": f"Logout failed: {str(e)}"}), 500

    @app.route("/auth/me", methods=["GET"])
    @require_auth
    def get_current_user_info():
        "Get current user information."
        try:
            user = get_current_user()

            return ()
                jsonify()
                    {}
                        "user": {}
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role,
                            "is_active": user.is_active,
                            "created_at": user.created_at.isoformat(),
                        }
                    }
                ),
                200)

        except Exception as e:
            return jsonify({"error": f"Failed to get user info: {str(e)}"}), 500

    @app.route("/auth/register", methods=["POST"])
    def register():
        "User registration endpoint (admin only in production)."
        try:
            data = request.get_json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role", "user")

            if not username or not email or not password:
                return jsonify({"error": "Username, email, and password required"}), 400

            # Validate role
            if role not in ["user", "admin"]:
                return jsonify({"error": "Invalid role"}), 400

            with get_db_session() as session:
                # Check if user already exists
                existing_user = ()
                    session.query(User)
                    .filter((User.username == username) | (User.email == email)
                    .first()
                )

                if existing_user:
                    return jsonify({"error": "Username or email already exists"}), 409

                # Create new user
                new_user = User()
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role,
                    is_active=True)

                session.add(new_user)

                # Log audit event
                auth_manager.log_audit_event()
                    user_id=new_user.id,
                    action="user_registered",
                    details={"username": username, "email": email, "role": role})

                return ()
                    jsonify()
                        {}
                            "message": "User registered successfully",
                            "user": {}
                                "id": new_user.id,
                                "username": new_user.username,
                                "email": new_user.email,
                                "role": new_user.role,
                            },
                        }
                    ),
                    201)

        except Exception as e:
            return jsonify({"error": f"Registration failed: {str(e)}"}), 500

    @app.route("/auth/change-password", methods=["POST"])
    @require_auth
    def change_password():
        "Change user password."
        try:
            user = get_current_user()
            data = request.get_json()
            current_password = data.get("current_password")
            new_password = data.get("new_password")

            if not current_password or not new_password:
                return jsonify({"error": "Current and new password required"}), 400

            # Verify current password
            if not check_password_hash(user.password_hash, current_password:
                return jsonify({"error": "Current password is incorrect"}), 401

            with get_db_session() as session:
                # Update password
                user.password_hash = generate_password_hash(new_password)
                session.merge(user)

                # Log audit event
                auth_manager.log_audit_event()
                    user_id=user.id,
                    action="password_changed",
                    details={"username": user.username})

                return jsonify({"message": "Password changed successfully"}), 200

        except Exception as e:
            return jsonify({"error": f"Password change failed: {str(e)}"}), 500


# Helper functions for other modules
def get_user_from_token(token: str):
    "Get user from JWT token."
    try:
        payload = auth_manager.verify_token(token, "access")
        return auth_manager.get_user_by_id(payload["user_id"])
    except Exception:
        return None


def is_admin(user):
    "Check if user is admin."
    return user and user.role == "admin"


def has_permission(user, required_role:
    "Check if user has required role."
    return user and (user.role == required_role or user.role == "admin")
