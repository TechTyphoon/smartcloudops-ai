#!/usr/bin/env python3
"""
Smart CloudOps AI - Safety Manager (Phase 4)
Implements safety mechanisms for auto-remediation actions
"""

import logging
import os
import boto3
from typing import List, Dict

logger = logging.getLogger(__name__)


class SafetyManager:
    """
    Manages safety mechanisms for auto-remediation actions.
    Implements cooldowns, rate limits, and approval workflows.
    """

    def __init__(
        self,
        max_actions_per_hour: int = 10,
        cooldown_minutes: int = 5,
        approval_param: str = "/smartcloudops/dev/approvals/auto",
    ):
        """Initialize the safety manager."""
        self.max_actions_per_hour = max_actions_per_hour
        self.cooldown_minutes = cooldown_minutes
        self.approval_param = approval_param

        # Track recent actions for rate limiting
        self.recent_actions: List[Dict] = []
        self.last_action_time: Optional[datetime] = None

        # Initialize AWS SSM client
        try:
            self.ssm = boto3.client(
                "ssm", region_name=os.getenv("AWS_REGION", "ap-south-1")
            )
        except Exception as e:
            logger.warning("Could not initialize SSM client: {e}")
            self.ssm = None

        logger.info(
            "Safety manager initialized: max_actions_per_hour="
            "{max_actions_per_hour}, cooldown_minutes={cooldown_minutes}"
        )

    def check_safety_conditions(
        self, severity: str, actions: List[Dict]
    ) -> Dict[str, any]:
        """
        Check if itf's safe to proceed with remediation actions.

        Args:
            severity: Anomaly severity level
            actions: List of proposed actions

        Returns:
            Dict with safety check results
        """
        try:
            safety_checks = {
                "cooldown_check": self._check_cooldown(),
                "rate_limit_check": self._check_rate_limit(),
                "approval_check": self._check_approval_required(severity, actions),
                "action_safety_check": self._check_action_safety(actions),
            }

            # Determine overall safety
            safe_to_proceed = all(check["safe"] for check in safety_checks.values())

            # Get primary reason if not safe
            reason = None
            if not safe_to_proceed:
                for check_name, check_result in safety_checks.items():
                    if not check_result["safe"]:
                        reason = check_result["reason"]
                        break

            result = {
                "safe_to_proceed": safe_to_proceed,
                "reason": reason,
                "checks": safety_checks,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("Safety check result: safe={safe_to_proceed}, reason={reason}")
            return result

        except Exception as e:
            logger.error("Error in safety check: {e}")
            return {
                "safe_to_proceed": False,
                "reason": "Safety check error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _check_cooldown(self) -> Dict[str, any]:
        """Check if enough time has passed since the last action."""
        try:
            if self.last_action_time is None:
                return {"safe": True, "reason": "No previous actions"}

            time_since_last = datetime.now() - self.last_action_time
            cooldown_duration = timedelta(minutes=self.cooldown_minutes)

            if time_since_last < cooldown_duration:
                remaining_time = cooldown_duration - time_since_last
                return {
                    "safe": False,
                    "reason": "Cooldown period active. Wait "
                    "{remaining_time.seconds // 60} more minutes",
                }

            return {"safe": True, "reason": "Cooldown period passed"}

        except Exception as e:
            logger.error("Error checking cooldown: {e}")
            return {"safe": False, "reason": "Cooldown check error: {str(e)}"}

    def _check_rate_limit(self) -> Dict[str, any]:
        """Check if we're within the hourly action limit."""
        try:
            # Clean up old actions (older than 1 hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.recent_actions = [
                action
                for action in self.recent_actions
                if action["timestamp"] > cutoff_time
            ]

            current_count = len(self.recent_actions)

            if current_count >= self.max_actions_per_hour:
                return {
                    "safe": False,
                    "reason": (
                        "Rate limit exceeded. {current_count}/"
                        "{self.max_actions_per_hour} actions in the last hour"
                    ),
                }

            return {
                "safe": True,
                "reason": (
                    "Rate limit OK. {current_count}/"
                    "{self.max_actions_per_hour} actions in the last hour"
                ),
            }

        except Exception as e:
            logger.error("Error checking rate limit: {e}")
            return {"safe": False, "reason": "Rate limit check error: {str(e)}"}

    def _check_approval_required(
        self, severity: str, actions: List[Dict]
    ) -> Dict[str, any]:
        """Check if approval is required for the proposed actions."""
        try:
            # Critical actions always require approval
            if severity == "critical":
                approval_required = True
            else:
                # Check SSM parameter for approval setting
                approval_required = self._get_approval_setting()

            if approval_required:
                # For now, wef'll auto-approve but log the requirement
                # In a real implementation, this would trigger a manual approval
                # workflow
                logger.warning(
                    "Approval required for {severity} severity actions: "
                    "{[a['action'] for a in actions]}"
                )
                return {
                    "safe": True,  # Auto-approved for demo
                    "reason": (
                        "Auto-approved (would require manual approval in production)"
                    ),
                    "approval_required": True,
                }

            return {
                "safe": True,
                "reason": "No approval required",
                "approval_required": False,
            }

        except Exception as e:
            logger.error("Error checking approval: {e}")
            return {"safe": False, "reason": "Approval check error: {str(e)}"}

    def _get_approval_setting(self) -> bool:
        """Get approval setting from SSM parameter."""
        try:
            if self.ssm is None:
                logger.warning(
                    "SSM client not available, using default approval setting"
                )
                return False

            response = self.ssm.get_parameter(
                Name=self.approval_param, WithDecryption=False
            )

            value = response["Parameter"]["Value"].lower()
            return value == "true"

        except Exception as e:
            logger.warning("Could not get approval setting from SSM: {e}")
            return False  # Default to no approval required

    def _check_action_safety(self, actions: List[Dict]) -> Dict[str, any]:
        """Check if the proposed actions are safe to execute."""
        try:
            dangerous_actions = ["restart_service", "scale_down", "terminate_instance"]

            for action in actions:
                if action.get("action") in dangerous_actions:
                    # Check if this is a critical action that might be dangerous
                    if action.get("priority") == "immediate":
                        return {
                            "safe": False,
                            "reason": "Dangerous action detected: "
                            '{action["action"]} with immediate priorityf',
                        }

            return {"safe": True, "reason": "All actions appear safe"}

        except Exception as e:
            logger.error("Error checking action safety: {e}")
            return {"safe": False, "reason": "Action safety check error: {str(e)}"}

    def record_action(self, action: Dict, severity: str):
        """Record an action for rate limiting and cooldown tracking."""
        try:
            self.recent_actions.append(
                {
                    "action": action.get("action", "unknown"),
                    "severity": severity,
                    "timestamp": datetime.now(),
                }
            )
            self.last_action_time = datetime.now()

            logger.info(
                "Recorded action: {action.get('action')} with severity {severity}"
            )

        except Exception as e:
            logger.error("Error recording action: {e}")

    def get_status(self) -> Dict[str, any]:
        """Get current status of the safety manager."""
        try:
            return {
                "max_actions_per_hour": self.max_actions_per_hour,
                "cooldown_minutes": self.cooldown_minutes,
                "recent_actions_count": len(self.recent_actions),
                "last_action_time": (
                    self.last_action_time.isoformat() if self.last_action_time else None
                ),
                "approval_param": self.approval_param,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error("Error getting safety status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
