#!/usr/bin/env python3
"""
Comprehensive Security Validation Module
Enterprise-grade input validation, sanitization, and security checks
"""

import logging
import re
import secrets
import string
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SecurityValidationError(Exception):
    """Custom exception for security validation errors."""


class InputValidator:
    """Enterprise-grade input validation and sanitization."""

    # Dangerous patterns for XSS and injection prevention
    XSS_PATTERNS = [
        r"<script[^>]*>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"vbscript:",  # VBScript URLs
        r"data:text/html",  # Data URLs
        r"onload\s*=",  # Event handlers
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"eval\s*\(",  # JavaScript eval
        r"document\.cookie",  # Cookie access
        r"window\.location",  # Location manipulation
        r"<iframe[^>]*>",  # Iframe injection
        r"<object[^>]*>",  # Object tags
        r"<embed[^>]*>",  # Embed tags
        r"expression\s*\(",  # CSS expressions
        r"url\s*\(",  # CSS URL injection
        r"@import",  # CSS imports
        r"<link[^>]*>",  # Link tags
        r"<meta[^>]*>",  # Meta tags
        r"<base[^>]*>",  # Base tags
        r"<\?php",  # PHP tags
        r"<%",  # ASP tags
        r"\${",  # Template injection
        r"{{",  # Template injection
        r"}}",  # Template injection
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"union\s+select",
        r"union\s+all\s+select",
        r"drop\s+table",
        r"delete\s+from",
        r"insert\s+into",
        r"update\s+set",
        r"exec\s*\(",
        r"execute\s*\(",
        r"sp_executesql",
        r"xp_cmdshell",
        r"xp_",  # Extended stored procedures
        r"sp_",  # System stored procedures
        r"--\s*$",  # SQL comments
        r"/\*.*\*/",  # SQL block comments
        r"waitfor\s+delay",  # Time-based attacks
        r"benchmark\s*\(",  # MySQL benchmark
        r"sleep\s*\(",  # MySQL sleep
        r"pg_sleep\s*\(",  # PostgreSQL sleep
        r"dbms_pipe",  # Oracle
        r"utl_http",  # Oracle
        r"\bOR\s+\d+\s*=\s*\d+",  # OR 1=1, OR 2=2, etc.
        r"\bAND\s+\d+\s*=\s*\d+",  # AND 1=1, AND 2=2, etc.
        r"'\s*OR\s*'",  # ' OR '
        r"'\s*AND\s*'",  # ' AND '
        r"'\s*;\s*",  # '; (semicolon after quote)
        r"'\s*--\s*",  # '-- (comment after quote)
        r"'\s*/\*",  # '/* (block comment after quote)
        r"\*\s*/\s*'",  # */' (block comment before quote)
    ]

    # NoSQL injection patterns
    NOSQL_INJECTION_PATTERNS = [
        r"\$where",
        r"\$ne",
        r"\$gt",
        r"\$lt",
        r"\$regex",
        r"\$exists",
        r"\$in",
        r"\$nin",
        r"\$or",
        r"\$and",
        r"\$not",
        r"\$nor",
        r"\$all",
        r"\$elemMatch",
        r"\$size",
        r"\$type",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r";\s*$",  # Command separator
        r"&\s*$",  # Background execution
        r"\|\s*$",  # Pipe at end
        r"`.*`",  # Command substitution
        r"\$\(.*\)",  # Command substitution
        r"exec\s*\(",
        r"system\s*\(",
        r"subprocess\.",
        r"os\.system",
        r"eval\s*\(",
        r"execfile\s*\(",
        r"raw_input\s*\(",
        r";\s+\w+",  # ; command
        r"\|\s+\w+",  # | command
        r"&&\s+\w+",  # && command
        r"\|\|\s+\w+",  # || command
        r"`\w+`",  # `command`
        r"\$\(\w+\)",  # $(command)
    ]

    def __init__(self):
        """Initialize the input validator."""
        self.compiled_patterns = {
            "xss": [
                re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS
            ],
            "sql": [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.SQL_INJECTION_PATTERNS
            ],
            "nosql": [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.NOSQL_INJECTION_PATTERNS
            ],
            "command": [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.COMMAND_INJECTION_PATTERNS
            ],
        }

    def validate_string(
        self, value: str, max_length: int = 1000, allow_html: bool = False
    ) -> str:
        """Validate and sanitize a string input."""
        if not isinstance(value, str):
            raise SecurityValidationError("Input must be a string")

        # Check length
        if len(value) > max_length:
            raise SecurityValidationError(
                f"Input too long (max {max_length} characters)"
            )

        # Check for dangerous patterns
        if not allow_html:
            self._check_dangerous_patterns(value)

        # Sanitize if needed
        if not allow_html:
            value = self._sanitize_html(value)

        return value.strip()

    def validate_email(self, email: str) -> str:
        """Validate email address format."""
        if not isinstance(email, str):
            raise SecurityValidationError("Email must be a string")

        email = email.strip().lower()

        # Basic email regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise SecurityValidationError("Invalid email format")

        # Check for dangerous patterns
        self._check_dangerous_patterns(email)

        return email

    def validate_url(self, url: str, allowed_schemes: List[str] = None) -> str:
        """Validate URL format and security."""
        if not isinstance(url, str):
            raise SecurityValidationError("URL must be a string")

        url = url.strip()

        # Default allowed schemes
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        # Check scheme
        if not any(url.startswith(f"{scheme}://") for scheme in allowed_schemes):
            raise SecurityValidationError(
                f"URL scheme must be one of: {', '.join(allowed_schemes)}"
            )

        # Check for dangerous patterns
        self._check_dangerous_patterns(url)

        return url

    def validate_integer(
        self, value: Any, min_value: int = None, max_value: int = None
    ) -> int:
        """Validate integer input."""
        try:
            if isinstance(value, str):
                value = int(value)
            elif not isinstance(value, int):
                raise SecurityValidationError("Input must be an integer")

            if min_value is not None and value < min_value:
                raise SecurityValidationError(f"Value must be at least {min_value}")

            if max_value is not None and value > max_value:
                raise SecurityValidationError(f"Value must be at most {max_value}")

            return value
        except ValueError:
            raise SecurityValidationError("Invalid integer format")

    def validate_float(
        self, value: Any, min_value: float = None, max_value: float = None
    ) -> float:
        """Validate float input."""
        try:
            if isinstance(value, str):
                value = float(value)
            elif not isinstance(value, (int, float)):
                raise SecurityValidationError("Input must be a number")

            if min_value is not None and value < min_value:
                raise SecurityValidationError(f"Value must be at least {min_value}")

            if max_value is not None and value > max_value:
                raise SecurityValidationError(f"Value must be at most {max_value}")

            return value
        except ValueError:
            raise SecurityValidationError("Invalid number format")

    def validate_list(
        self, value: Any, max_items: int = 100, item_validator: callable = None
    ) -> List:
        """Validate list input."""
        if not isinstance(value, list):
            raise SecurityValidationError("Input must be a list")

        if len(value) > max_items:
            raise SecurityValidationError(f"List too long (max {max_items} items)")

        if item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_items.append(item_validator(item))
                except Exception as e:
                    raise SecurityValidationError(
                        f"Invalid item at index {i}: {str(e)}"
                    )
            return validated_items

        return value

    def validate_dict(
        self,
        value: Any,
        required_keys: List[str] = None,
        optional_keys: List[str] = None,
    ) -> Dict:
        """Validate dictionary input."""
        if not isinstance(value, dict):
            raise SecurityValidationError("Input must be a dictionary")

        # Check required keys
        if required_keys:
            for key in required_keys:
                if key not in value:
                    raise SecurityValidationError(f"Missing required key: {key}")

        # Check for unexpected keys
        if optional_keys:
            allowed_keys = set(required_keys or []) | set(optional_keys)
            unexpected_keys = set(value.keys()) - allowed_keys
            if unexpected_keys:
                raise SecurityValidationError(
                    f"Unexpected keys: {', '.join(unexpected_keys)}"
                )

        return value

    def _check_dangerous_patterns(self, value: str):
        """Check for dangerous patterns in input."""
        for pattern_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(value):
                    logger.warning(
                        f"Pattern '{pattern.pattern}' matched in input: '{value}'"
                    )
                    raise SecurityValidationError(
                        f"Potentially dangerous {pattern_type.upper()} pattern detected"
                    )

    def _sanitize_html(self, value: str) -> str:
        """Sanitize HTML content."""
        # Remove script tags and their content
        value = re.sub(
            r"<script[^>]*>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove other dangerous tags
        dangerous_tags = ["iframe", "object", "embed", "link", "meta", "base"]
        for tag in dangerous_tags:
            value = re.sub(
                f"<{tag}[^>]*>.*?</{tag}>", "", value, flags=re.IGNORECASE | re.DOTALL
            )
            value = re.sub(f"<{tag}[^>]*/?>", "", value, flags=re.IGNORECASE)

        # Remove event handlers
        event_handlers = [
            "onload",
            "onerror",
            "onclick",
            "onmouseover",
            "onfocus",
            "onblur",
        ]
        for handler in event_handlers:
            value = re.sub(
                f"{handler}\\s*=\\s*[\"'][^\"']*[\"']", "", value, flags=re.IGNORECASE
            )

        return value

    def _validate_sql_input(self, value: str) -> Dict[str, Any]:
        """Validate input for SQL injection patterns."""
        for pattern in self.compiled_patterns["sql"]:
            if pattern.search(value):
                return {
                    "is_valid": False,
                    "error": "SQL injection pattern detected",
                }
        return {"is_valid": True}

    def _validate_xss_input(self, value: str) -> Dict[str, Any]:
        """Validate input for XSS patterns."""
        for pattern in self.compiled_patterns["xss"]:
            if pattern.search(value):
                return {"is_valid": False, "error": "XSS pattern detected"}
        return {"is_valid": True}

    def _validate_command_input(self, value: str) -> Dict[str, Any]:
        """Validate input for command injection patterns."""
        for pattern in self.compiled_patterns["command"]:
            if pattern.search(value):
                return {
                    "is_valid": False,
                    "error": "Command injection pattern detected",
                }
        return {"is_valid": True}

    def _validate_path_input(self, value: str) -> Dict[str, Any]:
        """Validate input for path traversal patterns."""
        path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"\.\.%2e%2e",
            r"\.\.%252e%252e",
            r"/etc/passwd",
            r"/etc/shadow",
            r"C:\\Windows\\System32",
            r"file:///",
            r"file://",
        ]
        for pattern in path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return {
                    "is_valid": False,
                    "error": "Path traversal pattern detected",
                }
        return {"is_valid": True}

    def _validate_general_input(self, value: str) -> Dict[str, Any]:
        """Validate input for general dangerous patterns."""
        try:
            self._check_dangerous_patterns(value)
            return {"is_valid": True}
        except SecurityValidationError as e:
            return {"is_valid": False, "error": str(e)}

    def validate_input(
        self, value: str, validation_type: str = "general"
    ) -> Dict[str, Any]:
        """Validate input based on the specified validation type."""
        if not isinstance(value, str):
            return {"is_valid": False, "error": "Input must be a string"}

        try:
            validation_methods = {
                "sql": self._validate_sql_input,
                "xss": self._validate_xss_input,
                "command": self._validate_command_input,
                "path": self._validate_path_input,
            }

            if validation_type in validation_methods:
                return validation_methods[validation_type](value)
            else:  # general validation
                return self._validate_general_input(value)

        except Exception as e:
            return {"is_valid": False, "error": f"Validation error: {str(e)}"}

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        if length < 8:
            raise SecurityValidationError("Token length must be at least 8 characters")

        return secrets.token_urlsafe(length)

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        if not isinstance(password, str):
            raise SecurityValidationError("Password must be a string")

        if len(password) < 8:
            raise SecurityValidationError("Password must be at least 8 characters long")

        # Check for different character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)

        # Calculate strength score
        score = 0
        if has_upper:
            score += 1
        if has_lower:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1
        if len(password) >= 12:
            score += 1

        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 3:
            strength = "medium"

        return {
            "valid": score >= 3,
            "strength": strength,
            "score": score,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_special": has_special,
            "length": len(password),
        }


# Global validator instance
input_validator = InputValidator()
