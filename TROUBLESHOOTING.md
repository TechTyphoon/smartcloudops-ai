# 🔧 Troubleshooting Guide - SmartCloudOps AI

This guide provides solutions for common issues encountered when deploying and operating SmartCloudOps AI.

---

## 📋 Table of Contents

- [Quick Diagnostics](#-quick-diagnostics)
- [Common Issues](#-common-issues)
- [Service-Specific Issues](#-service-specific-issues)
- [Performance Issues](#-performance-issues)
- [Security Issues](#-security-issues)
- [Debug Commands](#-debug-commands)
- [Recovery Procedures](#-recovery-procedures)

---

## 🔍 Quick Diagnostics

### Health Check Commands
```bash
# Basic health check
curl http://localhost:5000/health

# Comprehensive health check
python scripts/testing/health_check.py

# Verify setup
python scripts/testing/verify_setup.py

# Check all services
docker-compose ps
```

### System Status Commands
```bash
# Check system resources
python scripts/monitoring/real_system_monitor.py

# Monitor services
python scripts/monitoring/continuous_health_monitor.py

# Check logs
docker-compose logs --tail=100
```

---

## 🚨 Common Issues

### 1. Application Won't Start

#### Symptoms
- Service fails to start
- Port already in use errors
- Environment variable issues

#### Solutions
```bash
# Check if port is in use
sudo netstat -tulpn | grep :5000

# Kill process using port
sudo kill -9 $(sudo lsof -t -i:5000)

# Check environment variables
python scripts/testing/verify_setup.py --env-check

# Start with debug mode
export FLASK_DEBUG=true
python app/main.py
```

#### Debug Steps
```bash
# Check service logs
docker-compose logs smartcloudops-main

# Verify configuration
python scripts/testing/verify_setup.py --verbose

# Test database connection
python scripts/testing/health_check.py --database
```

### 2. Database Connection Issues

#### Symptoms
- Database connection timeout
- Authentication failures
- Connection pool exhaustion

#### Solutions
```bash
# Test database connection
python scripts/testing/health_check.py --database

# Check database status
docker-compose exec postgres pg_isready

# Verify database configuration
python scripts/testing/verify_setup.py --database-config

# Reset database connection
docker-compose restart postgres
```

#### Database Recovery
```bash
# Backup database
docker-compose exec postgres pg_dump -U cloudops cloudops > backup.sql

# Restore database
docker-compose exec -T postgres psql -U cloudops cloudops < backup.sql

# Reset database
docker-compose down
docker volume rm cloudops_postgres_data
docker-compose up -d postgres
```

### 3. Redis Connection Issues

#### Symptoms
- Cache failures
- Session storage issues
- Performance degradation

#### Solutions
```bash
# Test Redis connection
python scripts/testing/health_check.py --redis

# Check Redis status
docker-compose exec redis redis-cli ping

# Verify Redis configuration
python scripts/testing/verify_setup.py --redis-config

# Reset Redis
docker-compose restart redis
```

### 4. Monitoring Issues

#### Symptoms
- Prometheus not collecting metrics
- Grafana dashboards not loading
- Missing monitoring data

#### Solutions
```bash
# Check Prometheus status
curl http://localhost:9090/-/healthy

# Check Grafana status
curl http://localhost:3000/api/health

# Verify monitoring configuration
python scripts/testing/verify_setup.py --monitoring

# Restart monitoring services
docker-compose restart prometheus grafana
```

#### Monitoring Recovery
```bash
# Reset monitoring data
docker-compose down
docker volume rm cloudops_prometheus_data
docker-compose up -d prometheus grafana

# Reconfigure dashboards
./scripts/monitoring/upload_dashboards.sh
```

---

## 🔧 Service-Specific Issues

### Flask Application Issues

#### Application Crashes
```bash
# Check application logs
docker-compose logs -f smartcloudops-main

# Run with debug mode
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG
python app/main.py

# Check for memory leaks
python scripts/monitoring/real_system_monitor.py --memory
```

#### API Endpoint Issues
```bash
# Test API endpoints
curl -X GET http://localhost:5000/health
curl -X GET http://localhost:5000/status
curl -X GET http://localhost:5000/metrics

# Check API logs
docker-compose logs smartcloudops-main | grep "ERROR"
```

### PostgreSQL Issues

#### Database Performance
```bash
# Check database performance
docker-compose exec postgres psql -U cloudops -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
docker-compose exec postgres psql -U cloudops -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Analyze database
docker-compose exec postgres psql -U cloudops -c "ANALYZE;"
```

#### Database Corruption
```bash
# Check database integrity
docker-compose exec postgres psql -U cloudops -c "SELECT pg_check_visible('cloudops');"

# Rebuild database indexes
docker-compose exec postgres psql -U cloudops -c "REINDEX DATABASE cloudops;"
```

### Redis Issues

#### Memory Issues
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Monitor Redis performance
docker-compose exec redis redis-cli monitor
```

#### Connection Issues
```bash
# Check Redis connections
docker-compose exec redis redis-cli info clients

# Test Redis connectivity
docker-compose exec redis redis-cli ping

# Check Redis configuration
docker-compose exec redis redis-cli CONFIG GET *
```

---

## ⚡ Performance Issues

### High CPU Usage

#### Symptoms
- Slow response times
- High CPU utilization
- System resource exhaustion

#### Diagnosis
```bash
# Check CPU usage
python scripts/monitoring/real_system_monitor.py --cpu

# Analyze application metrics
curl http://localhost:5000/metrics | grep cpu

# Check for memory leaks
python scripts/monitoring/real_system_monitor.py --memory
```

#### Solutions
```bash
# Optimize application settings
export FLASK_ENV=production
export FLASK_DEBUG=false

# Scale application
docker-compose up -d --scale smartcloudops-main=3

# Optimize database queries
python scripts/testing/health_check.py --performance
```

### High Memory Usage

#### Symptoms
- Out of memory errors
- Slow performance
- Service crashes

#### Diagnosis
```bash
# Check memory usage
python scripts/monitoring/real_system_monitor.py --memory

# Check for memory leaks
docker stats

# Analyze memory usage
docker-compose exec smartcloudops-main ps aux
```

#### Solutions
```bash
# Restart services
docker-compose restart smartcloudops-main

# Clear caches
docker-compose exec redis redis-cli FLUSHALL

# Optimize memory settings
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
```

### Slow Database Queries

#### Symptoms
- Slow API responses
- Database connection timeouts
- High database CPU usage

#### Diagnosis
```bash
# Check slow queries
docker-compose exec postgres psql -U cloudops -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Analyze query performance
docker-compose exec postgres psql -U cloudops -c "EXPLAIN ANALYZE SELECT * FROM your_table;"
```

#### Solutions
```bash
# Optimize database
docker-compose exec postgres psql -U cloudops -c "VACUUM ANALYZE;"

# Rebuild indexes
docker-compose exec postgres psql -U cloudops -c "REINDEX DATABASE cloudops;"

# Update statistics
docker-compose exec postgres psql -U cloudops -c "ANALYZE;"
```

---

## 🔒 Security Issues

### Authentication Failures

#### Symptoms
- Login failures
- Token validation errors
- Authorization issues

#### Diagnosis
```bash
# Check authentication logs
docker-compose logs smartcloudops-main | grep "auth"

# Test authentication endpoints
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Verify JWT configuration
python scripts/testing/verify_setup.py --security
```

#### Solutions
```bash
# Reset JWT secret
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Clear user sessions
docker-compose exec redis redis-cli FLUSHDB

# Verify security configuration
python scripts/testing/health_check.py --security
```

### Rate Limiting Issues

#### Symptoms
- API rate limit errors
- Excessive API calls
- Performance degradation

#### Diagnosis
```bash
# Check rate limiting logs
docker-compose logs smartcloudops-main | grep "rate_limit"

# Monitor API usage
curl http://localhost:5000/metrics | grep rate_limit

# Test rate limiting
for i in {1..10}; do curl http://localhost:5000/health; done
```

#### Solutions
```bash
# Adjust rate limiting settings
export RATE_LIMIT_REQUESTS=100
export RATE_LIMIT_WINDOW=60

# Clear rate limiting cache
docker-compose exec redis redis-cli FLUSHDB

# Restart application
docker-compose restart smartcloudops-main
```

---

## 🐛 Debug Commands

### Application Debugging
```bash
# Enable debug mode
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug output
python scripts/testing/health_check.py --debug

# Check configuration
python scripts/testing/verify_setup.py --verbose

# Monitor logs in real-time
docker-compose logs -f --tail=100
```

### System Debugging
```bash
# Check system resources
htop
free -h
df -h

# Check network connectivity
netstat -tulpn
ss -tulpn

# Check process status
ps aux | grep python
ps aux | grep docker
```

### Database Debugging
```bash
# Connect to database
docker-compose exec postgres psql -U cloudops cloudops

# Check database status
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres
```

### Redis Debugging
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check Redis status
docker-compose exec redis redis-cli ping

# Monitor Redis commands
docker-compose exec redis redis-cli monitor
```

---

## 🔄 Recovery Procedures

### Complete System Recovery

#### 1. Stop All Services
```bash
# Stop all services
docker-compose down

# Remove volumes (if needed)
docker-compose down -v
```

#### 2. Clean Environment
```bash
# Remove containers
docker system prune -f

# Remove unused images
docker image prune -f

# Clean up volumes
docker volume prune -f
```

#### 3. Restart Services
```bash
# Start services
docker-compose up -d

# Verify services
python scripts/testing/health_check.py

# Check all components
python scripts/testing/verify_setup.py
```

### Database Recovery

#### 1. Backup Current Data
```bash
# Create backup
docker-compose exec postgres pg_dump -U cloudops cloudops > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. Reset Database
```bash
# Stop database
docker-compose stop postgres

# Remove database volume
docker volume rm cloudops_postgres_data

# Start database
docker-compose up -d postgres

# Wait for database to be ready
sleep 30
```

#### 3. Restore Data
```bash
# Restore from backup
docker-compose exec -T postgres psql -U cloudops cloudops < backup_YYYYMMDD_HHMMSS.sql
```

### Configuration Recovery

#### 1. Reset Configuration
```bash
# Backup current config
cp .env .env.backup

# Reset to defaults
cp env.example .env

# Edit configuration
nano .env
```

#### 2. Verify Configuration
```bash
# Check configuration
python scripts/testing/verify_setup.py --env-check

# Test configuration
python scripts/testing/health_check.py
```

#### 3. Restart Services
```bash
# Restart with new configuration
docker-compose down
docker-compose up -d
```

---

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Run diagnostics** using the commands above
3. **Check logs** for error messages
4. **Verify configuration** using verification scripts
5. **Search existing issues** on GitHub

### When Reporting Issues

Include the following information:
- **Error messages** and logs
- **System information** (OS, Docker version, etc.)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Diagnostic output** from health check scripts

### Support Channels

- **Documentation**: Check comprehensive docs
- **GitHub Issues**: [Report Issues](https://github.com/TechTyphoon/smartcloudops-ai/issues)
- **GitHub Discussions**: [Ask Questions](https://github.com/TechTyphoon/smartcloudops-ai/discussions)
- **Enterprise Support**: enterprise@smartcloudops.ai

---

## 📚 Additional Resources

### Documentation
- [Installation Guide](INSTALLATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Security Guide](SECURITY.md)

### Scripts
- [Health Check Script](scripts/testing/health_check.py)
- [Setup Verification](scripts/testing/verify_setup.py)
- [Monitoring Scripts](scripts/monitoring/)
- [Deployment Scripts](scripts/deployment/)

### External Resources
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**SmartCloudOps AI v3.3.0** - Troubleshooting Guide
