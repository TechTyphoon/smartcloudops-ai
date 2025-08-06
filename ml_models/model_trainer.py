#!/usr/bin/env python3
"""
Model Trainer for ML Anomaly Detection
Handles model training, validation, and persistence
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
import joblib
import yaml
import os
import logging
from typing import Dict, Tuple, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AnomalyModelTrainer:
    """Handles training and validation of anomaly detection models."""
    
    def __init__(self, config_path: str = "ml_models/config.yaml"):
        """Initialize model trainer with configuration."""
        self.config = self._load_config(config_path)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.training_history = []
        
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
            'model': {
                'type': 'isolation_forest',
                'contamination': 0.1,
                'n_estimators': 100,
                'random_state': 42
            },
            'training': {
                'min_f1_score': 0.85,
                'validation_split': 0.2
            }
        }
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training by selecting relevant columns."""
        # Select numeric columns for training
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove time-based features that are not useful for anomaly detection
        exclude_cols = ['hour', 'day_of_week', 'is_weekend']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # If we have time-based features, exclude them
        if 'hour' in numeric_cols:
            feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Ensure we have enough features
        if len(feature_cols) < 2:
            logger.warning(f"Only {len(feature_cols)} features available, using all numeric columns")
            feature_cols = numeric_cols
        
        self.feature_columns = feature_cols
        logger.info(f"Selected {len(feature_cols)} features for training: {feature_cols}")
        
        return df[feature_cols]
    
    def create_model(self) -> IsolationForest:
        """Create and configure the anomaly detection model."""
        model_config = self.config['model']
        
        model = IsolationForest(
            contamination=model_config.get('contamination', 0.1),
            n_estimators=model_config.get('n_estimators', 100),
            random_state=model_config.get('random_state', 42),
            max_samples=model_config.get('max_samples', 'auto')
        )
        
        logger.info(f"Created Isolation Forest model with contamination={model_config.get('contamination', 0.1)}")
        return model
    
    def train(self, df: pd.DataFrame) -> Dict:
        """Train the anomaly detection model."""
        try:
            logger.info("Starting model training...")
            
            # Prepare features
            feature_df = self.prepare_features(df)
            
            # Check data quality
            if len(feature_df) < 50:
                raise ValueError(f"Insufficient data for training: {len(feature_df)} samples")
            
            # Split data for validation
            validation_split = self.config['training'].get('validation_split', 0.2)
            train_data, val_data = train_test_split(
                feature_df, 
                test_size=validation_split, 
                random_state=42
            )
            
            logger.info(f"Training data shape: {train_data.shape}, Validation data shape: {val_data.shape}")
            
            # Scale features
            train_scaled = self.scaler.fit_transform(train_data)
            val_scaled = self.scaler.transform(val_data)
            
            # Create and train model
            self.model = self.create_model()
            self.model.fit(train_scaled)
            
            # Validate model
            validation_results = self.validate_model(val_scaled, val_data)
            
            # Store training history
            training_record = {
                'timestamp': datetime.now().isoformat(),
                'data_shape': df.shape,
                'feature_count': len(self.feature_columns),
                'validation_results': validation_results,
                'model_params': self.model.get_params()
            }
            self.training_history.append(training_record)
            
            logger.info(f"Model training completed. F1 Score: {validation_results['f1_score']:.3f}")
            return {
                'status': 'success',
                'f1_score': validation_results['f1_score'],
                'precision': validation_results['precision'],
                'recall': validation_results['recall'],
                'total_samples': validation_results['total_samples'],
                'anomaly_samples': validation_results['anomaly_samples']
            }
            
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {
                'status': 'failed',
                'reason': str(e)
            }
    
    def validate_model(self, val_data_scaled: np.ndarray, val_data_raw: pd.DataFrame) -> Dict:
        """Validate the trained model using synthetic anomalies."""
        try:
            # Generate synthetic anomalies for validation
            synthetic_anomalies = self._generate_synthetic_anomalies(val_data_raw)
            
            # Combine normal and anomalous data
            combined_data = np.vstack([val_data_scaled, synthetic_anomalies])
            
            # Create labels (0 for normal, 1 for anomaly)
            labels = np.concatenate([
                np.zeros(len(val_data_scaled)),  # Normal data
                np.ones(len(synthetic_anomalies))  # Anomalous data
            ])
            
            # Make predictions
            predictions = self.model.predict(combined_data)
            # Convert predictions: -1 (anomaly) -> 1, 1 (normal) -> 0
            predictions = (predictions == -1).astype(int)
            
            # Calculate metrics
            f1 = f1_score(labels, predictions)
            precision = precision_score(labels, predictions)
            recall = recall_score(labels, predictions)
            
            results = {
                'f1_score': f1,
                'precision': precision,
                'recall': recall,
                'total_samples': len(combined_data),
                'anomaly_samples': len(synthetic_anomalies)
            }
            
            logger.info(f"Validation results - F1: {f1:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error in model validation: {e}")
            return {'f1_score': 0.0, 'precision': 0.0, 'recall': 0.0}
    
    def _generate_synthetic_anomalies(self, normal_data: pd.DataFrame) -> np.ndarray:
        """Generate synthetic anomalies for validation."""
        # Create anomalies by adding noise and scaling
        anomaly_data = normal_data.copy()
        
        # Add random noise
        noise_factor = 2.0
        noise = np.random.normal(0, noise_factor, anomaly_data.shape)
        anomaly_data += noise
        
        # Scale some features to create more extreme anomalies
        scale_factors = np.random.uniform(2.0, 5.0, len(anomaly_data.columns))
        for i, col in enumerate(anomaly_data.columns):
            anomaly_data[col] *= scale_factors[i]
        
        # Scale using the same scaler
        return self.scaler.transform(anomaly_data)
    
    def save_model(self, model_path: str = "ml_models/models/anomaly_model.pkl") -> bool:
        """Save the trained model and scaler."""
        try:
            if self.model is None:
                raise ValueError("No trained model to save")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save model
            joblib.dump(self.model, model_path)
            
            # Save scaler
            scaler_path = model_path.replace('anomaly_model.pkl', 'scaler.pkl')
            joblib.dump(self.scaler, scaler_path)
            
            # Save feature columns
            features_path = model_path.replace('anomaly_model.pkl', 'features.pkl')
            joblib.dump(self.feature_columns, features_path)
            
            # Save training history
            history_path = model_path.replace('anomaly_model.pkl', 'training_history.pkl')
            joblib.dump(self.training_history, history_path)
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Scaler saved to {scaler_path}")
            logger.info(f"Features saved to {features_path}")
            logger.info(f"Training history saved to {history_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, model_path: str = "ml_models/models/anomaly_model.pkl") -> bool:
        """Load a trained model and scaler."""
        try:
            # Load model
            self.model = joblib.load(model_path)
            
            # Load scaler
            scaler_path = model_path.replace('anomaly_model.pkl', 'scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            
            # Load feature columns
            features_path = model_path.replace('anomaly_model.pkl', 'features.pkl')
            self.feature_columns = joblib.load(features_path)
            
            # Load training history
            history_path = model_path.replace('anomaly_model.pkl', 'training_history.pkl')
            self.training_history = joblib.load(history_path)
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Feature columns: {self.feature_columns}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        if self.model is None:
            return {'status': 'No model loaded'}
        
        return {
            'model_type': type(self.model).__name__,
            'feature_count': len(self.feature_columns),
            'feature_columns': self.feature_columns,
            'model_params': self.model.get_params(),
            'training_history': self.training_history[-1] if self.training_history else None
        }
    
    def meets_quality_threshold(self, validation_results: Dict) -> bool:
        """Check if model meets quality threshold."""
        min_f1_score = self.config['training'].get('min_f1_score', 0.85)
        return validation_results['f1_score'] >= min_f1_score 