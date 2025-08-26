# 📊 Observability Guide - SmartCloudOps AI

Complete observability stack with structured logging, metrics collection, and distributed tracing.

## 🎯 Overview

Our observability stack provides:
- **Structured JSON Logging** with correlation IDs
- **Prometheus Metrics** (30+ custom metrics)
- **OpenTelemetry Distributed Tracing**
- **Grafana Dashboards** (5 pre-configured dashboards)
- **Automated Instrumentation** for Flask, PostgreSQL, Redis
- **Business Event Tracking**
- **Performance Monitoring**

## 🏗️ Architecture

```mermaid
graph TB
    A[Flask App] --> B[Observability Middleware]
    B --> C[Structured Logging]
    B --> D[Metrics Collection]
    B --> E[Distributed Tracing]
    
    C --> F[JSON Logs with Correlation IDs]
    D --> G[Prometheus Metrics]
    E --> H[OpenTelemetry Traces]
    
    G --> I[Grafana Dashboards]
    H --> J[Jaeger/OTLP Collectors]
    F --> K[Log Aggregation]
```

## 🔧 Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json             # json or text
LOG_FILE=/var/log/smartcloudops/app.log

# Tracing Configuration
ENABLE_TRACING=true
JAEGER_ENDPOINT=http://localhost:14268/api/traces
OTLP_ENDPOINT=http://localhost:4317

# Metrics Configuration
METRICS_ENABLED=true
PROMETHEUS_URL=http://localhost:9090
```

### Dependencies

Add to `requirements.txt`:
```
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-flask==0.42b0
python-json-logger==2.0.7
```

## 📊 Metrics Available

### HTTP Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram
- `http_request_size_bytes` - Request size histogram
- `http_response_size_bytes` - Response size histogram

### Business Metrics
- `anomalies_detected_total` - Anomalies by severity, type, source
- `anomalies_resolved_total` - Resolved anomalies with time buckets
- `remediation_actions_total` - Remediation actions by type and status
- `ml_model_predictions_total` - ML predictions by model and version
- `active_users_total` - Current active users

### Infrastructure Metrics
- `database_connections_total` - Database connection pool status
- `database_query_duration_seconds` - Query performance
- `cache_operations_total` - Cache hit/miss rates
- `memory_usage_bytes` - Memory consumption
- `cpu_usage_percent` - CPU utilization

### System Metrics
- `app_health_status` - Application health (healthy/degraded/unhealthy)
- `app_info` - Application metadata

## 🔍 Structured Logging

### Log Format

All logs are structured JSON with:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "message": "Request completed",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "service": {
    "name": "smartcloudops-ai",
    "version": "3.3.0",
    "component": "app.api.anomalies"
  },
  "request": {
    "method": "POST",
    "path": "/api/anomalies/",
    "remote_addr": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  },
  "user": {
    "id": "user123",
    "email": "user@example.com"
  },
  "source": {
    "file": "anomalies.py",
    "line": 45,
    "function": "create_anomaly"
  }
}
```

### Using Structured Logging

```python
from app.observability import get_logger, log_business_event

# Get logger with automatic context
logger = get_logger(__name__)

# Standard logging
logger.info("Processing anomaly detection")

# Business event logging
log_business_event(
    logger, 
    event_type="created",
    entity_type="anomaly", 
    entity_id="anomaly_123",
    severity="high",
    metric_type="cpu_usage"
)

# Performance logging
with create_span("anomaly_detection"):
    result = detect_anomalies(data)
    log_performance_event("anomaly_detection", duration_ms)
```

## 🎯 Distributed Tracing

### Automatic Instrumentation

Enabled automatically for:
- Flask requests and responses
- Database queries (PostgreSQL)
- Redis operations
- HTTP requests (via `requests` library)

### Manual Instrumentation

```python
from app.observability import trace_request, create_span

# Decorate functions
@trace_request("custom_operation")
def my_function():
    pass

# Manual span creation
with create_span("ml_inference", attributes={"model": "anomaly_detector"}):
    result = model.predict(data)

# Specialized decorators
@trace_anomaly_detection
def detect_anomalies(data):
    return {"anomalies_found": [...]}

@trace_remediation
def execute_remediation(action):
    return {"status": "success", "action_id": "123"}
```

### Correlation IDs

Automatic correlation ID management:
- Generated for each request
- Passed via `X-Correlation-ID` header
- Included in all logs and traces
- Returned in response headers

## 📈 Grafana Dashboards

### Available Dashboards

1. **Overview Dashboard** (`overview_dashboard.json`)
   - System health status
   - Active users
   - HTTP request rates
   - Response time percentiles

2. **Anomaly Dashboard** (`anomaly_dashboard.json`)
   - Anomalies detected by severity
   - Detection performance
   - ML model accuracy
   - Prediction rates

3. **Remediation Dashboard** (`remediation_dashboard.json`)
   - Remediation success rates
   - Action types and durations
   - Status distributions

4. **Performance Dashboard** (`performance_dashboard.json`)
   - Memory and CPU usage
   - Database performance
   - Cache hit rates

5. **Business Dashboard** (`business_dashboard.json`)
   - Key performance indicators
   - User activity trends
   - System effectiveness metrics

### Dashboard Installation

```bash
# Export dashboards
python -c "
from app.observability.dashboards import export_dashboards_json
export_dashboards_json('docs/observability/dashboards')
"

# Import to Grafana
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @docs/observability/dashboards/overview_dashboard.json
```

## 🚨 Alerting Rules

### Prometheus Alerts

```yaml
groups:
- name: smartcloudops_alerts
  rules:
  - alert: HighAnomalyRate
    expr: rate(anomalies_detected_total{severity="high"}[5m]) > 0.1
    for: 2m
    
  - alert: RemediationFailureRate
    expr: rate(remediation_actions_total{status="failure"}[5m]) / rate(remediation_actions_total[5m]) > 0.2
    for: 5m
    
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
    for: 3m
    
  - alert: ApplicationDown
    expr: app_health_status != 0
    for: 1m
```

## 🔗 Integration Points

### Flask Application

```python
from app.observability.middleware import setup_observability_middleware

def create_app():
    app = Flask(__name__)
    
    # Setup observability
    setup_observability_middleware(
        app,
        enable_request_logging=True,
        enable_metrics=True,
        enable_tracing=True
    )
    
    return app
```

### Health Endpoints

Available endpoints:
- `/health` - Basic health check
- `/readyz` - Readiness probe
- `/metrics` - Prometheus metrics
- `/observability/health` - Observability status

### Custom Metrics

```python
from app.observability.metrics import metrics_collector, track_performance

# Record business events
metrics_collector.record_anomaly_detection(
    severity="high",
    metric_type="cpu",
    source="prometheus",
    detection_duration=0.15
)

# Track function performance
@track_performance("ml_inference")
def run_ml_inference():
    pass
```

## 📊 Monitoring Best Practices

### 1. Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General operational events
- **WARNING**: Warning conditions
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Critical errors that may stop the application

### 2. Correlation ID Usage
- Always include correlation IDs in external API calls
- Use correlation IDs for troubleshooting across services
- Include in error messages and support tickets

### 3. Metrics Collection
- Avoid high-cardinality labels
- Use histogram metrics for timing data
- Include error rates and success rates
- Monitor business KPIs

### 4. Distributed Tracing
- Keep span names consistent and meaningful
- Add relevant attributes to spans
- Use semantic conventions where possible
- Monitor trace sampling rates

## 🛠️ Development Tools

### Local Testing

```bash
# Start observability stack
docker-compose up prometheus grafana jaeger

# Install dependencies
pip install -r requirements.txt

# Run with observability
LOG_LEVEL=DEBUG ENABLE_TRACING=true python app/main.py
```

### Debugging

```bash
# Check logs
tail -f /var/log/smartcloudops/app.log | jq

# Query metrics
curl http://localhost:5000/metrics

# View traces
open http://localhost:16686  # Jaeger UI

# Check health
curl http://localhost:5000/observability/health | jq
```

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)

## 🔧 Troubleshooting

### Common Issues

1. **Missing correlation IDs**
   - Check middleware initialization
   - Verify headers are passed correctly

2. **Metrics not appearing**
   - Check `/metrics` endpoint
   - Verify Prometheus scraping configuration

3. **Traces not showing**
   - Check Jaeger/OTLP endpoints
   - Verify tracing initialization

4. **High memory usage**
   - Adjust sampling rates
   - Check metric cardinality
   - Review log retention

---

**Next**: See [Performance Testing](../PERFORMANCE_TESTING.md) for load testing with observability metrics.
