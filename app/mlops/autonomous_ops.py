#!/usr/bin/env python3
"""
Autonomous Operations for SmartCloudOps AI
Closed-loop automation with policy-based control
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np

from app.database import get_db_session
from app.models import Anomaly, RemediationAction, SystemMetrics, AuditLog
from app.mlops.knowledge_base import knowledge_base_manager
from app.mlops.reinforcement_learning import continuous_learning
from app.mlops.model_registry import model_registry, drift_detector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomationLevel(Enum):
    """Automation levels for remediation"""

    MANUAL = "manual"  # Always require human approval
    SEMI_AUTO = "semi_auto"  # Auto-remediate with human oversight
    FULL_AUTO = "full_auto"  # Fully autonomous remediation
    ADAPTIVE = "adaptive"  # Adaptive based on confidence and impact


class PolicyRule:
    """Policy rule for autonomous operations"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        conditions: Dict[str, Any],
        automation_level: AutomationLevel,
        priority: int = 1,
    ):
        self.rule_id = rule_id
        self.name = name
        self.conditions = conditions
        self.automation_level = automation_level
        self.priority = priority
        self.enabled = True
        self.created_at = datetime.now()

    def evaluate(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> bool:
        """Evaluate if policy rule applies to current situation"""
        if not self.enabled:
            return False

        # Check severity condition
        if "severity" in self.conditions:
            required_severity = self.conditions["severity"]
            if anomaly_info.get("severity") not in required_severity:
                return False

        # Check time condition
        if "time_window" in self.conditions:
            current_hour = datetime.now().hour
            time_window = self.conditions["time_window"]
            if not (time_window["start"] <= current_hour <= time_window["end"]):
                return False

        # Check system load condition
        if "max_system_load" in self.conditions:
            current_load = system_state.get("cpu_usage", 0)
            if current_load > self.conditions["max_system_load"]:
                return False

        # Check confidence threshold
        if "min_confidence" in self.conditions:
            confidence = anomaly_info.get("confidence", 0)
            if confidence < self.conditions["min_confidence"]:
                return False

        return True


class AutonomousOperationsEngine:
    """Autonomous operations engine with closed-loop automation"""

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
        """Load default automation policies"""
        policies = [
            # Critical anomalies - full automation
            PolicyRule(
                rule_id="critical_auto",
                name="Critical Anomaly Auto-Remediation",
                conditions={
                    "severity": ["critical"],
                    "min_confidence": 0.8,
                    "max_system_load": 95,
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
                    "max_system_load": 90,
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
                    "min_confidence": 0.75,
                },
                automation_level=AutomationLevel.SEMI_AUTO,
                priority=2,
            ),
        ]

        return policies

    def add_policy(self, policy: PolicyRule):
        """Add a new automation policy"""
        self.system_policies.append(policy)
        logger.info(f"Added automation policy: {policy.name}")

    def remove_policy(self, rule_id: str):
        """Remove an automation policy"""
        self.system_policies = [p for p in self.system_policies if p.rule_id != rule_id]
        logger.info(f"Removed automation policy: {rule_id}")

    def evaluate_automation_level(
        self, anomaly_info: Dict[str, Any], system_state: Dict[str, Any]
    ) -> Tuple[AutomationLevel, PolicyRule]:
        """Evaluate automation level based on policies"""
        applicable_policies = []

        for policy in self.system_policies:
            if policy.evaluate(anomaly_info, system_state):
                applicable_policies.append(policy)

        if not applicable_policies:
            return AutomationLevel.MANUAL, None

        # Sort by priority (lower number = higher priority)
        applicable_policies.sort(key=lambda p: p.priority)
        selected_policy = applicable_policies[0]

        return selected_policy.automation_level, selected_policy

    async def process_anomaly(self, anomaly_id: int) -> Dict[str, Any]:
        """Process anomaly with autonomous operations"""
        session = get_db_session()
        try:
            # Get anomaly details
            anomaly = session.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
            if not anomaly:
                return {"error": "Anomaly not found"}

            # Get current system state
            system_state = await self._get_system_state()

            # Prepare anomaly info
            anomaly_info = {
                "severity": anomaly.severity,
                "source": anomaly.source,
                "description": anomaly.description,
                "confidence": (
                    anomaly.metrics_data.get("confidence", 0.5)
                    if anomaly.metrics_data
                    else 0.5
                ),
                "metrics": anomaly.metrics_data or {},
            }

            # Evaluate automation level
            automation_level, policy = self.evaluate_automation_level(
                anomaly_info, system_state
            )

            # Get recommendations
            recommendations = knowledge_base_manager.get_recommendations(
                anomaly_info, limit=3
            )

            # Process based on automation level
            if automation_level == AutomationLevel.MANUAL:
                result = await self._handle_manual_intervention(
                    anomaly, recommendations
                )
            elif automation_level == AutomationLevel.SEMI_AUTO:
                result = await self._handle_semi_automation(
                    anomaly, recommendations, policy
                )
            elif automation_level == AutomationLevel.FULL_AUTO:
                result = await self._handle_full_automation(anomaly, recommendations)
            elif automation_level == AutomationLevel.ADAPTIVE:
                result = await self._handle_adaptive_automation(
                    anomaly, recommendations, system_state
                )
            else:
                result = {"error": "Unknown automation level"}

            # Update automation statistics
            self._update_automation_stats(result)

            return result

        except Exception as e:
            logger.error(f"Error processing anomaly {anomaly_id}: {e}")
            return {"error": str(e)}

    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        session = get_db_session()
        try:
            # Get latest metrics
            latest_metrics = (
                session.query(SystemMetrics)
                .order_by(SystemMetrics.timestamp.desc())
                .first()
            )

            if latest_metrics:
                return {
                    "cpu_usage": latest_metrics.cpu_usage,
                    "memory_usage": latest_metrics.memory_usage,
                    "disk_usage": latest_metrics.disk_usage,
                    "error_rate": latest_metrics.error_rate,
                    "response_time": latest_metrics.response_time,
                    "active_connections": latest_metrics.active_connections,
                }

            return {}

        except Exception as e:
            logger.error(f"Error getting system state: {e}")
            return {}

    async def _handle_manual_intervention(
        self, anomaly: Anomaly, recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle manual intervention"""
        self.automation_stats["manual_interventions"] += 1

        return {
            "automation_level": "manual",
            "action": "manual_intervention_required",
            "recommendations": recommendations,
            "message": "Manual intervention required. Please review recommendations and take action.",
            "anomaly_id": anomaly.id,
            "timestamp": datetime.now().isoformat(),
        }

    async def _handle_semi_automation(
        self,
        anomaly: Anomaly,
        recommendations: List[Dict[str, Any]],
        policy: PolicyRule,
    ) -> Dict[str, Any]:
        """Handle semi-automation with human oversight"""
        if not recommendations:
            return await self._handle_manual_intervention(anomaly, recommendations)

        # Select best recommendation
        best_recommendation = recommendations[0]

        # Create remediation action
        remediation = await self._create_remediation_action(
            anomaly, best_recommendation["action_type"], "semi_auto"
        )

        return {
            "automation_level": "semi_auto",
            "action": "remediation_executed",
            "remediation_id": remediation.id,
            "recommendation": best_recommendation,
            "policy": policy.name,
            "message": "Semi-automated remediation executed. Human oversight recommended.",
            "anomaly_id": anomaly.id,
            "timestamp": datetime.now().isoformat(),
        }

    async def _handle_full_automation(
        self, anomaly: Anomaly, recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle full automation"""
        if not recommendations:
            return {"error": "No recommendations available for full automation"}

        # Select best recommendation
        best_recommendation = recommendations[0]

        # Execute remediation
        remediation = await self._create_remediation_action(
            anomaly, best_recommendation["action_type"], "full_auto"
        )

        # Execute the remediation
        success = await self._execute_remediation(remediation)

        # Update remediation status
        await self._update_remediation_status(remediation, success)

        # Learn from experience
        knowledge_base_manager.add_experience(
            {
                "severity": anomaly.severity,
                "source": anomaly.source,
                "description": anomaly.description,
                "metrics": anomaly.metrics_data,
            },
            best_recommendation["action_type"],
            success,
        )

        return {
            "automation_level": "full_auto",
            "action": "remediation_executed",
            "remediation_id": remediation.id,
            "recommendation": best_recommendation,
            "success": success,
            "message": (
                "Fully automated remediation executed successfully."
                if success
                else "Automated remediation failed."
            ),
            "anomaly_id": anomaly.id,
            "timestamp": datetime.now().isoformat(),
        }

    async def _handle_adaptive_automation(
        self,
        anomaly: Anomaly,
        recommendations: List[Dict[str, Any]],
        system_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle adaptive automation based on confidence and system state"""
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

    async def _create_remediation_action(
        self, anomaly: Anomaly, action_type: str, automation_level: str
    ) -> RemediationAction:
        """Create remediation action"""
        session = get_db_session()

        remediation = RemediationAction(
            anomaly_id=anomaly.id,
            action_type=action_type,
            status="pending",
            automation_level=automation_level,
            created_at=datetime.now(),
            created_by="autonomous_system",
        )

        session.add(remediation)
        session.commit()

        return remediation

    async def _execute_remediation(self, remediation: RemediationAction) -> bool:
        """Execute remediation action"""
        try:
            # Simulate remediation execution
            start_time = datetime.now()

            # Simulate execution time
            await asyncio.sleep(2)  # Simulate 2-second execution

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # Simulate success/failure based on action type
            success_rate = {
                "restart_service": 0.9,
                "scale_up": 0.95,
                "scale_down": 0.95,
                "clear_cache": 0.98,
                "restart_database": 0.85,
                "increase_memory": 0.9,
                "decrease_load": 0.8,
            }

            success_probability = success_rate.get(remediation.action_type, 0.7)
            success = np.random.random() < success_probability

            # Update remediation with execution results
            session = get_db_session()
            remediation.execution_time = execution_time
            remediation.success = success
            remediation.status = "completed"
            remediation.completed_at = datetime.now()

            session.commit()

            logger.info(
                f"Executed remediation {remediation.id}: {remediation.action_type} (success: {success})"
            )
            return success

        except Exception as e:
            logger.error(f"Error executing remediation {remediation.id}: {e}")
            return False

    async def _update_remediation_status(
        self, remediation: RemediationAction, success: bool
    ):
        """Update remediation status and related entities"""
        session = get_db_session()
        try:
            # Update anomaly status based on remediation success
            anomaly = (
                session.query(Anomaly)
                .filter(Anomaly.id == remediation.anomaly_id)
                .first()
            )
            if anomaly:
                if success:
                    anomaly.status = "resolved"
                else:
                    anomaly.status = "escalated"

                session.commit()

        except Exception as e:
            logger.error(f"Error updating remediation status: {e}")

    def _update_automation_stats(self, result: Dict[str, Any]):
        """Update automation statistics"""
        self.automation_stats["total_automations"] += 1
        self.automation_stats["last_automation"] = datetime.now().isoformat()

        if result.get("success", False):
            self.automation_stats["successful_automations"] += 1
        elif "error" in result:
            self.automation_stats["failed_automations"] += 1

    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics"""
        stats = self.automation_stats.copy()

        # Calculate success rate
        if stats["total_automations"] > 0:
            stats["success_rate"] = (
                stats["successful_automations"] / stats["total_automations"]
            )
        else:
            stats["success_rate"] = 0.0

        return stats

    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all automation policies"""
        return [
            {
                "rule_id": policy.rule_id,
                "name": policy.name,
                "conditions": policy.conditions,
                "automation_level": policy.automation_level.value,
                "priority": policy.priority,
                "enabled": policy.enabled,
            }
            for policy in self.system_policies
        ]


class PolicyManager:
    """Manages automation policies"""

    def __init__(self, ops_engine: AutonomousOperationsEngine):
        self.ops_engine = ops_engine

    def create_policy(
        self,
        name: str,
        conditions: Dict[str, Any],
        automation_level: str,
        priority: int = 5,
    ) -> str:
        """Create a new automation policy"""
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
        """Update an existing policy"""
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
        """Delete a policy"""
        self.ops_engine.remove_policy(rule_id)
        return True


# Global autonomous operations engine
autonomous_ops_engine = AutonomousOperationsEngine()
policy_manager = PolicyManager(autonomous_ops_engine)
