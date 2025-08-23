# SmartCloudOps AI - Configuration Management

This directory contains all configuration files for SmartCloudOps AI, including monitoring dashboards, security settings, and deployment configurations.

## 📁 Configuration Structure

```
configs/
├── 📁 monitoring/              # Monitoring configurations
│   ├── 📁 dashboards/         # Grafana dashboard definitions
│   │   ├── docker-containers.json
│   │   ├── ml-anomaly.json
│   │   └── system-overview.json
│   ├── grafana-datasources.yml # Grafana data source configuration
│   └── prometheus.yml         # Prometheus configuration
├── 📁 production/              # Production deployment configs
│   └── docker-compose.production.yml
├── 📁 security/                # Security configurations
│   └── 📁 ssl/                # SSL certificates and keys
├── 📄 grafana_ai_dashboards.json # AI-specific Grafana dashboards
├── 📄 production-deployment.yaml # Production deployment config
├── 📄 remediation-rules.yaml   # Auto-remediation rules
└── 📄 security-alerts.yml      # Security alerting rules
```

## 🚀 Quick Start

### Environment Setup
```bash
# Copy environment template
cp ../env.example .env

# Edit configuration
nano .env
```

### Monitoring Setup
```bash
# Deploy monitoring stack
docker-compose -f ../docker-compose.yml up -d prometheus grafana

# Import dashboards
# Access Grafana at http://localhost:13000 (admin/admin)
# Import dashboards from configs/monitoring/dashboards/
```

## 📊 Monitoring Configuration

### Prometheus Configuration (`monitoring/prometheus.yml`)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'smartcloudops-app'
    static_configs:
      - targets: ['smartcloudops-main:5000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Grafana Data Sources (`monitoring/grafana-datasources.yml`)
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

### Grafana Dashboards
- **System Overview**: Real-time system health monitoring
- **ML Anomaly**: Machine learning anomaly detection metrics
- **Docker Containers**: Container performance and resource usage

## 🔒 Security Configuration

### Security Alerts (`security-alerts.yml`)
```yaml
groups:
  - name: security_alerts
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 90% for 5 minutes"
```

### Remediation Rules (`remediation-rules.yaml`)
```yaml
remediation_rules:
  - name: high_cpu_remediation
    condition: cpu_usage > 90
    duration: 5m
    action: scale_up
    parameters:
      scale_factor: 1.5
      max_instances: 10
```

## 🐳 Docker Configuration

### Production Docker Compose (`production/docker-compose.production.yml`)
```yaml
version: '3.8'
services:
  smartcloudops-main:
    image: smartcloudops-ai:latest
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## 🔧 Configuration Management

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/smartcloudops
REDIS_HOST=redis
REDIS_PORT=6379

# Security Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# AI Services
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

### Configuration Validation
```bash
# Validate Prometheus configuration
promtool check config monitoring/prometheus.yml

# Validate Grafana configuration
# Check syntax in Grafana UI

# Validate Docker Compose
docker-compose -f docker-compose.yml config
```

## 📈 Dashboard Configuration

### System Overview Dashboard
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: Memory consumption trends
- **Disk I/O**: Storage performance metrics
- **Network Traffic**: Network utilization
- **Application Metrics**: API response times and error rates

### ML Anomaly Dashboard
- **Anomaly Scores**: Real-time anomaly detection scores
- **Model Performance**: ML model accuracy and latency
- **Feature Importance**: Key features affecting predictions
- **Training Metrics**: Model training performance

### Docker Containers Dashboard
- **Container Health**: Container status and health checks
- **Resource Usage**: CPU, memory, and disk usage per container
- **Network Metrics**: Container network performance
- **Log Analysis**: Container log patterns and errors

## 🔄 Configuration Deployment

### Automated Deployment
```bash
# Deploy all configurations
./scripts/deploy/deploy_complete_stack.sh

# Deploy monitoring only
./scripts/deploy/deploy_monitoring_server.sh

# Deploy production stack
./scripts/deploy/deploy_production_stack.sh
```

### Manual Deployment
```bash
# Copy configurations to containers
docker cp configs/monitoring/prometheus.yml prometheus:/etc/prometheus/
docker cp configs/monitoring/grafana-datasources.yml grafana:/etc/grafana/provisioning/datasources/

# Restart services
docker-compose restart prometheus grafana
```

## 🔍 Configuration Troubleshooting

### Common Issues

1. **Prometheus Configuration Errors**
   ```bash
   # Check configuration syntax
   promtool check config monitoring/prometheus.yml
   
   # View Prometheus logs
   docker-compose logs prometheus
   ```

2. **Grafana Dashboard Issues**
   ```bash
   # Check Grafana logs
   docker-compose logs grafana
   
   # Verify data source connectivity
   # Check in Grafana UI: Configuration > Data Sources
   ```

3. **Security Configuration Problems**
   ```bash
   # Validate security rules
   python -c "import yaml; yaml.safe_load(open('security-alerts.yml'))"
   
   # Check SSL certificates
   openssl x509 -in security/ssl/cert.pem -text -noout
   ```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=1

# Run with verbose output
docker-compose up -d --verbose
```

## 📚 Configuration Best Practices

### Security
- **Secrets Management**: Use environment variables for sensitive data
- **SSL/TLS**: Always use HTTPS in production
- **Access Control**: Implement proper authentication and authorization
- **Audit Logging**: Enable comprehensive audit trails

### Monitoring
- **Alert Thresholds**: Set appropriate alert thresholds
- **Dashboard Design**: Create intuitive and informative dashboards
- **Data Retention**: Configure appropriate data retention policies
- **Performance**: Optimize queries for better performance

### Deployment
- **Environment Separation**: Use different configs for dev/staging/prod
- **Version Control**: Track configuration changes in version control
- **Validation**: Validate configurations before deployment
- **Backup**: Regularly backup configuration files

## 🔄 Configuration Updates

### Rolling Updates
```bash
# Update configuration without downtime
docker-compose up -d --no-deps --build smartcloudops-main

# Verify update
curl http://localhost:5000/health
```

### Configuration Reload
```bash
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload

# Reload Grafana configuration
# Restart Grafana container or use API
```

## 📊 Configuration Monitoring

### Configuration Health Checks
```bash
# Check configuration status
curl http://localhost:5000/config/status

# Validate configuration
curl http://localhost:5000/config/validate
```

### Configuration Metrics
- **Configuration Version**: Track configuration versions
- **Validation Status**: Monitor configuration validation
- **Deployment Status**: Track configuration deployment
- **Error Rates**: Monitor configuration-related errors

## 🤝 Contributing

### Adding New Configurations
1. **Follow Naming Convention**: Use descriptive names
2. **Document Changes**: Update this README
3. **Test Configuration**: Validate before deployment
4. **Version Control**: Commit configuration changes
5. **Backup**: Create backups before major changes

### Configuration Review Checklist
- [ ] Configuration is properly documented
- [ ] Security settings are appropriate
- [ ] Performance impact is considered
- [ ] Configuration is tested in staging
- [ ] Rollback plan is available

---

**SmartCloudOps AI v3.3.0** - Configuration Management
