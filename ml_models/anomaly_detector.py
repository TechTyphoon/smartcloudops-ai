#!/usr/bin/env python3
"""
Main Anomaly Detector for ML Anomaly Detection
Orchestrates data processing, model training, and inference
"""

import pandas as pd
import numpy as np
import logging
import yaml
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import time

from .data_processor import DataProcessor
from .model_trainer import AnomalyModelTrainer
from .inference_engine import AnomalyInferenceEngine

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Main class for anomaly detection system."""
    
    def __init__(self, config_path: str = "ml_models/config.yaml"):
        """Initialize the anomaly detection system."""
        self.config = self._load_config(config_path)
        self.data_processor = DataProcessor(config_path)
        self.model_trainer = AnomalyModelTrainer(config_path)
        self.inference_engine = None
        self.model_path = "ml_models/models/anomaly_model.pkl"
        self.is_initialized = False
        
        logger.info("Anomaly detector initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is missing."""
        return {
            'data': {
                'lookback_hours': 168,
                'feature_window': 60
            },
            'training': {
                'min_f1_score': 0.85
            }
        }
    
    def train_model(self, force_retrain: bool = False, data: pd.DataFrame = None) -> Dict:
        """
        Train the anomaly detection model.
        
        Args:
            force_retrain: Force retraining even if model exists
            data: Optional DataFrame with training data (if None, will extract from Prometheus)
            
        Returns:
            Dictionary with training results
        """
        try:
            # Check if model already exists and is recent enough
            if not force_retrain and self._is_model_recent():
                logger.info("Recent model exists, skipping training")
                return {'status': 'skipped', 'reason': 'Recent model exists'}
            
            logger.info("Starting model training process...")
            
            # Use provided data or extract from Prometheus
            if data is not None:
                logger.info("Using provided training data")
                raw_data = data
            else:
                # Extract training data
                end_time = datetime.now()
                lookback_hours = self.config['data'].get('lookback_hours', 168)
                start_time = end_time - timedelta(hours=lookback_hours)
                
                logger.info(f"Extracting data from {start_time} to {end_time}")
                raw_data = self.data_processor.extract_metrics(start_time, end_time)
                
                if raw_data is None or len(raw_data) == 0:
                    raise ValueError("No data available for training")
            
            # Preprocess data
            logger.info("Preprocessing data...")
            processed_data = self.data_processor.preprocess_data(raw_data)
            
            # Validate data
            is_valid, issues = self.data_processor.validate_data(processed_data)
            if not is_valid:
                logger.warning(f"Data validation issues: {issues}")
            
            # Save training data
            self.data_processor.save_data(processed_data, 'training_data.csv')
            
            # Train model
            logger.info("Training anomaly detection model...")
            validation_results = self.model_trainer.train(processed_data)
            
            # Check if model meets quality threshold
            if not self.model_trainer.meets_quality_threshold(validation_results):
                logger.warning(f"Model quality below threshold: F1={validation_results['f1_score']:.3f}")
                return {
                    'status': 'failed',
                    'reason': 'Model quality below threshold',
                    'f1_score': validation_results['f1_score']
                }
            
            # Save model
            if self.model_trainer.save_model(self.model_path):
                logger.info("Model saved successfully")
                
                # Initialize inference engine
                self.inference_engine = AnomalyInferenceEngine(self.model_path)
                self.is_initialized = True
                
                return {
                    'status': 'success',
                    'f1_score': validation_results['f1_score'],
                    'precision': validation_results['precision'],
                    'recall': validation_results['recall'],
                    'data_shape': processed_data.shape,
                    'feature_count': len(self.model_trainer.feature_columns)
                }
            else:
                return {'status': 'failed', 'reason': 'Failed to save model'}
                
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {'status': 'failed', 'reason': str(e)}
    
    def _is_model_recent(self) -> bool:
        """Check if the model file exists and is recent enough."""
        try:
            if not os.path.exists(self.model_path):
                return False
            
            # Check file modification time
            file_time = datetime.fromtimestamp(os.path.getmtime(self.model_path))
            current_time = datetime.now()
            
            # Check if model is less than 7 days old
            retrain_hours = self.config.get('training', {}).get('retrain_frequency_hours', 168)
            return (current_time - file_time).total_seconds() < (retrain_hours * 3600)
            
        except Exception as e:
            logger.error(f"Error checking model age: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load the trained model for inference."""
        try:
            if not os.path.exists(self.model_path):
                logger.warning("Model file not found")
                return False
            
            self.inference_engine = AnomalyInferenceEngine(self.model_path)
            self.is_initialized = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def detect_anomaly(self, metrics_data: Dict) -> Dict:
        """
        Detect anomalies in real-time metrics.
        
        Args:
            metrics_data: Dictionary containing metric values
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            if not self.is_initialized:
                # Try to load model if not initialized
                if not self.load_model():
                    return {
                        'status': 'error',
                        'message': 'Model not initialized. Please train or load a model first.'
                    }
            
            # Perform anomaly detection
            is_anomaly, severity_score, explanation = self.inference_engine.detect_anomalies(metrics_data)
            
            return {
                'status': 'success',
                'is_anomaly': is_anomaly,
                'severity_score': severity_score,
                'explanation': explanation,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics_data
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {
                'status': 'error',
                'message': f'Error during detection: {str(e)}'
            }
    
    def batch_detect(self, metrics_batch: List[Dict]) -> List[Dict]:
        """
        Detect anomalies in a batch of metrics.
        
        Args:
            metrics_batch: List of dictionaries containing metric values
            
        Returns:
            List of dictionaries with anomaly detection results
        """
        try:
            if not self.is_initialized:
                if not self.load_model():
                    return [{'status': 'error', 'message': 'Model not initialized'} for _ in metrics_batch]
            
            results = []
            for metrics in metrics_batch:
                result = self.detect_anomaly(metrics)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch detection: {e}")
            return [{'status': 'error', 'message': str(e)} for _ in metrics_batch]
    
    def get_system_status(self) -> Dict:
        """Get the current status of the anomaly detection system."""
        status = {
            'initialized': self.is_initialized,
            'model_path': self.model_path,
            'model_exists': os.path.exists(self.model_path),
            'config': self.config
        }
        
        if self.is_initialized and self.inference_engine:
            status['model_info'] = self.inference_engine.get_model_info()
        
        if self.model_trainer.model:
            status['training_info'] = self.model_trainer.get_model_info()
        
        return status
    
    def get_training_history(self) -> List[Dict]:
        """Get the training history."""
        if hasattr(self.model_trainer, 'training_history'):
            return self.model_trainer.training_history
        return []
    
    def retrain_model(self) -> Dict:
        """Force retrain the model."""
        return self.train_model(force_retrain=True)
    
    def clear_cache(self) -> None:
        """Clear the inference cache."""
        if self.inference_engine:
            self.inference_engine.clear_cache()
            logger.info("Cache cleared")
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance information."""
        if not self.is_initialized or not self.inference_engine:
            return {'error': 'Model not initialized'}
        
        try:
            feature_columns = self.inference_engine.feature_columns
            return {
                'feature_count': len(feature_columns),
                'features': feature_columns
            }
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {'error': str(e)}
    
    def validate_metrics(self, metrics_data: Dict) -> Tuple[bool, List[str]]:
        """Validate input metrics data."""
        issues = []
        
        # Check for required metrics
        required_metrics = ['cpu_usage_avg', 'memory_usage_pct']
        for metric in required_metrics:
            if metric not in metrics_data:
                issues.append(f"Missing required metric: {metric}")
        
        # Check for valid numeric values
        for key, value in metrics_data.items():
            if not isinstance(value, (int, float)):
                issues.append(f"Non-numeric value for {key}: {value}")
            elif pd.isna(value) or np.isinf(value):
                issues.append(f"Invalid value for {key}: {value}")
        
        return len(issues) == 0, issues 