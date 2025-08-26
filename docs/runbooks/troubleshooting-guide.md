# SmartCloudOps AI - Production Troubleshooting Guide
# Phase 3 Week 7: Production Runbook - Troubleshooting Manual

## Table of Contents
1. [General Troubleshooting Approach](#general-troubleshooting-approach)
2. [Application Issues](#application-issues)
3. [Infrastructure Problems](#infrastructure-problems)
4. [Performance Issues](#performance-issues)
5. [Security Incidents](#security-incidents)
6. [Monitoring and Logging Issues](#monitoring-and-logging-issues)
7. [Database Problems](#database-problems)
8. [Network and Connectivity](#network-and-connectivity)

## General Troubleshooting Approach

### 1. Incident Assessment Framework

#### Severity Levels
- **P0 (Critical)**: Complete service outage, data loss, security breach
- **P1 (High)**: Major functionality impaired, significant user impact
- **P2 (Medium)**: Minor functionality affected, limited user impact
- **P3 (Low)**: Cosmetic issues, no user impact

#### Initial Response Checklist ✅
1. [ ] Assess severity and impact scope
2. [ ] Check monitoring dashboards for alerts
3. [ ] Review recent deployments or changes
4. [ ] Gather initial diagnostics
5. [ ] Escalate if needed based on severity
6. [ ] Document findings and actions taken

### 2. Diagnostic Commands Quick Reference

```bash
# Kubernetes cluster health
kubectl get nodes
kubectl get pods --all-namespaces
kubectl top nodes
kubectl top pods --all-namespaces

# Application status
kubectl get deployments -n smartcloudops
kubectl get services -n smartcloudops
kubectl get ingress -n smartcloudops

# Recent events
kubectl get events --sort-by=.metadata.creationTimestamp -n smartcloudops

# Resource usage
kubectl describe node <node-name>
kubectl describe pod <pod-name> -n smartcloudops
```

## Application Issues

### Issue: API Service Unavailable (500/503 Errors)

#### Symptoms
- HTTP 500/503 errors on API endpoints
- Health check failures
- Load balancer marking targets as unhealthy

#### Diagnostic Steps
```bash
# Check pod status
kubectl get pods -n smartcloudops -l app.kubernetes.io/name=smartcloudops-ai

# View application logs
kubectl logs -f deployment/smartcloudops-api -n smartcloudops --tail=100

# Check recent events
kubectl describe pod <failing-pod> -n smartcloudops

# Test database connectivity
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
try:
    db = next(get_db())
    print('Database connection: OK')
except Exception as e:
    print(f'Database error: {e}')
"
```

#### Resolution Steps
1. **Check Resource Limits**
   ```bash
   kubectl describe pod <pod-name> -n smartcloudops | grep -E "(Limits|Requests|Events)"
   ```

2. **Restart Problematic Pods**
   ```bash
   kubectl delete pod <pod-name> -n smartcloudops
   kubectl rollout restart deployment/smartcloudops-api -n smartcloudops
   ```

3. **Scale Up if Resource Constrained**
   ```bash
   kubectl scale deployment smartcloudops-api --replicas=5 -n smartcloudops
   ```

4. **Check Configuration**
   ```bash
   kubectl get configmap smartcloudops-config -n smartcloudops -o yaml
   kubectl get secret smartcloudops-secrets -n smartcloudops -o yaml
   ```

### Issue: High Response Times / Performance Degradation

#### Symptoms
- API response times > 2 seconds
- Timeout errors from frontend
- High CPU/memory usage on pods

#### Diagnostic Steps
```bash
# Check performance metrics
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(flask_request_duration_seconds_bucket[5m]))"

# Application profiling
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
import cProfile
import pstats
# Profile a sample request
"

# Database query analysis
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
from sqlalchemy import text
with get_db() as db:
    result = db.execute(text(\"SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10\"))
    for row in result:
        print(f'Query: {row[0][:100]}... Time: {row[1]}ms Calls: {row[2]}')
"
```

#### Resolution Steps
1. **Enable Caching**
   ```bash
   kubectl patch configmap smartcloudops-config -n smartcloudops -p '{"data":{"CACHE_ENABLED":"true"}}'
   kubectl rollout restart deployment/smartcloudops-api -n smartcloudops
   ```

2. **Scale Horizontally**
   ```bash
   kubectl scale deployment smartcloudops-api --replicas=10 -n smartcloudops
   ```

3. **Optimize Database Queries**
   ```sql
   -- Run on RDS instance
   ANALYZE;
   REINDEX DATABASE smartcloudops;
   ```

4. **Enable Performance Monitoring**
   ```bash
   kubectl patch deployment smartcloudops-api -n smartcloudops -p '
   spec:
     template:
       metadata:
         annotations:
           prometheus.io/scrape: "true"
           prometheus.io/port: "5000"
           prometheus.io/path: "/api/metrics"
   '
   ```

### Issue: Memory Leaks / OOMKilled Events

#### Symptoms
- Pods getting OOMKilled frequently
- Memory usage continuously increasing
- Pod restarts with exit code 137

#### Diagnostic Steps
```bash
# Check memory usage trends
kubectl top pods -n smartcloudops --sort-by=memory

# Memory profiling
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
import psutil
import gc
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Memory percent: {process.memory_percent():.2f}%')
gc.collect()
print(f'Garbage collected objects: {gc.get_count()}')
"

# Check for memory leaks in logs
kubectl logs deployment/smartcloudops-api -n smartcloudops | grep -i "memory\|oom\|leak"
```

#### Resolution Steps
1. **Increase Memory Limits**
   ```bash
   kubectl patch deployment smartcloudops-api -n smartcloudops -p '
   spec:
     template:
       spec:
         containers:
         - name: smartcloudops-api
           resources:
             limits:
               memory: "4Gi"
             requests:
               memory: "2Gi"
   '
   ```

2. **Enable Memory Optimization**
   ```bash
   kubectl patch configmap smartcloudops-config -n smartcloudops -p '{"data":{"MEMORY_MONITORING":"true","GARBAGE_COLLECTION":"aggressive"}}'
   ```

3. **Implement Circuit Breakers**
   ```python
   # Add to application code
   from app.performance.circuit_breaker import CircuitBreaker
   
   @CircuitBreaker(failure_threshold=5, recovery_timeout=30)
   def memory_intensive_operation():
       # Implementation with memory monitoring
       pass
   ```

## Infrastructure Problems

### Issue: EKS Cluster Node Issues

#### Symptoms
- Nodes in NotReady state
- Pods stuck in Pending state
- Node resource exhaustion

#### Diagnostic Steps
```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Check node capacity
kubectl describe node <node-name> | grep -A 5 "Allocated resources"

# AWS instance health
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[].Instances[].State'

# Node logs
kubectl logs -n kube-system -l name=aws-node
```

#### Resolution Steps
1. **Drain and Replace Unhealthy Nodes**
   ```bash
   kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
   kubectl delete node <node-name>
   
   # Auto Scaling Group will replace the node automatically
   ```

2. **Scale Node Groups**
   ```bash
   aws eks update-nodegroup-config \
     --cluster-name smartcloudops-production-cluster \
     --nodegroup-name general \
     --scaling-config minSize=3,maxSize=15,desiredSize=6
   ```

3. **Check for Resource Limits**
   ```bash
   kubectl get limitrange --all-namespaces
   kubectl get resourcequota --all-namespaces
   ```

### Issue: Load Balancer Health Check Failures

#### Symptoms
- ALB targets showing unhealthy
- Intermittent 502/503 errors
- Traffic not routing to pods

#### Diagnostic Steps
```bash
# Check ALB target groups
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# Check ingress configuration
kubectl describe ingress smartcloudops-ingress -n smartcloudops

# Test health endpoint directly
kubectl port-forward deployment/smartcloudops-api 8080:5000 -n smartcloudops
curl http://localhost:8080/api/health
```

#### Resolution Steps
1. **Fix Health Check Configuration**
   ```bash
   kubectl patch ingress smartcloudops-ingress -n smartcloudops -p '
   metadata:
     annotations:
       alb.ingress.kubernetes.io/healthcheck-path: /api/health
       alb.ingress.kubernetes.io/healthcheck-interval-seconds: "30"
       alb.ingress.kubernetes.io/healthcheck-timeout-seconds: "5"
   '
   ```

2. **Update Service Configuration**
   ```bash
   kubectl patch service smartcloudops-api -n smartcloudops -p '
   spec:
     ports:
     - name: http
       port: 80
       targetPort: 5000
       protocol: TCP
   '
   ```

## Performance Issues

### Issue: Database Performance Degradation

#### Symptoms
- Slow database queries
- High database CPU utilization
- Connection pool exhaustion

#### Diagnostic Steps
```bash
# RDS performance insights
aws rds describe-db-instances --db-instance-identifier smartcloudops-prod

# Connection analysis
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import engine
pool = engine.pool
print(f'Pool size: {pool.size()}')
print(f'Checked out: {pool.checkedout()}')
print(f'Overflow: {pool.overflow()}')
print(f'Invalid: {pool.invalid()}')
"

# Query performance
psql -h $DB_HOST -U smartcloudops_admin -d smartcloudops -c "
SELECT query, mean_exec_time, calls, total_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
"
```

#### Resolution Steps
1. **Optimize Connection Pool**
   ```bash
   kubectl patch configmap smartcloudops-config -n smartcloudops -p '
   data:
     DATABASE_POOL_SIZE: "20"
     DATABASE_MAX_OVERFLOW: "30"
     DATABASE_POOL_TIMEOUT: "30"
     DATABASE_POOL_RECYCLE: "3600"
   '
   ```

2. **Database Maintenance**
   ```sql
   -- Run during maintenance window
   VACUUM ANALYZE;
   REINDEX DATABASE smartcloudops;
   UPDATE pg_stat_statements_reset();
   ```

3. **Scale Database Instance**
   ```bash
   aws rds modify-db-instance \
     --db-instance-identifier smartcloudops-prod \
     --db-instance-class db.r5.2xlarge \
     --apply-immediately
   ```

### Issue: Redis Cache Performance

#### Symptoms
- High cache miss rates
- Redis memory usage at 100%
- Slow cache responses

#### Diagnostic Steps
```bash
# Redis metrics
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
import redis
r = redis.Redis(host='smartcloudops-redis', port=6379, decode_responses=True)
info = r.info()
print(f'Used memory: {info[\"used_memory_human\"]}')
print(f'Hit rate: {info[\"keyspace_hits\"] / (info[\"keyspace_hits\"] + info[\"keyspace_misses\"]):.2%}')
print(f'Connected clients: {info[\"connected_clients\"]}')
"

# ElastiCache metrics
aws elasticache describe-cache-clusters --cache-cluster-id smartcloudops-redis
```

#### Resolution Steps
1. **Increase Cache Memory**
   ```bash
   aws elasticache modify-cache-cluster \
     --cache-cluster-id smartcloudops-redis \
     --cache-node-type cache.r6g.large \
     --apply-immediately
   ```

2. **Optimize Cache Strategy**
   ```bash
   kubectl patch configmap smartcloudops-config -n smartcloudops -p '
   data:
     CACHE_DEFAULT_TTL: "7200"
     CACHE_MAX_SIZE: "50000"
     CACHE_EVICTION_POLICY: "allkeys-lru"
   '
   ```

## Security Incidents

### Issue: Suspicious Authentication Activity

#### Symptoms
- High number of failed login attempts
- Unusual access patterns
- Security alerts from monitoring

#### Diagnostic Steps
```bash
# Check authentication logs
kubectl logs deployment/smartcloudops-api -n smartcloudops | grep -i "auth\|login\|fail"

# Failed authentication metrics
curl -s "http://prometheus:9090/api/v1/query?query=rate(authentication_failures_total[5m])"

# Security audit logs
kubectl logs -l app.kubernetes.io/name=smartcloudops-ai -n smartcloudops | grep -E "(SECURITY|AUDIT|BREACH)"
```

#### Response Steps
1. **Immediate Actions**
   ```bash
   # Block suspicious IPs
   kubectl patch networkpolicy smartcloudops-network-policy -n smartcloudops -p '
   spec:
     ingress:
     - from: []
       except:
       - ipBlock:
           cidr: <suspicious-ip>/32
   '
   
   # Force password reset for affected users
   kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
   from app.security.rbac.auth_system import AuthSystem
   auth = AuthSystem()
   auth.force_password_reset('suspicious-user@domain.com')
   "
   ```

2. **Investigation**
   ```bash
   # Export security logs
   kubectl logs -l app.kubernetes.io/name=smartcloudops-ai -n smartcloudops --since=24h > security-incident-$(date +%Y%m%d).log
   
   # Generate security report
   python security/audit/security_scanner.py --generate-report --output security-incident-report.json
   ```

3. **Incident Response**
   ```bash
   # Notify security team
   curl -X POST https://hooks.slack.com/security-alerts \
     -H 'Content-Type: application/json' \
     -d '{"text": "Security incident detected: Suspicious authentication activity"}'
   
   # Create incident ticket
   python scripts/create_incident.py --severity high --type security --description "Suspicious auth activity"
   ```

### Issue: Certificate Expiration

#### Symptoms
- SSL/TLS certificate warnings
- HTTPS connection failures
- Browser security warnings

#### Resolution Steps
```bash
# Check certificate expiration
openssl s_client -connect api.smartcloudops.ai:443 -servername api.smartcloudops.ai 2>/dev/null | openssl x509 -noout -dates

# Update certificate
kubectl create secret tls smartcloudops-tls \
  --cert=new-certificate.crt \
  --key=private-key.key \
  -n smartcloudops --dry-run=client -o yaml | kubectl apply -f -

# Restart ingress controller
kubectl rollout restart deployment/aws-load-balancer-controller -n kube-system

# Verify certificate update
curl -vI https://api.smartcloudops.ai 2>&1 | grep -E "(expire|subject|issuer)"
```

## Monitoring and Logging Issues

### Issue: Prometheus Not Collecting Metrics

#### Symptoms
- Missing metrics in Grafana dashboards
- Prometheus targets showing as down
- Alert rules not firing

#### Diagnostic Steps
```bash
# Check Prometheus status
kubectl get pods -n smartcloudops-monitoring -l app.kubernetes.io/name=prometheus

# Check Prometheus configuration
kubectl logs deployment/prometheus -n smartcloudops-monitoring

# Verify service discovery
curl -s http://prometheus:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# Check metric endpoints
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- curl http://localhost:5000/api/metrics
```

#### Resolution Steps
1. **Fix Service Discovery**
   ```bash
   kubectl apply -f monitoring/prometheus/prometheus-config.yaml
   kubectl rollout restart deployment/prometheus -n smartcloudops-monitoring
   ```

2. **Update RBAC Permissions**
   ```bash
   kubectl apply -f monitoring/prometheus/prometheus-deployment.yaml
   ```

3. **Restart Monitoring Stack**
   ```bash
   kubectl delete pod -l app.kubernetes.io/name=prometheus -n smartcloudops-monitoring
   kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n smartcloudops-monitoring --timeout=300s
   ```

### Issue: Log Ingestion Problems

#### Symptoms
- Missing logs in Elasticsearch
- Fluentd pods in error state
- Log parsing failures

#### Diagnostic Steps
```bash
# Check Fluentd status
kubectl get pods -n smartcloudops-monitoring -l app.kubernetes.io/name=fluentd

# Fluentd logs
kubectl logs daemonset/fluentd -n smartcloudops-monitoring --tail=100

# Elasticsearch cluster health
curl -s "https://elasticsearch:9200/_cluster/health" | jq '.'

# Check log indices
curl -s "https://elasticsearch:9200/_cat/indices/smartcloudops-logs-*?v"
```

#### Resolution Steps
1. **Fix Fluentd Configuration**
   ```bash
   kubectl apply -f monitoring/logging/fluentd-deployment.yaml
   kubectl delete pod -l app.kubernetes.io/name=fluentd -n smartcloudops-monitoring
   ```

2. **Restart Elasticsearch Cluster**
   ```bash
   kubectl rollout restart statefulset/elasticsearch -n smartcloudops-monitoring
   kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=elasticsearch -n smartcloudops-monitoring --timeout=600s
   ```

## Emergency Contact Information

### Escalation Matrix
| Severity | Contact | Response Time |
|----------|---------|---------------|
| P0 | On-Call Engineer + Platform Lead | 15 minutes |
| P1 | Platform Team | 1 hour |
| P2 | Assigned Engineer | 4 hours |
| P3 | Team Backlog | Next business day |

### Contact Details
- **Platform Team**: platform-team@smartcloudops.ai
- **On-Call Hotline**: +1-555-ONCALL (24/7)
- **Security Team**: security-team@smartcloudops.ai
- **DevOps Lead**: devops-lead@smartcloudops.ai
- **Database Team**: database-team@smartcloudops.ai
- **Network Team**: network-team@smartcloudops.ai

### Slack Channels
- **#incident-response**: For active incidents
- **#platform-alerts**: Automated alerts
- **#security-alerts**: Security-related issues
- **#database-alerts**: Database issues
- **#infrastructure**: Infrastructure discussions

---

**Document Version**: 2.0.0  
**Last Updated**: $(date +%Y-%m-%d)  
**Next Review**: $(date -d '+1 month' +%Y-%m-%d)
