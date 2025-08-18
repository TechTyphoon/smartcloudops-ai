#!/usr/bin/env python3
"""
Tests for the refactored SmartCloudOps.AI application
Comprehensive test suite for modular architecture
"""

import json
import os
import pytest
import tempfile
from unittest.mock import Mock, patch

from app.main_refactored import create_app, _get_memory_usage
from app.security import validate_string_input, validate_json_input
from app.monitoring import metrics


class TestRefactoredApplication:
    """Test the refactored Flask application"""
    
    @pytest.fixture
    def app(self):
        """Create test application"""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'testing',
            'LOG_LEVEL': 'DEBUG',
            'LOG_JSON': 'false'
        }):
            app = create_app()
            app.config['TESTING'] = True
            return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'components' in data
        assert 'metrics' in data
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/plain; version=0.0.4; charset=utf-8'
    
    def test_demo_endpoint(self, client):
        """Test demo endpoint"""
        response = client.get('/demo')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['message'] == 'SmartCloudOps.AI is running!'
        assert data['version'] == '3.1.0'
        assert 'features' in data
        assert 'endpoints' in data
    
    def test_anomaly_endpoint_success(self, client):
        """Test anomaly detection endpoint with valid data"""
        test_data = {
            "metrics": {
                "cpu_usage": 85.0,
                "memory_usage": 70.0,
                "disk_usage": 60.0
            }
        }
        
        with patch('app.main_refactored.ML_AVAILABLE', True):
            with patch('app.main_refactored.app.anomaly_detector') as mock_detector:
                mock_detector.detect_anomaly.return_value = {
                    "is_anomaly": True,
                    "severity": "medium",
                    "confidence": 0.85
                }
                
                response = client.post('/anomaly', 
                                     data=json.dumps(test_data),
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'success'
                assert 'data' in data
    
    def test_anomaly_endpoint_invalid_input(self, client):
        """Test anomaly detection endpoint with invalid input"""
        # Test missing data
        response = client.post('/anomaly')
        assert response.status_code == 400
        
        # Test empty data
        response = client.post('/anomaly', 
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
        
        # Test missing metrics
        response = client.post('/anomaly', 
                             data=json.dumps({"other": "data"}),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_query_endpoint_success(self, client):
        """Test query processing endpoint with valid data"""
        test_data = {"query": "What's the CPU usage?"}
        
        with patch('app.main_refactored.CHATOPS_AVAILABLE', True):
            with patch('app.main_refactored.app.ai_handler') as mock_handler:
                mock_handler.process_query.return_value = {
                    "response": "CPU usage is 45%",
                    "model": "gpt-3.5-turbo"
                }
                
                response = client.post('/query',
                                     data=json.dumps(test_data),
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'success'
                assert 'data' in data
    
    def test_query_endpoint_invalid_input(self, client):
        """Test query processing endpoint with invalid input"""
        # Test missing data
        response = client.post('/query')
        assert response.status_code == 400
        
        # Test empty query
        response = client.post('/query',
                             data=json.dumps({"query": ""}),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_404_error_handler(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Endpoint not found' in data['message']
    
    def test_500_error_handler(self, client):
        """Test 500 error handling"""
        # This would require mocking an endpoint to raise an exception
        # For now, we'll test the error handler structure
        with patch('app.main_refactored.log_error') as mock_log:
            # Simulate an error by patching the health endpoint
            with patch('app.main_refactored.db_manager.test_connection', side_effect=Exception("Test error")):
                response = client.get('/health')
                assert response.status_code == 500
                
                data = response.get_json()
                assert data['status'] == 'error'
                assert 'Internal server error' in data['message']


class TestSecurityValidation:
    """Test security validation functions"""
    
    def test_validate_string_input_valid(self):
        """Test string validation with valid input"""
        result = validate_string_input("valid string")
        assert result == "valid string"
    
    def test_validate_string_input_empty_allowed(self):
        """Test string validation with empty string allowed"""
        result = validate_string_input("", allow_empty=True)
        assert result == ""
    
    def test_validate_string_input_empty_not_allowed(self):
        """Test string validation with empty string not allowed"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_string_input("")
    
    def test_validate_string_input_too_long(self):
        """Test string validation with too long input"""
        long_string = "a" * 1001
        with pytest.raises(ValueError, match="too long"):
            validate_string_input(long_string, max_length=1000)
    
    def test_validate_string_input_xss_attempt(self):
        """Test string validation with XSS attempt"""
        xss_string = "<script>alert('xss')</script>"
        with pytest.raises(ValueError, match="malicious input"):
            validate_string_input(xss_string)
    
    def test_validate_string_input_sql_injection(self):
        """Test string validation with SQL injection attempt"""
        sql_string = "'; DROP TABLE users; --"
        with pytest.raises(ValueError, match="SQL injection"):
            validate_string_input(sql_string)
    
    def test_validate_json_input_valid(self):
        """Test JSON validation with valid input"""
        valid_json = {"key": "value", "number": 42}
        result = validate_json_input(valid_json)
        assert result == valid_json
    
    def test_validate_json_input_not_dict(self):
        """Test JSON validation with non-dict input"""
        with pytest.raises(ValueError, match="Expected dictionary"):
            validate_json_input("not a dict")
    
    def test_validate_json_input_deep_nesting(self):
        """Test JSON validation with deep nesting"""
        deep_json = {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": {"level7": {"level8": {"level9": {"level10": {"level11": "value"}}}}}}}}}}}
        with pytest.raises(ValueError, match="nesting too deep"):
            validate_json_input(deep_json)


class TestMetricsCollection:
    """Test metrics collection functionality"""
    
    def test_metrics_initialization(self):
        """Test metrics collector initialization"""
        assert metrics is not None
        assert hasattr(metrics, 'request_count')
        assert hasattr(metrics, 'request_latency')
        assert hasattr(metrics, 'ml_predictions')
        assert hasattr(metrics, 'ml_anomalies')
    
    def test_record_request(self):
        """Test request metrics recording"""
        # This test verifies the function doesn't raise exceptions
        metrics.record_request("GET", "/test", 200, 0.1)
        metrics.record_request("POST", "/api", 500, 0.5)
    
    def test_record_ml_prediction(self):
        """Test ML prediction metrics recording"""
        metrics.record_ml_prediction("anomaly_detector", "success")
        metrics.record_ml_prediction("anomaly_detector", "error")
    
    def test_record_anomaly(self):
        """Test anomaly metrics recording"""
        metrics.record_anomaly("high", "anomaly_detector")
        metrics.record_anomaly("medium", "anomaly_detector")
    
    def test_set_system_health(self):
        """Test system health metrics setting"""
        metrics.set_system_health("database", 95.5)
        metrics.set_system_health("overall", 87.2)


class TestMemoryUsage:
    """Test memory usage functionality"""
    
    def test_get_memory_usage_with_psutil(self):
        """Test memory usage with psutil available"""
        with patch('app.main_refactored.psutil') as mock_psutil:
            mock_process = Mock()
            mock_process.memory_info.return_value = Mock(rss=1024*1024*100, vms=1024*1024*200)
            mock_process.memory_percent.return_value = 25.5
            mock_psutil.Process.return_value = mock_process
            
            result = _get_memory_usage()
            
            assert result['rss_mb'] == 100.0
            assert result['vms_mb'] == 200.0
            assert result['percent'] == 25.5
    
    def test_get_memory_usage_without_psutil(self):
        """Test memory usage without psutil"""
        with patch('app.main_refactored.psutil', None):
            result = _get_memory_usage()
            assert result['error'] == 'psutil not available'


class TestApplicationConfiguration:
    """Test application configuration and setup"""
    
    def test_create_app_development(self):
        """Test application creation in development mode"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            app = create_app()
            assert app is not None
            assert app.config['TESTING'] is False
    
    def test_create_app_testing(self):
        """Test application creation in testing mode"""
        with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
            app = create_app()
            assert app is not None
    
    def test_component_initialization(self):
        """Test component initialization"""
        with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
            app = create_app()
            
            # Test that components are initialized (even if some are None)
            assert hasattr(app, 'anomaly_detector')
            assert hasattr(app, 'remediation_engine')
    
    def test_blueprint_registration(self):
        """Test blueprint registration"""
        with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
            with patch('app.main_refactored._register_blueprints') as mock_register:
                app = create_app()
                mock_register.assert_called_once_with(app)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
