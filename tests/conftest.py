"""
Pytest configuration and shared fixtures for SmartCloudOps AI tests.
Phase 2: Testing Backbone
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables before importing app
os.environ.update({
    "FLASK_ENV": "testing",
    "TESTING": "true",
    "SECRET_KEY": "test-secret-key-for-testing-only-32chars",
    "JWT_SECRET_KEY": "test-jwt-secret-key-for-testing-32ch",
    "DEFAULT_ADMIN_PASSWORD": "test-admin-password-16chars",
    "DATABASE_URL": "sqlite:///:memory:",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_PASSWORD": "test-redis-password",
    "OPENAI_API_KEY": "test-openai-key",
    "AWS_REGION": "us-east-1",
    "DISABLE_AWS_SERVICES": "true",
    "DISABLE_ELASTICSEARCH": "true",
    "USE_LOCAL_STORAGE": "true",
})

from app import create_app
from app.database import db_session, init_db
from app.models import User, Anomaly, RemediationAction


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app(
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key-for-testing-only-32chars",
    })
    
    with app.app_context():
        init_db()
        yield app
        # Cleanup handled by init_db


@pytest.fixture(scope="function")
def client(app):
    """Create test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Create test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def auth_headers():
    """Generate authentication headers for testing."""
    return {
        "Authorization": "Bearer test-jwt-token",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("openai.OpenAI") as mock:
        mock_client = MagicMock(
    mock.return_value = mock_client
        
        # Mock chat completion
        mock_response = MagicMock(
    mock_response.choices = [
            MagicMock(message=MagicMock(content="Test AI response"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        yield mock_client


@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis client for testing."""
    with patch("redis.Redis") as mock:
        mock_client = MagicMock(
    mock.return_value = mock_client
        
        # Mock common Redis operations
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1
        mock_client.exists.return_value = False
        
        yield mock_client


@pytest.fixture(scope="function")
def mock_prometheus():
    """Mock Prometheus client for testing."""
    with patch("prometheus_client.Counter") as mock_counter:
        with patch("prometheus_client.Histogram") as mock_histogram:
            with patch("prometheus_client.Gauge") as mock_gauge:
                yield {
                    "counter": mock_counter,
                    "histogram": mock_histogram,
                    "gauge": mock_gauge
                }


@pytest.fixture(scope="function")
def sample_anomaly():
    """Create sample anomaly for testing."""
    return {
        "id": "test-anomaly-123",
        "metric": "cpu_usage",
        "value": 95.5,
        "threshold": 80.0,
        "severity": "high",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": "High CPU usage detected",
        "affected_resource": "server-01",
    }


@pytest.fixture(scope="function")
def sample_remediation():
    """Create sample remediation for testing."""
    return {
        "id": "test-remediation-456",
        "anomaly_id": "test-anomaly-123",
        "action": "scale_up",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "instance_type": "t3.large",
            "min_instances": 2,
            "max_instances": 5
        }
    }


@pytest.fixture(scope="function")
def sample_user():
    """Create sample user for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "admin",
        "is_active": True
    }


@pytest.fixture(scope="function")
def mock_aws_services():
    """Mock AWS services for testing."""
    with patch("boto3.client") as mock_client:
        # Mock EC2
        ec2_mock = MagicMock(
    ec2_mock.describe_instances.return_value = {
            "Reservations": [{
                "Instances": [{
                    "InstanceId": "i-1234567890",
                    "State": {"Name": "running"}
                }]
            }]
        }
        
        # Mock CloudWatch
        cloudwatch_mock = MagicMock(
    cloudwatch_mock.get_metric_statistics.return_value = {
            "Datapoints": [
                {"Timestamp": datetime.now(timezone.utc), "Average": 50.0}
            ]
        }
        
        # Mock SSM
        ssm_mock = MagicMock(
    ssm_mock.get_parameter.return_value = {
            "Parameter": {"Value": "test-value"}
        }
        
        def client_factory(service_name, **kwargs):
            if service_name == "ec2":
                return ec2_mock
            elif service_name == "cloudwatch":
                return cloudwatch_mock
            elif service_name == "ssm":
                return ssm_mock
            return MagicMock()
        
        mock_client.side_effect = client_factory
        yield mock_client


@pytest.fixture(scope="function")
def temp_directory():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment after each test."""
    yield
    # Clean up any test-specific environment variables
    for key in list(os.environ.keys()):
        if key.startswith("TEST_"):
            del os.environ[key]


# Markers for test categorization
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "critical: Critical tests that must pass")
    config.addinivalue_line("markers", "auth: Authentication and authorization tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")


# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_test_token(user_id=1, username="testuser", role="admin"):
        """Create a test JWT token."""
        import jwt
        from datetime import datetime, timedelta, timezone
        
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        return jwt.encode(
            payload,
            os.environ.get("JWT_SECRET_KEY"),
            algorithm="HS256"
        )
    
    @staticmethod
    def assert_response_success(response, status_code=200):
        """Assert API response is successful."""
        assert response.status_code == status_code
        if response.content_type == "application/json":
            data = response.get_json()
            assert "error" not in data or data["error"] is None
        return response
    
    @staticmethod
    def assert_response_error(response, status_code=400):
        """Assert API response is an error."""
        assert response.status_code == status_code
        if response.content_type == "application/json":
            data = response.get_json()
            assert "error" in data
        return response


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils()


# Performance tracking
@pytest.fixture
def performance_tracker():
    """Track test performance."""
    import time
    
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return PerformanceTracker()
