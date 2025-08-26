# SmartCloudOps AI - Production Deployment Guide

## 🚀 Production Deployment System
**Phase 2C Week 2: Production Deployment - Complete Implementation**

This comprehensive production deployment system provides enterprise-grade deployment automation, monitoring, security, and health checking for SmartCloudOps AI.

## 📋 System Overview

### Core Components

1. **Health Checks System** (`health_checks.py`)
   - System resource monitoring
   - Database connectivity verification
   - MLOps service validation
   - API endpoint testing
   - Cache system health

2. **Monitoring & Alerting** (`monitoring.py`)
   - Real-time metrics collection
   - Alert management with multiple notification channels
   - Performance monitoring with thresholds
   - Dashboard data aggregation

3. **Configuration Management** (`config.py`)
   - Environment-specific configurations
   - Security settings management
   - Performance optimization settings
   - Validation and validation

4. **Security Hardening** (`security.py`)
   - Input validation and sanitization
   - Rate limiting with multiple strategies
   - Security auditing and vulnerability scanning
   - SSL/TLS and CORS configuration

5. **Deployment Automation** (`deploy.py`)
   - Multi-phase deployment process
   - Backup and rollback capabilities
   - Environment validation
   - Automated verification

## 🛠 Installation & Setup

### Prerequisites

```bash
# Required Python packages
pip install flask flask-cors psutil structlog

# Optional packages for enhanced functionality
pip install mlflow pandas numpy scikit-learn redis
```

### Environment Configuration

Create environment-specific configuration files:

```bash
# Production environment variables
export ENVIRONMENT=production
export DATABASE_PATH=/opt/smartcloudops/data/mlops_production.db
export LOG_LEVEL=INFO
export SSL_ENABLED=true
export MONITORING_ENABLED=true
export CACHE_ENABLED=true
```

### Security Configuration

```bash
# Generate secure secrets
export SECRET_KEY=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -base64 32)
export PASSWORD_SALT=$(openssl rand -base64 16)

# SSL Configuration
export SSL_CERT_PATH=/path/to/certificate.crt
export SSL_KEY_PATH=/path/to/private.key

# CORS Configuration
export CORS_ORIGINS=https://smartcloudops.ai,https://api.smartcloudops.ai
```

## 🚀 Deployment Process

### Automated Deployment

```bash
# Deploy to production
python deployment/production/deploy.py production

# Deploy to staging
python deployment/production/deploy.py staging
```

### Manual Deployment Steps

1. **Preparation Phase**
   ```python
   from deployment.production.config import initialize_config, Environment
   from deployment.production.deploy import DeploymentManager
   
   # Initialize configuration
   config = initialize_config(Environment.PRODUCTION)
   
   # Validate configuration
   issues = config.validate_config()
   if issues:
       print("Configuration issues:", issues)
   ```

2. **Security Validation**
   ```python
   from deployment.production.security import security_auditor
   
   # Run security audit
   audit_results = security_auditor.run_security_audit()
   print(f"Security score: {audit_results['score_percentage']:.1f}%")
   ```

3. **Health Checks**
   ```python
   from deployment.production.health_checks import quick_health_check
   import asyncio
   
   # Run health checks
   health_results = await quick_health_check()
   print(f"Overall status: {health_results['overall_status']}")
   ```

## 📊 Monitoring & Alerting

### Initialize Monitoring

```python
from deployment.production.monitoring import initialize_monitoring

# Email configuration for alerts
email_config = {
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'alerts@smartcloudops.ai',
    'password': 'app_password',
    'from_email': 'alerts@smartcloudops.ai',
    'to_emails': ['admin@smartcloudops.ai']
}

# Initialize monitoring with email alerts
initialize_monitoring(email_config)
```

### Custom Health Checks

```python
from deployment.production.health_checks import BaseHealthCheck, health_monitor

class CustomServiceCheck(BaseHealthCheck):
    def __init__(self):
        super().__init__("custom_service")
    
    async def check(self):
        # Custom health check logic
        return self._create_result(
            HealthStatus.HEALTHY,
            "Custom service operational",
            0.1
        )

# Add custom check
health_monitor.add_check(CustomServiceCheck())
```

## 🔒 Security Features

### Rate Limiting

```python
from deployment.production.security import security_required

@app.route('/api/sensitive')
@security_required(rule='auth')  # 10 requests per 5 minutes
def sensitive_endpoint():
    return jsonify({'data': 'sensitive'})
```

### Input Validation

```python
from deployment.production.security import validate_input

@app.route('/api/data', methods=['POST'])
@validate_input(
    username={'required': True, 'max_length': 50},
    message={'max_length': 500}
)
def create_data():
    return jsonify({'status': 'success'})
```

### Security Audit

```python
from deployment.production.security import security_auditor

# Run comprehensive security audit
audit_results = security_auditor.run_security_audit()

print(f"Security Level: {audit_results['security_level']}")
print(f"Score: {audit_results['score_percentage']:.1f}%")

if audit_results['critical_issues']:
    print("Critical Issues:")
    for issue in audit_results['critical_issues']:
        print(f"  - {issue}")
```

## 📈 Performance Monitoring

### System Metrics

The monitoring system automatically tracks:

- **System Resources**: CPU, memory, disk usage
- **Application Performance**: Response times, request counts
- **Database Performance**: Query times, connection pool status
- **Cache Performance**: Hit rates, eviction rates
- **Network I/O**: Bytes sent/received

### Custom Metrics

```python
from deployment.production.monitoring import metric_collector

# Record custom metrics
metric_collector.record_metric('api_requests', 1)
metric_collector.record_metric('user_logins', 1)
metric_collector.record_metric('model_predictions', 5)

# Get metric statistics
stats = metric_collector.calculate_metric_stats('api_requests', duration_hours=1)
print(f"API requests in last hour: {stats}")
```

### Alerts Configuration

```python
from deployment.production.monitoring import alert_manager, AlertSeverity

# Create custom alert
alert_manager.create_alert(
    title="High CPU Usage",
    message="CPU usage exceeded 90% for 5 minutes",
    severity=AlertSeverity.CRITICAL,
    component="system",
    metadata={'cpu_usage': 95.2}
)
```

## 🔧 Configuration Management

### Environment-Specific Configs

```python
from deployment.production.config import ProductionConfig, Environment

# Load configuration for specific environment
config = ProductionConfig(Environment.PRODUCTION)

# Access configuration sections
print(f"Database path: {config.database.path}")
print(f"Cache enabled: {config.cache.enabled}")
print(f"SSL enabled: {config.security.ssl_enabled}")
```

### Configuration Validation

```python
# Validate configuration
issues = config.validate_config()

if issues:
    print("Configuration Issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ Configuration is valid")
```

## 🏥 Health Checks

### Available Health Checks

1. **System Resources**: CPU, memory, disk usage
2. **Database**: Connectivity, performance, integrity
3. **MLOps Service**: Component availability, functionality
4. **API Endpoints**: Response times, status codes
5. **Cache System**: Operations, statistics

### Custom Health Checks

```python
from deployment.production.health_checks import BaseHealthCheck, HealthStatus

class DatabaseConnectionCheck(BaseHealthCheck):
    async def check(self):
        # Test database connection
        try:
            # Database connection logic here
            return self._create_result(
                HealthStatus.HEALTHY,
                "Database connection successful",
                0.05
            )
        except Exception as e:
            return self._create_result(
                HealthStatus.CRITICAL,
                f"Database connection failed: {e}",
                0.05
            )
```

## 🔄 Backup & Recovery

### Automated Backups

The deployment system automatically creates backups:

- **Database**: Full database backup before deployment
- **Configuration**: Current configuration snapshot
- **Logs**: Application logs backup
- **Retention**: Configurable retention period (default: 30 days)

### Manual Backup

```python
from deployment.production.deploy import DeploymentManager

deployment_manager = DeploymentManager()
backup_result = await deployment_manager._create_backup()
print(f"Backup created: {backup_result['backup_directory']}")
```

### Rollback Process

```python
# Automatic rollback on deployment failure
# Or manual rollback
rollback_result = await deployment_manager._rollback_deployment()
```

## 📋 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database file permissions
   ls -la data/mlops_production.db
   
   # Verify database integrity
   sqlite3 data/mlops_production.db "PRAGMA integrity_check;"
   ```

2. **High Memory Usage**
   ```python
   from deployment.production.monitoring import metric_collector
   
   # Check memory metrics
   memory_stats = metric_collector.calculate_metric_stats('memory_usage')
   print(f"Memory usage trend: {memory_stats['trend']}")
   ```

3. **SSL Certificate Issues**
   ```bash
   # Verify certificate validity
   openssl x509 -in /path/to/certificate.crt -text -noout
   
   # Check certificate expiration
   openssl x509 -in /path/to/certificate.crt -checkend 86400
   ```

### Logs Location

- **Application Logs**: `logs/production.log`
- **Deployment Logs**: `logs/deployments.json`
- **Alert Logs**: `logs/alerts.log`
- **Health Check Logs**: `logs/health_checks.log`

### Performance Tuning

1. **Database Optimization**
   ```python
   from app.performance.database_optimization import get_database
   
   db = get_database()
   optimization_result = db.optimize_table('experiments')
   ```

2. **Cache Tuning**
   ```python
   from app.performance.caching import cache_manager
   
   # Get cache statistics
   cache_stats = cache_manager.get_stats()
   
   # Optimize cache sizes based on hit rates
   for cache_name, stats in cache_stats.items():
       if stats['hit_rate'] < 0.7:
           print(f"Consider increasing size for {cache_name}")
   ```

## 🎯 Production Checklist

### Pre-Deployment

- [ ] Configuration validated
- [ ] Security audit passed (score ≥ 80%)
- [ ] SSL certificates valid
- [ ] Database backup created
- [ ] System requirements met
- [ ] Dependencies installed

### Post-Deployment

- [ ] Health checks passing
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Performance baseline established
- [ ] Backup schedule verified
- [ ] Documentation updated

### Daily Operations

- [ ] Review health check status
- [ ] Monitor performance metrics
- [ ] Check for security alerts
- [ ] Verify backup completion
- [ ] Review application logs

## 📞 Support

For deployment issues or questions:

1. Check the troubleshooting section
2. Review application logs
3. Run health checks for system status
4. Check monitoring dashboard for metrics

## 🔄 Updates

To update the production deployment system:

1. Test changes in staging environment
2. Run security audit on new code
3. Create backup before deployment
4. Use automated deployment process
5. Verify health checks post-deployment

---

**SmartCloudOps AI Production Deployment**  
*Enterprise-grade deployment automation with comprehensive monitoring, security, and health checking.*
