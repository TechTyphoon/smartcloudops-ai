# SmartCloudOps AI - Kubernetes Deployment

This directory contains Kubernetes manifests for deploying SmartCloudOps AI in production environments with high availability, scalability, and security.

## 📁 Kubernetes Structure

```
k8s/
├── 📄 00-namespace-and-storage.yaml    # Namespace and storage setup
├── 📄 01-database.yaml                 # PostgreSQL database deployment
├── 📄 02-application.yaml              # Main application deployment
├── 📄 03-nginx.yaml                    # Nginx ingress controller
├── 📄 04-prometheus.yaml               # Prometheus monitoring stack
├── 📄 05-grafana.yaml                  # Grafana visualization
├── 📄 app.yaml                         # Application deployment
├── 📄 monitoring.yaml                  # Monitoring stack deployment
├── 📄 namespace.yaml                   # Namespace definition
├── 📄 postgresql.yaml                  # PostgreSQL configuration
├── 📄 redis.yaml                       # Redis cache deployment
└── 📄 secret-template.yaml             # Secret management template
```

## 🚀 Quick Start

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm (optional)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify cluster access
kubectl cluster-info
```

### Deploy Complete Stack
```bash
# Create namespace and storage
kubectl apply -f 00-namespace-and-storage.yaml

# Deploy database
kubectl apply -f 01-database.yaml

# Deploy application
kubectl apply -f 02-application.yaml

# Deploy monitoring
kubectl apply -f 04-prometheus.yaml
kubectl apply -f 05-grafana.yaml

# Deploy ingress
kubectl apply -f 03-nginx.yaml
```

### Verify Deployment
```bash
# Check all resources
kubectl get all -n smartcloudops

# Check application status
kubectl get pods -n smartcloudops

# Check services
kubectl get svc -n smartcloudops
```

## 🏗️ Architecture Overview

### Namespace Structure
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: smartcloudops
  labels:
    name: smartcloudops
    environment: production
```

### Application Components
- **SmartCloudOps App**: Main Flask application
- **PostgreSQL**: Primary database
- **Redis**: Caching layer
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Nginx Ingress**: Load balancer and SSL termination

## 🔧 Configuration

### Environment Variables
```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: smartcloudops-secrets
        key: database-url
  - name: JWT_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: smartcloudops-secrets
        key: jwt-secret
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: smartcloudops-secrets
        key: openai-api-key
```

### Resource Limits
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 🔒 Security Configuration

### Secret Management
```bash
# Create secrets
kubectl create secret generic smartcloudops-secrets \
  --from-literal=database-url="postgresql://user:pass@postgres:5432/smartcloudops" \
  --from-literal=jwt-secret="your-secret-key" \
  --from-literal=openai-api-key="your-openai-key" \
  -n smartcloudops
```

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: smartcloudops-network-policy
spec:
  podSelector:
    matchLabels:
      app: smartcloudops
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 5000
```

### RBAC Configuration
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: smartcloudops
  name: smartcloudops-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

## 📊 Monitoring Setup

### Prometheus Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'smartcloudops'
        static_configs:
          - targets: ['smartcloudops-app:5000']
```

### Grafana Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
data:
  datasources.yml: |
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus:9090
        access: proxy
        isDefault: true
```

## 🔄 Deployment Strategies

### Rolling Update
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### Blue-Green Deployment
```bash
# Deploy new version
kubectl apply -f 02-application-v2.yaml

# Switch traffic
kubectl patch service smartcloudops-service \
  -p '{"spec":{"selector":{"version":"v2"}}}'
```

### Canary Deployment
```yaml
spec:
  replicas: 10
  template:
    metadata:
      labels:
        version: v1
        canary: "false"
---
spec:
  replicas: 1
  template:
    metadata:
      labels:
        version: v2
        canary: "true"
```

## 🔍 Troubleshooting

### Common Issues

1. **Pod Startup Issues**
   ```bash
   # Check pod logs
   kubectl logs -f deployment/smartcloudops-app -n smartcloudops
   
   # Check pod events
   kubectl describe pod <pod-name> -n smartcloudops
   ```

2. **Database Connection Issues**
   ```bash
   # Check database pod
   kubectl get pods -n smartcloudops -l app=postgres
   
   # Check database logs
   kubectl logs -f deployment/postgres -n smartcloudops
   ```

3. **Service Discovery Issues**
   ```bash
   # Check services
   kubectl get svc -n smartcloudops
   
   # Test service connectivity
   kubectl run test-pod --image=busybox -it --rm --restart=Never -- nslookup smartcloudops-service
   ```

### Debug Commands
```bash
# Port forward to access services
kubectl port-forward svc/smartcloudops-service 5000:5000 -n smartcloudops

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n smartcloudops

# Access Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n smartcloudops
```

## 📈 Scaling

### Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: smartcloudops-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: smartcloudops-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Pod Autoscaling
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: smartcloudops-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: smartcloudops-app
  updatePolicy:
    updateMode: "Auto"
```

## 🔄 Backup and Recovery

### Database Backup
```bash
# Create backup job
kubectl apply -f backup-job.yaml

# Manual backup
kubectl exec -it deployment/postgres -n smartcloudops -- pg_dump -U postgres smartcloudops > backup.sql
```

### Configuration Backup
```bash
# Backup all resources
kubectl get all -n smartcloudops -o yaml > backup.yaml

# Backup secrets
kubectl get secrets -n smartcloudops -o yaml > secrets-backup.yaml
```

## 🚀 Production Deployment

### Production Checklist
- [ ] **Security**: Secrets configured, RBAC enabled
- [ ] **Monitoring**: Prometheus and Grafana deployed
- [ ] **Logging**: Centralized logging configured
- [ ] **Backup**: Database backup strategy implemented
- [ ] **Scaling**: HPA/VPA configured
- [ ] **SSL**: TLS certificates configured
- [ ] **Network**: Network policies applied
- [ ] **Testing**: Load testing completed

### Production Commands
```bash
# Deploy to production
kubectl apply -f k8s/ -n smartcloudops

# Verify deployment
kubectl get all -n smartcloudops
kubectl get events -n smartcloudops --sort-by='.lastTimestamp'

# Monitor deployment
kubectl logs -f deployment/smartcloudops-app -n smartcloudops
```

## 📚 Best Practices

### Security
- **Secrets Management**: Use Kubernetes secrets or external secret managers
- **Network Policies**: Implement strict network policies
- **RBAC**: Use least privilege principle
- **Pod Security**: Enable Pod Security Standards

### Performance
- **Resource Limits**: Set appropriate resource requests and limits
- **Horizontal Scaling**: Use HPA for automatic scaling
- **Caching**: Implement Redis for caching
- **CDN**: Use CDN for static assets

### Reliability
- **Health Checks**: Implement proper liveness and readiness probes
- **Rolling Updates**: Use rolling update strategy
- **Backup Strategy**: Regular database and configuration backups
- **Monitoring**: Comprehensive monitoring and alerting

## 🤝 Contributing

### Adding New Resources
1. **Follow Naming Convention**: Use descriptive names
2. **Document Changes**: Update this README
3. **Test Deployment**: Test in staging environment
4. **Security Review**: Review security implications
5. **Performance Impact**: Consider performance impact

### Deployment Review Checklist
- [ ] Resources are properly configured
- [ ] Security settings are appropriate
- [ ] Monitoring is configured
- [ ] Backup strategy is implemented
- [ ] Rollback plan is available

---

**SmartCloudOps AI v3.3.0** - Kubernetes Deployment
