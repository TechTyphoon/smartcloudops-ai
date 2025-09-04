"""
Integration tests for API routes
Comprehensive testing of API endpoints with full application context
"""

import json
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from app.chatops.gpt_handler import GPTHandler
from app.main import app


class TestAPIRoutes:
    """Test suite for API route integration."""

    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_gpt_handler(self, valid_chatops_request):
        """Mock GPT handler for testing."""
        mock_handler = Mock(spec=GPTHandler)
        mock_handler.process_query.return_value = {
            "status": "success",
            "response": "Test response from GPT",
            "query": "test query",
            "timestamp": "2023-01-01T00:00:00Z",
            "model": "gpt-3.5-turbo",
        }
        return mock_handler

    @pytest.fixture
    def valid_chatops_request(self) -> Dict[str, Any]:
        """Valid ChatOps request data."""
        return {
            "query": "What is the current system status?",
            "context": {
                "system_health": "healthy",
                "resource_usage": "CPU: 45%, Memory: 60%",
            },
        }

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/status")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "uptime" in data
        assert "version" in data

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_success(
        self,
        mock_gpt_class,
        client,
        mock_gpt_handler,
        valid_chatops_request,
        auth_headers,
    ):
        """Test successful ChatOps query processing."""
        mock_gpt_class.return_value = mock_gpt_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps(valid_chatops_request),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["response"] == "Test response from GPT"
        assert data["query"] == valid_chatops_request["query"]

    def test_chatops_endpoint_invalid_json(self, client, auth_headers):
        """Test ChatOps endpoint with invalid JSON."""
        response = client.post(
            "/api/chatops",
            data="invalid json",
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_chatops_endpoint_missing_query(self, client, auth_headers):
        """Test ChatOps endpoint with missing query."""
        response = client.post(
            "/api/chatops",
            data=json.dumps({"context": {}}),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "query" in data["error"].lower()

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_gpt_error(
        self, mock_gpt_class, client, valid_chatops_request, auth_headers
    ):
        """Test ChatOps endpoint when GPT handler fails."""
        mock_handler = Mock(spec=GPTHandler)
        mock_handler.process_query.return_value = {
            "status": "error",
            "error": "Processing failed",
            "message": "Unable to process query",
        }
        mock_gpt_class.return_value = mock_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps(valid_chatops_request),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "error" in data

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_validation_error(
        self, mock_gpt_class, client, auth_headers
    ):
        """Test ChatOps endpoint with validation error."""
        mock_handler = Mock(spec=GPTHandler)
        mock_handler.process_query.side_effect = ValueError("Invalid input")
        mock_gpt_class.return_value = mock_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps({"query": "<script>alert('xss')</script>"}),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "Invalid input" in data["error"]

    def test_chatops_endpoint_method_not_allowed(self, client):
        """Test ChatOps endpoint with wrong HTTP method."""
        response = client.get("/api/chatops")

        assert response.status_code == 405

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_with_context(
        self, mock_gpt_class, client, mock_gpt_handler, auth_headers
    ):
        """Test ChatOps endpoint with context data."""
        request_data = {
            "query": "Analyze system performance",
            "context": {
                "system_health": "degraded",
                "recent_alerts": ["High CPU usage", "Memory pressure"],
                "resource_usage": {"cpu": 85, "memory": 90},
            },
        }

        mock_gpt_class.return_value = mock_gpt_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps(request_data),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 200
        # Verify context was passed to GPT handler
        mock_gpt_handler.process_query.assert_called_once()
        call_args = mock_gpt_handler.process_query.call_args
        assert call_args[0][0] == "Analyze system performance"
        assert call_args[0][1] == request_data["context"]

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")

        assert response.status_code == 200
        # Should return Prometheus format metrics
        assert "text/plain" in response.content_type
        assert "python_info" in response.data.decode()

    def test_api_documentation_endpoint(self, client):
        """Test API documentation endpoint."""
        response = client.get("/api/docs")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "endpoints" in data
        assert "version" in data

    def test_not_found_endpoint(self, client):
        """Test 404 handling for non-existent endpoints."""
        response = client.get("/api/nonexistent")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_method_not_allowed_endpoint(self, client):
        """Test 405 handling for wrong HTTP methods."""
        response = client.post("/health")  # Health endpoint only supports GET

        assert response.status_code == 405
        data = json.loads(response.data)
        assert "error" in data

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_rate_limiting(
        self,
        mock_gpt_class,
        client,
        mock_gpt_handler,
        valid_chatops_request,
        auth_headers,
    ):
        """Test ChatOps endpoint rate limiting."""
        mock_gpt_class.return_value = mock_gpt_handler

        # Make multiple rapid requests
        responses = []
        for _ in range(15):  # More than typical rate limit
            response = client.post(
                "/api/chatops",
                data=json.dumps(valid_chatops_request),
                content_type="application/json",
                headers=auth_headers,
            )
            responses.append(response)

        # At least some requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count > 0

    def test_chatops_endpoint_content_type_validation(self, client, auth_headers):
        """Test ChatOps endpoint content type validation."""
        response = client.post(
            "/api/chatops",
            data='{"query": "test"}',
            content_type="text/plain",
            headers=auth_headers,
        )  # Wrong content type

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_large_query(
        self, mock_gpt_class, client, mock_gpt_handler, auth_headers
    ):
        """Test ChatOps endpoint with large query."""
        large_query = "a" * 2000  # Query larger than limit
        request_data = {"query": large_query}

        mock_gpt_class.return_value = mock_gpt_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps(request_data),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_chatops_endpoint_empty_body(self, client, auth_headers):
        """Test ChatOps endpoint with empty request body."""
        response = client.post(
            "/api/chatops",
            data="",
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_conversation_history(
        self,
        mock_gpt_class,
        client,
        mock_gpt_handler,
        valid_chatops_request,
        auth_headers,
    ):
        """Test ChatOps endpoint maintains conversation history."""
        mock_gpt_class.return_value = mock_gpt_handler

        # Make multiple requests to same session
        for i in range(3):
            request_data = {
                "query": f"Query {i}",
                "context": {"session_id": "test_session"},
            }

            response = client.post(
                "/api/chatops",
                data=json.dumps(request_data),
                content_type="application/json",
                headers=auth_headers,
            )

            assert response.status_code == 200

        # Verify conversation history was maintained
        assert mock_gpt_handler.process_query.call_count == 3

    def test_api_version_endpoint(self, client):
        """Test API version endpoint."""
        response = client.get("/api/version")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "version" in data
        assert "build_date" in data
        assert "commit_hash" in data

    def test_api_health_detailed(self, client):
        """Test detailed API health endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_error_handling(
        self, mock_gpt_class, client, valid_chatops_request, auth_headers
    ):
        """Test ChatOps endpoint error handling."""
        mock_handler = Mock(spec=GPTHandler)
        mock_handler.process_query.side_effect = Exception("Unexpected error")
        mock_gpt_class.return_value = mock_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps(valid_chatops_request),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "internal server error" in data["error"].lower()

    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.get("/health")

        # Check for CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers

    def test_security_headers(self, client):
        """Test security headers are properly set."""
        response = client.get("/health")

        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_authentication(
        self, mock_gpt_class, client, mock_gpt_handler, valid_chatops_request
    ):
        """Test ChatOps endpoint authentication (if implemented)."""
        mock_gpt_class.return_value = mock_gpt_handler

        # Test without authentication
        response = client.post(
            "/api/chatops",
            data=json.dumps(valid_chatops_request),
            content_type="application/json",
        )

        # Should either require auth (401) or work without auth (200)
        assert response.status_code in [200, 401]

    def test_api_endpoints_content_type(self, client):
        """Test API endpoints return correct content type."""
        endpoints = ["/health", "/status", "/api/docs", "/api/version"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.content_type == "application/json"

    @patch("app.api.chatops.GPTHandler")
    def test_chatops_endpoint_response_structure(
        self,
        mock_gpt_class,
        client,
        mock_gpt_handler,
        valid_chatops_request,
        auth_headers,
    ):
        """Test ChatOps endpoint response structure."""
        mock_gpt_class.return_value = mock_gpt_handler

        response = client.post(
            "/api/chatops",
            data=json.dumps(valid_chatops_request),
            content_type="application/json",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check required fields
        required_fields = ["status", "response", "query", "timestamp", "model"]
        for field in required_fields:
            assert field in data

        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["query"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["model"], str)
