"""
Tests for configuration module
Phase 1: Basic configuration tests
"""

import os
import sys

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import Config, DevelopmentConfig, ProductionConfig, get_config


class TestConfig:
    """Test configuration classes."""

    def test_base_config(self):
        """Test base configuration values."""
        config = Config()
        assert config.APP_NAME == "Smart CloudOps AI"
        assert config.VERSION == "0.2.0"
        assert config.PROMETHEUS_ENABLED is True
        assert config.METRICS_PORT == 9090

    def test_development_config(self):
        """Test development configuration."""
        config = DevelopmentConfig()
        assert config.DEBUG is True
        assert config.APP_NAME == "Smart CloudOps AI"

    def test_production_config(self):
        """Test production configuration."""
        config = ProductionConfig()
        assert config.DEBUG is False
        assert config.APP_NAME == "Smart CloudOps AI"

    def test_get_config(self):
        """Test configuration factory function."""
        dev_config = get_config("development")
        prod_config = get_config("production")
        default_config = get_config()

        assert dev_config == DevelopmentConfig
        assert prod_config == ProductionConfig
        assert default_config == DevelopmentConfig

    def test_config_from_env(self):
        """Test configuration loading from environment variables."""
        # Set required environment variables for testing
        os.environ["AI_PROVIDER"] = "auto"
        os.environ["OPENAI_API_KEY"] = "test-key"

        try:
            env_config = Config.from_env()
            assert isinstance(env_config, dict)
            assert "ai_provider" in env_config
            assert "openai_api_key" in env_config
        finally:
            # Clean up environment variables
            if "AI_PROVIDER" in os.environ:
                del os.environ["AI_PROVIDER"]
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
