#!/usr/bin/env python3
"""
ML Models Package for Smart CloudOps AI
Anomaly detection using machine learning
"""

from .anomaly_detector import AnomalyDetector
from .data_processor import DataProcessor
from .model_trainer import AnomalyModelTrainer
from .inference_engine import AnomalyInferenceEngine

__version__ = "1.0.0"
__author__ = "Smart CloudOps AI Team"

__all__ = [
    'AnomalyDetector',
    'DataProcessor', 
    'AnomalyModelTrainer',
    'AnomalyInferenceEngine'
] 