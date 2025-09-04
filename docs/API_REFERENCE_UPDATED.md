# SmartCloudOps AI - Complete API Reference

## 🎯 Overview
Complete REST API with 85+ endpoints across 12 modules (Updated September 2025).

## 📋 API Modules Overview

| Module | Base Path | Endpoints | Purpose |
|--------|-----------|-----------|---------|
| **Core** | `/` | 15 | System health, metrics, configuration |
| **Anomalies** | `/api/anomalies` | 12 | Anomaly detection and management |
| **Remediation** | `/api/remediation` | 15 | Automated remediation actions |
| **ML** | `/api/ml` | 15 | Machine learning operations |
| **MLOps** | `/api/mlops` | 25 | ML lifecycle management |
| **AI** | `/api/ai` | 8 | AI-powered features |
| **Chat/ChatOps** | `/api/chat` | 5 | Conversational AI interface |
| **Performance** | `/api/performance` | 12 | Performance monitoring |
| **SLOs** | `/api/slos` | 8 | Service level objectives |
| **Feedback** | `/api/feedback` | 8 | User feedback system |
| **Auth** | `/api/auth` | 6 | Authentication endpoints |
| **ChatOps** | `/api/chatops` | 2 | ChatOps integration |

**Total: 85+ API endpoints + 8 system endpoints = 93+ total endpoints**

---

## 🔧 Core API Endpoints

### System Health & Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Application root |
| GET | `/health` | Basic health check |
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Kubernetes readiness probe |
| GET | `/status` | Application status |
| GET | `/api/status` | API status information |
| GET | `/api/version` | API version information |
| GET | `/api/health` | API health check |
| GET | `/api/metrics` | Application metrics |
| GET | `/metrics` | Prometheus metrics endpoint |
| GET | `/api/docs` | API documentation |
| GET | `/api/info` | API information |
| GET | `/database/status` | Database health status |
| GET | `/metrics/history` | Historical metrics data |

### Configuration
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Get application configuration |

---

## 🚨 Anomalies API (`/api/anomalies`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/anomalies` | List anomalies with filtering |
| POST | `/api/anomalies` | Create new anomaly |
| GET | `/api/anomalies/<id>` | Get specific anomaly |
| PUT | `/api/anomalies/<id>` | Update anomaly |
| DELETE | `/api/anomalies/<id>` | Delete anomaly |
| POST | `/api/anomalies/<id>/acknowledge` | Acknowledge anomaly |
| POST | `/api/anomalies/<id>/resolve` | Resolve anomaly |
| POST | `/api/anomalies/<id>/dismiss` | Dismiss anomaly |
| POST | `/api/anomalies/batch` | Batch create anomalies |
| GET | `/api/anomalies/stats` | Get anomaly statistics |
| GET | `/api/anomalies/export` | Export anomalies data |

---

## 🔧 Remediation API (`/api/remediation`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/remediation` | List remediation actions |
| GET | `/api/remediation/actions` | List all remediation actions |
| POST | `/api/remediation/actions` | Create remediation action |
| GET | `/api/remediation/actions/<id>` | Get specific remediation action |
| PUT | `/api/remediation/actions/<id>` | Update remediation action |
| DELETE | `/api/remediation/actions/<id>` | Delete remediation action |
| POST | `/api/remediation/actions/<id>/execute` | Execute remediation action |
| POST | `/api/remediation/actions/<id>/approve` | Approve remediation action |
| POST | `/api/remediation/actions/<id>/cancel` | Cancel remediation action |
| GET | `/api/remediation/stats` | Get remediation statistics |
| GET | `/api/remediation/export` | Export remediation data |
| POST | `/api/remediation/actions/batch` | Batch create remediation actions |
| GET | `/api/remediation/available-actions` | List available remediation actions |
| GET | `/api/remediation/actions/<id>/logs` | Get remediation action logs |
| GET | `/api/remediation/actions/<id>/status` | Get remediation action status |

---

## 🤖 ML API (`/api/ml`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ml/models` | List ML models |
| GET | `/api/ml/models/<id>` | Get specific ML model |
| POST | `/api/ml/train` | Train ML model |
| GET | `/api/ml/training-jobs` | List training jobs |
| GET | `/api/ml/training-jobs/<id>` | Get specific training job |
| GET | `/api/ml/datasets` | List datasets |
| POST | `/api/ml/predict` | Make predictions |
| POST | `/api/ml/models/<id>/deploy` | Deploy ML model |
| POST | `/api/ml/models/<id>/undeploy` | Undeploy ML model |
| GET | `/api/ml/stats` | Get ML statistics |
| POST | `/api/ml/anomaly` | Detect anomalies using ML |

---

## 🔬 MLOps API (`/api/mlops`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/mlops/experiments` | List ML experiments |
| POST | `/api/mlops/experiments` | Create new experiment |
| GET | `/api/mlops/experiments/<id>` | Get specific experiment |
| PUT | `/api/mlops/experiments/<id>` | Update experiment |
| POST | `/api/mlops/experiments/<id>/runs` | Start experiment run |
| POST | `/api/mlops/experiments/<id>/runs/<run_id>/end` | End experiment run |
| POST | `/api/mlops/experiments/<id>/runs/<run_id>/metrics` | Log experiment metrics |
| POST | `/api/mlops/experiments/<id>/runs/<run_id>/parameters` | Log experiment parameters |
| GET | `/api/mlops/mlflow/experiments` | Get MLflow experiments |
| GET | `/api/mlops/mlflow/runs` | Get MLflow runs |
| GET | `/api/mlops/mlflow/experiments/<id>/runs` | Get MLflow runs for experiment |
| GET | `/api/mlops/data/versions` | List data versions |
| GET | `/api/mlops/models` | List ML models |
| POST | `/api/mlops/models` | Register new model |
| GET | `/api/mlops/models/<id>` | Get specific model |
| PUT | `/api/mlops/models/<id>/status` | Update model status |
| POST | `/api/mlops/models/<id>/deploy` | Deploy model |
| GET | `/api/mlops/data-pipeline` | Get data pipeline status |
| POST | `/api/mlops/data-pipeline` | Create data pipeline |
| POST | `/api/mlops/data-pipeline/<id>/run` | Run data pipeline |
| POST | `/api/mlops/data/transformations` | Apply data transformations |
| GET | `/api/mlops/stats` | Get MLOps statistics |
| GET | `/api/mlops/algorithms` | List available algorithms |
| GET | `/api/mlops/frameworks` | List supported frameworks |
| GET | `/api/mlops/statistics` | Get detailed statistics |
| GET | `/api/mlops/health` | MLOps service health |

---

## 💬 Chat/ChatOps API (`/api/chat`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/query` | Send chat query |
| GET | `/api/chat/health` | Chat service health |
| GET | `/api/chat/history` | Get chat history |
| POST | `/api/chat/clear` | Clear chat history |

---

## ⚡ Performance API (`/api/performance`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/performance/health` | Performance service health |
| GET | `/api/performance/cache/stats` | Cache statistics |
| POST | `/api/performance/cache/clear` | Clear cache |
| GET | `/api/performance/metrics` | Performance metrics |
| POST | `/api/performance/optimization/analyze` | Analyze performance |
| GET | `/api/performance/optimization/recommendations` | Get optimization recommendations |
| GET | `/api/performance/alerts` | List performance alerts |
| POST | `/api/performance/alerts/<id>/acknowledge` | Acknowledge performance alert |
| GET | `/api/performance/cost/analysis` | Cost analysis |

---

## 📈 SLOs API (`/api/slos`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/slos/status` | SLO status overview |
| GET | `/api/slos/<name>` | Get specific SLO |
| GET | `/api/slos/error-budget` | Error budget information |
| GET | `/api/slos/history` | SLO history |
| GET | `/api/slos/trends` | SLO trends |
| GET | `/api/slos/alerts` | SLO alerts |
| GET | `/api/slos/metrics` | SLO metrics |
| GET | `/api/slos/health` | SLO service health |

---

## 💬 ChatOps API (`/api/chatops`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatops` | Send ChatOps command |
| POST | `/api/chatops/query` | Send ChatOps query |

---

## 🤖 AI API (`/api/ai`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/recommendations` | Get AI recommendations |
| POST | `/api/ai/analyze` | Analyze data with AI |
| POST | `/api/ai/chat` | AI chat interface |
| GET | `/api/ai/models` | List AI models |
| POST | `/api/ai/models/<id>/predict` | Make AI prediction |

---

## 📝 Feedback API (`/api/feedback`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/feedback` | List feedback |
| POST | `/api/feedback` | Submit feedback |
| GET | `/api/feedback/<id>` | Get specific feedback |
| PUT | `/api/feedback/<id>` | Update feedback |
| DELETE | `/api/feedback/<id>` | Delete feedback |
| GET | `/api/feedback/stats` | Get feedback statistics |
| GET | `/api/feedback/export` | Export feedback data |

---

## 🔐 Authentication API (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| POST | `/api/auth/refresh` | Refresh JWT token |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/verify` | Verify authentication |

---

## 📊 API Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| **GET endpoints** | 65+ | ~70% |
| **POST endpoints** | 25+ | ~27% |
| **PUT endpoints** | 8+ | ~9% |
| **DELETE endpoints** | 4+ | ~4% |
| **Total Endpoints** | 93+ | 100% |

---

## 🔧 Request/Response Format

All API endpoints follow RESTful conventions:

### Request Format
```json
{
  "data": {
    // Request payload
  },
  "metadata": {
    "version": "1.0",
    "timestamp": "2025-09-01T00:00:00Z"
  }
}
```

### Response Format
```json
{
  "status": "success|error",
  "data": {
    // Response payload
  },
  "error": null,
  "metadata": {
    "version": "1.0",
    "timestamp": "2025-09-01T00:00:00Z",
    "request_id": "uuid"
  }
}
```

---

## 🛡️ Authentication & Security

- **JWT Authentication**: Required for protected endpoints
- **Rate Limiting**: Applied to prevent abuse
- **Input Validation**: Comprehensive request validation
- **Audit Logging**: All API calls are logged
- **CORS Support**: Configured for frontend integration

---

## 📈 Monitoring & Metrics

- **Prometheus Metrics**: Available at `/metrics`
- **Health Checks**: Multiple endpoints for different probe types
- **Performance Monitoring**: Built-in response time tracking
- **Error Tracking**: Comprehensive error logging and reporting

**Last updated:** September 2025 | **API Version:** 3.3.0
