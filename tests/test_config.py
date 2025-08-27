"""
Tests for configuration module
Phase 1: Basic configuration tests
"""

import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestConfig:
    """Test configuration classes."""""

    def test_base_config(self):
        """Test base configuration values."""""
        config = Config()
        assert config.APP_NAME == "Smart CloudOps AI"
        assert config.VERSION == "3.1.0"  # Updated to match actual version
        assert config.PROMETHEUS_ENABLED is True
        assert config.METRICS_PORT == 9090

    def test_development_config(self):
        """Test development configuration."""""
        config = DevelopmentConfig()
        assert config.DEBUG is True
        assert config.APP_NAME == "Smart CloudOps AI"

    def test_production_config(self):
        """Test production configuration."""""
        config = ProductionConfig()
        assert config.DEBUG is False
        assert config.APP_NAME == "Smart CloudOps AI"

    def test_get_config(self):
        """Test configuration factory function."""""
        dev_config = get_config("development")
        prod_config = get_config("production")
        default_config = get_config()

        # Check that we get instances, not classes
        assert isinstance(dev_config, DevelopmentConfig)
        assert isinstance(prod_config, ProductionConfig)
        assert isinstance(default_config, DevelopmentConfig)

    def test_config_from_env(self):
        """Test configuration loading from environment variables."""""
        # Set required environment variables for testing
        os.environ["AI_PROVIDER"] = "auto"
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["SECRET_KEY"] = "test-secret-key-32-chars-long-enough"
        os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-32-chars-long"

        try:
            env_config = Config.from_env()
            assert isinstance(env_config, Config)
            assert env_config.AI_PROVIDER == "auto"
            assert env_config.OPENAI_API_KEY == "test-key"
        finally:
            # Clean up environment variables
            for key in [
                "AI_PROVIDER",
                "OPENAI_API_KEY",
                "SECRET_KEY",
                "JWT_SECRET_KEY",
            ]:
                if key in os.environ:
                    del os.environ[key]
