# SmartCloudOps AI - Production Deployment Procedures
# Phase 3 Week 7: Production Runbook - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Application Deployment](#application-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Rollback Procedures](#rollback-procedures)
7. [Environment Management](#environment-management)

## Overview

This document provides comprehensive procedures for deploying SmartCloudOps AI to production environments. All deployments must follow these procedures to ensure consistency, reliability, and security.

### Deployment Architecture
- **Infrastructure**: AWS EKS, RDS, ElastiCache, ALB
- **Application**: Containerized microservices with auto-scaling
- **Monitoring**: Prometheus, Grafana, Elasticsearch, Jaeger
- **Security**: RBAC, encryption, network policies, security scanning

## Pre-Deployment Checklist

### 1. Code Review and Testing ✅
- [ ] All code changes have been peer-reviewed
- [ ] Unit tests pass with >95% coverage
- [ ] Integration tests pass successfully
- [ ] Security scans show no high/critical issues
- [ ] Performance tests meet SLA requirements
- [ ] Documentation has been updated

### 2. Infrastructure Readiness ✅
- [ ] Terraform state is clean and up-to-date
- [ ] AWS credentials and permissions verified
- [ ] Kubernetes cluster health confirmed
- [ ] Database migrations tested and ready
- [ ] Backup systems operational
- [ ] Monitoring systems functional

### 3. Security Validation ✅
- [ ] Security audit completed
- [ ] Secrets and certificates updated
- [ ] RBAC policies reviewed and applied
- [ ] Network policies validated
- [ ] Compliance requirements verified
- [ ] Vulnerability scans passed

### 4. Communication and Approval ✅
- [ ] Deployment scheduled and communicated
- [ ] Stakeholders notified
- [ ] Change management approval obtained
- [ ] Rollback plan reviewed and approved
- [ ] On-call personnel informed
- [ ] Customer communication prepared (if needed)

## Infrastructure Deployment

### Step 1: Terraform Infrastructure Deployment

```bash
# Navigate to infrastructure directory
cd infrastructure/terraform

# Initialize Terraform (if first time)
terraform init -backend-config=backend.hcl

# Plan infrastructure changes
terraform plan -var-file=production.tfvars -out=tfplan

# Review the plan carefully
terraform show tfplan

# Apply infrastructure changes
terraform apply tfplan

# Verify infrastructure deployment
terraform output -json > outputs.json
```

### Step 2: Kubernetes Cluster Setup

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name smartcloudops-production-cluster

# Verify cluster connectivity
kubectl cluster-info
kubectl get nodes

# Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/secrets.yaml
kubectl apply -f infrastructure/kubernetes/service.yaml

# Wait for core services
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=smartcloudops-ai -n smartcloudops --timeout=300s
```

### Step 3: Monitoring Stack Deployment

```bash
# Deploy Prometheus
kubectl apply -f monitoring/prometheus/
kubectl wait --for=condition=available deployment/prometheus -n smartcloudops-monitoring --timeout=300s

# Deploy Grafana
kubectl apply -f monitoring/grafana/
kubectl wait --for=condition=available deployment/grafana -n smartcloudops-monitoring --timeout=300s

# Deploy Elasticsearch and Fluentd
kubectl apply -f monitoring/logging/
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=elasticsearch -n smartcloudops-monitoring --timeout=600s

# Deploy Jaeger and OpenTelemetry
kubectl apply -f observability/
kubectl wait --for=condition=available deployment/jaeger-collector -n smartcloudops-monitoring --timeout=300s
```

## Application Deployment

### Step 1: Database Migrations

```bash
# Connect to RDS instance
export DB_HOST=$(terraform output -raw rds_endpoint)
export DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id smartcloudops/production/database --query SecretString --output text | jq -r .password)

# Run database migrations
cd app/
python -m alembic upgrade head

# Verify migration success
python -c "
from app.database import get_db
from sqlalchemy import text
with get_db() as db:
    result = db.execute(text('SELECT version_num FROM alembic_version'))
    print(f'Current DB version: {result.fetchone()[0]}')
"
```

### Step 2: Application Container Deployment

```bash
# Build and push application images
docker build -t smartcloudops/api:${VERSION} -f Dockerfile.api .
docker build -t smartcloudops/worker:${VERSION} -f Dockerfile.worker .

# Push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ${ECR_REGISTRY}
docker tag smartcloudops/api:${VERSION} ${ECR_REGISTRY}/smartcloudops/api:${VERSION}
docker tag smartcloudops/worker:${VERSION} ${ECR_REGISTRY}/smartcloudops/worker:${VERSION}
docker push ${ECR_REGISTRY}/smartcloudops/api:${VERSION}
docker push ${ECR_REGISTRY}/smartcloudops/worker:${VERSION}

# Update Kubernetes deployment manifests
envsubst < infrastructure/kubernetes/deployment.yaml | kubectl apply -f -

# Monitor deployment rollout
kubectl rollout status deployment/smartcloudops-api -n smartcloudops
kubectl rollout status deployment/smartcloudops-worker -n smartcloudops
```

### Step 3: Service Configuration Updates

```bash
# Update ConfigMaps if needed
kubectl apply -f infrastructure/kubernetes/configmap.yaml

# Update Secrets if needed (using external secrets operator)
kubectl apply -f infrastructure/kubernetes/secrets.yaml

# Restart deployments to pick up config changes
kubectl rollout restart deployment/smartcloudops-api -n smartcloudops
kubectl rollout restart deployment/smartcloudops-worker -n smartcloudops

# Verify configuration updates
kubectl get configmap smartcloudops-config -n smartcloudops -o yaml
kubectl describe secret smartcloudops-secrets -n smartcloudops
```

## Post-Deployment Verification

### Step 1: Health Checks ✅

```bash
# Application health checks
kubectl get pods -n smartcloudops
kubectl describe deployment smartcloudops-api -n smartcloudops

# API endpoint health check
curl -f https://api.smartcloudops.ai/api/health
curl -f https://api.smartcloudops.ai/api/status

# Database connectivity check
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
from sqlalchemy import text
with get_db() as db:
    result = db.execute(text('SELECT 1'))
    print('Database connection: OK')
"
```

### Step 2: Monitoring Verification ✅

```bash
# Check Prometheus targets
curl -s https://prometheus.smartcloudops.ai/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# Verify Grafana dashboards
curl -f https://grafana.smartcloudops.ai/api/health

# Check log ingestion
curl -s "https://elasticsearch:9200/smartcloudops-logs-*/_search?size=1" | jq '.hits.total.value'

# Verify tracing
curl -s "http://jaeger-query:16686/api/services" | jq '.data[]'
```

### Step 3: Functional Testing ✅

```bash
# MLOps API functionality
curl -X POST https://api.smartcloudops.ai/api/mlops/experiments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{"name": "deployment-test", "description": "Post-deployment verification"}'

# Performance testing
kubectl run performance-test --image=loadimpact/k6 --rm -it -- \
  run --vus 10 --duration 30s - <<EOF
import http from 'k6/http';
export default function() {
  http.get('https://api.smartcloudops.ai/api/health');
}
EOF

# Security testing
kubectl run security-scan --image=owasp/zap2docker-stable --rm -it -- \
  zap-baseline.py -t https://api.smartcloudops.ai
```

### Step 4: User Acceptance Testing ✅

```bash
# Frontend accessibility
curl -f https://smartcloudops.ai
curl -f https://smartcloudops.ai/api

# Authentication flow
curl -X POST https://api.smartcloudops.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@smartcloudops.ai", "password": "test-password"}'

# End-to-end workflow testing
python scripts/e2e_tests.py --environment production
```

## Rollback Procedures

### Emergency Rollback (< 5 minutes)

```bash
# Immediate rollback to previous version
kubectl rollout undo deployment/smartcloudops-api -n smartcloudops
kubectl rollout undo deployment/smartcloudops-worker -n smartcloudops

# Monitor rollback status
kubectl rollout status deployment/smartcloudops-api -n smartcloudops
kubectl rollout status deployment/smartcloudops-worker -n smartcloudops

# Verify health after rollback
curl -f https://api.smartcloudops.ai/api/health
```

### Database Rollback

```bash
# Restore database from backup (if needed)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier smartcloudops-rollback-$(date +%Y%m%d-%H%M) \
  --db-snapshot-identifier smartcloudops-prod-snapshot-${SNAPSHOT_ID}

# Run database migration rollback
cd app/
python -m alembic downgrade ${PREVIOUS_VERSION}
```

### Infrastructure Rollback

```bash
# Terraform rollback
cd infrastructure/terraform
terraform plan -var-file=production.tfvars -target=aws_eks_cluster.main -destroy
terraform apply -target=aws_eks_cluster.main

# Kubernetes configuration rollback
kubectl apply -f infrastructure/kubernetes/previous-version/
```

## Environment Management

### Development Environment
- **Purpose**: Feature development and testing
- **Access**: Development team
- **Data**: Synthetic/anonymized data
- **Deployment**: Automated on PR merge

### Staging Environment
- **Purpose**: Production-like testing and validation
- **Access**: QA team, product managers
- **Data**: Production-like (anonymized)
- **Deployment**: Manual trigger after development validation

### Production Environment
- **Purpose**: Live customer-facing application
- **Access**: Restricted (production team only)
- **Data**: Real customer data
- **Deployment**: Scheduled maintenance windows

### Environment Promotion Process

```bash
# Development → Staging
./scripts/promote_environment.sh dev staging

# Staging → Production (with approval)
./scripts/promote_environment.sh staging production --require-approval

# Environment health check
./scripts/environment_health_check.sh production
```

## Security Procedures

### Certificate Management
```bash
# Update SSL certificates
kubectl create secret tls smartcloudops-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n smartcloudops --dry-run=client -o yaml | kubectl apply -f -

# Rotate secrets
kubectl create secret generic smartcloudops-secrets \
  --from-literal=DATABASE_PASSWORD=${NEW_DB_PASSWORD} \
  --from-literal=JWT_SECRET=${NEW_JWT_SECRET} \
  -n smartcloudops --dry-run=client -o yaml | kubectl apply -f -
```

### Security Scanning
```bash
# Container image scanning
trivy image smartcloudops/api:${VERSION}
trivy image smartcloudops/worker:${VERSION}

# Kubernetes security scanning
kube-score score infrastructure/kubernetes/*.yaml
```

## Troubleshooting Quick Reference

### Common Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| Pod CrashLoopBackOff | Pods restarting repeatedly | Check logs: `kubectl logs -f deployment/smartcloudops-api -n smartcloudops` |
| Database Connection Failed | 500 errors on API calls | Verify DB credentials and network connectivity |
| High Memory Usage | OOMKilled events | Increase memory limits or optimize application |
| SSL Certificate Expired | HTTPS connection failures | Update certificate with `kubectl create secret tls` |
| Monitoring Down | No metrics/logs | Restart monitoring stack components |

### Emergency Contacts
- **Platform Team**: platform-team@smartcloudops.ai
- **On-Call Engineer**: +1-555-ONCALL (24/7)
- **Security Team**: security-team@smartcloudops.ai
- **DevOps Lead**: devops-lead@smartcloudops.ai

---

**Document Version**: 2.0.0  
**Last Updated**: $(date +%Y-%m-%d)  
**Next Review**: $(date -d '+3 months' +%Y-%m-%d)
