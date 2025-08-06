#!/usr/bin/env python3
"""
Production Enhancements for ML Anomaly Detection
Real-world implementation with no synthetic data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProductionAnomalyDetector:
    """Production-ready anomaly detection with ensemble methods."""
    
    def __init__(self):
        self.models = {
            'isolation_forest': IsolationForest(
                contamination=0.1,
                n_estimators=200,  # Increased for robustness
                random_state=42
            ),
            'local_outlier_factor': LocalOutlierFactor(
                contamination=0.1,
                n_neighbors=20,
                novelty=True
            ),
            'one_class_svm': OneClassSVM(
                kernel='rbf',
                nu=0.1,
                gamma='scale'
            )
        }
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.ensemble_weights = None
        
    def extract_real_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract production-ready features from real data."""
        features = df.copy()
        
        # Basic metrics
        basic_cols = ['cpu_usage_avg', 'cpu_usage_max', 'memory_usage_pct', 
                     'disk_usage_pct', 'network_bytes_total', 'request_rate', 
                     'response_time_p95']
        
        # Advanced time-series features
        for col in basic_cols:
            if col in features.columns:
                # Rolling statistics with adaptive windows
                features[f'{col}_rolling_mean_5m'] = features[col].rolling(window=5, min_periods=1).mean()
                features[f'{col}_rolling_mean_15m'] = features[col].rolling(window=15, min_periods=1).mean()
                features[f'{col}_rolling_std_5m'] = features[col].rolling(window=5, min_periods=1).std()
                features[f'{col}_rolling_max_5m'] = features[col].rolling(window=5, min_periods=1).max()
                
                # Rate of change
                features[f'{col}_rate'] = features[col].diff().fillna(0)
                features[f'{col}_acceleration'] = features[f'{col}_rate'].diff().fillna(0)
                
                # Percentile-based features
                features[f'{col}_percentile_75'] = features[col].rolling(window=20, min_periods=1).quantile(0.75)
                features[f'{col}_percentile_25'] = features[col].rolling(window=20, min_periods=1).quantile(0.25)
                features[f'{col}_iqr'] = features[f'{col}_percentile_75'] - features[f'{col}_percentile_25']
        
        # Cross-correlation features
        if 'cpu_usage_avg' in features.columns and 'memory_usage_pct' in features.columns:
            features['cpu_memory_ratio'] = features['cpu_usage_avg'] / (features['memory_usage_pct'] + 1e-6)
            features['cpu_memory_correlation'] = features['cpu_usage_avg'].rolling(10).corr(features['memory_usage_pct'])
        
        # System health indicators
        if 'response_time_p95' in features.columns and 'request_rate' in features.columns:
            features['throughput_efficiency'] = features['request_rate'] / (features['response_time_p95'] + 1e-6)
        
        # Time-based features (if datetime index)
        if isinstance(features.index, pd.DatetimeIndex):
            features['hour'] = features.index.hour
            features['day_of_week'] = features.index.dayofweek
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
            features['is_business_hours'] = ((features['hour'] >= 9) & (features['hour'] <= 17)).astype(int)
        
        # Remove any remaining NaN values
        features = features.fillna(method='ffill').fillna(method='bfill')
        
        return features
    
    def train_ensemble(self, real_data: pd.DataFrame) -> Dict:
        """Train ensemble model on real data."""
        logger.info("Training production ensemble model on real data...")
        
        # Extract features
        feature_data = self.extract_real_features(real_data)
        
        # Select numeric features
        numeric_cols = feature_data.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['hour', 'day_of_week', 'is_weekend', 'is_business_hours']
        self.feature_columns = [col for col in numeric_cols if col not in exclude_cols]
        
        if len(self.feature_columns) < 10:
            raise ValueError(f"Insufficient features: {len(self.feature_columns)}")
        
        feature_matrix = feature_data[self.feature_columns]
        
        # Scale features
        feature_matrix_scaled = self.scaler.fit_transform(feature_matrix)
        
        # Train individual models
        model_predictions = {}
        for name, model in self.models.items():
            try:
                if name == 'local_outlier_factor':
                    # LOF needs to be fitted differently
                    model.fit(feature_matrix_scaled)
                    predictions = model.predict(feature_matrix_scaled)
                else:
                    model.fit(feature_matrix_scaled)
                    predictions = model.predict(feature_matrix_scaled)
                
                model_predictions[name] = predictions
                logger.info(f"Trained {name} successfully")
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue
        
        # Calculate ensemble weights based on model agreement
        self.ensemble_weights = self._calculate_ensemble_weights(model_predictions)
        
        # Save models
        self._save_models()
        
        return {
            'status': 'success',
            'models_trained': list(model_predictions.keys()),
            'feature_count': len(self.feature_columns),
            'ensemble_weights': self.ensemble_weights,
            'data_shape': real_data.shape
        }
    
    def _calculate_ensemble_weights(self, predictions: Dict) -> Dict:
        """Calculate ensemble weights based on model agreement."""
        weights = {}
        total_models = len(predictions)
        
        for name in predictions.keys():
            # Equal weights for now, can be optimized based on performance
            weights[name] = 1.0 / total_models
        
        return weights
    
    def detect_anomalies_production(self, metrics: Dict) -> Dict:
        """Production anomaly detection with ensemble voting."""
        try:
            # Prepare features
            feature_vector = self._prepare_feature_vector(metrics)
            if feature_vector is None:
                return {'status': 'error', 'message': 'Invalid feature data'}
            
            # Scale features
            feature_scaled = self.scaler.transform([feature_vector])
            
            # Get predictions from all models
            predictions = {}
            scores = {}
            
            for name, model in self.models.items():
                try:
                    if name == 'local_outlier_factor':
                        pred = model.predict(feature_scaled)[0]
                        score = model.score_samples(feature_scaled)[0]
                    else:
                        pred = model.predict(feature_scaled)[0]
                        score = model.decision_function(feature_scaled)[0]
                    
                    predictions[name] = pred
                    scores[name] = score
                    
                except Exception as e:
                    logger.error(f"Error with {name}: {e}")
                    continue
            
            # Ensemble voting
            if not predictions:
                return {'status': 'error', 'message': 'No models available'}
            
            # Weighted ensemble decision
            ensemble_score = 0
            total_weight = 0
            
            for name, pred in predictions.items():
                weight = self.ensemble_weights.get(name, 0)
                ensemble_score += pred * weight
                total_weight += weight
            
            if total_weight > 0:
                ensemble_score /= total_weight
            
            # Determine final prediction
            is_anomaly = ensemble_score < 0  # Negative scores indicate anomalies
            
            # Calculate confidence based on model agreement
            anomaly_votes = sum(1 for p in predictions.values() if p < 0)
            confidence = anomaly_votes / len(predictions) if predictions else 0
            
            # Generate explanation
            explanation = self._generate_production_explanation(metrics, predictions, confidence)
            
            return {
                'status': 'success',
                'is_anomaly': bool(is_anomaly),
                'confidence': confidence,
                'ensemble_score': ensemble_score,
                'individual_predictions': predictions,
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in production anomaly detection: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _prepare_feature_vector(self, metrics: Dict) -> np.ndarray:
        """Prepare feature vector from metrics."""
        feature_vector = []
        
        for feature in self.feature_columns:
            if feature in metrics:
                value = metrics[feature]
                if pd.isna(value) or np.isinf(value):
                    value = 0.0
                feature_vector.append(float(value))
            else:
                # Use default value for missing features
                feature_vector.append(0.0)
        
        return np.array(feature_vector)
    
    def _generate_production_explanation(self, metrics: Dict, predictions: Dict, confidence: float) -> str:
        """Generate production-ready explanation."""
        if confidence == 0:
            return "No anomalies detected. System metrics are within normal ranges."
        
        # Count model agreements
        anomaly_models = [name for name, pred in predictions.items() if pred < 0]
        normal_models = [name for name, pred in predictions.items() if pred >= 0]
        
        explanation_parts = [
            f"Anomaly detected with {confidence:.1%} confidence",
            f"Models detecting anomaly: {len(anomaly_models)}/{len(predictions)}"
        ]
        
        # Add specific model insights
        if anomaly_models:
            explanation_parts.append(f"Anomaly detected by: {', '.join(anomaly_models)}")
        
        # Add metric insights
        contributing_factors = []
        for metric, value in metrics.items():
            if 'cpu' in metric and value > 80:
                contributing_factors.append("High CPU usage")
            elif 'memory' in metric and value > 85:
                contributing_factors.append("High memory usage")
            elif 'disk' in metric and value > 90:
                contributing_factors.append("High disk usage")
            elif 'response_time' in metric and value > 1.0:
                contributing_factors.append("High response time")
        
        if contributing_factors:
            explanation_parts.append(f"Contributing factors: {', '.join(set(contributing_factors))}")
        
        return ". ".join(explanation_parts)
    
    def _save_models(self):
        """Save production models."""
        try:
            # Save individual models
            for name, model in self.models.items():
                joblib.dump(model, f'ml_models/models/{name}_production.pkl')
            
            # Save scaler and metadata
            joblib.dump(self.scaler, 'ml_models/models/scaler_production.pkl')
            joblib.dump(self.feature_columns, 'ml_models/models/features_production.pkl')
            joblib.dump(self.ensemble_weights, 'ml_models/models/ensemble_weights.pkl')
            
            logger.info("Production models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving production models: {e}")

# Production data collection requirements
PRODUCTION_DATA_REQUIREMENTS = {
    'minimum_days': 7,
    'target_days': 14,
    'minimum_metrics': 100000,
    'required_features': [
        'cpu_usage_avg', 'cpu_usage_max', 'memory_usage_pct',
        'disk_usage_pct', 'network_bytes_total', 'request_rate',
        'response_time_p95'
    ],
    'data_quality_checks': [
        'no_missing_values',
        'no_infinite_values',
        'reasonable_value_ranges',
        'consistent_timestamps'
    ]
} 