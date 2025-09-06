"""
Locust performance test file for SmartCloudOps AI
"""

from locust import HttpUser, task, between
import random
import json


class SmartCloudOpsUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Setup user session"""
        # Test user registration/login
        self.register_or_login()

    def register_or_login(self):
        """Register or login a test user"""
        user_data = {
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "password": "testpassword123",
            "name": f"Test User {random.randint(1, 1000)}",
        }

        # Try to register
        response = self.client.post(
            "/auth/register", json=user_data, catch_response=True
        )
        if response.status_code == 201:
            self.token = response.json().get("access_token")
        else:
            # Try to login
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"],
            }
            response = self.client.post(
                "/auth/login", json=login_data, catch_response=True
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
            else:
                self.token = None

    @property
    def headers(self):
        if hasattr(self, "token") and self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(10)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")

    @task(8)
    def get_dashboard(self):
        """Test dashboard data"""
        self.client.get("/api/dashboard/summary", headers=self.headers)

    @task(6)
    def list_anomalies(self):
        """Test anomaly listing"""
        self.client.get("/api/anomalies/", headers=self.headers)

    @task(4)
    def get_metrics(self):
        """Test metrics endpoint"""
        self.client.get("/api/monitoring/metrics", headers=self.headers)

    @task(3)
    def ml_model_info(self):
        """Test ML model info"""
        self.client.get("/api/ml/model/info", headers=self.headers)

    @task(2)
    def create_anomaly(self):
        """Test anomaly creation"""
        anomaly_data = {
            "metric_name": f"cpu_usage_{random.randint(1, 100)}",
            "value": random.uniform(0, 100),
            "threshold": 80.0,
            "severity": random.choice(["low", "medium", "high"]),
            "source": "test_load",
        }
        self.client.post("/api/anomalies/", json=anomaly_data, headers=self.headers)

    @task(1)
    def run_health_check(self):
        """Test system health check"""
        self.client.post("/api/monitoring/health-check", headers=self.headers)
