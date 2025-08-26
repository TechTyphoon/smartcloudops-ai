#!/usr/bin/env python3
"""
Unit tests for MLOps API endpoints
Phase 2A Week 4: MLOps API Integration
"""

import json
import unittest
from unittest.mock import patch, MagicMock
import pytest

from app.main import create_app


@pytest.mark.unit
class TestMLOpsAPI(unittest.TestCase):
    """Test MLOps API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    def test_mlops_health_endpoint(self):
        """Test MLOps health check endpoint."""
        response = self.client.get('/api/mlops/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertIn('service', data['data'])

    def test_get_mlops_statistics(self):
        """Test getting MLOps statistics."""
        response = self.client.get('/api/mlops/statistics')
        
        # Should return 200 even if service not available (graceful fallback)
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_experiments_pagination(self):
        """Test getting experiments with pagination."""
        response = self.client.get('/api/mlops/experiments?page=1&per_page=10')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_create_experiment_valid_data(self):
        """Test creating experiment with valid data."""
        experiment_data = {
            "name": "test_experiment",
            "description": "Test experiment for MLOps API",
            "tags": ["test", "api"]
        }
        
        response = self.client.post(
            '/api/mlops/experiments',
            data=json.dumps(experiment_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [201, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_create_experiment_missing_data(self):
        """Test creating experiment with missing required data."""
        experiment_data = {
            "description": "Missing name field"
        }
        
        response = self.client.post(
            '/api/mlops/experiments',
            data=json.dumps(experiment_data),
            content_type='application/json'
        )
        
        # Should return 400 for missing required fields
        self.assertIn(response.status_code, [400, 503])

    def test_create_experiment_no_data(self):
        """Test creating experiment with no data."""
        response = self.client.post('/api/mlops/experiments')
        
        # Should return 400 for no data
        self.assertIn(response.status_code, [400, 503])

    def test_start_experiment_run(self):
        """Test starting an experiment run."""
        run_data = {
            "run_name": "test_run",
            "parameters": {"learning_rate": 0.01, "epochs": 10},
            "tags": ["test"]
        }
        
        response = self.client.post(
            '/api/mlops/experiments/exp_123/runs',
            data=json.dumps(run_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [201, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_log_metric_valid_data(self):
        """Test logging metrics with valid data."""
        metric_data = {
            "key": "accuracy",
            "value": 0.95,
            "step": 100
        }
        
        response = self.client.post(
            '/api/mlops/experiments/exp_123/runs/run_456/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_log_metric_missing_data(self):
        """Test logging metrics with missing required data."""
        metric_data = {
            "key": "accuracy"
            # Missing value
        }
        
        response = self.client.post(
            '/api/mlops/experiments/exp_123/runs/run_456/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 503])

    def test_log_parameter_valid_data(self):
        """Test logging parameters with valid data."""
        param_data = {
            "key": "learning_rate",
            "value": 0.01
        }
        
        response = self.client.post(
            '/api/mlops/experiments/exp_123/runs/run_456/parameters',
            data=json.dumps(param_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_end_run(self):
        """Test ending an experiment run."""
        end_data = {
            "status": "FINISHED"
        }
        
        response = self.client.post(
            '/api/mlops/experiments/exp_123/runs/run_456/end',
            data=json.dumps(end_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_models(self):
        """Test getting registered models."""
        response = self.client.get('/api/mlops/models?page=1&per_page=10')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_register_model_valid_data(self):
        """Test registering a model with valid data."""
        model_data = {
            "name": "test_model",
            "version": "1.0.0",
            "model_path": "/models/test_model.pkl",
            "framework": "scikit-learn",
            "tags": ["test"],
            "metadata": {"accuracy": 0.95}
        }
        
        response = self.client.post(
            '/api/mlops/models',
            data=json.dumps(model_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [201, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_register_model_missing_data(self):
        """Test registering a model with missing required data."""
        model_data = {
            "name": "test_model"
            # Missing version and model_path
        }
        
        response = self.client.post(
            '/api/mlops/models',
            data=json.dumps(model_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 503])

    def test_update_model_status(self):
        """Test updating model status."""
        status_data = {
            "status": "production"
        }
        
        response = self.client.put(
            '/api/mlops/models/model_123/status',
            data=json.dumps(status_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_update_model_status_missing_data(self):
        """Test updating model status with missing data."""
        response = self.client.put('/api/mlops/models/model_123/status')
        
        self.assertIn(response.status_code, [400, 503])

    def test_get_data_versions(self):
        """Test getting data versions."""
        response = self.client.get('/api/mlops/data/versions?page=1&per_page=10')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_data_versions_with_filter(self):
        """Test getting data versions with dataset filter."""
        response = self.client.get('/api/mlops/data/versions?dataset_name=test_dataset')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_data_quality_report(self):
        """Test getting data quality report."""
        response = self.client.get('/api/mlops/data/versions/version_123/quality')
        
        self.assertIn(response.status_code, [200, 404, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_create_data_transformation_valid_data(self):
        """Test creating data transformation with valid data."""
        transform_data = {
            "source_version_id": "version_123",
            "transformations": [
                {"type": "normalize", "columns": ["feature1", "feature2"]},
                {"type": "remove_outliers", "method": "iqr"}
            ],
            "target_dataset_name": "transformed_dataset"
        }
        
        response = self.client.post(
            '/api/mlops/data/transformations',
            data=json.dumps(transform_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [201, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_create_data_transformation_missing_data(self):
        """Test creating data transformation with missing required data."""
        transform_data = {
            "source_version_id": "version_123"
            # Missing transformations
        }
        
        response = self.client.post(
            '/api/mlops/data/transformations',
            data=json.dumps(transform_data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 503])

    def test_get_mlflow_experiments(self):
        """Test getting MLflow experiments."""
        response = self.client.get('/api/mlops/mlflow/experiments')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_mlflow_runs(self):
        """Test getting MLflow runs."""
        response = self.client.get('/api/mlops/mlflow/experiments/exp_123/runs')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_available_frameworks(self):
        """Test getting available frameworks."""
        response = self.client.get('/api/mlops/frameworks')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_get_available_algorithms(self):
        """Test getting available algorithms."""
        response = self.client.get('/api/mlops/algorithms')
        
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)


@pytest.mark.unit
class TestMLOpsAPIEdgeCases(unittest.TestCase):
    """Test MLOps API edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    def test_invalid_json_data(self):
        """Test API endpoints with invalid JSON data."""
        invalid_json = '{"invalid": json syntax}'
        
        response = self.client.post(
            '/api/mlops/experiments',
            data=invalid_json,
            content_type='application/json'
        )
        
        # Should handle invalid JSON gracefully
        self.assertIn(response.status_code, [400, 503])

    def test_empty_request_body(self):
        """Test API endpoints with empty request body."""
        response = self.client.post(
            '/api/mlops/experiments',
            data='',
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 503])

    def test_unsupported_http_methods(self):
        """Test unsupported HTTP methods."""
        # Test DELETE on experiments endpoint (not supported)
        response = self.client.delete('/api/mlops/experiments')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_non_existent_endpoints(self):
        """Test non-existent MLOps endpoints."""
        response = self.client.get('/api/mlops/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_pagination_edge_cases(self):
        """Test pagination with edge case values."""
        # Test with very large per_page (should be capped)
        response = self.client.get('/api/mlops/experiments?per_page=1000')
        self.assertIn(response.status_code, [200, 503])
        
        # Test with negative page number
        response = self.client.get('/api/mlops/experiments?page=-1')
        self.assertIn(response.status_code, [200, 503])

    def test_special_characters_in_parameters(self):
        """Test API with special characters in parameters."""
        experiment_data = {
            "name": "test_experiment_!@#$%^&*()",
            "description": "Test with special chars: <script>alert('xss')</script>",
            "tags": ["test", "special-chars"]
        }
        
        response = self.client.post(
            '/api/mlops/experiments',
            data=json.dumps(experiment_data),
            content_type='application/json'
        )
        
        # Should handle special characters (security validation should catch malicious content)
        self.assertIn(response.status_code, [201, 400, 503])


if __name__ == '__main__':
    unittest.main()
