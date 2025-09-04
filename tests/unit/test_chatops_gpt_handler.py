"""
Unit tests for ChatOps GPT Handler
Comprehensive test coverage for GPT integration and security features
"""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from app.chatops.gpt_handler import GPTHandler


class TestGPTHandler:
    """Test suite for GPTHandler class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response from GPT"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 150
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    @pytest.fixture
    def gpt_handler(self, mock_openai_client):
        """Create GPTHandler instance with mocked dependencies."""
        with patch("app.chatops.gpt_handler.OpenAI", return_value=mock_openai_client):
            handler = GPTHandler(api_key="test-api-key")
            handler.client = mock_openai_client
            return handler

    @pytest.fixture
    def valid_context(self) -> Dict[str, Any]:
        """Valid context data for testing."""
        return {
            "system_health": "healthy",
            "prometheus_metrics": "all systems operational",
            "recent_alerts": "no active alerts",
            "resource_usage": "CPU: 45%, Memory: 60%",
        }

    def test_init_with_api_key(self, mock_openai_client):
        """Test GPTHandler initialization with valid API key."""
        with patch("app.chatops.gpt_handler.OpenAI", return_value=mock_openai_client):
            handler = GPTHandler(api_key="test-api-key")

            assert handler.api_key == "test-api-key"
            assert handler.client == mock_openai_client
            assert handler.conversation_history == []
            assert "Senior DevOps Engineer" in handler.system_prompt

    def test_init_without_api_key_raises_error(self):
        """Test GPTHandler initialization without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                GPTHandler()

    def test_init_with_env_api_key(self, mock_openai_client):
        """Test GPTHandler initialization with environment API key."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-api-key"}):
            with patch(
                "app.chatops.gpt_handler.OpenAI", return_value=mock_openai_client
            ):
                handler = GPTHandler()

                assert handler.api_key == "env-api-key"
                assert handler.client == mock_openai_client

    def test_init_openai_client_error(self):
        """Test GPTHandler initialization when OpenAI client fails."""
        with patch(
            "app.chatops.gpt_handler.OpenAI", side_effect=Exception("Connection failed")
        ):
            with pytest.raises(ValueError, match="Failed to initialize OpenAI client"):
                GPTHandler(api_key="test-api-key")

    def test_get_system_prompt(self, gpt_handler):
        """Test system prompt generation."""
        prompt = gpt_handler._get_system_prompt()

        assert "Senior DevOps Engineer" in prompt
        assert "Infrastructure Analysis" in prompt
        assert "Troubleshooting" in prompt
        assert "Best Practices" in prompt
        assert "Automation" in prompt
        assert "Monitoring" in prompt

    @pytest.mark.parametrize(
        "query,expected",
        [
            ("What is the system status?", "What is the system status?"),
            ("  Check CPU usage  ", "Check CPU usage"),
            ("Normal query", "Normal query"),
        ],
    )
    def test_sanitize_input_valid_queries(self, gpt_handler, query, expected):
        """Test input sanitization with valid queries."""
        result = gpt_handler.sanitize_input(query)
        assert result == expected

    @pytest.mark.parametrize(
        "query,error_type,error_message",
        [
            (None, ValueError, "Query must be a non-empty string"),
            ("", ValueError, "Query must be a non-empty string"),
            (123, ValueError, "Query must be a non-empty string"),
            ("a" * 1001, None, None),  # Should truncate instead of error
        ],
    )
    def test_sanitize_input_invalid_inputs(
        self, gpt_handler, query, error_type, error_message
    ):
        """Test input sanitization with invalid inputs."""
        if error_type is None:
            # For long inputs, should truncate instead of raising error
            result = gpt_handler.sanitize_input(query)
            assert len(result) <= 1003  # 1000 + "..."
        else:
            with pytest.raises(error_type, match=error_message):
                gpt_handler.sanitize_input(query)

    @pytest.mark.parametrize(
        "malicious_input",
        [
            "<script>alert('xss')</script>",
            "SELECT * FROM users WHERE id = 1",
            "system('rm -rf /')",
            "import os; os.system('ls')",
            "javascript:alert('xss')",
            "../../../etc/passwd",
            "alert('xss')",
            "document.cookie",
            "onload=alert('xss')",
        ],
    )
    def test_sanitize_input_malicious_content(self, gpt_handler, malicious_input):
        """Test input sanitization with malicious content."""
        with pytest.raises(ValueError, match="contains potentially unsafe"):
            gpt_handler.sanitize_input(malicious_input)

    def test_add_context_with_valid_data(self, gpt_handler, valid_context):
        """Test context addition with valid data."""
        context_prompt = gpt_handler.add_context(valid_context)

        assert "Current System Context" in context_prompt
        assert "System Health: healthy" in context_prompt
        assert "Prometheus Status: all systems operational" in context_prompt
        assert "Recent Alerts: no active alerts" in context_prompt
        assert "Resource Usage: CPU: 45%, Memory: 60%" in context_prompt

    def test_add_context_with_empty_context(self, gpt_handler):
        """Test context addition with empty context."""
        context_prompt = gpt_handler.add_context({})

        assert "Current System Context" in context_prompt
        assert "System Health:" not in context_prompt

    def test_add_context_with_none_context(self, gpt_handler):
        """Test context addition with None context."""
        context_prompt = gpt_handler.add_context(None)

        assert "Current System Context" in context_prompt

    def test_process_query_success(self, gpt_handler, valid_context):
        """Test successful query processing."""
        query = "What is the current system status?"

        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "success"
        assert result["response"] == "Test response from GPT"
        assert result["query"] == query
        assert "timestamp" in result
        assert result["model"] == "gpt-3.5-turbo"
        assert result["tokens_used"] == 150

    def test_process_query_without_client(self, gpt_handler, valid_context):
        """Test query processing when client is not available."""
        gpt_handler.client = None
        query = "What is the current system status?"

        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "error"
        assert "GPT functionality not available" in result["error"]
        assert "OPENAI_API_KEY" in result["message"]

    def test_process_query_invalid_input(self, gpt_handler, valid_context):
        """Test query processing with invalid input."""
        query = "<script>alert('xss')</script>"

        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "error"
        assert result["error"] == "Invalid input"
        assert "contains potentially unsafe" in result["message"]

    def test_process_query_api_error(self, gpt_handler, valid_context):
        """Test query processing when API call fails."""
        gpt_handler.client.chat.completions.create.side_effect = Exception("API Error")
        query = "What is the current system status?"

        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "error"
        assert result["error"] == "Processing failed"
        assert "Unable to process query" in result["message"]

    def test_process_query_conversation_history(self, gpt_handler, valid_context):
        """Test query processing with conversation history."""
        # Add some conversation history
        gpt_handler.conversation_history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]

        query = "What is the current system status?"
        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "success"
        # Verify history was included in the API call
        call_args = gpt_handler.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) > 2  # System prompt + history + current query

    def test_process_query_history_limit(self, gpt_handler, valid_context):
        """Test conversation history limit enforcement."""
        # Add more than 20 messages to history
        for i in range(25):
            gpt_handler.conversation_history.append(
                {"role": "user", "content": f"Question {i}"}
            )
            gpt_handler.conversation_history.append(
                {"role": "assistant", "content": f"Answer {i}"}
            )

        query = "What is the current system status?"
        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "success"
        # History should be limited to 20 messages
        assert len(gpt_handler.conversation_history) <= 20

    def test_get_conversation_history(self, gpt_handler):
        """Test conversation history retrieval."""
        # Add some history
        gpt_handler.conversation_history = [
            {"role": "user", "content": "Test question"},
            {"role": "assistant", "content": "Test answer"},
        ]

        history = gpt_handler.get_conversation_history()

        assert history == gpt_handler.conversation_history
        # Should return a copy, not the original
        assert history is not gpt_handler.conversation_history

    def test_clear_history(self, gpt_handler):
        """Test conversation history clearing."""
        # Add some history
        gpt_handler.conversation_history = [
            {"role": "user", "content": "Test question"},
            {"role": "assistant", "content": "Test answer"},
        ]

        result = gpt_handler.clear_history()

        assert result is True
        assert gpt_handler.conversation_history == []

    def test_process_query_response_sanitization(self, gpt_handler, valid_context):
        """Test that GPT responses are sanitized."""
        # Mock a response with potentially dangerous content
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "<script>alert('xss')</script>Test response"
        )
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 150
        gpt_handler.client.chat.completions.create.return_value = mock_response

        query = "What is the current system status?"
        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "success"
        # Response should be sanitized (script tags removed)
        assert "<script>" not in result["response"]
        assert "Test response" in result["response"]

    @pytest.mark.parametrize(
        "context_key,context_value",
        [
            ("system_health", "healthy"),
            ("prometheus_metrics", "all operational"),
            ("recent_alerts", "no alerts"),
            ("resource_usage", "CPU: 50%"),
        ],
    )
    def test_add_context_individual_fields(
        self, gpt_handler, context_key, context_value
    ):
        """Test context addition with individual fields."""
        context = {context_key: context_value}
        context_prompt = gpt_handler.add_context(context)

        assert context_value in context_prompt

    def test_sanitize_input_html_encoding(self, gpt_handler):
        """Test that input is properly HTML encoded."""
        query = "Test & < > \" ' query"
        result = gpt_handler.sanitize_input(query)

        # Should be HTML encoded
        assert "&amp;" in result or "&lt;" in result or "&gt;" in result

    def test_process_query_timeout_handling(self, gpt_handler, valid_context):
        """Test query processing timeout handling."""
        gpt_handler.client.chat.completions.create.side_effect = Exception("timeout")
        query = "What is the current system status?"

        result = gpt_handler.process_query(query, valid_context)

        assert result["status"] == "error"
        assert result["error"] == "Processing failed"

    def test_system_prompt_content(self, gpt_handler):
        """Test system prompt contains all required sections."""
        prompt = gpt_handler._get_system_prompt()

        required_sections = [
            "Infrastructure Analysis",
            "Troubleshooting",
            "Best Practices",
            "Automation",
            "Monitoring",
            "Response Guidelines",
            "Current System Context",
        ]

        for section in required_sections:
            assert section in prompt

    def test_conversation_history_management(self, gpt_handler, valid_context):
        """Test conversation history management."""
        queries = ["Query 1", "Query 2", "Query 3"]

        for query in queries:
            gpt_handler.process_query(query, valid_context)

        # Should have 6 messages (3 user + 3 assistant)
        assert len(gpt_handler.conversation_history) == 6

        # Check alternating user/assistant pattern
        for i in range(0, len(gpt_handler.conversation_history), 2):
            assert gpt_handler.conversation_history[i]["role"] == "user"
            if i + 1 < len(gpt_handler.conversation_history):
                assert gpt_handler.conversation_history[i + 1]["role"] == "assistant"
