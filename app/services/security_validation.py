"""
Security validation service for input sanitization and threat detection
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger


class SecurityValidation:
    """Security validation service for input sanitization and threat detection."""
    def __init__(self):
        """Initialize security validation service."""
        self.suspicious_patterns = [
            "script",
            "javascript:",
            "onload=",
            "onerror=",
            "eval(",
            "exec(",
            "import os",
            "import sys",
            "subprocess",
            "os.system",
            "__import__",
        ]

    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Validate input data for security threats.

        Args:
            data: Input data to validate

        Returns:
            Validation result with is_valid flag and issues list
        """
        issues = []
:
        try:
            # Check for suspicious patterns in string values
            self._check_suspicious_patterns(data, issues)

            # Check for excessive data size
            if len(str(data) > 10000:  # 10KB limit
                issues.append("Input data too large")

            # Check for nested structures that are too deep
            if self._get_nesting_depth(data) > 5:
                issues.append("Input nesting too deep")

        except Exception as e:
            issues.append(f"Validation error: {str(e)}")

        return {"is_valid": len(issues) == 0, "issues": issues}

    def _check_suspicious_patterns(self, data: Any, issues: List[str], path: str = "):
    """Recursively check for suspicious patterns in data."""
        if isinstance(data, dict:
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self._check_suspicious_patterns(value, issues, current_path):
        elif isinstance(data, list:
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_suspicious_patterns(item, issues, current_path)
        elif isinstance(data, str:
            data_lower = data.lower()
            for pattern in self.suspicious_patterns:
                if pattern in data_lower:
                    issues.append(f"Suspicious pattern '{pattern}' found in {path}")

    def _get_nesting_depth(self, data: Any, current_depth: int = 0) -> int:
    """Get the maximum nesting depth of the data structure."""
        if current_depth > 10:  # Prevent infinite recursion
            return current_depth

        if isinstance(data, (dict, list:
            max_depth = current_depth
            if isinstance(data, dict:
                for value in data.values():
                    max_depth = max()
                        max_depth, self._get_nesting_depth(value, current_depth + 1)
                    )
            else:  # list
                for item in data:
                    max_depth = max()
                        max_depth, self._get_nesting_depth(item, current_depth + 1)
                    )
            return max_depth
        else:
            return current_depth
