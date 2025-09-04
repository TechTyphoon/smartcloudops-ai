# SmartCloudOps AI - User Tutorials

## Getting Started Guide

Welcome to SmartCloudOps AI! This comprehensive tutorial will guide you through getting started with our enterprise DevOps AI platform, covering everything from basic setup to advanced automation scenarios.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [System Monitoring](#system-monitoring)
3. [Anomaly Detection](#anomaly-detection)
4. [Automated Remediation](#automated-remediation)
5. [ChatOps Commands](#chatops-commands)
6. [ML Model Management](#ml-model-management)
7. [Performance Optimization](#performance-optimization)
8. [CI/CD Integration](#cicd-integration)
9. [Advanced Scenarios](#advanced-scenarios)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for SDK usage)
- Git (for cloning repositories)

### Step 1: Start SmartCloudOps AI
```bash
# Clone the repository (if not already done)
git clone https://github.com/your-org/smartcloudops-ai.git
cd smartcloudops-ai

# Start all services
docker-compose up -d

# Wait for services to be healthy
sleep 30

# Verify everything is running
curl -f http://localhost:5000/health
```

### Step 2: Verify Installation
```bash
# Check all services
docker-compose ps

# Test core functionality
curl -s http://localhost:5000/health | jq '.data.checks'

# Access monitoring dashboards
echo "Grafana: http://localhost:13000 (admin/admin123)"
echo "Prometheus: http://localhost:9090"
```

### Step 3: Your First API Call
```python
import requests

# Simple health check
response = requests.get("http://localhost:5000/health")
print(f"System Status: {response.json()['data']['checks']['database']}")

# Get system status
status = requests.get("http://localhost:5000/status")
print(f"Active Services: {status.json()['data']['active_services']}")
```

---

## System Monitoring

### Real-time Metrics Monitoring

**Goal**: Set up comprehensive system monitoring and receive alerts.

#### Step 1: Configure Monitoring
```bash
# Check current metrics
curl -s http://localhost:5000/api/performance/metrics | jq '.data.cpu'

# View cache performance
curl -s http://localhost:5000/api/performance/cache/stats | jq '.data.hit_rate'
```

#### Step 2: Set Up Automated Monitoring
```python
import time
import requests
from datetime import datetime

def monitor_system():
    """Monitor system metrics every 30 seconds"""
    while True:
        try:
            # Get performance metrics
            response = requests.get("http://localhost:5000/api/performance/metrics")
            metrics = response.json()['data']

            # Check CPU usage
            cpu_usage = metrics['cpu']['usage_percent']
            if cpu_usage > 80:
                print(f"⚠️  HIGH CPU USAGE: {cpu_usage}%")

            # Check memory usage
            mem_usage = metrics['memory']['usage_percent']
            if mem_usage > 85:
                print(f"⚠️  HIGH MEMORY USAGE: {mem_usage}%")

            # Log metrics
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] CPU: {cpu_usage:.1f}% | Memory: {mem_usage:.1f}%")

        except Exception as e:
            print(f"Monitoring error: {e}")

        time.sleep(30)

if __name__ == "__main__":
    monitor_system()
```

#### Step 3: Create Custom Alerts
```python
def check_alerts():
    """Check for system alerts and anomalies"""
    # Get current anomalies
    response = requests.get("http://localhost:5000/api/anomalies?severity=high")
    anomalies = response.json()['data']['anomalies']

    if anomalies:
        print(f"🚨 {len(anomalies)} high-severity anomalies detected!")
        for anomaly in anomalies[:3]:  # Show first 3
            print(f"  - {anomaly['title']}: {anomaly['description']}")

    # Get performance alerts
    alerts_response = requests.get("http://localhost:5000/api/performance/alerts")
    alerts = alerts_response.json()['data']['alerts']

    if alerts:
        print(f"⚠️  {len(alerts)} performance alerts active!")
        for alert in alerts[:3]:
            print(f"  - {alert['message']}")

check_alerts()
```

---

## Anomaly Detection

### Scenario: Detecting System Anomalies

**Goal**: Automatically detect and respond to system anomalies.

#### Step 1: Train Anomaly Detection Model
```python
import requests
import json

def train_anomaly_model():
    """Train a custom anomaly detection model"""

    training_request = {
        "model_type": "anomaly_detection",
        "algorithm": "isolation_forest",
        "parameters": {
            "contamination": 0.1,
            "random_state": 42,
            "n_estimators": 100
        },
        "dataset": "system_metrics"
    }

    response = requests.post(
        "http://localhost:5000/api/ml/train",
        json=training_request
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Model training started: {result['data']['model_id']}")
        return result['data']['model_id']
    else:
        print(f"❌ Training failed: {response.json()}")
        return None

model_id = train_anomaly_model()
```

#### Step 2: Real-time Anomaly Detection
```python
def detect_anomalies(model_id):
    """Detect anomalies in real-time"""

    # Sample system metrics
    test_data = [
        {"cpu_percent": 45.2, "memory_percent": 67.8, "disk_usage": 54.3},
        {"cpu_percent": 89.5, "memory_percent": 78.9, "disk_usage": 54.5},
        {"cpu_percent": 12.3, "memory_percent": 45.6, "disk_usage": 54.1}
    ]

    for i, data in enumerate(test_data):
        prediction_request = {
            "model_id": model_id,
            "data": data
        }

        response = requests.post(
            "http://localhost:5000/api/ml/predict",
            json=prediction_request
        )

        if response.status_code == 200:
            result = response.json()['data']
            status = "🚨 ANOMALY" if result['is_anomaly'] else "✅ Normal"
            confidence = result['confidence']
            print(f"Sample {i+1}: {status} (confidence: {confidence:.2f})")
        else:
            print(f"❌ Prediction failed for sample {i+1}")

if model_id:
    detect_anomalies(model_id)
```

#### Step 3: Automated Response to Anomalies
```python
def handle_anomalies():
    """Automatically handle detected anomalies"""

    # Get recent high-severity anomalies
    response = requests.get("http://localhost:5000/api/anomalies?severity=high&status=open")
    anomalies = response.json()['data']['anomalies']

    for anomaly in anomalies:
        anomaly_id = anomaly['id']
        title = anomaly['title']

        # Acknowledge the anomaly
        ack_response = requests.post(f"http://localhost:5000/api/anomalies/{anomaly_id}/acknowledge")

        if ack_response.status_code == 200:
            print(f"✅ Acknowledged anomaly: {title}")

            # Check if auto-remediation is possible
            if "CPU" in title:
                # Scale up service automatically
                remediation_request = {
                    "reason": f"Auto-remediation for: {title}",
                    "priority": "high",
                    "parameters": {
                        "target_replicas": 3
                    }
                }

                rem_response = requests.post(
                    f"http://localhost:5000/api/remediation/actions/scale_web_service/execute",
                    json=remediation_request
                )

                if rem_response.status_code == 200:
                    print(f"🚀 Auto-scaling triggered for high CPU usage")
                else:
                    print(f"❌ Auto-scaling failed: {rem_response.json()}")

        else:
            print(f"❌ Failed to acknowledge anomaly: {title}")

handle_anomalies()
```

---

## Automated Remediation

### Scenario: Auto-scaling Based on Load

**Goal**: Automatically scale services based on system load.

#### Step 1: Monitor System Load
```python
def monitor_and_scale():
    """Monitor CPU usage and scale automatically"""

    # Get current metrics
    response = requests.get("http://localhost:5000/api/performance/metrics")
    metrics = response.json()['data']

    cpu_usage = metrics['cpu']['usage_percent']
    memory_usage = metrics['memory']['usage_percent']

    print(f"Current load - CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%")

    # Scaling thresholds
    if cpu_usage > 80 or memory_usage > 85:
        print("🔥 High load detected! Scaling up...")

        # Execute scaling remediation
        scale_request = {
            "reason": ".1f",
            "priority": "high",
            "parameters": {
                "service_name": "web-server",
                "target_replicas": 5,
                "min_replicas": 2,
                "max_replicas": 10
            }
        }

        scale_response = requests.post(
            "http://localhost:5000/api/remediation/actions/scale_web_service/execute",
            json=scale_request
        )

        if scale_response.status_code == 200:
            result = scale_response.json()['data']
            print(f"✅ Scaling initiated - Execution ID: {result['execution_id']}")
        else:
            print(f"❌ Scaling failed: {scale_response.json()}")

    elif cpu_usage < 30 and memory_usage < 50:
        print("📉 Low load detected. Considering scale down...")

        # Scale down if appropriate
        scale_down_request = {
            "reason": ".1f",
            "priority": "medium",
            "parameters": {
                "service_name": "web-server",
                "target_replicas": 2
            }
        }

        scale_response = requests.post(
            "http://localhost:5000/api/remediation/actions/scale_down/execute",
            json=scale_down_request
        )

        if scale_response.status_code == 200:
            print("✅ Scale down initiated")
        else:
            print(f"❌ Scale down failed: {scale_response.json()}")

monitor_and_scale()
```

#### Step 2: Database Optimization
```python
def optimize_database():
    """Automatically optimize database performance"""

    # Get current performance metrics
    response = requests.get("http://localhost:5000/api/performance/metrics")
    metrics = response.json()['data']

    # Check if database optimization is needed
    if metrics['memory']['usage_percent'] > 80:
        print("🗄️  High memory usage detected. Optimizing database...")

        # Execute database optimization
        optimization_request = {
            "reason": "High memory usage detected",
            "priority": "high",
            "parameters": {
                "optimization_type": "memory",
                "max_connections": 50,
                "shared_buffers": "256MB"
            }
        }

        opt_response = requests.post(
            "http://localhost:5000/api/remediation/actions/optimize_database/execute",
            json=optimization_request
        )

        if opt_response.status_code == 200:
            print("✅ Database optimization initiated")
        else:
            print(f"❌ Database optimization failed: {opt_response.json()}")

    # Check for slow queries
    query_response = requests.get("http://localhost:5000/api/performance/slow_queries")

    if query_response.status_code == 200:
        slow_queries = query_response.json()['data']['queries']

        if slow_queries:
            print(f"🐌 Found {len(slow_queries)} slow queries")

            # Optimize slow queries
            for query in slow_queries[:3]:  # Handle first 3
                query_opt_request = {
                    "reason": f"Slow query detected: {query['query'][:50]}...",
                    "priority": "medium",
                    "parameters": {
                        "query_id": query['id'],
                        "optimization_type": "index"
                    }
                }

                opt_response = requests.post(
                    "http://localhost:5000/api/remediation/actions/optimize_query/execute",
                    json=query_opt_request
                )

                if opt_response.status_code == 200:
                    print(f"✅ Query optimization initiated for query {query['id']}")
                else:
                    print(f"❌ Query optimization failed: {opt_response.json()}")

optimize_database()
```

---

## ChatOps Commands

### Natural Language System Management

**Goal**: Use natural language commands to manage your infrastructure.

#### Basic Commands
```python
import requests

def chatops_command(command, context=None):
    """Execute a natural language command"""

    payload = {"command": command}
    if context:
        payload["context"] = context

    response = requests.post("http://localhost:5000/api/chatops", json=payload)

    if response.status_code == 200:
        result = response.json()['data']
        print(f"🤖 Response: {result['response']}")

        if result.get('actions_taken'):
            print(f"⚡ Actions taken: {len(result['actions_taken'])}")

        if result.get('suggested_commands'):
            print("💡 Suggestions:")
            for suggestion in result['suggested_commands'][:3]:
                print(f"  - {suggestion}")

    else:
        print(f"❌ Command failed: {response.json()}")

# System status commands
chatops_command("show me the current system status")
chatops_command("what's the CPU usage right now?")
chatops_command("are there any active anomalies?")

# Remediation commands
chatops_command("scale the web service to 5 replicas")
chatops_command("clear the application cache")
chatops_command("restart the database service")

# Monitoring commands
chatops_command("show me performance metrics for the last hour")
chatops_command("what are the top 5 slow queries?")
chatops_command("check the health of all services")
```

#### Advanced ChatOps Scenarios
```python
def automated_maintenance():
    """Perform automated maintenance using ChatOps"""

    # Check system health
    chatops_command("perform a full system health check")

    # Check for issues
    chatops_command("are there any critical anomalies that need attention?")

    # Performance optimization
    chatops_command("optimize database performance if needed")
    chatops_command("clear old log files to free up disk space")

    # Security checks
    chatops_command("run security scan and report any issues")
    chatops_command("check for outdated dependencies")

    # Backup verification
    chatops_command("verify that backups are running correctly")
    chatops_command("check backup integrity for last 7 days")

def incident_response():
    """Automated incident response using ChatOps"""

    # Detect incident
    chatops_command("check for any service outages or performance issues")

    # Assess impact
    chatops_command("what services are affected and what's the impact?")

    # Execute remediation
    chatops_command("automatically remediate any detected issues")

    # Notify stakeholders
    chatops_command("send incident notification to the on-call engineer")

    # Document incident
    chatops_command("create incident report with timeline and resolution steps")

# Run automated maintenance
automated_maintenance()

# Handle potential incidents
incident_response()
```

---

## ML Model Management

### Scenario: Managing ML Models in Production

**Goal**: Deploy, monitor, and update ML models in production.

#### Step 1: Register a New Model
```python
def register_model():
    """Register a new ML model"""

    model_data = {
        "name": "fraud_detection_v2",
        "version": "3.3.0",
        "description": "Enhanced fraud detection model with improved accuracy",
        "algorithm": "xgboost",
        "framework": "scikit-learn",
        "metrics": {
            "accuracy": 0.945,
            "precision": 0.892,
            "recall": 0.876,
            "f1_score": 0.884
        },
        "tags": ["fraud-detection", "production", "xgboost"],
        "metadata": {
            "training_data_size": 100000,
            "features_count": 25,
            "training_time_hours": 4.5
        }
    }

    response = requests.post("http://localhost:5000/api/mlops/models", json=model_data)

    if response.status_code == 200:
        result = response.json()['data']
        print(f"✅ Model registered successfully: {result['id']}")
        return result['id']
    else:
        print(f"❌ Model registration failed: {response.json()}")
        return None

model_id = register_model()
```

#### Step 2: Deploy Model to Production
```python
def deploy_model(model_id):
    """Deploy model to production environment"""

    deployment_config = {
        "environment": "production",
        "min_replicas": 2,
        "max_replicas": 10,
        "cpu_limit": "2",
        "memory_limit": "4Gi",
        "auto_scaling": {
            "enabled": True,
            "target_cpu_utilization": 70,
            "target_memory_utilization": 80
        },
        "health_checks": {
            "enabled": True,
            "interval_seconds": 30,
            "timeout_seconds": 10
        }
    }

    response = requests.post(
        f"http://localhost:5000/api/mlops/models/{model_id}/deploy",
        json=deployment_config
    )

    if response.status_code == 200:
        result = response.json()['data']
        print(f"🚀 Model deployment initiated: {result['deployment_id']}")

        # Monitor deployment status
        monitor_deployment(model_id, result['deployment_id'])
    else:
        print(f"❌ Deployment failed: {response.json()}")

def monitor_deployment(model_id, deployment_id):
    """Monitor model deployment progress"""

    import time

    for _ in range(30):  # Check for 5 minutes
        response = requests.get(f"http://localhost:5000/api/mlops/models/{model_id}/status")

        if response.status_code == 200:
            status = response.json()['data']['status']

            if status == "deployed":
                print("✅ Model deployment completed successfully!")
                break
            elif status == "failed":
                print("❌ Model deployment failed")
                break
            else:
                print(f"⏳ Deployment status: {status}")

        time.sleep(10)

if model_id:
    deploy_model(model_id)
```

#### Step 3: Monitor Model Performance
```python
def monitor_model_performance(model_id):
    """Monitor deployed model performance"""

    # Get model metrics
    response = requests.get(f"http://localhost:5000/api/mlops/models/{model_id}/metrics")

    if response.status_code == 200:
        metrics = response.json()['data']

        print("📊 Model Performance Metrics:")
        print(f"  Requests per minute: {metrics['requests_per_minute']}")
        print(f"  Average latency: {metrics['avg_latency_ms']}ms")
        print(f"  Error rate: {metrics['error_rate']:.2%}")
        print(f"  Accuracy: {metrics['accuracy']:.3f}")

        # Check for performance degradation
        if metrics['accuracy'] < 0.90:
            print("⚠️  Model accuracy has degraded!")
            print("  Consider retraining with fresh data")

        if metrics['error_rate'] > 0.05:
            print("⚠️  High error rate detected!")
            print("  Investigating model issues")

        if metrics['avg_latency_ms'] > 1000:
            print("⚠️  High latency detected!")
            print("  Consider optimizing model or scaling")

    else:
        print(f"❌ Failed to get model metrics: {response.json()}")

def compare_model_versions(old_model_id, new_model_id):
    """Compare performance of two model versions"""

    def get_metrics(model_id):
        response = requests.get(f"http://localhost:5000/api/mlops/models/{model_id}/metrics")
        return response.json()['data'] if response.status_code == 200 else None

    old_metrics = get_metrics(old_model_id)
    new_metrics = get_metrics(new_model_id)

    if old_metrics and new_metrics:
        print("🔄 Model Version Comparison:")
        print(f"  Accuracy: {old_metrics['accuracy']:.3f} → {new_metrics['accuracy']:.3f}")
        print(f"  Latency: {old_metrics['avg_latency_ms']}ms → {new_metrics['avg_latency_ms']}ms")
        print(f"  Error Rate: {old_metrics['error_rate']:.2%} → {new_metrics['error_rate']:.2%}")

        # Determine if new model is better
        if (new_metrics['accuracy'] > old_metrics['accuracy'] and
            new_metrics['avg_latency_ms'] < old_metrics['avg_latency_ms']):
            print("✅ New model version performs better!")
        else:
            print("⚠️  New model version needs improvement")

if model_id:
    monitor_model_performance(model_id)
```

---

## Performance Optimization

### Scenario: Database Performance Tuning

**Goal**: Automatically optimize database performance.

#### Step 1: Analyze Database Performance
```python
def analyze_database_performance():
    """Comprehensive database performance analysis"""

    print("🔍 Analyzing database performance...")

    # Get database metrics
    response = requests.get("http://localhost:5000/api/performance/database/metrics")

    if response.status_code == 200:
        db_metrics = response.json()['data']

        print("📊 Database Performance Metrics:")
        print(f"  Active connections: {db_metrics['active_connections']}")
        print(f"  Connection pool utilization: {db_metrics['pool_utilization']:.1%}")
        print(f"  Average query time: {db_metrics['avg_query_time_ms']}ms")
        print(f"  Slow queries (>1s): {db_metrics['slow_queries_count']}")

        # Check for issues
        issues = []

        if db_metrics['pool_utilization'] > 0.9:
            issues.append("Connection pool nearly exhausted")

        if db_metrics['avg_query_time_ms'] > 500:
            issues.append("Slow average query time")

        if db_metrics['slow_queries_count'] > 10:
            issues.append("High number of slow queries")

        if issues:
            print("⚠️  Issues detected:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Database performance looks good")

    return db_metrics

db_metrics = analyze_database_performance()
```

#### Step 2: Optimize Slow Queries
```python
def optimize_slow_queries():
    """Identify and optimize slow database queries"""

    # Get slow queries
    response = requests.get("http://localhost:5000/api/performance/database/slow-queries")

    if response.status_code == 200:
        slow_queries = response.json()['data']['queries']

        if not slow_queries:
            print("✅ No slow queries detected")
            return

        print(f"🐌 Found {len(slow_queries)} slow queries")

        for i, query in enumerate(slow_queries[:5]):  # Handle top 5
            print(f"\nQuery {i+1}:")
            print(f"  Execution time: {query['execution_time_ms']}ms")
            print(f"  Query: {query['query'][:100]}...")

            # Analyze query for optimization opportunities
            analysis_response = requests.post(
                "http://localhost:5000/api/performance/database/analyze-query",
                json={"query": query['query']}
            )

            if analysis_response.status_code == 200:
                analysis = analysis_response.json()['data']
                print(f"  Missing indexes: {len(analysis['missing_indexes'])}")
                print(f"  Optimization suggestions: {len(analysis['suggestions'])}")

                # Apply optimizations
                if analysis['missing_indexes']:
                    for index in analysis['missing_indexes'][:2]:  # Top 2
                        index_request = {
                            "table": index['table'],
                            "columns": index['columns'],
                            "reason": f"Optimize slow query: {query['query'][:50]}..."
                        }

                        create_response = requests.post(
                            "http://localhost:5000/api/performance/database/create-index",
                            json=index_request
                        )

                        if create_response.status_code == 200:
                            print(f"  ✅ Created index on {index['table']}({', '.join(index['columns'])})")
                        else:
                            print(f"  ❌ Failed to create index: {create_response.json()}")

optimize_slow_queries()
```

#### Step 3: Connection Pool Optimization
```python
def optimize_connection_pool():
    """Optimize database connection pool settings"""

    current_response = requests.get("http://localhost:5000/api/performance/database/pool-status")

    if current_response.status_code == 200:
        pool_status = current_response.json()['data']

        print("🏊 Connection Pool Status:")
        print(f"  Total connections: {pool_status['total_connections']}")
        print(f"  Active connections: {pool_status['active_connections']}")
        print(f"  Idle connections: {pool_status['idle_connections']}")
        print(f"  Waiting requests: {pool_status['waiting_requests']}")

        # Analyze and optimize
        recommendations = []

        if pool_status['waiting_requests'] > 0:
            recommendations.append("Increase max connections")

        if pool_status['idle_connections'] > pool_status['total_connections'] * 0.7:
            recommendations.append("Reduce min connections")

        if pool_status['active_connections'] > pool_status['total_connections'] * 0.9:
            recommendations.append("Scale up database instance")

        if recommendations:
            print("💡 Optimization Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

            # Apply optimizations
            optimization_request = {
                "action": "optimize_pool",
                "current_issues": recommendations,
                "target_utilization": 0.8
            }

            opt_response = requests.post(
                "http://localhost:5000/api/performance/database/optimize-pool",
                json=optimization_request
            )

            if opt_response.status_code == 200:
                print("✅ Connection pool optimization initiated")
            else:
                print(f"❌ Optimization failed: {opt_response.json()}")
        else:
            print("✅ Connection pool configuration is optimal")

optimize_connection_pool()
```

---

## CI/CD Integration

### Scenario: Automated Deployment Pipeline

**Goal**: Integrate SmartCloudOps AI into your CI/CD pipeline.

#### GitHub Actions Integration
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to SmartCloudOps
      run: |
        # Notify SmartCloudOps of deployment
        curl -X POST http://your-smartcloudops-instance/api/deployments \
          -H "Content-Type: application/json" \
          -d '{
            "service": "my-app",
            "version": "${{ github.sha }}",
            "environment": "production"
          }'

    - name: Monitor deployment
      run: |
        # Wait for deployment to complete
        for i in {1..30}; do
          status=$(curl -s http://your-smartcloudops-instance/api/deployments/my-app/status)
          if [ "$status" = "healthy" ]; then
            echo "✅ Deployment successful"
            break
          fi
          sleep 10
        done
```

#### Automated Testing with SmartCloudOps
```python
def run_deployment_tests():
    """Run comprehensive tests after deployment"""

    test_results = {
        "health_check": False,
        "api_endpoints": False,
        "performance": False,
        "security": False
    }

    # Health check
    try:
        response = requests.get("http://your-app-instance/health", timeout=10)
        if response.status_code == 200:
            test_results["health_check"] = True
            print("✅ Health check passed")
    except:
        print("❌ Health check failed")

    # API endpoint tests
    api_endpoints = [
        "/api/users",
        "/api/products",
        "/api/orders"
    ]

    api_passed = 0
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"http://your-app-instance{endpoint}", timeout=5)
            if response.status_code == 200:
                api_passed += 1
        except:
            pass

    if api_passed == len(api_endpoints):
        test_results["api_endpoints"] = True
        print("✅ All API endpoints responding")
    else:
        print(f"⚠️  {len(api_endpoints) - api_passed} API endpoints failed")

    # Performance test
    import time
    start_time = time.time()

    for _ in range(10):
        requests.get("http://your-app-instance/api/health")

    avg_response_time = (time.time() - start_time) / 10 * 1000

    if avg_response_time < 500:  # Less than 500ms
        test_results["performance"] = True
        print(".1f"    else:
        print(".1f"
    # Security scan
    security_response = requests.post(
        "http://your-smartcloudops-instance/api/security/scan",
        json={"target": "http://your-app-instance"}
    )

    if security_response.status_code == 200:
        security_result = security_response.json()['data']
        if security_result['vulnerabilities'] == 0:
            test_results["security"] = True
            print("✅ Security scan passed")
        else:
            print(f"⚠️  {security_result['vulnerabilities']} security issues found")

    # Report results to SmartCloudOps
    deployment_report = {
        "service": "my-app",
        "version": "1.2.3",
        "environment": "production",
        "tests": test_results,
        "timestamp": datetime.now().isoformat()
    }

    report_response = requests.post(
        "http://your-smartcloudops-instance/api/deployments/report",
        json=deployment_report
    )

    if report_response.status_code == 200:
        print("✅ Test results reported to SmartCloudOps")
    else:
        print("❌ Failed to report test results")

    return test_results

# Run deployment tests
results = run_deployment_tests()
passed_tests = sum(results.values())
total_tests = len(results)

print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")

if passed_tests == total_tests:
    print("🎉 All tests passed! Deployment successful.")
else:
    print("⚠️  Some tests failed. Manual review required.")
```

---

## Advanced Scenarios

### Scenario 1: Multi-Environment Deployment Strategy
```python
def multi_environment_deployment():
    """Deploy across multiple environments with SmartCloudOps"""

    environments = ["staging", "production", "dr"]

    for env in environments:
        print(f"🚀 Deploying to {env}...")

        # Health check environment
        health_response = requests.get(f"http://{env}.your-app.com/health")

        if health_response.status_code != 200:
            print(f"❌ {env} environment is not healthy")
            continue

        # Deploy to environment
        deploy_request = {
            "service": "my-app",
            "version": "1.2.3",
            "environment": env,
            "strategy": "rolling" if env == "production" else "recreate"
        }

        deploy_response = requests.post(
            f"http://smartcloudops-{env}/api/deployments",
            json=deploy_request
        )

        if deploy_response.status_code == 200:
            deployment_id = deploy_response.json()['data']['deployment_id']

            # Monitor deployment
            monitor_deployment_status(env, deployment_id)
        else:
            print(f"❌ Deployment to {env} failed")

def monitor_deployment_status(environment, deployment_id):
    """Monitor deployment status across environments"""

    import time

    for attempt in range(60):  # 10 minutes
        status_response = requests.get(
            f"http://smartcloudops-{environment}/api/deployments/{deployment_id}/status"
        )

        if status_response.status_code == 200:
            status = status_response.json()['data']['status']

            if status == "completed":
                print(f"✅ Deployment to {environment} completed successfully")
                break
            elif status == "failed":
                print(f"❌ Deployment to {environment} failed")
                break
            elif status == "rolling_back":
                print(f"⚠️  Deployment to {environment} rolling back")
                break
            else:
                if attempt % 10 == 0:  # Log every 10 attempts
                    print(f"⏳ {environment} deployment status: {status}")

        time.sleep(10)
    else:
        print(f"⏰ Deployment to {environment} timed out")

multi_environment_deployment()
```

### Scenario 2: Predictive Auto-scaling
```python
def predictive_autoscaling():
    """Implement predictive auto-scaling based on ML predictions"""

    # Get historical metrics
    historical_response = requests.get(
        "http://localhost:5000/api/performance/metrics/history?hours=24"
    )

    if historical_response.status_code == 200:
        historical_data = historical_response.json()['data']

        # Train predictive model for resource usage
        training_data = []
        for metric in historical_data:
            training_data.append({
                "timestamp": metric['timestamp'],
                "cpu_usage": metric['cpu']['usage_percent'],
                "memory_usage": metric['memory']['usage_percent'],
                "request_count": metric['requests_per_minute']
            })

        # Train prediction model
        model_request = {
            "model_type": "time_series_prediction",
            "algorithm": "prophet",
            "target": "cpu_usage",
            "training_data": training_data
        }

        model_response = requests.post(
            "http://localhost:5000/api/ml/train",
            json=model_request
        )

        if model_response.status_code == 200:
            model_id = model_response.json()['data']['model_id']

            # Predict future resource needs
            prediction_request = {
                "model_id": model_id,
                "prediction_hours": 2
            }

            pred_response = requests.post(
                "http://localhost:5000/api/ml/predict/future",
                json=prediction_request
            )

            if pred_response.status_code == 200:
                predictions = pred_response.json()['data']['predictions']

                # Analyze predictions and scale proactively
                max_predicted_cpu = max(p['cpu_usage'] for p in predictions)

                if max_predicted_cpu > 80:
                    print(".1f"                    # Scale up proactively
                    scale_request = {
                        "reason": ".1f",
                        "priority": "high",
                        "parameters": {
                            "target_replicas": 4,
                            "scale_type": "predictive"
                        }
                    }

                    scale_response = requests.post(
                        "http://localhost:5000/api/remediation/actions/scale_web_service/execute",
                        json=scale_request
                    )

                    if scale_response.status_code == 200:
                        print("✅ Predictive scaling initiated")
                    else:
                        print("❌ Predictive scaling failed")

predictive_autoscaling()
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Startup Issues
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs smartcloudops-main

# Restart specific service
docker-compose restart smartcloudops-main

# Check resource usage
docker stats
```

#### 2. Database Connection Issues
```python
# Test database connection
import requests

response = requests.get("http://localhost:5000/api/database/status")
if response.status_code == 200:
    print("✅ Database connection OK")
else:
    print(f"❌ Database issue: {response.json()}")

# Reset database connection pool
reset_response = requests.post("http://localhost:5000/api/database/reset-pool")
if reset_response.status_code == 200:
    print("✅ Database pool reset")
```

#### 3. High Memory Usage
```python
# Check memory usage
metrics_response = requests.get("http://localhost:5000/api/performance/metrics")
metrics = metrics_response.json()['data']

if metrics['memory']['usage_percent'] > 85:
    # Clear caches
    cache_response = requests.post("http://localhost:5000/api/performance/cache/clear")

    # Optimize memory usage
    mem_response = requests.post("http://localhost:5000/api/performance/optimize-memory")

    print("✅ Memory optimization initiated")
```

#### 4. Slow API Responses
```python
# Check API performance
perf_response = requests.get("http://localhost:5000/api/performance/api-metrics")

if perf_response.status_code == 200:
    api_metrics = perf_response.json()['data']

    if api_metrics['avg_response_time'] > 1000:  # > 1 second
        # Enable caching
        cache_response = requests.post("http://localhost:5000/api/performance/enable-caching")

        # Optimize queries
        opt_response = requests.post("http://localhost:5000/api/performance/optimize-queries")

        print("✅ API optimization initiated")
```

#### 5. Model Performance Issues
```python
# Check model health
model_response = requests.get("http://localhost:5000/api/ml/models/status")

if model_response.status_code == 200:
    models = model_response.json()['data']['models']

    for model in models:
        if model['accuracy'] < 0.85:  # Below threshold
            print(f"⚠️  Model {model['name']} accuracy degraded: {model['accuracy']}")

            # Retrain model
            retrain_response = requests.post(
                f"http://localhost:5000/api/ml/models/{model['id']}/retrain"
            )

            if retrain_response.status_code == 200:
                print(f"✅ Retraining initiated for {model['name']}")
```

### Getting Help
1. **Check the logs**: `docker-compose logs -f`
2. **Health endpoint**: `GET /health`
3. **System status**: `GET /status`
4. **Performance metrics**: `GET /api/performance/metrics`
5. **API documentation**: Visit `/api/docs` in your browser

### Emergency Commands
```bash
# Emergency restart all services
docker-compose down
docker-compose up -d

# Force cache clear
curl -X POST http://localhost:5000/api/performance/cache/clear

# Emergency database reset
curl -X POST http://localhost:5000/api/database/emergency-reset

# Get full system report
curl -s http://localhost:5000/api/diagnostics/full-report | jq '.'
```

---

This comprehensive tutorial covers everything from basic setup to advanced automation scenarios. Each section includes practical code examples that you can run immediately. For additional help, check the API documentation at `/api/docs` or the logs at `/logs/`.
