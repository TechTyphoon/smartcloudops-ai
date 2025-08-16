# Smart CloudOps AI - Complete User Manual

**Version**: 1.0  
**Phase**: 7.3.3 - Final Documentation & Handover  
**Generated**: December 19, 2024  

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Daily Operations](#daily-operations)
4. [Feature Guide](#feature-guide)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)
9. [Security](#security)
10. [API Reference](#api-reference)

---

## 🎯 System Overview

### What is Smart CloudOps AI?

Smart CloudOps AI is a comprehensive DevOps automation platform that combines:

- **🤖 AI-Powered Anomaly Detection**: Machine learning models for infrastructure monitoring
- **📊 Advanced Monitoring**: Prometheus + Grafana stack for comprehensive metrics
- **🔧 Automated Operations**: Flask-based API for system management
- **🛡️ Security-First Design**: Built-in security best practices and monitoring
- **📈 Scalable Architecture**: Docker-based deployment for easy scaling

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   Prometheus    │    │     Grafana     │
│  (Port 3003)    │◄──►│  (Port 9090)    │◄──►│  (Port 3001)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │  Node Exporter  │    │      Redis      │
│  (Port 5432)    │    │  (Port 9100)    │    │  (Port 6379)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

#### 🔍 **Anomaly Detection**
- **ML Algorithm**: Isolation Forest with 18 engineered features
- **Performance**: Sub-100ms inference time
- **Accuracy**: >95% for known patterns
- **Real-time Processing**: Live data analysis and alerting

#### 📊 **Monitoring Stack**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Advanced visualization and dashboards
- **Node Exporter**: System metrics collection
- **Custom Metrics**: Application-specific monitoring

#### 🚀 **API Endpoints**
- **Health Checks**: `/health`, `/status`
- **ML Detection**: `/api/ml/detect`
- **Metrics**: `/metrics` (Prometheus format)
- **System Info**: Various information endpoints

---

## 🚀 Quick Start Guide

### Prerequisites

- **Docker & Docker Compose**: Latest versions installed
- **System Requirements**: 4GB RAM, 2 CPU cores minimum
- **Network**: Ports 3003, 3001, 9090 available
- **Storage**: 10GB free disk space

### Installation Steps

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd CloudOps
   python setup.py
   ```

2. **Start the System**
   ```bash
   docker-compose up -d
   ```

3. **Verify Installation**
   ```bash
   ./scripts/morning_check.sh
   ```

4. **Access Interfaces**
   - **Main App**: http://localhost:3003
   - **Grafana**: http://localhost:3001 (admin/admin)
   - **Prometheus**: http://localhost:9090

### First Use Checklist

- [ ] All 5 containers are running and healthy
- [ ] Health endpoint returns "healthy" status
- [ ] ML detection endpoint responds correctly
- [ ] Grafana dashboard loads and shows data
- [ ] Prometheus shows targets as "UP"

---

## 📅 Daily Operations

### Morning Routine (5 minutes)

```bash
# Comprehensive health check
./scripts/morning_check.sh

# Expected output:
# ✅ All containers healthy
# ✅ System status: healthy  
# ✅ ML system initialized
# ✅ Prometheus connectivity confirmed
```

### Health Monitoring

#### System Health Check
```bash
curl http://localhost:3003/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "checks": {
    "ai_handler": true,
    "ml_models": true,
    "remediation_engine": true
  }
}
```

#### Container Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Performance Testing

#### ML Anomaly Detection
```bash
# Test normal data
curl -X POST http://localhost:3003/api/ml/detect \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_usage": 45.0,
    "memory_usage": 60.0,
    "disk_io": 100.5,
    "network_io": 250.0
  }'
```

**Expected Response:**
```json
{
  "is_anomaly": false,
  "confidence": 0.85,
  "response_time_ms": 64.5
}
```

#### Performance Benchmarking
```bash
# Run comprehensive performance test
python3 scripts/beta_testing.py
```

---

## 🎯 Feature Guide

### ML Anomaly Detection

#### Supported Metrics
- **CPU Usage**: Percentage utilization
- **Memory Usage**: Memory consumption percentage
- **Disk I/O**: Read/write operations per second
- **Network I/O**: Network traffic volume
- **Request Rate**: API requests per second
- **Response Time**: Application response latency

#### Detection Examples

**Normal Operation:**
```json
{
  "cpu_usage": 25.5,
  "memory_usage": 35.8,
  "disk_io": 150.2,
  "network_io": 500.0,
  "request_rate": 12.3,
  "response_time": 0.08
}
```

**Anomalous Pattern:**
```json
{
  "cpu_usage": 95.0,
  "memory_usage": 98.0,
  "disk_io": 800.0,
  "network_io": 2000.0,
  "request_rate": 150.0,
  "response_time": 2.5
}
```

### Monitoring Features

#### Grafana Dashboards
1. **System Overview**: General system health and performance
2. **ML Performance**: Machine learning model metrics
3. **Application Metrics**: Flask application specific data
4. **Infrastructure**: Container and system resource usage

#### Prometheus Queries

**CPU Usage Trend:**
```promql
rate(node_cpu_seconds_total{mode="user"}[5m]) * 100
```

**Memory Usage:**
```promql
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
```

**ML Inference Time:**
```promql
histogram_quantile(0.95, rate(ml_inference_duration_seconds_bucket[5m]))
```

---

## 🌐 Production Deployment

### Domain Deployment Guide

#### 1. Domain Configuration
```bash
# Update DNS records
your-domain.com         A    YOUR_SERVER_IP
app.your-domain.com     A    YOUR_SERVER_IP
monitoring.your-domain.com  A    YOUR_SERVER_IP
```

#### 2. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d your-domain.com \
  -d app.your-domain.com \
  -d monitoring.your-domain.com
```

#### 3. Production Deployment
```bash
# Use production configuration
docker-compose -f configs/production/docker-compose.production.yml up -d

# Configure Nginx
sudo cp configs/production/nginx.conf /etc/nginx/sites-available/smartcloudops
sudo ln -s /etc/nginx/sites-available/smartcloudops /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

#### 4. Environment Configuration
```bash
# Copy environment template
cp .env.template .env.production

# Configure production variables
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@postgres:5432/smartcloudops
GRAFANA_ADMIN_PASSWORD=secure-password
```

### Security Configuration

#### Firewall Setup
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### Access Control
```bash
# Create monitoring access file
sudo htpasswd -c /etc/nginx/.htpasswd monitoring_user

# Configure in nginx.conf:
# auth_basic "Monitoring Access";
# auth_basic_user_file /etc/nginx/.htpasswd;
```

---

## 📊 Monitoring & Alerting

### Dashboard Access

#### Grafana Interface
- **URL**: http://localhost:3001 (or https://monitoring.your-domain.com)
- **Default Credentials**: admin/admin
- **Key Dashboards**: System Overview, ML Performance, Application Metrics

#### Prometheus Interface
- **URL**: http://localhost:9090
- **Query Interface**: Custom metric queries and exploration
- **Targets**: Monitor scraping endpoint health

### Alert Configuration

#### System Alerts
- **High CPU**: >80% for 5 minutes
- **High Memory**: >85% for 5 minutes
- **Disk Full**: >90% usage
- **Container Down**: Any container unhealthy

#### Application Alerts
- **High Response Time**: >200ms average for 5 minutes
- **High Error Rate**: >5% errors for 5 minutes
- **ML Model Failure**: Detection endpoint failing

#### Custom Alert Rules
```yaml
# Add to configs/alert-rules.yml
groups:
- name: custom_alerts
  rules:
  - alert: AnomalyDetectionSpike
    expr: rate(ml_anomaly_detections_total[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High anomaly detection rate"
```

---

## 🔧 Troubleshooting

### Common Issues

#### Containers Not Starting
```bash
# Check logs
docker-compose logs

# Common solutions:
1. Check port conflicts: `netstat -tulpn | grep :3003`
2. Verify Docker service: `sudo systemctl status docker`
3. Clear Docker cache: `docker system prune -f`
4. Restart services: `docker-compose down && docker-compose up -d`
```

#### ML Model Not Responding
```bash
# Check ML endpoint
curl -v http://localhost:3003/api/ml/health

# Debug steps:
1. Review application logs: `docker logs smartcloudops-app`
2. Check model files: `ls -la ml_models/`
3. Restart application: `docker-compose restart smartcloudops-app`
4. Verify dependencies: Check requirements.txt packages
```

#### Grafana Dashboard Issues
```bash
# Common solutions:
1. Reset admin password: 
   docker exec -it smartcloudops-grafana grafana-cli admin reset-admin-password admin

2. Check Prometheus connection:
   curl http://localhost:9090/api/v1/query?query=up

3. Reimport dashboards:
   Copy dashboard JSON from configs/grafana/dashboards/
```

#### Performance Issues
```bash
# Resource monitoring
docker stats

# Performance optimization:
1. Increase container memory limits
2. Enable ML model caching
3. Optimize Prometheus retention
4. Clean up old logs: `docker system prune -f`
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart smartcloudops-app

# Check detailed logs
docker logs -f smartcloudops-app
```

---

## 🛠️ Maintenance

### Daily Maintenance (5 minutes)
- [ ] Run health check script
- [ ] Review Grafana dashboards for anomalies
- [ ] Check disk space and resource usage
- [ ] Verify all containers are healthy

### Weekly Maintenance (30 minutes)
- [ ] Run comprehensive system audit
- [ ] Review and clear old logs
- [ ] Update system packages (if needed)
- [ ] Test backup and recovery procedures
- [ ] Review ML model performance trends

### Monthly Maintenance (2 hours)
- [ ] Update Docker images to latest versions
- [ ] Review and update alert rules
- [ ] Perform security audit and updates
- [ ] Optimize database performance
- [ ] Update documentation

### Backup Procedures

#### Database Backup
```bash
# Manual backup
docker exec smartcloudops-postgres pg_dump -U postgres smartcloudops > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i smartcloudops-postgres psql -U postgres smartcloudops < backup_20241219.sql
```

#### Configuration Backup
```bash
# Backup all configurations
tar -czf smartcloudops_config_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  configs/ \
  .env.production \
  ml_models/
```

#### Automated Backup Script
```bash
#!/bin/bash
# Add to crontab: 0 2 * * * /path/to/backup_script.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/smartcloudops"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker exec smartcloudops-postgres pg_dump -U postgres smartcloudops | \
  gzip > $BACKUP_DIR/database_$DATE.sql.gz

# Configuration backup
tar -czf $BACKUP_DIR/config_$DATE.tar.gz docker-compose.yml configs/ .env.production

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

---

## 🛡️ Security

### Security Best Practices

#### Production Security
1. **Use strong passwords** for all services
2. **Enable SSL/TLS** for all external access
3. **Regular security updates** for base images
4. **Network isolation** with Docker networks
5. **Access logging** enabled for all services

#### Environment Security
```bash
# Secure environment file permissions
chmod 600 .env.production

# Use Docker secrets for sensitive data
echo "db_password" | docker secret create db_password -
```

#### Authentication Setup
```nginx
# Basic authentication for monitoring
location /monitoring {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://grafana;
}
```

### Security Monitoring

#### Log Analysis
```bash
# Check authentication logs
docker logs smartcloudops-nginx | grep "auth"

# Monitor failed requests
docker logs smartcloudops-app | grep "ERROR"
```

#### Security Alerts
- **Failed Authentication**: Multiple failed login attempts
- **Unusual Access Patterns**: High request rates from single IP
- **System Integrity**: Unauthorized configuration changes

---

## 📖 API Reference

### Health Endpoints

#### GET /health
**Description**: Basic health check  
**Response**: System health status  
**Example**:
```bash
curl http://localhost:3003/health
```

#### GET /status
**Description**: Detailed system status  
**Response**: Comprehensive system information  

### ML Endpoints

#### POST /api/ml/detect
**Description**: Anomaly detection  
**Content-Type**: application/json  
**Body**:
```json
{
  "cpu_usage": 45.0,
  "memory_usage": 60.0,
  "disk_io": 100.5,
  "network_io": 250.0,
  "request_rate": 12.3,
  "response_time": 0.08
}
```

**Response**:
```json
{
  "is_anomaly": false,
  "confidence": 0.85,
  "severity_score": 0.23,
  "response_time_ms": 64.5,
  "model_version": "1.0"
}
```

#### GET /api/ml/health
**Description**: ML system health check  
**Response**: Model status and performance metrics  

### Metrics Endpoints

#### GET /metrics
**Description**: Prometheus metrics  
**Format**: Prometheus exposition format  
**Use**: Metrics collection by Prometheus  

---

## 🎯 Success Metrics

### Performance Targets
- **API Response Time**: < 100ms average
- **ML Inference Time**: < 150ms
- **System Uptime**: > 99.9%
- **Error Rate**: < 1%

### Operational Metrics
- **Daily Health Checks**: 100% completion
- **Monitoring Coverage**: All critical metrics tracked
- **Alert Response**: < 5 minutes to acknowledgment
- **Backup Success**: 100% successful backups

### User Satisfaction
- **Ease of Use**: Daily operations < 5 minutes
- **Reliability**: Consistent performance
- **Documentation**: Complete and up-to-date
- **Support**: Clear troubleshooting guidance

---

## 📞 Support & Resources

### Documentation
- **Architecture Guide**: `docs/architecture.md`
- **Deployment Guide**: `docs/deployment-guide.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **API Documentation**: `docs/api-reference.md`

### Scripts & Tools
- **Health Check**: `scripts/morning_check.sh`
- **Beta Testing**: `scripts/beta_testing.py`
- **Feedback Collection**: `scripts/collect_feedback.py`
- **System Audit**: `scripts/comprehensive_audit.py`

### Community
- **Repository**: GitHub repository with issues and discussions
- **Documentation**: Comprehensive guides and tutorials
- **Updates**: Regular feature updates and improvements

---

**Smart CloudOps AI v1.0** - Your complete DevOps automation platform is ready for production use!

*Last Updated: December 19, 2024*
