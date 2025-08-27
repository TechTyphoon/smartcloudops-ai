# 🛠️ SmartCloudOps AI - Phase 4 Operational Runbooks

**Enhanced operational procedures for production support and incident response**

## 📋 Table of Contents

- [Incident Response Procedures](#incident-response-procedures)
- [Rollback Procedures](#rollback-procedures)
- [Database Recovery](#database-recovery)
- [Performance Troubleshooting](#performance-troubleshooting)
- [Security Incident Response](#security-incident-response)
- [Monitoring & Alerting](#monitoring--alerting)
- [Emergency Contacts](#emergency-contacts)

## 🚨 Incident Response Procedures

### Incident Severity Levels

#### P0 - Critical (Immediate Response)
- **Service completely down**
- **Data loss or corruption**
- **Security breach**
- **Response Time**: 5 minutes
- **Escalation**: Immediate to on-call engineer

#### P1 - High (Urgent Response)
- **Service degraded significantly**
- **High error rates (>5%)**
- **Performance issues affecting users**
- **Response Time**: 15 minutes
- **Escalation**: Within 30 minutes

#### P2 - Medium (Normal Response)
- **Minor service issues**
- **Performance degradation**
- **Non-critical features down**
- **Response Time**: 1 hour
- **Escalation**: Within 2 hours

#### P3 - Low (Scheduled Response)
- **Cosmetic issues**
- **Documentation updates**
- **Feature requests**
- **Response Time**: 24 hours
- **Escalation**: Within 48 hours

### Incident Response Workflow

#### 1. Incident Detection & Acknowledgment
```bash
# Check current alerts
kubectl get events -n smartcloudops --sort-by='.lastTimestamp'

# Check pod status
kubectl get pods -n smartcloudops -o wide

# Check service endpoints
kubectl get endpoints -n smartcloudops

# Check recent logs
kubectl logs -n smartcloudops -l app=backend --tail=100
```

#### 2. Initial Assessment
```bash
# Check application health
curl -f http://backend:5000/health

# Check database connectivity
kubectl exec -it backend-pod -n smartcloudops -- python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ Database OK')
except Exception as e:
    print(f'❌ Database Error: {e}')
"

# Check external dependencies
curl -f http://backend:5000/health/external
```

#### 3. Communication Protocol
```bash
# Create incident channel
# Channel: #incident-smartcloudops-{YYYYMMDD}-{P0/P1/P2/P3}

# Update status page
# Update: https://status.smartcloudops.ai

# Notify stakeholders
# Slack: @oncall @engineering @product
```

## 🔄 Rollback Procedures

### Application Rollback

#### 1. Quick Rollback (Last Known Good Version)
```bash
# Get current deployment
kubectl get deployment backend -n smartcloudops -o yaml > current-deployment.yaml

# Rollback to previous version
kubectl rollout undo deployment/backend -n smartcloudops

# Verify rollback
kubectl rollout status deployment/backend -n smartcloudops

# Check application health
curl -f http://backend:5000/health
```

#### 2. Specific Version Rollback
```bash
# List available revisions
kubectl rollout history deployment/backend -n smartcloudops

# Rollback to specific revision
kubectl rollout undo deployment/backend -n smartcloudops --to-revision=2

# Verify rollback
kubectl rollout status deployment/backend -n smartcloudops
```

#### 3. Database Schema Rollback
```bash
# Check current migration
kubectl exec -it backend-pod -n smartcloudops -- alembic current

# List migration history
kubectl exec -it backend-pod -n smartcloudops -- alembic history

# Rollback to previous migration
kubectl exec -it backend-pod -n smartcloudops -- alembic downgrade -1

# Verify database state
kubectl exec -it backend-pod -n smartcloudops -- python -c "
from app.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT version_num FROM alembic_version')
    print(f'Current version: {result.scalar()}')
"
```

### Infrastructure Rollback

#### 1. Terraform Rollback
```bash
# Check current state
terraform show

# List available states
terraform state list

# Rollback to previous state
terraform apply -var-file=previous.tfvars

# Verify infrastructure
terraform plan
```

#### 2. Kubernetes Configuration Rollback
```bash
# Get current config
kubectl get configmap -n smartcloudops -o yaml > current-config.yaml

# Apply previous configuration
kubectl apply -f previous-config.yaml

# Restart pods to pick up new config
kubectl rollout restart deployment/backend -n smartcloudops
```

## 🗄️ Database Recovery

### PostgreSQL Recovery Procedures

#### 1. Connection Issues
```bash
# Check PostgreSQL pod status
kubectl get pods -n smartcloudops -l app=postgresql

# Check PostgreSQL logs
kubectl logs -n smartcloudops postgresql-0 --tail=100

# Check database connections
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT count(*) as connections, 
       state,
       application_name
FROM pg_stat_activity 
GROUP BY state, application_name
ORDER BY connections DESC;
"
```

#### 2. Database Corruption Recovery
```bash
# Stop application
kubectl scale deployment backend -n smartcloudops --replicas=0

# Create backup before recovery
kubectl exec -it postgresql-0 -n smartcloudops -- pg_dump -U postgres smartcloudops > backup-$(date +%Y%m%d-%H%M%S).sql

# Run database recovery
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "REINDEX DATABASE smartcloudops;"

# Check database integrity
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
"

# Restart application
kubectl scale deployment backend -n smartcloudops --replicas=3
```

#### 3. Data Restoration
```bash
# Stop application
kubectl scale deployment backend -n smartcloudops --replicas=0

# Drop and recreate database
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
DROP DATABASE IF EXISTS smartcloudops;
CREATE DATABASE smartcloudops;
"

# Restore from backup
kubectl exec -i postgresql-0 -n smartcloudops -- psql -U postgres smartcloudops < backup-20240827-143000.sql

# Run migrations
kubectl exec -it backend-pod -n smartcloudops -- alembic upgrade head

# Restart application
kubectl scale deployment backend -n smartcloudops --replicas=3
```

## ⚡ Performance Troubleshooting

### High CPU Usage
```bash
# Check CPU usage
kubectl top pods -n smartcloudops

# Check CPU limits
kubectl describe pod backend-pod -n smartcloudops | grep -A 5 "Limits:"

# Check application metrics
curl http://backend:5000/metrics | grep cpu

# Check system resources
kubectl exec -it backend-pod -n smartcloudops -- top -n 1
```

### High Memory Usage
```bash
# Check memory usage
kubectl top pods -n smartcloudops

# Check memory limits
kubectl describe pod backend-pod -n smartcloudops | grep -A 5 "Limits:"

# Check application memory
curl http://backend:5000/metrics | grep memory

# Check for memory leaks
kubectl exec -it backend-pod -n smartcloudops -- python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Memory %: {process.memory_percent():.2f}%')
"
```

### Slow Response Times
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://backend:5000/health

# Check database query performance
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT query, 
       calls, 
       total_time, 
       mean_time,
       rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check slow queries
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT query_start,
       state,
       query
FROM pg_stat_activity 
WHERE state = 'active' 
AND query NOT LIKE '%pg_stat_activity%'
ORDER BY query_start;
"
```

## 🔒 Security Incident Response

### Unauthorized Access
```bash
# Check authentication logs
kubectl logs -n smartcloudops -l app=backend | grep -i "auth\|login\|unauthorized"

# Check failed login attempts
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT user_id, 
       ip_address, 
       event_type, 
       created_at
FROM security_events 
WHERE event_type = 'failed_login'
AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
"

# Check for suspicious IPs
kubectl logs -n smartcloudops -l app=backend | grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" | sort | uniq -c | sort -nr
```

### Data Breach Response
```bash
# Immediately isolate affected systems
kubectl scale deployment backend -n smartcloudops --replicas=0

# Preserve evidence
kubectl logs -n smartcloudops -l app=backend --since=1h > security-logs-$(date +%Y%m%d-%H%M%S).log

# Check database for unauthorized access
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT user_id, 
       action, 
       table_name, 
       created_at
FROM audit_log 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
"

# Rotate secrets
kubectl delete secret app-secrets -n smartcloudops
kubectl create secret generic app-secrets -n smartcloudops \
  --from-literal=JWT_SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=DEFAULT_ADMIN_PASSWORD=$(openssl rand -base64 32)
```

## 📊 Monitoring & Alerting

### Alert Investigation

#### 1. High Error Rate Alert
```bash
# Check error logs
kubectl logs -n smartcloudops -l app=backend | grep -i error | tail -50

# Check error metrics
curl http://backend:5000/metrics | grep -E "(error|exception)"

# Check application health
curl -v http://backend:5000/health

# Check database errors
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT * FROM pg_stat_database 
WHERE datname = 'smartcloudops';
"
```

#### 2. High Latency Alert
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://backend:5000/health

# Check database performance
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT pid, 
       now() - pg_stat_activity.query_start AS duration, 
       query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Check resource usage
kubectl top pods -n smartcloudops
```

#### 3. Service Down Alert
```bash
# Check pod status
kubectl get pods -n smartcloudops -o wide

# Check service endpoints
kubectl get endpoints -n smartcloudops

# Check pod logs
kubectl logs -n smartcloudops -l app=backend --tail=100

# Check pod events
kubectl describe pod backend-pod -n smartcloudops
```

### SLO Monitoring

#### 1. Check SLO Compliance
```bash
# Get SLO status
curl http://backend:5000/slos/status

# Check specific SLO
curl http://backend:5000/slos/api_availability

# Check error budget
curl http://backend:5000/slos/error-budget
```

#### 2. SLO Alert Investigation
```bash
# Check SLO metrics
curl http://backend:5000/metrics | grep -E "(slo|availability|latency)"

# Check historical SLO data
curl http://backend:5000/slos/history?days=7

# Check SLO trends
curl http://backend:5000/slos/trends
```

## 📞 Emergency Contacts

### On-Call Rotation
- **Primary**: @oncall-engineer
- **Secondary**: @senior-engineer
- **Escalation**: @engineering-manager

### External Contacts
- **Cloud Provider**: AWS Support (Premium)
- **Database**: PostgreSQL Support
- **Security**: Security Team (@security)

### Communication Channels
- **Incident Channel**: #incident-smartcloudops
- **Engineering**: #engineering
- **Status Page**: https://status.smartcloudops.ai
- **PagerDuty**: SmartCloudOps On-Call

### Escalation Matrix

#### P0 - Critical
1. **Immediate**: On-call engineer
2. **5 minutes**: Senior engineer
3. **15 minutes**: Engineering manager
4. **30 minutes**: CTO

#### P1 - High
1. **15 minutes**: On-call engineer
2. **30 minutes**: Senior engineer
3. **1 hour**: Engineering manager

#### P2 - Medium
1. **1 hour**: On-call engineer
2. **2 hours**: Senior engineer
3. **4 hours**: Engineering manager

#### P3 - Low
1. **24 hours**: On-call engineer
2. **48 hours**: Senior engineer

## 🔧 Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- [ ] Check SLO compliance
- [ ] Review error rates
- [ ] Check resource usage
- [ ] Review security events

#### Weekly
- [ ] Update dependencies
- [ ] Review performance metrics
- [ ] Check database performance
- [ ] Review access logs

#### Monthly
- [ ] Security audit
- [ ] Performance optimization
- [ ] Capacity planning
- [ ] Disaster recovery test

### Backup Procedures

#### Database Backup
```bash
# Create daily backup
kubectl exec -it postgresql-0 -n smartcloudops -- pg_dump -U postgres smartcloudops > backup-daily-$(date +%Y%m%d).sql

# Create weekly backup
kubectl exec -it postgresql-0 -n smartcloudops -- pg_dump -U postgres smartcloudops > backup-weekly-$(date +%Y%m-%U).sql

# Upload to S3
aws s3 cp backup-daily-$(date +%Y%m%d).sql s3://smartcloudops-backups/daily/
aws s3 cp backup-weekly-$(date +%Y%m-%U).sql s3://smartcloudops-backups/weekly/
```

#### Configuration Backup
```bash
# Backup Kubernetes configs
kubectl get all -n smartcloudops -o yaml > k8s-backup-$(date +%Y%m%d).yaml

# Backup secrets (encrypted)
kubectl get secrets -n smartcloudops -o yaml > secrets-backup-$(date +%Y%m%d).yaml

# Backup Terraform state
terraform state pull > terraform-state-$(date +%Y%m%d).json
```

## 📈 Performance Optimization

### Application Optimization

#### 1. Database Query Optimization
```bash
# Analyze slow queries
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT query, 
       calls, 
       total_time, 
       mean_time,
       rows,
       shared_blks_hit,
       shared_blks_read
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Create missing indexes
kubectl exec -it postgresql-0 -n smartcloudops -- psql -U postgres -c "
SELECT schemaname, 
       tablename, 
       indexname, 
       idx_scan, 
       idx_tup_read, 
       idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
"
```

#### 2. Application Performance
```bash
# Check application metrics
curl http://backend:5000/metrics | grep -E "(duration|latency|throughput)"

# Profile application
kubectl exec -it backend-pod -n smartcloudops -- python -c "
import cProfile
import pstats
from app.main import app

profiler = cProfile.Profile()
profiler.enable()
# Run application code
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
"
```

### Infrastructure Optimization

#### 1. Resource Optimization
```bash
# Check resource usage
kubectl top pods -n smartcloudops

# Check resource requests/limits
kubectl describe pod backend-pod -n smartcloudops | grep -A 10 "Limits:"

# Optimize resource allocation
kubectl patch deployment backend -n smartcloudops -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "backend",
          "resources": {
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            },
            "limits": {
              "cpu": "500m",
              "memory": "512Mi"
            }
          }
        }]
      }
    }
  }
}'
```

#### 2. Scaling Optimization
```bash
# Check HPA status
kubectl get hpa -n smartcloudops

# Check scaling events
kubectl describe hpa backend-hpa -n smartcloudops

# Optimize HPA settings
kubectl patch hpa backend-hpa -n smartcloudops -p '
{
  "spec": {
    "minReplicas": 3,
    "maxReplicas": 10,
    "targetCPUUtilizationPercentage": 70,
    "targetMemoryUtilizationPercentage": 80
  }
}'
```

## 🚀 Recovery Procedures

### Full System Recovery

#### 1. Complete System Restore
```bash
# Stop all services
kubectl scale deployment --all -n smartcloudops --replicas=0

# Restore database
kubectl exec -i postgresql-0 -n smartcloudops -- psql -U postgres smartcloudops < backup-latest.sql

# Restore configuration
kubectl apply -f k8s-backup-latest.yaml

# Restart services
kubectl scale deployment backend -n smartcloudops --replicas=3
kubectl scale deployment frontend -n smartcloudops --replicas=2

# Verify recovery
curl -f http://backend:5000/health
curl -f http://frontend:3000/health
```

#### 2. Disaster Recovery Test
```bash
# Create test environment
kubectl create namespace smartcloudops-dr-test

# Deploy test application
kubectl apply -f k8s-backup-latest.yaml -n smartcloudops-dr-test

# Test functionality
curl -f http://backend-dr-test:5000/health

# Cleanup test environment
kubectl delete namespace smartcloudops-dr-test
```

## 📋 Post-Incident Procedures

### Incident Documentation

#### 1. Incident Report Template
```markdown
# Incident Report: {Incident ID}

## Incident Summary
- **Date**: {Date}
- **Time**: {Start Time} - {End Time}
- **Severity**: {P0/P1/P2/P3}
- **Affected Services**: {List of services}

## Timeline
- {Time}: Incident detected
- {Time}: Initial response
- {Time}: Root cause identified
- {Time}: Resolution implemented
- {Time}: Service restored

## Root Cause Analysis
{Detailed analysis of what caused the incident}

## Impact Assessment
- **Users Affected**: {Number}
- **Downtime**: {Duration}
- **Data Loss**: {Yes/No}
- **Financial Impact**: {Estimate}

## Resolution Steps
{Step-by-step resolution process}

## Lessons Learned
{What went well, what could be improved}

## Action Items
- [ ] {Action item 1}
- [ ] {Action item 2}
- [ ] {Action item 3}

## Follow-up
- **Review Date**: {Date}
- **Owner**: {Person responsible}
```

#### 2. Post-Incident Review
```bash
# Schedule post-incident review
# Meeting: Post-Incident Review - {Incident ID}
# Attendees: On-call engineer, Senior engineer, Engineering manager

# Prepare metrics
curl http://backend:5000/metrics > incident-metrics-$(date +%Y%m%d).txt

# Document lessons learned
# File: docs/incidents/{YYYY-MM-DD}-{incident-id}.md
```

### Continuous Improvement

#### 1. Process Improvement
- Review incident response procedures
- Update runbooks based on lessons learned
- Improve monitoring and alerting
- Enhance automation and tooling

#### 2. Training and Knowledge Sharing
- Conduct incident response training
- Share lessons learned with team
- Update documentation
- Practice disaster recovery scenarios

---

**Last Updated**: August 27, 2024  
**Version**: 4.0.0  
**Owner**: DevOps Team  
**Review Schedule**: Monthly
