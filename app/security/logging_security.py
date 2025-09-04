import logging
import re
from typing import Any, Dict


class SecurityLogger:
    """Logger that sanitizes sensitive data before logging."""

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        r'password["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # password: value
        r'passwd["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # passwd: value
        r'secret["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # secret: value
        r'token["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # token: value
        r'api_key["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # api_key: value
        r'apikey["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # apikey: value
        r'private_key["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',  # private_key: value
        r"'password':\s*'([^']+)'",  # 'password': 'value'
        r'"password":\s*"([^"]+)"',  # "password": "value"
    ]

    def __init__(self, logger_name: str = None):
        """Initialize the security logger."""
        self.logger = logging.getLogger(logger_name or __name__)
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for sensitive data detection."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.SENSITIVE_PATTERNS
        ]

    def _sanitize_string(self, text: str) -> str:
        """Sanitize sensitive data in a string."""
        sanitized = text

        # Replace any password-like values with [REDACTED]
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub(r"\1: [REDACTED]", sanitized)

        # Additional pattern to catch any remaining password values
        # This catches the case where the password appears in the string representation
        password_pattern = r"'password':\s*'([^']+)'"
        sanitized = re.sub(password_pattern, "'password': '[REDACTED]'", sanitized)

        return sanitized

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data in a dictionary."""
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, str):
                # Check if the key itself is sensitive
                if any(
                    sensitive in key.lower()
                    for sensitive in [
                        "password",
                        "passwd",
                        "secret",
                        "token",
                        "api_key",
                        "apikey",
                        "private_key",
                    ]
                ):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_string(value)
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive data in any data structure."""
        if isinstance(data, dict):
            return self._sanitize_dict(data)
        elif isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, (list, tuple)):
            return [self._sanitize_data(item) for item in data]
        else:
            return data

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitized data."""
        # If the message contains a dictionary representation, sanitize it properly
        if isinstance(message, str) and "{" in message and "}" in message:
            # Try to extract and sanitize dictionary-like structures
            import re

            # Find dictionary-like patterns and sanitize them
            dict_pattern = r"\{[^}]*\}"

            def sanitize_dict_match(match):
                dict_str = match.group(0)
                # Replace password values in the dictionary string
                sanitized = re.sub(
                    r"'password':\s*'[^']*'", "'password': '[REDACTED]'", dict_str
                )
                sanitized = re.sub(
                    r'"password":\s*"[^"]*"', '"password": "[REDACTED]"', sanitized
                )
                return sanitized

            sanitized_message = re.sub(dict_pattern, sanitize_dict_match, message)
        else:
            sanitized_message = self._sanitize_data(message)

        self.logger.info(sanitized_message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitized data."""
        sanitized_message = self._sanitize_data(message)
        self.logger.warning(sanitized_message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitized data."""
        sanitized_message = self._sanitize_data(message)
        self.logger.error(sanitized_message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitized data."""
        sanitized_message = self._sanitize_data(message)
        self.logger.debug(sanitized_message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitized data."""
        sanitized_message = self._sanitize_data(message)
        self.logger.critical(sanitized_message, *args, **kwargs)


# Global security logger instance
security_logger = SecurityLogger()


def get_security_logger(name: str = None) -> SecurityLogger:
    """Get a security logger instance."""
    return SecurityLogger(name)


def sanitize_log_data(data: Any) -> Any:
    """Sanitize data for logging."""
    return security_logger._sanitize_data(data)
