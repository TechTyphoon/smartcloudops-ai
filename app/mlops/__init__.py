"""
SmartCloudOps AI - MLOps Module
Production-ready MLOps capabilities for experiment tracking, model management, and automated operations

Phase 2A: Working modules only - Conservative import approach
"""

# Start with minimal working imports
try:
    from .experiment_tracker import ExperimentTracker, get_experiment_tracker

    EXPERIMENT_TRACKER_AVAILABLE = True
except ImportError:
    EXPERIMENT_TRACKER_AVAILABLE = False

try:
    from .model_registry import ModelRegistry, get_model_registry

    MODEL_REGISTRY_AVAILABLE = True
except ImportError:
    MODEL_REGISTRY_AVAILABLE = False

# Export available components
__all__ = []

if EXPERIMENT_TRACKER_AVAILABLE:
    __all__.extend(["ExperimentTracker", "get_experiment_tracker"])

if MODEL_REGISTRY_AVAILABLE:
    __all__.extend(["ModelRegistry", "get_model_registry"])

# Status tracking
AVAILABLE_MODULES = {
    "experiment_tracker": EXPERIMENT_TRACKER_AVAILABLE,
    "model_registry": MODEL_REGISTRY_AVAILABLE,
}


def get_available_modules():
    """Get status of available MLOps modules."""
    return AVAILABLE_MODULES
