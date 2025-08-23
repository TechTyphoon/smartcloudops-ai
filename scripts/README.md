# SmartCloudOps AI - Utility Scripts

This directory contains utility scripts for deployment, monitoring, health checks, and operational tasks for SmartCloudOps AI.

## 📁 Scripts Structure

```
scripts/
├── 📁 deploy/                    # Deployment scripts
│   ├── deploy_complete_stack.sh # Complete stack deployment
│   ├── deploy_k8s_stack.sh      # Kubernetes deployment
│   ├── deploy-local-production.sh # Local production setup
│   ├── deploy_monitoring_server.sh # Monitoring stack deployment
│   └── deploy_production_stack.sh # Production deployment
├── 📁 monitoring/                # Monitoring scripts
│   ├── continuous_health_monitor.py # Continuous health monitoring
│   ├── continuous_monitor.sh    # Continuous monitoring shell script
│   ├── daily_status.sh          # Daily status report
│   ├── real_system_monitor.py   # Real-time system monitoring
│   └── uptime_monitor.py        # Uptime monitoring
├── 📄 cleanup.sh                # Cleanup utilities
├── 📄 deploy_flask_app.py       # Flask app deployment
├── 📄 deploy_production.sh      # Production deployment script
├── 📄 env_manager.py            # Environment management
├── 📄 health_check.py           # Health check utilities
├── 📄 morning_check.sh          # Morning health check
├── 📄 production_validation.py  # Production validation
├── 📄 quick-lint-fix.sh         # Quick linting fixes
├── 📄 setup.py                  # Setup utilities
├── 📄 start_app.py              # Application startup
├── 📄 test-local.sh             # Local testing script
├── 📄 validate_before_commit.sh # Pre-commit validation
└── 📄 verify_setup.py           # Setup verification
```

## 🚀 Quick Start

### Essential Scripts
```bash
# Start the application
./scripts/start_app.py

# Health check
./scripts/health_check.py

# Deploy complete stack
./scripts/deploy/deploy_complete_stack.sh

# Morning health check
./scripts/morning_check.sh
```

### Development Scripts
```bash
# Quick lint fix
./scripts/quick-lint-fix.sh

# Validate before commit
./scripts/validate_before_commit.sh

# Test locally
./scripts/test-local.sh
```

## 📋 Script Categories

### Deployment Scripts (`deploy/`)
- **Complete Stack**: Deploy entire SmartCloudOps AI stack
- **Kubernetes**: Deploy to Kubernetes cluster
- **Production**: Production environment deployment
- **Monitoring**: Monitoring stack deployment
- **Local Production**: Local production-like setup

### Monitoring Scripts (`monitoring/`)
- **Health Monitoring**: Continuous health checks
- **System Monitoring**: Real-time system metrics
- **Uptime Monitoring**: Service uptime tracking
- **Daily Reports**: Automated daily status reports

### Utility Scripts
- **Health Checks**: Application and service health
- **Environment Management**: Environment setup and configuration
- **Setup Verification**: Verify installation and configuration
- **Cleanup**: System cleanup utilities

## 🔧 Script Usage

### Deployment Scripts

#### Complete Stack Deployment
```bash
# Deploy complete stack
./scripts/deploy/deploy_complete_stack.sh

# Deploy with custom environment
./scripts/deploy/deploy_complete_stack.sh --env production
```

#### Kubernetes Deployment
```bash
# Deploy to Kubernetes
./scripts/deploy/deploy_k8s_stack.sh

# Deploy with specific namespace
./scripts/deploy/deploy_k8s_stack.sh --namespace smartcloudops
```

#### Production Deployment
```bash
# Deploy to production
./scripts/deploy/deploy_production_stack.sh

# Deploy with blue-green strategy
./scripts/deploy/deploy_production_stack.sh --strategy blue-green
```

### Monitoring Scripts

#### Health Monitoring
```bash
# Start continuous health monitoring
python scripts/monitoring/continuous_health_monitor.py

# Monitor specific services
python scripts/monitoring/continuous_health_monitor.py --services app,database,redis
```

#### System Monitoring
```bash
# Start real-time system monitoring
python scripts/monitoring/real_system_monitor.py

# Monitor with custom thresholds
python scripts/monitoring/real_system_monitor.py --cpu-threshold 80 --memory-threshold 85
```

#### Daily Status Report
```bash
# Generate daily status report
./scripts/monitoring/daily_status.sh

# Send report via email
./scripts/monitoring/daily_status.sh --email admin@company.com
```

### Utility Scripts

#### Health Checks
```bash
# Run health check
python scripts/health_check.py

# Check specific components
python scripts/health_check.py --components app,database,redis,prometheus
```

#### Environment Management
```bash
# Setup environment
python scripts/env_manager.py setup

# Validate environment
python scripts/env_manager.py validate

# Update environment
python scripts/env_manager.py update
```

#### Setup Verification
```bash
# Verify complete setup
python scripts/verify_setup.py

# Verify specific components
python scripts/verify_setup.py --components app,database,monitoring
```

## 📊 Monitoring and Alerting

### Health Check Metrics
- **Application Health**: Flask app status and performance
- **Database Health**: PostgreSQL connection and performance
- **Redis Health**: Redis connection and memory usage
- **Monitoring Health**: Prometheus and Grafana status
- **System Health**: CPU, memory, disk usage

### Alerting Configuration
```bash
# Configure alerts
python scripts/monitoring/continuous_health_monitor.py --configure-alerts

# Set alert thresholds
python scripts/monitoring/continuous_health_monitor.py \
  --cpu-threshold 80 \
  --memory-threshold 85 \
  --disk-threshold 90
```

### Notification Channels
- **Email**: SMTP-based email notifications
- **Slack**: Slack webhook notifications
- **Teams**: Microsoft Teams notifications
- **Webhook**: Custom webhook notifications

## 🔍 Troubleshooting

### Common Issues

1. **Deployment Failures**
   ```bash
   # Check deployment logs
   ./scripts/deploy/deploy_complete_stack.sh --debug
   
   # Validate configuration
   python scripts/verify_setup.py --validate-config
   ```

2. **Health Check Failures**
   ```bash
   # Run detailed health check
   python scripts/health_check.py --verbose
   
   # Check specific service
   python scripts/health_check.py --service app --debug
   ```

3. **Monitoring Issues**
   ```bash
   # Check monitoring status
   python scripts/monitoring/continuous_health_monitor.py --status
   
   # Restart monitoring
   python scripts/monitoring/continuous_health_monitor.py --restart
   ```

### Debug Mode
```bash
# Enable debug mode for all scripts
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run script with debug output
python scripts/health_check.py --debug
```

## 🔄 Automation

### Cron Jobs
```bash
# Add to crontab for automated monitoring
# Daily health check at 9 AM
0 9 * * * /path/to/smartcloudops-ai/scripts/morning_check.sh

# Continuous monitoring every 5 minutes
*/5 * * * * /path/to/smartcloudops-ai/scripts/monitoring/continuous_monitor.sh

# Daily status report at 6 PM
0 18 * * * /path/to/smartcloudops-ai/scripts/monitoring/daily_status.sh
```

### CI/CD Integration
```bash
# Pre-deployment validation
./scripts/validate_before_commit.sh

# Post-deployment verification
python scripts/verify_setup.py --post-deployment

# Health check after deployment
python scripts/health_check.py --post-deployment
```

## 📈 Performance Monitoring

### Performance Metrics
- **Response Time**: API response times
- **Throughput**: Requests per second
- **Error Rate**: Error percentage
- **Resource Usage**: CPU, memory, disk usage
- **Database Performance**: Query times, connections

### Performance Alerts
```bash
# Set performance thresholds
python scripts/monitoring/continuous_health_monitor.py \
  --response-time-threshold 500 \
  --error-rate-threshold 5 \
  --throughput-threshold 100
```

## 🔒 Security

### Security Checks
```bash
# Run security audit
python scripts/security_audit.py

# Check for vulnerabilities
python scripts/security_audit.py --vulnerabilities

# Validate security configuration
python scripts/verify_setup.py --security
```

### Access Control
- **Script Permissions**: Proper file permissions
- **Environment Variables**: Secure credential management
- **Network Security**: Secure communication channels
- **Audit Logging**: Comprehensive audit trails

## 📚 Best Practices

### Script Development
- **Error Handling**: Comprehensive error handling
- **Logging**: Proper logging and debugging
- **Documentation**: Clear documentation and usage
- **Testing**: Thorough testing of scripts
- **Security**: Security best practices

### Script Usage
- **Environment**: Use appropriate environment
- **Permissions**: Check script permissions
- **Dependencies**: Ensure dependencies are installed
- **Backup**: Backup before running scripts
- **Monitoring**: Monitor script execution

### Script Maintenance
- **Regular Updates**: Keep scripts updated
- **Version Control**: Track script changes
- **Testing**: Test scripts regularly
- **Documentation**: Maintain documentation
- **Security**: Regular security reviews

## 🤝 Contributing

### Adding New Scripts
1. **Follow Naming Convention**: Use descriptive names
2. **Add Documentation**: Document script purpose and usage
3. **Include Error Handling**: Comprehensive error handling
4. **Add Tests**: Include tests for new scripts
5. **Security Review**: Review security implications

### Script Review Checklist
- [ ] Script is properly documented
- [ ] Error handling is comprehensive
- [ ] Security considerations addressed
- [ ] Tests are included
- [ ] Performance impact considered

---

**SmartCloudOps AI v3.3.0** - Utility Scripts
