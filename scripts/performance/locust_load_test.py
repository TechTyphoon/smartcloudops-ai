#!/usr/bin/env python3
"""
SmartCloudOps AI - Advanced Load Testing with Locust
Comprehensive performance testing with realistic user behavior patterns
"""

import random
import time
import json
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartCloudOpsUser(HttpUser):
    """Simulates realistic user behavior patterns"""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    weight = 1
    
    def on_start(self):
        """Setup user session with authentication"""
        self.token = None
        self.user_id = None
        self.correlation_id = f"load-test-{random.randint(10000, 99999)}"
        
        # Register or login user
        self.authenticate()
        
        # Set common headers
        self.client.headers.update({
            'X-Correlation-ID': self.correlation_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def authenticate(self):
        """Authenticate user and get token"""
        try:
            # Generate unique test user
            test_email = f"loadtest{random.randint(1000, 9999)}@example.com"
            user_data = {
                "email": test_email,
                "password": "LoadTest123!",
                "name": f"Load Test User {random.randint(1, 1000)}"
            }
            
            # Try to register
            with self.client.post(
                "/auth/register", 
                json=user_data,
                catch_response=True,
                name="Auth - Register"
            ) as response:
                if response.status_code in [200, 201]:
                    self.token = response.json().get("access_token")
                    self.user_id = response.json().get("user", {}).get("id")
                else:
                    # Try to login if registration fails
                    login_data = {"email": test_email, "password": user_data["password"]}
                    with self.client.post(
                        "/auth/login",
                        json=login_data,
                        catch_response=True,
                        name="Auth - Login"
                    ) as login_response:
                        if login_response.status_code == 200:
                            self.token = login_response.json().get("access_token")
                            self.user_id = login_response.json().get("user", {}).get("id")
                        
            # Update headers with token
            if self.token:
                self.client.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
    
    @property
    def auth_headers(self):
        """Get headers with authentication"""
        headers = {'X-Correlation-ID': self.correlation_id}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    # ================================
    # CORE API ENDPOINTS (High Frequency)
    # ================================
    
    @task(20)
    def health_check(self):
        """Test health endpoints"""
        with self.client.get("/health", name="Health - Basic") as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(15)
    def metrics_endpoint(self):
        """Test metrics collection"""
        self.client.get("/metrics", name="Metrics - Prometheus")
    
    @task(15)
    def observability_health(self):
        """Test observability health"""
        self.client.get("/observability/health", name="Health - Observability")
    
    @task(12)
    def dashboard_summary(self):
        """Test dashboard data retrieval"""
        self.client.get(
            "/api/dashboard/summary",
            headers=self.auth_headers,
            name="Dashboard - Summary"
        )
    
    # ================================
    # ANOMALY DETECTION (Medium Frequency)
    # ================================
    
    @task(10)
    def list_anomalies(self):
        """Test anomaly listing with pagination"""
        params = {
            'page': random.randint(1, 3),
            'per_page': random.choice([10, 25, 50]),
            'severity': random.choice(['', 'low', 'medium', 'high'])
        }
        
        self.client.get(
            "/api/anomalies/",
            params=params,
            headers=self.auth_headers,
            name="Anomalies - List"
        )
    
    @task(8)
    def get_anomaly_details(self):
        """Test individual anomaly retrieval"""
        anomaly_id = random.randint(1, 100)  # Simulate existing anomaly IDs
        
        with self.client.get(
            f"/api/anomalies/{anomaly_id}",
            headers=self.auth_headers,
            catch_response=True,
            name="Anomalies - Get Details"
        ) as response:
            if response.status_code == 404:
                response.success()  # 404 is expected for non-existent anomalies
    
    @task(5)
    def create_anomaly(self):
        """Test anomaly creation"""
        anomaly_data = {
            "metric_name": f"cpu_usage_{random.randint(1, 100)}",
            "value": round(random.uniform(0, 100), 2),
            "threshold": random.choice([70.0, 80.0, 90.0, 95.0]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "source": "load_test",
            "timestamp": int(time.time()),
            "metadata": {
                "instance_id": f"i-{random.randint(100000, 999999)}",
                "region": random.choice(["us-west-2", "us-east-1", "eu-west-1"]),
                "service": random.choice(["web", "api", "worker", "database"])
            }
        }
        
        self.client.post(
            "/api/anomalies/",
            json=anomaly_data,
            headers=self.auth_headers,
            name="Anomalies - Create"
        )
    
    # ================================
    # ML OPERATIONS (Medium Frequency)
    # ================================
    
    @task(8)
    def ml_model_info(self):
        """Test ML model information"""
        self.client.get(
            "/api/ml/model/info",
            headers=self.auth_headers,
            name="ML - Model Info"
        )
    
    @task(6)
    def ml_predictions(self):
        """Test ML predictions"""
        prediction_data = {
            "features": [
                random.uniform(0, 100) for _ in range(10)
            ],
            "model_name": "anomaly_detector",
            "threshold": 0.5
        }
        
        self.client.post(
            "/api/ml/predict",
            json=prediction_data,
            headers=self.auth_headers,
            name="ML - Predict"
        )
    
    @task(4)
    def ml_model_metrics(self):
        """Test ML model performance metrics"""
        self.client.get(
            "/api/ml/model/metrics",
            headers=self.auth_headers,
            name="ML - Model Metrics"
        )
    
    # ================================
    # REMEDIATION (Lower Frequency)
    # ================================
    
    @task(6)
    def list_remediation_actions(self):
        """Test remediation action listing"""
        params = {
            'status': random.choice(['', 'pending', 'running', 'completed', 'failed']),
            'action_type': random.choice(['', 'restart', 'scale', 'alert'])
        }
        
        self.client.get(
            "/api/remediation/actions",
            params=params,
            headers=self.auth_headers,
            name="Remediation - List Actions"
        )
    
    @task(3)
    def create_remediation_action(self):
        """Test remediation action creation"""
        action_data = {
            "action_type": random.choice(["restart_service", "scale_up", "scale_down", "send_alert"]),
            "target_resource": f"instance-{random.randint(1, 100)}",
            "parameters": {
                "severity": random.choice(["low", "medium", "high"]),
                "timeout": random.randint(30, 300),
                "retry_count": random.randint(1, 3)
            },
            "require_approval": random.choice([True, False]),
            "triggered_by": "load_test"
        }
        
        self.client.post(
            "/api/remediation/actions",
            json=action_data,
            headers=self.auth_headers,
            name="Remediation - Create Action"
        )
    
    # ================================
    # MONITORING & FEEDBACK (Lower Frequency)
    # ================================
    
    @task(5)
    def monitoring_status(self):
        """Test monitoring system status"""
        self.client.get(
            "/api/monitoring/status",
            headers=self.auth_headers,
            name="Monitoring - Status"
        )
    
    @task(3)
    def submit_feedback(self):
        """Test feedback submission"""
        feedback_data = {
            "type": random.choice(["bug", "feature", "improvement", "question"]),
            "category": random.choice(["anomaly_detection", "remediation", "ui", "performance"]),
            "title": f"Load test feedback {random.randint(1, 1000)}",
            "description": "Automated feedback from load testing",
            "rating": random.randint(1, 5),
            "metadata": {
                "user_agent": "LoadTest/1.0",
                "session_duration": random.randint(60, 3600)
            }
        }
        
        self.client.post(
            "/api/feedback/",
            json=feedback_data,
            headers=self.auth_headers,
            name="Feedback - Submit"
        )
    
    # ================================
    # AI OPERATIONS (Lower Frequency)
    # ================================
    
    @task(4)
    def ai_chat_query(self):
        """Test AI chat functionality"""
        queries = [
            "What are the current system alerts?",
            "Show me anomalies from the last hour",
            "What is the CPU usage trend?",
            "Are there any failed remediation actions?",
            "Give me a system health summary"
        ]
        
        chat_data = {
            "message": random.choice(queries),
            "context": {
                "user_id": self.user_id,
                "session_id": self.correlation_id,
                "timestamp": int(time.time())
            }
        }
        
        self.client.post(
            "/api/ai/chat",
            json=chat_data,
            headers=self.auth_headers,
            name="AI - Chat Query"
        )
    
    # ================================
    # HEAVY OPERATIONS (Occasional)
    # ================================
    
    @task(2)
    def bulk_anomaly_analysis(self):
        """Test bulk data processing"""
        bulk_data = {
            "metrics": [
                {
                    "name": f"metric_{i}",
                    "value": random.uniform(0, 100),
                    "timestamp": int(time.time()) - random.randint(0, 3600)
                }
                for i in range(50)  # Bulk data
            ],
            "analysis_type": "anomaly_detection",
            "parameters": {
                "threshold": 0.8,
                "algorithm": "isolation_forest"
            }
        }
        
        with self.client.post(
            "/api/ml/analyze/bulk",
            json=bulk_data,
            headers=self.auth_headers,
            timeout=30,  # Longer timeout for heavy operations
            name="ML - Bulk Analysis"
        ) as response:
            if response.elapsed.total_seconds() > 10:
                logger.warning(f"Slow bulk analysis: {response.elapsed.total_seconds()}s")
    
    def on_stop(self):
        """Cleanup when user stops"""
        logger.info(f"User {self.correlation_id} completed session")


class AdminUser(HttpUser):
    """Simulates admin user with heavier operations"""
    
    wait_time = between(10, 30)  # Longer wait times
    weight = 1  # Lower weight = fewer admin users
    
    def on_start(self):
        """Admin authentication"""
        self.token = None
        self.correlation_id = f"admin-{random.randint(10000, 99999)}"
        
        # Admin login
        admin_data = {
            "email": "admin@smartcloudops.ai",
            "password": "AdminPassword123!"
        }
        
        with self.client.post("/auth/login", json=admin_data) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
        
        self.client.headers.update({
            'Authorization': f'Bearer {self.token}',
            'X-Correlation-ID': self.correlation_id
        })
    
    @task(10)
    def admin_dashboard(self):
        """Admin dashboard with comprehensive data"""
        self.client.get("/api/admin/dashboard", name="Admin - Dashboard")
    
    @task(8)
    def system_health_report(self):
        """Generate system health report"""
        self.client.get("/api/admin/health/report", name="Admin - Health Report")
    
    @task(5)
    def user_management(self):
        """User management operations"""
        self.client.get("/api/admin/users", name="Admin - List Users")
    
    @task(3)
    def system_configuration(self):
        """System configuration management"""
        self.client.get("/api/admin/config", name="Admin - Get Config")


# ================================
# EVENT HANDLERS FOR METRICS
# ================================

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Track detailed request metrics"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    elif response_time > 5000:  # Log slow requests (>5s)
        logger.warning(f"Slow request: {name} - {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start"""
    logger.info("Load test started")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test completion and summary"""
    logger.info("Load test completed")
    
    # Log final statistics
    stats = environment.stats.total
    logger.info(f"Total requests: {stats.num_requests}")
    logger.info(f"Total failures: {stats.num_failures}")
    logger.info(f"Average response time: {stats.avg_response_time:.2f}ms")
    logger.info(f"RPS: {stats.current_rps:.2f}")


if __name__ == "__main__":
    # Can be run directly for testing
    import subprocess
    import sys
    
    # Run locust with this file
    cmd = [
        "locust",
        "-f", __file__,
        "--host", "http://localhost:5000",
        "--users", "10",
        "--spawn-rate", "2",
        "--run-time", "60s",
        "--html", "docs/results/load-test-report.html"
    ]
    
    subprocess.run(cmd)
