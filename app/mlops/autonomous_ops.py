#!/usr/bin/env python3
"""
Autonomous Operations Engine - Minimal Working Version
Intelligent automation for anomaly remediation
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AutomationLevel(Enum):
    """Automation levels for remediation actions."""

    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"
    ADAPTIVE = "adaptive"


@dataclass
class PolicyRule:
    """Policy rule for automation decisions."""

    rule_id: str
    name: str
    conditions: Dict[str, Any]
    automation_level: AutomationLevel
    priority: int = 5
    enabled: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def evaluate(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> bool:
        """Evaluate if this policy rule applies to the given anomaly and system state."""

        # Check severity condition - ensure anomaly severity matches required levels
        if "severity" in self.conditions:
            required_severity = self.conditions["severity"]
            if anomaly_info.get("severity") not in required_severity:
                return False

        # Check time condition - ensure current time falls within allowed window
        if "time_window" in self.conditions:
            current_hour = datetime.now().hour
            time_window = self.conditions["time_window"]
            if not (
                time_window.get("start", 0)
                <= current_hour
                <= time_window.get("end", 23)
            ):
                return False

        # Check system load condition - prevent automation during high load
        if "max_system_load" in self.conditions:
            current_load = system_state.get("cpu_usage", 0)
            if current_load > self.conditions["max_system_load"]:
                return False

        # Check confidence threshold - ensure ML model confidence is sufficient
        if "min_confidence" in self.conditions:
            confidence = anomaly_info.get("confidence", 0)
            if confidence < self.conditions["min_confidence"]:
                return False

        return True


class AutonomousOperationsEngine:
    """Autonomous operations engine with closed-loop automation."""

    def __init__(self):
        self.policies = []
        self.automation_history = []
        self.system_policies = self._load_default_policies()
        self.automation_stats = {
            "total_automations": 0,
            "successful_automations": 0,
            "failed_automations": 0,
            "manual_interventions": 0,
            "last_automation": None,
        }

    def _load_default_policies(self) -> List[PolicyRule]:
        """Load default automation policies."""
        policies = [
            # Critical anomalies - full automation
            PolicyRule(
                rule_id="critical_auto",
                name="Critical Anomaly Auto-Remediation",
                conditions={
                    "severity": ["critical"],
                    "min_confidence": 0.8,
                    "max_system_load": 90,
                },
                automation_level=AutomationLevel.FULL_AUTO,
                priority=1,
            ),
            # High severity - semi-automation
            PolicyRule(
                rule_id="high_semi_auto",
                name="High Severity Semi-Automation",
                conditions={
                    "severity": ["high"],
                    "min_confidence": 0.7,
                    "max_system_load": 85,
                },
                automation_level=AutomationLevel.SEMI_AUTO,
                priority=2,
            ),
            # Medium severity - manual with suggestions
            PolicyRule(
                rule_id="medium_manual",
                name="Medium Severity Manual Review",
                conditions={"severity": ["medium"], "min_confidence": 0.6},
                automation_level=AutomationLevel.MANUAL,
                priority=3,
            ),
        ]
        return policies

    def add_policy(self, policy: PolicyRule) -> bool:
        """Add a new automation policy."""
        try:
            self.policies.append(policy)
            logger.info(f"Added automation policy: {policy.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add policy: {e}")
            return False

    def remove_policy(self, rule_id: str) -> bool:
        """Remove an automation policy."""
        try:
            self.policies = [p for p in self.policies if p.rule_id != rule_id]
            logger.info(f"Removed automation policy: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove policy: {e}")
            return False

    def evaluate_automation_level(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> AutomationLevel:
        """Evaluate the appropriate automation level for an anomaly."""
        try:
            applicable_policies = []

            # Check all policies
            for policy in self.policies + self.system_policies:
                if policy.enabled and policy.evaluate(anomaly_info, system_state):
                    applicable_policies.append(policy)

            if not applicable_policies:
                return AutomationLevel.MANUAL

            # Sort by priority (lower number = higher priority)
            applicable_policies.sort(key=lambda p: p.priority)

            # Return the highest priority policy's automation level
            return applicable_policies[0].automation_level

        except Exception as e:
            logger.error(f"Error evaluating automation level: {e}")
            return AutomationLevel.MANUAL

    def execute_automation(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute automation based on evaluated level."""
        try:
            automation_level = self.evaluate_automation_level(
                anomaly_info, system_state
            )

            automation_result = {
                "automation_level": automation_level.value,
                "anomaly_id": anomaly_info.get("id"),
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "action_taken": None,
                "details": {},
            }

            if automation_level == AutomationLevel.FULL_AUTO:
                result = self._execute_full_automation(anomaly_info, system_state)
                automation_result.update(result)
            elif automation_level == AutomationLevel.SEMI_AUTO:
                result = self._execute_semi_automation(anomaly_info, system_state)
                automation_result.update(result)
            elif automation_level == AutomationLevel.MANUAL:
                result = self._generate_manual_suggestions(anomaly_info, system_state)
                automation_result.update(result)
            else:
                automation_result["details"] = {"message": "No automation action taken"}

            # Update statistics
            self._update_automation_stats(automation_result)

            # Add to history
            self.automation_history.append(automation_result)

            return automation_result

        except Exception as e:
            logger.error(f"Error executing automation: {e}")
            return {
                "automation_level": "manual",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _execute_full_automation(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute full automation for critical anomalies."""
        try:
            anomaly_type = anomaly_info.get("type", "unknown")

            if anomaly_type == "cpu_spike":
                action = self._remediate_cpu_spike(anomaly_info, system_state)
            elif anomaly_type == "memory_leak":
                action = self._remediate_memory_leak(anomaly_info, system_state)
            elif anomaly_type == "disk_full":
                action = self._remediate_disk_full(anomaly_info, system_state)
            else:
                action = {
                    "action": "unknown",
                    "success": False,
                    "message": "Unknown anomaly type",
                }

            return {
                "success": action.get("success", False),
                "action_taken": action.get("action"),
                "details": action,
            }

        except Exception as e:
            logger.error(f"Full automation error: {e}")
            return {
                "success": False,
                "action_taken": "error",
                "details": {"error": str(e)},
            }

    def _execute_semi_automation(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute semi-automation with human approval."""
        try:
            # Generate suggested actions
            suggestions = self._generate_suggestions(anomaly_info, system_state)

            return {
                "success": True,
                "action_taken": "suggestions_generated",
                "details": {
                    "suggestions": suggestions,
                    "requires_approval": True,
                    "message": "Semi-automation: Human approval required",
                },
            }

        except Exception as e:
            logger.error(f"Semi-automation error: {e}")
            return {
                "success": False,
                "action_taken": "error",
                "details": {"error": str(e)},
            }

    def _generate_manual_suggestions(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate manual suggestions for review."""
        try:
            suggestions = self._generate_suggestions(anomaly_info, system_state)

            return {
                "success": True,
                "action_taken": "suggestions_generated",
                "details": {
                    "suggestions": suggestions,
                    "requires_manual_action": True,
                    "message": "Manual review required",
                },
            }

        except Exception as e:
            logger.error(f"Manual suggestions error: {e}")
            return {
                "success": False,
                "action_taken": "error",
                "details": {"error": str(e)},
            }

    def _generate_suggestions(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on anomaly type."""
        anomaly_type = anomaly_info.get("type", "unknown")
        suggestions = []

        if anomaly_type == "cpu_spike":
            suggestions = [
                {"action": "scale_up", "description": "Scale up CPU resources"},
                {
                    "action": "restart_service",
                    "description": "Restart affected service",
                },
                {
                    "action": "check_processes",
                    "description": "Check for runaway processes",
                },
            ]
        elif anomaly_type == "memory_leak":
            suggestions = [
                {
                    "action": "restart_service",
                    "description": "Restart service to free memory",
                },
                {
                    "action": "increase_memory",
                    "description": "Increase memory allocation",
                },
                {
                    "action": "check_memory_usage",
                    "description": "Analyze memory usage patterns",
                },
            ]
        elif anomaly_type == "disk_full":
            suggestions = [
                {"action": "cleanup_logs", "description": "Clean up old log files"},
                {"action": "increase_disk", "description": "Increase disk space"},
                {"action": "archive_data", "description": "Archive old data"},
            ]
        else:
            suggestions = [
                {"action": "investigate", "description": "Investigate the anomaly"},
                {"action": "monitor", "description": "Continue monitoring"},
                {"action": "escalate", "description": "Escalate to senior engineer"},
            ]

        return suggestions

    def _remediate_cpu_spike(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Remediate CPU spike anomaly."""
        try:
            # Simulate CPU spike remediation
            return {
                "action": "scale_up_cpu",
                "success": True,
                "message": "CPU resources scaled up successfully",
                "details": {
                    "previous_cpu": system_state.get("cpu_usage", 0),
                    "action_taken": "increased_cpu_limits",
                },
            }
        except Exception as e:
            return {
                "action": "scale_up_cpu",
                "success": False,
                "message": f"Failed to scale CPU: {e}",
            }

    def _remediate_memory_leak(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Remediate memory leak anomaly."""
        try:
            # Simulate memory leak remediation
            return {
                "action": "restart_service",
                "success": True,
                "message": "Service restarted to free memory",
                "details": {
                    "previous_memory": system_state.get("memory_usage", 0),
                    "action_taken": "service_restart",
                },
            }
        except Exception as e:
            return {
                "action": "restart_service",
                "success": False,
                "message": f"Failed to restart service: {e}",
            }

    def _remediate_disk_full(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Remediate disk full anomaly."""
        try:
            # Simulate disk cleanup
            return {
                "action": "cleanup_logs",
                "success": True,
                "message": "Old log files cleaned up",
                "details": {
                    "previous_disk": system_state.get("disk_usage", 0),
                    "action_taken": "log_cleanup",
                },
            }
        except Exception as e:
            return {
                "action": "cleanup_logs",
                "success": False,
                "message": f"Failed to cleanup logs: {e}",
            }

    def _update_automation_stats(self, result: Dict[str, Any]):
        """Update automation statistics."""
        self.automation_stats["total_automations"] += 1
        self.automation_stats["last_automation"] = datetime.now().isoformat()

        if result.get("success", False):
            self.automation_stats["successful_automations"] += 1
        else:
            self.automation_stats["failed_automations"] += 1

    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics."""
        return self.automation_stats.copy()

    def get_automation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent automation history."""
        return self.automation_history[-limit:] if self.automation_history else []

    def clear_history(self) -> bool:
        """Clear automation history."""
        try:
            self.automation_history.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False


# Global instance
autonomous_engine = AutonomousOperationsEngine()
