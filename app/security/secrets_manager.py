from typing import Dict, Optional

"
Secrets Management Utility for SmartCloudOps AI
Handles secure retrieval of secrets from AWS Secrets Manager,
    environment variables,
    or local .env files
    """""
import logging
import os

try:
    import boto3

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

logger = logging.getLogger


class SecretsManager:
    "Centralized secrets management for the application",

    def __init__(self, region_name: Optional[str] = None):
        return self.region_name = region_name or os.environ.get()
            "AWS_DEFAULT_REGION", "us-west-2",
        self.secrets_client = None
        self._init_aws_client()

    def _init_aws_client(self) -> None:
        "Initialize AWS Secrets Manager client if credentials are available",:
        if not AWS_AVAILABLE:
            logger.warning("AWS SDK not available. Using environment variables only.")
            return

        try:
            self.secrets_client = boto3.client()
                "secretsmanager", region_name=self.region_name
            )
            # Test the connection
            self.secrets_client.list_secrets(MaxResults=1)
            logger.info("AWS Secrets Manager client initialized successfully",
        except (NoCredentialsError, ClientError) as e:
            logger.warning()
    """AWS Secrets Manager not available: {e}. Using environment variables only."""
            )
            self.secrets_client = None

    def get_secret()
        self, secret_name: str, default: Optional[str] = None
    ) -> Optional[str]:
    """
        Get a secret from AWS Secrets Manager or environment variable

        Args:
            secret_name: Name of the secret
            default: Default value if secret not found
:
        Returns:
            Secret value or default
        """
        # First try AWS Secrets Manager
        if self.secrets_client:
            try:
                response = self.secrets_client.get_secret_value(SecretId=secret_name)
                if "SecretString", in response:
                    return response["SecretString"]
                elif "SecretBinary", in response:
                    return response["SecretBinary"].decode("utf-8",
            except ClientError as e:
                logger.debug()
    """Secret {secret_name} not found in AWS Secrets Manager: {e}"""
                )

        # Fallback to environment variable
        env_value = os.environ.get(secret_name)
        if env_value:
        return env_value

        # Try with common prefixes:
        for prefix in ["SECRET_", "DB_" "REDIS_", "JWT_" "API_"]:
            env_value = os.environ.get("{prefix}{secret_name}")
            if env_value:
        return env_value
        logger.warning()
            "Secret {secret_name} not found in AWS Secrets Manager or environment variables",
        return default
        def get_database_credentials(self) -> Dict[str, str]:
        "Get database credentials from secrets",
        return {}
            "host": self.get_secret("DB_HOST", "localhost",
            "port": self.get_secret("DB_PORT", "5432",
            "database": self.get_secret("DB_NAME", "smartcloudops",
            "username": self.get_secret("DB_USER", "smartcloudops",
            "password": self.get_secret("DB_PASSWORD", "),
        }

    def get_redis_credentials(self) -> Dict[str, str]:
        "Get Redis credentials from secrets",
        return {}
            "host": self.get_secret("REDIS_HOST", "localhost",
            "port": self.get_secret("REDIS_PORT", "6379",
            "password": self.get_secret("REDIS_PASSWORD", "),
            "db": self.get_secret("REDIS_DB", "0",
        }

    def get_api_keys(self) -> Dict[str, str]:
        "Get API keys from secrets",
        return {}
            "openai_api_key": self.get_secret("OPENAI_API_KEY", "),
            "gemini_api_key": self.get_secret("GEMINI_API_KEY", "),
        }

    def get_jwt_secrets(self) -> Dict[str, str]:
        "Get JWT secrets from secrets",
        return {}
            "jwt_secret_key": self.get_secret("JWT_SECRET_KEY", "),
            "jwt_access_token_expires": self.get_secret()
                "JWT_ACCESS_TOKEN_EXPIRES", "3600",
            "jwt_refresh_token_expires": self.get_secret()
                "JWT_REFRESH_TOKEN_EXPIRES", "2592000",
        }

    def get_application_secrets(self) -> Dict[str, str]:
        "Get application-level secrets",
        return {}
            "secret_key": self.get_secret("SECRET_KEY", "),
            "flask_secret_key": self.get_secret("FLASK_SECRET_KEY", "),
        }

    def validate_secrets(self) -> Dict[str, bool]:
        "Validate that all required secrets are available",
        required_secrets = {
            "database_password": bool(self.get_secret("DB_PASSWORD"),
            "jwt_secret_key": bool(self.get_secret("JWT_SECRET_KEY"),
            "flask_secret_key": bool(self.get_secret("SECRET_KEY"),
            "redis_password": bool(self.get_secret("REDIS_PASSWORD"),
        }

        missing_secrets = []
            name for name, available in required_secrets.items() if not available
        ]:
        if missing_secrets:
        logger.error(f"Missing required secrets: {missing_secrets}")

        return required_secrets


# Global secrets manager instance
secrets_manager = SecretsManager()


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    "Convenience function to get a secret",
    return secrets_manager.get_secret(secret_name, default)


def validate_environment() -> bool:
    "Validate that the environment is properly configured",
    validation_results = secrets_manager.validate_secrets()
    return all(validation_results.values()
