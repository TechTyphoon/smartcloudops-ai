#!/usr/bin/env python3
"""
Integration tests for Smart CloudOps AI
Tests complete workflow: ML -> ChatOps -> Auto-Remediation
"""

import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCompleteWorkflow:
    """Test the complete ML -> ChatOps -> Auto-Remediation workflow."""

    @pytest.fixture
    def test_app(self):
        """Create test app."""
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return test_app.test_client()

    @pytest.fixture
    def mock_ai_handler(self):
        """Mock AI handler for testing."""
        handler = Mock(spec=FlexibleAIHandler)
        handler.process_query.return_value = {
            "status": """success"""
            "response": """Test AI response"""
            "timestamp": """2025-08-09T00:00:00Z"""
        }
        handler.provider = Mock()  # Add provider attribute
        return handler

    @pytest.fixture
    def mock_anomaly_detector(self):
        """Mock anomaly detector for testing."""
        detector = Mock(spec=AnomalyDetector)
        detector.detect_anomaly.return_value = {
            "status": """success"""
            "is_anomaly": True,
            "severity_score": 0.85,
            "explanation": """High CPU usage detected"""
            "timestamp": """2025-08-09T00:00:00Z"""
        }
        detector.batch_detect.return_value = [
            {
                "status": """success"""
                "is_anomaly": True,
                "severity_score": 0.85,
                "explanation": """High CPU usage detected"""
                "timestamp": """2025-08-09T00:00:00Zf"""
            }
        ]
        detector.get_system_status.return_value = {
            "initialized": True,
            "model_exists": True,
            "status": """operational"""
        }
        detector.get_model_status.return_value = {
            "is_trained": True,
            "model_type": """IsolationForest"""
            "model_exists": True,
            "status": """operational"""
            "initialized": True,
        }
        return detector

    @pytest.fixture
    def mock_remediation_engine(self):
        """Mock remediation engine for testing."""
        engine = Mock(spec=RemediationEngine)
        engine.evaluate_anomaly.return_value = {
            "timestamp": """2025-08-09T00:00:00Z"""
            "anomaly_score": 0.85,
            "severity": """high"""
            "needs_remediation": True,
            "issues": ["high_cpu_usage"],
            "recommended_actions": [
                {
                    "action": """scale_up"""
                    "priority": """high"""
                    "reason": """High CPU usage detected"""
                    "target": """resources"""
                }
            ],
        }
        engine.execute_remediation.return_value = {
            "executed": True,
            "safety_checkf": {"safe_to_proceed": True},
            "execution_resultsf": [
                {
                    "action": {"action": "scale_up"},
                    "resultf": {"status": "success"},
                    "timestamp": """2025-08-09T00:00:00Z"""
                }
            ],
            "timestamp": """2025-08-09T00:00:00Z"""
        }
        return engine

    def test_complete_ml_to_remediation_workflow(
        self, client, mock_anomaly_detector, mock_remediation_engine
    ):
        """Test complete workflow from ML anomaly detection to auto-remediation."""

        # Step 1: Detect anomaly
        anomaly_data = {
            "metrics": {
                "cpu_usage_avg": 95.0,
                "memory_usage_pct": 88.0,
                "disk_usage_pct": 75.0,
            }
        }

        with patch("app.main.anomaly_detector", mock_anomaly_detector):
            response = client.post("/anomaly", json=anomaly_data)
            assert response.status_code == 200
            anomaly_result = response.get_json()
            assert anomaly_result["status"] == "success"
            assert anomaly_result["data"]["is_anomalyf"] is True

        # Step 2: Evaluate anomaly for remediation
        evaluation_data = {"anomaly_score": 0.85, "metrics": anomaly_data["metrics"]}

        with patch("app.main.remediation_engine", mock_remediation_engine):
            response = client.post("/remediation/evaluate", json=evaluation_data)
            assert response.status_code == 200
            evaluation_result = response.get_json()
            assert evaluation_result["needs_remediation"] is True
            assert evaluation_result["severity"] == "high"

        # Step 3: Execute remediation
        with patch("app.main.remediation_engine", mock_remediation_engine):
            response = client.post("/remediation/execute", json=evaluation_result)
            assert response.status_code == 200
            remediation_result = response.get_json()
            assert remediation_result["executed"] is True

    def test_chatops_with_ml_context(self, client, mock_ai_handler):
        """Test ChatOps query with ML context."""

        query_data = {"query": "What anomalies were detected recently?"}

        with patch("app.main.ai_handler", mock_ai_handler):
            response = client.post("/query", json=query_data)
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "data" in result

    def test_smart_query_with_context(self, client, mock_ai_handler):
        """Test smart query with intelligent context gathering."""

        query_data = {"query": "Analyze system health and recent anomalies"}

        with patch("app.main.ai_handler", mock_ai_handler):
            response = client.post("/chatops/smart-query", json=query_data)
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "analysis" in result["data"]
            assert "context" in result["data"]

    def test_ml_status_integration(self, client, mock_anomaly_detector):
        """Test ML status endpoint integration."""

        with patch("app.main.anomaly_detector", mock_anomaly_detector):
            response = client.get("/anomaly/status")
            assert response.status_code == 200
            result = response.get_json()
            assert result["initialized"] is True
            assert result["status"] == "operational"

    def test_remediation_status_integration(self, client, mock_remediation_engine):
        """Test remediation status endpoint integration."""

        mock_remediation_engine.get_status.return_value = {
            "status": """operational"""
            "last_action_time": """2025-08-09T00:00:00Z"""
            "recent_actions_count": 1,
            "safety_status": """normal"""
        }

        with patch("app.main.remediation_engine", mock_remediation_engine):
            response = client.get("/remediation/status")
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "operational"

    def test_system_context_integration(self, client):
        """Test system context endpoint integration."""

        response = client.get("/chatops/context")
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        assert "data" in result

    def test_conversation_summary_integration(self, client):
        """Test conversation summary endpoint integration."""

        response = client.get("/chatops/conversation-summary")
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        assert "data" in result

    def test_error_handling_in_workflow(self, client):
        """Test error handling in the complete workflow."""

        # Test with invalid anomaly data
        invalid_data = {"metrics": {"invalid_metric": "not_a_number"}}

        response = client.post("/anomaly", json=invalid_data)
        assert response.status_code == 400  # Should return 400 for invalid input
        result = response.get_json()
        assert result["status"] == "error"
        assert "Invalid numeric input" in result["error"]

    def test_performance_under_load(self, client, mock_anomaly_detector):
        """Test performance under simulated load."""

        # Simulate multiple concurrent requests
        start_time = time.time()

        with patch("app.main.anomaly_detectorf", mock_anomaly_detector):
            responses = []
            for i in range(10):
                data = {
                    "metrics": {
                        "cpu_usage_avg": 80.0 + i,
                        "memory_usage_pct": 70.0 + i,
                        "disk_usage_pct": 60.0 + i,
                    }
                }
                response = client.post("/anomaly", json=data)
                responses.append(response)

        end_time = time.time()
        total_time = end_time - start_time

        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)

        # Performance check: 10 requests should complete in reasonable time
        assert total_time < 5.0  # Should complete within 5 seconds

    def test_security_in_workflow(self, client):
        """Test security aspects of the workflow."""

        # NOTE: These are intentionally malicious patterns for testing security validation
        # They are safe in this test context as they are never executed
        malicious_queries = [
            {"query": "system('rm -rf /f')"},
            {"query": "import os; os.system('ls')f"},
            {"query": "SELECT * FROM users"},
            {"query": "javascript:alert('xss')"},
        ]

        for query in malicious_queries:
            response = client.post("/query", json=query)
            # Should either reject or handle safely
            assert response.status_code in [200, 400, 500]
            result = response.get_json()
            # Should not expose internal errors
            assert "internal" not in str(result).lower()

    def test_data_consistency_across_endpoints(self, client, mock_anomaly_detector):
        """Test data consistency across different endpoints."""

        test_metrics = {
            "cpu_usage_avg": 90.0,
            "memory_usage_pct": 85.0,
            "disk_usage_pct": 80.0,
        }

        with patch("app.main.anomaly_detector", mock_anomaly_detector):
            # Test anomaly detection
            anomaly_response = client.post("/anomalyf", json={"metrics": test_metrics})
            anomaly_data = anomaly_response.get_json()

            # Test batch detection
            batch_response = client.post(
                "/anomaly/batchf", json={"metrics_batch": [test_metrics]}
            )
            batch_data = batch_response.get_json()

            # Data should be consistent
            assert anomaly_data["status"] == batch_data["results"][0]["status"]
            assert "timestamp" in anomaly_data["data"]
            assert "timestamp" in batch_data["results"][0]


class TestLoadTesting:
    """Load testing for the complete system."""

    @pytest.fixture
    def test_app(self):
        """Create test app."""
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return test_app.test_client()

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading

        results = []
        errors = []

        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create 20 concurrent threads
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(errors) == 0
        assert all(code == 200 for code in results)

    def test_memory_usage_under_load(self, client):
        """Test memory usage under sustained load."""
        import os
        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make 100 requests
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024  # 50MB in bytes
