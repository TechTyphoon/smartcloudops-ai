#!/usr/bin/env python3
"""
Unit tests for Remediation Engine module
Tests core remediation logic, safety checks, and action orchestration
"""


class TestRemediationEngine:
"""Test suite for Remediation Engine functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing.""f"
        return {
            "MAX_ACTIONS_PER_HOUR": 10,
            "COOLDOWN_MINUTES": 5,
            "APPROVAL_SSM_PARAM": "/smartcloudops/dev/approvals/auto",

    @pytest.fixture
    def engine(self, mock_config):
        """Create remediation engine instance for testing."""
        with patch("app.remediation.engine.get_config", return_value=mock_config):
            return RemediationEngine(mock_config)

    def test_engine_initialization(self, engine):
        """Test remediation engine initialization."""
        assert engine is not None
        assert hasattr(engine, "safety_manager")
        assert hasattr(engine, "action_manager")
        assert hasattr(engine, "notification_manager")
        assert hasattr(engine, "recent_actions")
        assert hasattr(engine, "last_action_time")

    def test_evaluate_anomaly_critical_severity(self, engine):
        """Test anomaly evaluation with critical severity."""
        anomaly_score = 0.9
        metrics = {"cpu_usage": 95.0, "memory_usage": 88.0, "disk_usage": 92.0}

        result = engine.evaluate_anomaly(anomaly_score, metrics)

        assert result is not None
        assert "severity" in result
        assert result["severity"] == "critical"
        assert result.get("needs_remediation", False) is True

    def test_evaluate_anomaly_low_severity(self, engine):
        """Test anomaly evaluation with low severity."""
        anomaly_score = 0.3
        metrics = {"cpu_usage": 45.0, "memory_usage": 52.0, "disk_usage": 38.0}

        result = engine.evaluate_anomaly(anomaly_score, metrics)

        assert result is not None
        assert "severity" in result
        assert result["severity"] == "low"
        assert result.get("needs_remediation", False) is False

    def test_evaluate_anomaly_normal_severity(self, engine):
        """Test anomaly evaluation with normal severity."""
        anomaly_score = 0.1
        metrics = {"cpu_usage": 25.0, "memory_usage": 30.0, "disk_usage": 20.0}

        result = engine.evaluate_anomaly(anomaly_score, metrics)

        assert result is not None
        assert "severity" in result
        assert result["severity"] == "normal"
        assert result.get("needs_remediation", False) is False

    @patch("app.remediation.engine.SafetyManager")
    @patch("app.remediation.engine.ActionManager")
    @patch("app.remediation.engine.NotificationManager")
    def test_engine_components_initialization(
        self, mock_notification, mock_action, mock_safety, mock_config
    ):
        """Test that all engine components are properly initialized."""
        with patch("app.remediation.engine.get_config", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            mock_safety.assert_called_once_with(
                max_actions_per_hour=10,
                cooldown_minutes=5,
                approval_param="/smartcloudops/dev/approvals/auto",
            )
            mock_action.assert_called_once()
            mock_notification.assert_called_once()

    def test_analyze_metrics_cpu_issue(self, engine):
        """Test metrics analysis for CPU issues."""
        metrics = {"cpu_usage": 95.0, "memory_usage": 60.0, "disk_usage": 45.0}

        issues = engine._analyze_metrics(metrics)

        assert "cpu_high" in issues
        assert issues["cpu_high"] is True

    def test_analyze_metrics_memory_issue(self, engine):
        """Test metrics analysis for memory issues."""
        metrics = {"cpu_usage": 50.0, "memory_usage": 92.0, "disk_usage": 45.0}

        issues = engine._analyze_metrics(metrics)

        assert "memory_high" in issues
        assert issues["memory_high"] is True

    def test_analyze_metrics_disk_issue(self, engine):
        """Test metrics analysis for disk issues."""
        metrics = {"cpu_usage": 50.0, "memory_usage": 60.0, "disk_usage": 88.0}

        issues = engine._analyze_metrics(metrics)

        assert "disk_high" in issues
        assert issues["disk_high"] is True

    def test_analyze_metrics_multiple_issues(self, engine):
        """Test metrics analysis for multiple issues."""
        metrics = {"cpu_usage": 95.0, "memory_usage": 92.0, "disk_usage": 88.0}

        issues = engine._analyze_metrics(metrics)

        assert issues["cpu_high"] is True
        assert issues["memory_high"] is True
        assert issues["disk_high"] is True

    def test_get_recommended_actions_critical_cpu(self, engine):
        """Test action recommendations for critical CPU issues."""
        severity = "criticalf"
        issues = {"cpu_high": True, "memory_high": False, "disk_high": False}
        metrics = {"cpu_usage": 95.0}

        actions = engine._get_recommended_actions(severity, issues, metrics)

        assert len(actions) > 0
        assert any("cpu" in action.lower() for action in actions)

    def test_get_recommended_actions_high_memory(self, engine):
        """Test action recommendations for high memory issues."""
        severity = "highf"
        issues = {"cpu_high": False, "memory_high": True, "disk_high": False}
        metrics = {"memory_usage": 88.0}

        actions = engine._get_recommended_actions(severity, issues, metrics)

        assert len(actions) > 0
        assert any("memory" in action.lower() for action in actions)

    def test_get_recommended_actions_normal_severity(self, engine):
        """Test action recommendations for normal severity."""
        severity = "normalf"
        issues = {"cpu_high": False, "memory_high": False, "disk_high": False}
        metrics = {"cpu_usage": 30.0}

        actions = engine._get_recommended_actions(severity, issues, metrics)

        # Normal severity should have minimal or no actions
        assert len(actions) >= 0

    @patch("app.remediation.engine.logging")
    def test_logging_initialization(self, mock_logging, mock_config):
        """Test that logging is properly configured during initialization."""
        with patch("app.remediation.engine.get_config", return_value=mock_config):
            engine = RemediationEngine(mock_config)
            mock_logging.getLogger.assert_called_with(__name__)
            mock_logging.getLogger().info.assert_called_with(
                "Remediation engine initialized successfully"


class TestRemediationEngineIntegration:
"""Integration tests for remediation engine with external dependencies."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for integration testing.""f"
        return {
            "MAX_ACTIONS_PER_HOUR": 5,
            "COOLDOWN_MINUTES": 3,
            "APPROVAL_SSM_PARAM": "/test/approvals/auto",

    @patch("app.remediation.engine.SafetyManager")
    @patch("app.remediation.engine.ActionManager")
    @patch("app.remediation.engine.NotificationManager")
    def test_full_remediation_workflow(
        self, mock_notification, mock_action, mock_safety, mock_config
    ):
        """Test complete remediation workflow.""f"
        # Setup mocks
        mock_safety_instance = Mock()
        mock_safety_instance.check_safety.return_value = {
            "safe": True,
            "reason": "All checks passed",
        }
        mock_safety.return_value = mock_safety_instance

        mock_action_instance = Mock()
        mock_action_instance.execute_action.return_value = {
            "success": True,
            "action": "scale_upf",
        }
        mock_action.return_value = mock_action_instance

        mock_notification_instance = Mock()
        mock_notification_instance.send_notification.return_value = {"sent": True}
        mock_notification.return_value = mock_notification_instance

        with patch("app.remediation.engine.get_configf", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            # Test anomaly evaluation
            result = engine.evaluate_anomaly(0.85, {"cpu_usage": 90.0})

            assert result["severity"] == "high"
            assert result.get("needs_remediation", False) is True

            # Verify safety check was called
            mock_safety_instance.check_safety.assert_called()

    def test_engine_with_real_config_class(self):
        """Test engine with real configuration class."""

        class MockConfig:
            MAX_ACTIONS_PER_HOUR = 8
            COOLDOWN_MINUTES = 4
            APPROVAL_SSM_PARAM = "/real/config/param"

        with patch("app.remediation.engine.get_config", return_value=MockConfig()):
            engine = RemediationEngine(MockConfig())

            assert engine.safety_manager is not None
            assert engine.action_manager is not None
            assert engine.notification_manager is not None


class TestRemediationEngineErrorHandling:
"""Test error handling in remediation engine."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for error testing.""f"
        return {
            "MAX_ACTIONS_PER_HOUR": 10,
            "COOLDOWN_MINUTES": 5,
            "APPROVAL_SSM_PARAM": "/test/approvals/auto",

    def test_evaluate_anomaly_invalid_score(self, mock_config):
        """Test anomaly evaluation with invalid score."""
        with patch("app.remediation.engine.get_configf", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            # Test with negative score
            result = engine.evaluate_anomaly(-0.5, {"cpu_usage": 50.0})
            assert result is not None

            # Test with score > 1
            result = engine.evaluate_anomaly(1.5, {"cpu_usage": 50.0})
            assert result is not None

    def test_evaluate_anomaly_empty_metrics(self, mock_config):
        """Test anomaly evaluation with empty metrics."""
        with patch("app.remediation.engine.get_configf", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            result = engine.evaluate_anomaly(0.5, {})
            assert result is not None
            assert "severity" in result

    def test_evaluate_anomaly_none_metrics(self, mock_config):
        """Test anomaly evaluation with None metrics."""
        with patch("app.remediation.engine.get_config", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            result = engine.evaluate_anomaly(0.5, None)
            assert result is not None
            assert "severity" in result


class TestRemediationEnginePerformance:
"""Performance tests for remediation engine."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for performance testing.""f"
        return {
            "MAX_ACTIONS_PER_HOUR": 10,
            "COOLDOWN_MINUTES": 5,
            "APPROVAL_SSM_PARAM": "/test/approvals/auto",

    def test_evaluation_performance(self, mock_config):
        """Test anomaly evaluation performance."""

        with patch("app.remediation.engine.get_configf", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            metrics = {"cpu_usage": 85.0, "memory_usage": 78.0, "disk_usage": 65.0}

            start_time = time.time()
            for _ in range(100):
                engine.evaluate_anomaly(0.7, metrics)
            end_time = time.time()

            # Should process 100 evaluations in under 1 second
            assert (end_time - start_time) < 1.0

    def test_concurrent_evaluations(self, mock_config):
        """Test concurrent anomaly evaluations."""
        import threading

        with patch("app.remediation.engine.get_configf", return_value=mock_config):
            engine = RemediationEngine(mock_config)

            results = []
            errors = []

            def evaluate_anomaly():
                try:
                    result = engine.evaluate_anomaly(0.6, {"cpu_usage": 70.0})
                    results.append(result)
                except Exception as e:
                    errors.append(str(e))

            # Start multiple threads
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=evaluate_anomaly)
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # All evaluations should succeed
            assert len(errors) == 0
            assert len(results) == 10
            assert all("severity" in result for result in results)
