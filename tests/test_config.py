"""
Tests for configuration module
Phase 1: Basic configuration tests
"""

import pytest
from app.config import Config, DevelopmentConfig, ProductionConfig, get_config


class TestConfig:
    """Test configuration classes."""

    def test_base_config(self):
        """Test base configuration values."""
        config = Config()
        assert config.APP_NAME == "Smart CloudOps AI"
        assert config.VERSION == "0.1.0"
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
        
        assert isinstance(dev_config, DevelopmentConfig)
        assert isinstance(prod_config, ProductionConfig)
        assert isinstance(default_config, DevelopmentConfig)

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        env_config = Config.from_env()
        assert isinstance(env_config, dict)
        assert "debug" in env_config
        assert "metrics_port" in env_config