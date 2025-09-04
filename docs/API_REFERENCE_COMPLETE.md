# SmartCloudOps AI - Complete API Reference

## Overview

SmartCloudOps AI is an enterprise-grade DevOps AI platform that provides comprehensive monitoring, anomaly detection, ML operations, and automated remediation capabilities. This API reference documents all available endpoints across the platform.

## Base URL
```
http://localhost:5000
```

## Authentication
Most endpoints require authentication. Include the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Response Format
All API responses follow this standard format:
```json
{
  "status": "success|error",
  "data": { ... },
  "error": null|string,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Rate Limiting
API endpoints are rate-limited to prevent abuse:
- **General endpoints**: 100 requests per minute
- **Admin endpoints**: 50 requests per minute
- **AI/ML endpoints**: 20 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1640995200
```

---

## 1. Core API (`/`)
### 1.1 Root Endpoint
**GET** `/`

Returns system information and available endpoints.

**Response:**
```json
{
  "status": "success",
  "data": {
    "name": "SmartCloudOps AI",
    "version": "3.3.0",
    "status": "operational",
    "features": {
      "mlops": true,
      "performance_monitoring": true,
      "caching": true
    },
    "endpoints": {
      "status": "/api/status",
      "health": "/health",
      "mlops": "/api/mlops/"
    }
  }
}
```

### 1.2 Health Check
**GET** `/health`

Comprehensive system health check.

**Response:**
```json
{
  "status": "success",
  "data": {
    "checks": {
      "ai_handler": true,
      "database": true,
      "ml_models": true,
      "performance_monitoring": true
    },
    "database_health": {
      "connection_pool": "active",
      "last_check": "2025-01-01T12:00:00Z",
      "status": "healthy"
    }
  }
}
```

### 1.3 System Status
**GET** `/status`

Get overall system status.

**Response:**
```json
{
  "status": "success",
  "data": {
    "system_status": "healthy",
    "uptime_seconds": 86400,
    "active_services": 8,
    "total_alerts": 3,
    "last_backup": "2025-01-01T06:00:00Z"
  }
}
```

---

## 2. Anomalies API (`/api/anomalies`)

### 2.1 List Anomalies
**GET** `/api/anomalies`

Retrieve paginated list of anomalies.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20)
- `severity` (string): Filter by severity (low, medium, high, critical)
- `status` (string): Filter by status (open, acknowledged, resolved)

**Response:**
```json
{
  "status": "success",
  "data": {
    "anomalies": [
      {
        "id": 1,
        "title": "High CPU Usage Detected",
        "description": "CPU utilization exceeded 90% for 5 minutes",
        "severity": "high",
        "status": "open",
        "metric_name": "cpu_percent",
        "metric_value": 95.2,
        "detected_at": "2025-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

### 2.2 Get Anomaly Details
**GET** `/api/anomalies/{anomaly_id}`

Get detailed information about a specific anomaly.

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "High CPU Usage Detected",
    "description": "CPU utilization exceeded 90% for 5 minutes",
    "severity": "high",
    "status": "open",
    "details": {
      "metric_name": "cpu_percent",
      "current_value": 95.2,
      "threshold": 90,
      "duration_minutes": 5
    },
    "recommendations": [
      "Consider scaling up the web-server service",
      "Check for memory leaks in the application"
    ]
  }
}
```

### 2.3 Acknowledge Anomaly
**POST** `/api/anomalies/{anomaly_id}/acknowledge`

Acknowledge an anomaly to prevent duplicate alerts.

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Anomaly acknowledged successfully",
    "acknowledged_at": "2025-01-01T12:00:00Z"
  }
}
```

### 2.4 Resolve Anomaly
**POST** `/api/anomalies/{anomaly_id}/resolve`

Mark an anomaly as resolved.

**Request:**
```json
{
  "resolution": "Scaled up web-server instances",
  "root_cause": "Traffic spike due to marketing campaign"
}
```

---

## 3. MLOps API (`/api/mlops`)

### 3.1 List Experiments
**GET** `/api/mlops/experiments`

List all ML experiments.

**Response:**
```json
{
  "status": "success",
  "data": {
    "experiments": [
      {
        "id": "exp_001",
        "name": "Fraud Detection Model v2",
        "status": "completed",
        "metrics": {
          "accuracy": 0.945,
          "precision": 0.892
        }
      }
    ]
  }
}
```

### 3.2 Create Experiment
**POST** `/api/mlops/experiments`

Create a new ML experiment.

**Request:**
```json
{
  "name": "Customer Churn Prediction",
  "description": "Predict customer churn using historical data",
  "parameters": {
    "algorithm": "random_forest",
    "max_depth": 10
  }
}
```

### 3.3 List Models
**GET** `/api/mlops/models`

List all registered models.

**Response:**
```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "id": "model_001",
        "name": "fraud_detection_v2",
        "version": "2.1.0",
        "status": "production"
      }
    ]
  }
}
```

---

## 4. ML API (`/api/ml`)

### 4.1 Make Prediction
**POST** `/api/ml/predict`

Make predictions using a deployed model.

**Request:**
```json
{
  "model_id": "anomaly_detector",
  "data": {
    "cpu_percent": 85.5,
    "memory_percent": 72.3
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "prediction": -1,
    "confidence": 0.876,
    "is_anomaly": true
  }
}
```

### 4.2 Train Model
**POST** `/api/ml/train`

Start model training.

**Request:**
```json
{
  "model_type": "anomaly_detection",
  "algorithm": "isolation_forest",
  "parameters": {
    "contamination": 0.1,
    "n_estimators": 100
  }
}
```

---

## 5. Performance API (`/api/performance`)

### 5.1 Get Performance Metrics
**GET** `/api/performance/metrics`

Get current performance metrics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "cpu": {
      "usage_percent": 45.2,
      "cores": 8
    },
    "memory": {
      "total_gb": 16,
      "used_gb": 8.5,
      "usage_percent": 53.1
    },
    "disk": {
      "total_gb": 500,
      "used_gb": 234,
      "usage_percent": 46.8
    }
  }
}
```

### 5.2 Get Cache Statistics
**GET** `/api/performance/cache/stats`

Get cache performance statistics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "hits": 1234,
    "misses": 567,
    "hit_rate": 0.685,
    "total_requests": 1801
  }
}
```

---

## 6. Remediation API (`/api/remediation`)

### 6.1 List Remediation Actions
**GET** `/api/remediation/actions`

List available remediation actions.

**Response:**
```json
{
  "status": "success",
  "data": {
    "actions": [
      {
        "id": 1,
        "name": "scale_web_service",
        "description": "Scale web service to handle increased load",
        "type": "auto_scaling",
        "status": "available"
      }
    ]
  }
}
```

### 6.2 Execute Remediation Action
**POST** `/api/remediation/actions/{action_id}/execute`

Execute a remediation action.

**Request:**
```json
{
  "reason": "High CPU usage detected",
  "priority": "high"
}
```

---

## 7. ChatOps API (`/api/chatops`)

### 7.1 Execute Chat Command
**POST** `/api/chatops`

Execute a natural language command.

**Request:**
```json
{
  "command": "show me the current system status",
  "context": {
    "user": "admin"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "response": "Current system status: All services operational. CPU usage at 45%, Memory at 67%.",
    "actions_taken": []
  }
}
```

---

## 8. AI API (`/api/ai`)

### 8.1 Get AI Recommendations
**POST** `/api/ai/recommendations`

Get AI-powered recommendations.

**Request:**
```json
{
  "context": "high_cpu_usage",
  "metrics": {
    "cpu_percent": 95.5,
    "memory_percent": 78.3
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "type": "scaling",
        "priority": "high",
        "action": "scale_web_service",
        "reason": "CPU usage is critically high"
      }
    ]
  }
}
```

---

## 9. SLOs API (`/api/slos`)

### 9.1 Get SLO Status
**GET** `/api/slos/status`

Get current Service Level Objective status.

**Response:**
```json
{
  "status": "success",
  "data": {
    "slos": [
      {
        "name": "api_response_time",
        "target": 0.95,
        "current": 0.967,
        "status": "meeting"
      }
    ]
  }
}
```

---

## 10. Feedback API (`/api/feedback`)

### 10.1 Submit Feedback
**POST** `/api/feedback`

Submit user feedback.

**Request:**
```json
{
  "type": "recommendation_feedback",
  "rating": 4,
  "feedback": "Good recommendation, but took longer than expected"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "feedback_id": 123,
    "message": "Feedback submitted successfully"
  }
}
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "severity",
      "issue": "must be one of: low, medium, high, critical"
    }
  }
}
```

### Common Error Codes:
- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `RATE_LIMITED`: Too many requests

---

## Best Practices

### 1. Error Handling
```python
try:
    response = client.anomalies.list()
    if response.status == "success":
        # Process data
        pass
    else:
        print(f"Error: {response.error}")
except Exception as e:
    print(f"Network error: {e}")
```

### 2. Pagination
```python
page = 1
while True:
    response = client.anomalies.list(page=page, per_page=50)
    if not response.data.anomalies:
        break
    # Process anomalies
    page += 1
```

### 3. Rate Limiting
```python
import time

for i in range(100):
    response = client.metrics.get()
    if response.status_code == 429:  # Rate limited
        time.sleep(60)  # Wait for reset
        continue
```

---

## SDK Examples

### Python SDK Usage
```python
import requests
import json

class SmartCloudOpsClient:
    def __init__(self, base_url="http://localhost:5000", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        return response.json()

    # Core endpoints
    def health_check(self):
        return self._make_request("GET", "/health")

    def get_status(self):
        return self._make_request("GET", "/status")

    # Anomalies endpoints
    def list_anomalies(self, page=1, per_page=20, severity=None):
        params = {"page": page, "per_page": per_page}
        if severity:
            params["severity"] = severity
        return self._make_request("GET", "/api/anomalies", params=params)

    def get_anomaly(self, anomaly_id):
        return self._make_request("GET", f"/api/anomalies/{anomaly_id}")

    def acknowledge_anomaly(self, anomaly_id):
        return self._make_request("POST", f"/api/anomalies/{anomaly_id}/acknowledge")

    # ML endpoints
    def make_prediction(self, model_id, data):
        payload = {"model_id": model_id, "data": data}
        return self._make_request("POST", "/api/ml/predict", json=payload)

    # Performance endpoints
    def get_performance_metrics(self):
        return self._make_request("GET", "/api/performance/metrics")

    # ChatOps endpoints
    def execute_command(self, command, context=None):
        payload = {"command": command}
        if context:
            payload["context"] = context
        return self._make_request("POST", "/api/chatops", json=payload)

# Usage example
client = SmartCloudOpsClient()

# Check system health
health = client.health_check()
print(f"System status: {health['data']['checks']['database']}")

# List anomalies
anomalies = client.list_anomalies(severity="high")
print(f"Found {len(anomalies['data']['anomalies'])} high-severity anomalies")

# Make prediction
prediction = client.make_prediction("anomaly_detector", {
    "cpu_percent": 85.5,
    "memory_percent": 72.3
})
print(f"Anomaly detected: {prediction['data']['is_anomaly']}")

# Execute natural language command
result = client.execute_command("show me system status")
print(f"ChatOps response: {result['data']['response']}")
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');

class SmartCloudOpsClient {
    constructor(baseURL = 'http://localhost:5000', apiKey = null) {
        this.client = axios.create({
            baseURL,
            headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
        });
    }

    // Core endpoints
    async healthCheck() {
        const response = await this.client.get('/health');
        return response.data;
    }

    async getStatus() {
        const response = await this.client.get('/status');
        return response.data;
    }

    // Anomalies endpoints
    async listAnomalies(params = {}) {
        const response = await this.client.get('/api/anomalies', { params });
        return response.data;
    }

    async getAnomaly(anomalyId) {
        const response = await this.client.get(`/api/anomalies/${anomalyId}`);
        return response.data;
    }

    // ML endpoints
    async makePrediction(modelId, data) {
        const response = await this.client.post('/api/ml/predict', {
            model_id: modelId,
            data
        });
        return response.data;
    }

    // ChatOps endpoints
    async executeCommand(command, context = null) {
        const payload = { command };
        if (context) payload.context = context;

        const response = await this.client.post('/api/chatops', payload);
        return response.data;
    }
}

// Usage example
const client = new SmartCloudOpsClient();

async function main() {
    try {
        // Check system health
        const health = await client.healthCheck();
        console.log(`Database healthy: ${health.data.checks.database}`);

        // List high-severity anomalies
        const anomalies = await client.listAnomalies({ severity: 'high' });
        console.log(`High anomalies: ${anomalies.data.anomalies.length}`);

        // Make prediction
        const prediction = await client.makePrediction('anomaly_detector', {
            cpu_percent: 85.5,
            memory_percent: 72.3
        });
        console.log(`Anomaly: ${prediction.data.is_anomaly}`);

        // Execute command
        const result = await client.executeCommand('show system status');
        console.log(`Response: ${result.data.response}`);

    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

main();
```

---

## Webhooks Integration

Configure webhooks for real-time notifications:

### Anomaly Webhook
```json
{
  "event": "anomaly_detected",
  "data": {
    "anomaly_id": 123,
    "severity": "high",
    "description": "High CPU usage detected",
    "detected_at": "2025-01-01T12:00:00Z"
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Remediation Webhook
```json
{
  "event": "remediation_executed",
  "data": {
    "action_id": 456,
    "status": "success",
    "result": "Service scaled successfully",
    "executed_at": "2025-01-01T12:02:00Z"
  },
  "timestamp": "2025-01-01T12:02:00Z"
}
```

### SLO Violation Webhook
```json
{
  "event": "slo_violation",
  "data": {
    "slo_name": "api_response_time",
    "target": 0.95,
    "current": 0.923,
    "violation_duration_minutes": 15
  },
  "timestamp": "2025-01-01T12:15:00Z"
}
```

---

## Versioning

API versioning follows semantic versioning:
- **Major version** (breaking changes): `/api/v2/`
- **Minor version** (new features): `/api/v1.1/`
- **Current version**: `/api/` (defaults to latest stable)

---

## Support and Resources

### Getting Help
- **Documentation**: Full API docs at `/api/docs`
- **Health Check**: System status at `/health`
- **Interactive API**: Swagger UI available in development mode

### Troubleshooting
1. **Connection Issues**: Verify the service is running on port 5000
2. **Authentication Errors**: Check your JWT token is valid
3. **Rate Limiting**: Monitor X-RateLimit headers in responses
4. **Timeouts**: Increase timeout for complex operations

### Monitoring Your Integration
```python
# Monitor API usage
response = client.get_status()
print(f"Total requests: {response.data.total_requests}")
print(f"Error rate: {response.data.error_rate}")

# Check system health
health = client.health_check()
for service, status in health.data.checks.items():
    print(f"{service}: {'✅' if status else '❌'}")
```

---

This comprehensive API reference covers all available endpoints, request/response formats, authentication, error handling, SDK examples, webhooks, and best practices for integrating with SmartCloudOps AI.