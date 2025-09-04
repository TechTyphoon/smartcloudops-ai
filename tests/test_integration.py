#!/usr/bin/env python3
"""
Integration tests for Smart CloudOps AI
Tests complete workflow: ML -> ChatOps -> Auto-Remediation
"""

import os
import sys
import time
from unittest.mock import Mock, patch

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the modules to test
try:
    from app.chatops.ai_handler import FlexibleAIHandler
    from app.main import app
    from app.mlops.anomaly_detector import AnomalyDetector
    from app.remediation.engine import RemediationEngine
except ImportError:
    # Create mock classes for testing if modules are not available
    class FlexibleAIHandler:
        def __init__(self):
            pass

        def process_query(self, query):
            return {"status": "error", "response": "AI handler not available"}

    class AnomalyDetector:
        def __init__(self):
            pass

        def detect_anomaly(self, data):
            return {"status": "error", "response": "Anomaly detector not available"}

        def batch_detect(self, data):
            return [{"status": "error", "response": "Anomaly detector not available"}]

        def get_system_status(self):
            return {"status": "error"}

        def get_model_status(self):
            return {"status": "error"}

    class RemediationEngine:
        def __init__(self):
            pass

        def evaluate_anomaly(self, score, metrics):
            return {"status": "error", "response": "Remediation engine not available"}

        def execute_remediation(self, evaluation):
            return {"status": "error", "response": "Remediation engine not available"}

        def get_status(self):
            return {"status": "error"}

    # Import the real app
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True


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
            "status": "success",
            "response": "Test AI response",
            "timestamp": "2025-08-09T00:00:00Z",
        }
        handler.provider = Mock()  # Add provider attribute
        return handler

    @pytest.fixture
    def mock_anomaly_detector(self):
        """Mock anomaly detector for testing."""
        detector = Mock(spec=AnomalyDetector)
        detector.detect_anomaly.return_value = {
            "status": "success",
            "is_anomaly": True,
            "severity_score": 0.85,
            "explanation": "High CPU usage detected",
            "timestamp": "2025-08-09T00:00:00Z",
        }
        detector.batch_detect.return_value = [
            {
                "status": "success",
                "is_anomaly": True,
                "severity_score": 0.85,
                "explanation": "High CPU usage detected",
                "timestamp": "2025-08-09T00:00:00Z",
            }
        ]
        detector.get_system_status.return_value = {
            "initialized": True,
            "model_exists": True,
            "status": "operational",
        }
        detector.get_model_status.return_value = {
            "is_trained": True,
            "model_type": "IsolationForest",
            "model_exists": True,
            "status": "operational",
            "initialized": True,
        }
        return detector

    @pytest.fixture
    def mock_remediation_engine(self):
        """Mock remediation engine for testing."""
        engine = Mock(spec=RemediationEngine)
        engine.evaluate_anomaly.return_value = {
            "timestamp": "2025-08-09T00:00:00Z",
            "anomaly_score": 0.85,
            "severity": "high",
            "needs_remediation": True,
            "issues": ["high_cpu_usage"],
            "recommended_actions": [
                {
                    "action": "scale_up",
                    "priority": "high",
                    "reason": "High CPU usage detected",
                    "target": "resources",
                }
            ],
        }
        engine.execute_remediation.return_value = {
            "executed": True,
            "safety_check": {"safe_to_proceed": True},
            "execution_results": [
                {
                    "action": {"action": "scale_up"},
                    "result": {"status": "success"},
                    "timestamp": "2025-08-09T00:00:00Z",
                }
            ],
            "timestamp": "2025-08-09T00:00:00Z",
        }
        return engine

    def test_complete_ml_to_remediation_workflow(
        self, client, mock_anomaly_detector, mock_remediation_engine
    ):
        """Test complete workflow from ML anomaly detection to auto-remediation."""

        # Step 1: Detect anomaly using ML endpoint
        anomaly_data = {
            "metrics": {
                "cpu_usage": 95.0,
                "memory_usage": 88.0,
                "disk_usage": 75.0,
            },
            "timestamp": "2025-08-31T16:00:00Z",
        }

        # Test the ML endpoint without mocking - it should work with the real anomaly detector
        response = client.post("/api/ml/anomaly", json=anomaly_data)
        assert response.status_code == 200
        anomaly_result = response.get_json()
        assert anomaly_result["status"] == "success"
        assert "data" in anomaly_result

        # Step 2: Create remediation action
        remediation_data = {
            "anomaly_id": 1,
            "action_type": "scale_up",
            "action_name": "Scale Up Resources",
            "description": "Scale up resources due to high CPU usage",
            "parameters": {"instance_count": 2},
        }

        response = client.post("/api/remediation/actions", json=remediation_data)
        assert response.status_code == 201
        remediation_result = response.get_json()
        assert remediation_result["status"] == "success"
        assert "remediation_action" in remediation_result["data"]
        action_id = remediation_result["data"]["remediation_action"]["id"]

        # Step 3: Execute remediation action
        response = client.post(f"/api/remediation/actions/{action_id}/execute")
        assert response.status_code == 200
        execution_result = response.get_json()
        assert execution_result["status"] == "success"
        assert "execution_result" in execution_result["data"]

    def test_chatops_with_ml_context(self, client, mock_ai_handler, auth_headers):
        """Test ChatOps query with ML context."""

        query_data = {"query": "What anomalies were detected recently?"}

        with patch("app.api.chatops.GPTHandler") as mock_gpt_class:
            mock_handler = Mock()
            mock_handler.process_query.return_value = {
                "status": "success",
                "response": "Recent anomalies detected: High CPU usage on server-01",
                "timestamp": "2025-08-31T16:00:00Z",
                "model": "gpt-4",
            }
            mock_gpt_class.return_value = mock_handler

            response = client.post(
                "/api/chatops", json=query_data, headers=auth_headers
            )
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "response" in result

    def test_smart_query_with_context(self, client, mock_ai_handler, auth_headers):
        """Test smart query with intelligent context gathering."""

        query_data = {"query": "Analyze system health and recent anomalies"}

        with patch("app.api.chatops.GPTHandler") as mock_gpt_class:
            mock_handler = Mock()
            mock_handler.process_query.return_value = {
                "status": "success",
                "response": "System health analysis: CPU 45%, Memory 67%, Disk 23%. Recent anomalies: None detected.",
                "timestamp": "2025-08-31T16:00:00Z",
                "model": "gpt-4",
            }
            mock_gpt_class.return_value = mock_handler

            response = client.post(
                "/api/chatops", json=query_data, headers=auth_headers
            )
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "response" in result

    def test_ml_status_integration(self, client, mock_anomaly_detector):
        """Test ML status endpoint integration."""

        # Test ML endpoint with normal data
        response = client.post(
            "/api/ml/anomaly",
            json={
                "metrics": {
                    "cpu_usage": 45.0,
                    "memory_usage": 60.0,
                    "disk_usage": 30.0,
                },
                "timestamp": "2025-08-31T16:00:00Z",
            },
        )
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        assert "data" in result

    def test_remediation_status_integration(self, client, mock_remediation_engine):
        """Test remediation status endpoint integration."""

        # Test remediation actions endpoint
        response = client.get("/api/remediation/actions")
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        assert "remediation_actions" in result["data"]

    def test_system_context_integration(self, client, auth_headers):
        """Test system context endpoint integration."""

        # Test ChatOps endpoint with context
        query_data = {
            "query": "What is the current system context?",
            "context": {"system_health": "healthy", "recent_alerts": "none"},
        }

        with patch("app.api.chatops.GPTHandler") as mock_gpt_class:
            mock_handler = Mock()
            mock_handler.process_query.return_value = {
                "status": "success",
                "response": "System context: Healthy with no recent alerts",
                "timestamp": "2025-08-31T16:00:00Z",
                "model": "gpt-4",
            }
            mock_gpt_class.return_value = mock_handler

            response = client.post(
                "/api/chatops", json=query_data, headers=auth_headers
            )
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "response" in result

    def test_conversation_summary_integration(self, client, auth_headers):
        """Test conversation summary endpoint integration."""

        # Test ChatOps endpoint for conversation summary
        query_data = {"query": "Summarize our conversation"}

        with patch("app.api.chatops.GPTHandler") as mock_gpt_class:
            mock_handler = Mock()
            mock_handler.process_query.return_value = {
                "status": "success",
                "response": "Conversation summary: Discussed system health and anomaly detection",
                "timestamp": "2025-08-31T16:00:00Z",
                "model": "gpt-4",
            }
            mock_gpt_class.return_value = mock_handler

            response = client.post(
                "/api/chatops", json=query_data, headers=auth_headers
            )
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "response" in result

    def test_error_handling_in_workflow(self, client):
        """Test error handling in the complete workflow."""

        # Test with invalid anomaly data
        invalid_data = {"metrics": {"invalid_metric": "not_a_number"}}

        response = client.post("/api/ml/anomaly", json=invalid_data)
        assert response.status_code == 400  # Should return 400 for invalid input
        result = response.get_json()
        assert result["status"] == "error"

    def test_performance_under_load(self, client, mock_anomaly_detector):
        """Test performance under simulated load."""

        # Simulate multiple concurrent requests
        start_time = time.time()

        responses = []
        for i in range(10):
            data = {
                "metrics": {
                    "cpu_usage": 80.0 + i,
                    "memory_usage": 70.0 + i,
                    "disk_usage": 60.0 + i,
                },
                "timestamp": "2025-08-31T16:00:00Z",
            }
            response = client.post("/api/ml/anomaly", json=data)
            responses.append(response)

        end_time = time.time()
        total_time = end_time - start_time

        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)

        # Performance check: 10 requests should complete in reasonable time
        assert total_time < 5.0  # Should complete within 5 seconds

    def test_security_in_workflow(self, client, auth_headers):
        """Test security aspects of the workflow."""

        # NOTE: These are intentionally malicious patterns for testing security validation
        # They are safe in this test context as they are never executed
        malicious_queries = [
            {"query": "system('rm -rf /')"},
            {"query": "import os; os.system('ls')"},
            {"query": "SELECT * FROM users"},
            {"query": "javascript:alert('xss')"},
        ]

        for query in malicious_queries:
            response = client.post("/api/chatops", json=query, headers=auth_headers)
            # Should either reject or handle safely
            assert response.status_code in [200, 400, 500]
            result = response.get_json()
            # Should not expose internal errors
            assert "internal" not in str(result).lower()

    def test_data_consistency_across_endpoints(
        self, client, mock_anomaly_detector, auth_headers
    ):
        """Test data consistency across different endpoints."""

        test_metrics = {
            "cpu_usage": 90.0,
            "memory_usage": 85.0,
            "disk_usage": 80.0,
        }

        # Test anomaly detection
        anomaly_response = client.post(
            "/api/ml/anomaly",
            json={"metrics": test_metrics, "timestamp": "2025-08-31T16:00:00Z"},
        )
        anomaly_data = anomaly_response.get_json()

        # Test anomalies endpoint
        anomalies_response = client.get("/api/anomalies", headers=auth_headers)
        anomalies_data = anomalies_response.get_json()

        # Data should be consistent
        assert anomaly_data["status"] == "success"
        assert anomalies_data["status"] == "success"
        assert "data" in anomaly_data
        assert "data" in anomalies_data


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
