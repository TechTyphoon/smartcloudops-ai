"""Test status endpoint."""

import json
import time
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from werkzeug.test import Client as FlaskClient  # type: ignore
    except Exception:  # pragma: no cover - optional test dependency
        FlaskClient = Any
else:
    # At runtime tests will provide client fixture; keep FlaskClient as Any for runtime
    FlaskClient = Any


def test_status_endpoint(client):
    """Test /status endpoint returns 200 and expected structure."""
    response = client.get("/status")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)

    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "uptime" in data
    assert "components" in data

    # Check status is healthy
    assert data["status"] == "healthy"

    # Check timestamp is numeric
    assert isinstance(data["timestamp"], (int, float))

    # Check uptime is string
    assert isinstance(data["uptime"], str)
    assert len(data["uptime"]) > 0

    # Check components structure
    components = data["components"]
    assert isinstance(components, dict)

    # Check specific components
    expected_components = ["ai_handler", "ml_models", "database", "remediation_engine"]
    for component in expected_components:
        assert component in components


def test_status_components_structure(client):
    """Test status components have expected structure."""
    response = client.get("/status")
    data = json.loads(response.data)
    components = data["components"]

    # Test ai_handler structure
    ai_handler = components.get("ai_handler")
    if ai_handler is not None:
        assert isinstance(ai_handler, dict)
        assert "status" in ai_handler

    # Test ml_models structure
    ml_models = components.get("ml_models")
    if ml_models is not None:
        assert isinstance(ml_models, dict)
        assert "available" in ml_models
        assert isinstance(ml_models["available"], bool)

        # Check status if available
        if ml_models.get("status") is not None:
            assert isinstance(ml_models["status"], dict)

    # Test database structure
    database = components.get("database")
    if database is not None:
        assert isinstance(database, dict)
        assert "connected" in database
        assert isinstance(database["connected"], bool)

    # Test remediation_engine structure
    remediation_engine = components.get("remediation_engine")
    if remediation_engine is not None:
        assert isinstance(remediation_engine, dict)


def test_api_status_endpoint(client):
    """Test /api/status endpoint returns same as /status."""
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data)

    # Should have same structure as /status
    assert "status" in data
    assert "timestamp" in data
    assert "uptime" in data
    assert "components" in data
    assert data["status"] == "healthy"


def test_status_endpoint_methods(client):
    """Test status endpoint only accepts GET method."""
    # Test POST should fail
    response = client.post("/status")
    assert response.status_code == 405  # Method Not Allowed

    # Test PUT should fail
    response = client.put("/status")
    assert response.status_code == 405

    # Test DELETE should fail
    response = client.delete("/status")
    assert response.status_code == 405


def test_status_response_time(client):
    """Test status endpoint responds within reasonable time."""

    start_time = time.time()
    response = client.get("/status")
    end_time = time.time()

    assert response.status_code == 200
    # Should respond within 2 seconds (may need to gather metrics)
    assert (end_time - start_time) < 2.0


def test_status_timestamp_format(client):
    """Test status timestamp is recent."""

    response = client.get("/status")
    data = json.loads(response.data)

    timestamp = data["timestamp"]
    current_time = time.time()

    # Timestamp should be within last 60 seconds
    assert abs(current_time - timestamp) < 60.0
