# SmartCloudOps AI - API Reference

## 🎯 Overview
Complete REST API with 55 endpoints across 5 modules.

## 📋 API Modules

### 1. Anomalies API (/api/anomalies) - 10 endpoints
- GET /api/anomalies/ - List anomalies
- POST /api/anomalies/ - Create anomaly  
- GET /api/anomalies/{id} - Get specific anomaly
- PUT /api/anomalies/{id}/acknowledge - Acknowledge anomaly
- PUT /api/anomalies/{id}/resolve - Resolve anomaly
- PUT /api/anomalies/{id}/dismiss - Dismiss anomaly
- PUT /api/anomalies/{id} - Update anomaly
- GET /api/anomalies/stats - Get statistics
- POST /api/anomalies/batch - Batch create

### 2. Remediation API (/api/remediation) - 11 endpoints  
- GET /api/remediation/actions - List actions
- POST /api/remediation/actions - Create action
- GET /api/remediation/actions/{id} - Get specific action
- PUT /api/remediation/actions/{id}/approve - Approve action
- PUT /api/remediation/actions/{id}/execute - Execute action
- PUT /api/remediation/actions/{id}/cancel - Cancel action
- PUT /api/remediation/actions/{id} - Update action
- DELETE /api/remediation/actions/{id} - Delete action
- GET /api/remediation/actions/stats - Get statistics
- POST /api/remediation/actions/batch - Batch create
- GET /api/remediation/available-actions - List available actions

### 3. Feedback API (/api/feedback) - 9 endpoints
- GET /api/feedback/ - List feedback
- POST /api/feedback/ - Submit feedback
- GET /api/feedback/{id} - Get specific feedback
- PUT /api/feedback/{id}/update-status - Update status
- PUT /api/feedback/{id} - Update feedback
- DELETE /api/feedback/{id} - Delete feedback
- GET /api/feedback/stats - Get statistics
- GET /api/feedback/my-feedback - Get user feedback
- GET /api/feedback/types - List feedback types

### 4. ML API (/api/ml) - 7 endpoints
- POST /api/ml/anomalies - Detect anomalies
- POST /api/ml/anomalies/realtime - Real-time detection
- POST /api/ml/train - Train model
- GET /api/ml/model/info - Get model info
- POST /api/ml/model/retrain - Retrain model
- GET /api/ml/predictions - Get recent predictions
- GET /api/ml/performance - Get model performance

### 5. AI API (/api/ai) - 18 endpoints
- GET /api/ai/recommendations - Get AI recommendations
- POST /api/ai/autonomous/process - Process autonomous
- GET /api/ai/autonomous/policies - List automation policies
- POST /api/ai/autonomous/policies - Create automation policy
- PUT /api/ai/autonomous/policies/{id} - Update policy
- DELETE /api/ai/autonomous/policies/{id} - Delete policy
- POST /api/ai/learning/cycle - Run learning cycle
- GET /api/ai/learning/statistics - Get learning stats
- POST /api/ai/data/collect - Collect data
- GET /api/ai/models/registry - Get model registry
- POST /api/ai/models/{type}/promote - Promote model
- POST /api/ai/experiments/ab-testing - Start A/B test
- PUT /api/ai/experiments/ab-testing/{id}/end - End A/B test
- POST /api/ai/drift/detect - Detect drift
- GET /api/ai/knowledge/stats - Knowledge stats
- POST /api/ai/knowledge/experience - Add experience
- GET /api/ai/autonomous/stats - Autonomous stats

## ❤️ Health Endpoints
- GET /health - Basic health check
- GET /healthz - Kubernetes liveness probe
- GET /readyz - Kubernetes readiness probe

## 📊 Monitoring
- GET /metrics - Prometheus metrics
- GET /status - Application status

**Total: 55 API endpoints + 4 system endpoints = 59 total endpoints**

