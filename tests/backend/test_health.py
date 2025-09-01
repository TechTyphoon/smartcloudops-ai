"""Test health endpoint."""

import json
import time
from typing import Any

try:
    # In test environments the test client fixture provides a Flask test client
    from werkzeug.test import Client as FlaskClient  # type: ignore
except Exception:  # pragma: no cover - import fallbacks for static analysis
    FlaskClient = Any  # type: ignore


def test_health_endpoint(client: FlaskClient):
    """Test /health endpoint returns 200 and expected structure."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)

    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "checks" in data

    # Check status is healthy
    assert data["status"] == "healthy"

    # Check timestamp is numeric
    assert isinstance(data["timestamp"], (int, float))

    # Check version format
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0

    # Check checks object structure
    checks = data["checks"]
    assert isinstance(checks, dict)

    # Check specific components (may be None in test mode)
    expected_checks = ["ai_handler", "ml_models", "remediation_engine"]
    for check in expected_checks:
        assert check in checks


def test_api_health_endpoint(client: FlaskClient):
    """Test /api/health endpoint returns same as /health."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)

    # Should have same structure as /health
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "checks" in data
    assert data["status"] == "healthy"


def test_health_endpoint_methods(client: FlaskClient):
    """Test health endpoint only accepts GET method."""
    # Test POST should fail
    response = client.post("/health")
    assert response.status_code == 405  # Method Not Allowed

    # Test PUT should fail
    response = client.put("/health")
    assert response.status_code == 405

    # Test DELETE should fail
    response = client.delete("/health")
    assert response.status_code == 405


def test_health_response_time(client: FlaskClient):
    """Test health endpoint responds quickly."""

    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    assert response.status_code == 200
    # Should respond within 1 second
    assert (end_time - start_time) < 1.0
