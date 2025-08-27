"""Tests for Flask application."""""

import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestFlaskApplication:
    """Test cases for Flask application."""""

    @pytest.fixture
    def test_app(self):
        """Create test app."""""
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, test_app):
        """Create test client."""""
        return test_app.test_client()

    def test_home_endpoint(self, client):
        """Test home endpoint."""""
        response = client.get("/")
        assert response.status_code == 200
        # Home endpoint returns HTML dashboard, so check content type and content
        if response.content_type.startswith("text/html"):
            assert "Smart CloudOps AI" in response.get_data(as_text=True)
        else:
            # If it returns JSON (fallback case)
            data = response.get_json()
            assert "error" in data or "message" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.content_type.startswith("text/plain")

    def test_status_endpoint(self, client):
        """Test status endpoint."""""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "components" in data

    def test_404_handler(self, client):
        """Test 404 error handler."""""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_health_endpoint(self, client):
        """Test health endpoint."""""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data
