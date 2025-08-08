"""Configuration module for Smart CloudOps AI Phase 2: ChatOps configuration setup."""

import os
from typing import Dict, Any
from pathlib import Path


# Load .env file if it exists
def load_dotenv():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


# Load .env file
load_dotenv()


class Config:
    """Base configuration class."""

    # Basic app configuration
    APP_NAME: str = "Smart CloudOps AI"
    VERSION: str = "0.2.0"
    DEBUG: bool = False

    # Monitoring configuration (Phase 1)
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int = 9090

    # ChatOps configuration (Phase 2)
    AI_PROVIDER: str = "auto"  # "openai", "gemini", or "auto"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_MAX_TOKENS: int = 500
    GEMINI_TEMPERATURE: float = 0.3

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    # Remediation configuration (Phase 4)
    REQUIRE_APPROVAL: bool = False
    MAX_ACTIONS_PER_HOUR: int = 3
    COOLDOWN_MINUTES: int = 10
    REMEDIATION_TAG_KEY: str = "Name"
    REMEDIATION_TAG_VALUE: str = "smartcloudops-ai-application"
    SSM_SERVICE_NAME: str = "smartcloudops-app"

    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
            "ai_provider": os.getenv("AI_PROVIDER", "auto"),
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "openai_max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "500")),
            "openai_temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "gemini_model": os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            "gemini_max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "500")),
            "gemini_temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.3")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_dir": os.getenv("LOG_DIR", "logs"),
            # Phase 4 remediation config
            "require_approval": os.getenv("REQUIRE_APPROVAL", "false").lower()
            == "true",
            "max_actions_per_hour": int(os.getenv("MAX_ACTIONS_PER_HOUR", "3")),
            "cooldown_minutes": int(os.getenv("COOLDOWN_MINUTES", "10")),
            "remediation_tag_key": os.getenv("REMEDIATION_TAG_KEY", "Name"),
            "remediation_tag_value": os.getenv(
                "REMEDIATION_TAG_VALUE", "smartcloudops-ai-application"
            ),
            "ssm_service_name": os.getenv("SSM_SERVICE_NAME", "smartcloudops-app"),
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
