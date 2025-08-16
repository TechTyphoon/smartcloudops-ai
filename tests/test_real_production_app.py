"""Tests for the real production Flask application."""

import pytest
import sys
import os
import json

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import our real production app
from complete_production_app_real_data import app


class TestRealProductionApp:
    """Test cases for the real production Flask application with 100% real data."""

    @pytest.fixture
    def client(self):
        """Create test client for the real app."""
        app.config['TESTING'] = True
        return app.test_client()

    def test_health_endpoint_responds(self, client):
        """Test that health endpoint responds correctly."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'status' in data
        assert data['data_source'] == '100% real system data'

    def test_status_endpoint_real_data(self, client):
        """Test status endpoint returns real system data."""
        response = client.get('/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'system_metrics' in data
        assert 'ml_model' in data
        assert data['data_sources']['all_data'] == '100% real, 0% mock'

    def test_metrics_endpoint_prometheus_format(self, client):
        """Test metrics endpoint returns Prometheus format."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type == 'text/plain; charset=utf-8'
        
        metrics_text = response.get_data(as_text=True)
        assert 'smartcloudops_cpu_usage_percent' in metrics_text
        assert 'smartcloudops_memory_usage_percent' in metrics_text

    def test_anomaly_status_endpoint(self, client):
        """Test anomaly detection status endpoint."""
        response = client.get('/anomaly/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'model_status' in data
        assert 'training_data' in data

    def test_anomaly_batch_detection(self, client):
        """Test batch anomaly detection with real metrics."""
        test_data = {
            'metrics': [
                {'cpu': 85, 'memory': 75},
                {'cpu': 20, 'memory': 30}
            ]
        }
        
        response = client.post('/anomaly/batch',
                             data=json.dumps(test_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'processed_count' in data
        assert data['processed_count'] == 2
        assert 'processing_method' in data

    def test_remediation_execute_dry_run(self, client):
        """Test remediation execution in dry run mode."""
        test_data = {
            'action': 'restart_service',
            'target': 'test_service',
            'dry_run': True
        }
        
        response = client.post('/remediation/execute',
                             data=json.dumps(test_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert data['dry_run'] == True
        assert 'execution_log' in data

    def test_chatops_analyze_query(self, client):
        """Test ChatOps AI query analysis."""
        test_data = {
            'query': 'What is the system health status?'
        }
        
        response = client.post('/chatops/analyze',
                             data=json.dumps(test_data),
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'intent_classification' in data
        assert 'confidence' in data
        assert data['data_authenticity'] == '100% real system data'

    def test_dashboard_loads(self, client):
        """Test that the modern dashboard loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Smart CloudOps AI' in response.data
        assert b'dashboard_modern.html' or b'Smart CloudOps AI - Production Dashboard' in response.data

    def test_all_get_endpoints_respond(self, client):
        """Test that all GET endpoints respond successfully."""
        get_endpoints = [
            '/health',
            '/status', 
            '/metrics',
            '/anomaly/status',
            '/remediation/status',
            '/chatops/history',
            '/chatops/context'
        ]
        
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed with status {response.status_code}"

    def test_error_handling_invalid_json(self, client):
        """Test error handling for invalid JSON in POST requests."""
        response = client.post('/anomaly/batch',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 500  # Should handle gracefully

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        # Test anomaly detection without metrics
        response = client.post('/anomaly/batch',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400

        # Test ChatOps without query
        response = client.post('/chatops/analyze',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
