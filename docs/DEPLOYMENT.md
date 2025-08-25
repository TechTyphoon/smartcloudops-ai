# 🚀 SmartCloudOps AI - Deployment Guide

**Complete deployment guide for production, staging, and development environments**

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Configuration](#configuration)
- [Monitoring Setup](#monitoring-setup)
- [Troubleshooting](#troubleshooting)

## ⚡ Quick Start

### Local Development (5 minutes)

```bash
# Clone repository
git clone https://github.com/your-org/smartcloudops-ai.git
cd smartcloudops-ai

# Start with Docker Compose
docker-compose up -d

# Wait for services to start
sleep 30

# Access the application
open http://localhost:3000
```

### Production Deployment (Kubernetes)

```bash
# Deploy with Helm
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  -f values-prod.yaml

# Verify deployment
kubectl get pods -n smartcloudops
```

## 📋 Prerequisites

### System Requirements

#### Minimum (Development)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Network**: 100 Mbps

#### Recommended (Production)
- **CPU**: 16+ cores
- **RAM**: 32+ GB
- **Storage**: 500+ GB SSD
- **Network**: 1+ Gbps

### Software Dependencies

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Kubernetes**: 1.25+
- **Helm**: 3.10+
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 13+
- **Redis**: 6+

## 🏗️ Environment Setup

### Development Environment

```bash
# 1. Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Install Node.js dependencies
npm install

# 3. Setup environment variables
cp env.example .env
# Edit .env with your configuration

# 4. Initialize database
python scripts/init_db.py

# 5. Start development servers
# Terminal 1: Backend
python -m flask run --debug

# Terminal 2: Frontend
npm run dev
```

### Staging Environment

```bash
# Deploy to staging namespace
helm install smartcloudops-ai-staging ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops-staging \
  --create-namespace \
  -f values-staging.yaml \
  --set image.tag=staging-latest

# Configure ingress for staging
kubectl apply -f deploy/k8s/staging-ingress.yaml
```

### Production Environment

```bash
# Deploy to production
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops-prod \
  --create-namespace \
  -f values-prod.yaml \
  --set image.tag=v1.0.0

# Apply production configurations
kubectl apply -f deploy/k8s/prod-configs/
```

## 🌐 Deployment Options

### Option 1: Docker Compose (Development)

**Best for**: Local development, testing, small deployments

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/smartcloudops
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:5000

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: smartcloudops
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

#### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Option 2: Kubernetes with Helm (Production)

**Best for**: Production, staging, scalable deployments

#### Helm Chart Structure

```
deploy/helm/smartcloudops-ai/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-staging.yaml
├── values-prod.yaml
└── templates/
    ├── backend/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── configmap.yaml
    │   └── secret.yaml
    ├── frontend/
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    └── networkpolicy.yaml
```

#### Installation Commands

```bash
# Add required repositories
helm repo add postgresql https://charts.bitnami.com/bitnami
helm repo add redis https://charts.bitnami.com/bitnami
helm repo update

# Install dependencies
helm dependency build deploy/helm/smartcloudops-ai/

# Deploy to production
helm install smartcloudops-ai deploy/helm/smartcloudops-ai/ \
  --namespace smartcloudops \
  --create-namespace \
  -f deploy/helm/smartcloudops-ai/values-prod.yaml \
  --wait --timeout=10m

# Upgrade deployment
helm upgrade smartcloudops-ai deploy/helm/smartcloudops-ai/ \
  --namespace smartcloudops \
  -f deploy/helm/smartcloudops-ai/values-prod.yaml

# Rollback if needed
helm rollback smartcloudops-ai 1 --namespace smartcloudops
```

### Option 3: Cloud-Specific Deployments

#### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name smartcloudops-cluster \
  --region us-west-2 \
  --nodes 3 \
  --node-type t3.medium

# Deploy with AWS-specific configurations
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  -f values-aws.yaml
```

#### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group smartcloudops-rg \
  --name smartcloudops-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3

# Deploy with Azure-specific configurations
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  -f values-azure.yaml
```

#### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create smartcloudops-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium

# Deploy with GCP-specific configurations
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  --create-namespace \
  -f values-gcp.yaml
```

## ⚙️ Configuration

### Environment Variables

#### Backend Configuration

```bash
# Application
FLASK_APP=app/main.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/smartcloudops
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

# ML/AI
ML_MODEL_PATH=/app/models
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-hf-key

# Monitoring
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# External Services
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_SIGNING_SECRET=your-slack-secret
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email
EMAIL_PASSWORD=your-app-password
```

#### Frontend Configuration

```bash
# API
NEXT_PUBLIC_API_URL=https://api.smartcloudops.ai
NEXT_PUBLIC_WS_URL=wss://api.smartcloudops.ai

# Analytics
NEXT_PUBLIC_GA_ID=GA_MEASUREMENT_ID
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Features
NEXT_PUBLIC_ENABLE_PWA=true
NEXT_PUBLIC_ENABLE_DARK_MODE=true
```

### Kubernetes Secrets

```bash
# Create secrets for sensitive data
kubectl create secret generic smartcloudops-secrets \
  --namespace smartcloudops \
  --from-literal=database-url="postgresql://user:pass@db:5432/smartcloudops" \
  --from-literal=redis-url="redis://redis:6379/0" \
  --from-literal=jwt-secret="your-jwt-secret" \
  --from-literal=openai-api-key="your-openai-key" \
  --from-literal=slack-bot-token="xoxb-your-slack-token"

# Create ConfigMap for non-sensitive configuration
kubectl create configmap smartcloudops-config \
  --namespace smartcloudops \
  --from-literal=log-level="INFO" \
  --from-literal=prometheus-multiproc-dir="/tmp/prometheus"
```

### Database Setup

#### PostgreSQL Configuration

```sql
-- Create database and user
CREATE DATABASE smartcloudops;
CREATE USER smartcloudops_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE smartcloudops TO smartcloudops_user;

-- Connect to database
\c smartcloudops;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS monitoring;
```

#### Database Migration

```bash
# Run database migrations
python -m flask db upgrade

# Create initial admin user
python scripts/create_admin.py \
  --email admin@smartcloudops.ai \
  --password SecureAdminPassword123! \
  --name "System Administrator"
```

## 📊 Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'smartcloudops-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'smartcloudops-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/api/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards

```bash
# Import dashboards
curl -X POST \
  http://admin:admin@grafana:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana/dashboards/overview.json

# Set up data sources
curl -X POST \
  http://admin:admin@grafana:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'
```

### Health Checks

```bash
# Backend health check
curl http://localhost:5000/health
# Expected: {"status": "healthy", "timestamp": "2024-01-15T12:00:00Z"}

# Frontend health check
curl http://localhost:3000/api/health
# Expected: {"status": "ok", "uptime": 3600}

# Database health check
curl http://localhost:5000/health/db
# Expected: {"status": "connected", "response_time_ms": 15}

# Redis health check
curl http://localhost:5000/health/redis
# Expected: {"status": "connected", "response_time_ms": 5}
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: Backend fails to start

**Symptoms**: 
- Container exits with code 1
- Database connection errors
- Import errors

**Solutions**:
```bash
# Check logs
docker-compose logs backend

# Verify database connectivity
docker-compose exec backend python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:pass@db:5432/smartcloudops')
print('Database connection successful')
"

# Check environment variables
docker-compose exec backend env | grep -E "(DATABASE|REDIS|SECRET)"

# Rebuild with no cache
docker-compose build --no-cache backend
```

#### Issue: Frontend build failures

**Symptoms**:
- npm install errors
- Build process fails
- Module not found errors

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+

# Build with verbose output
npm run build --verbose
```

#### Issue: Kubernetes pods not starting

**Symptoms**:
- Pods stuck in Pending/CrashLoopBackOff
- ImagePullBackOff errors
- Resource constraints

**Solutions**:
```bash
# Check pod status
kubectl get pods -n smartcloudops

# Describe problematic pod
kubectl describe pod <pod-name> -n smartcloudops

# Check logs
kubectl logs <pod-name> -n smartcloudops --previous

# Check resource usage
kubectl top pods -n smartcloudops

# Verify secrets and configmaps
kubectl get secrets,configmaps -n smartcloudops
```

#### Issue: Database migration failures

**Symptoms**:
- Migration scripts fail
- Table creation errors
- Permission denied errors

**Solutions**:
```bash
# Check database connectivity
python -c "
from app.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print(result.fetchone())
"

# Run migrations manually
python -m flask db current
python -m flask db upgrade

# Reset migrations (WARNING: Data loss)
python -m flask db downgrade base
python -m flask db upgrade
```

### Performance Issues

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Analyze Python memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Optimize PostgreSQL
# Add to postgresql.conf:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB
```

#### Slow Database Queries

```bash
# Enable query logging
# Add to postgresql.conf:
# log_min_duration_statement = 1000
# log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

# Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

### Network Issues

#### Service Discovery Problems

```bash
# Check DNS resolution
kubectl exec -it <pod-name> -n smartcloudops -- nslookup backend

# Test service connectivity
kubectl exec -it <pod-name> -n smartcloudops -- wget -qO- http://backend:5000/health

# Check network policies
kubectl get networkpolicies -n smartcloudops
```

#### Ingress Issues

```bash
# Check ingress status
kubectl get ingress -n smartcloudops

# Verify ingress controller
kubectl get pods -n ingress-nginx

# Test external connectivity
curl -H "Host: smartcloudops.local" http://<ingress-ip>/health
```

### Log Analysis

#### Centralized Logging

```bash
# View application logs
kubectl logs -f deployment/backend -n smartcloudops

# Search logs with grep
kubectl logs deployment/backend -n smartcloudops | grep ERROR

# Export logs for analysis
kubectl logs deployment/backend -n smartcloudops --since=1h > backend-logs.txt
```

#### Common Log Patterns

```bash
# Error patterns to watch for
grep -E "(ERROR|CRITICAL|Exception)" logs/*.log

# Performance patterns
grep -E "(slow|timeout|connection)" logs/*.log

# Security patterns
grep -E "(auth|login|permission)" logs/*.log
```

## 🔄 Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump -h localhost -U smartcloudops_user smartcloudops > backup.sql

# Restore from backup
psql -h localhost -U smartcloudops_user smartcloudops < backup.sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
```

### Application Data Backup

```bash
# Backup uploaded files
tar -czf app_data_backup.tar.gz /app/uploads /app/models

# Backup Redis data
redis-cli --rdb /backups/redis_backup.rdb

# Backup configuration
kubectl get configmap,secret -n smartcloudops -o yaml > config_backup.yaml
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend pods
kubectl scale deployment backend --replicas=5 -n smartcloudops

# Auto-scaling configuration
kubectl autoscale deployment backend \
  --min=2 \
  --max=10 \
  --cpu-percent=70 \
  -n smartcloudops
```

### Database Scaling

```bash
# Read replicas for PostgreSQL
# Add to postgresql.conf:
# wal_level = replica
# max_wal_senders = 3
# wal_keep_segments = 64

# Connection pooling with PgBouncer
# Deploy PgBouncer as a sidecar or separate service
```

---

## 📚 Related Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE_COMPLETE.md)
- [Operations Runbook](./OPS_RUNBOOK.md)
- [Security Guide](./SECURITY.md)

---

*For additional support, please refer to our [troubleshooting guide](./TROUBLESHOOTING.md) or contact the development team.*