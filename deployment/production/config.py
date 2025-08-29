"""
Production Configuration Management
Phase 2C Week 2: Production Deployment - Configuration
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import secrets
import hashlib

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str
    max_connections: int = 20
    timeout: float = 30.0
    backup_enabled: bool = True
    backup_interval_hours: int = 6
    vacuum_interval_hours: int = 24


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    max_size: int = 10000
    default_ttl: int = 300
    cleanup_interval: int = 300
    redis_url: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str
    jwt_secret: str
    password_salt: str
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 100
    cors_origins: List[str] = None
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    health_check_interval: int = 30
    metrics_retention_days: int = 30
    alert_email_enabled: bool = False
    alert_emails: List[str] = None
    log_level: str = "INFO"
    log_file: str = "logs/app.log"


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    caching_enabled: bool = True
    database_optimization: bool = True
    background_tasks: bool = True
    memory_monitoring: bool = True
    request_timeout: int = 30
    max_workers: int = 4


class ProductionConfig:
    """Production configuration manager"""
    
    def __init__(self, environment: Environment = Environment.PRODUCTION):
        self.environment = environment
        self.config_file = Path(f"deployment/production/config_{environment.value}.json")
        
        # Initialize configuration
        self.database = DatabaseConfig(
            path=self._get_env("DATABASE_PATH", f"data/mlops_{environment.value}.db"),
            max_connections=int(self._get_env("DB_MAX_CONNECTIONS", "20")),
            timeout=float(self._get_env("DB_TIMEOUT", "30.0"))
        )
        
        self.cache = CacheConfig(
            enabled=self._get_env_bool("CACHE_ENABLED", True),
            max_size=int(self._get_env("CACHE_MAX_SIZE", "10000")),
            default_ttl=int(self._get_env("CACHE_DEFAULT_TTL", "300")),
            redis_url=self._get_env("REDIS_URL")
        )
        
        self.security = SecurityConfig(
            secret_key=self._get_or_generate_secret("SECRET_KEY"),
            jwt_secret=self._get_or_generate_secret("JWT_SECRET"),
            password_salt=self._get_or_generate_secret("PASSWORD_SALT"),
            rate_limit_enabled=self._get_env_bool("RATE_LIMIT_ENABLED", True),
            max_requests_per_minute=int(self._get_env("MAX_REQUESTS_PER_MINUTE", "100")),
            cors_origins=self._get_env_list("CORS_ORIGINS", ["http://localhost:3000"]),
            ssl_enabled=self._get_env_bool("SSL_ENABLED", environment == Environment.PRODUCTION),
            ssl_cert_path=self._get_env("SSL_CERT_PATH"),
            ssl_key_path=self._get_env("SSL_KEY_PATH")
        )
        
        self.monitoring = MonitoringConfig(
            enabled=self._get_env_bool("MONITORING_ENABLED", True),
            health_check_interval=int(self._get_env("HEALTH_CHECK_INTERVAL", "30")),
            metrics_retention_days=int(self._get_env("METRICS_RETENTION_DAYS", "30")),
            alert_email_enabled=self._get_env_bool("ALERT_EMAIL_ENABLED", False),
            alert_emails=self._get_env_list("ALERT_EMAILS", []),
            log_level=self._get_env("LOG_LEVEL", "INFO" if environment == Environment.PRODUCTION else "DEBUG"),
            log_file=self._get_env("LOG_FILE", f"logs/{environment.value}.log")
        )
        
        self.performance = PerformanceConfig(
            caching_enabled=self._get_env_bool("PERFORMANCE_CACHING", True),
            database_optimization=self._get_env_bool("DATABASE_OPTIMIZATION", True),
            background_tasks=self._get_env_bool("BACKGROUND_TASKS", True),
            memory_monitoring=self._get_env_bool("MEMORY_MONITORING", True),
            request_timeout=int(self._get_env("REQUEST_TIMEOUT", "30")),
            max_workers=int(self._get_env("MAX_WORKERS", "4"))
        )
        
        # Load or save configuration
        self._load_or_create_config()
    
    def _get_env(self, key: str, default: str = None) -> Optional[str]:
        """Get environment variable with default"""
        return os.getenv(key, default)
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_env_list(self, key: str, default: List[str] = None) -> List[str]:
        """Get list environment variable"""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(',')]
        return default or []
    
    def _get_or_generate_secret(self, key: str) -> str:
        """Get or generate a secure secret"""
        value = os.getenv(key)
        if value:
            return value
        
        # Generate secure random secret
        secret = secrets.token_urlsafe(32)
        logger.warning(f"Generated new secret for {key}. Set {key} environment variable in production!")
        return secret
    
    def _load_or_create_config(self):
        """Load configuration from file or create new one"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
                self._save_config()
        else:
            self._save_config()
    
    def _save_config(self):
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                'environment': self.environment.value,
                'database': {
                    'path': self.database.path,
                    'max_connections': self.database.max_connections,
                    'timeout': self.database.timeout,
                    'backup_enabled': self.database.backup_enabled,
                    'backup_interval_hours': self.database.backup_interval_hours,
                    'vacuum_interval_hours': self.database.vacuum_interval_hours
                },
                'cache': {
                    'enabled': self.cache.enabled,
                    'max_size': self.cache.max_size,
                    'default_ttl': self.cache.default_ttl,
                    'cleanup_interval': self.cache.cleanup_interval,
                    'redis_url': self.cache.redis_url
                },
                'security': {
                    # Don't save actual secrets to file
                    'rate_limit_enabled': self.security.rate_limit_enabled,
                    'max_requests_per_minute': self.security.max_requests_per_minute,
                    'cors_origins': self.security.cors_origins,
                    'ssl_enabled': self.security.ssl_enabled,
                    'ssl_cert_path': self.security.ssl_cert_path,
                    'ssl_key_path': self.security.ssl_key_path
                },
                'monitoring': {
                    'enabled': self.monitoring.enabled,
                    'health_check_interval': self.monitoring.health_check_interval,
                    'metrics_retention_days': self.monitoring.metrics_retention_days,
                    'alert_email_enabled': self.monitoring.alert_email_enabled,
                    'alert_emails': self.monitoring.alert_emails,
                    'log_level': self.monitoring.log_level,
                    'log_file': self.monitoring.log_file
                },
                'performance': {
                    'caching_enabled': self.performance.caching_enabled,
                    'database_optimization': self.performance.database_optimization,
                    'background_tasks': self.performance.background_tasks,
                    'memory_monitoring': self.performance.memory_monitoring,
                    'request_timeout': self.performance.request_timeout,
                    'max_workers': self.performance.max_workers
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Database validation
        db_path = Path(self.database.path)
        if not db_path.parent.exists():
            issues.append(f"Database directory does not exist: {db_path.parent}")
        
        if self.database.max_connections < 1:
            issues.append("Database max_connections must be at least 1")
        
        # Security validation
        if len(self.security.secret_key) < 32:
            issues.append("SECRET_KEY should be at least 32 characters")
        
        if self.security.ssl_enabled:
            if not self.security.ssl_cert_path or not Path(self.security.ssl_cert_path).exists():
                issues.append("SSL certificate file not found")
            
            if not self.security.ssl_key_path or not Path(self.security.ssl_key_path).exists():
                issues.append("SSL key file not found")
        
        # Monitoring validation
        log_dir = Path(self.monitoring.log_file).parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                issues.append(f"Cannot create log directory: {log_dir}")
        
        if self.monitoring.alert_email_enabled and not self.monitoring.alert_emails:
            issues.append("Alert emails not configured but email alerts enabled")
        
        # Performance validation
        if self.performance.max_workers < 1:
            issues.append("max_workers must be at least 1")
        
        if self.performance.request_timeout < 1:
            issues.append("request_timeout must be at least 1 second")
        
        return issues
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask-specific configuration"""
        return {
            'SECRET_KEY': self.security.secret_key,
            'DEBUG': self.environment == Environment.DEVELOPMENT,
            'TESTING': self.environment == Environment.TESTING,
            'ENV': self.environment.value,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
            'WTF_CSRF_TIME_LIMIT': None,
            'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': self.environment == Environment.DEVELOPMENT
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'level': self.monitoring.log_level,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': self.monitoring.log_file,
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'detailed'
                },
                'console': {
                    'level': self.monitoring.log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file', 'console'],
                    'level': self.monitoring.log_level,
                    'propagate': False
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment.value,
            'database': self.database.__dict__,
            'cache': self.cache.__dict__,
            'security': {
                # Exclude sensitive data
                'rate_limit_enabled': self.security.rate_limit_enabled,
                'max_requests_per_minute': self.security.max_requests_per_minute,
                'cors_origins': self.security.cors_origins,
                'ssl_enabled': self.security.ssl_enabled
            },
            'monitoring': self.monitoring.__dict__,
            'performance': self.performance.__dict__
        }


class ConfigManager:
    """Global configuration manager"""
    
    _instance = None
    _config = None
    
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = cls(
    return cls._instance
    
    def __init__(self):
        if ConfigManager._instance is not None:
            raise Exception("ConfigManager is a singleton")
    
    def initialize(self, environment: Environment = None) -> ProductionConfig:
        """Initialize configuration"""
        if environment is None:
            env_name = os.getenv('ENVIRONMENT', 'development').lower()
            try:
                environment = Environment(env_name)
            except ValueError:
                logger.warning(f"Unknown environment '{env_name}', defaulting to development")
                environment = Environment.DEVELOPMENT
        
        self._config = ProductionConfig(environment)
        
        # Validate configuration
        issues = self._config.validate_config()
        if issues:
            logger.warning("Configuration validation issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        
        logger.info(f"Configuration initialized for {environment.value} environment")
        return self._config
    
    def get_config(self) -> ProductionConfig:
        """Get current configuration"""
        if self._config is None:
            raise RuntimeError("Configuration not initialized. Call initialize() first.")
        return self._config


# Global configuration instance
config_manager = ConfigManager(
    def get_config() -> ProductionConfig:
    """Get global configuration"""
    return config_manager.get_config()


def initialize_config(environment: Environment = None) -> ProductionConfig:
    """Initialize global configuration"""
    return config_manager.initialize(environment)
