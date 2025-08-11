#!/usr/bin/env python3
"""
ML Models Package for Smart CloudOps AI
Anomaly detection using machine learning

This package provides production-ready machine learning models for anomaly detection
in cloud operations. It includes both traditional ML approaches and production
enhancements for real-world deployment.

Classes:
    AnomalyDetector: Main anomaly detection orchestrator
    DataProcessor: Data preprocessing and validation
    AnomalyModelTrainer: Model training and validation
    AnomalyInferenceEngine: Real-time inference engine
    ProductionAnomalyDetector: Production-ready ensemble detector

Example:
    >>> from ml_models import create_anomaly_detector
    >>> detector = create_anomaly_detector()
    >>> result = detector.detect_anomaly({'cpu_usage': 85.0})
    >>> print(result)
"""

from .anomaly_detector import AnomalyDetector
from .data_processor import DataProcessor
from .inference_engine import AnomalyInferenceEngine
from .model_trainer import AnomalyModelTrainer
from .production_enhancements import ProductionAnomalyDetector

# Version and metadata
__version__ = "1.0.0"
__author__ = "Smart CloudOps AI Team"
__description__ = "Production-ready ML anomaly detection for CloudOps"

# Main classes
__all__ = [
    "AnomalyDetector",
    "DataProcessor", 
    "AnomalyModelTrainer",
    "AnomalyInferenceEngine",
    "ProductionAnomalyDetector",
]

# Utility functions for easier access
def create_anomaly_detector(config_path: str = "ml_models/config.yaml") -> AnomalyDetector:
    """
    Create and return a configured AnomalyDetector instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured AnomalyDetector instance
        
    Example:
        >>> detector = create_anomaly_detector()
        >>> detector.train_model()
    """
    return AnomalyDetector(config_path)

def create_production_detector() -> ProductionAnomalyDetector:
    """
    Create and return a production-ready anomaly detector.
    
    Returns:
        ProductionAnomalyDetector instance with ensemble models
        
    Example:
        >>> detector = create_production_detector()
        >>> result = detector.detect_anomalies_production(metrics)
    """
    return ProductionAnomalyDetector()

def get_package_info() -> dict:
    """
    Get comprehensive package information and status.
    
    Returns:
        Dictionary containing package metadata and status
        
    Example:
        >>> info = get_package_info()
        >>> print(f"Version: {info['version']}")
    """
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "available_classes": __all__,
        "status": "ready",
        "python_version": "3.8+",
        "dependencies": ["pandas", "numpy", "scikit-learn", "joblib", "pyyaml"]
    }

def get_quick_start_example() -> str:
    """
    Get a quick start example for using the package.
    
    Returns:
        String containing quick start code example
    """
    return '''
# Quick Start Example
from ml_models import create_anomaly_detector

# Create detector
detector = create_anomaly_detector()

# Train model (if needed)
results = detector.train_model()

# Detect anomalies
metrics = {
    'cpu_usage_avg': 85.0,
    'memory_usage_pct': 75.0,
    'disk_usage_pct': 60.0
}
result = detector.detect_anomaly(metrics)
print(f"Anomaly detected: {result['is_anomaly']}")
'''

def validate_package_health() -> dict:
    """
    Validate the health and readiness of the ML models package.
    
    Returns:
        Dictionary containing health check results
        
    Example:
        >>> health = validate_package_health()
        >>> print(f"Package healthy: {health['healthy']}")
    """
    health_status = {
        "healthy": True,
        "checks": {},
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check if all classes can be imported
        from .anomaly_detector import AnomalyDetector
        from .data_processor import DataProcessor
        from .inference_engine import AnomalyInferenceEngine
        from .model_trainer import AnomalyModelTrainer
        from .production_enhancements import ProductionAnomalyDetector
        
        health_status["checks"]["imports"] = "✓ All classes imported successfully"
        
        # Check if model files exist
        import os
        model_path = "ml_models/models/anomaly_model.pkl"
        if os.path.exists(model_path):
            health_status["checks"]["model_files"] = "✓ Model files exist"
        else:
            health_status["checks"]["model_files"] = "⚠ Model files not found"
            health_status["warnings"].append("Model files not found - training required")
        
        # Check if config file exists
        config_path = "ml_models/config.yaml"
        if os.path.exists(config_path):
            health_status["checks"]["config"] = "✓ Configuration file exists"
        else:
            health_status["checks"]["config"] = "⚠ Configuration file not found"
            health_status["warnings"].append("Configuration file not found")
            
    except Exception as e:
        health_status["healthy"] = False
        health_status["errors"].append(f"Health check failed: {str(e)}")
        health_status["checks"]["health_check"] = f"✗ Health check failed: {str(e)}"
    
    return health_status

def get_usage_statistics() -> dict:
    """
    Get usage statistics and information about the package.
    
    Returns:
        Dictionary containing usage statistics
        
    Example:
        >>> stats = get_usage_statistics()
        >>> print(f"Available models: {stats['available_models']}")
    """
    import os
    
    stats = {
        "package_version": __version__,
        "available_models": [],
        "config_files": [],
        "data_files": []
    }
    
    # Check available models
    models_dir = "ml_models/models"
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.pkl'):
                stats["available_models"].append(file)
    
    # Check config files
    config_dir = "ml_models"
    if os.path.exists(config_dir):
        for file in os.listdir(config_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                stats["config_files"].append(file)
    
    # Check data files
    data_dir = "ml_models/data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv') or file.endswith('.json'):
                stats["data_files"].append(file)
    
    return stats

# Constants for common configurations
DEFAULT_CONFIG_PATH = "ml_models/config.yaml"
DEFAULT_MODEL_PATH = "ml_models/models/anomaly_model.pkl"
DEFAULT_LOOKBACK_HOURS = 168  # 1 week
DEFAULT_MIN_F1_SCORE = 0.85

# Package status indicators
PACKAGE_STATUS = {
    "ready": "Package is ready for production use",
    "testing": "Package is in testing phase",
    "development": "Package is under development"
}

# Add the new functions to __all__
__all__.extend([
    "validate_package_health",
    "get_usage_statistics"
])
