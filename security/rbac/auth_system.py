"""
Role-Based Access Control (RBAC) System
Phase 3 Week 2: Security Hardening - RBAC Implementation
"""

import hashlib
import json
import logging
import secrets
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import bcrypt
import jwt

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """System user roles with hierarchical permissions"""

    SUPER_ADMIN = "super_admin"  # Full system access
    ADMIN = "admin"  # Administrative access
    MLOps_ENGINEER = "mlops_engineer"  # MLOps platform access
    DATA_SCIENTIST = "data_scientist"  # Data and model access
    ANALYST = "analyst"  # Read-only access to reports
    VIEWER = "viewer"  # Basic read-only access
    API_USER = "api_user"  # API-only access


class Permission(Enum):
    """System permissions"""

    # System administration
    SYSTEM_ADMIN = "system.admin"
    SYSTEM_CONFIG = "system.config"
    SYSTEM_USERS = "system.users"
    SYSTEM_MONITORING = "system.monitoring"

    # MLOps operations
    MLOPS_EXPERIMENTS_READ = "mlops.experiments.read"
    MLOPS_EXPERIMENTS_WRITE = "mlops.experiments.write"
    MLOPS_EXPERIMENTS_DELETE = "mlops.experiments.delete"
    MLOPS_MODELS_READ = "mlops.models.read"
    MLOPS_MODELS_WRITE = "mlops.models.write"
    MLOPS_MODELS_DEPLOY = "mlops.models.deploy"
    MLOPS_MODELS_DELETE = "mlops.models.delete"
    MLOPS_DATA_READ = "mlops.data.read"
    MLOPS_DATA_WRITE = "mlops.data.write"
    MLOPS_DATA_DELETE = "mlops.data.delete"

    # API access
    API_READ = "api.read"
    API_WRITE = "api.write"
    API_ADMIN = "api.admin"

    # Reports and analytics
    REPORTS_READ = "reports.read"
    REPORTS_WRITE = "reports.write"

    # Performance and monitoring
    MONITORING_READ = "monitoring.read"
    MONITORING_WRITE = "monitoring.write"


@dataclass
class User:
    """User data model"""

    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    permissions: Set[Permission]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    session_token: Optional[str] = None

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary, optionally excluding sensitive data"""
        user_dict = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "failed_login_attempts": self.failed_login_attempts,
            "locked_until": (
                self.locked_until.isoformat() if self.locked_until else None
            ),
        }

        if include_sensitive:
            user_dict.update(
                {
                    "password_hash": self.password_hash,
                    "session_token": self.session_token,
                }
            )

        return user_dict


@dataclass
class AccessToken:
    """JWT access token model"""

    user_id: str
    username: str
    role: UserRole
    permissions: Set[Permission]
    issued_at: datetime
    expires_at: datetime
    token_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "iat": int(self.issued_at.timestamp()),
            "exp": int(self.expires_at.timestamp()),
            "jti": self.token_id,
        }


class RolePermissionManager:
    """Manage role-based permissions"""

    def __init__(self):
        self.role_permissions = self._define_role_permissions()

    def _define_role_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Define permissions for each role"""
        return {
            UserRole.SUPER_ADMIN: {
                # Full access to everything
                Permission.SYSTEM_ADMIN,
                Permission.SYSTEM_CONFIG,
                Permission.SYSTEM_USERS,
                Permission.SYSTEM_MONITORING,
                Permission.MLOPS_EXPERIMENTS_READ,
                Permission.MLOPS_EXPERIMENTS_WRITE,
                Permission.MLOPS_EXPERIMENTS_DELETE,
                Permission.MLOPS_MODELS_READ,
                Permission.MLOPS_MODELS_WRITE,
                Permission.MLOPS_MODELS_DEPLOY,
                Permission.MLOPS_MODELS_DELETE,
                Permission.MLOPS_DATA_READ,
                Permission.MLOPS_DATA_WRITE,
                Permission.MLOPS_DATA_DELETE,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.API_ADMIN,
                Permission.REPORTS_READ,
                Permission.REPORTS_WRITE,
                Permission.MONITORING_READ,
                Permission.MONITORING_WRITE,
            },
            UserRole.ADMIN: {
                # Administrative access without system config
                Permission.SYSTEM_USERS,
                Permission.SYSTEM_MONITORING,
                Permission.MLOPS_EXPERIMENTS_READ,
                Permission.MLOPS_EXPERIMENTS_WRITE,
                Permission.MLOPS_EXPERIMENTS_DELETE,
                Permission.MLOPS_MODELS_READ,
                Permission.MLOPS_MODELS_WRITE,
                Permission.MLOPS_MODELS_DEPLOY,
                Permission.MLOPS_MODELS_DELETE,
                Permission.MLOPS_DATA_READ,
                Permission.MLOPS_DATA_WRITE,
                Permission.MLOPS_DATA_DELETE,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.REPORTS_READ,
                Permission.REPORTS_WRITE,
                Permission.MONITORING_READ,
                Permission.MONITORING_WRITE,
            },
            UserRole.MLOps_ENGINEER: {
                # Full MLOps access
                Permission.MLOPS_EXPERIMENTS_READ,
                Permission.MLOPS_EXPERIMENTS_WRITE,
                Permission.MLOPS_EXPERIMENTS_DELETE,
                Permission.MLOPS_MODELS_READ,
                Permission.MLOPS_MODELS_WRITE,
                Permission.MLOPS_MODELS_DEPLOY,
                Permission.MLOPS_DATA_READ,
                Permission.MLOPS_DATA_WRITE,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.REPORTS_READ,
                Permission.REPORTS_WRITE,
                Permission.MONITORING_READ,
            },
            UserRole.DATA_SCIENTIST: {
                # Data and model access, no deployment
                Permission.MLOPS_EXPERIMENTS_READ,
                Permission.MLOPS_EXPERIMENTS_WRITE,
                Permission.MLOPS_MODELS_READ,
                Permission.MLOPS_MODELS_WRITE,
                Permission.MLOPS_DATA_READ,
                Permission.MLOPS_DATA_WRITE,
                Permission.API_READ,
                Permission.REPORTS_READ,
                Permission.REPORTS_WRITE,
                Permission.MONITORING_READ,
            },
            UserRole.ANALYST: {
                # Read-only access to reports and data
                Permission.MLOPS_EXPERIMENTS_READ,
                Permission.MLOPS_MODELS_READ,
                Permission.MLOPS_DATA_READ,
                Permission.API_READ,
                Permission.REPORTS_READ,
                Permission.MONITORING_READ,
            },
            UserRole.VIEWER: {
                # Basic read-only access
                Permission.MLOPS_EXPERIMENTS_READ,
                Permission.MLOPS_MODELS_READ,
                Permission.API_READ,
                Permission.REPORTS_READ,
            },
            UserRole.API_USER: {
                # API-only access
                Permission.API_READ,
                Permission.API_WRITE,
            },
        }

    def get_permissions(self, role: UserRole) -> Set[Permission]:
        """Get permissions for a role"""
        return self.role_permissions.get(role, set())

    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in self.get_permissions(role)

    def can_access_resource(self, role: UserRole, resource: str, action: str) -> bool:
        """Check if role can perform action on resource"""
        permission_map = {
            ("experiments", "read"): Permission.MLOPS_EXPERIMENTS_READ,
            ("experiments", "write"): Permission.MLOPS_EXPERIMENTS_WRITE,
            ("experiments", "delete"): Permission.MLOPS_EXPERIMENTS_DELETE,
            ("models", "read"): Permission.MLOPS_MODELS_READ,
            ("models", "write"): Permission.MLOPS_MODELS_WRITE,
            ("models", "deploy"): Permission.MLOPS_MODELS_DEPLOY,
            ("models", "delete"): Permission.MLOPS_MODELS_DELETE,
            ("data", "read"): Permission.MLOPS_DATA_READ,
            ("data", "write"): Permission.MLOPS_DATA_WRITE,
            ("data", "delete"): Permission.MLOPS_DATA_DELETE,
            ("api", "read"): Permission.API_READ,
            ("api", "write"): Permission.API_WRITE,
            ("reports", "read"): Permission.REPORTS_READ,
            ("reports", "write"): Permission.REPORTS_WRITE,
            ("monitoring", "read"): Permission.MONITORING_READ,
            ("monitoring", "write"): Permission.MONITORING_WRITE,
            ("system", "admin"): Permission.SYSTEM_ADMIN,
            ("system", "users"): Permission.SYSTEM_USERS,
        }

        required_permission = permission_map.get((resource, action))
        if not required_permission:
            return False

        return self.has_permission(role, required_permission)


class UserManager:
    """Manage user accounts and authentication"""

    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        self.role_manager = RolePermissionManager()
        self.jwt_secret = self._get_jwt_secret()
        self.token_expiry_hours = 24
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30

        # Initialize database
        self._init_database()

        # Create default admin user if none exists
        self._create_default_admin()

    def _get_jwt_secret(self) -> str:
        """Get or generate JWT secret"""
        secret_file = Path("security/jwt_secret.key")
        secret_file.parent.mkdir(parents=True, exist_ok=True)

        if secret_file.exists():
            return secret_file.read_text().strip()
        else:
            secret = secrets.token_urlsafe(32)
            secret_file.write_text(secret)
            logger.info("Generated new JWT secret")
            return secret

    @contextmanager
    def _get_db_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        """Initialize user database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    session_token TEXT
                )
            """
            )

            # User sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Audit log table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN
                )
            """
            )

            conn.commit()

    def _create_default_admin(self):
        """Create default admin user if none exists"""
        try:
            if not self.get_user_by_username("admin"):
                admin_user = self.create_user(
                    username="admin",
                    email="admin@smartcloudops.ai",
                    password="SmartCloudOps2024!",  # Should be changed immediately
                    role=UserRole.SUPER_ADMIN,
                )
                logger.warning(
                    "Created default admin user. Please change the password immediately!"
                )
                return admin_user
        except Exception as e:
            logger.error(f"Failed to create default admin user: {e}")

        return None

    def create_user(
        self, username: str, email: str, password: str, role: UserRole
    ) -> User:
        """Create new user"""
        # Validate input
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if "@" not in email:
            raise ValueError("Invalid email format")

        # Generate user ID and hash password
        user_id = hashlib.sha256(
            f"{username}{email}{time.time()}".encode()
        ).hexdigest()[:16]
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Get role permissions
        permissions = self.role_manager.get_permissions(role)

        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            permissions=permissions,
            is_active=True,
            created_at=datetime.now(),
        )

        # Save to database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO users (id, username, email, password_hash, role, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user.id,
                        user.username,
                        user.email,
                        user.password_hash,
                        user.role.value,
                        user.is_active,
                        user.created_at,
                    ),
                )

                conn.commit()

                # Log user creation
                self._log_audit_event(
                    user.id,
                    "user_created",
                    "users",
                    {"username": username, "role": role.value},
                )

                logger.info(f"Created user: {username} with role: {role.value}")
                return user

            except sqlite3.IntegrityError as e:
                if "username" in str(e):
                    raise ValueError("Username already exists")
                elif "email" in str(e):
                    raise ValueError("Email already exists")
                else:
                    raise ValueError(f"Failed to create user: {e}")

    def authenticate_user(
        self, username: str, password: str, ip_address: str = None
    ) -> Optional[AccessToken]:
        """Authenticate user and return access token"""
        user = self.get_user_by_username(username)

        if not user:
            self._log_audit_event(
                None,
                "login_failed",
                "auth",
                {"username": username, "reason": "user_not_found"},
                ip_address,
                False,
            )
            return None

        # Check if user is locked
        if user.locked_until and datetime.now() < user.locked_until:
            self._log_audit_event(
                user.id,
                "login_failed",
                "auth",
                {"reason": "account_locked"},
                ip_address,
                False,
            )
            return None

        # Check if user is active
        if not user.is_active:
            self._log_audit_event(
                user.id,
                "login_failed",
                "auth",
                {"reason": "account_disabled"},
                ip_address,
                False,
            )
            return None

        # Verify password
        if not bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            # Increment failed attempts
            self._increment_failed_attempts(user)
            self._log_audit_event(
                user.id,
                "login_failed",
                "auth",
                {"reason": "invalid_password"},
                ip_address,
                False,
            )
            return None

        # Reset failed attempts on successful login
        self._reset_failed_attempts(user)

        # Update last login
        self._update_last_login(user)

        # Generate access token
        token = self._generate_access_token(user, ip_address)

        self._log_audit_event(
            user.id,
            "login_success",
            "auth",
            {"token_id": token.token_id},
            ip_address,
            True,
        )

        logger.info(f"User {username} authenticated successfully")
        return token

    def validate_token(self, token_string: str) -> Optional[AccessToken]:
        """Validate JWT token and return access token"""
        try:
            # Decode JWT token
            payload = jwt.decode(token_string, self.jwt_secret, algorithms=["HS256"])

            # Extract token data
            user_id = payload.get("user_id")
            token_id = payload.get("jti")

            if not user_id or not token_id:
                return None

            # Check if session is still active
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT is_active, expires_at FROM user_sessions 
                    WHERE token_id = ? AND user_id = ?
                """,
                    (token_id, user_id),
                )

                session = cursor.fetchone()
                if not session or not session["is_active"]:
                    return None

                # Check if token has expired
                expires_at = datetime.fromisoformat(session["expires_at"])
                if datetime.now() > expires_at:
                    # Deactivate expired session
                    cursor.execute(
                        """
                        UPDATE user_sessions SET is_active = 0 WHERE token_id = ?
                    """,
                        (token_id,),
                    )
                    conn.commit()
                    return None

            # Get user data
            user = self.get_user_by_id(user_id)
            if not user or not user.is_active:
                return None

            # Create access token object
            access_token = AccessToken(
                user_id=user.id,
                username=user.username,
                role=user.role,
                permissions=user.permissions,
                issued_at=datetime.fromtimestamp(payload["iat"]),
                expires_at=datetime.fromtimestamp(payload["exp"]),
                token_id=token_id,
            )

            return access_token

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def revoke_token(self, token_id: str, user_id: str = None):
        """Revoke access token"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            if user_id:
                cursor.execute(
                    """
                    UPDATE user_sessions SET is_active = 0 
                    WHERE token_id = ? AND user_id = ?
                """,
                    (token_id, user_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE user_sessions SET is_active = 0 
                    WHERE token_id = ?
                """,
                    (token_id,),
                )

            conn.commit()

            self._log_audit_event(
                user_id, "token_revoked", "auth", {"token_id": token_id}
            )

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_user(row)

            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

            if row:
                return self._row_to_user(row)

            return None

    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        role = UserRole(row["role"])
        permissions = self.role_manager.get_permissions(role)

        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=role,
            permissions=permissions,
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_login=(
                datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
            ),
            failed_login_attempts=row["failed_login_attempts"],
            locked_until=(
                datetime.fromisoformat(row["locked_until"])
                if row["locked_until"]
                else None
            ),
            session_token=row["session_token"],
        )

    def _generate_access_token(self, user: User, ip_address: str = None) -> AccessToken:
        """Generate JWT access token"""
        now = datetime.now()
        expires_at = now + timedelta(hours=self.token_expiry_hours)
        token_id = secrets.token_urlsafe(16)

        access_token = AccessToken(
            user_id=user.id,
            username=user.username,
            role=user.role,
            permissions=user.permissions,
            issued_at=now,
            expires_at=expires_at,
            token_id=token_id,
        )

        # Create JWT token
        token_string = jwt.encode(
            access_token.to_dict(), self.jwt_secret, algorithm="HS256"
        )

        # Save session to database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_sessions (token_id, user_id, expires_at, ip_address)
                VALUES (?, ?, ?, ?)
            """,
                (token_id, user.id, expires_at, ip_address),
            )
            conn.commit()

        # Set token string for return
        access_token.token_string = token_string

        return access_token

    def _increment_failed_attempts(self, user: User):
        """Increment failed login attempts"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            new_count = user.failed_login_attempts + 1
            locked_until = None

            if new_count >= self.max_failed_attempts:
                locked_until = datetime.now() + timedelta(
                    minutes=self.lockout_duration_minutes
                )

            cursor.execute(
                """
                UPDATE users 
                SET failed_login_attempts = ?, locked_until = ?
                WHERE id = ?
            """,
                (new_count, locked_until, user.id),
            )

            conn.commit()

    def _reset_failed_attempts(self, user: User):
        """Reset failed login attempts"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users 
                SET failed_login_attempts = 0, locked_until = NULL
                WHERE id = ?
            """,
                (user.id,),
            )
            conn.commit()

    def _update_last_login(self, user: User):
        """Update user's last login timestamp"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users SET last_login = ? WHERE id = ?
            """,
                (datetime.now(), user.id),
            )
            conn.commit()

    def _log_audit_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        success: bool = True,
    ):
        """Log audit event"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, resource, details, ip_address, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    action,
                    resource,
                    json.dumps(details) if details else None,
                    ip_address,
                    success,
                ),
            )
            conn.commit()


# Global user manager instance
user_manager = UserManager()


def require_permission(permission: Permission):
    """Decorator to require specific permission"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import g, jsonify, request

            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Authentication required",
                            "message": "Valid access token required",
                        }
                    ),
                    401,
                )

            # Extract token
            token_string = auth_header[7:]  # Remove 'Bearer '

            # Validate token
            access_token = user_manager.validate_token(token_string)
            if not access_token:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Invalid token",
                            "message": "Token is invalid or expired",
                        }
                    ),
                    401,
                )

            # Check permission
            if permission not in access_token.permissions:
                user_manager._log_audit_event(
                    access_token.user_id,
                    "access_denied",
                    "api",
                    {"endpoint": request.endpoint, "permission": permission.value},
                    request.remote_addr,
                    False,
                )

                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Insufficient permissions",
                            "message": f"Permission {permission.value} required",
                        }
                    ),
                    403,
                )

            # Set user context
            g.current_user = access_token

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: UserRole):
    """Decorator to require specific role"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import g, jsonify, request

            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return (
                    jsonify({"status": "error", "error": "Authentication required"}),
                    401,
                )

            # Extract and validate token
            token_string = auth_header[7:]
            access_token = user_manager.validate_token(token_string)

            if not access_token:
                return jsonify({"status": "error", "error": "Invalid token"}), 401

            # Check role hierarchy
            role_hierarchy = {
                UserRole.SUPER_ADMIN: 7,
                UserRole.ADMIN: 6,
                UserRole.MLOps_ENGINEER: 5,
                UserRole.DATA_SCIENTIST: 4,
                UserRole.ANALYST: 3,
                UserRole.VIEWER: 2,
                UserRole.API_USER: 1,
            }

            user_level = role_hierarchy.get(access_token.role, 0)
            required_level = role_hierarchy.get(role, 0)

            if user_level < required_level:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Insufficient role",
                            "message": f"Role {role.value} or higher required",
                        }
                    ),
                    403,
                )

            # Set user context
            g.current_user = access_token

            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user() -> Optional[AccessToken]:
    """Get current authenticated user from Flask context"""
    from flask import g

    return getattr(g, "current_user", None)
