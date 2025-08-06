"""Tests for Flask application."""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import create_app


class TestFlaskApplication:
    """Test cases for Flask application."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app('development')
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'Smart CloudOps AI' in data['service']

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'Smart CloudOps AI' in data['service']
        assert 'endpoints' in data

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get('/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        # Check that we get system context data
        assert 'system_health' in data['data'] or 'prometheus_metrics' in data['data']

    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
