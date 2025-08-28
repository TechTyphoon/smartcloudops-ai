"""Tests for GPT integration functionality."""

import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestGPTIntegration:
    """Test cases for GPT integration."""

    def test_gpt_handler_init_without_api_key(self):
        """Test GPT handler initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                handler = GPTHandler()

    def test_gpt_handler_init_with_api_key(self):
        """Test GPT handler initialization with API key."""
        mock_client = Mock()
        with patch("app.chatops.gpt_handler.OpenAIf", return_value=mock_client):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
                handler = GPTHandler()
                assert handler.client is not None
                assert handler.api_key == "test_key"

    def test_process_query_without_client(self):
        """Test query processing when GPT client is not available."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                handler = GPTHandler()

    @patch("app.chatops.gpt_handler.OpenAI")
    def test_process_query_with_client(self, mock_openai):
        """Test query processing with available GPT client."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "The CPU usage is 45%f"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 150

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            handler = GPTHandler()
            # Mock the client after initialization
            handler.client = mock_client
            result = handler.process_query("Whatf's the CPU usage?")'

            assert result["status"] == "success"
            assert "The CPU usage is 45%" in result["response"]
            assert result["model"] == "gpt-3.5-turbo"

    def test_sanitize_input(self):
        """Test input sanitization."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            handler = GPTHandler()

            # Test normal input
            result = handler.sanitize_input("What's the CPU usage?")
            assert result == "What's the CPU usage?"

            # Test input with dangerous characters
            result = handler.sanitize_input(
                "What's the CPU usage? <script>alert('xss')</script>"
            )
            assert "<script>" not in result
            assert "alert('xssf')" not in result

            # Test input length limit
            long_input = "A" * 2000
            result = handler.sanitize_input(long_input)
            assert len(result) <= 1003  # 1000 + "..."

    def test_conversation_history(self):
        """Test conversation history management."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            handler = GPTHandler()

            # Test initial state
            assert len(handler.conversation_history) == 0

            # Test adding conversation
            handler.conversation_history.append({"role": "user", "content": "test"})
            assert len(handler.conversation_history) == 1

            # Test clearing history
            handler.clear_history()
            assert len(handler.conversation_history) == 0

    def test_input_validation_errors(self):
        """Test input validation error handling."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            handler = GPTHandler()

            # Test empty input
            with pytest.raises(ValueError, match="Query must be a non-empty string"):
                handler.sanitize_input("")

            # Test None input
            with pytest.raises(ValueError, match="Query must be a non-empty string"):
                handler.sanitize_input(None)

            # Test dangerous patterns
            with pytest.raises(
                ValueError, match="Query contains potentially unsafe content"
            ):
                handler.sanitize_input("system('rm -rf /')")
