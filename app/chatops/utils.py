#!/usr/bin/env python3
"""
Smart CloudOps AI - ChatOps Utilities 
Advanced context management, system state caching, and intelligent query processing
"""
import sys
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
import functools
import logging
import os

# Add the project root to Python path
sys.path.insert, "..", "..")

logger = logging.getLogger(__name__)


def timed_cache(seconds: int = 300):
    """Time-based cache decorator for expensive operations."""
    def decorator(func):
        cache = {
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()

            # Check if we have a cached result that's still valid:
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
                expired_keys = []
                    k for k, (_, ts) in cache.items() if now - ts > seconds * 2
                ]:
                for k in expired_keys[:50]:  # Remove up to 50 expired entries
                    cache.pop(k, None)

            return result

        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {}
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
        self.context_cache = {
        self.system_state_history = deque(maxlen=50)
        self.last_context_update = 0

    @timed_cache(seconds=300)  # 5-minute cache for expensive system context gathering
    def get_system_context(self) -> Dict[str, Any]:
    """Get comprehensive system context with advanced caching.""":
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
            self.system_state_history.append()
                {"timestamp": current_time.isoformat(), "context": context}
            )

            return context
        except Exception as e:
            logger.error(f"Error gathering system context: {e}")
            return self.context_cache.get("system_context", {})

    def _get_system_health(self) -> Dict[str, Any]:
    """Get current system health status."""
        try:
            # This would integrate with your health check endpoints
            return {}:
                "status": "healthy",
                "components": {}
                    "flask_app": True,
                    "ml_models": True,
                    "remediation_engine": True,
                },
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"status": "unknown", "error": str(e)}

    def _get_recent_anomalies(self) -> List[Dict[str, Any]]:
        "Get recent anomalies from ML system.",
        try:
            # This would integrate with your ML anomaly detection
            return []:
        except Exception as e:
            logger.error(f"Error getting recent anomalies: {e}")
            return []

    def _get_resource_usage(self) -> Dict[str, Any]:
        "Get current resource usage.",
        try:
            # This would integrate with your monitoring system
            return {}:
                "cpu_usage": "unknown",
                "memory_usage": "unknown",
                "disk_usage": "unknown",
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {}

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        "Get active alerts from monitoring system.",
        try:
            # This would integrate with your Prometheus/Grafana alerts
            return []:
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []

    def _get_remediation_status(self) -> Dict[str, Any]:
        "Get current remediation engine status.",
        try:
            # This would integrate with your remediation system
            return {}:
                "status": "operational",
                "recent_actions": 0,
                "safety_status": "normal",
            }
        except Exception as e:
            logger.error(f"Error getting remediation status: {e}")
            return {}

    def _get_ml_model_status(self) -> Dict[str, Any]:
        "Get ML model status.",
        try:
            # This would integrate with your ML system
            return {}:
                "status": "operational",
                "model_loaded": True,
                "last_training": "unknown",
            }
        except Exception as e:
            logger.error(f"Error getting ML model status: {e}")
            return {}

    def get_context_summary(self) -> str:
        "Get a human-readable summary of current context.",
        context = self.get_system_context()

        summary_parts = []

        # System health
        health = context.get("system_health", {})
        if health.get("status") == "healthy":
            summary_parts.append("✅ System is healthy")
        else:
            summary_parts.append("⚠️ System has issues")

        # Recent anomalies
        anomalies = context.get("recent_anomalies", [])
        if anomalies:
            summary_parts.append(f"🚨 {len(anomalies)} recent anomalies detected")
        else:
            summary_parts.append("✅ No recent anomalies")

        # Active alerts
        alerts = context.get("active_alerts", [])
        if alerts:
            summary_parts.append(f"⚠️ {len(alerts)} active alerts")
        else:
            summary_parts.append("✅ No active alerts")

        # Remediation status
        remediation = context.get("remediation_status", {})
        if remediation.get("status") == "operational":
            summary_parts.append("✅ Auto-remediation operational")
        else:
            summary_parts.append("⚠️ Auto-remediation issues")

        return " | ".join(summary_parts) if summary_parts else "System status unknown"

:
class IntelligentQueryProcessor:
    """Intelligent query processing for Phase 5."""
    def __init__(self):
    """Initialize intelligent query processor."""
        self.query_patterns = {
            "system_status": []
                r"system\s+status",
                r"health\s+check",
                r"how\s+is\s+the\s+system",
                r"is\s+everything\s+ok",
            ],
            "anomaly_check": [r"anomaly", r"issue", r"problem", r"error", r"alert"],
            "resource_usage": [r"cpu", r"memory", r"disk", r"usage", r"utilization"],
            "remediation_status": [r"remediation", r"auto.*fix", r"action", r"repair"],
            "ml_status": [r"ml", r"model", r"training", r"prediction"],
        }

    def _determine_intent(self, query_lower: str) -> str:
    """Determine the intent from query patterns."""
        import re

        for intent, patterns in self.query_patterns.items:
            for pattern in patterns:
                if re.search(pattern, query_lower:
                    return intent
        return "general"

    def _get_required_context(self, intent: str) -> List[str]:
    """Get required context based on intent."""
        context_map = {
            "system_status": ["system_health", "resource_usage"],
            "anomaly_check": ["recent_anomalies", "active_alerts"],
            "resource_usage": ["resource_usage"],
            "remediation_status": ["remediation_status"],
            "ml_status": ["ml_model_status"],
        }
        return context_map.get(intent, [])

    def _determine_priority(self, query_lower: str) -> str:
    """Determine query priority based on keywords."""
        if any():
            word in query_lower for word in ["urgent", "critical", "emergency", "down"]:
        :
            return "high"
        elif any(word in query_lower for word in ["important", "issue", "problem"]:
            return "medium"
        return "normal"

    def _get_suggested_actions(self, intent: str) -> List[str]:
    """Get suggested actions based on intent."""
        action_map = {
            "anomaly_check": ["check_recent_anomalies", "review_alerts"],
            "resource_usage": ["get_resource_metrics", "check_thresholds"],
        }
        return action_map.get(intent, [])

    def analyze_query(self, query: str) -> Dict[str, Any]:
    """Analyze query to determine intent and required context."""
        query_lower = query.lower()

        intent = self._determine_intent(query_lower)

        analysis = {
            "intent": intent,
            "required_context": self._get_required_context(intent),
            "priority": self._determine_priority(query_lower),
            "suggested_actions": self._get_suggested_actions(intent),
        }

        return analysis


class ConversationManager:
    """Enhanced conversation management for Phase 5."""
    def __init__(self, max_history: int = 50):
    """Initialize conversation manager."""
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.context_manager = AdvancedContextManager(
    self.query_processor = IntelligentQueryProcessor(
    def add_exchange()
        self, user_query: str, ai_response: str, context: Dict[str, Any] = None
    ):
    """Add a conversation exchange to history."""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "ai_response": ai_response,
            "context": context or {},
            "query_analysis": self.query_processor.analyze_query(user_query),
        }

        self.conversation_history.append(exchange)

    def get_conversation_summary(self) -> str:
    """Get a summary of the conversation history."""
        if not self.conversation_history:
            return "No conversation history available."

        recent_exchanges = list(self.conversation_history)[-5:]  # Last 5 exchanges

        summary_parts = []
        for exchange in recent_exchanges:
            query = ()
                exchange["user_query"][:50] + "..."
                if len(exchange["user_query"]) > 50
                else exchange["user_query"]
            ):
            summary_parts.append(f"Q: {query}")

        return "\n".join(summary_parts)

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
    """Get relevant context for a specific query."""
        analysis = self.query_processor.analyze_query(query)
        system_context = self.context_manager.get_system_context()

        # Filter context based on query intent
        relevant_context = {
        for context_key in analysis["required_context"]:
            if context_key in system_context:
                relevant_context[context_key] = system_context[context_key]

        return {}
            "query_analysis": analysis,
            "relevant_context": relevant_context,
            "conversation_summary": self.get_conversation_summary(),
            "system_summary": self.context_manager.get_context_summary(),
        }


# Initialize global instances
advanced_context_manager = AdvancedContextManager()
intelligent_query_processor = IntelligentQueryProcessor()
conversation_manager = ConversationManager(
    class SystemContextGatherer:
    """Enhanced system context gatherer for Phase 5."""
    def get_system_health(self) -> Dict[str, Any]:
    """Get comprehensive system health information."""
        return advanced_context_manager.get_system_context()

    def get_system_context(self) -> Dict[str, Any]:
    """Get comprehensive system context."""
        return advanced_context_manager.get_system_context()

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
    """Get intelligent context for a specific query."""
        return conversation_manager.get_context_for_query(query)


class LogRetriever:
    """Enhanced log retriever for Phase 5."""
    def __init__(self, log_dir: str = "logs"):
    """Initialize log retriever."""
        self.log_dir = log_dir

    def create_sample_log(self) -> Dict[str, Any]:
    """Create a sample log entry for testing."""
        return {}
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Sample log entry for testing",
            "source": "chatops",
            "user_id": "test_user",
        }

    def get_recent_logs()
        self, hours: int = 24, level: str = None
    ) -> List[Dict[str, Any]]:
    """Get recent logs with enhanced filtering.""":
        try:
            # For now, return sample logs
            # In production, this would read actual log files
            sample_logs = []
            for i in range(5):
                sample_logs.append()
                    {}
                        "timestamp": (datetime.now() - timedelta(hours=i).isoformat(),
                        "level": "INFO" if i % 2 == 0 else "WARNING",:
                        "message": f"Sample log entry {i + 1}",
                        "source": "chatops",
                        "user_id": "test_user",
                    }
                )

            # Filter by level if specified:
            if level:
                sample_logs = []
                    log for log in sample_logs if log["level"] == level.upper()
                ]
:
            return sample_logs:
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return []


def validate_query_params(hours: int = None, level: str = None) -> Tuple[bool, str]:
    """Validate query parameters with enhanced validation.""":
    if hours is not None:
        if not isinstance(hours, int) or hours < 1 or hours > 168:
            return False, "Hours must be an integer between 1 and 168"

    if level is not None:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            return False, f"Level must be one of: {', '.join(valid_levels)}"

    return True, "


def format_response()
    status: str, data: Any = None, message: str = ", error: str = None
) -> Dict[str, Any]:
    """Format response with enhanced structure for Phase 5."""
    response = {:
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "message": message,
    }

    if data is not None:
        response["data"] = data

    if error is not None:
        response["error"] = error

    return response
