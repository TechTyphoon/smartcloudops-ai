"""
Production Security Hardening
Phase 2C Week 2: Production Deployment - Security
"""

import hashlib
import ipaddress
import logging
import os
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Security validation utilities"""

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        score = 0

        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            score += 2
        else:
            score += 1

        # Character variety checks
        if re.search(r"[a-z]", password):
            score += 1
        else:
            issues.append("Password must contain lowercase letters")

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            issues.append("Password must contain uppercase letters")

        if re.search(r"\d", password):
            score += 1
        else:
            issues.append("Password must contain numbers")

        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>?]', password):
            score += 1
        else:
            issues.append("Password must contain special characters")

        # Common patterns check
        common_patterns = ["123", "abc", "password", "admin", "qwerty"]
        if any(pattern in password.lower() for pattern in common_patterns):
            issues.append("Password contains common patterns")
            score -= 1

        # Determine strength
        if score >= 5:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"

        return {
            "strength": strength,
            "score": max(0, score),
            "issues": issues,
            "valid": len(issues) == 0,
        }

    @staticmethod
    def sanitize_input(input_data: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not isinstance(input_data, str):
            input_data = str(input_data)

        # Truncate length
        if len(input_data) > max_length:
            input_data = input_data[:max_length]

        # Remove null bytes
        input_data = input_data.replace("\x00", "")

        # Basic XSS prevention (remove common script tags)
        input_data = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            input_data,
            flags=re.IGNORECASE | re.DOTALL,
        )
        input_data = re.sub(r"javascript:", "", input_data, flags=re.IGNORECASE)
        input_data = re.sub(r"on\w+\s*=", "", input_data, flags=re.IGNORECASE)

        return input_data.strip()

    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: List[str]) -> bool:
        """Validate file path to prevent directory traversal"""
        try:
            # Resolve path
            resolved_path = Path(file_path).resolve()

            # Check if path is within allowed directories
            for allowed_dir in allowed_dirs:
                allowed_path = Path(allowed_dir).resolve()
                try:
                    resolved_path.relative_to(allowed_path)
                    return True
                except ValueError:
                    continue

            return False
        except Exception:
            return False

    @staticmethod
    def validate_ip_address(ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""

    def __init__(self):
        self.requests = defaultdict(lambda: deque())
        self.blocked_ips = defaultdict(lambda: deque())
        self.persistent_blocks = set()

        # Rate limiting rules
        self.rules = {
            "default": {"requests": 100, "window": 3600},  # 100 requests per hour
            "api": {"requests": 1000, "window": 3600},  # 1000 API requests per hour
            "auth": {"requests": 10, "window": 300},  # 10 auth attempts per 5 minutes
            "upload": {"requests": 50, "window": 3600},  # 50 uploads per hour
        }

    def is_allowed(self, identifier: str, rule: str = "default") -> bool:
        """Check if request is allowed under rate limit"""
        if identifier in self.persistent_blocks:
            return False

        current_time = time.time()
        rule_config = self.rules.get(rule, self.rules["default"])
        window_size = rule_config["window"]
        max_requests = rule_config["requests"]

        # Clean old requests
        request_times = self.requests[identifier]
        while request_times and current_time - request_times[0] > window_size:
            request_times.popleft()

        # Check if under limit
        if len(request_times) < max_requests:
            request_times.append(current_time)
            return True

        # Rate limit exceeded
        self.blocked_ips[identifier].append(current_time)

        # Check for persistent blocking (multiple violations)
        blocks_in_hour = sum(
            1 for t in self.blocked_ips[identifier] if current_time - t < 3600
        )

        if blocks_in_hour >= 3:  # 3 violations in an hour = persistent block
            self.persistent_blocks.add(identifier)
            logger.warning(
                f"IP {identifier} persistently blocked for repeated violations"
            )

        return False

    def unblock_ip(self, ip_address: str):
        """Manually unblock an IP address"""
        self.persistent_blocks.discard(ip_address)
        if ip_address in self.requests:
            del self.requests[ip_address]
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
        logger.info(f"IP {ip_address} manually unblocked")

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        current_time = time.time()

        # Active rate limits (requests in last hour)
        active_limits = {}
        for identifier, request_times in self.requests.items():
            recent_requests = sum(1 for t in request_times if current_time - t < 3600)
            if recent_requests > 0:
                active_limits[identifier] = recent_requests

        # Recent blocks (in last hour)
        recent_blocks = {}
        for identifier, block_times in self.blocked_ips.items():
            recent_blocks_count = sum(1 for t in block_times if current_time - t < 3600)
            if recent_blocks_count > 0:
                recent_blocks[identifier] = recent_blocks_count

        return {
            "active_rate_limits": active_limits,
            "recent_blocks": recent_blocks,
            "persistent_blocks": list(self.persistent_blocks),
            "total_blocked_ips": len(self.persistent_blocks),
        }


class SecurityAuditor:
    """Security audit and vulnerability scanning"""

    def __init__(self):
        self.security_log = []
        self.vulnerability_checks = [
            self._check_file_permissions,
            self._check_secret_exposure,
            self._check_default_credentials,
            self._check_ssl_configuration,
            self._check_cors_configuration,
        ]

    def run_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "max_score": 0,
            "checks": [],
            "critical_issues": [],
            "recommendations": [],
        }

        # Run all vulnerability checks
        for check in self.vulnerability_checks:
            try:
                result = check()
                audit_results["checks"].append(result)
                audit_results["max_score"] += result.get("max_score", 10)
                audit_results["overall_score"] += result.get("score", 0)

                if result.get("severity") == "critical":
                    audit_results["critical_issues"].extend(result.get("issues", []))

                audit_results["recommendations"].extend(
                    result.get("recommendations", [])
                )

            except Exception as e:
                logger.error(f"Security check failed: {e}")
                audit_results["checks"].append(
                    {"check": check.__name__, "status": "error", "error": str(e)}
                )

        # Calculate security score percentage
        if audit_results["max_score"] > 0:
            score_percentage = (
                audit_results["overall_score"] / audit_results["max_score"]
            ) * 100
        else:
            score_percentage = 0

        audit_results["score_percentage"] = score_percentage

        # Determine overall security level
        if score_percentage >= 90:
            audit_results["security_level"] = "excellent"
        elif score_percentage >= 75:
            audit_results["security_level"] = "good"
        elif score_percentage >= 60:
            audit_results["security_level"] = "fair"
        else:
            audit_results["security_level"] = "poor"

        # Log security audit
        self.security_log.append(audit_results)

        return audit_results

    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file and directory permissions"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10

        # Check critical files
        critical_files = [
            "app/main.py",
            "deployment/production/config.py",
            "logs/",
            "data/",
        ]

        for file_path in critical_files:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                mode = oct(stat.st_mode)[-3:]

                # Check for overly permissive permissions
                if path.is_file() and mode in ["777", "666"]:
                    issues.append(
                        f"File {file_path} has overly permissive permissions: {mode}"
                    )
                elif path.is_dir() and mode == "777":
                    issues.append(
                        f"Directory {file_path} has overly permissive permissions: {mode}"
                    )
                else:
                    score += 2

        if not issues:
            score = max_score
            recommendations.append("File permissions are properly configured")
        else:
            recommendations.append("Review and restrict file permissions for security")

        return {
            "check": "file_permissions",
            "status": "passed" if not issues else "failed",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations,
            "severity": "medium" if issues else "low",
        }

    def _check_secret_exposure(self) -> Dict[str, Any]:
        """Check for exposed secrets in code"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10

        # Common secret patterns
        secret_patterns = [
            (r'SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']', "SECRET_KEY hardcoded"),
            (r'PASSWORD\s*=\s*["\'][^"\']+["\']', "Password hardcoded"),
            (r'API_KEY\s*=\s*["\'][^"\']+["\']', "API key hardcoded"),
            (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', "AWS credentials hardcoded"),
        ]

        # Check Python files
        for py_file in Path(".").glob("**/*.py"):
            try:
                with open(py_file, "r") as f:
                    content = f.read()

                for pattern, description in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"{description} in {py_file}")
            except Exception:
                continue

        if not issues:
            score = max_score
            recommendations.append("No hardcoded secrets detected")
        else:
            recommendations.append(
                "Move secrets to environment variables or secure config"
            )

        return {
            "check": "secret_exposure",
            "status": "passed" if not issues else "failed",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations,
            "severity": "critical" if issues else "low",
        }

    def _check_default_credentials(self) -> Dict[str, Any]:
        """Check for default credentials"""
        issues = []
        recommendations = []
        score = 10
        max_score = 10

        # Check environment variables for default values
        default_patterns = [
            ("SECRET_KEY", "dev-secret-key"),
            ("PASSWORD", "password"),
            ("ADMIN_PASSWORD", "admin"),
        ]

        for env_var, default_value in default_patterns:
            if os.getenv(env_var, "").lower() == default_value:
                issues.append(f"Default value detected for {env_var}")
                score -= 3

        if not issues:
            recommendations.append("No default credentials detected")
        else:
            recommendations.append("Change all default credentials before production")

        return {
            "check": "default_credentials",
            "status": "passed" if not issues else "failed",
            "score": max(0, score),
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations,
            "severity": "critical" if issues else "low",
        }

    def _check_ssl_configuration(self) -> Dict[str, Any]:
        """Check SSL/TLS configuration"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10

        ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
        ssl_cert = os.getenv("SSL_CERT_PATH")
        ssl_key = os.getenv("SSL_KEY_PATH")

        if ssl_enabled:
            score += 5

            if ssl_cert and Path(ssl_cert).exists():
                score += 3
            else:
                issues.append("SSL certificate file not found")

            if ssl_key and Path(ssl_key).exists():
                score += 2
            else:
                issues.append("SSL key file not found")
        else:
            issues.append("SSL/TLS not enabled")
            recommendations.append("Enable SSL/TLS for production deployment")

        return {
            "check": "ssl_configuration",
            "status": "passed" if ssl_enabled and not issues else "failed",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations,
            "severity": "medium" if not ssl_enabled else "low",
        }

    def _check_cors_configuration(self) -> Dict[str, Any]:
        """Check CORS configuration"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10

        cors_origins = os.getenv("CORS_ORIGINS", "")

        if cors_origins:
            origins = [origin.strip() for origin in cors_origins.split(",")]

            # Check for wildcard
            if "*" in origins:
                issues.append("CORS configured with wildcard (*) - security risk")
                score = 2
            else:
                score = 8

                # Check for localhost in production
                env = os.getenv("ENVIRONMENT", "development")
                if env == "production" and any(
                    "localhost" in origin for origin in origins
                ):
                    issues.append("Localhost origins configured in production")
                    score -= 2
        else:
            score = 5
            recommendations.append("Configure CORS origins explicitly")

        if not issues:
            score = max_score
            recommendations.append("CORS configuration is secure")

        return {
            "check": "cors_configuration",
            "status": "passed" if not issues else "warning",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations,
            "severity": "medium" if issues else "low",
        }


# Global security components
rate_limiter = RateLimiter()
security_auditor = SecurityAuditor()


def security_required(rule: str = "default"):
    """Decorator for rate limiting endpoints"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import jsonify, request

            # Get client IP
            client_ip = request.remote_addr or "unknown"

            # Check rate limit
            if not rate_limiter.is_allowed(client_ip, rule):
                logger.warning(f"Rate limit exceeded for {client_ip} on {rule}")
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Rate limit exceeded",
                            "message": "Too many requests. Please try again later.",
                        }
                    ),
                    429,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_input(**validators):
    """Decorator for input validation"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import jsonify, request

            # Validate request data
            if request.is_json:
                data = request.get_json()

                for field, validator_config in validators.items():
                    if field in data:
                        value = data[field]

                        # Apply validation rules
                        if "max_length" in validator_config:
                            value = SecurityValidator.sanitize_input(
                                value, validator_config["max_length"]
                            )
                            data[field] = value

                        if (
                            "required" in validator_config
                            and validator_config["required"]
                        ):
                            if not value or (
                                isinstance(value, str) and not value.strip()
                            ):
                                return (
                                    jsonify(
                                        {
                                            "status": "error",
                                            "error": f"Field {field} is required",
                                        }
                                    ),
                                    400,
                                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
