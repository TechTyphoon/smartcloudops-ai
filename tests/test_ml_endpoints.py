#!/usr/bin/env python3
"""
Tests for ML anomaly detection endpoints
"""

import os
from unittest.mock import Mock, patch

import pytest

# Set testing environment to bypass auth
os.environ["TESTING"] = "true"

from app.main import app


class TestMLEndpoints:
    """Test ML anomaly detection endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_anomaly_detector(self):
        """Mock anomaly detector."""
        with patch("app.main.anomaly_detector") as mock:
            # Configure the mock to return proper dictionaries instead of MagicMocks
            mock.detect_anomaly.return_value = {
                "is_anomaly": True,
                "score": 0.85,
                "severity": "high",
                "explanation": "High CPU usage detected",
            }
            mock.batch_detect.return_value = [
                {"is_anomaly": True, "score": 0.85, "severity": "high"},
                {"is_anomaly": False, "score": 0.15, "severity": "normal"},
            ]
            # Fix: Use get_system_status for the status endpoint
            mock.get_system_status.return_value = {
                "initialized": True,
                "model_exists": True,
                "model_path": "models/anomaly_detector.pkl",
                "status": "operational",
                "config": {"contamination": 0.1},
            }
            # Fix: Use train instead of train_model
            mock.train.return_value = {
                "status": "success",
                "f1_score": 0.95,
                "training_time": 120.5,
            }
            yield mock

    def test_detect_anomaly_success(self, client, mock_anomaly_detector):
        """Test successful anomaly detection."""
        with patch("app.main.anomaly_detector", mock_anomaly_detector):
            response = client.post(
                "/anomaly", json={"metrics": {"cpu_usage_avg": 90.0}}
            )
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert result["data"]["is_anomaly"] == True

    def test_detect_anomaly_invalid_data(self, client):
        """Test anomaly detection with invalid data."""
        response = client.post("/anomaly", json={})
        assert response.status_code == 400

    def test_detect_anomaly_no_metrics(self, client):
        """Test anomaly detection with no metrics."""
        response = client.post("/anomaly", json={"data": {}})
        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result

    def test_batch_detect_anomaly_success(self, client, mock_anomaly_detector):
        """Test successful batch anomaly detection."""
        data = {
            "metrics_batch": [
                {"cpu_usage_avg": 85.0, "memory_usage_pct": 75.0},
                {"cpu_usage_avg": 45.0, "memory_usage_pct": 55.0},
            ]
        }

        response = client.post("/anomaly/batch", json=data)

        assert response.status_code == 200
        result = response.get_json()
        assert "results" in result
        assert len(result["results"]) == 2
        assert result["count"] == 2
        mock_anomaly_detector.batch_detect.assert_called_once()

    def test_batch_detect_anomaly_no_data(self, client):
        """Test batch anomaly detection with no data."""
        response = client.post("/anomaly/batch", json={})
        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result

    def test_model_status(self, client, mock_anomaly_detector):
        """Test model status endpoint."""
        with patch("app.main.anomaly_detector", mock_anomaly_detector):
            response = client.get("/anomaly/status")
            assert response.status_code == 200
            result = response.get_json()
            assert result["status"] == "success"
            assert "system_status" in result["data"]

    def test_train_model_success(self, client, mock_anomaly_detector):
        """Test successful model training."""
        data = {"force_retrain": True}
        response = client.post("/anomaly/train", json=data)
        assert response.status_code == 200
        result = response.get_json()
        assert "status" in result
        # The endpoint doesn't use force_retrain parameter, it gets training_data
        mock_anomaly_detector.train.assert_called_once_with([])

    def test_train_model_default(self, client, mock_anomaly_detector):
        """Test model training with default parameters."""
        response = client.post("/anomaly/train", json={})
        assert response.status_code == 200
        result = response.get_json()
        assert "status" in result
        mock_anomaly_detector.train.assert_called_once_with([])

    def test_ml_endpoints_disabled(self, client):
        """Test ML endpoints when ML is disabled."""
        with patch("app.main.ML_AVAILABLE", False):
            response = client.post(
                "/anomaly", json={"metrics": {"cpu_usage_avg": 90.0}}
            )
            assert response.status_code == 503
            result = response.get_json()
            assert result["status"] == "error"
            assert "disabled" in result["error"]

    def test_ml_endpoints_error_handling(self, client, mock_anomaly_detector):
        """Test error handling in ML endpoints."""
        # Mock exception
        mock_anomaly_detector.detect_anomaly.side_effect = Exception("Test error")

        data = {"metrics": {"cpu_usage_avg": 85.0}}
        response = client.post("/anomaly", json=data)

        assert response.status_code == 500
        result = response.get_json()
        assert "error" in result
