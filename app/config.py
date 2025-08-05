"""Configuration module for Smart CloudOps AI Phase 1: Basic configuration setup."""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""

    # Basic app configuration
    APP_NAME: str = "Smart CloudOps AI"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Monitoring configuration (Phase 1)
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int = 9090

    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
        }


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(env: str = "default") -> Config:
    """Get configuration based on environment."""
    return config_map.get(env, DevelopmentConfig)
