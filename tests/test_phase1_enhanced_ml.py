"""
Tests for Phase 1: Enhanced Anomaly Detection Features
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.enhanced_ml_api import enhanced_ml_bp
from ml_models.anomaly_detector import AnomalyDetector


class TestEnhancedMLAPI:
    """Test cases for Enhanced ML API endpoints"""

    @pytest.fixture
    def app(self):
        """Create test Flask app"""
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(enhanced_ml_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    @pytest.fixture
    def mock_config(self):
        """Mock configuration with all features enabled"""
        return {
            "enable_enhanced_anomaly": True,
            "enable_multi_metric_correlation": True,
            "enable_failure_prediction": True,
            "enable_anomaly_explanation": True
        }

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_config:
            mock_config.return_value = {
                "enable_enhanced_anomaly": True,
                "enable_multi_metric_correlation": True,
                "enable_failure_prediction": True,
                "enable_anomaly_explanation": True
            }
            
            response = client.get('/api/v1/ml/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert data['service'] == 'enhanced_ml'
            assert 'features' in data
            assert 'detector_available' in data

    def test_multi_metric_anomaly_feature_disabled(self, client):
        """Test multi-metric anomaly endpoint when feature is disabled"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_config:
            mock_config.return_value = {"enable_multi_metric_correlation": False}
            
            response = client.post('/api/v1/ml/multi-metric-anomaly',
                                 json={"metrics": {"cpu": [{"value": 75, "timestamp": "2025-08-17T10:00:00Z"}]}})
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert data['status'] == 'feature_disabled'

    def test_multi_metric_anomaly_valid_request(self, client, mock_config):
        """Test multi-metric anomaly endpoint with valid data"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_cfg, \
             patch('app.enhanced_ml_api.anomaly_detector') as mock_detector:
            
            mock_cfg.return_value = mock_config
            mock_detector.detect_multi_metric_anomaly.return_value = {
                "status": "success",
                "anomalies": [],
                "correlation_matrix": {"cpu": {"memory": 0.8}}
            }
            
            test_metrics = {
                "cpu": [{"value": 75, "timestamp": "2025-08-17T10:00:00Z"}],
                "memory": [{"value": 80, "timestamp": "2025-08-17T10:00:00Z"}]
            }
            
            response = client.post('/api/v1/ml/multi-metric-anomaly',
                                 json={"metrics": test_metrics})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'

    def test_failure_prediction_valid_request(self, client, mock_config):
        """Test failure prediction endpoint with valid data"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_cfg, \
             patch('app.enhanced_ml_api.anomaly_detector') as mock_detector:
            
            mock_cfg.return_value = mock_config
            mock_detector.predict_failure_probability.return_value = {
                "status": "success",
                "failure_probability": 0.25,
                "confidence": 0.8
            }
            
            test_metrics = {
                "cpu_usage_percent": 85,
                "memory_usage_percent": 90,
                "disk_usage_percent": 75
            }
            
            response = client.post('/api/v1/ml/failure-prediction',
                                 json={"metrics": test_metrics, "time_horizon": 3600})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'failure_probability' in data

    def test_anomaly_explanation_valid_request(self, client, mock_config):
        """Test anomaly explanation endpoint with valid data"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_cfg, \
             patch('app.enhanced_ml_api.anomaly_detector') as mock_detector:
            
            mock_cfg.return_value = mock_config
            mock_detector.get_anomaly_explanation.return_value = {
                "status": "success",
                "explanation": "High CPU usage detected",
                "factors": []
            }
            
            test_anomaly = {
                "is_anomaly": True,
                "severity": "high",
                "anomaly_score": -0.15,
                "metrics": {"cpu_usage_percent": 95}
            }
            
            response = client.post('/api/v1/ml/anomaly-explanation',
                                 json={"anomaly_result": test_anomaly})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'

    def test_feature_status_endpoint(self, client, mock_config):
        """Test feature status endpoint"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_cfg:
            mock_cfg.return_value = mock_config
            
            response = client.get('/api/v1/ml/features/status')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'features' in data
            assert data['enabled_features'] == 4  # All features enabled

    def test_demo_endpoint(self, client, mock_config):
        """Test demo endpoint"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_cfg:
            mock_cfg.return_value = mock_config
            
            response = client.get('/api/v1/ml/demo')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'service' in data
            assert 'endpoints' in data
            assert 'capabilities' in data

    def test_missing_payload_validation(self, client, mock_config):
        """Test validation of missing payloads"""
        with patch('app.enhanced_ml_api.Config.from_env') as mock_cfg:
            mock_cfg.return_value = mock_config
            
            # Test multi-metric endpoint without payload
            response = client.post('/api/v1/ml/multi-metric-anomaly')
            assert response.status_code == 400
            
            # Test failure prediction without payload
            response = client.post('/api/v1/ml/failure-prediction')
            assert response.status_code == 400
            
            # Test anomaly explanation without payload
            response = client.post('/api/v1/ml/anomaly-explanation')
            assert response.status_code == 400


class TestEnhancedAnomalyDetector:
    """Test cases for Enhanced AnomalyDetector methods"""

    @pytest.fixture
    def detector(self):
        """Create AnomalyDetector instance"""
        return AnomalyDetector()

    def test_multi_metric_anomaly_detection(self, detector):
        """Test multi-metric correlation analysis"""
        metrics_dict = {
            'cpu': [
                {'value': 75, 'timestamp': '2025-08-17T10:00:00Z'},
                {'value': 80, 'timestamp': '2025-08-17T10:01:00Z'},
                {'value': 85, 'timestamp': '2025-08-17T10:02:00Z'}
            ],
            'memory': [
                {'value': 70, 'timestamp': '2025-08-17T10:00:00Z'},
                {'value': 75, 'timestamp': '2025-08-17T10:01:00Z'},
                {'value': 80, 'timestamp': '2025-08-17T10:02:00Z'}
            ]
        }
        
        result = detector.detect_multi_metric_anomaly(metrics_dict)
        
        assert result['status'] == 'success'
        assert 'correlation_matrix' in result
        assert 'anomalies' in result
        assert result['metrics_analyzed'] == ['cpu', 'memory']

    def test_multi_metric_insufficient_data(self, detector):
        """Test multi-metric analysis with insufficient data"""
        metrics_dict = {
            'cpu': [{'value': 75, 'timestamp': '2025-08-17T10:00:00Z'}]
        }
        
        result = detector.detect_multi_metric_anomaly(metrics_dict)
        
        assert result['status'] == 'insufficient_data'
        assert 'Need at least 2 metric types' in result['message']

    def test_failure_prediction_untrained_model(self, detector):
        """Test failure prediction with untrained model"""
        metrics = {
            'cpu_usage_percent': 85,
            'memory_usage_percent': 90,
            'disk_usage_percent': 75
        }
        
        result = detector.predict_failure_probability(metrics, 3600)
        
        assert result['status'] == 'success'
        assert 'failure_probability' in result
        assert 'confidence' in result
        assert result['method'] == 'rule_based'

    def test_failure_prediction_high_risk_scenario(self, detector):
        """Test failure prediction with high-risk metrics"""
        metrics = {
            'cpu_usage_percent': 98,
            'memory_usage_percent': 97,
            'disk_usage_percent': 96
        }
        
        result = detector.predict_failure_probability(metrics, 3600)
        
        assert result['status'] == 'success'
        assert result['failure_probability'] > 0.5  # Should be high
        assert len(result['risk_factors']) > 0

    def test_anomaly_explanation_not_anomaly(self, detector):
        """Test anomaly explanation for non-anomalous data"""
        anomaly_result = {
            'is_anomaly': False,
            'severity': 'low'
        }
        
        result = detector.get_anomaly_explanation(anomaly_result)
        
        assert result['status'] == 'not_anomaly'
        assert 'No anomaly detected' in result['explanation']

    def test_anomaly_explanation_with_factors(self, detector):
        """Test anomaly explanation with contributing factors"""
        anomaly_result = {
            'is_anomaly': True,
            'severity': 'high',
            'anomaly_score': -0.25,
            'metrics': {
                'cpu_usage_percent': 96,
                'memory_usage_percent': 92,
                'disk_usage_percent': 88
            }
        }
        
        result = detector.get_anomaly_explanation(anomaly_result)
        
        assert result['status'] == 'success'
        assert len(result['contributing_factors']) > 0
        assert 'recommendations' in result
        assert result['severity'] == 'high'

    def test_rule_based_failure_prediction(self, detector):
        """Test rule-based failure prediction logic"""
        # Test critical scenario
        metrics_critical = {
            'cpu_usage_percent': 98,
            'memory_usage_percent': 97,
            'disk_usage_percent': 96
        }
        
        result = detector._rule_based_failure_prediction(metrics_critical, 3600)
        assert result['failure_probability'] > 0.8
        
        # Test normal scenario
        metrics_normal = {
            'cpu_usage_percent': 50,
            'memory_usage_percent': 60,
            'disk_usage_percent': 70
        }
        
        result = detector._rule_based_failure_prediction(metrics_normal, 3600)
        assert result['failure_probability'] < 0.3

    def test_recommendation_generation(self, detector):
        """Test recommendation generation for different factors"""
        factors = [
            {'metric': 'cpu_usage_percent', 'impact': 'critical'},
            {'metric': 'memory_usage_percent', 'impact': 'high'},
            {'metric': 'disk_usage_percent', 'impact': 'critical'}
        ]
        
        recommendations = detector._generate_anomaly_recommendations(factors)
        
        assert len(recommendations) == len(factors)
        assert any('CPU' in rec for rec in recommendations)
        assert any('memory' in rec for rec in recommendations)
        assert any('disk' in rec for rec in recommendations)
