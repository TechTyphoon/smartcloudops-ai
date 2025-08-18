"""
Tests for ChatOps functionality.
"""

import json
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.chatops.ai_handler import FlexibleAIHandler
from app.chatops.gpt_handler import GPTHandler
from app.chatops.utils import (
    LogRetriever,
    SystemContextGatherer,
    format_response,
    validate_query_params,
)
from app.main import app


class TestGPTHandler:
    """Test cases for GPT Handler."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch("app.chatops.gpt_handler.OpenAI") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def gpt_handler(self, mock_openai_client):
        """Create GPT handler with mocked client."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            return GPTHandler()

    def test_gpt_handler_initialization(self, mock_openai_client):
        """Test GPT handler initialization."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            handler = GPTHandler()
            assert handler.api_key == "test-key"
            assert handler.conversation_history == []

    def test_gpt_handler_missing_api_key(self):
        """Test GPT handler initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                GPTHandler()

    def test_sanitize_input_valid(self, gpt_handler):
        """Test input sanitization with valid input."""
        result = gpt_handler.sanitize_input("What's the CPU usage?")
        assert result == "What's the CPU usage?"

    def test_sanitize_input_empty(self, gpt_handler):
        """Test input sanitization with empty input."""
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            gpt_handler.sanitize_input("")

    def test_sanitize_input_too_long(self, gpt_handler):
        """Test input sanitization with long input."""
        long_input = "a" * 1500
        result = gpt_handler.sanitize_input(long_input)
        assert len(result) <= 1003  # 1000 + "..."

    def test_sanitize_input_dangerous_patterns(self, gpt_handler):
        """Test input sanitization with dangerous patterns."""
        # NOTE: These are intentionally dangerous patterns for testing input sanitization
        # They are safe in this test context as they are never executed
        dangerous_inputs = [
            "system('rm -rf /')",
            "eval('dangerous code')",
            "exec('malicious')",
            "import os",
            "__import__('os')",
        ]

        for dangerous_input in dangerous_inputs:
            with pytest.raises(
                ValueError, match="Query contains potentially unsafe content"
            ):
                gpt_handler.sanitize_input(dangerous_input)

    def test_process_query_success(self, gpt_handler, mock_openai_client):
        """Test successful query processing."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "CPU usage is 45%"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 50
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Create handler with API key and mock the client
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch(
                "app.chatops.gpt_handler.OpenAI", return_value=mock_openai_client
            ):
                handler = GPTHandler(api_key="test-key")
                # Mock the client after initialization
                handler.client = mock_openai_client
                result = handler.process_query("What's the CPU usage?")

                assert result["status"] == "success"
                assert "CPU usage is 45%" in result["response"]
                assert result["model"] == "gpt-3.5-turbo"

    def test_process_query_validation_error(self, gpt_handler):
        """Test query processing with validation error."""
        result = gpt_handler.process_query("")

        assert result["status"] == "error"
        assert result["error"] == "Invalid input"

    def test_get_conversation_history(self, gpt_handler):
        """Test conversation history retrieval."""
        # Add some history
        gpt_handler.conversation_history = [
            {"role": "user", "content": "test query"},
            {"role": "assistant", "content": "test response"},
        ]

        history = gpt_handler.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_clear_history(self, gpt_handler):
        """Test conversation history clearing."""
        gpt_handler.conversation_history = [{"role": "user", "content": "test"}]
        result = gpt_handler.clear_history()

        assert result is True
        assert len(gpt_handler.conversation_history) == 0


class TestSystemContextGatherer:
    """Test cases for System Context Gatherer."""

    @pytest.fixture
    def context_gatherer(self):
        """Create context gatherer."""
        return SystemContextGatherer()

    def test_get_system_health_flask_healthy(self, context_gatherer):
        """Test system health with healthy Flask app."""
        health = context_gatherer.get_system_health()

        # Check that we get a system context structure
        assert "system_health" in health or "components" in health
        assert isinstance(health, dict)

    def test_get_context_for_query(self, context_gatherer):
        """Test context gathering for specific query."""
        context = context_gatherer.get_context_for_query("How is the system?")

        assert "query_analysis" in context
        assert "relevant_context" in context
        assert "system_summary" in context


class TestLogRetriever:
    """Test cases for Log Retriever."""

    @pytest.fixture
    def log_retriever(self):
        """Create log retriever."""
        return LogRetriever()

    def test_create_sample_log(self, log_retriever):
        """Test sample log creation."""
        log_entry = log_retriever.create_sample_log()

        assert log_entry["message"] == "Sample log entry for testing"
        assert log_entry["level"] == "INFO"
        assert log_entry["source"] == "chatops"

    def test_get_recent_logs_empty(self, log_retriever):
        """Test getting logs from empty directory."""
        logs = log_retriever.get_recent_logs()
        assert isinstance(logs, list)

    def test_get_recent_logs_with_data(self, log_retriever):
        """Test getting logs with data."""
        logs = log_retriever.get_recent_logs()
        assert isinstance(logs, list)
        # Should return sample logs in development
        assert len(logs) > 0


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_validate_query_params_valid(self):
        """Test parameter validation with valid parameters."""
        # Test valid hours
        is_valid, message = validate_query_params(hours=12)
        assert is_valid is True
        assert message == ""

        # Test valid level
        is_valid, message = validate_query_params(level="INFO")
        assert is_valid is True
        assert message == ""

    def test_validate_query_params_invalid_hours(self):
        """Test parameter validation with invalid hours."""
        is_valid, message = validate_query_params(hours="invalid")
        assert is_valid is False
        assert "integer" in message

    def test_validate_query_params_hours_out_of_range(self):
        """Test parameter validation with hours out of range."""
        is_valid, message = validate_query_params(hours=200)  # More than 168 (1 week)
        assert is_valid is False
        assert "between 1 and 168" in message

    def test_validate_query_params_invalid_level(self):
        """Test parameter validation with invalid level."""
        is_valid, message = validate_query_params(level="invalid_level")
        assert is_valid is False
        assert "must be one of" in message

    def test_format_response_success(self):
        """Test response formatting."""
        result = format_response("success", {"test": "data"}, "Test message")

        assert result["status"] == "success"
        assert result["data"] == {"test": "data"}
        assert result["message"] == "Test message"
        assert "timestamp" in result

    def test_format_response_error(self):
        """Test error response formatting."""
        result = format_response("error", error="test error", message="Error occurred")

        assert result["status"] == "error"
        assert result["error"] == "test error"
        assert result["message"] == "Error occurred"


class TestChatOpsIntegration:
    """Test ChatOps integration with Flask app."""

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

    def test_query_endpoint_success(self, client, mock_ai_handler):
        """Test successful query endpoint."""
        with patch("app.main.ai_handler", mock_ai_handler):
            response = client.post("/query", json={"query": "test query"})
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            assert "data" in data

    def test_query_endpoint_missing_query(self, client):
        """Test query endpoint with missing query."""
        response = client.post("/query", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert "error" in data

    def test_logs_endpoint(self, client):
        """Test logs endpoint."""
        response = client.get("/logs")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "data" in data

    def test_logs_endpoint_with_filters(self, client):
        """Test logs endpoint with filters."""
        response = client.get("/logs?hours=1&level=INFO")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "data" in data

    def test_chat_history_endpoint(self, client):
        """Test chat history endpoint."""
        response = client.get("/chatops/history")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == "success"
        assert data["status"]["count"] >= 0
        assert "history" in data["status"]

    def test_clear_history_endpoint(self, client):
        """Test clear history endpoint."""
        response = client.post("/chatops/clear")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_system_summary_endpoint(self, client):
        """Test system summary endpoint."""
        response = client.get("/chatops/system-summary")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "summary" in data["data"]

    def test_analyze_endpoint(self, client):
        """Test query analysis endpoint."""
        response = client.post("/chatops/analyze", json={"query": "test query"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "intent" in data["data"]
