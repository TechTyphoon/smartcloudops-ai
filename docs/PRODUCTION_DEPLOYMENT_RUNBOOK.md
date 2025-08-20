# 🚀 **PRODUCTION DEPLOYMENT RUNBOOK - SmartCloudOps.AI**

## 📋 **Pre-Deployment Checklist**

### **Environment Preparation**
- [ ] **Environment Variables**: All required variables set in production environment
- [ ] **Secrets Management**: All secrets stored securely (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] **Database Setup**: PostgreSQL database created and configured
- [ ] **SSL Certificates**: Valid SSL certificates installed
- [ ] **Domain Configuration**: DNS records configured for production domain
- [ ] **Monitoring Setup**: Prometheus, Grafana, and alerting configured
- [ ] **Backup Strategy**: Database and application backups configured
- [ ] **Security Audit**: Latest security scan completed and issues resolved

### **Infrastructure Validation**
- [ ] **Terraform Plan**: Infrastructure changes reviewed and approved
- [ ] **Resource Limits**: CPU, memory, and storage limits configured
- [ ] **Network Security**: Security groups and firewall rules configured
- [ ] **Load Balancer**: Application Load Balancer configured with health checks
- [ ] **Auto Scaling**: Auto scaling groups configured for high availability
- [ ] **Logging**: Centralized logging configured (CloudWatch, ELK Stack)

---

## 🏗️ **DEPLOYMENT STEPS**

### **Phase 1: Infrastructure Deployment**

#### **Step 1: Deploy Infrastructure with Terraform**
```bash
# Navigate to terraform directory
cd terraform/

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="terraform.tfvars"

# Apply infrastructure changes
terraform apply -var-file="terraform.tfvars" -auto-approve

# Verify infrastructure
terraform output
```

#### **Step 2: Configure Secrets**
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name "smartcloudops/production/database" \
    --description "Database credentials for SmartCloudOps production" \
    --secret-string '{"username":"cloudops","password":"secure_password","host":"your-db-host","port":"5432","database":"cloudops"}'

aws secretsmanager create-secret \
    --name "smartcloudops/production/jwt" \
    --description "JWT secret for SmartCloudOps production" \
    --secret-string '{"jwt_secret":"your-super-secure-jwt-secret-32-chars-minimum"}'

aws secretsmanager create-secret \
    --name "smartcloudops/production/api-keys" \
    --description "API keys for SmartCloudOps production" \
    --secret-string '{"openai_api_key":"your-openai-key","gemini_api_key":"your-gemini-key"}'
```

### **Phase 2: Application Deployment**

#### **Step 3: Build and Push Docker Images**
```bash
# Build production Docker image
docker build -f Dockerfile.production -t smartcloudops-ai:latest .

# Tag for registry
docker tag smartcloudops-ai:latest your-registry.com/smartcloudops-ai:latest

# Push to registry
docker push your-registry.com/smartcloudops-ai:latest
```

#### **Step 4: Deploy Application Stack**
```bash
# Deploy with Docker Compose (production)
docker-compose -f docker-compose.production.yml up -d

# Verify deployment
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs -f
```

#### **Step 5: Deploy to Kubernetes (Alternative)**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/00-namespace-and-storage.yaml
kubectl apply -f k8s/01-database.yaml
kubectl apply -f k8s/02-application.yaml
kubectl apply -f k8s/03-nginx.yaml
kubectl apply -f k8s/04-prometheus.yaml
kubectl apply -f k8s/05-grafana.yaml

# Verify deployment
kubectl get pods -n smartcloudops
kubectl get services -n smartcloudops
```

### **Phase 3: Configuration and Validation**

#### **Step 6: Configure Monitoring**
```bash
# Import Grafana dashboards
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @configs/monitoring/dashboards/system-overview.json

# Configure Prometheus targets
# Update configs/monitoring/prometheus.yml with production targets

# Restart monitoring services
docker-compose restart prometheus grafana
```

#### **Step 7: Health Checks and Validation**
```bash
# Run comprehensive health checks
./scripts/morning_check.sh

# Test all API endpoints
curl -X GET http://your-domain.com/health
curl -X GET http://your-domain.com/api/status
curl -X GET http://your-domain.com/metrics

# Verify monitoring
curl -X GET http://your-domain.com:9090/api/v1/targets
curl -X GET http://your-domain.com:3000/api/health
```

---

## 🚨 **ROLLBACK PROCEDURES**

### **Application Rollback**
```bash
# Rollback to previous version
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --force-recreate

# Or rollback specific service
docker-compose -f docker-compose.production.yml up -d --force-recreate app
```

### **Database Rollback**
```bash
# Restore from backup
pg_restore -h your-db-host -U cloudops -d cloudops backup_file.sql

# Or use AWS RDS snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier smartcloudops-production-restored \
    --db-snapshot-identifier your-snapshot-id
```

### **Infrastructure Rollback**
```bash
# Rollback Terraform changes
terraform plan -var-file="terraform.tfvars" -out=rollback.tfplan
terraform apply rollback.tfplan
```

---

## 📊 **POST-DEPLOYMENT VERIFICATION**

### **Performance Validation**
```bash
# Load testing
python scripts/load_testing.py

# Performance monitoring
curl -X GET http://your-domain.com/metrics | grep flask_requests_total

# Response time validation
curl -w "@curl-format.txt" -o /dev/null -s http://your-domain.com/health
```

### **Security Validation**
```bash
# Security scan
python scripts/security_audit.py

# SSL certificate validation
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Vulnerability scan
nmap -sV --script vuln your-domain.com
```

### **Monitoring Validation**
```bash
# Check all monitoring components
curl -X GET http://your-domain.com:9090/api/v1/query?query=up
curl -X GET http://your-domain.com:3000/api/health

# Verify alerting
# Check that alerts are firing correctly
```

---

## 🆘 **EMERGENCY PROCEDURES**

### **Emergency Contacts**
- **DevOps Team**: devops@company.com
- **On-Call Engineer**: +1-555-0123
- **System Administrator**: sysadmin@company.com
- **Security Team**: security@company.com

### **Critical Issues Response**
```bash
# Service down - immediate restart
docker-compose -f docker-compose.production.yml restart

# Database issues - check connectivity
pg_isready -h your-db-host -p 5432

# Memory issues - check resource usage
docker stats

# Network issues - check connectivity
ping your-domain.com
telnet your-domain.com 443
```

### **Data Recovery**
```bash
# Emergency backup
pg_dump -h your-db-host -U cloudops cloudops > emergency_backup.sql

# Restore from backup
psql -h your-db-host -U cloudops -d cloudops < emergency_backup.sql
```

---

## 📈 **MONITORING AND ALERTING**

### **Key Metrics to Monitor**
- **Application Health**: `/health` endpoint response time
- **Database Performance**: Connection pool usage, query response times
- **System Resources**: CPU, memory, disk usage
- **Network Performance**: Response times, error rates
- **Security Events**: Failed login attempts, suspicious activity

### **Alerting Rules**
```yaml
# Example Prometheus alerting rules
groups:
  - name: smartcloudops_alerts
    rules:
      - alert: ApplicationDown
        expr: up{job="smartcloudops-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "SmartCloudOps application is down"
          description: "Application has been down for more than 1 minute"

      - alert: HighErrorRate
        expr: rate(flask_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for the last 5 minutes"
```

---

## 📋 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Documentation updated
- [ ] Backup strategy verified
- [ ] Rollback plan prepared
- [ ] Team notified of deployment

### **During Deployment**
- [ ] Infrastructure deployed successfully
- [ ] Application deployed successfully
- [ ] Database migrations completed
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] Performance validated
- [ ] Security validated

### **Post-Deployment**
- [ ] All services running
- [ ] Monitoring alerts configured
- [ ] Performance baseline established
- [ ] Team notified of successful deployment
- [ ] Documentation updated with deployment notes
- [ ] Lessons learned documented

---

## 🎯 **SUCCESS CRITERIA**

### **Deployment Success Metrics**
- ✅ **Uptime**: 99.9% availability
- ✅ **Response Time**: <50ms average response time
- ✅ **Error Rate**: <1% error rate
- ✅ **Security**: All security scans passing
- ✅ **Performance**: All performance tests passing
- ✅ **Monitoring**: All monitoring components healthy

### **Business Success Metrics**
- ✅ **User Experience**: No user-reported issues
- ✅ **Performance**: Application meets performance SLAs
- ✅ **Reliability**: System handles expected load
- ✅ **Security**: No security incidents
- ✅ **Compliance**: All compliance requirements met

---

*This runbook should be updated after each deployment with lessons learned and improvements.*
