#!/usr/bin/env python3
"""
Security Configuration for SmartCloudOps AI
Comprehensive security settings and validation rules
"""

import os
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
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default-secret-key")
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

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 100
    RATE_LIMIT_REQUESTS_PER_HOUR = 1000
    RATE_LIMIT_REQUESTS_PER_DAY = 10000

    # Rate Limiting by Endpoint
    ENDPOINT_RATE_LIMITS = {
        "/auth/login": {"requests_per_minute": 5, "requests_per_hour": 20},
        "/api/mlops/experiments": {"requests_per_minute": 30, "requests_per_hour": 200},
        "/api/anomalies": {"requests_per_minute": 50, "requests_per_hour": 500},
        "/api/remediation": {"requests_per_minute": 20, "requests_per_hour": 100},
    }

    # ========================================================================
    # ENCRYPTION & HASHING
    # ========================================================================

    # Encryption Configuration
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    HASH_ALGORITHM = "bcrypt"
    SALT_ROUNDS = 12

    # ========================================================================
    # AUDIT & LOGGING
    # ========================================================================

    # Audit Configuration
    AUDIT_ENABLED = True
    AUDIT_LOG_LEVEL = "INFO"
    AUDIT_RETENTION_DAYS = 90

    # Security Event Logging
    SECURITY_EVENTS = [
        "login_attempt",
        "logout",
        "password_change",
        "role_change",
        "permission_change",
        "data_access",
        "configuration_change",
        "security_violation",
    ]

    # ========================================================================
    # CORS & HEADERS
    # ========================================================================

    # CORS Configuration
    CORS_ENABLED = True
    CORS_ORIGINS = ["http://localhost:3000", "https://smartcloudops.ai"]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["Content-Type", "Authorization"]

    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' "
        "'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # ========================================================================
    # VALIDATION RULES
    # ========================================================================

    # Input Validation Rules
    VALIDATION_RULES = {
        "username": {
            "min_length": 3,
            "max_length": 50,
            "pattern": r"^[a-zA-Z0-9_-]+$",
            "description": "Username must be 3-50 characters, alphanumeric "
            "with underscore and dash",
        },
        "email": {
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "description": "Valid email address required",
        },
        "password": {
            "min_length": 12,
            "max_length": 128,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special": True,
            "description": "Password must be 12-128 characters with uppercase, "
            "lowercase, digits, and special characters",
        },
        "api_key": {
            "min_length": 32,
            "max_length": 64,
            "pattern": r"^[a-zA-Z0-9_-]+$",
            "description": "API key must be 32-64 characters, alphanumeric "
            "with underscore and dash",
        },
    }

    # ========================================================================
    # THREAT DETECTION
    # ========================================================================

    # Threat Detection Configuration
    THREAT_DETECTION_ENABLED = True
    THREAT_SCORE_THRESHOLD = 0.7
    THREAT_BLOCK_THRESHOLD = 0.9

    # Suspicious Activity Patterns
    SUSPICIOUS_PATTERNS = [
        r"(\b(admin|root|test|guest)\b)",
        r"(\b(password|passwd|pwd)\b)",
        r"(\b(select|union|insert|update|delete)\b)",
        r"(\b(script|javascript|vbscript)\b)",
        r"(\b(eval|exec|system)\b)",
    ]

    # ========================================================================
    # COMPLIANCE & STANDARDS
    # ========================================================================

    # Compliance Standards
    COMPLIANCE_STANDARDS = {
        "OWASP_TOP_10": True,
        "NIST_CYBERSECURITY": True,
        "ISO_27001": True,
        "GDPR": True,
        "HIPAA": False,  # Enable if handling healthcare data
    }

    # Data Classification
    DATA_CLASSIFICATION = {
        "public": {"encryption": False, "audit": False},
        "internal": {"encryption": True, "audit": True},
        "confidential": {"encryption": True, "audit": True, "access_control": True},
        "restricted": {
            "encryption": True,
            "audit": True,
            "access_control": True,
            "masking": True,
        },
    }

    # ========================================================================
    # METHODS
    # ========================================================================

    @classmethod
    def get_jwt_config(cls) -> Dict[str, Any]:
        """Get JWT configuration."""
        return {
            "secret_key": cls.JWT_SECRET_KEY,
            "access_token_expires": cls.JWT_ACCESS_TOKEN_EXPIRES,
            "refresh_token_expires": cls.JWT_REFRESH_TOKEN_EXPIRES,
            "algorithm": cls.JWT_ALGORITHM,
        }

    @classmethod
    def get_password_config(cls) -> Dict[str, Any]:
        """Get password security configuration."""
        return {
            "min_length": cls.PASSWORD_MIN_LENGTH,
            "require_uppercase": cls.PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": cls.PASSWORD_REQUIRE_LOWERCASE,
            "require_digits": cls.PASSWORD_REQUIRE_DIGITS,
            "require_special": cls.PASSWORD_REQUIRE_SPECIAL,
            "history_count": cls.PASSWORD_HISTORY_COUNT,
        }

    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            "enabled": cls.RATE_LIMIT_ENABLED,
            "requests_per_minute": cls.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "requests_per_hour": cls.RATE_LIMIT_REQUESTS_PER_HOUR,
            "requests_per_day": cls.RATE_LIMIT_REQUESTS_PER_DAY,
            "endpoint_limits": cls.ENDPOINT_RATE_LIMITS,
        }

    @classmethod
    def get_validation_patterns(cls) -> Dict[str, list]:
        """Get all validation patterns."""
        return {
            "sql_injection": cls.SQL_INJECTION_PATTERNS,
            "command_injection": cls.COMMAND_INJECTION_PATTERNS,
            "xss": cls.XSS_PATTERNS,
            "path_traversal": cls.PATH_TRAVERSAL_PATTERNS,
            "suspicious": cls.SUSPICIOUS_PATTERNS,
        }

    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        """Get security headers configuration."""
        return cls.SECURITY_HEADERS.copy()

    @classmethod
    def get_validation_rules(cls) -> Dict[str, Dict]:
        """Get input validation rules."""
        return cls.VALIDATION_RULES.copy()

    @classmethod
    def get_compliance_config(cls) -> Dict[str, bool]:
        """Get compliance configuration."""
        return cls.COMPLIANCE_STANDARDS.copy()

    @classmethod
    def get_data_classification(cls) -> Dict[str, Dict]:
        """Get data classification configuration."""
        return cls.DATA_CLASSIFICATION.copy()


# Global security configuration instance
security_config = SecurityConfig()
