"""
Integration tests for ML model deployment
"""

import pytest
import requests
import time
import json
from typing import Dict, Any


class TestMLModelDeployment:
    """Test ML model deployment and functionality."""

    @pytest.fixture
    def base_url(self):
        """Base URL for the application."""
        return "http://localhost:5000"

    def test_ml_model_info_endpoint(self, base_url):
        """Test ML model info endpoint."""
        try:
            response = requests.get(f"{base_url}/api/ml/model/info", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "model_info" in data["data"]

            model_info = data["data"]["model_info"]
            assert "model_name" in model_info
            assert "version" in model_info
            assert "status" in model_info
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_prediction(self, base_url):
        """Test ML model prediction endpoint."""
        test_data = {
            "metric_name": "cpu_usage",
            "value": 85.5,
            "threshold": 80.0,
            "severity": "high",
            "source": "integration_test",
        }

        try:
            response = requests.post(
                f"{base_url}/api/anomalies/", json=test_data, timeout=5
            )

            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "anomaly_id" in data["data"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_health(self, base_url):
        """Test ML model health check."""
        try:
            response = requests.get(f"{base_url}/api/ml/model/health", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "status" in data["data"]
            assert data["data"]["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_metrics(self, base_url):
        """Test ML model metrics endpoint."""
        try:
            response = requests.get(f"{base_url}/api/ml/model/metrics", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "metrics" in data["data"]

            metrics = data["data"]["metrics"]
            assert "accuracy" in metrics
            assert "precision" in metrics
            assert "recall" in metrics
            assert "f1_score" in metrics
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_batch_prediction(self, base_url):
        """Test ML model batch prediction."""
        test_data = {
            "predictions": [
                {
                    "metric_name": "cpu_usage",
                    "value": 85.5,
                    "threshold": 80.0,
                    "severity": "high",
                    "source": "batch_test_1",
                },
                {
                    "metric_name": "memory_usage",
                    "value": 75.2,
                    "threshold": 80.0,
                    "severity": "medium",
                    "source": "batch_test_2",
                },
            ]
        }

        try:
            response = requests.post(
                f"{base_url}/api/ml/model/batch-predict", json=test_data, timeout=5
            )

            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "predictions" in data["data"]
            assert len(data["data"]["predictions"]) == 2
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_version_info(self, base_url):
        """Test ML model version information."""
        try:
            response = requests.get(f"{base_url}/api/ml/model/versions", timeout=5)
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "versions" in data["data"]

            versions = data["data"]["versions"]
            assert isinstance(versions, list)
            if versions:
                version = versions[0]
                assert "version" in version
                assert "created_at" in version
                assert "status" in version
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_retrain_trigger(self, base_url):
        """Test ML model retrain trigger."""
        try:
            response = requests.post(f"{base_url}/api/ml/model/retrain", timeout=5)
            # This might return 202 (accepted) or 200 (completed)
            assert response.status_code in [200, 202]

            data = response.json()
            assert "data" in data
            assert "status" in data["data"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask application not running - skipping integration test")

    def test_ml_model_performance_under_load(self, base_url):
        """Test ML model performance under load."""
        test_data = {
            "metric_name": "cpu_usage",
            "value": 85.5,
            "threshold": 80.0,
            "severity": "high",
            "source": "load_test",
        }

        response_times = []
        num_requests = 10

        for i in range(num_requests):
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/anomalies/", json=test_data, timeout=10
            )
            end_time = time.time()

            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)

        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 2000  # Should be under 2 seconds

        print(f"Average response time: {avg_response_time:.2f}ms")

    def test_ml_model_error_handling(self, base_url):
        """Test ML model error handling."""
        # Test with invalid data
        invalid_data = {"invalid_field": "invalid_value"}

        response = requests.post(
            f"{base_url}/api/anomalies/", json=invalid_data, timeout=10
        )

        # Should return 400 (Bad Request) or 422 (Unprocessable Entity)
        assert response.status_code in [400, 422]

        data = response.json()
        assert "error" in data or "message" in data
