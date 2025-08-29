#!/usr/bin/env python3
"""
Remediation Service - Business Logic Layer
Handles all remediation action-related business operations
"""

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple


class RemediationService:
    """Service class for remediation action-related business logic."""

    def __init__(self):
        """Initialize the remediation service."""
        self.mock_data = [
            {
                "id": 1,
                "anomaly_id": 1,
                "action_type": "scale_up",
                "action_name": "Scale Up Resources",
                "description": "Increase instance count to handle high CPU usage",
                "status": "completed",
                "priority": "high",
                "parameters": {"instance_count": 3, "instance_type": "t3.medium"},
                "execution_result": {"success": True, "execution_time": 45.2},
                "error_message": None,
                "created_at": "2024-01-15T10:35:00Z",
                "updated_at": "2024-01-15T10:36:30Z",
            },
            {
                "id": 2,
                "anomaly_id": 2,
                "action_type": "restart_service",
                "action_name": "Restart Application Service",
                "description": "Restart the application service to free memory",
                "status": "pending",
                "priority": "medium",
                "parameters": {"service_name": "app-service", "graceful": True},
                "execution_result": None,
                "error_message": None,
                "created_at": "2024-01-15T09:50:00Z",
                "updated_at": "2024-01-15T09:50:00Z",
            },
        ]

    def get_remediation_actions(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        action_type: Optional[str] = None,
        priority: Optional[str] = None,
        anomaly_id: Optional[int] = None,
    ) -> Tuple[List[Dict], Dict]:
        """
        Get remediation actions with pagination and filtering.

        Returns:
            Tuple of (actions_list, pagination_info)
        """
        # Apply filters
        filtered_actions = self.mock_data.copy()

        if status:
            filtered_actions = [r for r in filtered_actions if r["status"] == status]
        if action_type:
            filtered_actions = [
                r for r in filtered_actions if r["action_type"] == action_type
            ]
        if priority:
            filtered_actions = [
                r for r in filtered_actions if r["priority"] == priority
            ]
        if anomaly_id:
            filtered_actions = [
                r for r in filtered_actions if r["anomaly_id"] == anomaly_id
            ]

        # Calculate pagination
        total = len(filtered_actions)
        start = (page - 1) * per_page
        end = start + per_page
        actions_page = filtered_actions[start:end]

        pagination_info = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }

        return actions_page, pagination_info

    def get_remediation_action_by_id(self, action_id: int) -> Optional[Dict]:
        """Get a specific remediation action by ID."""
        return next((r for r in self.mock_data if r["id"] == action_id), None)

    def create_remediation_action(self, action_data: Dict) -> Dict:
        """
        Create a new remediation action.

        Args:
            action_data: Dictionary containing remediation action information

        Returns:
            Created remediation action dictionary

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["action_type", "action_name", "description"]
        for field in required_fields:
            if field not in action_data or not action_data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")

        # Validate action type
        valid_action_types = [
            "scale_up",
            "scale_down",
            "restart_service",
            "cleanup_logs",
            "update_config",
            "rollback",
        ]
        if action_data["action_type"] not in valid_action_types:
            raise ValueError(
                f"Invalid action type. Must be one of: {', '.join(valid_action_types)}"
            )

        # Validate priority
        valid_priorities = ["low", "medium", "high", "critical"]
        priority = action_data.get("priority", "medium")
        if priority not in valid_priorities:
            raise ValueError(
                f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
            )

        # Create new remediation action
        new_action = {
            "id": len(self.mock_data) + 1,
            "anomaly_id": action_data.get("anomaly_id"),
            "action_type": action_data["action_type"],
            "action_name": action_data["action_name"],
            "description": action_data["description"],
            "status": action_data.get("status", "pending"),
            "priority": priority,
            "parameters": action_data.get("parameters", {}),
            "execution_result": None,
            "error_message": None,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
        }

        self.mock_data.append(new_action)
        return new_action

    def update_remediation_action(
        self, action_id: int, update_data: Dict
    ) -> Optional[Dict]:
        """
        Update an existing remediation action.

        Args:
            action_id: ID of the remediation action to update
            update_data: Dictionary containing fields to update

        Returns:
            Updated remediation action dictionary or None if not found

        Raises:
            ValueError: If invalid data is provided
        """
        action = self.get_remediation_action_by_id(action_id)
        if not action:
            return None

        # Validate updateable fields
        updateable_fields = [
            "action_name",
            "description",
            "status",
            "priority",
            "parameters",
            "execution_result",
            "error_message",
        ]

        for field, value in update_data.items():
            if field not in updateable_fields:
                continue

            # Validate specific fields
            if field == "status":
                valid_statuses = [
                    "pending",
                    "in_progress",
                    "completed",
                    "failed",
                    "cancelled",
                ]
                if value not in valid_statuses:
                    raise ValueError(
                        f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                    )
            elif field == "priority":
                valid_priorities = ["low", "medium", "high", "critical"]
                if value not in valid_priorities:
                    raise ValueError(
                        f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
                    )

            action[field] = value

        action["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return action

    def execute_remediation_action(self, action_id: int) -> Optional[Dict]:
        """
        Execute a remediation action.

        Args:
            action_id: ID of the remediation action to execute

        Returns:
            Execution result dictionary or None if action not found
        """
        action = self.get_remediation_action_by_id(action_id)
        if not action:
            return None

        if action["status"] != "pending":
            raise ValueError("Action can only be executed if status is 'pending'")

        # Update status to in_progress
        action["status"] = "in_progress"
        action["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        # Simulate execution
        execution_time = random.uniform(10, 60)
        success = random.choice([True, True, True, False])  # 75% success rate

        execution_result = {
            "success": success,
            "execution_time": round(execution_time, 2),
            "started_at": datetime.now(timezone.utc).isoformat() + "Z",
            "completed_at": (
                datetime.now(timezone.utc) + timedelta(seconds=execution_time)
            ).isoformat()
            + "Z",
        }

        if success:
            action["status"] = "completed"
            action["execution_result"] = execution_result
        else:
            action["status"] = "failed"
            action["error_message"] = "Simulated execution failure"
            action["execution_result"] = execution_result

        action["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return execution_result

    def approve_remediation_action(self, action_id: int) -> Optional[Dict]:
        """
        Approve a remediation action for execution.

        Args:
            action_id: ID of the remediation action to approve

        Returns:
            Updated action dictionary or None if not found
        """
        action = self.get_remediation_action_by_id(action_id)
        if not action:
            return None

        if action["status"] != "pending":
            raise ValueError("Action can only be approved if status is 'pending'")

        action["status"] = "approved"
        action["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return action

    def cancel_remediation_action(self, action_id: int) -> Optional[Dict]:
        """
        Cancel a remediation action.

        Args:
            action_id: ID of the remediation action to cancel

        Returns:
            Updated action dictionary or None if not found
        """
        action = self.get_remediation_action_by_id(action_id)
        if not action:
            return None

        if action["status"] not in ["pending", "approved"]:
            raise ValueError(
                "Action can only be cancelled if status is 'pending' or 'approved'"
            )

        action["status"] = "cancelled"
        action["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        return action

    def get_remediation_statistics(self) -> Dict:
        """
        Get remediation action statistics.

        Returns:
            Dictionary containing various remediation statistics
        """
        total_actions = len(self.mock_data)

        stats_by_status = {}
        stats_by_type = {}
        stats_by_priority = {}
        success_rate = 0

        completed_actions = 0
        successful_actions = 0

        for action in self.mock_data:
            # Count by status
            status = action["status"]
            stats_by_status[status] = stats_by_status.get(status, 0) + 1

            # Count by type
            action_type = action["action_type"]
            stats_by_type[action_type] = stats_by_type.get(action_type, 0) + 1

            # Count by priority
            priority = action["priority"]
            stats_by_priority[priority] = stats_by_priority.get(priority, 0) + 1

            # Calculate success rate
            if status == "completed":
                completed_actions += 1
                if action.get("execution_result", {}).get("success", False):
                    successful_actions += 1

        if completed_actions > 0:
            success_rate = round((successful_actions / completed_actions) * 100, 2)

        return {
            "total_actions": total_actions,
            "by_status": stats_by_status,
            "by_type": stats_by_type,
            "by_priority": stats_by_priority,
            "success_rate": success_rate,
            "completed_actions": completed_actions,
            "successful_actions": successful_actions,
        }
