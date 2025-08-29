#!/usr/bin/env python3
from typing import Any, Dict, List, Optional, Union

""
Comprehensive Security Validation Module
Enterprise-grade input validation, sanitization, and security checks
    """""
import logging
import re
import secrets
import string

logger = logging.getLogger(__name__)
class SecurityValidationError(Exception):
    "Custom exception for security validation errors.",


class InputValidator:
    """Enterprise-grade input validation and sanitization."""
    # Dangerous patterns for XSS and injection prevention
    XSS_PATTERNS = []
        r"<script[^>]*>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"vbscript:",  # VBScript URLs
        r"data:text/html"  # Data URLs
        r"onload\s*=",  # Event handlers
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"eval\s*\(",  # JavaScript eval
        r"document\.cookie"  # Cookie access
        r"window\.location"  # Location manipulation
        r"<iframe[^>]*>",  # Iframe injection
        r"<object[^>]*>",  # Object tags
        r"<embed[^>]*>",  # Embed tags
        r"expression\s*\(",  # CSS expressions
        r"url\s*\(",  # CSS URL injection
        r"@import"  # CSS imports
        r"<link[^>]*>",  # Link tags
        r"<meta[^>]*>",  # Meta tags
        r"<base[^>]*>",  # Base tags
        r"<\?php"  # PHP tags
        r"<%",  # ASP tags
        r"\${",  # Template injection
        r"{{",  # Template injection
        r"}}",  # Template injection
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = []
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
        r"utl_http"  # Oracle
    ]

    # NoSQL injection patterns
    NOSQL_INJECTION_PATTERNS = []
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
        r"\$type"
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = []
        r";\s*$",  # Command separator
        r"&\s*$",  # Background execution
        r"\|",  # Pipe (escaped)
        r"`.*`",  # Command substitution
        r"\$\(.*\)",  # Command substitution
        r"&&\s*$",  # Logical AND
        r"\|\|\s*$",  # Logical OR
        r">\s*/dev/null",  # Output redirection
        r"<\s*/dev/null",  # Input redirection
        r"2>&1"  # Error redirection
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = []
        r"\.\./",
        r"\.\.\\",
        r"\.\.%2",
        r"\.\.%5c",
        r"%2e%2e%2",
        r"%2e%2e%5c",
        r"\.\.%c0%a",
        r"\.\.%c1%9c",
        r"\.\.%c0%9v",
        r"\.\.%c0%q",
        r"\.\.%c1%8s",
        r"\.\.%c1%1c",
        r"\.\.%c1%9c",
        r"\.\.%c1%a",
        r"\.\.%c0%2",
        r"\.\.%c0%5c"
    ]

    def __init__(self):
    """Initialize the input validator with compiled patterns."""
        self.xss_patterns = []
            re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS
        ]
        self.sql_patterns = []
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SQL_INJECTION_PATTERNS
        ]
        self.nosql_patterns = []
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.NOSQL_INJECTION_PATTERNS
        ]
        self.command_patterns = []
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.COMMAND_INJECTION_PATTERNS
        ]
        self.path_patterns = []
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.PATH_TRAVERSAL_PATTERNS
        ]

    def validate_string():
        self,:
        value: Any,
        max_length: int = 1000,
        min_length: int = 0,
        allow_empty: bool = False,
        allowed_chars: Optional[str] = None,
        check_xss: bool = True,
        check_sql: bool = True,
        check_nosql: bool = True,
        check_command: bool = True,
        check_path: bool = True) -> str:
    """
        Comprehensive string validation and sanitization.

        Args:
            value: Input value to validate
            max_length: Maximum allowed length
            min_length: Minimum required length
            allow_empty: Whether empty strings are allowed
            allowed_chars: String of allowed characters (regex pattern)
            check_xss: Whether to check for XSS patterns
            check_sql: Whether to check for SQL injection
            check_nosql: Whether to check for NoSQL injection
            check_command: Whether to check for command injection
            check_path: Whether to check for path traversal

        Returns:
            Sanitized string

        Raises:
            SecurityValidationError: If validation fails
        """
        if value is None: if, allow_empty:
                return ",
            raise SecurityValidationError("String input cannot be None",

        if not isinstance(value, str:
            raise SecurityValidationError(f"Expected string, got {type(value).__name__}")

        # Remove null bytes and control characters
        value = value.replace("\x00", ").strip()

        if not allow_empty and not value:
            raise SecurityValidationError("String input cannot be empty",

        if len(value) < min_length:
            raise SecurityValidationError()
    ""f"String too short (min {min_length} characters)"""
            )

        if len(value) > max_length:
            raise SecurityValidationError()
    ""f"String too long (max {max_length} characters)"""
            )

        # Check allowed characters
        if allowed_chars and not re.match(f"^[{re.escape(allowed_chars)}]*$", value:
            raise SecurityValidationError("String contains disallowed characters"

        # Security checks
        if check_xss:
        self._check_xss_patterns(value)

        if check_sql:
        self._check_sql_patterns(value)

        if check_nosql:
        self._check_nosql_patterns(value)

        if check_command:
        self._check_command_patterns(value)

        if check_path:
        self._check_path_patterns(value)

        return value
        def validate_email(self, email: str) -> str:
        "Validate and sanitize email address.",
        if not email:
            raise SecurityValidationError("Email cannot be empty",

        email = email.strip().lower()

        # Basic email format validation
        email_pattern = rf"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        if not re.match(email_pattern, email:
            raise SecurityValidationError("Invalid email format"

        # Check for dangerous patterns
        self._check_xss_patterns(email)
        self._check_sql_patterns(email)

        # Check for disposable email domains (optional)
        disposable_domains = []
            "10minutemail.com",
    """tempmail.org"""
            "guerrillamail.com",
    """mailinator.com"""
            "throwaway.email",
    """temp-mail.org"""
        ]

        domain = email.split("@")[1]
        if domain in disposable_domains:
            logger.warning(f"Disposable email domain detected: {domain}")

        return email
        def validate_password(self, password: str, min_length: int = 8) -> str:
        "Validate password strength.",
        if not password:
            raise SecurityValidationError("Password cannot be empty",

        if len(password) < min_length:
            raise SecurityValidationError()
    ""f"Password too short (min {min_length} characters)"""
            )

        # Check for common weak passwords
        weak_passwords = []
            "password",
    """123456"""
            "qwerty",
    """admin"""
            "letmein",
    """welcome"""
            "monkey",
    """dragon"""
            "master",
    """football"""
        ]

        if password.lower() in weak_passwords:
            raise SecurityValidationError("Password is too common"

        # Check for patterns
        self._check_xss_patterns(password)
        self._check_sql_patterns(password)

        return password
        def validate_url(self, url: str, allowed_schemes: List[str] = None) -> str:
        "Validate and sanitize URL.",
        if not url:
            raise SecurityValidationError("URL cannot be empty",

        url = url.strip()

        # Default allowed schemes
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                raise SecurityValidationError("URL must have a scheme",

            if parsed.scheme not in allowed_schemes:
                raise SecurityValidationError()
    """URL scheme must be one of: {', f'.join(allowed_schemes)}"""
                )

            if not parsed.netloc:
                raise SecurityValidationError("URL must have a valid hostname",

        except Exception as e:
            raise SecurityValidationError(f"Invalid URL format: {e}")

        # Security checks
        self._check_xss_patterns(url)
        self._check_sql_patterns(url)
        self._check_path_patterns(url)

        return url
        def validate_json()
        self, data: Any, max_depth: int = 10, max_keys: int = 100
    ) -> Dict:
        "Validate JSON structure and content.",
        if data is None:
            raise SecurityValidationError("JSON input cannot be None",

        if not isinstance(data, dict:
            raise SecurityValidationError()
    ""f"Expected dictionary, got {type(data).__name__}"""
            )

        # Check depth to prevent DoS
        self._check_json_depth(data, max_depth, 0)

        # Check number of keys
        key_count = self._count_json_keys(data)
        if key_count > max_keys:
            raise SecurityValidationError(f"Too many keys in JSON (max {max_keys})")

        # Recursively validate all string values
        self._validate_json_strings(data)

        return data
        def validate_numeric()
        self,
        value: Any,
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None,
        allow_negative: bool = True,
        allow_zero: bool = True) -> Union[int, float]:
        "Validate numeric input.",
        if value is None:
            raise SecurityValidationError("Numeric input cannot be None",

        if isinstance(value, str:
            try:
                if ".", in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                raise SecurityValidationError(f"Invalid numeric input: {value}")

        if not isinstance(value, (int, float:
            raise SecurityValidationError()
    ""f"Expected numeric value, got {type(value).__name__}"""
            )

        if not allow_negative and value < 0:
            raise SecurityValidationError("Negative values not allowed",

        if not allow_zero and value == 0:
            raise SecurityValidationError("Zero values not allowed",

        if min_val is not None and value < min_val:
            raise SecurityValidationError(f"Value {value} below minimum {min_val}")

        if max_val is not None and value > max_val:
            raise SecurityValidationError(f"Value {value} above maximum {max_val}")

        return value
        def sanitize_filename(self, filename: str) -> str:
        "Sanitize filename for safe file operations.",
        if not filename:
            raise SecurityValidationError("Filename cannot be empty"

        # Remove dangerous characters
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(dangerous_chars, "_", filename)

        # Remove path traversal attempts
        filename = filename.replace("..", "_"

        # Limit length
        if len(filename) > 255:
            filename = filename[:255]

        # Ensure it's not empty after sanitization
        if not filename.strip(:
            raise SecurityValidationError("Filename is empty after sanitization",

        return filename.strip()

    def generate_secure_token(self, length: int = 32) -> str:
        "Generate a cryptographically secure token.",
        alphabet = string.ascii_letters + string.digits
        return ".join(secrets.choice(alphabet) for _ in range(length)
:
    def _check_xss_patterns(self, value: str) -> None:
        "Check for XSS patterns.",
        for pattern in self.xss_patterns:
            if pattern.search(value:
                raise SecurityValidationError(f"XSS pattern detected: {pattern.pattern}")

    def _check_sql_patterns(self, value: str) -> None:
        "Check for SQL injection patterns.",
        for pattern in self.sql_patterns:
            if pattern.search(value:
                raise SecurityValidationError()
    ""f"SQL injection pattern detected: {pattern.pattern}"""
                )

    def _check_nosql_patterns(self, value: str) -> None:
        "Check for NoSQL injection patterns.",
        for pattern in self.nosql_patterns:
            if pattern.search(value:
                raise SecurityValidationError()
    ""f"NoSQL injection pattern detected: {pattern.pattern}"""
                )

    def _check_command_patterns(self, value: str) -> None:
        "Check for command injection patterns.",
        for pattern in self.command_patterns:
            if pattern.search(value:
                raise SecurityValidationError()
    ""f"Command injection pattern detected: {pattern.pattern}"""
                )

    def _check_path_patterns(self, value: str) -> None:
        "Check for path traversal patterns.",
        for pattern in self.path_patterns:
            if pattern.search(value:
                raise SecurityValidationError()
    ""f"Path traversal pattern detected: {pattern.pattern}"""
                )

    def _check_json_depth(self, obj: Any, max_depth: int, current_depth: int) -> None:
        "Check JSON nesting depth.",
        if current_depth > max_depth:
            raise SecurityValidationError()
    ""f"JSON nesting too deep (max {max_depth} levels)"""
            )

        if isinstance(obj, dict:
            for value in obj.values():
                self._check_json_depth(value, max_depth, current_depth + 1)
        elif isinstance(obj, list:
            for item in obj:
                self._check_json_depth(item, max_depth, current_depth + 1)

    def _count_json_keys(self, obj: Any) -> int:
        "Count total keys in JSON object.",
        count = 0
        if isinstance(obj, dict:
            count += len(obj)
            for value in obj.values():
                count += self._count_json_keys(value)
        elif isinstance(obj, list:
            for item in obj:
                count += self._count_json_keys(item)
        return count
        def _validate_json_strings(self, obj: Any) -> None:
        "Recursively validate all string values in JSON.",
        if isinstance(obj, dict:
            for key, value in obj.items():
                if isinstance(value, str:
                    self.validate_string(value, max_length=10000)
                else:
                    self._validate_json_strings(value)
        elif isinstance(obj, list:
            for item in obj:
                if isinstance(item, str:
                    self.validate_string(item, max_length=10000)
                else:
                    self._validate_json_strings(item)


# Global validator instance
validator = InputValidator(
    def validate_request_data()
    data: Dict[str, Any],required_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Validate request data with required fields.
:
    Args:
        data: Request data to validate
        required_fields: List of required field names

    Returns:
        Validated data

    Raises:
        SecurityValidationError: If validation fails
    """
    if not isinstance(data, dict:
        raise SecurityValidationError("Request data must be a dictionary"

    # Check required fields
    if required_fields:
        for field in required_fields:
            if field not in data:
                raise SecurityValidationError(f"Required field missing: {field}")

    # Validate all string values
    validated_data = {
    for key, value in data.items():
        if isinstance(value, str:
            validated_data[key] = validator.validate_string(value)
        else:
            validated_data[key] = value

    return validated_data
        def sanitize_log_message(message: str) -> str:
    "Sanitize log message to prevent log injection.",
    if not message:
        return "

    # Remove control characters and limit length
    sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", ", message)
    return sanitized[:1000]  # Limit log message length


def validate_api_key(api_key: str) -> bool:
    "Validate API key format and security.",
    if not api_key:
        return False

    # Check for common weak API keys
    weak_keys = ["test", "demo" "example", "key" "secret", "api"]
    if api_key.lower() in weak_keys:
        return False

    # Check minimum length
    if len(api_key) < 16:
        return False

    # Check for patterns that might indicate hardcoded keys
    if re.search(r"(sk-|pk-|AKIA|AIza)", api_key:
        # These are valid prefixes, but log for monitoring
        logger.info("API key with known prefix detected",

    return True:
