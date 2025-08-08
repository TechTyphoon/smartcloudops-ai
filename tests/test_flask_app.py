"""Tests for Flask application."""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app


class TestFlaskApplication:
    """Test cases for Flask application."""

    @pytest.fixture
    def test_app(self):
        """Create test app."""
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return test_app.test_client()

    def test_home_endpoint(self, client):
        """Test home endpoint."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'running'
        assert 'Smart CloudOps AI' in data['message']

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get('/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'components' in data



    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
