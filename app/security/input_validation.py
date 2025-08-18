#!/usr/bin/env python3
"""
Security: Input Validation Module
Centralized input validation for security and data integrity
"""

import logging
import re
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)


def validate_string_input(
    value: Any, max_length: int = 1000, allow_empty: bool = False
) -> str:
    """
    Advanced security validation for string input.

    Args:
        value: Input value to validate
        max_length: Maximum allowed length
        allow_empty: Whether empty strings are allowed

    Returns:
        Validated string

    Raises:
        ValueError: If validation fails
    """
    if value is None:
        if allow_empty:
            return ""
        raise ValueError("String input cannot be None")

    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    # Remove null bytes and control characters (security)
    value = value.replace("\x00", "").strip()

    if not allow_empty and not value:
        raise ValueError("String input cannot be empty")

    if len(value) > max_length:
        raise ValueError(f"String input too long (max {max_length} characters)")

    # Comprehensive XSS and injection prevention
    dangerous_patterns = [
        r"<script[^>]*>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"onload\s*=",  # Event handlers
        r"onerror\s*=",
        r"onclick\s*=",
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
        r"vbscript:",  # VBScript URLs
        r"data:text/html",  # Data URLs
        r"<\?php",  # PHP tags
        r"<%",  # ASP tags
        r"\${",  # Template injection
        r"{{",  # Template injection
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"Potentially malicious input detected: {pattern}")
            raise ValueError(f"Potentially malicious input detected: {pattern}")

    # SQL injection prevention patterns
    sql_patterns = [
        r"union\s+select",
        r"drop\s+table",
        r"delete\s+from",
        r"insert\s+into",
        r"update\s+set",
        r"exec\s*\(",
        r"sp_executesql",
        r"xp_cmdshell",
        r"--\s*$",  # SQL comments
        r"/\*.*\*/",  # SQL block comments
    ]

    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"Potential SQL injection detected: {pattern}")
            raise ValueError(f"Potential SQL injection detected: {pattern}")

    return value


def validate_numeric_input(
    value: Any, min_val: float = None, max_val: float = None
) -> Union[int, float]:
    """
    Validate numeric input for security.

    Args:
        value: Input value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Validated numeric value

    Raises:
        ValueError: If validation fails
    """
    if value is None:
        raise ValueError("Numeric input cannot be None")

    if isinstance(value, str):
        try:
            # Try int first, then float
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            raise ValueError(f"Invalid numeric input: {value}")

    if not isinstance(value, (int, float)):
        raise ValueError(f"Expected numeric value, got {type(value).__name__}")

    if min_val is not None and value < min_val:
        raise ValueError(f"Value {value} below minimum {min_val}")

    if max_val is not None and value > max_val:
        raise ValueError(f"Value {value} above maximum {max_val}")

    return value


def validate_json_input(data: Any) -> Dict:
    """
    Validate JSON input for security.

    Args:
        data: Input data to validate

    Returns:
        Validated dictionary

    Raises:
        ValueError: If validation fails
    """
    if data is None:
        raise ValueError("JSON input cannot be None")

    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary, got {type(data).__name__}")

    # Prevent deeply nested objects (DoS protection)
    def check_depth(obj, max_depth=10, current_depth=0):
        if current_depth > max_depth:
            raise ValueError(f"JSON nesting too deep (max {max_depth} levels)")

        if isinstance(obj, dict):
            for value in obj.values():
                check_depth(value, max_depth, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, max_depth, current_depth + 1)

    check_depth(data)
    return data


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for security.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return ""

    # Remove path traversal attempts
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")

    # Remove dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "")

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename.strip()


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Validated email address

    Raises:
        ValueError: If email is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")

    email = email.strip().lower()

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValueError("Invalid email format")

    # Check for dangerous patterns
    dangerous_patterns = [
        r"javascript:",
        r"data:text/html",
        r"vbscript:",
        r"<script",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, email, re.IGNORECASE):
            raise ValueError(f"Email contains dangerous content: {pattern}")

    return email
