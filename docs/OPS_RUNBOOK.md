# 🛠️ SmartCloudOps AI - Operations Runbook

**Comprehensive operations guide for production support and incident response**

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Monitoring & Alerting](#monitoring--alerting)
- [Incident Response](#incident-response)
- [Common Operations](#common-operations)
- [Maintenance Procedures](#maintenance-procedures)
- [Performance Tuning](#performance-tuning)
- [Disaster Recovery](#disaster-recovery)
- [Emergency Contacts](#emergency-contacts)

## 🎯 System Overview

### Service Architecture
- **Frontend**: Next.js application (Port 3000)
- **Backend API**: Flask application (Port 5000)
- **Database**: PostgreSQL (Port 5432)
- **Cache**: Redis (Port 6379)
- **Monitoring**: Prometheus + Grafana
- **Message Queue**: Celery with Redis broker

### Key Metrics to Monitor
- **Response Time**: API endpoints <500ms P95
- **Error Rate**: <1% across all endpoints
- **CPU Usage**: <70% average across pods
- **Memory Usage**: <80% of allocated memory
- **Database Connections**: <80% of max connections

## 📊 Monitoring & Alerting

### Critical Alerts

#### Application Down
**Alert**: `up{job="smartcloudops-backend"} == 0`
**Severity**: Critical
**Response Time**: Immediate (5 minutes)

**Immediate Actions**:
```bash
# Check pod status
kubectl get pods -n smartcloudops -l app=backend

# Check recent logs
kubectl logs -n smartcloudops -l app=backend --tail=100

# Check resource usage
kubectl top pods -n smartcloudops

# If pods are down, check deployment
kubectl describe deployment backend -n smartcloudops
```

#### High Error Rate
**Alert**: `rate(http_requests_total{status=~"5.."}[5m]) > 0.05`
**Severity**: Critical
**Response Time**: 10 minutes

**Investigation Steps**:
```bash
# Check error logs
kubectl logs -n smartcloudops -l app=backend | grep -i error

# Check database connectivity
kubectl exec -it backend-pod -n smartcloudops -- python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('DB OK')
except Exception as e:
    print(f'DB Error: {e}')
"

# Check external service status
curl -f http://backend:5000/health/external
```

#### Database Issues
**Alert**: `pg_up == 0` or `pg_stat_database_numbackends > 90`
**Severity**: Critical
**Response Time**: 5 minutes

**Immediate Actions**:
```bash
# Check PostgreSQL pod status
kubectl get pods -n smartcloudops -l app=postgresql

# Check database logs
kubectl logs -n smartcloudops postgresql-0 --tail=100

# Check database connections
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT count(*) as connections, 
       state 
FROM pg_stat_activity 
GROUP BY state;"

# Check disk space
kubectl exec -it postgresql-0 -n smartcloudops -- df -h /var/lib/postgresql/data
```

#### High Memory Usage
**Alert**: `container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9`
**Severity**: Warning
**Response Time**: 30 minutes

**Investigation Steps**:
```bash
# Check memory usage by pod
kubectl top pods -n smartcloudops --sort-by=memory

# Get detailed memory stats
kubectl exec -it backend-pod -n smartcloudops -- cat /proc/meminfo

# Check for memory leaks
kubectl exec -it backend-pod -n smartcloudops -- python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Open files: {process.num_fds()}')
"
```

### Warning Alerts

#### Slow Response Times
**Alert**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1`
**Severity**: Warning
**Response Time**: 1 hour

#### High CPU Usage
**Alert**: `rate(container_cpu_usage_seconds_total[5m]) > 0.8`
**Severity**: Warning
**Response Time**: 1 hour

#### Disk Space Low
**Alert**: `(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.85`
**Severity**: Warning
**Response Time**: 2 hours

## 🚨 Incident Response

### Incident Severity Levels

#### Severity 1 (Critical)
- **Definition**: Complete service outage, data loss, security breach
- **Response Time**: 15 minutes
- **Escalation**: Immediate to on-call engineer and management
- **Communication**: Status page update within 30 minutes

#### Severity 2 (High)
- **Definition**: Significant feature degradation, performance issues
- **Response Time**: 1 hour
- **Escalation**: On-call engineer within 2 hours
- **Communication**: Internal team notification

#### Severity 3 (Medium)
- **Definition**: Minor feature issues, non-critical bugs
- **Response Time**: 4 hours
- **Escalation**: Next business day
- **Communication**: Ticket creation

### Incident Response Workflow

1. **Detection**: Alert fired or user report
2. **Assessment**: Determine severity level
3. **Response**: Assign responder based on severity
4. **Investigation**: Identify root cause
5. **Mitigation**: Apply temporary fix if needed
6. **Resolution**: Implement permanent fix
7. **Post-mortem**: Document lessons learned

### Incident Communication Template

```
INCIDENT ALERT - [SEVERITY LEVEL]

Service: SmartCloudOps AI
Start Time: [TIMESTAMP]
Status: [INVESTIGATING/IDENTIFIED/MONITORING/RESOLVED]

Issue: [Brief description]
Impact: [User impact description]
Current Actions: [What's being done]

Next Update: [Timeframe]
Incident Commander: [Name]
```

## 🔄 Common Operations

### Deployment Operations

#### Standard Deployment
```bash
# 1. Verify staging deployment
helm test smartcloudops-ai-staging -n smartcloudops-staging

# 2. Deploy to production
helm upgrade smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  -f values-prod.yaml \
  --set image.tag=v1.0.1 \
  --wait --timeout=10m

# 3. Verify deployment
kubectl rollout status deployment/backend -n smartcloudops
kubectl rollout status deployment/frontend -n smartcloudops

# 4. Run health checks
curl -f https://api.smartcloudops.ai/health
curl -f https://smartcloudops.ai/api/health

# 5. Monitor for 30 minutes
watch kubectl get pods -n smartcloudops
```

#### Emergency Rollback
```bash
# 1. Identify last good deployment
helm history smartcloudops-ai -n smartcloudops

# 2. Rollback to previous version
helm rollback smartcloudops-ai 1 -n smartcloudops

# 3. Verify rollback
kubectl get pods -n smartcloudops
curl -f https://api.smartcloudops.ai/health

# 4. Notify team
echo "Emergency rollback completed at $(date)" | \
  slack-notify "#ops-alerts"
```

### Database Operations

#### Database Backup
```bash
# 1. Create backup
kubectl exec -it postgresql-0 -n smartcloudops -- \
  pg_dump -U postgres smartcloudops | \
  gzip > "backup-$(date +%Y%m%d-%H%M%S).sql.gz"

# 2. Upload to S3
aws s3 cp backup-*.sql.gz s3://smartcloudops-backups/

# 3. Verify backup
gunzip -t backup-*.sql.gz && echo "Backup verified"

# 4. Cleanup old backups (keep 30 days)
find . -name "backup-*.sql.gz" -mtime +30 -delete
```

#### Database Maintenance
```bash
# 1. Check database stats
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
ORDER BY pg_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 10;"

# 2. Analyze slow queries
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# 3. Vacuum and analyze
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
VACUUM ANALYZE;"
```

### Application Scaling

#### Manual Scaling
```bash
# Scale backend pods
kubectl scale deployment backend --replicas=5 -n smartcloudops

# Scale frontend pods
kubectl scale deployment frontend --replicas=3 -n smartcloudops

# Verify scaling
kubectl get pods -n smartcloudops -w
```

#### Auto-scaling Configuration
```bash
# CPU-based auto-scaling
kubectl autoscale deployment backend \
  --min=2 --max=10 --cpu-percent=70 \
  -n smartcloudops

# Memory-based auto-scaling (if metrics server supports)
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: smartcloudops
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF
```

### Log Management

#### Log Collection
```bash
# Collect logs for troubleshooting
kubectl logs -n smartcloudops -l app=backend --since=1h > backend-logs.txt
kubectl logs -n smartcloudops -l app=frontend --since=1h > frontend-logs.txt
kubectl logs -n smartcloudops -l app=postgresql --since=1h > db-logs.txt

# Search for errors
grep -i error *.txt
grep -i exception *.txt
grep -i timeout *.txt
```

#### Log Rotation
```bash
# Configure log rotation for containers
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: logging-config
  namespace: smartcloudops
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
    </source>
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      index_name fluentd.${Time.at(time).strftime('%Y.%m.%d')}
    </match>
EOF
```

## 🔧 Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Tasks
- [ ] Check system health dashboard
- [ ] Review overnight alerts
- [ ] Verify backup completion
- [ ] Monitor resource usage trends

#### Weekly Tasks
- [ ] Review performance metrics
- [ ] Update security patches
- [ ] Clean up old logs and artifacts
- [ ] Review capacity planning metrics

#### Monthly Tasks
- [ ] Security vulnerability scan
- [ ] Database maintenance (VACUUM, ANALYZE)
- [ ] Review and update documentation
- [ ] Capacity planning review
- [ ] Disaster recovery test

### System Updates

#### Security Patch Updates
```bash
# 1. Update base images
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull postgres:15

# 2. Rebuild application images
docker build -t smartcloudops-ai:latest .
docker build -f Dockerfile.frontend -t smartcloudops-frontend:latest .

# 3. Push to registry
docker push registry.company.com/smartcloudops-ai:latest
docker push registry.company.com/smartcloudops-frontend:latest

# 4. Deploy updates
helm upgrade smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --set image.tag=latest \
  --namespace smartcloudops
```

#### Kubernetes Cluster Updates
```bash
# 1. Drain nodes one by one
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# 2. Update node
# (Cloud provider specific - AWS EKS, Azure AKS, etc.)

# 3. Uncordon node
kubectl uncordon node-1

# 4. Verify pods rescheduled
kubectl get pods -n smartcloudops -o wide

# 5. Repeat for remaining nodes
```

### Certificate Management

#### SSL Certificate Renewal
```bash
# Check certificate expiration
echo | openssl s_client -servername smartcloudops.ai -connect smartcloudops.ai:443 2>/dev/null | \
  openssl x509 -noout -dates

# Renew Let's Encrypt certificate (cert-manager)
kubectl annotate certificate smartcloudops-tls -n smartcloudops \
  cert-manager.io/force-renew="$(date +%s)"

# Verify renewal
kubectl describe certificate smartcloudops-tls -n smartcloudops
```

## ⚡ Performance Tuning

### Database Performance

#### Query Optimization
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Analyze slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements 
WHERE mean_time > 1000 
ORDER BY mean_time DESC;

-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_anomalies_timestamp ON anomalies(timestamp DESC);
CREATE INDEX CONCURRENTLY idx_users_active ON users(is_active) WHERE is_active = true;
```

#### Connection Pool Tuning
```python
# Database connection pool settings
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'echo': False
}
```

### Application Performance

#### Memory Optimization
```python
# Python memory optimization
import gc
import psutil

def monitor_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")
    
    if memory_mb > 500:  # 500MB threshold
        gc.collect()
        print("Garbage collection triggered")
```

#### Redis Optimization
```bash
# Redis configuration tuning
kubectl exec -it redis-0 -n smartcloudops -- redis-cli CONFIG SET maxmemory-policy allkeys-lru
kubectl exec -it redis-0 -n smartcloudops -- redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### Infrastructure Tuning

#### Kubernetes Resource Limits
```yaml
# Optimized resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Load Balancer Configuration
```nginx
# NGINX optimization
worker_processes auto;
worker_connections 1024;

upstream backend {
    least_conn;
    server backend-1:5000 max_fails=3 fail_timeout=30s;
    server backend-2:5000 max_fails=3 fail_timeout=30s;
    server backend-3:5000 max_fails=3 fail_timeout=30s;
}

server {
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

## 🔥 Disaster Recovery

### Backup Strategy

#### Automated Backups
```bash
#!/bin/bash
# Daily backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"
mkdir -p $BACKUP_DIR

# Database backup
kubectl exec -it postgresql-0 -n smartcloudops -- \
  pg_dump -U postgres smartcloudops | \
  gzip > "$BACKUP_DIR/database.sql.gz"

# Application data backup
kubectl cp smartcloudops/backend-0:/app/uploads "$BACKUP_DIR/uploads"
kubectl cp smartcloudops/backend-0:/app/models "$BACKUP_DIR/models"

# Configuration backup
kubectl get configmap,secret -n smartcloudops -o yaml > "$BACKUP_DIR/config.yaml"

# Upload to cloud storage
aws s3 sync $BACKUP_DIR s3://smartcloudops-backups/$DATE/

# Cleanup local backups older than 7 days
find /backups -type d -mtime +7 -exec rm -rf {} +
```

### Recovery Procedures

#### Database Recovery
```bash
# 1. Stop application
kubectl scale deployment backend --replicas=0 -n smartcloudops

# 2. Restore database
kubectl exec -it postgresql-0 -n smartcloudops -- \
  psql -U postgres -c "DROP DATABASE smartcloudops;"
kubectl exec -it postgresql-0 -n smartcloudops -- \
  psql -U postgres -c "CREATE DATABASE smartcloudops;"

gunzip -c backup/database.sql.gz | \
  kubectl exec -i postgresql-0 -n smartcloudops -- \
  psql -U postgres smartcloudops

# 3. Verify data integrity
kubectl exec -it postgresql-0 -n smartcloudops -- \
  psql -U postgres smartcloudops -c "SELECT COUNT(*) FROM users;"

# 4. Restart application
kubectl scale deployment backend --replicas=3 -n smartcloudops
```

#### Full System Recovery
```bash
# 1. Restore Kubernetes cluster (cloud provider specific)
# 2. Restore persistent volumes
# 3. Restore configuration
kubectl apply -f backup/config.yaml

# 4. Deploy application
helm install smartcloudops-ai ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops \
  -f values-prod.yaml

# 5. Restore application data
kubectl cp backup/uploads smartcloudops/backend-0:/app/uploads
kubectl cp backup/models smartcloudops/backend-0:/app/models

# 6. Verify system health
./scripts/health-check.sh
```

### Testing Recovery Procedures

#### Monthly DR Test
```bash
#!/bin/bash
# Disaster recovery test script

echo "Starting DR test at $(date)"

# 1. Create test backup
./scripts/backup.sh test

# 2. Deploy to DR environment
helm install smartcloudops-ai-dr ./deploy/helm/smartcloudops-ai \
  --namespace smartcloudops-dr \
  -f values-dr.yaml

# 3. Restore data
./scripts/restore.sh test smartcloudops-dr

# 4. Run health checks
./scripts/health-check.sh smartcloudops-dr

# 5. Cleanup DR environment
helm uninstall smartcloudops-ai-dr -n smartcloudops-dr

echo "DR test completed at $(date)"
```

## 📞 Emergency Contacts

### On-Call Rotation
- **Primary**: ops-primary@company.com, +1-555-0001
- **Secondary**: ops-secondary@company.com, +1-555-0002
- **Escalation**: engineering-manager@company.com, +1-555-0003

### External Vendors
- **Cloud Provider**: support.aws.com, +1-206-266-4064
- **Database Vendor**: postgresql.org/support
- **Monitoring Vendor**: support@grafana.com

### Communication Channels
- **Slack**: #ops-alerts, #incident-response
- **Email**: ops-team@company.com
- **Status Page**: status.smartcloudops.ai
- **Documentation**: docs.smartcloudops.ai

---

## 📚 Related Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Reference](./API_REFERENCE_COMPLETE.md)
- [Security Guide](./SECURITY.md)

---

*This runbook should be reviewed and updated monthly. Last updated: January 2024*
