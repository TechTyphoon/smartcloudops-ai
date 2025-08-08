#!/usr/bin/env python3
"""
Tests for ML anomaly detection endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch
from app.main import app


class TestMLEndpoints:
    """Test ML anomaly detection endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def mock_anomaly_detector(self):
        """Mock anomaly detector."""
        with patch('app.main.anomaly_detector') as mock:
            mock.detect_anomaly.return_value = {
                'is_anomaly': True,
                'score': 0.85,
                'severity': 'high',
                'explanation': 'High CPU usage detected'
            }
            mock.batch_detect.return_value = [
                {'is_anomaly': True, 'score': 0.85, 'severity': 'high'},
                {'is_anomaly': False, 'score': 0.15, 'severity': 'normal'}
            ]
            mock.get_system_status.return_value = {
                'status': 'operational',
                'model_loaded': True,
                'last_training': '2024-01-01T00:00:00Z'
            }
            mock.train_model.return_value = {
                'status': 'success',
                'f1_score': 0.95,
                'training_time': 120.5
            }
            yield mock
    
    def test_detect_anomaly_success(self, client, mock_anomaly_detector):
        """Test successful anomaly detection."""
        data = {
            'metrics': {
                'cpu_usage_avg': 85.0,
                'memory_usage_pct': 75.0,
                'disk_usage_pct': 60.0
            }
        }
        
        response = client.post('/anomaly', json=data)
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['is_anomaly'] == True
        assert result['severity'] == 'high'
        mock_anomaly_detector.detect_anomaly.assert_called_once()
    
    def test_detect_anomaly_no_data(self, client):
        """Test anomaly detection with no data."""
        response = client.post('/anomaly', json={})
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_detect_anomaly_no_metrics(self, client):
        """Test anomaly detection with no metrics."""
        response = client.post('/anomaly', json={'data': {}})
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_batch_detect_anomaly_success(self, client, mock_anomaly_detector):
        """Test successful batch anomaly detection."""
        data = {
            'metrics_batch': [
                {'cpu_usage_avg': 85.0, 'memory_usage_pct': 75.0},
                {'cpu_usage_avg': 45.0, 'memory_usage_pct': 55.0}
            ]
        }
        
        response = client.post('/anomaly/batch', json=data)
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'results' in result
        assert len(result['results']) == 2
        assert result['count'] == 2
        mock_anomaly_detector.batch_detect.assert_called_once()
    
    def test_batch_detect_anomaly_no_data(self, client):
        """Test batch anomaly detection with no data."""
        response = client.post('/anomaly/batch', json={})
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_ml_status_success(self, client, mock_anomaly_detector):
        """Test successful ML status retrieval."""
        response = client.get('/anomaly/status')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'operational'
        assert result['model_loaded'] == True
        mock_anomaly_detector.get_system_status.assert_called_once()
    
    def test_train_model_success(self, client, mock_anomaly_detector):
        """Test successful model training."""
        data = {'force_retrain': True}
        
        response = client.post('/anomaly/train', json=data)
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'success'
        assert result['f1_score'] == 0.95
        mock_anomaly_detector.train_model.assert_called_once_with(force_retrain=True)
    
    def test_train_model_default(self, client, mock_anomaly_detector):
        """Test model training with default parameters."""
        response = client.post('/anomaly/train', json={})
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'success'
        mock_anomaly_detector.train_model.assert_called_once_with(force_retrain=False)
    
    @patch('app.main.ML_AVAILABLE', False)
    def test_ml_endpoints_disabled(self, client):
        """Test ML endpoints when ML is not available."""
        endpoints = ['/anomaly', '/anomaly/batch', '/anomaly/status', '/anomaly/train']
        
        for endpoint in endpoints:
            if endpoint in ['/anomaly', '/anomaly/batch', '/anomaly/train']:
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 503
            result = json.loads(response.data)
            assert 'error' in result
            assert 'not available' in result['error']
    
    def test_ml_endpoints_error_handling(self, client, mock_anomaly_detector):
        """Test error handling in ML endpoints."""
        # Mock exception
        mock_anomaly_detector.detect_anomaly.side_effect = Exception("Test error")
        
        data = {'metrics': {'cpu_usage_avg': 85.0}}
        response = client.post('/anomaly', json=data)
        
        assert response.status_code == 500
        result = json.loads(response.data)
        assert 'error' in result 