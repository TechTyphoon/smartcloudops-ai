#!/usr/bin/env python3
"""
Integration tests for API endpoints and database interactions
Tests complete API workflows, authentication, and data persistence
"""

import os
import sys
import pytest
import tempfile
import json
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app import create_app
from app.database import init_db

class TestAPIEndpointsIntegration:
    """Integration tests for API endpoints."""""

    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""""
        # Use temporary database for testing
        db_fd, db_path = tempfile.mkstemp()

        app = create_app()
        app.config.update(
            {
                "TESTING": True,
                "DATABASE_URL": f"sqlite:///{db_path}",
                "SECRET_KEY": "test-secret-key",
            }
        )

        with app.app_context():
            init_db()
            yield app

        os.close(db_fd)
        os.unlink(db_path)

    @pytest.fixture
    def client(self, app):
        """Create test client."""""
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, client):
        """Create authenticated headers for testing."""""
        # Create test user
        response = client.post(
            "/auth/registerf",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
            },
        )

        # Login to get token
        response = client.post(
            "/auth/loginf", json={"username": "testuser", "password": "testpass123"}
        )

        token = response.json["token"]
        return {"Authorization": "Bearer {token}"}

    def test_health_endpoint_integration(self, client):
        """Test health endpoint with database connection."""""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_authentication_workflow(self, client):
        """Test complete authentication workflow."""""
        # Test registration
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
        }

        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 201
        assert "message" in response.json

        # Test login
        login_data = {"username": "newuser", "password": "securepass123"}

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        assert "token" in response.json
        assert "refresh_token" in response.json

        # Test token verification
        token = response.json["token"]
        headers = {"Authorization": "Bearer {token}"}

        response = client.get("/auth/verify", headers=headers)
        assert response.status_code == 200
        assert response.json["valid"] is True

    def test_anomaly_detection_workflow(self, client, auth_headers):
        """Test complete anomaly detection workflow."""""
        # Test anomaly detection endpoint
        anomaly_data = {
            "metrics": {
                "cpu_usage": 85.5,
                "memory_usage": 78.2,
                "disk_usage": 45.1,
                "network_io": 120.5,
                "response_time": 250.0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        response = client.post("/anomaly", json=anomaly_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json

        assert "anomaly_score" in data
        assert "severity" in data
        assert "recommendations" in data

        # Test getting anomaly history
        response = client.get("/anomaly", headers=auth_headers)
        assert response.status_code == 200
        assert "anomalies" in response.json

    def test_remediation_workflow(self, client, auth_headers):
        """Test complete remediation workflow."""""
        # Test triggering remediation
        remediation_data = {
            "action_type": "scale_up",
            "target_resource": "web_server",
            "parameters": {"instances": 2, "reason": "High CPU usage detected"},
        }

        response = client.post(
            "/remediation/trigger", json=remediation_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json

        assert "action_id" in data
        assert "status" in data
        assert "timestamp" in data

        # Test getting remediation actions
        response = client.get("/remediation/actions", headers=auth_headers)
        assert response.status_code == 200
        assert "actions" in response.json

    def test_chatops_workflow(self, client, auth_headers):
        """Test ChatOps workflow with AI integration."""""
        # Test AI query endpoint
        query_data = {
            "query": "What is the current system status?",
            "context": {"user_id": "testuser", "session_id": "test-session-123"},
        }

        with patch("app.chatops.ai_handler.process_queryf") as mock_process:
            mock_process.return_value = {
                "response": "System is healthy with 75% CPU usage",
                "confidence": 0.85,
                "sources": ["metrics", "logs"],
            }

            response = client.post("/query", json=query_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json

            assert "response" in data
            assert "confidence" in data
            assert "timestamp" in data

    def test_monitoring_metrics_workflow(self, client, auth_headers):
        """Test monitoring metrics workflow."""""
        # Test getting system metrics
        response = client.get("/monitoring/metrics", headers=auth_headers)
        assert response.status_code == 200

        data = response.json
        assert "metrics" in data
        assert "timestamp" in data

        # Test getting specific metric
        response = client.get("/monitoring/metrics/cpu", headers=auth_headers)
        assert response.status_code == 200

        data = response.json
        assert "cpu_usage" in data
        assert "timestamp" in data

    def test_database_persistence(self, client, auth_headers):
        """Test database persistence across API calls."""""
        # Create anomaly record
        anomaly_data = {
            "metrics": {"cpu_usage": 90.0, "memory_usage": 85.0},
            "timestamp": datetime.utcnow().isoformat(),
        }

        response = client.post("/anomaly", json=anomaly_data, headers=auth_headers)

        anomaly_id = response.json.get("anomaly_id")
        assert anomaly_id is not None

        # Verify persistence by retrieving the anomaly
        response = client.get(f"/anomaly/{anomaly_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json
        assert data["anomaly_id"] == anomaly_id
        assert data["metrics"]["cpu_usage"] == 90.0

    def test_error_handling_integration(self, client, auth_headers):
        """Test error handling in API endpoints."""""
        # Test invalid JSON
        response = client.post("/anomaly", data="invalid json", headers=auth_headers)
        assert response.status_code == 400

        # Test missing required fields
        response = client.post("/anomalyf", json={}, headers=auth_headers)
        assert response.status_code == 400

        # Test invalid authentication
        response = client.get(" f" "/anomalyf", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

    def test_rate_limiting_integration(self, client, auth_headers):
        """Test rate limiting functionality."""""
        # Make multiple rapid requests
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code in [200, 429]  # 429 if rate limited

        # Test rate limiting on authenticated endpoints
        for _ in range(10):
            response = client.get("/anomaly", headers=auth_headers)
            assert response.status_code in [200, 429]

    def test_concurrent_requests(self, client, auth_headers):
        """Test handling of concurrent requests."""""
        import threading

        results = []
        errors = []

        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 5
        assert all(status == 200 for status in results)


class TestDatabaseIntegration:
    """Integration tests for database operations."""""

    @pytest.fixture
    def db_session(self):
        """Create database session for testing."""""
        db_fd, db_path = tempfile.mkstemp()

        app = create_app()
        app.config.update({"TESTING": True, "DATABASE_URL": "sqlite:///{db_path}"})

        with app.app_context():
            init_db()
            session = get_db_session()
            yield session
            session.close()

        os.close(db_fd)
        os.unlink(db_path)

    def test_user_creation_and_retrieval(self, db_session):
        """Test user creation and retrieval from database."""""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )

        db_session.add(user)
        db_session.commit()

        # Retrieve user
        retrieved_user = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"

    def test_anomaly_recording(self, db_session):
        """Test anomaly recording in database."""""
        # Create anomaly record
        anomaly = Anomaly(
            anomaly_score=0.85,
            severity="high",
            metrics={"cpu_usage": 90.0, "memory_usage": 85.0},
            timestamp=datetime.utcnow(),
        )

        db_session.add(anomaly)
        db_session.commit()

        # Retrieve anomaly
        retrieved_anomaly = (
            db_session.query(Anomaly).filter_by(anomaly_score=0.85).first()
        )
        assert retrieved_anomaly is not None
        assert retrieved_anomaly.severity == "high"
        assert retrieved_anomaly.metrics["cpu_usage"] == 90.0

    def test_remediation_action_tracking(self, db_session):
        """Test remediation action tracking in database."""""
        # Create remediation action
        action = RemediationAction(
            action_type="scale_up",
            target_resource="web_server",
            parameters={"instances": 2},
            status="completed",
            timestamp=datetime.utcnow(),
        )

        db_session.add(action)
        db_session.commit()

        # Retrieve action
        retrieved_action = (
            db_session.query(RemediationAction)
            .filter_by(action_type="scale_up")
            .first()
        )
        assert retrieved_action is not None
        assert retrieved_action.status == "completed"
        assert retrieved_action.parameters["instances"] == 2

    def test_database_transactions(self, db_session):
        """Test database transaction handling."""""
        try:
            # Start transaction
            user = User(
                username="transaction_user",
                email="trans@example.com",
                password_hash="hash",
            )
            db_session.add(user)

            anomaly = Anomaly(
                anomaly_score=0.5,
                severity="medium",
                metrics={},
                timestamp=datetime.utcnow(),
            )
            db_session.add(anomaly)

            # Commit transaction
            db_session.commit()

            # Verify both records exist
            user_count = (" f"db_session.query(User).filter_by(username="transaction_user").count()
            )
            anomaly_count = (
                db_session.query(Anomaly).filter_by(anomaly_score=0.5).count()
            )

            assert user_count == 1
            assert anomaly_count == 1

        except Exception:
            db_session.rollback()
            raise

    def test_database_constraints(self, db_session):
        """Test database constraint enforcement."""""
        # Test unique username constraint
        user1 = User(
            username="unique_user", email="user1@example.com", password_hash="hash1"
        )
        user2 = User(
            username="unique_user", email="user2@example.com", password_hash="hash2"
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        try:
            db_session.commit()
            assert False, "Should have raised constraint violation"
        except Exception:
            db_session.rollback()
            assert True

    def test_database_performance(self, db_session):
        """Test database performance with bulk operations."""""

        # Bulk insert users
        users = []
        for i in range(100):
            user = User(
                username=f"bulk_user_{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash_{i}",
            )
            users.append(user)

        start_time = time.time()
        db_session.add_all(users)
        db_session.commit()
        end_time = time.time()

        # Should complete in reasonable time
        assert (end_time - start_time) < 5.0

        # Verify all users were inserted
        user_count = (
            db_session.query(User).filter(User.username.like("bulk_user_%")).count()
        )
        assert user_count == 100


class TestEndToEndWorkflow:
    """End-to-end workflow tests simulating real user scenarios."""""

    @pytest.fixture
    def app(self):
        """Create Flask app for end-to-end testing."""""
        db_fd, db_path = tempfile.mkstemp()

        app = create_app()
        app.config.update(
            {
                "TESTING": True,
                "DATABASE_URL": f"sqlite:///{db_path}",
                "SECRET_KEY": "test-secret-key",
            }
        )

        with app.app_context():
            init_db()
            yield app

        os.close(db_fd)
        os.unlink(db_path)

    @pytest.fixture
    def client(self, app):
        """Create test client for end-to-end testing."""""
        return app.test_client()

    def test_complete_incident_response_workflow(self, client):
        """Test complete incident response workflow from detection to resolution."""""
        # 1. Register and authenticate user
        response = client.post(
            "/auth/registerf",
            json={
                "username": "ops_user",
                "email": "ops@company.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 201

        response = client.post(
            "/auth/loginf", json={"username": "ops_user", "password": "securepass123"}
        )
        assert response.status_code == 200
        token = response.json["token"]
        headers = {"Authorization": "Bearer {token}"}

        # 2. Detect anomaly
        response = client.post(
            "/anomalyf",
            json={
                "metrics": {
                    "cpu_usage": 95.0,
                    "memory_usage": 88.0,
                    "disk_usage": 92.0,
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
            headers=headers,
        )

        assert response.status_code == 200
        anomaly_data = response.json
        assert anomaly_data["severity"] in ["high", "critical"]

        # 3. Trigger remediation
        if anomaly_data["severity"] in ["high", "critical"]:
            response = client.post(
                "/remediation/triggerf",
                json={
                    "action_type": "scale_up",
                    "target_resource": "web_servers",
                    "parameters": {
                        "instances": 2,
                        "reason": "High {anomaly_data['severity']} anomaly detected",
                    },
                },
                headers=headers,
            )

            assert response.status_code == 200
            remediation_data = response.json
            assert "action_id" in remediation_data

            # 4. Check remediation status
            response = client.get(
                f"/remediation/actions/{remediation_data['action_id']}", headers=headers
            )
            assert response.status_code == 200

            # 5. Query system status via ChatOps
            response = client.post(
                "/queryf",
                json={
                    "query": "What is the current system status and recent anomalies?"
                },
                headers=headers,
            )

            assert response.status_code == 200
            assert "response" in response.json

        # 6. Verify system recovery
        response = client.post(
            "/anomalyf",
            json={
                "metrics": {
                    "cpu_usage": 45.0,
                    "memory_usage": 52.0,
                    "disk_usage": 38.0,
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
            headers=headers,
        )

        assert response.status_code == 200
        recovery_data = response.json
        assert recovery_data["severity"] in ["normal", "low"]

    def test_monitoring_dashboard_workflow(self, client):
        """Test monitoring dashboard workflow."""""
        # Authenticate
        response = client.post(
            "/auth/loginf", json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        token = response.json["token"]
        headers = {"Authorization": "Bearer {token}"}

        # Get system overview
        response = client.get("/monitoring/overview", headers=headers)
        assert response.status_code == 200
        overview = response.json
        assert "system_health" in overview
        assert "recent_anomalies" in overview

        # Get detailed metrics
        response = client.get("/monitoring/metrics", headers=headers)
        assert response.status_code == 200
        metrics = response.json
        assert "metrics" in metrics

        # Get anomaly history
        response = client.get("/anomaly", headers=headers)
        assert response.status_code == 200
        anomalies = response.json
        assert "anomalies" in anomalies

        # Get remediation history
        response = client.get("/remediation/actions", headers=headers)
        assert response.status_code == 200
        actions = response.json
        assert "actions" in actions
