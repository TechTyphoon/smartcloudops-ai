# test_database_integration.py - Database Integration Tests
# Smart CloudOps AI Database Integration Validation

import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"


class TestDatabaseIntegration:
    """Test database integration functionality"""

    def test_database_health_endpoint(self):
        """Test database health monitoring"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "database_health" in data
        assert data["database_health"]["status"] == "healthy"
        assert "PostgreSQL" in data["database_health"]["version"]
        assert data["version"] == "v3.0.0-database-integrated"

    def test_database_status_endpoint(self):
        """Test database-specific status endpoint"""
        response = requests.get(f"{BASE_URL}/database/status")
        assert response.status_code == 200

        data = response.json()
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

    def test_metrics_history_endpoint(self):
        """Test metrics history from database"""
        response = requests.get(f"{BASE_URL}/metrics/history")
        assert response.status_code == 200

        data = response.json()
        assert "total_samples" in data
        assert "summary_statistics" in data
        assert "recent_metrics" in data
        assert data["period_hours"] == 24  # Default period

        # Test with custom period
        response = requests.get(f"{BASE_URL}/metrics/history?hours=1")
        assert response.status_code == 200

        data = response.json()
        assert data["period_hours"] == 1

    def test_system_metrics_persistence(self):
        """Test that system metrics are being stored in database"""
        # Make multiple requests to generate metrics
        for _ in range(3):
            response = requests.get(f"{BASE_URL}/health")
            assert response.status_code == 200

        # Check metrics history
        response = requests.get(f"{BASE_URL}/metrics/history")
        data = response.json()

        # Should have multiple samples now
        assert data["total_samples"] >= 3
        assert "summary_statistics" in data

        # Check summary statistics
        summary = data["summary_statistics"]
        assert "cpu_stats" in summary
        assert "memory_stats" in summary
        assert "sample_count" in summary
        assert summary["sample_count"] >= 3

    def test_enhanced_status_with_database(self):
        """Test enhanced status endpoint with database features"""
        response = requests.get(f"{BASE_URL}/status")
        assert response.status_code == 200

        data = response.json()
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

    def test_prometheus_metrics_with_database(self):
        """Test Prometheus metrics include database info"""
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        metrics_text = response.text

        # Check for database-specific metrics
        assert "smartcloudops_database_connected 1" in metrics_text
        assert "smartcloudops_training_records" in metrics_text
        assert "smartcloudops_security_issues" in metrics_text

        # Verify standard metrics are still present
        assert "smartcloudops_cpu_usage_percent" in metrics_text
        assert "smartcloudops_memory_usage_percent" in metrics_text

    def test_data_persistence_across_requests(self):
        """Test that data persists across multiple requests"""
        # Get initial request count
        response1 = requests.get(f"{BASE_URL}/health")
        data1 = response1.json()
        initial_count = data1["request_count"]

        # Make another request
        response2 = requests.get(f"{BASE_URL}/health")
        data2 = response2.json()
        second_count = data2["request_count"]

        # Request count should increment (data persistence working)
        assert second_count > initial_count

        # Database health should be consistent
        assert data1["database_health"]["status"] == data2["database_health"]["status"]
        assert data1["database_health"]["user"] == data2["database_health"]["user"]

    def test_error_handling_database_integration(self):
        """Test error handling in database operations"""
        # Test invalid endpoints still work
        response = requests.get(f"{BASE_URL}/nonexistent")
        assert response.status_code == 404

        # Test that application continues to work even with database queries
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200

        # Application should not crash due to database operations
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    print("🧪 Running Database Integration Tests...")

    # Run basic connectivity test first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        exit(1)

    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
