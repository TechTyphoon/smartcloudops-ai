# 📖 Usage Guide - SmartCloudOps AI

Complete usage guide for SmartCloudOps AI, covering all features, workflows, and practical examples.

---

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Core Features](#-core-features)
- [API Usage](#-api-usage)
- [Monitoring & Dashboards](#-monitoring--dashboards)
- [AI & ML Features](#-ai--ml-features)
- [ChatOps Interface](#-chatops-interface)
- [Advanced Workflows](#-advanced-workflows)
- [Best Practices](#-best-practices)

---

## 🚀 Getting Started

### First Steps After Installation

#### 1. Verify Platform Status
```bash
# Check system health
curl http://localhost:5000/health

# Get detailed status
curl http://localhost:5000/status

# View API documentation
curl http://localhost:5000/api/docs
```

#### 2. Access Dashboards
- **Grafana**: http://localhost:13000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Application**: http://localhost:5000

#### 3. Create Your First User
```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_password_123"
  }'

# Login to get access token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password_123"
  }'
```

---

## 🔧 Core Features

### Health Monitoring

#### System Health Check
```bash
# Basic health check
curl http://localhost:5000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-01-27T10:30:00Z",
  "version": "1.0.0",
  "components": {
    "database": true,
    "chatops": true,
    "ml": true,
    "remediation": true
  }
}
```

#### Detailed System Status
```bash
# Get comprehensive system status
curl http://localhost:5000/status

# Response includes:
# - Component health
# - Performance metrics
# - Resource usage
# - Recent events
```

### Metrics Collection

#### View Prometheus Metrics
```bash
# Get application metrics
curl http://localhost:5000/metrics

# Key metrics available:
# - HTTP request counts
# - Response times
# - ML inference duration
# - System resource usage
```

#### Custom Metrics Summary
```bash
# Get human-readable metrics summary
curl http://localhost:5000/api/metrics/summary

# Response:
{
  "performance": {
    "requests_per_second": 45.2,
    "average_response_time": "18ms",
    "p95_response_time": "32ms"
  },
  "system": {
    "cpu_usage": "45.2%",
    "memory_usage": "1.8GB",
    "disk_usage": "34.5%"
  }
}
```

---

## 🔧 API Usage

### Authentication

#### Getting Access Tokens
```bash
# Login to get access token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

#### Using Access Tokens
```bash
# Use token in API requests
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5000/api/anomalies/
```

### Anomaly Detection

#### Single Anomaly Detection
```bash
# Detect anomalies in system metrics
curl -X POST http://localhost:5000/api/ml/anomalies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "cpu_usage": 85.5,
    "memory_usage": 78.2,
    "disk_usage": 45.0,
    "network_io": 1024,
    "timestamp": "2025-01-27T10:30:00Z"
  }'

# Response:
{
  "prediction": {
    "anomaly_score": 0.12,
    "is_anomaly": false,
    "confidence": 0.95,
    "risk_level": "low"
  },
  "analysis": {
    "primary_factors": ["cpu_usage"],
    "recommendations": [
      "Monitor CPU usage trend over next 10 minutes",
      "Consider scaling if usage remains above 80%"
    ]
  }
}
```

#### Batch Anomaly Detection
```bash
# Process multiple data points
curl -X POST http://localhost:5000/api/ml/anomalies/batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "data_points": [
      {"cpu_usage": 85.5, "memory_usage": 78.2, "disk_usage": 45.0},
      {"cpu_usage": 23.1, "memory_usage": 45.8, "disk_usage": 67.2},
      {"cpu_usage": 91.2, "memory_usage": 89.5, "disk_usage": 23.1}
    ]
  }'
```

### Remediation Actions

#### Create Remediation Action
```bash
# Create automated remediation
curl -X POST http://localhost:5000/api/remediation/actions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "anomaly_id": "anom_123",
    "action_type": "scale_up",
    "target_resource": "web-server-1",
    "parameters": {
      "cpu_threshold": 80,
      "scale_factor": 1.5
    },
    "priority": "high"
  }'
```

#### List Remediation Actions
```bash
# Get all remediation actions
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5000/api/remediation/actions

# Filter by status
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:5000/api/remediation/actions?status=pending"
```

### Feedback System

#### Submit Feedback
```bash
# Submit user feedback (no auth required)
curl -X POST http://localhost:5000/api/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "bug_report",
    "title": "Slow response times during peak hours",
    "description": "The system becomes slow between 2-4 PM daily",
    "severity": "medium",
    "contact_email": "user@example.com"
  }'
```

#### View Feedback (Admin)
```bash
# Get all feedback (requires admin token)
curl -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  http://localhost:5000/api/feedback/

# Get feedback statistics
curl -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  http://localhost:5000/api/feedback/stats
```

---

## 📊 Monitoring & Dashboards

### Grafana Dashboards

#### Accessing Dashboards
1. Open http://localhost:13000
2. Login with `admin/admin`
3. Navigate to **Dashboards** → **SmartCloudOps AI**

#### Available Dashboards
- **System Overview**: Overall system health and performance
- **ML Anomaly Detection**: Anomaly detection metrics and trends
- **Docker Containers**: Container resource usage and health
- **Prometheus Monitoring**: Detailed metrics and alerting

#### Creating Custom Dashboards
```bash
# Export dashboard configuration
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:13000/api/dashboards/db/system-overview" \
  > system-overview-dashboard.json

# Import custom dashboard
curl -X POST http://localhost:13000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d @custom-dashboard.json
```

### Prometheus Queries

#### Basic Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Response time percentiles
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# CPU usage
system_cpu_usage

# Memory usage
system_memory_usage / 1024 / 1024 / 1024
```

#### Advanced Queries
```promql
# Anomaly detection rate
rate(ml_anomalies_detected_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Top slow endpoints
topk(5, rate(http_request_duration_seconds_sum[5m]))
```

### Alerting Rules

#### Setting Up Alerts
```yaml
# prometheus/alerts.yml
groups:
  - name: smartcloudops
    rules:
      - alert: HighCPUUsage
        expr: system_cpu_usage > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: AnomalyDetected
        expr: ml_anomalies_detected_total > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Anomaly detected"
          description: "ML model detected system anomaly"
```

---

## 🤖 AI & ML Features

### Model Management

#### Get Model Information
```bash
# Get current model details
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5000/api/ml/model/info

# Response:
{
  "model_version": "v2.1.0",
  "training_date": "2025-01-20T10:00:00Z",
  "accuracy": 0.95,
  "features": ["cpu_usage", "memory_usage", "disk_usage"],
  "last_updated": "2025-01-27T10:30:00Z"
}
```

#### Retrain Model
```bash
# Trigger model retraining
curl -X POST http://localhost:5000/api/ml/model/retrain \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "reason": "performance_degradation",
    "include_recent_data": true,
    "validation_split": 0.2
  }'
```

### Performance Analytics

#### Get Model Performance
```bash
# Get performance metrics
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5000/api/ml/performance

# Response:
{
  "accuracy": 0.95,
  "precision": 0.92,
  "recall": 0.88,
  "f1_score": 0.90,
  "inference_time_avg": "18ms",
  "predictions_count": 15420
}
```

#### Get Recent Predictions
```bash
# Get recent ML predictions
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:5000/api/ml/predictions?limit=10"

# Response:
{
  "predictions": [
    {
      "timestamp": "2025-01-27T10:30:00Z",
      "anomaly_score": 0.12,
      "is_anomaly": false,
      "confidence": 0.95,
      "input_features": {
        "cpu_usage": 85.5,
        "memory_usage": 78.2
      }
    }
  ]
}
```

---

## 💬 ChatOps Interface

### Natural Language Queries

#### System Status Queries
```bash
# Ask about system status
curl -X POST http://localhost:5000/chatops/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "What is the current system performance?",
    "context": {
      "user_id": "admin",
      "session_id": "sess_123"
    }
  }'

# Response:
{
  "response": "Current system performance is excellent. CPU usage is at 45%, memory usage is 1.8GB, and average response time is 18ms. All containers are healthy and running optimally.",
  "actions_taken": [],
  "recommendations": [
    "System is performing well within normal parameters",
    "No immediate action required"
  ]
}
```

#### Troubleshooting Queries
```bash
# Ask for troubleshooting help
curl -X POST http://localhost:5000/chatops/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "Why is the system slow?",
    "context": {
      "user_id": "admin",
      "session_id": "sess_123"
    }
  }'
```

### Context-Aware Responses

#### Get System Context
```bash
# Get current system context
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5000/chatops/context

# Response includes:
# - Container health status
# - Performance metrics
# - Recent events
# - Available capabilities
```

---

## 🔄 Advanced Workflows

### Automated Incident Response

#### Complete Workflow Example
```bash
#!/bin/bash

# 1. Monitor system continuously
while true; do
  # 2. Check for anomalies
  response=$(curl -s -X POST http://localhost:5000/api/ml/anomalies \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{
      "cpu_usage": $(top -bn1 | grep "Cpu(s)" | awk "{print \$2}" | cut -d"%" -f1),
      "memory_usage": $(free | grep Mem | awk "{printf \"%.1f\", \$3/\$2 * 100.0}"),
      "disk_usage": $(df / | tail -1 | awk "{print \$5}" | cut -d"%" -f1)
    }')
  
  # 3. Parse response
  anomaly_score=$(echo $response | jq -r '.prediction.anomaly_score')
  is_anomaly=$(echo $response | jq -r '.prediction.is_anomaly')
  
  # 4. Take action if anomaly detected
  if [ "$is_anomaly" = "true" ]; then
    echo "Anomaly detected! Score: $anomaly_score"
    
    # 5. Create remediation action
    curl -X POST http://localhost:5000/api/remediation/actions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d '{
        "action_type": "investigate",
        "priority": "high",
        "description": "Automated response to detected anomaly"
      }'
  fi
  
  sleep 60  # Check every minute
done
```

### Integration with External Tools

#### Slack Integration
```python
import requests
import json

def send_slack_alert(message, channel="#alerts"):
    webhook_url = "YOUR_SLACK_WEBHOOK_URL"
    
    payload = {
        "channel": channel,
        "text": message,
        "username": "SmartCloudOps AI",
        "icon_emoji": ":robot_face:"
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# Monitor and alert
def monitor_and_alert():
    # Check system health
    health_response = requests.get("http://localhost:5000/health")
    health_data = health_response.json()
    
    if health_data["status"] != "healthy":
        send_slack_alert(f"🚨 System health check failed: {health_data}")
```

#### PagerDuty Integration
```python
import requests

def create_pagerduty_incident(title, description, urgency="high"):
    api_key = "YOUR_PAGERDUTY_API_KEY"
    service_id = "YOUR_SERVICE_ID"
    
    payload = {
        "incident": {
            "type": "incident",
            "title": title,
            "service": {
                "id": service_id,
                "type": "service_reference"
            },
            "urgency": urgency,
            "body": {
                "type": "incident_body",
                "details": description
            }
        }
    }
    
    headers = {
        "Authorization": f"Token token={api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.pagerduty.com/incidents",
        json=payload,
        headers=headers
    )
    
    return response.json()
```

### Custom Dashboards

#### Creating Custom Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Custom SmartCloudOps Dashboard",
    "panels": [
      {
        "title": "Anomaly Detection Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ml_anomalies_detected_total[5m])",
            "legendFormat": "Anomalies/min"
          }
        ]
      },
      {
        "title": "System Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "system_health_status",
            "legendFormat": "Health Score"
          }
        ]
      }
    ]
  }
}
```

---

## 📋 Best Practices

### Security Best Practices

#### Token Management
```bash
# Store tokens securely
export ACCESS_TOKEN="your_token_here"

# Use token in scripts
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:5000/api/anomalies/

# Rotate tokens regularly
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN"
```

#### Input Validation
```bash
# Always validate input data
curl -X POST http://localhost:5000/api/ml/anomalies \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_usage": 85.5,  # Must be 0-100
    "memory_usage": 78.2,  # Must be 0-100
    "disk_usage": 45.0   # Must be 0-100
  }'
```

### Performance Optimization

#### Caching Strategies
```bash
# Use Redis for caching
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:5000/api/metrics/summary?cache=true"

# Batch requests when possible
curl -X POST http://localhost:5000/api/ml/anomalies/batch \
  -H "Content-Type: application/json" \
  -d '{"data_points": [...]}'
```

#### Monitoring Best Practices
```bash
# Set up regular health checks
*/5 * * * * curl -f http://localhost:5000/health || echo "Health check failed"

# Monitor key metrics
# - Response times
# - Error rates
# - Resource usage
# - ML model performance
```

### Error Handling

#### Graceful Error Handling
```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, headers=None, data=None):
    try:
        if data:
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    
    except RequestException as e:
        print(f"API call failed: {e}")
        return None
    except ValueError as e:
        print(f"Invalid JSON response: {e}")
        return None
```

---

## 📞 Getting Help

### Common Issues and Solutions

#### API Rate Limiting
```bash
# Check rate limit headers
curl -I http://localhost:5000/api/anomalies/

# Response headers:
# X-RateLimit-Limit: 1000
# X-RateLimit-Remaining: 847
# X-RateLimit-Reset: 1629876543
```

#### Authentication Issues
```bash
# Check token validity
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/auth/me

# Refresh expired token
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer REFRESH_TOKEN"
```

### Support Resources
- **📖 Documentation**: [Getting Started Guide](docs/GETTING_STARTED.md)
- **🔧 API Reference**: [Complete API Docs](docs/API_REFERENCE.md)
- **💬 Community**: [GitHub Discussions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)
- **🐛 Issues**: [GitHub Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)

---

<div align="center">

**🚀 Ready to explore SmartCloudOps AI? Start with the Getting Started section above! 🚀**

[Back to Main README](../README.md) | [Next: API Reference](docs/API_REFERENCE.md)

</div>
