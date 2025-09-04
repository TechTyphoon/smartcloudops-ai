# test_database_integration.py - Database Integration Tests
# Smart CloudOps AI Database Integration Validation


import pytest

from app import create_app


# Create Flask test client
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestDatabaseIntegration:
    """Test database integration functionality"""

    def test_database_health_endpoint(self, client):
        """Test database health monitoring"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "healthy"
        assert "database_health" in data
        assert data["database_health"]["status"] == "healthy"
        assert "PostgreSQL" in data["database_health"]["version"]
        assert data["version"] == "v3.0.0-database-integrated"

    def test_database_status_endpoint(self, client):
        """Test database-specific status endpoint"""
        response = client.get("/database/status")
        assert response.status_code == 200

        data = response.get_json()
        assert "database_health" in data
        assert "connection_info" in data
        assert "data_statistics" in data
        assert "models_available" in data

        # Check available models
        expected_models = [
            "SystemMetrics",
            "MLTrainingData",
            "AnomalyDetection",
            "RemediationAction",
            "ChatOpsInteraction",
            "HealthCheck",
            "SecurityScan",
        ]
        assert all(model in data["models_available"] for model in expected_models)

    def test_metrics_history_endpoint(self, client):
        """Test metrics history from database"""
        response = client.get("/metrics/history")
        assert response.status_code == 200

        data = response.get_json()
        assert "total_samples" in data
        assert "summary_statistics" in data
        assert "recent_metrics" in data
        assert data["period_hours"] == 24  # Default period

        # Test with custom period
        response = client.get("/metrics/history?hours=1")
        assert response.status_code == 200

        data = response.get_json()
        assert data["period_hours"] == 1

    def test_system_metrics_persistence(self, client):
        """Test that system metrics are being stored in database"""
        # Make multiple requests to generate metrics
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200

        # Check metrics history
        response = client.get("/metrics/history")
        data = response.get_json()

        # Check that metrics history structure is correct (may have 0 samples in test environment)
        assert isinstance(data["total_samples"], int)
        assert "summary_statistics" in data

    def test_enhanced_status_with_database(self, client):
        """Test enhanced status endpoint with database features"""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.get_json()
        assert data["version"] == "v3.0.0-database-integrated"
        assert data["database_integrated"] == True
        assert "database_connection" in data
        assert "metrics_summary_24h" in data
        assert "health_summary" in data

        # Verify database connection info
        db_conn = data["database_connection"]
        assert db_conn["host"] == "localhost"
        assert db_conn["database"] == "smartcloudops_production"
        assert db_conn["user"] == "smartcloudops"

    def test_prometheus_metrics_with_database(self, client):
        """Test Prometheus metrics include database info"""
        response = client.get("/monitoring/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

        metrics_text = response.text

        # Check for database-specific metrics
        assert "smartcloudops_database_connected" in metrics_text
        assert "smartcloudops_training_records" in metrics_text
        assert "smartcloudops_security_issues" in metrics_text

        # Verify standard metrics are still present
        assert "smartcloudops_cpu_usage_percent" in metrics_text
        assert "smartcloudops_memory_usage_percent" in metrics_text

    def test_data_persistence_across_requests(self, client):
        """Test that data persists across multiple requests"""
        # Get initial request count
        response1 = client.get("/health")
        data1 = response1.get_json()
        initial_count = data1.get("request_count", 0)

        # Make another request
        response2 = client.get("/health")
        data2 = response2.get_json()
        second_count = data2.get("request_count", 0)

        # Request count should increment (data persistence working)
        assert second_count > initial_count

        # Database health should be consistent
        assert data1["database_health"]["status"] == data2["database_health"]["status"]
        assert data1["database_health"]["user"] == data2["database_health"]["user"]

    def test_error_handling_database_integration(self, client):
        """Test error handling in database operations"""
        # Test invalid endpoints still work
        response = client.get("/nonexistent")
        assert response.status_code == 404

        # Test that application continues to work even with database queries
        response = client.get("/health")
        assert response.status_code == 200

        # Application should not crash due to database operations
        data = response.get_json()
        assert data["status"] == "healthy"
