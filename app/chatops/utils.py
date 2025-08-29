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
                expired_keys = [
                    k for k, (_, ts) in cache.items() if now - ts > seconds * 2
                ]
                for k in expired_keys[:50]:  # Remove up to 50 expired entries
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
