"""
Tests for ChatOps functionality.
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.chatops.gpt_handler import GPTHandler
from app.chatops.utils import SystemContextGatherer, LogRetriever, validate_query_params, format_response


class TestGPTHandler:
    """Test cases for GPT Handler."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch('app.chatops.gpt_handler.OpenAI') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def gpt_handler(self, mock_openai_client):
        """Create GPT handler with mocked client."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            return GPTHandler()

    def test_gpt_handler_initialization(self, mock_openai_client):
        """Test GPT handler initialization."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            handler = GPTHandler()
            assert handler.api_key == 'test-key'
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
        dangerous_inputs = [
            "system('rm -rf /')",
            "eval('dangerous code')",
            "exec('malicious')",
            "import os",
            "__import__('os')"
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(ValueError, match="Query contains potentially unsafe content"):
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
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('app.chatops.gpt_handler.OpenAI', return_value=mock_openai_client):
                handler = GPTHandler(api_key='test-key')
                # Mock the client after initialization
                handler.client = mock_openai_client
                result = handler.process_query("What's the CPU usage?")
    
                assert result['status'] == 'success'
                assert 'CPU usage is 45%' in result['response']
                assert result['model'] == 'gpt-3.5-turbo'

    def test_process_query_validation_error(self, gpt_handler):
        """Test query processing with validation error."""
        result = gpt_handler.process_query("")
        
        assert result['status'] == 'error'
        assert result['error'] == 'Invalid input'

    def test_get_conversation_history(self, gpt_handler):
        """Test conversation history retrieval."""
        # Add some history
        gpt_handler.conversation_history = [
            {"role": "user", "content": "test query"},
            {"role": "assistant", "content": "test response"}
        ]
        
        history = gpt_handler.get_conversation_history()
        assert len(history) == 2
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'

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

    @patch('app.chatops.utils.requests.get')
    def test_get_system_health_flask_healthy(self, mock_get, context_gatherer):
        """Test system health with healthy Flask app."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response

        health = context_gatherer.get_system_health()
        
        assert 'flask_app' in health
        assert 'prometheus' in health
        assert health['flask_app']['status'] == 'healthy'

    @patch('app.chatops.utils.requests.get')
    def test_get_prometheus_metrics_success(self, mock_get, context_gatherer):
        """Test Prometheus metrics retrieval."""
        # Mock successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "result": [{"value": [1234567890, "45.5"]}]
            }
        }
        mock_get.return_value = mock_response

        metrics = context_gatherer.get_prometheus_metrics()
        
        assert metrics['status'] == 'success'
        assert 'metrics' in metrics
        assert 'timestamp' in metrics


class TestLogRetriever:
    """Test cases for Log Retriever."""

    @pytest.fixture
    def log_retriever(self, tmp_path):
        """Create log retriever with temporary directory."""
        return LogRetriever(str(tmp_path))

    def test_create_sample_log(self, log_retriever, tmp_path):
        """Test sample log creation."""
        log_entry = log_retriever.create_sample_log("Test message", "info", "test-service")
        
        assert log_entry['message'] == "Test message"
        assert log_entry['level'] == "INFO"
        assert log_entry['service'] == "test-service"
        
        # Check if log file was created
        log_file = tmp_path / "test-service.log"
        assert log_file.exists()

    def test_get_recent_logs_empty(self, log_retriever):
        """Test getting logs from empty directory."""
        logs = log_retriever.get_recent_logs()
        assert logs == []

    def test_get_recent_logs_with_data(self, log_retriever, tmp_path):
        """Test getting logs with data."""
        # Create a log file with sample data
        log_file = tmp_path / "test.log"
        from datetime import datetime, timedelta
        # Use a recent timestamp
        recent_time = datetime.now() - timedelta(hours=1)
        sample_log = {
            "timestamp": recent_time.isoformat(),
            "level": "INFO",
            "service": "test",
            "message": "Test log entry"
        }
        
        with open(log_file, 'w') as f:
            f.write(json.dumps(sample_log) + '\n')
        
        logs = log_retriever.get_recent_logs()
        assert len(logs) == 1
        assert logs[0]['message'] == "Test log entry"


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_validate_query_params_valid(self):
        """Test parameter validation with valid parameters."""
        params = {
            "hours": "12",
            "level": "error",
            "service": "flask"
        }
        
        result = validate_query_params(params)
        
        assert result['hours'] == 12
        assert result['level'] == 'error'
        assert result['service'] == 'flask'

    def test_validate_query_params_invalid_hours(self):
        """Test parameter validation with invalid hours."""
        params = {"hours": "invalid"}
        result = validate_query_params(params)
        assert result['hours'] == 24  # Default value

    def test_validate_query_params_hours_out_of_range(self):
        """Test parameter validation with hours out of range."""
        params = {"hours": "200"}  # More than 168 (1 week)
        result = validate_query_params(params)
        assert result['hours'] == 24  # Default value

    def test_validate_query_params_invalid_level(self):
        """Test parameter validation with invalid level."""
        params = {"level": "invalid_level"}
        result = validate_query_params(params)
        assert 'level' not in result

    def test_format_response_success(self):
        """Test response formatting."""
        data = {"test": "data"}
        result = format_response(data, "success", "Test message")
        
        assert result['status'] == 'success'
        assert result['data'] == data
        assert result['message'] == 'Test message'
        assert 'timestamp' in result

    def test_format_response_error(self):
        """Test error response formatting."""
        data = {"error": "test error"}
        result = format_response(data, "error", "Error occurred")
        
        assert result['status'] == 'error'
        assert result['data'] == data
        assert result['message'] == 'Error occurred'


class TestChatOpsIntegration:
    """Integration tests for ChatOps functionality."""

    @pytest.fixture
    def test_app(self):
        """Create test Flask app."""
        from app.main import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return test_app.test_client()

    def test_query_endpoint_success(self, client):
        """Test successful query endpoint."""
        # Mock the FlexibleAIHandler at the module level
        with patch('app.main.ai_handler') as mock_ai_handler:
            mock_ai_handler.process_query.return_value = {
                "status": "success",
                "response": "Test response",
                "query": "test query"
            }
            mock_ai_handler.get_provider_info.return_value = {
                "provider": "test",
                "model": "test-model"
            }
            
            response = client.post('/query', json={'query': 'test query'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert 'Test response' in data['data']['response']

    def test_query_endpoint_missing_query(self, client):
        """Test query endpoint with missing query parameter."""
        response = client.post('/query', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_logs_endpoint(self, client):
        """Test logs endpoint."""
        response = client.get('/logs')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data

    def test_logs_endpoint_with_filters(self, client):
        """Test logs endpoint with filters."""
        response = client.get('/logs?hours=12&level=error')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_chat_history_endpoint(self, client):
        """Test chat history endpoint."""
        response = client.get('/chatops/history')
        
        # Should work even without GPT handler
        assert response.status_code in [200, 503]

    def test_clear_history_endpoint(self, client):
        """Test clear history endpoint."""
        response = client.post('/chatops/clear')
        
        # Should work even without GPT handler
        assert response.status_code in [200, 503] 