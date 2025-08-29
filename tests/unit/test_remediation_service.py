#!/usr/bin/env python3
"""
Unit tests for RemediationService
Tests business logic layer for remediation action operations
"""

import os

# Import the service we're testing
import sys
from datetime import datetime
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.remediation_service import RemediationService


class TestRemediationService:
    """Test suite for RemediationService business logic."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = RemediationService()

    def test_service_initialization(self):
        """Test that RemediationService initializes correctly."""
        assert self.service is not None
        assert len(self.service.mock_data) == 2  # Default mock data
        assert all(isinstance(action, dict) for action in self.service.mock_data)

    def test_get_remediation_actions_default_pagination(self):
        """Test getting remediation actions with default pagination."""
        actions, pagination = self.service.get_remediation_actions()

        assert isinstance(actions, list)
        assert isinstance(pagination, dict)
        assert len(actions) == 2  # All mock data fits in one page
        assert pagination["page"] == 1
        assert pagination["per_page"] == 20
        assert pagination["total"] == 2
        assert pagination["pages"] == 1

    def test_get_remediation_actions_custom_pagination(self):
        """Test getting remediation actions with custom pagination."""
        actions, pagination = self.service.get_remediation_actions(page=1, per_page=1)

        assert len(actions) == 1  # Only one per page
        assert pagination["page"] == 1
        assert pagination["per_page"] == 1
        assert pagination["total"] == 2
        assert pagination["pages"] == 2

    def test_get_remediation_actions_status_filter(self):
        """Test filtering remediation actions by status."""
        actions, pagination = self.service.get_remediation_actions(status="completed")

        assert len(actions) == 1
        assert all(action["status"] == "completed" for action in actions)

    def test_get_remediation_actions_action_type_filter(self):
        """Test filtering remediation actions by action type."""
        actions, pagination = self.service.get_remediation_actions(
            action_type="scale_up"
        )

        assert len(actions) == 1
        assert all(action["action_type"] == "scale_up" for action in actions)

    def test_get_remediation_actions_priority_filter(self):
        """Test filtering remediation actions by priority."""
        actions, pagination = self.service.get_remediation_actions(priority="high")

        assert len(actions) == 1
        assert all(action["priority"] == "high" for action in actions)

    def test_get_remediation_actions_anomaly_id_filter(self):
        """Test filtering remediation actions by anomaly ID."""
        actions, pagination = self.service.get_remediation_actions(anomaly_id=1)

        assert len(actions) == 1
        assert all(action["anomaly_id"] == 1 for action in actions)

    def test_get_remediation_action_by_id_existing(self):
        """Test getting an existing remediation action by ID."""
        action = self.service.get_remediation_action_by_id(1)

        assert action is not None
        assert action["id"] == 1
        assert "action_type" in action
        assert "action_name" in action

    def test_get_remediation_action_by_id_nonexistent(self):
        """Test getting a non-existent remediation action by ID."""
        action = self.service.get_remediation_action_by_id(999)

        assert action is None

    def test_create_remediation_action_valid_data(self):
        """Test creating a remediation action with valid data."""
        action_data = {
            "anomaly_id": 1,
            "action_type": "scale_up",
            "action_name": "Test Scale Up",
            "description": "Test description",
            "priority": "medium",
        }

        original_count = len(self.service.mock_data)
        new_action = self.service.create_remediation_action(action_data)

        assert new_action is not None
        assert new_action["id"] == original_count + 1
        assert new_action["anomaly_id"] == 1
        assert new_action["action_type"] == "scale_up"
        assert new_action["status"] == "pending"  # Default status
        assert new_action["priority"] == "medium"
        assert len(self.service.mock_data) == original_count + 1
        assert "created_at" in new_action
        assert "updated_at" in new_action

    def test_create_remediation_action_missing_required_field(self):
        """Test creating a remediation action with missing required fields."""
        action_data = {
            "anomaly_id": 1,
            "action_type": "scale_up",
            # Missing action_name and description
        }

        with pytest.raises(ValueError, match="Missing required field: action_name"):
            self.service.create_remediation_action(action_data)

    def test_create_remediation_action_invalid_action_type(self):
        """Test creating a remediation action with invalid action type."""
        action_data = {
            "anomaly_id": 1,
            "action_type": "invalid_type",
            "action_name": "Test Action",
            "description": "Test description",
        }

        with pytest.raises(ValueError, match="Invalid action_type"):
            self.service.create_remediation_action(action_data)

    def test_create_remediation_action_invalid_priority(self):
        """Test creating a remediation action with invalid priority."""
        action_data = {
            "anomaly_id": 1,
            "action_type": "scale_up",
            "action_name": "Test Action",
            "description": "Test description",
            "priority": "invalid_priority",
        }

        with pytest.raises(ValueError, match="Invalid priority"):
            self.service.create_remediation_action(action_data)

    def test_update_remediation_action_existing(self):
        """Test updating an existing remediation action."""
        update_data = {"action_name": "Updated Action Name", "priority": "critical"}

        updated_action = self.service.update_remediation_action(1, update_data)

        assert updated_action is not None
        assert updated_action["id"] == 1
        assert updated_action["action_name"] == "Updated Action Name"
        assert updated_action["priority"] == "critical"
        assert "updated_at" in updated_action

    def test_update_remediation_action_nonexistent(self):
        """Test updating a non-existent remediation action."""
        update_data = {"action_name": "Updated Action Name"}

        updated_action = self.service.update_remediation_action(999, update_data)

        assert updated_action is None

    def test_update_remediation_action_invalid_priority(self):
        """Test updating a remediation action with invalid priority."""
        update_data = {"priority": "invalid_priority"}

        with pytest.raises(ValueError, match="Invalid priority"):
            self.service.update_remediation_action(1, update_data)

    def test_update_remediation_action_invalid_status(self):
        """Test updating a remediation action with invalid status."""
        update_data = {"status": "invalid_status"}

        with pytest.raises(ValueError, match="Invalid status"):
            self.service.update_remediation_action(1, update_data)

    @patch("app.services.remediation_service.random.choice")
    def test_execute_remediation_action_success(self, mock_random):
        """Test executing a remediation action successfully."""
        # Mock random to always return success
        mock_random.return_value = True

        # Set action to pending first
        self.service.update_remediation_action(2, {"status": "pending"})

        executed_action = self.service.execute_remediation_action(2)

        assert executed_action is not None
        assert executed_action["id"] == 2
        assert executed_action["status"] == "completed"
        assert executed_action["execution_result"]["success"] is True
        assert "execution_time" in executed_action["execution_result"]
        assert executed_action["error_message"] is None

    @patch("app.services.remediation_service.random.choice")
    def test_execute_remediation_action_failure(self, mock_random):
        """Test executing a remediation action that fails."""
        # Mock random to always return failure
        mock_random.return_value = False

        # Set action to pending first
        self.service.update_remediation_action(2, {"status": "pending"})

        executed_action = self.service.execute_remediation_action(2)

        assert executed_action is not None
        assert executed_action["id"] == 2
        assert executed_action["status"] == "failed"
        assert executed_action["execution_result"]["success"] is False
        assert executed_action["error_message"] is not None

    def test_execute_remediation_action_invalid_status(self):
        """Test executing a remediation action with invalid status."""
        # Action 1 has status 'completed', cannot be executed
        with pytest.raises(
            ValueError, match="Cannot execute action with status: completed"
        ):
            self.service.execute_remediation_action(1)

    def test_execute_remediation_action_nonexistent(self):
        """Test executing a non-existent remediation action."""
        executed_action = self.service.execute_remediation_action(999)

        assert executed_action is None

    def test_approve_remediation_action_existing(self):
        """Test approving an existing remediation action."""
        # Set action to pending first
        self.service.update_remediation_action(2, {"status": "pending"})

        approved_action = self.service.approve_remediation_action(2)

        assert approved_action is not None
        assert approved_action["id"] == 2
        assert approved_action["status"] == "approved"
        assert "updated_at" in approved_action

    def test_approve_remediation_action_invalid_status(self):
        """Test approving a remediation action with invalid status."""
        # Action 1 has status 'completed', cannot be approved
        with pytest.raises(
            ValueError, match="Cannot approve action with status: completed"
        ):
            self.service.approve_remediation_action(1)

    def test_approve_remediation_action_nonexistent(self):
        """Test approving a non-existent remediation action."""
        approved_action = self.service.approve_remediation_action(999)

        assert approved_action is None

    def test_cancel_remediation_action_existing(self):
        """Test cancelling an existing remediation action."""
        # Set action to pending first
        self.service.update_remediation_action(2, {"status": "pending"})

        cancelled_action = self.service.cancel_remediation_action(2)

        assert cancelled_action is not None
        assert cancelled_action["id"] == 2
        assert cancelled_action["status"] == "cancelled"
        assert "updated_at" in cancelled_action

    def test_cancel_remediation_action_invalid_status(self):
        """Test cancelling a remediation action with invalid status."""
        # Action 1 has status 'completed', cannot be cancelled
        with pytest.raises(
            ValueError, match="Cannot cancel action with status: completed"
        ):
            self.service.cancel_remediation_action(1)

    def test_cancel_remediation_action_nonexistent(self):
        """Test cancelling a non-existent remediation action."""
        cancelled_action = self.service.cancel_remediation_action(999)

        assert cancelled_action is None

    def test_get_remediation_statistics(self):
        """Test getting remediation action statistics."""
        stats = self.service.get_remediation_statistics()

        assert isinstance(stats, dict)
        assert "total_actions" in stats
        assert "success_rate" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert "by_priority" in stats

        assert stats["total_actions"] == 2
        assert isinstance(stats["success_rate"], (int, float))
        assert isinstance(stats["by_status"], dict)
        assert isinstance(stats["by_type"], dict)
        assert isinstance(stats["by_priority"], dict)


@pytest.mark.unit
class TestRemediationServiceEdgeCases:
    """Test edge cases and error conditions for RemediationService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = RemediationService()

    def test_pagination_edge_cases(self):
        """Test pagination edge cases."""
        # Test page beyond available data
        actions, pagination = self.service.get_remediation_actions(page=10, per_page=20)
        assert len(actions) == 0
        assert pagination["page"] == 10
        assert pagination["total"] == 2

    def test_filter_no_matches(self):
        """Test filtering that returns no matches."""
        actions, pagination = self.service.get_remediation_actions(status="nonexistent")
        assert len(actions) == 0
        assert pagination["total"] == 0

    def test_multiple_filters_combined(self):
        """Test multiple filters applied together."""
        actions, pagination = self.service.get_remediation_actions(
            status="pending", action_type="restart_service", priority="medium"
        )

        # Should match action with id=2
        assert len(actions) == 1
        assert actions[0]["id"] == 2

    def test_create_remediation_action_default_values(self):
        """Test creating a remediation action with default values."""
        action_data = {
            "anomaly_id": 1,
            "action_type": "scale_up",
            "action_name": "Test Action",
            "description": "Test description",
            # No priority specified, should default to "medium"
        }

        new_action = self.service.create_remediation_action(action_data)

        assert new_action["priority"] == "medium"  # Default value
        assert new_action["status"] == "pending"  # Default value
        assert new_action["parameters"] == {}  # Default value

    def test_update_remediation_action_no_changes(self):
        """Test updating a remediation action with no actual changes."""
        original_action = self.service.get_remediation_action_by_id(1)
        updated_action = self.service.update_remediation_action(1, {})

        assert updated_action is not None
        assert updated_action["action_name"] == original_action["action_name"]
        # updated_at should still be updated
        assert "updated_at" in updated_action

    def test_success_rate_calculation_edge_cases(self):
        """Test success rate calculation with edge cases."""
        # Clear data and add specific test data
        self.service.mock_data = []

        # Test with no executed actions
        stats = self.service.get_remediation_statistics()
        assert stats["success_rate"] == 0

        # Add only pending actions
        self.service.mock_data = [
            {"status": "pending", "action_type": "test", "priority": "low"}
        ]
        stats = self.service.get_remediation_statistics()
        assert stats["success_rate"] == 0

    def test_execute_action_from_approved_status(self):
        """Test executing an action from approved status."""
        # Set action to approved first
        self.service.update_remediation_action(2, {"status": "approved"})

        with patch("app.services.remediation_service.random.choice", return_value=True):
            executed_action = self.service.execute_remediation_action(2)
            assert executed_action["status"] == "completed"
