#!/usr/bin/env python3
"""
Autonomous Operations Engine - Minimal Working Version
Intelligent automation for anomaly remediation
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

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
                    "min_confidence": 0.9,
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
                    "min_confidence": 0.8,
                    "max_system_load": 85,
                },
                automation_level=AutomationLevel.SEMI_AUTO,
                priority=2,
            ),
            # Medium severity - adaptive automation
            PolicyRule(
                rule_id="medium_adaptive",
                name="Medium Severity Adaptive Automation",
                conditions={"severity": ["medium"], "min_confidence": 0.6},
                automation_level=AutomationLevel.ADAPTIVE,
                priority=3,
            ),
            # Low severity - manual intervention
            PolicyRule(
                rule_id="low_manual",
                name="Low Severity Manual Intervention",
                conditions={"severity": ["low"]},
                automation_level=AutomationLevel.MANUAL,
                priority=4,
            ),
            # Business hours policy
            PolicyRule(
                rule_id="business_hours",
                name="Business Hours Automation",
                conditions={
                    "time_window": {"start": 9, "end": 17},
                    "severity": ["high", "critical"],
                },
                automation_level=AutomationLevel.FULL_AUTO,
                priority=2,
            ),
        ]

        return policies

    def add_policy(self, policy: PolicyRule):
        """Add a new automation policy."""
        self.system_policies.append(policy)
        logger.info(f"Added automation policy: {policy.name}")

    def remove_policy(self, rule_id: str):
        """Remove an automation policy."""
        self.system_policies = [p for p in self.system_policies if p.rule_id != rule_id]
        logger.info(f"Removed automation policy: {rule_id}")

    def evaluate_automation_level(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Tuple[AutomationLevel, PolicyRule]:
        """Evaluate automation level based on policies."""
        applicable_policies = []

        # Find all applicable policies
        for policy in self.system_policies:
            if policy.enabled and policy.evaluate(anomaly_info, system_state):
                applicable_policies.append(policy)

        if not applicable_policies:
            # Default to manual intervention
            default_policy = PolicyRule(
                rule_id="default_manual",
                name="Default Manual Intervention",
                conditions={},
                automation_level=AutomationLevel.MANUAL,
                priority=10,
            )
            return AutomationLevel.MANUAL, default_policy

        # Sort by priority (lower number = higher priority)
        applicable_policies.sort(key=lambda p: p.priority)
        selected_policy = applicable_policies[0]

        logger.info(
            f"Selected automation policy: {selected_policy.name} "
            f"(level: {selected_policy.automation_level.value})"
        )

        return selected_policy.automation_level, selected_policy

    async def process_anomaly(self, anomaly_id: int) -> Dict[str, Any]:
        """Process anomaly with autonomous operations."""
        try:
            # Mock anomaly data for demonstration
            anomaly_info = {
                "id": anomaly_id,
                "severity": "high",
                "description": f"Anomaly {anomaly_id}",
                "confidence": 0.85,
                "source": "ml_model",
                "metrics": {"cpu_usage": 85, "memory_usage": 78},
            }

            # Get current system state
            system_state = await self._get_system_state()

            # Evaluate automation level
            automation_level, policy = self.evaluate_automation_level(
                anomaly_info, system_state
            )

            # Mock recommendations
            recommendations = [
                {
                    "action_type": "scale_up",
                    "confidence": 0.9,
                    "description": "Scale up resources to handle load",
                }
            ]

            # Execute based on automation level
            if automation_level == AutomationLevel.MANUAL:
                result = await self._handle_manual_intervention(
                    anomaly_info, recommendations
                )
            elif automation_level == AutomationLevel.SEMI_AUTO:
                result = await self._handle_semi_automation(
                    anomaly_info, recommendations, policy
                )
            elif automation_level == AutomationLevel.FULL_AUTO:
                result = await self._handle_full_automation(
                    anomaly_info, recommendations
                )
            elif automation_level == AutomationLevel.ADAPTIVE:
                result = await self._handle_adaptive_automation(
                    anomaly_info, recommendations, system_state
                )
            else:
                result = {"error": "Unknown automation level"}

            # Update statistics
            self._update_automation_stats(result)

            return result

        except Exception as e:
            logger.error(f"Error processing anomaly {anomaly_id}: {e}")
            return {"error": str(e)}

    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state."""
        # Mock implementation - in real system, would fetch from monitoring
        return {
            "cpu_usage": 75.0,
            "memory_usage": 68.0,
            "disk_usage": 45.0,
            "error_rate": 2.1,
            "response_time": 150.0,
            "active_connections": 342,
            "timestamp": datetime.now().isoformat(),
        }

    async def _handle_manual_intervention(
        self, anomaly: Dict[str, Any], recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle manual intervention."""
        self.automation_stats["manual_interventions"] += 1

        return {
            "automation_level": "manual",
            "action": "manual_intervention_required",
            "recommendations": recommendations,
            "message": "Manual intervention required. Recommendations provided.",
            "next_steps": [
                "Review anomaly details",
                "Evaluate recommendations",
                "Execute manual remediation if needed",
            ],
        }

    async def _handle_semi_automation(
        self,
        anomaly: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        policy: PolicyRule,
    ) -> Dict[str, Any]:
        """Handle semi-automation with human oversight."""
        if not recommendations:
            return await self._handle_manual_intervention(anomaly, recommendations)

        # Select best recommendation
        best_recommendation = max(recommendations, key=lambda r: r.get("confidence", 0))

        # In real implementation, would create pending remediation for approval
        return {
            "automation_level": "semi_auto",
            "action": "pending_approval",
            "recommendation": best_recommendation,
            "policy": policy.name,
            "message": "Semi-automated remediation prepared. Awaiting approval.",
            "approval_required": True,
        }

    async def _handle_full_automation(
        self, anomaly: Dict[str, Any], recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle full automation."""
        if not recommendations:
            return {"error": "No recommendations available for full automation"}

        # Select best recommendation
        best_recommendation = max(recommendations, key=lambda r: r.get("confidence", 0))

        # Mock execution - in real system would execute actual remediation
        success = best_recommendation.get("confidence", 0) > 0.8

        return {
            "automation_level": "full_auto",
            "action": "remediation_executed",
            "recommendation": best_recommendation,
            "success": success,
            "message": (
                "Fully automated remediation executed successfully."
                if success
                else "Automated remediation failed."
            ),
        }

    async def _handle_adaptive_automation(
        self,
        anomaly: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        system_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle adaptive automation based on confidence and system state."""
        if not recommendations:
            return await self._handle_manual_intervention(anomaly, recommendations)

        best_recommendation = recommendations[0]
        confidence = best_recommendation.get("confidence", 0)

        # Adaptive logic based on confidence and system state
        if confidence > 0.8 and system_state.get("cpu_usage", 0) < 80:
            # High confidence, low system load - full automation
            return await self._handle_full_automation(anomaly, recommendations)
        elif confidence > 0.6:
            # Medium confidence - semi-automation
            return await self._handle_semi_automation(anomaly, recommendations, None)
        else:
            # Low confidence - manual intervention
            return await self._handle_manual_intervention(anomaly, recommendations)

    def _update_automation_stats(self, result: Dict[str, Any]):
        """Update automation statistics."""
        self.automation_stats["total_automations"] += 1
        self.automation_stats["last_automation"] = datetime.now().isoformat()

        if result.get("success", False):
            self.automation_stats["successful_automations"] += 1
        elif "error" in result:
            self.automation_stats["failed_automations"] += 1

    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics."""
        stats = self.automation_stats.copy()

        # Calculate success rate
        total = stats["total_automations"]
        if total > 0:
            stats["success_rate"] = stats["successful_automations"] / total
            stats["failure_rate"] = stats["failed_automations"] / total
        else:
            stats["success_rate"] = 0.0
            stats["failure_rate"] = 0.0

        return stats

    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all automation policies."""
        return [
            {
                "rule_id": policy.rule_id,
                "name": policy.name,
                "conditions": policy.conditions,
                "automation_level": policy.automation_level.value,
                "priority": policy.priority,
                "enabled": policy.enabled,
                "created_at": policy.created_at.isoformat(),
            }
            for policy in self.system_policies
        ]


class PolicyManager:
    """Manages automation policies."""

    def __init__(self, ops_engine: AutonomousOperationsEngine):
        self.ops_engine = ops_engine

    def create_policy(
        self,
        name: str,
        conditions: Dict[str, Any],
        automation_level: str,
        priority: int = 5,
    ) -> str:
        """Create a new automation policy."""
        rule_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        automation_level_enum = AutomationLevel(automation_level)

        policy = PolicyRule(
            rule_id=rule_id,
            name=name,
            conditions=conditions,
            automation_level=automation_level_enum,
            priority=priority,
        )

        self.ops_engine.add_policy(policy)
        return rule_id

    def update_policy(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing policy."""
        for policy in self.ops_engine.system_policies:
            if policy.rule_id == rule_id:
                if "name" in updates:
                    policy.name = updates["name"]
                if "conditions" in updates:
                    policy.conditions = updates["conditions"]
                if "automation_level" in updates:
                    policy.automation_level = AutomationLevel(
                        updates["automation_level"]
                    )
                if "priority" in updates:
                    policy.priority = updates["priority"]
                if "enabled" in updates:
                    policy.enabled = updates["enabled"]

                logger.info(f"Updated policy {rule_id}")
                return True

        return False

    def delete_policy(self, rule_id: str) -> bool:
        """Delete a policy."""
        self.ops_engine.remove_policy(rule_id)
        return True
