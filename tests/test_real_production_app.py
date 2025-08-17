"""Tests for the real production Flask application."""

import json
import os
import sys

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import our real production app
from app.main_modular import create_app


class TestRealProductionApp:
    """Test cases for the real production Flask application with 100% real data."""

    @pytest.fixture
    def client(self):
        """Create test client for the real app."""
        app = create_app()
        app.config["TESTING"] = True
        return app.test_client()

    def test_health_endpoint_responds(self, client):
        """Test that health endpoint responds correctly."""
        response = client.get("/monitoring/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "status" in data
        assert "services" in data

    def test_status_endpoint_real_data(self, client):
        """Test status endpoint returns real system data."""
        response = client.get("/monitoring/status")
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "system" in data
        assert "application" in data

    def test_metrics_endpoint_prometheus_format(self, client):
        """Test metrics endpoint returns Prometheus format."""
        response = client.get("/monitoring/metrics")
        assert response.status_code == 200
        # Accept both content type formats
        assert "text/plain" in response.content_type

        metrics_text = response.get_data(as_text=True)
        # Check for Prometheus format
        assert "# HELP" in metrics_text
        assert "# TYPE" in metrics_text

    def test_anomaly_status_endpoint(self, client):
        """Test anomaly detection status endpoint."""
        response = client.get("/ml/status")
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "status" in data

    def test_dashboard_loads(self, client):
        """Test that the main dashboard loads correctly."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "message" in data
        assert "Smart CloudOps AI" in data["message"]

    def test_ml_endpoint_responds(self, client):
        """Test that ML endpoint responds."""
        response = client.get("/ml/status")
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "status" in data

    def test_chatops_endpoint_responds(self, client):
        """Test that ChatOps endpoint responds."""
        response = client.get("/chatops/query")
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "message" in data
