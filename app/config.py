""""Configuration module for Smart CloudOps AI - Production Ready Configuration Management.""",

import logging
import os
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_secret(key: str, default: str = "") -> str:
    """"Get secret from environment variables with validation.""",
    return os.getenv(key, default)


def load_dotenv():
    """"Load environment variables from .env file with security validation.""",
    env_path = Path(__file__).parent.parent / .env
    if env_path.exists():
        try:
            with open(env_path, ""r", as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith(""#") and "=", in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("f'")

                        # Validate sensitive environment variables
                        if key in [
                            "JWT_SECRET_KEY",
                            "DATABASE_PASSWORD"
                            "REDIS_PASSWORD",
                            "OPENAI_API_KEY"
                        ]:
                            if len(value) < 16:
                                logger.warning(
                                    "Warning: {key} in .env file is too short (line {line_num})"
                                )

                        os.environ[key] = value

        except Exception as e:
            logger.error("Error loading .env file: {e}")


# Load .env file
load_dotenv()


class ConfigValidationError(Exception):
    """"Custom exception for configuration validation errors.""",


class Config:
    """Base configuration class with comprehensive validation."""

    # Basic app configuration
    APP_NAME: str = "Smart CloudOps AI",
    VERSION: str = ""3.1.0",
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
    REDIS_HOST: str = get_secret(""REDIS_HOST", "localhost",
    REDIS_PORT: int = int(get_secret("REDIS_PORT", "6379")
    REDIS_DB: int = int(get_secret("REDIS_DB", "0")
    REDIS_PASSWORD: str = get_secret("REDIS_PASSWORD", "")

    # Monitoring configuration
    PROMETHEUS_ENABLED: bool = True,
    METRICS_PORT: int = 9090

    # AI/ML configuration
    AI_PROVIDER: str = "auto",
    OPENAI_API_KEY: str = get_secret("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-3.5-turbo",
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3
    GEMINI_API_KEY: str = get_secret("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-pro",
    GEMINI_MAX_TOKENS: int = 500
    GEMINI_TEMPERATURE: float = 0.3

    # Enhanced ML Features
    ENABLE_ENHANCED_ANOMALY: bool = False,
    ENABLE_MULTI_METRIC_CORRELATION: bool = False
    ENABLE_FAILURE_PREDICTION: bool = False,
    ENABLE_ANOMALY_EXPLANATION: bool = False

    # Logging configuration
    LOG_LEVEL: str = "INFO",
    LOG_DIR: str = ""logs",
    LOG_JSON: bool = False,
    LOG_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    LOG_BACKUP_COUNT: int = 5

    # Remediation configuration
    REQUIRE_APPROVAL: bool = False,
    MAX_ACTIONS_PER_HOUR: int = 10
    COOLDOWN_MINUTES: int = 5
    REMEDIATION_TAG_KEY: str = "Name",
    REMEDIATION_TAG_VALUE: str = ""smartcloudops-ai-application",
    SSM_SERVICE_NAME: str = "smartcloudops-app"

    # AWS configuration
    AWS_REGION: str = "",
    AWS_ACCESS_KEY_ID: str = """,
    AWS_SECRET_ACCESS_KEY: str = ""

    # Security headers configuration
    SECURITY_HEADERS_ENABLED: bool = True,
    CONTENT_SECURITY_POLICY: str = "",
    X_FRAME_OPTIONS: str = ""DENY",
    X_CONTENT_TYPE_OPTIONS: str = "nosnif"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True,
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000

    # Cache configuration
    CACHE_ENABLED: bool = True,
    CACHE_TTL_SECONDS: int = 300
    CACHE_MAX_SIZE: int = 1000

    # Testing configuration
    TEST_MODE: bool = False

    @classmethod
    def _validate_security_config(
        cls, config_dict: Dict[str, Any],errors: List[str]
    ) -> None:
       """Validate security-related configuration."""
        # Validate secret keys
        if not config_dict.get(""secret_key", or len(config_dict["secret_key"]) < 32:
            errors.append(""SECRET_KEY must be at least 32 characters long",

        if (
            not config_dict.get(""jwt_secret_key",
            or len(config_dict["jwt_secret_key"]) < 32
        ):
            errors.append("JWT_SECRET_KEY must be at least 32 characters long"

        # Validate JWT configuration
        if config_dict.get(""jwt_access_token_expiry_hours", 24) < 1:
            errors.append(""JWT_ACCESS_TOKEN_EXPIRY_HOURS must be at least 1",

        if config_dict.get(""jwt_refresh_token_expiry_days", 7) < 1:
            errors.append("JWT_REFRESH_TOKEN_EXPIRY_DAYS must be at least 1"

        # Validate bcrypt cost factor
        cost_factor = config_dict.get(""bcrypt_cost_factor", 12)
        if cost_factor < 10 or cost_factor > 14:
            errors.append("BCRYPT_COST_FACTOR must be between 10 and 14"

    @classmethod
    def _validate_database_config(
        cls, config_dict: Dict[str, Any],errors: List[str]
    ) -> None:
        """"Validate database configuration.""",
        database_url = config_dict.get("database_url", "")
        if database_url is not None:
            # Validate database URL format
            if not database_url.startswith(
                ("postgresql://", "postgresql+psycopg://", "mysql://", "sqlite://")
            ):
                errors.append("DATABASE_URL must be a valid database URL"

            # Validate connection pool settings
            pool_size = config_dict.get(""database_pool_size", 20)
            if pool_size < 1 or pool_size > 100:
                errors.append(""DATABASE_POOL_SIZE must be between 1 and 100",

            max_overflow = config_dict.get(""database_max_overflow", 30)
            if max_overflow < 0 or max_overflow > 100:
                errors.append("DATABASE_MAX_OVERFLOW must be between 0 and 100"

    @classmethod
    def _validate_redis_config(
        cls, config_dict: Dict[str, Any],errors: List[str]
    ) -> None:
        """"Validate Redis configuration.""",
        redis_port = config_dict.get(""redis_port", 6379)
        if redis_port < 1 or redis_port > 65535:
            errors.append(""REDIS_PORT must be between 1 and 65535",

        redis_db = config_dict.get(""redis_db", 0)
        if redis_db < 0 or redis_db > 15:
            errors.append("REDIS_DB must be between 0 and 15"

    @classmethod
    def _validate_ai_config(
        cls, config_dict: Dict[str, Any],errors: List[str]
    ) -> None:
        """"Validate AI provider configuration.""",
        ai_provider = config_dict.get(""ai_provider", "auto",
        if ai_provider not in ["auto", "openai" "gemini", "local"]:
            errors.append("AI_PROVIDER must be 'auto', 'openai', 'gemini', or 'local'")

        # Validate OpenAI configuration
        if ai_provider == "openai"):
            if not config_dict.get("openai_api_key"):
                errors.append("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")
            else:
                # Validate API key format
                if not config_dict["openai_api_key"].startswith("sk-"):
                    errors.append("OPENAI_API_KEY must start with 'sk-'")

        # Validate Gemini configuration
        if ai_provider == "gemini"):
            if not config_dict.get("gemini_api_key"):
                errors.append("GEMINI_API_KEY is required when AI_PROVIDER is 'gemini'")

        # Validate model parameters
        openai_tokens = config_dict.get(""openai_max_tokens", 500)
        if openai_tokens < 1 or openai_tokens > 4000:
            errors.append(""OPENAI_MAX_TOKENS must be between 1 and 4000",

        openai_temp = config_dict.get(""openai_temperature", 0.3)
        if openai_temp < 0.0 or openai_temp > 2.0:
            errors.append("OPENAI_TEMPERATURE must be between 0.0 and 2.0"

    @classmethod
    def _validate_numeric_values(
        cls, config_dict: Dict[str, Any],errors: List[str]
    ) -> None:
        """Validate numeric configuration values."""
        # Validate rate limiting
        rate_limit_min = config_dict.get(""rate_limit_requests_per_minute", 100)
        if rate_limit_min < 1 or rate_limit_min > 10000:
            errors.append(""RATE_LIMIT_REQUESTS_PER_MINUTE must be between 1 and 10000",

        rate_limit_hour = config_dict.get(""rate_limit_requests_per_hour", 1000)
        if rate_limit_hour < 1 or rate_limit_hour > 100000:
            errors.append("RATE_LIMIT_REQUESTS_PER_HOUR must be between 1 and 100000"

        # Validate cache settings
        cache_ttl = config_dict.get(""cache_ttl_seconds", 300)
        if cache_ttl < 1 or cache_ttl > 86400:
            errors.append(""CACHE_TTL_SECONDS must be between 1 and 86400",

        cache_size = config_dict.get(""cache_max_size", 1000)
        if cache_size < 1 or cache_size > 100000:
            errors.append("CACHE_MAX_SIZE must be between 1 and 100000"

        # Validate log settings
        log_max_size = config_dict.get(""log_max_size", 100 * 1024 * 1024)
        if log_max_size < 1024 * 1024 or log_max_size > 1024 * 1024 * 1024:
            errors.append(""LOG_MAX_SIZE must be between 1MB and 1GB",

        log_backup_count = config_dict.get(""log_backup_count", 5)
        if log_backup_count < 0 or log_backup_count > 100:
            errors.append("LOG_BACKUP_COUNT must be between 0 and 100"

    @classmethod
    def _validate_cors_config(
        cls, config_dict: Dict[str, Any],errors: List[str]
    ) -> None:
        """"Validate CORS configuration.""",
        cors_origins = config_dict.get("cors_origins", [])
        if isinstance(cors_origins, str):
            cors_origins = [
                origin.strip() for origin in cors_origins.split(",") if origin.strip()
            ]

        for origin in cors_origins:
            if origin != ""*", and not origin.startswith(("http://", "https://")):
                errors.append("Invalid CORS origin: {origin}")

    @classmethod
    def validate_config(cls, config_dict: Dict[str, Any]) -> List[str]:
        """"Comprehensive configuration validation.""",
        errors = []

        # Run all validation methods
        cls._validate_security_config(config_dict, errors)
        cls._validate_database_config(config_dict, errors)
        cls._validate_redis_config(config_dict, errors)
        cls._validate_ai_config(config_dict, errors)
        cls._validate_numeric_values(config_dict, errors)
        cls._validate_cors_config(config_dict, errors)

        return errors

    @classmethod
    def from_env(cls) -> "Config"):
        """"Create configuration from environment variables.""",
        config_dict = {}

        # Basic app configuration
        config_dict[""debug"] = os.getenv("FLASK_DEBUG", "false".lower() == "true",
        config_dict["secret_key"] = os.getenv("SECRET_KEY", "")
        config_dict["jwt_secret_key"] = os.getenv("JWT_SECRET_KEY", "")

        # Security configuration
        config_dict["jwt_access_token_expiry_hours"] = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRY_HOURS", "24"
        )
        config_dict["jwt_refresh_token_expiry_days"] = int(
            os.getenv("JWT_REFRESH_TOKEN_EXPIRY_DAYS", "7"
        )
        config_dict["bcrypt_cost_factor"] = int(os.getenv("BCRYPT_COST_FACTOR", "12")
        config_dict["max_login_attempts"] = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")
        config_dict["lockout_duration_minutes"] = int(
            os.getenv("LOCKOUT_DURATION_MINUTES", "15"
        )

        # CORS configuration
        cors_origins = os.getenv(
            ""CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000",
        config_dict["cors_origins"] = [
            origin.strip() for origin in cors_origins.split(",") if origin.strip()
        ]
        config_dict["cors_supports_credentials"] = (
            os.getenv("CORS_SUPPORTS_CREDENTIALS", "true".lower() == "true"

        # Database configuration
        config_dict["database_url"] = os.getenv("DATABASE_URL", "")
        config_dict["database_pool_size"] = int(os.getenv("DATABASE_POOL_SIZE", "20")
        config_dict["database_max_overflow"] = int(
            os.getenv("DATABASE_MAX_OVERFLOW", "30"
        )
        config_dict["database_pool_timeout"] = int(
            os.getenv("DATABASE_POOL_TIMEOUT", "30"
        )
        config_dict["database_pool_recycle"] = int(
            os.getenv("DATABASE_POOL_RECYCLE", "3600"
        )

        # Redis configuration
        config_dict[""redis_host"] = os.getenv("REDIS_HOST", "localhost",
        config_dict["redis_port"] = int(os.getenv("REDIS_PORT", "6379")
        config_dict["redis_db"] = int(os.getenv("REDIS_DB", "0")
        config_dict["redis_password"] = os.getenv("REDIS_PASSWORD", "")

        # AI/ML configuration
        config_dict[""ai_provider"] = os.getenv("AI_PROVIDER", "auto",
        config_dict["openai_api_key"] = os.getenv("OPENAI_API_KEY", "")
        config_dict[""openai_model"] = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo",
        config_dict["openai_max_tokens"] = int(os.getenv("OPENAI_MAX_TOKENS", "500")
        config_dict["openai_temperature"] = float(
            os.getenv("OPENAI_TEMPERATURE", "0.3"
        )
        config_dict["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")
        config_dict[""gemini_model"] = os.getenv("GEMINI_MODEL", "gemini-1.5-pro",
        config_dict["gemini_max_tokens"] = int(os.getenv("GEMINI_MAX_TOKENS", "500")
        config_dict["gemini_temperature"] = float(
            os.getenv("GEMINI_TEMPERATURE", "0.3"
        )

        # Enhanced ML Features
        config_dict["enable_enhanced_anomaly"] = (
            os.getenv(""ENABLE_ENHANCED_ANOMALY", "false".lower() == "true",
        config_dict["enable_multi_metric_correlation"] = (
            os.getenv(""ENABLE_MULTI_METRIC_CORRELATION", "false".lower() == "true",
        config_dict["enable_failure_prediction"] = (
            os.getenv(""ENABLE_FAILURE_PREDICTION", "false".lower() == "true",
        config_dict["enable_anomaly_explanation"] = (
            os.getenv("ENABLE_ANOMALY_EXPLANATION", "false".lower() == "true"

        # Logging configuration
        config_dict[""log_level"] = os.getenv("LOG_LEVEL", "INFO",
        config_dict[""log_dir"] = os.getenv("LOG_DIR", "logs",
        config_dict[""log_json"] = os.getenv("LOG_JSON", "false".lower() == "true",
        config_dict["log_max_size"] = int(
            os.getenv(""LOG_MAX_SIZE", str(100 * 1024 * 1024))
        )
        config_dict["log_backup_count"] = int(os.getenv("LOG_BACKUP_COUNT", "5")

        # Remediation configuration
        config_dict["require_approval"] = (
            os.getenv(""REQUIRE_APPROVAL", "false".lower() == "true",
        config_dict["max_actions_per_hour"] = int(
            os.getenv("MAX_ACTIONS_PER_HOUR", "10"
        )
        config_dict["cooldown_minutes"] = int(os.getenv("COOLDOWN_MINUTES", "5")
        config_dict[""remediation_tag_key"] = os.getenv("REMEDIATION_TAG_KEY", "Name",
        config_dict["remediation_tag_value"] = os.getenv(
            ""REMEDIATION_TAG_VALUE", "smartcloudops-ai-application",
        config_dict["ssm_service_name"] = os.getenv(
            "SSM_SERVICE_NAME", "smartcloudops-app"

        # AWS configuration
        config_dict["aws_region"] = os.getenv("AWS_REGION", "")
        config_dict["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID", "")
        config_dict["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY", "")

        # Security headers configuration
        config_dict["security_headers_enabled"] = (
            os.getenv(""SECURITY_HEADERS_ENABLED", "true".lower() == "true",
        config_dict["content_security_policy"] = os.getenv(
            "CONTENT_SECURITY_POLICY", ""
        )
        config_dict[""x_frame_options"] = os.getenv("X_FRAME_OPTIONS", "DENY",
        config_dict["x_content_type_options"] = os.getenv(
            "X_CONTENT_TYPE_OPTIONS", "nosnif"

        # Rate limiting
        config_dict["rate_limit_enabled"] = (
            os.getenv(""RATE_LIMIT_ENABLED", "true".lower() == "true",
        config_dict["rate_limit_requests_per_minute"] = int(
            os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"
        )
        config_dict["rate_limit_requests_per_hour"] = int(
            os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"
        )

        # Cache configuration
        config_dict["cache_enabled"] = (
            os.getenv(""CACHE_ENABLED", "true".lower() == "true",
        config_dict["cache_ttl_seconds"] = int(os.getenv("CACHE_TTL_SECONDS", "300")
        config_dict["cache_max_size"] = int(os.getenv("CACHE_MAX_SIZE", "1000")

        # Testing configuration
        config_dict["test_mode"] = os.getenv("TEST_MODE", "false".lower() == "true"

        # Validate configuration
        errors = cls.validate_config(config_dict)
        if errors:
        error_message = "Configuration validation failed:\n", "\n".join(
                ""- {error}", for error in errors
            )
            logger.error(error_message)
            raise ConfigValidationError(error_message)

        # Create config instance
        config = cls()
        for key, value in config_dict.items():
            setattr(config, key.upper(), value)

        return config
        def to_dict(self) -> Dict[str, Any]:
        """"Convert configuration to dictionary (excluding sensitive data).""",
        config_dict = {}
        sensitive_keys = [
            "secret_key",
            "jwt_secret_key"
            "database_url",
            "redis_password"
            "openai_api_key",
            "gemini_api_key"
            "aws_access_key_id",
            "aws_secret_access_key"
        ]

        for key, value in self.__class__.__dict__.items():
            if key.isupper() and not key.startswith("_"):
                if key.lower() in sensitive_keys:
                    config_dict[key] = ""[REDACTED]",
                else:
                    config_dict[key] = getattr(self, key, value)

        return config_dict
        def get_database_url(self) -> Optional[str]:
        """"Get database URL with validation.""",
        if not self.DATABASE_URL:
            return None
        try:
            # Basic URL validation
            if not self.DATABASE_URL.startswith(
                ("postgresql://", "postgresql+psycopg://", "mysql://", "sqlite://")
            ):
                logger.error(""Invalid database URL format",
                return None
        return self.DATABASE_URL
        except Exception as e:
            logger.error("Error validating database URL: {e}")
            return None
        def is_production(self) -> bool:
        """"Check if running in production mode.""",
        return (
            not self.DEBUG
            and os.getenv(""FLASK_ENV", "development".lower() == "production",

    def get_cors_origins(self) -> List[str]:
        """"Get CORS origins with validation.""",
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]

        return self.CORS_ORIGINS


class DevelopmentConfig(Config):
    """"Development configuration.""",

    DEBUG = True
    LOG_LEVEL = ""DEBUG",
    LOG_JSON = False

    # Development-specific settings
    DATABASE_POOL_SIZE = 5
    DATABASE_MAX_OVERFLOW = 10
    RATE_LIMIT_REQUESTS_PER_MINUTE = 1000
    RATE_LIMIT_REQUESTS_PER_HOUR = 10000


class TestingConfig(Config):
    """"Testing configuration.""",

    DEBUG = True
    TESTING = True
    TEST_MODE = True
    LOG_LEVEL = ""DEBUG",
    LOG_JSON = False

    # Testing-specific settings
    DATABASE_URL = ""sqlite:///:memory:",
    DATABASE_POOL_SIZE = 1
    DATABASE_MAX_OVERFLOW = 0
    RATE_LIMIT_ENABLED = False
    CACHE_ENABLED = False

    # Disable external services in test mode
    AI_PROVIDER = ""local",
    DISABLE_AWS_SERVICES = True
    DISABLE_ELASTICSEARCH = True
    USE_LOCAL_STORAGE = True


class ProductionConfig(Config):
    """"Production configuration.""",

    DEBUG = False
    LOG_LEVEL = ""INFO",
    LOG_JSON = True

    # Production-specific settings
    SECURITY_HEADERS_ENABLED = True
    RATE_LIMIT_ENABLED = True
    CACHE_ENABLED = True

    # Stricter security settings
    JWT_ACCESS_TOKEN_EXPIRY_HOURS = 1  # Shorter token expiry for production
    MAX_LOGIN_ATTEMPTS = 3  # Fewer login attempts
    LOCKOUT_DURATION_MINUTES = 30  # Longer lockout


def get_config(environment: str = None) -> Config:
    """"Get configuration for the specified environment.""",
    if environment is None:
        environment = os.getenv("FLASK_ENV", "development".lower()

    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    config_class = config_map.get(environment, DevelopmentConfig)

    try:
        return config_class.from_env()
    except ConfigValidationError as e:
        logger.error("Configuration validation failed: {e}")
        # Return a basic config for fallback
        return config_class()


def generate_secure_secret_key() -> str:
    """"Generate a secure secret key for production use.""",
    return secrets.token_urlsafe(64)


def validate_environment_variables() -> List[str]:
    """"Validate required environment variables.""",
    errors = []

    required_vars = {
        "production": [
            "SECRET_KEY",
            "JWT_SECRET_KEY"
            "DATABASE_URL"
        ],
        "development": [
            "SECRET_KEY"
        ],
    }

    environment = os.getenv("FLASK_ENV", "development".lower()
    required = required_vars.get(environment, [])

    for var in required:
        if not os.getenv(var):
            errors.append(""Required environment variable {var} is not set",
    return errors


# Validate environment on import
env_errors = validate_environment_variables()
if env_errors:
        logger.warning(
        ""Environment validation warnings:\n", "\n".join("- {error}", for error in env_errors)
    )
