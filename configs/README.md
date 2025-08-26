# 📁 SmartCloudOps AI - Configuration Guide

This directory contains all configuration files for the SmartCloudOps AI platform. The configuration system has been consolidated to reduce redundancy and improve maintainability.

## 🏗️ Configuration Structure

```
configs/
├── README.md                           # This file - Configuration guide
├── env.production.override             # Production environment overrides
├── monitoring/                         # Monitoring stack configurations
│   ├── prometheus.yml                  # Prometheus configuration
│   ├── grafana-datasources.yml         # Grafana data sources
│   └── dashboards/                     # Grafana dashboard definitions
├── production/                         # Production deployment files
│   ├── docker-compose.production.yml   # Production Docker setup
│   └── nginx.conf                      # Production Nginx configuration
├── security/                           # Security configurations
│   ├── security-alerts.yml             # Security alert rules
│   └── ssl/                           # SSL certificate storage
├── nginx.conf                          # Development Nginx configuration
├── nginx-server.conf                   # Alternative Nginx setup
└── remediation-rules.yaml              # Automated remediation rules
```

## 🔧 Environment Configuration

### Primary Configuration Files

1. **`../env.template`** - Master configuration template
   - Contains all available configuration options
   - Secure defaults for development
   - Comprehensive documentation for each setting
   - Copy to `.env` and customize for your environment

2. **`env.production.override`** - Production overrides
   - Production-specific security settings
   - AWS integration configurations
   - Performance optimizations
   - Use with env.template for production deployment

### Deprecated/Removed Files
- ~~`env.secure`~~ → Merged into `env.template`
- ~~`deployment.env`~~ → Merged into `env.template`
- ~~`env.production`~~ → Replaced with `env.production.override`

## 🚀 Quick Setup

### Development Environment
```bash
# 1. Copy the template
cp env.template .env

# 2. Edit configuration for your local setup
nano .env
```

### Production Environment
```bash
# 1. Copy the template
cp env.template .env.production

# 2. Apply production overrides
cat configs/env.production.override >> .env.production

# 3. Set secure values for production variables
nano .env.production
```

## 🔐 Security Configuration

### Required Production Changes
1. **Generate secure keys**:
   ```bash
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
   python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
   ```

2. **Enable security headers**:
   ```env
   SECURITY_HEADERS_ENABLED=true
   SECURE_COOKIES=true
   SESSION_COOKIE_SECURE=true
   ```

3. **Configure database credentials**:
   - Use AWS Secrets Manager for RDS passwords
   - Enable SSL connections
   - Use connection pooling

4. **Set up AI API keys**:
   - Store in AWS Secrets Manager
   - Use environment variables for access
   - Rotate keys regularly

## 📊 Monitoring Configuration

### Prometheus (`monitoring/prometheus.yml`)
- Scrape configurations for all services
- Alerting rules for anomaly detection
- Data retention policies

### Grafana (`monitoring/grafana-datasources.yml`)
- Prometheus data source configuration
- Dashboard provisioning
- User authentication settings

### Dashboards (`monitoring/dashboards/`)
- `system-overview.json` - System health overview
- `ml-anomaly.json` - ML model monitoring
- `docker-containers.json` - Container metrics

## 🔄 Automated Remediation

### Rules Configuration (`remediation-rules.yaml`)
```yaml
rules:
  - name: high_cpu_usage
    condition: cpu_usage > 90
    duration: 5m
    action: scale_up
    cooldown: 10m
```

## 🌐 Network Configuration

### Nginx Configuration
- `nginx.conf` - Development proxy configuration
- `nginx-server.conf` - Alternative server setup
- `production/nginx.conf` - Production-ready configuration with SSL

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security (HSTS)

## 📦 Container Configuration

### Docker Compose Files
- `../docker-compose.yml` - Development stack
- `production/docker-compose.production.yml` - Production stack
- `../demo/docker-compose.demo.yml` - Demo environment

## 🔍 Configuration Validation

Run the configuration validator:
```bash
python scripts/testing/verify_setup.py
```

## 📚 Environment Variables Reference

### Core Variables
| Variable | Description | Default | Production Required |
|----------|-------------|---------|-------------------|
| `FLASK_ENV` | Flask environment | `development` | `production` |
| `SECRET_KEY` | Flask secret key | Random | ✅ Required |
| `JWT_SECRET_KEY` | JWT signing key | Random | ✅ Required |
| `DATABASE_URL` | Database connection | SQLite | PostgreSQL ✅ |

### AWS Variables
| Variable | Description | Required for AWS |
|----------|-------------|------------------|
| `AWS_REGION` | AWS region | ✅ |
| `DB_HOST` | RDS endpoint | ✅ |
| `REDIS_HOST` | ElastiCache endpoint | ✅ |

### AI/ML Variables
| Variable | Description | Required for AI |
|----------|-------------|-----------------|
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `GEMINI_API_KEY` | Google Gemini key | Optional |

## 🚨 Security Best Practices

1. **Never commit secrets** to version control
2. **Use AWS Secrets Manager** for production secrets
3. **Enable security headers** in production
4. **Use strong random keys** (minimum 32 characters)
5. **Enable SSL/TLS** for all connections
6. **Regularly rotate** API keys and passwords
7. **Use IAM roles** instead of access keys when possible

## 🆘 Troubleshooting

### Common Configuration Issues

1. **Database connection fails**:
   - Check `DATABASE_URL` format
   - Verify database credentials
   - Ensure database server is running

2. **AI features not working**:
   - Verify API keys are set correctly
   - Check `AI_PROVIDER` setting
   - Ensure network connectivity to AI services

3. **Monitoring not working**:
   - Check Prometheus configuration
   - Verify service discovery settings
   - Ensure all services are accessible

### Configuration Validation
```bash
# Test configuration loading
python -c "from app.config import get_config; print('Config loaded successfully')"

# Validate environment
python scripts/testing/verify_setup.py
```

---

## 📞 Support

For configuration support:
- Check the [troubleshooting guide](../docs/troubleshooting.md)
- Review [deployment documentation](../DEPLOYMENT_GUIDE.md)
- Submit issues on GitHub