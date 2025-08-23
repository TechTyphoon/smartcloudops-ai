# SmartCloudOps AI - Production Deployment Guide

**Phase 7: Production Launch & Feedback**  
**Version**: 1.0.0  
**Last Updated**: August 9, 2025

## 🚀 Overview

This guide provides comprehensive instructions for deploying SmartCloudOps AI to production environments. The system includes:

- **Backend API** with JWT authentication and role-based access control
- **Database** with PostgreSQL and Redis caching
- **Monitoring** with Prometheus and Grafana
- **Reverse Proxy** with Nginx and SSL/TLS
- **Log Aggregation** with ELK Stack (optional)
- **Automated Deployment** scripts for cloud environments

## 📋 Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ / CentOS 8+ / Amazon Linux 2
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: 50GB+ available space
- **Network**: Public IP with ports 80, 443, 8080 open

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **OpenSSL**: For certificate generation

### Domain & SSL

- **Domain Name**: Registered domain pointing to your server
- **SSL Certificate**: Let's Encrypt (automatic) or custom certificate
- **Email**: Valid email for SSL certificate notifications

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/smartcloudops-ai.git
cd smartcloudops-ai
```

### 2. Run Production Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy_production.sh

# Set environment variables
export DOMAIN_NAME="yourdomain.com"
export SSL_EMAIL="admin@yourdomain.com"
export DEPLOYMENT_ENV="production"

# Run deployment
./scripts/deploy_production.sh
```

The deployment script will:
- ✅ Check system prerequisites
- ✅ Setup environment variables
- ✅ Create necessary directories
- ✅ Obtain SSL certificates
- ✅ Deploy all services
- ✅ Initialize database
- ✅ Setup monitoring
- ✅ Run health checks

### 3. Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# 1. Setup environment
cp env.template .env
# Edit .env with your configuration

# 2. Create directories
mkdir -p logs backups configs/ssl data

# 3. Deploy services
docker-compose -f docker-compose.prod.yml up -d

# 4. Initialize database
docker-compose -f docker-compose.prod.yml exec app python3 -c "
import sys
sys.path.append('/app')
from app.database import init_db, seed_initial_data
init_db()
seed_initial_data()
"
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://smartcloudops:your_secure_password@postgres:5432/smartcloudops

# Redis Configuration
REDIS_PASSWORD=your_redis_password

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production
JWT_EXPIRY_HOURS=24

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO

# Domain Configuration
DOMAIN_NAME=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# AI Provider Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Security Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=true

# AWS Configuration (if using AWS services)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Monitoring Configuration
GRAFANA_PASSWORD=your_grafana_password
```

### SSL Certificate Setup

#### Automatic (Let's Encrypt)

The deployment script automatically handles SSL certificate generation using Let's Encrypt.

#### Manual SSL Setup

If you have custom certificates:

```bash
# Copy your certificates
cp your_certificate.crt configs/ssl/live/yourdomain.com/fullchain.pem
cp your_private_key.key configs/ssl/live/yourdomain.com/privkey.pem

# Set proper permissions
chmod 600 configs/ssl/live/yourdomain.com/privkey.pem
chmod 644 configs/ssl/live/yourdomain.com/fullchain.pem
```

## 🌐 Service URLs

After deployment, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| Main Application | `https://yourdomain.com` | SmartCloudOps AI main interface |
| API Documentation | `https://yourdomain.com/api/docs` | Complete API documentation |
| Grafana Dashboard | `https://yourdomain.com/grafana` | Monitoring dashboards |
| Prometheus | `https://yourdomain.com/prometheus` | Metrics and alerting |
| Health Check | `https://yourdomain.com/health` | System health status |

## 🔐 Default Credentials

**⚠️ IMPORTANT**: Change these credentials immediately after deployment!

### Application Users

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full system access |
| `demo` | `demo123` | User | Limited access for testing |

### Grafana

- **Username**: `admin`
- **Password**: Set in `GRAFANA_PASSWORD` environment variable

### Database

- **Database**: `smartcloudops`
- **Username**: `smartcloudops`
- **Password**: Set in `POSTGRES_PASSWORD` environment variable

## 📊 Monitoring & Logging

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:

- HTTP request counts and latency
- Database connection status
- Application health metrics
- Custom business metrics

### Grafana Dashboards

Pre-configured dashboards include:

- **System Overview**: CPU, memory, disk usage
- **Application Metrics**: Request rates, error rates, response times
- **Database Performance**: Connection pools, query performance
- **Security Metrics**: Authentication attempts, failed logins

### Log Aggregation

Logs are collected and can be viewed in:

- **Application Logs**: `logs/app.log`
- **Nginx Logs**: `logs/nginx/`
- **Docker Logs**: `docker-compose -f docker-compose.prod.yml logs`

### ELK Stack (Optional)

For advanced log analysis, the ELK stack is included:

- **Elasticsearch**: `http://localhost:9200`
- **Kibana**: `http://localhost:5601`
- **Filebeat**: Collects logs from all services

## 🔄 Maintenance

### Backup

#### Database Backup

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U smartcloudops smartcloudops > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup (configured in docker-compose.prod.yml)
docker-compose -f docker-compose.prod.yml run --rm backup
```

#### Configuration Backup

```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    .env \
    configs/ \
    logs/ \
    backups/
```

### Updates

#### Application Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml build app
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations (if any)
docker-compose -f docker-compose.prod.yml exec app python3 -c "
import sys
sys.path.append('/app')
from app.database import init_db
init_db()
"
```

#### SSL Certificate Renewal

SSL certificates auto-renew every 60 days. Manual renewal:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

### Health Monitoring

#### Automated Health Checks

The system includes automated health checks:

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View health check logs
docker-compose -f docker-compose.prod.yml logs healthcheck

# Manual health check
curl -f https://yourdomain.com/health
```

#### Monitoring Alerts

Configure alerts in Grafana for:

- High CPU/memory usage
- Database connection failures
- Application errors
- SSL certificate expiration

## 🚨 Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check service logs
docker-compose -f docker-compose.prod.yml logs app
docker-compose -f docker-compose.prod.yml logs postgres

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

#### 2. Database Connection Issues

```bash
# Check database connectivity
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U smartcloudops

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

#### 3. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in configs/ssl/live/yourdomain.com/fullchain.pem -text -noout

# Renew certificates manually
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
```

#### 4. Performance Issues

```bash
# Check resource usage
docker stats

# Check application metrics
curl https://yourdomain.com/metrics

# Check nginx access logs
tail -f logs/nginx/access.log
```

### Log Locations

| Component | Log Location |
|-----------|--------------|
| Application | `logs/app.log` |
| Nginx | `logs/nginx/` |
| Database | `docker-compose -f docker-compose.prod.yml logs postgres` |
| Prometheus | `docker-compose -f docker-compose.prod.yml logs prometheus` |
| Grafana | `docker-compose -f docker-compose.prod.yml logs grafana` |

### Performance Tuning

#### Database Optimization

```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Optimize database
VACUUM ANALYZE;
REINDEX DATABASE smartcloudops;
```

#### Application Optimization

```bash
# Increase worker processes
# Edit docker-compose.prod.yml
# Add to app service:
#   environment:
#     - GUNICORN_WORKERS=4
#     - GUNICORN_THREADS=2
```

## 🔒 Security

### Security Best Practices

1. **Change Default Passwords**: Immediately after deployment
2. **Firewall Configuration**: Only open necessary ports
3. **Regular Updates**: Keep system and dependencies updated
4. **Backup Strategy**: Regular automated backups
5. **Monitoring**: Set up alerts for security events
6. **Access Control**: Use role-based access control
7. **SSL/TLS**: Always use HTTPS in production

### Security Headers

The application includes security headers:

- `X-Frame-Options`: Prevent clickjacking
- `X-Content-Type-Options`: Prevent MIME type sniffing
- `X-XSS-Protection`: XSS protection
- `Strict-Transport-Security`: Force HTTPS
- `Content-Security-Policy`: Prevent XSS and injection attacks

### Rate Limiting

API endpoints are rate limited:

- **General API**: 10 requests/second
- **Login endpoints**: 5 requests/minute
- **Health checks**: No limits

## 📞 Support

### Getting Help

1. **Documentation**: Check this guide and API documentation
2. **Logs**: Review application and system logs
3. **Community**: GitHub issues and discussions
4. **Support**: Email support@smartcloudops.ai

### Useful Commands

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker-compose -f docker-compose.prod.yml restart app

# Check resource usage
docker system df
docker stats

# Clean up unused resources
docker system prune -f

# Update all services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Scaling

### Horizontal Scaling

To scale the application:

```bash
# Scale application instances
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Update nginx configuration for load balancing
# Edit configs/nginx.conf to include multiple app instances
```

### Vertical Scaling

For increased performance:

1. **Increase Resources**: More CPU/RAM for containers
2. **Database Optimization**: Connection pooling, indexing
3. **Caching**: Redis caching for frequently accessed data
4. **CDN**: Use CDN for static assets

## 🎯 Next Steps

After successful deployment:

1. **Change Default Passwords**: Immediately
2. **Configure Monitoring**: Set up Grafana dashboards and alerts
3. **Setup Backup**: Configure automated backup strategy
4. **Security Audit**: Review security configuration
5. **Performance Testing**: Load test the application
6. **Documentation**: Update internal documentation
7. **Training**: Train team on system usage

---

**SmartCloudOps AI** - Phase 7 Production Deployment Guide  
**Version**: 1.0.0  
**Last Updated**: August 9, 2025
