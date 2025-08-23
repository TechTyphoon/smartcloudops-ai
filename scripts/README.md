# 📁 SmartCloudOps AI Scripts

This directory contains utility scripts for development, deployment, monitoring, and testing of the SmartCloudOps AI platform.

## 📂 Directory Structure

```
scripts/
├── deployment/          # Deployment and infrastructure scripts
├── monitoring/          # System monitoring and health checks
├── testing/            # Testing and validation scripts
├── security/           # Security and compliance scripts
├── utils/              # Utility and helper scripts
└── README.md           # This file
```

## 🚀 Quick Start

### Development
```bash
# Start the application
./scripts/utils/start_app.py

# Health check
./scripts/testing/health_check.py

# Verify setup
./scripts/testing/verify_setup.py
```

### Deployment
```bash
# Deploy complete stack
./scripts/deployment/deploy_complete_stack.sh

# Deploy to production
./scripts/deployment/deploy_production_stack.sh --env production

# Deploy to Kubernetes
./scripts/deployment/deploy_k8s_stack.sh

# Deploy to Kubernetes with namespace
./scripts/deployment/deploy_k8s_stack.sh --namespace smartcloudops

# Deploy production stack
./scripts/deployment/deploy_production_stack.sh

# Deploy with blue-green strategy
./scripts/deployment/deploy_production_stack.sh --strategy blue-green
```

### Monitoring
```bash
# Continuous health monitoring
python scripts/monitoring/continuous_health_monitor.py

# Monitor specific services
python scripts/monitoring/continuous_health_monitor.py --services app,database,redis

# Real-time system monitoring
python scripts/monitoring/real_system_monitor.py

# Monitor with custom thresholds
python scripts/monitoring/real_system_monitor.py --cpu-threshold 80 --memory-threshold 85

# Daily status report
./scripts/monitoring/daily_status.sh

# Daily status with email
./scripts/monitoring/daily_status.sh --email admin@company.com
```

### Testing
```bash
# Health check
python scripts/testing/health_check.py

# Health check with components
python scripts/testing/health_check.py --components app,database,redis,prometheus

# Environment setup
python scripts/utils/env_manager.py setup

# Environment validation
python scripts/utils/env_manager.py validate

# Environment update
python scripts/utils/env_manager.py update

# Verify setup
python scripts/testing/verify_setup.py

# Verify setup with components
python scripts/testing/verify_setup.py --components app,database,monitoring
```

### Utilities
```bash
# Quick lint fix
./scripts/utils/quick-lint-fix.sh

# Validate before commit
./scripts/utils/validate_before_commit.sh

# Morning check
./scripts/utils/morning_check.sh

# Cleanup
./scripts/utils/cleanup.sh
```

## 🔧 Advanced Usage

### Continuous Monitoring Setup
```bash
# Configure alerts
python scripts/monitoring/continuous_health_monitor.py --configure-alerts

# Monitor with custom configuration
python scripts/monitoring/continuous_health_monitor.py \
    --services app,database,redis,prometheus \
    --interval 30 \
    --log-level INFO
```

### Production Validation
```bash
# Validate configuration
python scripts/testing/verify_setup.py --validate-config

# Health check with verbose output
python scripts/testing/health_check.py --verbose

# Health check specific service with debug
python scripts/testing/health_check.py --service app --debug
```

### Monitoring Management
```bash
# Check monitoring status
python scripts/monitoring/continuous_health_monitor.py --status

# Restart monitoring
python scripts/monitoring/continuous_health_monitor.py --restart
```

### Troubleshooting
```bash
# Health check with debug
python scripts/testing/health_check.py --debug

# Post-deployment verification
python scripts/testing/verify_setup.py --post-deployment

# Post-deployment health check
python scripts/testing/health_check.py --post-deployment
```

### Monitoring with Alerts
```bash
# Monitor with custom configuration
python scripts/monitoring/continuous_health_monitor.py \
    --services app,database,redis,prometheus \
    --interval 30 \
    --log-level INFO \
    --alert-webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 📋 Cron Jobs

For production environments, set up these cron jobs:

```bash
# Morning health check (9 AM daily)
0 9 * * * /path/to/project/scripts/utils/morning_check.sh

# Continuous monitoring (every 5 minutes)
*/5 * * * * /path/to/project/scripts/monitoring/continuous_monitor.sh

# Daily status report (6 PM daily)
0 18 * * * /path/to/project/scripts/monitoring/daily_status.sh
```

## 🔍 Script Details

### Deployment Scripts
- **deploy_complete_stack.sh**: Deploy the entire application stack
- **deploy_production_stack.sh**: Production deployment with safety checks
- **deploy_k8s_stack.sh**: Kubernetes deployment
- **deploy_monitoring_server.sh**: Monitoring infrastructure deployment
- **deploy_flask_app.py**: Flask application deployment

### Monitoring Scripts
- **continuous_health_monitor.py**: Continuous health monitoring
- **real_system_monitor.py**: Real-time system monitoring
- **uptime_monitor.py**: Uptime monitoring
- **continuous_monitor.sh**: Shell-based continuous monitoring
- **daily_status.sh**: Daily status reporting

### Testing Scripts
- **test-local.sh**: Local testing suite
- **health_check.py**: Health check utilities
- **verify_setup.py**: Setup verification
- **production_validation.py**: Production validation

### Utility Scripts
- **start_app.py**: Application startup
- **setup.py**: Environment setup
- **env_manager.py**: Environment management
- **cleanup.sh**: Cleanup utilities
- **quick-lint-fix.sh**: Quick linting fixes
- **validate_before_commit.sh**: Pre-commit validation
- **morning_check.sh**: Morning health checks

## 🛠️ Development

### Adding New Scripts
1. Place scripts in the appropriate directory
2. Add documentation to this README
3. Ensure proper error handling
4. Add logging for debugging
5. Test thoroughly

### Script Standards
- Use Python 3.8+ for Python scripts
- Use bash for shell scripts
- Include proper error handling
- Add logging and verbose output options
- Follow the existing naming conventions
- Include help/usage information

## 📞 Support

For issues with scripts:
1. Check the script's help output: `./script.sh --help`
2. Review the logs for error messages
3. Verify environment configuration
4. Check dependencies and permissions
