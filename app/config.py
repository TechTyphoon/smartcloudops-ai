"""Configuration module for Smart CloudOps AI Phase 2: ChatOps configuration setup."""

import os
from pathlib import Path
from typing import Any, Dict, Optional


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


class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors."""
    pass


class Config:
    """Base configuration class with validation."""

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
    MAX_ACTIONS_PER_HOUR: int = 10
    COOLDOWN_MINUTES: int = 5
    REMEDIATION_TAG_KEY: str = "Name"
    REMEDIATION_TAG_VALUE: str = "smartcloudops-ai-application"
    SSM_SERVICE_NAME: str = "smartcloudops-app"

    @classmethod
    def validate_config(cls, config_dict: Dict[str, Any]) -> None:
        """Validate configuration values."""
        errors = []

        # Validate AI provider
        if config_dict.get("ai_provider") not in ["auto", "openai", "gemini"]:
            errors.append("AI_PROVIDER must be 'auto', 'openai', or 'gemini'")

        # Validate OpenAI configuration
        if config_dict.get("ai_provider") == "openai" and not config_dict.get("openai_api_key"):
            errors.append("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")

        # Validate Gemini configuration
        if config_dict.get("ai_provider") == "gemini" and not config_dict.get("gemini_api_key"):
            errors.append("GEMINI_API_KEY is required when AI_PROVIDER is 'gemini'")

        # Validate numeric values
        if not isinstance(config_dict.get("openai_max_tokens", 500), int) or config_dict.get("openai_max_tokens", 500) <= 0:
            errors.append("OPENAI_MAX_TOKENS must be a positive integer")

        if not isinstance(config_dict.get("gemini_max_tokens", 500), int) or config_dict.get("gemini_max_tokens", 500) <= 0:
            errors.append("GEMINI_MAX_TOKENS must be a positive integer")

        if not isinstance(config_dict.get("openai_temperature", 0.3), (int, float)) or not 0 <= config_dict.get("openai_temperature", 0.3) <= 2:
            errors.append("OPENAI_TEMPERATURE must be between 0 and 2")

        if not isinstance(config_dict.get("gemini_temperature", 0.3), (int, float)) or not 0 <= config_dict.get("gemini_temperature", 0.3) <= 2:
            errors.append("GEMINI_TEMPERATURE must be between 0 and 2")

        # Validate remediation configuration
        if not isinstance(config_dict.get("max_actions_per_hour", 10), int) or config_dict.get("max_actions_per_hour", 10) <= 0:
            errors.append("MAX_ACTIONS_PER_HOUR must be a positive integer")

        if not isinstance(config_dict.get("cooldown_minutes", 5), int) or config_dict.get("cooldown_minutes", 5) < 0:
            errors.append("COOLDOWN_MINUTES must be a non-negative integer")

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config_dict.get("log_level", "INFO").upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")

        if errors:
            raise ConfigValidationError(f"Configuration validation failed: {'; '.join(errors)}")

    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables with validation."""
        config_dict = {
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
            "require_approval": os.getenv("REQUIRE_APPROVAL", "false").lower() == "true",
            "max_actions_per_hour": int(os.getenv("MAX_ACTIONS_PER_HOUR", "10")),
            "cooldown_minutes": int(os.getenv("COOLDOWN_MINUTES", "5")),
            "remediation_tag_key": os.getenv("REMEDIATION_TAG_KEY", "Name"),
            "remediation_tag_value": os.getenv("REMEDIATION_TAG_VALUE", "smartcloudops-ai-application"),
            "ssm_service_name": os.getenv("SSM_SERVICE_NAME", "smartcloudops-app"),
        }

        # Validate configuration
        cls.validate_config(config_dict)
        return config_dict

    @classmethod
    def get_required_env_vars(cls) -> Dict[str, str]:
        """Get required environment variables for the current configuration."""
        config_dict = cls.from_env()
        required_vars = {}

        if config_dict.get("ai_provider") == "openai":
            required_vars["OPENAI_API_KEY"] = "Required for OpenAI integration"
        elif config_dict.get("ai_provider") == "gemini":
            required_vars["GEMINI_API_KEY"] = "Required for Gemini integration"

        return required_vars

    @classmethod
    def check_missing_env_vars(cls) -> Dict[str, str]:
        """Check for missing required environment variables."""
        required_vars = cls.get_required_env_vars()
        missing_vars = {}

        for var_name, description in required_vars.items():
            if not os.getenv(var_name):
                missing_vars[var_name] = description

        return missing_vars


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False

    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load production configuration with additional validation."""
        config_dict = super().from_env()
        
        # Additional production-specific validation
        if config_dict.get("debug", False):
            raise ConfigValidationError("DEBUG must be False in production")
        
        if config_dict.get("ai_provider") == "auto":
            raise ConfigValidationError("AI_PROVIDER must be explicitly set in production")
        
        return config_dict


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(env: str = "default") -> Config:
    """Get configuration based on environment with validation."""
    try:
        config_class = config_map.get(env, DevelopmentConfig)
        return config_class
    except Exception as e:
        raise ConfigValidationError(f"Failed to load configuration for environment '{env}': {str(e)}")


def validate_current_config() -> Dict[str, Any]:
    """Validate the current configuration and return status."""
    try:
        config_dict = Config.from_env()
        missing_vars = Config.check_missing_env_vars()
        
        return {
            "valid": True,
            "config": config_dict,
            "missing_vars": missing_vars,
            "warnings": [] if not missing_vars else [f"Missing: {', '.join(missing_vars.keys())}"]
        }
    except ConfigValidationError as e:
        return {
            "valid": False,
            "error": str(e),
            "config": {},
            "missing_vars": {},
            "warnings": []
        }
