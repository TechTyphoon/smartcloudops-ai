# SmartCloudOps AI Helm Chart

A Helm chart for deploying SmartCloudOps AI on Kubernetes - an AI-powered DevOps platform with anomaly detection and automated remediation.

## 🎯 Quick Start

### Prerequisites

- Kubernetes 1.19+
- Helm 3.8+
- NGINX Ingress Controller
- cert-manager (for TLS)
- A local Kubernetes cluster (kind, minikube, or k3s)

### Installation

```bash
# Add required Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install the chart
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  --values ./deploy/helm/smartcloudops-ai/values-dev.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=smartcloudops-ai --timeout=300s
```

## 🚀 Environment-Specific Deployments

### Development Environment
```bash
# Minimal resources, single replicas, no TLS
helm install smartcloudops-ai-dev ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops-dev \
  --create-namespace \
  --values ./deploy/helm/smartcloudops-ai/values-dev.yaml
```

### Staging Environment
```bash
# Moderate resources, autoscaling, basic TLS
helm install smartcloudops-ai-staging ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops-staging \
  --create-namespace \
  --values ./deploy/helm/smartcloudops-ai/values-staging.yaml
```

### Production Environment
```bash
# High availability, autoscaling, security policies
helm install smartcloudops-ai-prod ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops-prod \
  --create-namespace \
  --values ./deploy/helm/smartcloudops-ai/values-prod.yaml
```

## 🔧 Configuration

### Core Components

| Component | Description | Default Port |
|-----------|-------------|--------------|
| Backend API | Flask application with 55 API endpoints | 5000 |
| Frontend | Next.js web interface | 3000 |
| PostgreSQL | Primary database | 5432 |
| Redis | Caching and session storage | 6379 |
| Prometheus | Metrics collection | 9090 |
| Grafana | Monitoring dashboards | 3000 |

### Key Configuration Options

```yaml
# Backend scaling
backend:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10

# Security
security:
  networkPolicies:
    enabled: true
  podSecurityPolicy:
    enabled: true

# Ingress
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: smartcloudops.local
```

## 🏥 Health Checks

The chart includes comprehensive health checks:

- **Liveness Probe**: `/healthz` - Kubernetes liveness checks
- **Readiness Probe**: `/readyz` - Service readiness validation
- **Startup Probe**: Gradual startup validation

## 🔒 Security Features

- Non-root container execution
- Read-only root filesystem
- Network policies for traffic isolation
- Secret management for sensitive data
- Pod Security Standards compliance
- Resource limits and requests

## 📊 Monitoring & Observability

### Prometheus Metrics
- Application metrics exposed on `/metrics`
- Custom business metrics for anomaly detection
- Infrastructure monitoring via node-exporter

### Grafana Dashboards
- System overview dashboard
- Application performance monitoring
- ML model performance tracking
- Business metrics visualization

## 🧪 Testing the Installation

### 1. Verify Pods are Running
```bash
kubectl get pods -n smartcloudops
```

### 2. Check Service Health
```bash
# Port forward to access locally
kubectl port-forward svc/smartcloudops-ai-backend 5000:5000 -n smartcloudops &
kubectl port-forward svc/smartcloudops-ai-frontend 3000:3000 -n smartcloudops &

# Test health endpoints
curl http://localhost:5000/health
curl http://localhost:5000/readyz
curl http://localhost:3000/
```

### 3. Test API Endpoints
```bash
# List all available APIs
curl http://localhost:5000/api/docs

# Test anomaly detection
curl -X GET http://localhost:5000/api/anomalies/

# Test ML endpoints
curl -X GET http://localhost:5000/api/ml/model/info
```

### 4. Access Web Interface
Visit `http://localhost:3000` in your browser to access the web interface.

## 🐳 Local Development with kind

### Create kind Cluster
```bash
# Create cluster with ingress support
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### Deploy SmartCloudOps AI
```bash
# Install the chart
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  --values ./deploy/helm/smartcloudops-ai/values-dev.yaml

# Add local hostname
echo "127.0.0.1 smartcloudops-dev.local" | sudo tee -a /etc/hosts

# Access the application
open http://smartcloudops-dev.local
```

## 🔄 Upgrades

```bash
# Upgrade to new version
helm upgrade smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --values ./deploy/helm/smartcloudops-ai/values-dev.yaml

# Rollback if needed
helm rollback smartcloudops-ai 1 --namespace smartcloudops
```

## 🗑️ Uninstall

```bash
# Remove the application
helm uninstall smartcloudops-ai --namespace smartcloudops

# Remove namespace
kubectl delete namespace smartcloudops
```

## 📋 Chart Validation

```bash
# Lint the chart
helm lint ./deploy/helm/smartcloudops-ai

# Validate templates
helm template smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --values ./deploy/helm/smartcloudops-ai/values-dev.yaml \
  --debug

# Dry run installation
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  --values ./deploy/helm/smartcloudops-ai/values-dev.yaml \
  --dry-run
```

## 🆘 Troubleshooting

### Common Issues

1. **Pods in CrashLoopBackOff**
   ```bash
   kubectl logs -l app.kubernetes.io/instance=smartcloudops-ai --tail=50
   ```

2. **Database Connection Issues**
   ```bash
   kubectl exec -it deployment/smartcloudops-ai-backend -- env | grep DATABASE
   ```

3. **Ingress Not Working**
   ```bash
   kubectl get ingress -n smartcloudops
   kubectl describe ingress smartcloudops-ai -n smartcloudops
   ```

4. **Check Resource Usage**
   ```bash
   kubectl top pods -n smartcloudops
   kubectl describe hpa -n smartcloudops
   ```

## 📚 Additional Resources

- [SmartCloudOps AI Documentation](../../README.md)
- [API Reference](../../docs/API_REFERENCE_COMPLETE.md)
- [Security Guide](../../docs/security/security-baseline-report.md)
- [Production Deployment Guide](../../PRODUCTION_READY_REPORT.md)

## 🤝 Contributing

Please read our [Contributing Guide](../../CONTRIBUTING.md) for development and contribution guidelines.
