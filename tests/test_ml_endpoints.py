#!/usr/bin/env python3
"""
Tests for ML anomaly detection endpoints
"""

import os
import sys
from unittest.mock import patch


# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set testing environment to bypass auth
os.environ["TESTING"] = "true"


def test_detect_anomaly_success(client, mock_anomaly_detector):
    """Test successful anomaly detection."""
    with patch("flask.current_app.anomaly_detector", mock_anomaly_detector):
        response = client.post(
            "/api/ml/anomaly", json={"metrics": {"cpu_usage_avg": 90.0}}
        )
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        assert result["data"]["is_anomaly"] == True


def test_detect_anomaly_invalid_data(client):
    """Test anomaly detection with invalid data."""
    response = client.post("/api/ml/anomaly", json={})
    assert response.status_code == 400


def test_detect_anomaly_no_metrics(client):
    """Test anomaly detection with no metrics."""
    response = client.post("/api/ml/anomaly", json={"data": {}})
    assert response.status_code == 400
    result = response.get_json()
    assert "message" in result  # API returns "message" not "error"


def test_model_status(client, mock_anomaly_detector):
    """Test model status endpoint."""
    with patch("flask.current_app.anomaly_detector", mock_anomaly_detector):
        response = client.get("/api/ml/stats")
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        assert "stats" in result["data"]
        assert result["data"]["stats"]["total_models"] == 2


def test_train_model_success(client, mock_anomaly_detector, auth_headers):
    """Test successful model training."""
    data = {
        "model_name": "test_model",
        "algorithm": "isolation_forest",
        "dataset_id": 1,
        "force_retrain": True,
    }
    response = client.post("/api/ml/train", json=data, headers=auth_headers)
    assert response.status_code == 201
    result = response.get_json()
    assert result["status"] == "success"
    assert "training_job" in result["data"]


def test_train_model_default(client, mock_anomaly_detector, auth_headers):
    """Test model training with default parameters."""
    data = {
        "model_name": "default_model",
        "algorithm": "random_forest",
        "dataset_id": 1,
    }
    response = client.post("/api/ml/train", json=data, headers=auth_headers)
    assert response.status_code == 201
    result = response.get_json()
    assert result["status"] == "success"
    assert "training_job" in result["data"]


def test_ml_endpoints_error_handling(client, mock_anomaly_detector):
    """Test error handling in ML endpoints."""
    # Mock exception
    mock_anomaly_detector.detect_anomaly.side_effect = Exception("Test error")

    with patch("flask.current_app.anomaly_detector", mock_anomaly_detector):
        data = {"metrics": {"cpu_usage_avg": 85.0}}
        response = client.post("/api/ml/anomaly", json=data)

        assert response.status_code == 500
        result = response.get_json()
        assert "message" in result  # API returns "message" not "error"
