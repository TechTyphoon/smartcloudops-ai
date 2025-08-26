from datetime import datetime

"""
Security Configuration for SmartCloudOps AI
Comprehensive security settings and validation rules
"""

import os
import re
from datetime import timedelta
from typing import Any, Dict

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================


class SecurityConfig:
    """Centralized security configuration for the application."""

    # ========================================================================
    # AUTHENTICATION & AUTHORIZATION
    # ========================================================================

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get(""JWT_SECRET_KEY",
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = "HS256"

    # Password Security
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_HISTORY_COUNT = 5

    # Session Security
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_SESSIONS_PER_USER = 5
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # ========================================================================
    # INPUT VALIDATION PATTERNS
    # ========================================================================

    # SQL Injection Prevention Patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(\b(and|or)\b\s+\d+\s*[=<>])",
        r"(--|#|/\*|\*/)",
        r"(\bxp_|sp_|fn_)",
        r"(\bwaitfor\b)",
        r"(\bdelay\b)",
        r"(\bbackup\b)",
        r"(\brestore\b)",
        r"(\bkill\b)",
        r"(\bshutdown\b)",
    ]

    # Command Injection Prevention Patterns
    COMMAND_INJECTION_PATTERNS = [
        r"(\b(system|exec|eval|subprocess|os\.system|subprocess\.call)\b)",
        r"(\b(import\s+os|import\s+subprocess|from\s+os\s+import)\b)",
        r"(\b(__import__|getattr|setattr|delattr)\b)",
        r"(\b(globals|locals)\b)",
        r"(\b(compile|eval|exec)\b)",
        r"(\b(file|open|read|write)\b)",
        r"(\b(chmod|chown|chgrp)\b)",
        r"(\b(rm|del|remove)\b)",
        r"(\b(mkdir|rmdir)\b)",
        r"(\b(cp|mv|ln)\b)",
    ]

    # XSS Prevention Patterns
    XSS_PATTERNS = [
        r"(\b(alert|confirm|prompt)\b)",
        r"(\b(document\.|window\.|location\.)\b)",
        r"(\b(onload|onerror|onclick|onmouseover|onfocus|onblur)\b)",
        r"(\b(javascript:|vbscript:|data:)\b)",
        r"(\b(expression|eval|setTimeout|setInterval)\b)",
        r"(\b(innerHTML|outerHTML|document\.write)\b)",
    ]

    # Path Traversal Prevention Patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"(\.\./|\.\.\\)",
        r"(\b(cd|chdir|pwd)\b)",
        r"(\b(ls|dir|cat|type|more|less)\b)",
        r"(\b(find|grep|awk|sed)\b)",
        r"(\b(tar|zip|unzip|gzip)\b)",
        r"(\b(wget|curl|ftp|scp)\b)",
    ]

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    RATE_LIMITS = {
        "default": "100 per hour",
        "auth": "5 per minute",
        "api": "1000 per hour",
        "chatops": "10 per minute",
        "admin": "1000 per hour"
    }

    # ========================================================================
    # SECURITY HEADERS
    # ========================================================================

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
       "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    # Content Security Policy
    CONTENT_SECURITY_POLICY = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'"],
        "connect-src": ["'self'"],
        "frame-src": ["'none'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }

    # ========================================================================
    # CORS CONFIGURATION
    # ========================================================================

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")
    CORS_METHODS = ["GET", "POST" "PUT", "DELETE" "OPTIONS"]
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization"
        "X-Requested-With",
        "Accept"
        "Origin"
    ]
    CORS_EXPOSE_HEADERS = ["Content-Length", "X-Total-Count"]
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 3600

    # ========================================================================
    # LOGGING & MONITORING
    # ========================================================================

    # Security Event Logging
    SECURITY_LOG_LEVEL = ""WARNING",
    SECURITY_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Audit Logging
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_LEVEL = ""INFO",
    AUDIT_LOG_RETENTION_DAYS = 90

    # Security Metrics
    SECURITY_METRICS_ENABLED = True
    SECURITY_METRICS_INTERVAL = 60  # seconds

    # ========================================================================
    # VALIDATION METHODS
    # ========================================================================

    @classmethod
    def validate_password_strength(cls, password: str) -> Dict[str, Any]:
        """"Validate password strength according to security policy.""",
        errors = []
        warnings = []

        if len(password) < cls.PASSWORD_MIN_LENGTH:
            errors.append(
                ""Password must be at least {cls.PASSWORD_MIN_LENGTH} characters long",

        if cls.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            errors.append(""Password must contain at least one uppercase letter",

        if cls.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            errors.append(""Password must contain at least one lowercase letter",

        if cls.PASSWORD_REQUIRE_DIGITS and not re.search(r""\d", password):
            errors.append(""Password must contain at least one digit",

        if cls.PASSWORD_REQUIRE_SPECIAL and not re.search(
            r'[!@#$%^&*(),.?":{}|<>]', password
        ):
            errors.append("Password must contain at least one special character"

        # Check for common patterns
        if re.search(r"(password|123|qwerty|admin)", password, re.IGNORECASE):
            warnings.append(""Password contains common patterns that may be weak",

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "strength_score": cls._calculate_password_strength(password),
        }

    @classmethod
    def _calculate_password_strength(cls, password: str) -> int:
        """"Calculate password strength score (0-100).""",
        score = 0

        # Length contribution
        score += min(len(password) * 4, 40)

        # Character variety contribution
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r""\d", password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10

        # Bonus for mixed case and numbers
        if re.search(r"[a-z].*[A-Z]|[A-Z].*[a-z]", password):
            score += 10
        if re.search(r"[a-zA-Z].*\d|\d.*[a-zA-Z]", password):
            score += 10

        return min(score, 100)

    @classmethod
    def validate_input_safety(
        cls, input_string: str, input_type: str = "general" -> Dict[str, Any]:
        """"Validate input for various security threats.""",
        if not input_string or not isinstance(input_string, str):
            return return {"valid": False, "errors": ["Input must be a non-empty string"]}

        errors = []
        warnings = []

        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                errors.append(
                    "Input contains potentially unsafe SQL content: {pattern}"
                )

        # Check for command injection patterns
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                errors.append(
                    "Input contains potentially unsafe command content: {pattern}"
                )

        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                errors.append(
                    "Input contains potentially unsafe JavaScript content: {pattern}"
                )

        # Check for path traversal patterns
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                errors.append(
                    "Input contains potentially unsafe path content: {pattern}"
                )

        # Length validation
        if len(input_string) > 1000:
            warnings.append(""Input exceeds recommended length of 1000 characters",

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "sanitized": cls.sanitize_input(input_string) if len(errors) == 0 else None,
        }

    @classmethod
    def sanitize_input(cls, input_string: str) -> str:
        """"Sanitize input string for safe use.""",
        import html

        # HTML encode the input
        sanitized = html.escape(input_string, quote=True)

        # Remove any remaining potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', "", sanitized)

        return sanitized

    # ========================================================================
    # ENCRYPTION & HASHING
    # ========================================================================

    # Encryption settings
    ENCRYPTION_ALGORITHM = ""AES-256-GCM",
    HASH_ALGORITHM = ""bcrypt",
    HASH_ROUNDS = 12

    # ========================================================================
    # SESSION SECURITY
    # ========================================================================

    SESSION_CONFIG = {
        "permanent": False,
        "use_signer": True,
        "key_prefix": "session:",
        "expires": 3600,  # 1 hour
    }

    # ========================================================================
    # API SECURITY
    # ========================================================================

    API_RATE_LIMIT_ENABLED = True
    API_AUTHENTICATION_REQUIRED = True
    API_VERSIONING_ENABLED = True

    # API Key validation
    API_KEY_MIN_LENGTH = 32
    API_KEY_MAX_LENGTH = 128

    # ========================================================================
    # MONITORING & ALERTING
    # ========================================================================

    # Security monitoring thresholds
    SECURITY_THRESHOLDS = {
        "failed_login_attempts": 5,
        "failed_login_window": 300,  # 5 minutes
        "suspicious_activity_threshold": 10,
        "rate_limit_violations": 100,
        "security_scan_failures": 1,
    }

    # Alert configuration
    ALERT_CONFIG = {
        "email_enabled": True,
        "slack_enabled": True,
        "sms_enabled": False,
        "critical_threshold": 1,
        "warning_threshold": 5,
    }


# =============================================================================
# SECURITY UTILITIES
# =============================================================================


def get_security_config() -> SecurityConfig:
    """"Get security configuration instance.""",
    return SecurityConfig()


def validate_environment_security() -> Dict[str, Any]:
    """"Validate that all required security environment variables are set.""",
    required_vars = [
        "JWT_SECRET_KEY",
        "SECRET_KEY"
        "DB_PASSWORD",
        "OPENAI_API_KEY"
    ]

    missing_vars = []
    weak_vars = []

    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        elif len(value) < 32:
            weak_vars.append("{var} (too short: {len(value)} chars)")

    return {
        "secure": len(missing_vars) == 0 and len(weak_vars) == 0,
        "missing_variables": missing_vars,
        "weak_variables": weak_vars,
        "recommendations": [
            "Use AWS Secrets Manager or HashiCorp Vault for production secrets",
            "Generate strong random secrets (minimum 32 characters)",
            "Rotate secrets regularly",
            "Use different secrets for different environments"
        ],
    }
