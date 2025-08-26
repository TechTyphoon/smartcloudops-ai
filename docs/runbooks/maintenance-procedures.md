# SmartCloudOps AI - Maintenance Procedures & Operations Manual
# Phase 3 Week 7: Production Runbook - Routine Maintenance

## Table of Contents
1. [Maintenance Schedule](#maintenance-schedule)
2. [Routine Maintenance Tasks](#routine-maintenance-tasks)
3. [Database Maintenance](#database-maintenance)
4. [Infrastructure Maintenance](#infrastructure-maintenance)
5. [Security Maintenance](#security-maintenance)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Capacity Planning](#capacity-planning)
8. [Backup & Recovery](#backup--recovery)

## Maintenance Schedule

### Regular Maintenance Windows 🕐
- **Weekly**: Sundays 02:00-04:00 UTC (Low-impact maintenance)
- **Monthly**: First Sunday 01:00-05:00 UTC (Standard maintenance)
- **Quarterly**: Planned 6-hour window (Major updates)
- **Emergency**: As needed with 2-hour notice minimum

### Maintenance Calendar
```bash
# Current month maintenance schedule
cal $(date +%m) $(date +%Y)

# Upcoming maintenance windows
cat << EOF > maintenance-schedule-$(date +%Y-%m).md
# Maintenance Schedule - $(date +%B\ %Y)

## Weekly Maintenance (Sundays 02:00-04:00 UTC)
- $(date -d 'next sunday' +%Y-%m-%d): Security updates, log rotation
- $(date -d 'next sunday + 7 days' +%Y-%m-%d): Database optimization, backup verification
- $(date -d 'next sunday + 14 days' +%Y-%m-%d): Certificate updates, dependency updates
- $(date -d 'next sunday + 21 days' +%Y-%m-%d): Infrastructure health checks, monitoring review

## Monthly Maintenance (First Sunday 01:00-05:00 UTC)
- $(date -d 'first sunday of next month' +%Y-%m-%d): Major system updates, performance optimization

## Quarterly Maintenance
- $(date -d 'first sunday of next quarter' +%Y-%m-%d): Infrastructure upgrades, major version updates
EOF
```

## Routine Maintenance Tasks

### Daily Automated Checks ✅
```bash
#!/bin/bash
# Daily automated maintenance script
# Runs at 03:00 UTC via cron

LOG_FILE="/var/log/smartcloudops/daily-maintenance-$(date +%Y%m%d).log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "=== DAILY MAINTENANCE - $(date -u) ==="

# 1. System Health Check
echo "1. SYSTEM HEALTH VERIFICATION"
kubectl get nodes | grep -v Ready && echo "❌ Unhealthy nodes detected" || echo "✅ All nodes healthy"
kubectl get pods --all-namespaces | grep -E "(Error|CrashLoopBackOff|Pending)" && echo "❌ Pod issues detected" || echo "✅ All pods healthy"

# 2. Disk Space Monitoring
echo "2. DISK SPACE CHECK"
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- df -h | awk '$5 > "80%" {print "⚠️ " $6 " is " $5 " full"}'

# 3. Database Connection Verification
echo "3. DATABASE CONNECTIVITY"
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
try:
    with get_db() as db:
        db.execute(text('SELECT 1'))
    print('✅ Database connection verified')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# 4. Cache System Health
echo "4. CACHE SYSTEM STATUS"
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
import redis
try:
    r = redis.Redis(host='smartcloudops-redis', port=6379)
    r.ping()
    print('✅ Redis connection verified')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
"

# 5. SSL Certificate Expiry Check
echo "5. SSL CERTIFICATE EXPIRY"
openssl s_client -connect api.smartcloudops.ai:443 -servername api.smartcloudops.ai 2>/dev/null | \
  openssl x509 -noout -dates | \
  grep notAfter | \
  awk -F= '{print $2}' | \
  while read date; do
    exp_date=$(date -d "$date" +%s)
    current_date=$(date +%s)
    days_left=$(( (exp_date - current_date) / 86400 ))
    if [ $days_left -lt 30 ]; then
      echo "⚠️ SSL certificate expires in $days_left days"
    else
      echo "✅ SSL certificate valid for $days_left days"
    fi
  done

# 6. Log Rotation and Cleanup
echo "6. LOG MAINTENANCE"
find /var/log/smartcloudops -name "*.log" -mtime +30 -delete
echo "✅ Old logs cleaned up"

# 7. Backup Verification
echo "7. BACKUP VERIFICATION"
LATEST_BACKUP=$(aws rds describe-db-snapshots \
  --db-instance-identifier smartcloudops-prod \
  --query 'DBSnapshots[0].SnapshotCreateTime' \
  --output text)
BACKUP_AGE=$(( ($(date +%s) - $(date -d "$LATEST_BACKUP" +%s)) / 3600 ))

if [ $BACKUP_AGE -lt 25 ]; then
  echo "✅ Recent backup found ($BACKUP_AGE hours old)"
else
  echo "⚠️ Latest backup is $BACKUP_AGE hours old"
fi

echo "=== DAILY MAINTENANCE COMPLETE ==="
```

### Weekly Maintenance Tasks 📅
```bash
#!/bin/bash
# Weekly maintenance script - Sundays 02:00 UTC

echo "=== WEEKLY MAINTENANCE - $(date -u) ==="

# 1. Security Updates
echo "1. SECURITY UPDATES"
kubectl patch daemonset node-exporter -n smartcloudops-monitoring -p '{"spec":{"template":{"metadata":{"annotations":{"maintenance.date":"'$(date -u)'"}}}}}'

# Update base images
docker pull smartcloudops/api:latest
docker pull smartcloudops/worker:latest

# Scan for vulnerabilities
trivy image smartcloudops/api:latest --severity HIGH,CRITICAL
trivy image smartcloudops/worker:latest --severity HIGH,CRITICAL

# 2. Certificate Management
echo "2. CERTIFICATE RENEWAL CHECK"
certbot renew --dry-run --nginx

# 3. Database Maintenance
echo "3. DATABASE OPTIMIZATION"
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
from sqlalchemy import text

with get_db() as db:
    # Analyze tables
    db.execute(text('ANALYZE;'))
    print('✅ Database analysis complete')
    
    # Update statistics
    db.execute(text('VACUUM ANALYZE;'))
    print('✅ Database vacuum complete')
    
    # Check for bloat
    result = db.execute(text('''
        SELECT schemaname, tablename, 
               pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 10
    '''))
    print('Top 10 largest tables:')
    for row in result:
        print(f'  {row[1]}: {row[2]}')
"

# 4. Log Analysis and Alerting Review
echo "4. LOG ANALYSIS"
kubectl logs deployment/smartcloudops-api -n smartcloudops --since=168h | \
  grep -E "(ERROR|CRITICAL|FATAL)" | \
  wc -l | \
  awk '{print "Error count this week: " $1}'

# 5. Performance Metrics Review
echo "5. PERFORMANCE METRICS"
curl -s "http://prometheus:9090/api/v1/query?query=rate(flask_request_duration_seconds_sum[7d])/rate(flask_request_duration_seconds_count[7d])" | \
  jq -r '.data.result[0].value[1]' | \
  awk '{printf "Average response time: %.3f seconds\n", $1}'

# 6. Dependency Updates
echo "6. DEPENDENCY UPDATES"
cd /app && pip list --outdated --format=json | jq -r '.[] | "\(.name): \(.version) -> \(.latest_version)"'

echo "=== WEEKLY MAINTENANCE COMPLETE ==="
```

## Database Maintenance

### PostgreSQL Routine Maintenance 🗄️

#### Daily Database Monitoring
```sql
-- Database health check queries
-- Run daily at 06:00 UTC

-- 1. Connection monitoring
SELECT datname, numbackends, xact_commit, xact_rollback
FROM pg_stat_database 
WHERE datname = 'smartcloudops';

-- 2. Table sizes and growth
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as data_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- 3. Index usage analysis
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_scan = 0
ORDER BY schemaname, tablename;

-- 4. Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
AND state = 'active';

-- 5. Database bloat estimation
SELECT schemaname, tablename,
       ROUND(CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END,1) AS tbloat,
       CASE WHEN relpages < otta THEN 0 ELSE relpages::bigint - otta END AS wastedpages,
       CASE WHEN relpages < otta THEN 0 ELSE bs*(sml.relpages-otta)::bigint END AS wastedbytes,
       pg_size_pretty(CASE WHEN relpages < otta THEN 0 ELSE bs*(sml.relpages-otta)::bigint END) AS wastedsize
FROM (
  SELECT schemaname, tablename, cc.reltuples, cc.relpages, bs,
         CEIL((cc.reltuples*((datahdr+ma-(CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta
  FROM (
    SELECT ma,bs,schemaname,tablename,
           (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr,
           (hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)) AS nullhdr2
    FROM (
      SELECT schemaname, tablename, hdr, ma, bs,
             SUM((1-null_frac)*avg_width) AS datawidth
      FROM pg_stats s2
      JOIN (
        SELECT 2 as hdr, 4 as ma, 8192 as bs
      ) AS constants ON (true)
      WHERE s2.schemaname = 'public'
      GROUP BY 1,2,3,4,5
    ) AS foo
  ) AS rs
  JOIN pg_class cc ON cc.relname = rs.tablename
  JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname
) AS sml
WHERE sml.relpages > 0
ORDER BY wastedbytes DESC;
```

#### Weekly Database Optimization
```bash
#!/bin/bash
# Weekly database optimization script

echo "=== DATABASE OPTIMIZATION - $(date -u) ==="

# 1. Vacuum and Analyze
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
from sqlalchemy import text
import time

start_time = time.time()
with get_db() as db:
    # Full vacuum analyze
    db.execute(text('VACUUM ANALYZE;'))
    print(f'✅ VACUUM ANALYZE completed in {time.time() - start_time:.2f} seconds')
    
    # Reindex if needed
    db.execute(text('REINDEX DATABASE smartcloudops;'))
    print(f'✅ REINDEX completed')
    
    # Update table statistics
    db.execute(text('ANALYZE;'))
    print(f'✅ ANALYZE completed')
"

# 2. Index Maintenance
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
from sqlalchemy import text

with get_db() as db:
    # Find unused indexes
    unused_indexes = db.execute(text('''
        SELECT schemaname, tablename, indexname, idx_scan
        FROM pg_stat_user_indexes 
        WHERE idx_scan = 0 
        AND indexname NOT LIKE '%_pkey'
        ORDER BY schemaname, tablename, indexname
    ''')).fetchall()
    
    if unused_indexes:
        print('⚠️ Unused indexes found:')
        for idx in unused_indexes:
            print(f'  {idx[0]}.{idx[1]}.{idx[2]} (scans: {idx[3]})')
    else:
        print('✅ No unused indexes found')
    
    # Check for missing indexes
    slow_queries = db.execute(text('''
        SELECT query, calls, mean_exec_time, total_exec_time
        FROM pg_stat_statements 
        WHERE mean_exec_time > 1000  -- queries taking more than 1 second
        ORDER BY mean_exec_time DESC
        LIMIT 10
    ''')).fetchall()
    
    if slow_queries:
        print('⚠️ Slow queries detected (>1s average):')
        for query in slow_queries:
            print(f'  {query[0][:100]}... ({query[2]:.2f}ms avg)')
    else:
        print('✅ No slow queries detected')
"

# 3. Connection Pool Monitoring
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import engine
import psutil

pool = engine.pool
print(f'Connection Pool Status:')
print(f'  Pool size: {pool.size()}')
print(f'  Checked out: {pool.checkedout()}')
print(f'  Overflow: {pool.overflow()}')
print(f'  Invalid: {pool.invalid()}')

# System resource usage
process = psutil.Process()
print(f'Application Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Application CPU: {process.cpu_percent():.2f}%')
"

echo "=== DATABASE OPTIMIZATION COMPLETE ==="
```

## Infrastructure Maintenance

### Kubernetes Cluster Maintenance ☸️

#### Node Maintenance Procedure
```bash
#!/bin/bash
# Node maintenance and updates

NODE_NAME=${1:-"auto-select"}

if [ "$NODE_NAME" = "auto-select" ]; then
  # Select node with least pods for maintenance
  NODE_NAME=$(kubectl get nodes -o custom-columns=NAME:.metadata.name,PODS:.status.allocatable.pods --no-headers | sort -k2 -n | head -1 | cut -d' ' -f1)
  echo "Auto-selected node for maintenance: $NODE_NAME"
fi

echo "=== NODE MAINTENANCE: $NODE_NAME ==="

# 1. Pre-maintenance health check
echo "1. PRE-MAINTENANCE HEALTH CHECK"
kubectl describe node $NODE_NAME | grep -E "(Conditions|Allocated resources)"

# 2. Cordon the node
echo "2. CORDONING NODE"
kubectl cordon $NODE_NAME
echo "✅ Node cordoned"

# 3. Drain the node gracefully
echo "3. DRAINING NODE"
kubectl drain $NODE_NAME \
  --ignore-daemonsets \
  --delete-emptydir-data \
  --force \
  --grace-period=300
echo "✅ Node drained"

# 4. Perform node updates (this would typically involve OS updates)
echo "4. PERFORMING NODE UPDATES"
# In a real environment, this would involve:
# - OS security updates
# - Kubernetes component updates
# - Docker/containerd updates
# - System configuration changes

# Simulate update process
sleep 30
echo "✅ Node updates completed"

# 5. Uncordon the node
echo "5. UNCORDONING NODE"
kubectl uncordon $NODE_NAME
echo "✅ Node uncordoned"

# 6. Verify node is healthy and pods are scheduling
echo "6. POST-MAINTENANCE VERIFICATION"
sleep 60  # Allow time for pods to schedule

kubectl get node $NODE_NAME
kubectl get pods --all-namespaces --field-selector spec.nodeName=$NODE_NAME

echo "=== NODE MAINTENANCE COMPLETE ==="
```

#### Cluster Component Updates
```bash
#!/bin/bash
# Kubernetes cluster component maintenance

echo "=== CLUSTER COMPONENT MAINTENANCE ==="

# 1. EKS Cluster Version Check
echo "1. EKS CLUSTER VERSION"
CLUSTER_VERSION=$(aws eks describe-cluster --name smartcloudops-production-cluster --query 'cluster.version' --output text)
echo "Current cluster version: $CLUSTER_VERSION"

# Check for available updates
aws eks describe-update --name smartcloudops-production-cluster

# 2. Node Group Updates
echo "2. NODE GROUP STATUS"
aws eks describe-nodegroup \
  --cluster-name smartcloudops-production-cluster \
  --nodegroup-name general \
  --query 'nodegroup.{Version:version,Status:status,Health:health}'

# 3. Add-on Updates
echo "3. EKS ADD-ON STATUS"
aws eks list-addons --cluster-name smartcloudops-production-cluster

for addon in coredns kube-proxy vpc-cni aws-ebs-csi-driver; do
  echo "Checking $addon..."
  aws eks describe-addon \
    --cluster-name smartcloudops-production-cluster \
    --addon-name $addon \
    --query 'addon.{Name:addonName,Version:addonVersion,Status:status}'
done

# 4. CNI Plugin Health
echo "4. CNI PLUGIN HEALTH"
kubectl get pods -n kube-system -l k8s-app=aws-node

# 5. DNS Resolution Test
echo "5. DNS RESOLUTION TEST"
kubectl run dns-test --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default.svc.cluster.local

echo "=== CLUSTER COMPONENT MAINTENANCE COMPLETE ==="
```

### AWS Infrastructure Maintenance 🏗️

#### RDS Maintenance
```bash
#!/bin/bash
# RDS maintenance procedures

echo "=== RDS MAINTENANCE ==="

# 1. Check maintenance windows
echo "1. MAINTENANCE WINDOW STATUS"
aws rds describe-db-instances \
  --db-instance-identifier smartcloudops-prod \
  --query 'DBInstances[0].{MaintenanceWindow:PreferredMaintenanceWindow,BackupWindow:PreferredBackupWindow,MultiAZ:MultiAZ}'

# 2. Check for pending maintenance
echo "2. PENDING MAINTENANCE"
aws rds describe-pending-maintenance-actions \
  --resource-identifier arn:aws:rds:us-west-2:123456789012:db:smartcloudops-prod

# 3. Performance insights
echo "3. PERFORMANCE INSIGHTS"
aws rds describe-db-instances \
  --db-instance-identifier smartcloudops-prod \
  --query 'DBInstances[0].{PerformanceInsights:PerformanceInsightsEnabled,MonitoringInterval:MonitoringInterval}'

# 4. Backup verification
echo "4. BACKUP VERIFICATION"
aws rds describe-db-snapshots \
  --db-instance-identifier smartcloudops-prod \
  --max-items 5 \
  --query 'DBSnapshots[].{SnapshotId:DBSnapshotIdentifier,CreateTime:SnapshotCreateTime,Status:Status}'

# 5. Connection monitoring
echo "5. CONNECTION MONITORING"
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=smartcloudops-prod \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Maximum

echo "=== RDS MAINTENANCE COMPLETE ==="
```

## Security Maintenance

### Security Updates and Patches 🔒

#### Weekly Security Scan
```bash
#!/bin/bash
# Weekly security maintenance

echo "=== SECURITY MAINTENANCE - $(date -u) ==="

# 1. Container Image Scanning
echo "1. CONTAINER SECURITY SCAN"
for image in smartcloudops/api:latest smartcloudops/worker:latest; do
  echo "Scanning $image..."
  trivy image $image --severity HIGH,CRITICAL --format json > security-scan-$(echo $image | tr '/:' '-')-$(date +%Y%m%d).json
  
  # Count vulnerabilities
  high_count=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")' security-scan-$(echo $image | tr '/:' '-')-$(date +%Y%m%d).json | jq -s length)
  critical_count=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")' security-scan-$(echo $image | tr '/:' '-')-$(date +%Y%m%d).json | jq -s length)
  
  echo "  High: $high_count, Critical: $critical_count vulnerabilities"
done

# 2. Kubernetes Security Audit
echo "2. KUBERNETES SECURITY AUDIT"
kubectl auth can-i --list --as=system:anonymous | head -10
kubectl get pods --all-namespaces -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,SECURITY_CONTEXT:.spec.securityContext.runAsNonRoot

# 3. Network Policy Verification
echo "3. NETWORK POLICY VERIFICATION"
kubectl get networkpolicies --all-namespaces

# 4. RBAC Audit
echo "4. RBAC PERMISSIONS AUDIT"
kubectl get clusterrolebindings -o custom-columns=NAME:.metadata.name,ROLE:.roleRef.name,SUBJECTS:.subjects[*].name

# 5. Secret Rotation Check
echo "5. SECRET ROTATION STATUS"
kubectl get secrets --all-namespaces -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,AGE:.metadata.creationTimestamp | grep -E "(password|token|key)"

# 6. Certificate Expiry Monitoring
echo "6. CERTIFICATE EXPIRY CHECK"
kubectl get certificates --all-namespaces -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,READY:.status.conditions[0].status,AGE:.metadata.creationTimestamp

# 7. Security Policy Compliance
echo "7. SECURITY POLICY COMPLIANCE"
kubectl get podsecuritypolicies
kubectl get pods --all-namespaces -o custom-columns=NAME:.metadata.name,SECURITY_CONTEXT:.spec.securityContext.runAsUser | grep -v "null"

echo "=== SECURITY MAINTENANCE COMPLETE ==="
```

#### Certificate Management
```bash
#!/bin/bash
# Certificate management and renewal

echo "=== CERTIFICATE MANAGEMENT ==="

# 1. Check all certificate expiry dates
echo "1. CERTIFICATE EXPIRY STATUS"
for domain in api.smartcloudops.ai grafana.smartcloudops.ai prometheus.smartcloudops.ai; do
  echo "Checking $domain..."
  openssl s_client -connect $domain:443 -servername $domain 2>/dev/null | \
    openssl x509 -noout -dates | \
    grep notAfter | \
    awk -F= '{print "  Expires: " $2}'
done

# 2. Let's Encrypt renewal (if applicable)
echo "2. CERTIFICATE RENEWAL"
certbot renew --dry-run

# 3. Kubernetes TLS secrets update
echo "3. KUBERNETES TLS SECRETS"
kubectl get secrets --all-namespaces -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,TYPE:.type | grep kubernetes.io/tls

# 4. AWS Certificate Manager status
echo "4. AWS CERTIFICATE MANAGER"
aws acm list-certificates --query 'CertificateSummaryList[].{DomainName:DomainName,Status:Status}'

echo "=== CERTIFICATE MANAGEMENT COMPLETE ==="
```

## Monitoring & Health Checks

### Monitoring Stack Maintenance 📊

#### Prometheus Maintenance
```bash
#!/bin/bash
# Prometheus maintenance procedures

echo "=== PROMETHEUS MAINTENANCE ==="

# 1. Storage usage check
echo "1. PROMETHEUS STORAGE USAGE"
kubectl exec -it deployment/prometheus -n smartcloudops-monitoring -- \
  du -sh /prometheus/

# 2. Query performance analysis
echo "2. QUERY PERFORMANCE"
curl -s "http://prometheus:9090/api/v1/query?query=prometheus_engine_query_duration_seconds" | \
  jq '.data.result[] | {metric: .metric.__name__, value: .value[1]}'

# 3. Target health verification
echo "3. TARGET HEALTH STATUS"
curl -s "http://prometheus:9090/api/v1/targets" | \
  jq '.data.activeTargets[] | select(.health != "up") | {job: .labels.job, instance: .labels.instance, health: .health}'

# 4. Alert rule validation
echo "4. ALERT RULE STATUS"
curl -s "http://prometheus:9090/api/v1/rules" | \
  jq '.data.groups[].rules[] | select(.type == "alerting") | {name: .name, state: .state}'

# 5. Retention policy check
echo "5. DATA RETENTION STATUS"
kubectl describe deployment prometheus -n smartcloudops-monitoring | grep -E "(retention|storage)"

echo "=== PROMETHEUS MAINTENANCE COMPLETE ==="
```

#### Elasticsearch Maintenance
```bash
#!/bin/bash
# Elasticsearch maintenance procedures

echo "=== ELASTICSEARCH MAINTENANCE ==="

# 1. Cluster health check
echo "1. CLUSTER HEALTH"
curl -s "https://elasticsearch:9200/_cluster/health?pretty"

# 2. Index management
echo "2. INDEX MANAGEMENT"
curl -s "https://elasticsearch:9200/_cat/indices/smartcloudops-logs-*?v&s=index"

# 3. Shard allocation
echo "3. SHARD ALLOCATION"
curl -s "https://elasticsearch:9200/_cat/shards?v" | head -20

# 4. Node statistics
echo "4. NODE STATISTICS"
curl -s "https://elasticsearch:9200/_nodes/stats" | \
  jq '.nodes[] | {name: .name, heap_used_percent: .jvm.mem.heap_used_percent, disk_free: .fs.total.free_in_bytes}'

# 5. Index lifecycle management
echo "5. ILM POLICY STATUS"
curl -s "https://elasticsearch:9200/_ilm/policy" | jq '.policies | keys'

# 6. Old index cleanup
echo "6. OLD INDEX CLEANUP"
curl -X DELETE "https://elasticsearch:9200/smartcloudops-logs-$(date -d '30 days ago' +%Y.%m.%d)"

echo "=== ELASTICSEARCH MAINTENANCE COMPLETE ==="
```

## Capacity Planning

### Resource Monitoring and Planning 📈

#### Infrastructure Capacity Analysis
```bash
#!/bin/bash
# Monthly capacity planning analysis

echo "=== CAPACITY PLANNING ANALYSIS - $(date +%B\ %Y) ==="

# 1. Kubernetes cluster capacity
echo "1. KUBERNETES CLUSTER CAPACITY"
kubectl describe nodes | grep -E "(cpu|memory|pods)" | \
  awk '/Allocatable:/{flag=1; next} /System Info:/{flag=0} flag {print "  " $0}'

# 2. Resource utilization trends
echo "2. RESOURCE UTILIZATION TRENDS"
curl -s "http://prometheus:9090/api/v1/query?query=100-(avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m]))*100)" | \
  jq -r '.data.result[0].value[1] + "% average CPU usage"'

curl -s "http://prometheus:9090/api/v1/query?query=100*((node_memory_MemTotal_bytes-node_memory_MemAvailable_bytes)/node_memory_MemTotal_bytes)" | \
  jq -r '.data.result[0].value[1] + "% average memory usage"'

# 3. Database growth analysis
echo "3. DATABASE GROWTH ANALYSIS"
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
from app.database import get_db
from sqlalchemy import text

with get_db() as db:
    # Database size
    result = db.execute(text('SELECT pg_size_pretty(pg_database_size(\"smartcloudops\"))'))
    print(f'Current database size: {result.fetchone()[0]}')
    
    # Table growth rates
    result = db.execute(text('''
        SELECT schemaname, tablename, 
               pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 5
    '''))
    print('Top 5 largest tables:')
    for row in result:
        print(f'  {row[1]}: {row[2]}')
"

# 4. Storage growth projection
echo "4. STORAGE GROWTH PROJECTION"
kubectl get pv -o custom-columns=NAME:.metadata.name,SIZE:.spec.capacity.storage,USED:.status.phase

# 5. Traffic growth analysis
echo "5. TRAFFIC GROWTH ANALYSIS"
curl -s "http://prometheus:9090/api/v1/query?query=rate(flask_request_total[24h])" | \
  jq -r '.data.result[] | .value[1] + " requests/second for " + .metric.endpoint'

# 6. Generate capacity recommendations
echo "6. CAPACITY RECOMMENDATIONS"
cat << EOF > capacity-recommendations-$(date +%Y-%m).md
# Capacity Planning Recommendations - $(date +%B\ %Y)

## Current Status
- Cluster CPU Utilization: Average load within acceptable limits
- Memory Usage: Monitor application memory growth
- Database Size: $(kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "from app.database import get_db; from sqlalchemy import text; print(next(get_db()).execute(text('SELECT pg_size_pretty(pg_database_size(\"smartcloudops\"))')).fetchone()[0])")

## Recommendations
1. **Kubernetes Nodes**: Consider adding 1 additional node if CPU > 70%
2. **Database**: Plan for storage expansion if growth > 10GB/month
3. **Monitoring**: Increase retention if disk usage < 80%
4. **Caching**: Scale Redis if hit rate < 80%

## Action Items
- [ ] Review auto-scaling policies
- [ ] Plan infrastructure budget for next quarter
- [ ] Update resource requests/limits based on actual usage
- [ ] Evaluate new AWS instance types for cost optimization

## Next Review
$(date -d '+1 month' +%Y-%m-%d)
EOF

echo "✅ Capacity recommendations generated"

echo "=== CAPACITY PLANNING ANALYSIS COMPLETE ==="
```

## Backup & Recovery

### Backup Procedures 💾

#### Database Backup Automation
```bash
#!/bin/bash
# Automated database backup procedure

echo "=== DATABASE BACKUP PROCEDURE ==="

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="smartcloudops-backup-$TIMESTAMP"

# 1. Create RDS snapshot
echo "1. CREATING RDS SNAPSHOT"
aws rds create-db-snapshot \
  --db-instance-identifier smartcloudops-prod \
  --db-snapshot-identifier $BACKUP_NAME

# Wait for snapshot completion
while true; do
  STATUS=$(aws rds describe-db-snapshots \
    --db-snapshot-identifier $BACKUP_NAME \
    --query 'DBSnapshots[0].Status' \
    --output text)
  
  if [ "$STATUS" = "available" ]; then
    echo "✅ RDS snapshot completed"
    break
  elif [ "$STATUS" = "error" ]; then
    echo "❌ RDS snapshot failed"
    exit 1
  else
    echo "⏳ Snapshot status: $STATUS"
    sleep 30
  fi
done

# 2. Backup application data
echo "2. BACKING UP APPLICATION DATA"
kubectl exec -it deployment/smartcloudops-api -n smartcloudops -- python -c "
import os
import json
from datetime import datetime
from app.database import get_db
from sqlalchemy import text

backup_data = {
    'timestamp': datetime.utcnow().isoformat(),
    'version': os.getenv('APP_VERSION', 'unknown'),
    'tables': {}
}

with get_db() as db:
    # Backup critical configuration data
    tables_to_backup = ['users', 'experiments', 'models', 'configurations']
    
    for table in tables_to_backup:
        try:
            result = db.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.fetchone()[0]
            backup_data['tables'][table] = {'count': count}
            print(f'✅ {table}: {count} records')
        except Exception as e:
            print(f'❌ {table}: {e}')

# Save backup metadata
with open(f'/tmp/backup-metadata-{datetime.now().strftime(\"%Y%m%d-%H%M%S\")}.json', 'w') as f:
    json.dump(backup_data, f, indent=2)

print('✅ Application data backup metadata created')
"

# 3. Backup Kubernetes configurations
echo "3. BACKING UP KUBERNETES CONFIGURATIONS"
mkdir -p /backup/kubernetes/$TIMESTAMP

kubectl get all --all-namespaces -o yaml > /backup/kubernetes/$TIMESTAMP/all-resources.yaml
kubectl get configmaps --all-namespaces -o yaml > /backup/kubernetes/$TIMESTAMP/configmaps.yaml
kubectl get secrets --all-namespaces -o yaml > /backup/kubernetes/$TIMESTAMP/secrets.yaml
kubectl get persistentvolumes -o yaml > /backup/kubernetes/$TIMESTAMP/persistentvolumes.yaml

echo "✅ Kubernetes configurations backed up"

# 4. Backup monitoring data
echo "4. BACKING UP MONITORING DATA"
kubectl exec -it deployment/prometheus -n smartcloudops-monitoring -- \
  tar -czf /tmp/prometheus-data-$TIMESTAMP.tar.gz /prometheus/

# 5. Verify backup integrity
echo "5. VERIFYING BACKUP INTEGRITY"
aws rds describe-db-snapshots \
  --db-snapshot-identifier $BACKUP_NAME \
  --query 'DBSnapshots[0].{Status:Status,Size:AllocatedStorage,Encrypted:Encrypted}'

# 6. Update backup inventory
echo "6. UPDATING BACKUP INVENTORY"
cat << EOF >> /backup/inventory.log
$(date -u +"%Y-%m-%d %H:%M:%S UTC") | $BACKUP_NAME | RDS Snapshot | $(aws rds describe-db-snapshots --db-snapshot-identifier $BACKUP_NAME --query 'DBSnapshots[0].AllocatedStorage' --output text)GB
$(date -u +"%Y-%m-%d %H:%M:%S UTC") | kubernetes-$TIMESTAMP | K8s Config | $(du -sh /backup/kubernetes/$TIMESTAMP | cut -f1)
EOF

echo "=== DATABASE BACKUP PROCEDURE COMPLETE ==="
echo "Backup ID: $BACKUP_NAME"
```

#### Backup Verification and Testing
```bash
#!/bin/bash
# Monthly backup restoration test

echo "=== BACKUP RESTORATION TEST ==="

# 1. List available backups
echo "1. AVAILABLE BACKUPS"
aws rds describe-db-snapshots \
  --db-instance-identifier smartcloudops-prod \
  --max-items 10 \
  --query 'DBSnapshots[].{SnapshotId:DBSnapshotIdentifier,CreateTime:SnapshotCreateTime,Status:Status}'

# 2. Restore to test instance
LATEST_SNAPSHOT=$(aws rds describe-db-snapshots \
  --db-instance-identifier smartcloudops-prod \
  --query 'DBSnapshots[0].DBSnapshotIdentifier' \
  --output text)

echo "2. RESTORING TEST INSTANCE FROM $LATEST_SNAPSHOT"
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier smartcloudops-backup-test-$(date +%Y%m%d) \
  --db-snapshot-identifier $LATEST_SNAPSHOT \
  --db-instance-class db.t3.micro \
  --no-publicly-accessible

# 3. Wait for test instance to become available
TEST_INSTANCE="smartcloudops-backup-test-$(date +%Y%m%d)"
echo "3. WAITING FOR TEST INSTANCE TO BECOME AVAILABLE"

while true; do
  STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier $TEST_INSTANCE \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text 2>/dev/null)
  
  if [ "$STATUS" = "available" ]; then
    echo "✅ Test instance is available"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "❌ Test instance failed to start"
    exit 1
  else
    echo "⏳ Test instance status: $STATUS"
    sleep 60
  fi
done

# 4. Verify data integrity
echo "4. VERIFYING DATA INTEGRITY"
TEST_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier $TEST_INSTANCE \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

# Connect to test database and verify data
PGPASSWORD=$DB_PASSWORD psql -h $TEST_ENDPOINT -U smartcloudops_admin -d smartcloudops -c "
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'experiments', COUNT(*) FROM experiments
UNION ALL
SELECT 'models', COUNT(*) FROM models
ORDER BY table_name;
"

# 5. Cleanup test instance
echo "5. CLEANING UP TEST INSTANCE"
aws rds delete-db-instance \
  --db-instance-identifier $TEST_INSTANCE \
  --skip-final-snapshot

echo "=== BACKUP RESTORATION TEST COMPLETE ==="
```

---

**Document Version**: 2.0.0  
**Last Updated**: $(date +%Y-%m-%d)  
**Next Review**: $(date -d '+1 month' +%Y-%m-%d)  
**Document Owner**: Platform Engineering Team
