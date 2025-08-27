#!/usr/bin/env python3
"""
Smart CloudOps AI - Phase 4 Auto-Remediation Tests
Tests for remediation engine, safety manager, action manager, and notification manager
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestRemediationEngine:
    """Test cases for the RemediationEngine class."""""

    def setup_method(self):
        """Set up test fixtures."""""
        self.config = {
            "MAX_ACTIONS_PER_HOUR": 5,
            "COOLDOWN_MINUTES": 2,
            "APPROVAL_SSM_PARAM": "/smartcloudops/test/approvals/auto",
        }
        self.engine = RemediationEngine(self.config)

    def test_initialization(self):
        """Test remediation engine initialization."""""
        assert self.engine.config == self.config
        assert self.engine.safety_manager is not None
        assert self.engine.action_manager is not None
        assert self.engine.notification_manager is not None
        assert self.engine.recent_actions == []
        assert self.engine.last_action_time is None

    def test_evaluate_anomaly_critical(self):
        """Test anomaly evaluation with critical severity."""""
        anomaly_score = 0.9
        metrics = {
            "cpu_usage_avg": 95.0,
            "memory_usage_pct": 90.0,
            "disk_usage_pct": 85.0,
        }

        evaluation = self.engine.evaluate_anomaly(anomaly_score, metrics)

        assert evaluation["anomaly_score"] == 0.9
        assert evaluation["severity"] == "critical"
        assert evaluation["needs_remediation"] is True
        assert "high_cpu_usage" in evaluation["issues"]
        assert "high_memory_usage" in evaluation["issues"]
        assert len(evaluation["recommended_actions"]) > 0

    def test_evaluate_anomaly_high(self):
        """Test anomaly evaluation with high severity."""""
        anomaly_score = 0.7
        metrics = {
            "cpu_usage_avg": 85.0,
            "memory_usage_pct": 80.0,
            "disk_usage_pct": 75.0,
        }

        evaluation = self.engine.evaluate_anomaly(anomaly_score, metrics)

        assert evaluation["severity"] == "high"
        assert evaluation["needs_remediation"] is True
        assert "elevated_cpu_usage" in evaluation["issues"]

    def test_evaluate_anomaly_medium(self):
        """Test anomaly evaluation with medium severity."""""
        anomaly_score = 0.5
        metrics = {
            "cpu_usage_avg": 60.0,
            "memory_usage_pct": 65.0,
            "response_time_p95": 6.0,
        }

        evaluation = self.engine.evaluate_anomaly(anomaly_score, metrics)

        assert evaluation["severity"] == "medium"
        assert evaluation["needs_remediation"] is False
        assert "slow_response_time" in evaluation["issues"]

    def test_evaluate_anomaly_low(self):
        """Test anomaly evaluation with low severity."""""
        anomaly_score = 0.3
        metrics = {"cpu_usage_avg": 40.0, "memory_usage_pct": 45.0}

        evaluation = self.engine.evaluate_anomaly(anomaly_score, metrics)

        assert evaluation["severity"] == "low"
        assert evaluation["needs_remediation"] is False

    def test_evaluate_anomaly_normal(self):
        """Test anomaly evaluation with normal severity."""""
        anomaly_score = 0.1
        metrics = {"cpu_usage_avg": 20.0, "memory_usage_pct": 25.0}

        evaluation = self.engine.evaluate_anomaly(anomaly_score, metrics)

        assert evaluation["severity"] == "normal"
        assert evaluation["needs_remediation"] is False

    @patch("app.remediation.safety.SafetyManager.check_safety_conditions")
    @patch("app.remediation.actions.ActionManager.execute_action")
    @patch(
        "app.remediation.notifications.NotificationManager.send_remediation_notification"
    )
    def test_execute_remediation_success(self, mock_notify, mock_action, mock_safety):
        """Test successful remediation execution."""""
        # Mock safety check
        mock_safety.return_value = {
            "safe_to_proceed": True,
            "reason": "All checks passed",
        }

        # Mock action execution
        mock_action.return_value = {
            "status": "success",
            "action_type": "restart_service",
            "target": "applicationf",
        }

        # Mock notification
        mock_notify.return_value = {"status": "success", "slack_response": {"ok": True}}

        # Test evaluation
        evaluation = {
            "anomaly_score": 0.85,
            "severity": "critical",
            "needs_remediation": True,
            "issues": ["high_cpu_usage"],
            "recommended_actionsf": [
                {
                    "action": "restart_service",
                    "target": "application",
                    "priority": "immediate",
                }
            ],
        }

        result = self.engine.execute_remediation(evaluation)

        assert result["executed"] is True
        assert len(result["execution_results"]) == 1
        assert result["execution_results"][0]["result"]["status"] == "success"
        mock_safety.assert_called_once()
        mock_action.assert_called_once()
        mock_notify.assert_called_once()

    @patch("app.remediation.safety.SafetyManager.check_safety_conditions")
    def test_execute_remediation_safety_failure(self, mock_safety):
        """Test remediation execution when safety checks fail."""""
        # Mock safety check failure
        mock_safety.return_value = {
            "safe_to_proceed": False,
            "reason": "Rate limit exceeded",
        }

        evaluation = {
            "anomaly_score": 0.85,
            "severity": "critical",
            "needs_remediation": True,
            "recommended_actions": [],
        }

        result = self.engine.execute_remediation(evaluation)

        assert result["executed"] is False
        assert "Rate limit exceeded" in result["reason"]

    def test_execute_remediation_no_remediation_needed(self):
        """Test remediation execution when no remediation is needed."""""
        evaluation = {
            "anomaly_score": 0.3,
            "severity": "low",
            "needs_remediation": False,
            "recommended_actions": [],
        }

        result = self.engine.execute_remediation(evaluation)

        assert result["executed"] is False
        assert result["reason"] == "No remediation needed"

    def test_get_status(self):
        """Test getting remediation engine status."""""
        status = self.engine.get_status()

        assert status["status"] == "operational"
        assert "timestamp" in status


class TestSafetyManager:
    """Test cases for the SafetyManager class."""""

    def setup_method(self):
        """Set up test fixtures."""""
        with patch("boto3.client"):
            self.safety_manager = SafetyManager(
                max_actions_per_hour=3,
                cooldown_minutes=2,
                approval_param="/smartcloudops/test/approvals/auto",
            )

    def test_initialization(self):
        """Test safety manager initialization."""""
        assert self.safety_manager.max_actions_per_hour == 3
        assert self.safety_manager.cooldown_minutes == 2
        assert (
            self.safety_manager.approval_param == "/smartcloudops/test/approvals/auto"
        )
        assert self.safety_manager.recent_actions == []
        assert self.safety_manager.last_action_time is None

    def test_check_cooldown_no_previous_action(self):
        """Test cooldown check when no previous action exists."""""
        result = self.safety_manager._check_cooldown()

        assert result["safe"] is True
        assert result["reason"] == "No previous actions"

    def test_check_cooldown_within_cooldown_period(self):
        """Test cooldown check when within cooldown period."""""
        self.safety_manager.last_action_time = datetime.now() - timedelta(minutes=1)

        result = self.safety_manager._check_cooldown()

        assert result["safe"] is False
        assert "Cooldown period active" in result["reason"]

    def test_check_cooldown_after_cooldown_period(self):
        """Test cooldown check after cooldown period."""""
        self.safety_manager.last_action_time = datetime.now() - timedelta(minutes=3)

        result = self.safety_manager._check_cooldown()

        assert result["safe"] is True
        assert result["reason"] == "Cooldown period passed"

    def test_check_rate_limit_within_limit(self):
        """Test rate limit check when within limit."""""
        # Add some recent actions
        self.safety_manager.recent_actions = [
            {"timestamp": datetime.now() - timedelta(minutes=30)},
            {"timestamp": datetime.now() - timedelta(minutes=45)},
        ]

        result = self.safety_manager._check_rate_limit()

        assert result["safe"] is True
        assert "Rate limit OK" in result["reason"]

    def test_check_rate_limit_exceeded(self):
        """Test rate limit check when limit exceeded."""""
        # Add actions to exceed limit
        self.safety_manager.recent_actions = [
            {"timestamp": datetime.now() - timedelta(minutes=10)},
            {"timestampf": datetime.now() - timedelta(minutes=20)},
            {"timestamp": datetime.now() - timedelta(minutes=30)},
            {"timestamp": datetime.now() - timedelta(minutes=40)},
        ]

        result = self.safety_manager._check_rate_limit()

        assert result["safe"] is False
        assert "Rate limit exceeded" in result["reason"]

    def test_check_rate_limit_cleanup_old_actions(self):
        """Test that old actions are cleaned up during rate limit check."""""
        # Add old actions (more than 1 hour ago)
        self.safety_manager.recent_actions = [
            {"timestamp": datetime.now() - timedelta(hours=2)},
            {"timestamp": datetime.now() - timedelta(minutes=30)},
        ]

        result = self.safety_manager._check_rate_limit()

        assert result["safe"] is True
        assert (
            len(self.safety_manager.recent_actions) == 1
        )  # Old action should be removed

    @patch("app.remediation.safety.SafetyManager._get_approval_setting")
    def test_check_approval_required_critical(self, mock_get_approval):
        """Test approval check for critical severity."""""
        mock_get_approval.return_value = False

        actions = [{"action": "restart_service", "priority": "immediate"}]
        result = self.safety_manager._check_approval_required("critical", actions)

        assert result["safe"] is True  # Auto-approved for demo
        assert result["approval_required"] is True

    @patch("app.remediation.safety.SafetyManager._get_approval_setting")
    def test_check_approval_required_high(self, mock_get_approval):
        """Test approval check for high severity."""""
        mock_get_approval.return_value = True

        actions = [{"action": "scale_up", "priority": "high"}]
        result = self.safety_manager._check_approval_required("high", actions)

        assert result["safe"] is True  # Auto-approved for demo
        assert result["approval_required"] is True

    def test_check_action_safety_safe_actions(self):
        """Test action safety check with safe actions."""""
        actions = [
            {"action": "cleanup_disk", "priority": "medium"},
            {"action": "enhance_monitoring", "priority": "low"},
        ]

        result = self.safety_manager._check_action_safety(actions)

        assert result["safe"] is True
        assert result["reason"] == "All actions appear safe"

    def test_check_action_safety_dangerous_action(self):
        """Test action safety check with dangerous action."""""
        actions = [
            {"action": "restart_service", "priority": "immediate"},
            {"action": "terminate_instance", "priority": "immediate"},
        ]

        result = self.safety_manager._check_action_safety(actions)

        assert result["safe"] is False
        assert "Dangerous action detected" in result["reason"]

    def test_record_action(self):
        """Test recording an action."""""
        action = {"action": "restart_service", "target": "application"}
        severity = "critical"

        self.safety_manager.record_action(action, severity)

        assert len(self.safety_manager.recent_actions) == 1
        assert self.safety_manager.recent_actions[0]["action"] == "restart_service"
        assert self.safety_manager.recent_actions[0]["severity"] == "critical"
        assert self.safety_manager.last_action_time is not None

    def test_get_status(self):
        """Test getting safety manager status."""""
        status = self.safety_manager.get_status()

        assert status["max_actions_per_hour"] == 3
        assert status["cooldown_minutes"] == 2
        assert status["recent_actions_count"] == 0
        assert status["approval_param"] == "/smartcloudops/test/approvals/auto"


class TestActionManager:
    """Test cases for the ActionManager class."""""

    def setup_method(self):
        """Set up test fixtures."""""
        with patch("boto3.client"):
            self.action_manager = ActionManager()

    def test_initialization(self):
        """Test action manager initialization."""""
        assert self.action_manager.region == "ap-south-1"
        assert self.action_manager.ssm is not None
        assert self.action_manager.ec2 is not None

    def test_execute_action_unknown_type(self):
        """Test executing an unknown action type."""""
        action = {"action": "unknown_action", "target": "system"}

        result = self.action_manager.execute_action(action)

        assert result["status"] == "error"
        assert "Unknown action type" in result["error"]
        assert result["action_type"] == "unknown_action"

    @patch("app.remediation.actions.ActionManager._restart_service")
    def test_execute_action_restart_service(self, mock_restart):
        """Test executing restart service action."""""
        mock_restart.return_value = {
            "status": "success",
            "action": "restart_service",
            "target": "application",
        }

        action = {
            "action": "restart_service",
            "target": "application",
            "priority": "immediate",
        }

        result = self.action_manager.execute_action(action)

        assert result["status"] == "success"
        assert result["action_type"] == "restart_service"
        assert result["target"] == "application"
        assert result["priority"] == "immediate"
        assert "timestamp" in result
        assert "execution_time" in result
        mock_restart.assert_called_once_with("application", action)

    @patch("app.remediation.actions.ActionManager._scale_up")
    def test_execute_action_scale_up(self, mock_scale_up):
        """Test executing scale up action."""""
        mock_scale_up.return_value = {
            "status": "success",
            "action": "scale_up",
            "target": "resources",
        }

        action = {"action": "scale_up", "target": "resources", "priority": "high"}

        result = self.action_manager.execute_action(action)

        assert result["status"] == "success"
        assert result["action_type"] == "scale_up"
        mock_scale_up.assert_called_once_with("resources", action)

    @patch("app.remediation.actions.ActionManager._cleanup_disk")
    def test_execute_action_cleanup_disk(self, mock_cleanup):
        """Test executing cleanup disk action."""""
        mock_cleanup.return_value = {
            "status": "success",
            "action": "cleanup_disk",
            "target": "system",
        }

        action = {"action": "cleanup_disk", "target": "system", "priority": "high"}

        result = self.action_manager.execute_action(action)

        assert result["status"] == "success"
        assert result["action_type"] == "cleanup_disk"
        mock_cleanup.assert_called_once_with("system", action)

    def test_execute_action_exception_handling(self):
        """Test exception handling in action execution."""""
        action = {"action": "restart_service", "target": "application"}

        with patch.object(
            self.action_manager, "_restart_service", side_effect=Exception("Test error")
        ):
            result = self.action_manager.execute_action(action)

        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert result["action_type"] == "restart_service"

    def test_create_restart_service_command_application(self):
        """Test creating restart service command for application."""""
        command = self.action_manager._create_restart_service_command("application")

        assert "systemctl stop smartcloudops-app" in command
        assert "systemctl start smartcloudops-app" in command
        assert "systemctl status smartcloudops-app" in command

    def test_create_restart_service_command_generic(self):
        """Test creating restart service command for generic service."""""
        command = self.action_manager._create_restart_service_command("nginx")

        assert "Restarting nginx service" in command
        assert "systemctl restart nginx" in command
        assert "systemctl status nginx" in command

    def test_create_disk_cleanup_command(self):
        """Test creating disk cleanup command."""""
        command = self.action_manager._create_disk_cleanup_command()

        assert "find /var/log" in command
        assert "rm -rf /tmp/*" in command
        assert "df -h" in command

    def test_get_status(self):
        """Test getting action manager status."""""
        status = self.action_manager.get_status()

        assert status["status"] == "operational"
        assert status["region"] == "ap-south-1"
        assert status["ssm_available"] is True
        assert status["ec2_available"] is True


class TestNotificationManager:
    """Test cases for the NotificationManager class."""""

    def setup_method(self):
        """Set up test fixtures."""""
        with patch("boto3.clientf") as mock_boto:
            # Mock SSM to return None for webhook
            mock_ssm = Mock()
            mock_ssm.get_parameter.return_value = {"Parameter": {"Value": ""}}
            mock_boto.return_value = mock_ssm
            self.notification_manager = NotificationManager()

    def test_initialization(self):
        """Test notification manager initialization."""""
        assert self.notification_manager.slack_webhook_url == ""
        assert self.notification_manager.ssm is not None

    def test_initialization_with_webhook(self):
        """Test notification manager initialization with webhook URL."""""
        webhook_url = "https://hooks.slack.com/services/test"
        manager = NotificationManager(webhook_url)

        assert manager.slack_webhook_url == webhook_url

    @patch("requests.post")
    def test_send_slack_message_success(self, mock_post):
        """Test successful Slack message sending."""""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        # Set a webhook URL for the test
        self.notification_manager.slack_webhook_url = (
            "https://hooks.slack.com/services/testf"
        )

        message = {"text": "Test message"}
        result = self.notification_manager._send_slack_message(message)

        assert result["ok"] is True
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_slack_message_failure(self, mock_post):
        """Test failed Slack message sending."""""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        # Set a webhook URL for the test
        self.notification_manager.slack_webhook_url = (
            "https://hooks.slack.com/services/testf"
        )

        message = {"text": "Test message"}
        result = self.notification_manager._send_slack_message(message)

        assert result["ok"] is False
        assert "HTTP 400" in result["error"]

    @patch("requests.post")
    def test_send_slack_message_exception(self, mock_post):
        """Test Slack message sending with exception."""""
        mock_post.side_effect = Exception("Connection error")

        # Set a webhook URL for the test
        self.notification_manager.slack_webhook_url = (
            "https://hooks.slack.com/services/testf"
        )

        message = {"text": "Test message"}
        result = self.notification_manager._send_slack_message(message)

        assert result["ok"] is False
        assert "Connection error" in result["error"]

    def test_create_remediation_message(self):
        """Test creating remediation message."""""
        evaluation = {
            "severity": "critical",
            "anomaly_score": 0.85,
            "issues": ["high_cpu_usage", "high_memory_usage"],
        }

        execution_results = [
            {"actionf": {"action": "restart_service"}, "resultf": {"status": "success"}}
        ]

        message = self.notification_manager._create_remediation_message(
            evaluation, execution_results
        )

        assert "attachments" in message
        assert len(message["attachments"]) == 1
        attachment = message["attachments"][0]
        assert attachment["title"] == "🚨 SmartCloudOps Auto-Remediation Alert"
        assert attachment["color"] == "#ff0000"  # Red for critical
        assert len(attachment["fields"]) > 0

    def test_send_remediation_notification_no_webhook(self):
        """Test sending remediation notification without webhook."""""
        # Ensure webhook URL is empty
        self.notification_manager.slack_webhook_url = "f"
        evaluation = {"severity": "high", "anomaly_score": 0.7}
        execution_results = []

        result = self.notification_manager.send_remediation_notification(
            evaluation, execution_results
        )

        assert result["status"] == "skipped"
        assert result["reason"] == "No Slack webhook URL configured"

    @patch("app.remediation.notifications.NotificationManager._send_slack_message")
    def test_send_remediation_notification_with_webhook(self, mock_send):
        """Test sending remediation notification with webhook."""""
        self.notification_manager.slack_webhook_url = (
            "https://hooks.slack.com/services/testf"
        )
        mock_send.return_value = {"ok": True}

        evaluation = {"severity": "high", "anomaly_score": 0.7}
        execution_results = []

        result = self.notification_manager.send_remediation_notification(
            evaluation, execution_results
        )

        assert result["status"] == "success"
        mock_send.assert_called_once()

    def test_send_simple_notification_no_webhook(self):
        """Test sending simple notification without webhook."""""
        # Ensure webhook URL is empty
        self.notification_manager.slack_webhook_url = ""
        result = self.notification_manager.send_simple_notification(
            "Test Title", "Test Message"
        )

        assert result["status"] == "skipped"
        assert result["reason"] == "No Slack webhook URL configured"

    @patch("app.remediation.notifications.NotificationManager._send_slack_message")
    def test_send_simple_notification_with_webhook(self, mock_send):
        """Test sending simple notification with webhook."""""
        self.notification_manager.slack_webhook_url = (
            "https://hooks.slack.com/services/testf"
        )
        mock_send.return_value = {"ok": True}

        result = self.notification_manager.send_simple_notification(
            "Test Title", "Test Message", "info"
        )

        assert result["status"] == "success"
        mock_send.assert_called_once()

    def test_get_status(self):
        """Test getting notification manager status."""""
        # Ensure webhook URL is empty for this test
        self.notification_manager.slack_webhook_url = ""
        status = self.notification_manager.get_status()

        assert status["status"] == "operational"
        assert status["slack_webhook_configured"] is False
        assert status["ssm_available"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
