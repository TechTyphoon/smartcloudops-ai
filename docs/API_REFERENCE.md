# 🔧 **SmartCloudOps AI - API Reference**

Complete API documentation for SmartCloudOps AI v3.0.0. This reference covers all REST endpoints, authentication, request/response formats, and usage examples.

---

## 🌐 **Base URL & API Information**

- **Base URL**: `http://localhost:5000` (development) or `https://your-domain.com` (production)
- **API Version**: v3.0.0
- **Protocol**: HTTP/HTTPS
- **Content-Type**: `application/json`
- **Authentication**: Bearer token (where required)

---

## 🔐 **Authentication**

### 📋 **Overview**
SmartCloudOps AI uses token-based authentication for protected endpoints. Most monitoring and health endpoints are public, while administrative and configuration endpoints require authentication.

### 🔑 **Authentication Header**
```bash
Authorization: Bearer <your_token_here>
```

### 🎯 **Getting a Token**
```bash
# Login endpoint (future implementation)
POST /api/auth/login
{
  "username": "your_username",
  "password": "your_password"
}

# Response
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

---

## 📊 **Core API Endpoints**

### 🏥 **Health & Status**

#### **GET /health**
Basic health check endpoint.

**Request:**
```bash
curl -X GET http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-15T10:30:00Z",
  "version": "3.0.0",
  "uptime": 3600
}
```

**Response Codes:**
- `200`: Service is healthy
- `503`: Service is unhealthy or starting up

---

#### **GET /api/status**
Comprehensive system status with component health.

**Request:**
```bash
curl -X GET http://localhost:5000/api/status
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-15T10:30:00Z",
  "components": {
    "database": {
      "status": "connected",
      "latency": "2ms"
    },
    "redis": {
      "status": "connected", 
      "latency": "1ms"
    },
    "ml_engine": {
      "status": "ready",
      "models_loaded": 3,
      "last_inference": "2025-08-15T10:29:45Z"
    }
  },
  "metrics": {
    "requests_per_second": 45,
    "average_response_time": "18ms",
    "memory_usage": "1.8GB",
    "cpu_usage": "45%"
  }
}
```

**Response Codes:**
- `200`: System status retrieved successfully

---

### 🤖 **Machine Learning & Predictions**

#### **POST /api/predict**
Anomaly detection and prediction endpoint.

**Request:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_usage": 85.5,
    "memory_usage": 78.2,
    "disk_usage": 45.0,
    "network_io": 1024,
    "timestamp": "2025-08-15T10:30:00Z"
  }'
```

**Request Body:**
```json
{
  "cpu_usage": 85.5,          // CPU usage percentage (0-100)
  "memory_usage": 78.2,       // Memory usage percentage (0-100)  
  "disk_usage": 45.0,         // Disk usage percentage (0-100)
  "network_io": 1024,         // Network I/O in KB/s (optional)
  "timestamp": "2025-08-15T10:30:00Z"  // ISO 8601 timestamp (optional)
}
```

**Response:**
```json
{
  "prediction": {
    "anomaly_score": 0.12,     // Anomaly score (0-1, higher = more anomalous)
    "is_anomaly": false,       // Boolean anomaly detection
    "confidence": 0.95,        // Prediction confidence (0-1)
    "risk_level": "low"        // Risk level: low, medium, high, critical
  },
  "analysis": {
    "primary_factors": ["cpu_usage"],
    "recommendations": [
      "Monitor CPU usage trend over next 10 minutes",
      "Consider scaling if usage remains above 80%"
    ]
  },
  "metadata": {
    "model_version": "v2.1.0",
    "inference_time": "18ms",
    "timestamp": "2025-08-15T10:30:00Z"
  }
}
```

**Response Codes:**
- `200`: Prediction completed successfully
- `400`: Invalid input data
- `422`: Input validation failed
- `500`: ML engine error

---

#### **POST /api/batch_predict**
Batch prediction for multiple data points.

**Request:**
```bash
curl -X POST http://localhost:5000/api/batch_predict \
  -H "Content-Type: application/json" \
  -d '{
    "data_points": [
      {"cpu_usage": 85.5, "memory_usage": 78.2, "disk_usage": 45.0},
      {"cpu_usage": 23.1, "memory_usage": 45.8, "disk_usage": 67.2},
      {"cpu_usage": 91.2, "memory_usage": 89.5, "disk_usage": 23.1}
    ]
  }'
```

**Response:**
```json
{
  "predictions": [
    {
      "index": 0,
      "anomaly_score": 0.12,
      "is_anomaly": false,
      "risk_level": "low"
    },
    {
      "index": 1, 
      "anomaly_score": 0.05,
      "is_anomaly": false,
      "risk_level": "low"
    },
    {
      "index": 2,
      "anomaly_score": 0.87,
      "is_anomaly": true,
      "risk_level": "critical"
    }
  ],
  "summary": {
    "total_predictions": 3,
    "anomalies_detected": 1,
    "average_score": 0.35,
    "processing_time": "45ms"
  }
}
```

---

### 💬 **ChatOps Interface**

#### **GET /chatops/context**
Get current system context for ChatOps interface.

**Request:**
```bash
curl -X GET http://localhost:5000/chatops/context
```

**Response:**
```json
{
  "status": "active",
  "system_state": {
    "containers": {
      "total": 5,
      "healthy": 5,
      "unhealthy": 0
    },
    "performance": {
      "response_time": "18ms",
      "cpu_usage": "45%",
      "memory_usage": "1.8GB"
    },
    "recent_events": [
      {
        "timestamp": "2025-08-15T10:25:00Z",
        "type": "info",
        "message": "System health check completed successfully"
      }
    ]
  },
  "capabilities": [
    "system_status",
    "performance_analysis", 
    "anomaly_detection",
    "log_analysis",
    "basic_troubleshooting"
  ]
}
```

---

#### **POST /chatops/query**
Submit natural language query to ChatOps interface.

**Request:**
```bash
curl -X POST http://localhost:5000/chatops/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current system performance?",
    "context": {
      "user_id": "admin",
      "session_id": "sess_123456"
    }
  }'
```

**Response:**
```json
{
  "response": "Current system performance is excellent. CPU usage is at 45%, memory usage is 1.8GB, and average response time is 18ms. All containers are healthy and running optimally.",
  "actions_taken": [],
  "recommendations": [
    "System is performing well within normal parameters",
    "No immediate action required"
  ],
  "metadata": {
    "response_time": "234ms",
    "confidence": 0.92,
    "intent": "system_status_inquiry"
  }
}
```

---

### 📈 **Metrics & Monitoring**

#### **GET /metrics**
Prometheus-compatible metrics endpoint.

**Request:**
```bash
curl -X GET http://localhost:5000/metrics
```

**Response:**
```
# HELP flask_requests_total Total number of requests
# TYPE flask_requests_total counter
flask_requests_total{method="GET",status="200"} 1247.0
flask_requests_total{method="POST",status="200"} 342.0

# HELP flask_request_duration_seconds Request duration in seconds  
# TYPE flask_request_duration_seconds histogram
flask_request_duration_seconds_bucket{le="0.01"} 523.0
flask_request_duration_seconds_bucket{le="0.05"} 1156.0
flask_request_duration_seconds_bucket{le="0.1"} 1589.0

# HELP ml_inference_duration_seconds ML inference duration
# TYPE ml_inference_duration_seconds histogram
ml_inference_duration_seconds_sum 45.67
ml_inference_duration_seconds_count 2341.0

# HELP system_cpu_usage Current CPU usage percentage
# TYPE system_cpu_usage gauge
system_cpu_usage 45.2

# HELP system_memory_usage Current memory usage in bytes
# TYPE system_memory_usage gauge
system_memory_usage 1932735283.0
```

---

#### **GET /api/metrics/summary**
Human-readable metrics summary.

**Request:**
```bash
curl -X GET http://localhost:5000/api/metrics/summary
```

**Response:**
```json
{
  "performance": {
    "requests_per_second": 45.2,
    "average_response_time": "18ms",
    "p95_response_time": "32ms", 
    "p99_response_time": "78ms"
  },
  "system": {
    "cpu_usage": "45.2%",
    "memory_usage": "1.8GB",
    "disk_usage": "34.5%",
    "network_io": "2.1MB/s"
  },
  "application": {
    "active_connections": 23,
    "cache_hit_ratio": "94.2%",
    "ml_inferences_per_minute": 127,
    "error_rate": "0.01%"
  },
  "timestamp": "2025-08-15T10:30:00Z"
}
```

---

### 🔧 **Configuration & Management**

#### **GET /api/config**
Get current application configuration.

**Request:**
```bash
curl -X GET http://localhost:5000/api/config \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "application": {
    "version": "3.0.0",
    "environment": "production",
    "debug_mode": false,
    "log_level": "INFO"
  },
  "security": {
    "audit_enabled": true,
    "compliance_level": 80,
    "rate_limiting": true
  },
  "ml_engine": {
    "model_version": "v2.1.0",
    "inference_timeout": 30,
    "batch_size": 100
  },
  "monitoring": {
    "prometheus_enabled": true,
    "grafana_url": "http://grafana:3000",
    "retention_days": 15
  }
}
```

---

#### **POST /api/config**
Update application configuration.

**Request:**
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "security": {
      "compliance_level": 85
    },
    "ml_engine": {
      "inference_timeout": 25
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "updated_fields": [
    "security.compliance_level",
    "ml_engine.inference_timeout"
  ],
  "restart_required": false
}
```

---

### 🧪 **Testing & Diagnostics**

#### **GET /api/test/connectivity**
Test connectivity to external services.

**Request:**
```bash
curl -X GET http://localhost:5000/api/test/connectivity
```

**Response:**
```json
{
  "tests": {
    "database": {
      "status": "success",
      "latency": "2ms",
      "details": "PostgreSQL connection successful"
    },
    "redis": {
      "status": "success", 
      "latency": "1ms",
      "details": "Redis connection successful"
    },
    "prometheus": {
      "status": "success",
      "latency": "5ms", 
      "details": "Prometheus metrics endpoint accessible"
    }
  },
  "overall_status": "healthy",
  "timestamp": "2025-08-15T10:30:00Z"
}
```

---

#### **POST /api/test/ml_performance**
Run ML performance benchmark.

**Request:**
```bash
curl -X POST http://localhost:5000/api/test/ml_performance \
  -H "Content-Type: application/json" \
  -d '{
    "test_samples": 100,
    "include_batch_test": true
  }'
```

**Response:**
```json
{
  "results": {
    "single_predictions": {
      "total_tests": 100,
      "average_latency": "18ms",
      "min_latency": "12ms", 
      "max_latency": "34ms",
      "success_rate": "100%"
    },
    "batch_predictions": {
      "batch_size": 10,
      "total_batches": 10,
      "average_latency": "45ms",
      "throughput": "222 predictions/sec"
    }
  },
  "recommendations": [
    "Performance is within optimal range",
    "Consider increasing batch size for higher throughput"
  ]
}
```

---

## 🚨 **Error Responses**

### 📋 **Standard Error Format**
All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "field": "cpu_usage",
      "issue": "Value must be between 0 and 100"
    }
  },
  "timestamp": "2025-08-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 🔍 **Common Error Codes**

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| `400` | `BAD_REQUEST` | Invalid request format |
| `401` | `UNAUTHORIZED` | Authentication required |
| `403` | `FORBIDDEN` | Insufficient permissions |
| `404` | `NOT_FOUND` | Endpoint not found |
| `422` | `VALIDATION_ERROR` | Input validation failed |
| `429` | `RATE_LIMITED` | Too many requests |
| `500` | `INTERNAL_ERROR` | Server error |
| `503` | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

---

## 📊 **Rate Limiting**

### 🚦 **Rate Limits**
| Endpoint Type | Rate Limit | Window |
|---------------|------------|---------|
| **Health Checks** | 100/min | 1 minute |
| **Predictions** | 1000/hour | 1 hour |
| **ChatOps** | 60/min | 1 minute |
| **Configuration** | 10/min | 1 minute |
| **Metrics** | 200/min | 1 minute |

### 📋 **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1629876543
X-RateLimit-Window: 3600
```

---

## 🔄 **Webhooks**

### 📡 **Webhook Events**
SmartCloudOps AI can send webhook notifications for important events:

#### **Anomaly Detected**
```json
{
  "event": "anomaly_detected",
  "timestamp": "2025-08-15T10:30:00Z",
  "data": {
    "anomaly_score": 0.87,
    "risk_level": "critical", 
    "affected_metrics": ["cpu_usage", "memory_usage"],
    "recommendations": ["Immediate investigation required"]
  }
}
```

#### **System Health Changed**
```json
{
  "event": "health_status_changed",
  "timestamp": "2025-08-15T10:30:00Z",
  "data": {
    "previous_status": "healthy",
    "current_status": "degraded",
    "affected_components": ["database"],
    "details": "Database connection latency increased"
  }
}
```

---

## 📚 **SDK & Libraries**

### 🐍 **Python SDK** (Future)
```python
from smartcloudops import SmartCloudOpsClient

# Initialize client
client = SmartCloudOpsClient(
    base_url="http://localhost:5000",
    token="your_token_here"
)

# Make predictions
result = client.predict({
    "cpu_usage": 85.5,
    "memory_usage": 78.2,
    "disk_usage": 45.0
})

# Check system status
status = client.get_status()
```

### 🟨 **JavaScript SDK** (Future)
```javascript
import { SmartCloudOpsClient } from '@smartcloudops/sdk';

const client = new SmartCloudOpsClient({
  baseURL: 'http://localhost:5000',
  token: 'your_token_here'
});

// Make predictions
const result = await client.predict({
  cpu_usage: 85.5,
  memory_usage: 78.2,
  disk_usage: 45.0
});

// Check system status  
const status = await client.getStatus();
```

---

## 📖 **Examples**

### 🚀 **Complete Workflow Example**
```bash
#!/bin/bash

# 1. Check system health
curl -s http://localhost:5000/health | jq

# 2. Get current status
curl -s http://localhost:5000/api/status | jq

# 3. Run anomaly detection
curl -s -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_usage": 85.5,
    "memory_usage": 78.2, 
    "disk_usage": 45.0
  }' | jq

# 4. Query ChatOps
curl -s -X POST http://localhost:5000/chatops/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current system status?"
  }' | jq

# 5. Check metrics
curl -s http://localhost:5000/api/metrics/summary | jq
```

### 🔄 **Monitoring Script**
```python
#!/usr/bin/env python3
import requests
import time
import json

BASE_URL = "http://localhost:5000"

def check_health():
    """Check system health"""
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

def run_prediction(metrics):
    """Run anomaly detection"""
    response = requests.post(
        f"{BASE_URL}/api/predict",
        json=metrics
    )
    return response.json()

def main():
    while True:
        # Check health
        health = check_health()
        print(f"Health: {health['status']}")
        
        # Run prediction with sample data
        metrics = {
            "cpu_usage": 75.5,
            "memory_usage": 68.2,
            "disk_usage": 45.0
        }
        
        prediction = run_prediction(metrics)
        print(f"Anomaly Score: {prediction['prediction']['anomaly_score']}")
        
        time.sleep(60)  # Wait 1 minute

if __name__ == "__main__":
    main()
```

---

## 🔗 **Related Documentation**

- **[Getting Started Guide](GETTING_STARTED.md)** - Setup and deployment
- **[Architecture Overview](ARCHITECTURE.md)** - System design details  
- **[Security Guide](../docs/SECURITY_AUDIT_REPORT_ENHANCED.md)** - Security implementation
- **[Monitoring Guide](MONITORING_GUIDE.md)** - Dashboard and alerting setup

---

<div align="center">

**🔧 Complete API Reference • Production Ready • Developer Friendly 🔧**

[Back to Main README](../README.md) | [Next: Security Guide](../docs/SECURITY_AUDIT_REPORT_ENHANCED.md)

</div>
