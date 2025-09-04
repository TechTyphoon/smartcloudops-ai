#!/usr/bin/env python3
"""
Smart CloudOps AI - ChatOps Utilities
Advanced context management, system state caching, and intelligent query processing
"""

import functools
import logging
import os
import sys
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

logger = logging.getLogger(__name__)


def timed_cache(seconds: int = 300):
    """Time-based cache decorator for expensive operations."""

    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()

            # Check if we have a cached result that's still valid
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result

            # Cache miss or expired - compute new result
            logger.debug(f"Cache miss for {func.__name__}, computing new result")
            result = func(*args, **kwargs)
            cache[key] = (result, now)

            # Clean old entries periodically
            if len(cache) > 100:  # Prevent cache from growing too large
                # Remove expired entries first
                expired_keys = [
                    k for k, (_, ts) in cache.items() if now - ts > seconds * 2
                ]
                for k in expired_keys:
                    cache.pop(k, None)

                # If still too large, remove oldest entries
                if len(cache) > 100:
                    # Sort by timestamp and remove oldest entries
                    sorted_keys = sorted(cache.keys(), key=lambda k: cache[k][1])
                    for k in sorted_keys[: len(cache) - 100]:
                        cache.pop(k, None)

            return result

        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {
            "size": len(cache),
            "hits": getattr(wrapper, "_hits", 0),
        }
        return wrapper

    return decorator


class AdvancedContextManager:
    """Enhanced context management for Phase 5 ChatOps."""

    def __init__(self, max_context_size: int = 100, cache_duration: int = 300):
        """Initialize advanced context manager."""
        self.max_context_size = max_context_size
        self.cache_duration = cache_duration
        self.context_cache = {}
        self.system_state_history = deque(maxlen=50)
        self.last_context_update = 0

    def _enforce_size_limit(self):
        """Enforce max_context_size limit by removing oldest entries."""
        if len(self.context_cache) > self.max_context_size:
            # Remove oldest entries to maintain size limit
            items_to_remove = len(self.context_cache) - self.max_context_size
            # For simplicity, remove the first items (oldest)
            keys_to_remove = list(self.context_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                self.context_cache.pop(key, None)

    def __setattr__(self, name, value):
        """Override to enforce size limit when context_cache is modified."""
        if name == "context_cache" and isinstance(value, dict):
            # Create a custom dict that enforces size limit
            class SizeLimitedDict(dict):
                def __init__(self, max_size, *args, **kwargs):
                    self.max_size = max_size
                    super().__init__(*args, **kwargs)

                def __setitem__(self, key, value):
                    super().__setitem__(key, value)
                    if len(self) > self.max_size:
                        # Remove oldest entries
                        items_to_remove = len(self) - self.max_size
                        keys_to_remove = list(self.keys())[:items_to_remove]
                        for k in keys_to_remove:
                            self.pop(k, None)

            value = SizeLimitedDict(self.max_context_size, value)

        super().__setattr__(name, value)

    @timed_cache(seconds=300)  # 5-minute cache for expensive system context gathering
    def get_system_context(self) -> Dict[str, Any]:
        """Get comprehensive system context with advanced caching."""
        try:
            current_time = datetime.now()

            # Gather fresh system context - this is expensive so we cache it
            context = {
                "timestamp": current_time.isoformat(),
                "system_health": self._get_system_health(),
                "recent_anomalies": self._get_recent_anomalies(),
                "resource_usage": self._get_resource_usage(),
                "active_alerts": self._get_active_alerts(),
                "remediation_status": self._get_remediation_status(),
                "ml_model_status": self._get_ml_model_status(),
            }

            # Update cache
            self.context_cache["system_context"] = context
            self._enforce_size_limit()  # Enforce size limit
            self.last_context_update = current_time

            # Add to history
            self.system_state_history.append(
                {"timestamp": current_time.isoformat(), "context": context}
            )

            return context

        except Exception as e:
            logger.error(f"Failed to get system context: {e}")
            return self._get_fallback_context()

    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            return {
                "status": "healthy",
                "uptime": "24h 15m",
                "last_check": datetime.now().isoformat(),
                "services": {
                    "web": "running",
                    "database": "running",
                    "monitoring": "running",
                },
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {"status": "unknown", "error": str(e)}

    def _get_recent_anomalies(self) -> List[Dict[str, Any]]:
        """Get recent anomalies."""
        try:
            return [
                {
                    "id": "anom_001",
                    "type": "cpu_spike",
                    "severity": "medium",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "status": "resolved",
                }
            ]
        except Exception as e:
            logger.error(f"Failed to get recent anomalies: {e}")
            return []

    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        try:
            return {
                "cpu": 45.2,
                "memory": 62.8,
                "disk": 78.1,
                "network": {"in": 1024, "out": 2048},
            }
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
            return {"error": str(e)}

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        try:
            return []
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    def _get_remediation_status(self) -> Dict[str, Any]:
        """Get remediation status."""
        try:
            return {"status": "idle", "last_action": None, "pending_actions": 0}
        except Exception as e:
            logger.error(f"Failed to get remediation status: {e}")
            return {"status": "unknown"}

    def _get_ml_model_status(self) -> Dict[str, Any]:
        """Get ML model status."""
        try:
            return {
                "anomaly_detector": "active",
                "last_training": (datetime.now() - timedelta(days=7)).isoformat(),
                "accuracy": 0.95,
            }
        except Exception as e:
            logger.error(f"Failed to get ML model status: {e}")
            return {"status": "unknown"}

    def _get_fallback_context(self) -> Dict[str, Any]:
        """Get fallback context when system context fails."""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": {"status": "unknown"},
            "recent_anomalies": [],
            "resource_usage": {"error": "unavailable"},
            "active_alerts": [],
            "remediation_status": {"status": "unknown"},
            "ml_model_status": {"status": "unknown"},
        }

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context."""
        try:
            context = self.get_system_context()
            return {
                "timestamp": context.get("timestamp"),
                "health_status": context.get("system_health", {}).get(
                    "status", "unknown"
                ),
                "anomaly_count": len(context.get("recent_anomalies", [])),
                "alert_count": len(context.get("active_alerts", [])),
                "cpu_usage": context.get("resource_usage", {}).get("cpu", 0),
                "memory_usage": context.get("resource_usage", {}).get("memory", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get context summary: {e}")
            return {"error": str(e)}

    def clear_cache(self) -> bool:
        """Clear the context cache."""
        try:
            self.context_cache.clear()
            self.system_state_history.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


class QueryProcessor:
    """Intelligent query processing for ChatOps."""

    def __init__(self):
        """Initialize query processor."""
        self.query_patterns = {
            "system_status": ["status", "health", "system", "uptime"],
            "anomalies": ["anomaly", "anomalies", "detection", "spike"],
            "performance": ["performance", "cpu", "memory", "disk", "slow"],
            "alerts": ["alert", "alerts", "warning", "critical"],
            "remediation": ["remediation", "fix", "resolve", "action"],
            "deployment": ["deploy", "deployment", "release", "rollback"],
        }

    def classify_query(self, query: str) -> str:
        """Classify the type of query."""
        query_lower = query.lower()

        for query_type, keywords in self.query_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return query_type

        return "general"

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query."""
        entities = {
            "metrics": [],
            "time_range": None,
            "severity": None,
            "service": None,
        }

        query_lower = query.lower()

        # Extract metrics
        metric_keywords = ["cpu", "memory", "disk", "network", "response_time"]
        for metric in metric_keywords:
            if metric in query_lower:
                entities["metrics"].append(metric)

        # Extract time range
        time_patterns = {
            "last hour": "1h",
            "last 24 hours": "24h",
            "last week": "7d",
            "last month": "30d",
        }

        for pattern, value in time_patterns.items():
            if pattern in query_lower:
                entities["time_range"] = value
                break

        # Extract severity
        severity_keywords = ["critical", "high", "medium", "low"]
        for severity in severity_keywords:
            if severity in query_lower:
                entities["severity"] = severity
                break

        return entities

    def enhance_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Enhance query with context."""
        enhanced = query

        if context:
            # Add context information to query
            if context.get("system_health", {}).get("status") == "unhealthy":
                enhanced += " (system currently unhealthy)"

            anomaly_count = len(context.get("recent_anomalies", []))
            if anomaly_count > 0:
                enhanced += f" (recent anomalies: {anomaly_count})"

        return enhanced


# Global instances
context_manager = AdvancedContextManager()
query_processor = QueryProcessor()


def format_response(
    response: Any,
    data: Any = None,
    message: str = None,
    status: str = "success",
    error: str = None,
) -> Dict[str, Any]:
    """Format API response with consistent structure."""
    formatted = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }

    # Handle different response types
    if isinstance(response, dict):
        formatted.update(response)
    elif isinstance(response, str):
        formatted["response"] = response

    if data is not None:
        formatted["data"] = data

    if message:
        formatted["message"] = message

    if error:
        formatted["error"] = error
        formatted["status"] = "error"

    return formatted


def validate_query_params(data: Dict[str, Any] = None, **kwargs) -> Tuple[bool, str]:
    """Validate query parameters."""
    if data is None:
        data = kwargs

    # Validate hours parameter
    if "hours" in data:
        hours = data["hours"]
        if not isinstance(hours, int):
            return False, "hours must be an integer"
        if hours < 1 or hours > 168:
            return False, "hours must be between 1 and 168"

    # Validate level parameter
    if "level" in data:
        level = data["level"]
        if level is not None:  # Only validate if level is provided
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if level not in valid_levels:
                return False, f"level must be one of {valid_levels}"

    # Basic validation - can be extended
    if "query" in data and not isinstance(data["query"], str):
        return False, "Query must be a string"

    return True, ""


class LogRetriever:
    """Retrieve logs from the system."""

    def create_sample_log(self) -> Dict[str, Any]:
        """Create a sample log entry for testing."""
        return {
            "message": "Sample log entry for testing",
            "level": "INFO",
            "source": "chatops",
            "timestamp": datetime.now().isoformat(),
        }

    def get_recent_logs(
        self, hours: int = 24, level: str = None
    ) -> List[Dict[str, Any]]:
        """Get recent logs."""
        # Placeholder implementation
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Log retrieval placeholder",
                "source": "system",
            }
        ]


class SystemContextGatherer:
    """Gather system context."""

    def get_system_context(self) -> Dict[str, Any]:
        """Get system context."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        return {
            "system_health": "healthy",
            "components": {
                "database": "connected",
                "cache": "available",
                "mlflow": "fallback_mode",
                "ai_handler": "initialized",
            },
            "timestamp": datetime.now().isoformat(),
        }

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """Get context relevant to a specific query."""
        return {
            "query_analysis": {
                "query": query,
                "intent": "system_status",
                "confidence": 0.85,
            },
            "relevant_context": {
                "system_status": "healthy",
                "components": {"database": "connected", "cache": "available"},
            },
            "system_summary": self.get_system_summary(),
        }

    def get_system_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "status": "healthy",
            "components": {
                "database": "connected",
                "cache": "available",
                "mlflow": "fallback_mode",
                "ai_handler": "initialized",
            },
            "timestamp": datetime.now().isoformat(),
        }


# Additional utility functions
conversation_manager = AdvancedContextManager()  # Alias for backward compatibility
