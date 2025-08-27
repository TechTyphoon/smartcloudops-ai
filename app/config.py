"""
Configuration module for Smart CloudOps AI - Production Ready Configuration Management.
"""

import logging
import os
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_secret(key: str, default: str = "") -> str:
    """Get secret from environment variables with validation."""""
    return os.getenv(key, default)


def load_dotenv():
    """Load environment variables from .env file with security validation."""""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")

                        # Validate sensitive environment variables
                        if key in [
                            "JWT_SECRET_KEY",
                            "DATABASE_PASSWORD",
                            "REDIS_PASSWORD",
                            "OPENAI_API_KEY",
                        ]:
                            if len(value) < 16:
                                logger.warning(
                                    f"Warning: {key} in .env file is too short (line {line_num})"
                                )

                        os.environ[key] = value

        except Exception as e:
            logger.error(f"Error loading .env file: {e}")


# Load .env file
load_dotenv()


class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors."""""


class Config:
    """Base configuration class with comprehensive validation."""""

    # Basic app configuration
    APP_NAME: str = "Smart CloudOps AI"
    VERSION: str = "3.1.0"
    DEBUG: bool = False

    # Security configuration
    SECRET_KEY: str = get_secret("SECRET_KEY", "")
    JWT_SECRET_KEY: str = get_secret("JWT_SECRET_KEY", "")
    JWT_ACCESS_TOKEN_EXPIRY_HOURS: int = 24
    JWT_REFRESH_TOKEN_EXPIRY_DAYS: int = 7
    BCRYPT_COST_FACTOR: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # CORS configuration
    CORS_ORIGINS: List[str] = []
    CORS_SUPPORTS_CREDENTIALS: bool = True

    # Database configuration
    DATABASE_URL: str = get_secret("DATABASE_URL", "")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # Redis configuration
    REDIS_HOST: str = get_secret("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(get_secret("REDIS_PORT", "6379"))
    REDIS_DB: int = int(get_secret("REDIS_DB", "0"))
    REDIS_PASSWORD: str = get_secret("REDIS_PASSWORD", "")

    # Monitoring configuration
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int = 9090

    # AI/ML configuration
    AI_PROVIDER: str = "auto"
    OPENAI_API_KEY: str = get_secret("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3
    GEMINI_API_KEY: str = get_secret("GEMINI_API_KEY", "")

    # Logging configuration
    LOG_LEVEL: str = get_secret("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = get_secret("LOG_FORMAT", "json")
    LOG_FILE: str = get_secret("LOG_FILE", "logs/app.log")

    # Performance configuration
    WORKER_PROCESSES: int = int(get_secret("WORKER_PROCESSES", "4"))
    WORKER_THREADS: int = int(get_secret("WORKER_THREADS", "2"))
    REQUEST_TIMEOUT: int = int(get_secret("REQUEST_TIMEOUT", "30"))

    def __init__(self):
        """Initialize configuration with validation."""""
        self.validate_config()

    def validate_config(self):
        """Validate critical configuration values."""""
        errors = []

        # Validate required secrets
        if not self.SECRET_KEY:
            errors.append("SECRET_KEY is required")
        if not self.JWT_SECRET_KEY:
            errors.append("JWT_SECRET_KEY is required")

        # Validate database URL
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")

        # Validate AI provider configuration
        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")
        elif self.AI_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required when AI_PROVIDER is 'gemini'")

        if errors:
            raise ConfigValidationError(f"Configuration validation failed: {', '.join(errors)}")

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration as dictionary."""""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT,
            "pool_recycle": self.DATABASE_POOL_RECYCLE,
        }

    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration as dictionary."""""
        return {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD,
        }

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration as dictionary."""""
        return {
            "provider": self.AI_PROVIDER,
            "openai_api_key": self.OPENAI_API_KEY,
            "openai_model": self.OPENAI_MODEL,
            "openai_max_tokens": self.OPENAI_MAX_TOKENS,
            "openai_temperature": self.OPENAI_TEMPERATURE,
            "gemini_api_key": self.GEMINI_API_KEY,
        }


def get_config() -> Config:
    """Get application configuration instance."""""
    return Config()


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development configuration."""""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing configuration."""""
    DEBUG = True
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"


class ProductionConfig(Config):
    """Production configuration."""""
    DEBUG = False
    LOG_LEVEL = "WARNING"


# Configuration factory
def get_config_by_env(env: str = None) -> Config:
    """Get configuration based on environment."""""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")

    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()
