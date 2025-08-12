# Security Hardening Guide for Smart CloudOps AI

## 🔒 Production Security Checklist

### ✅ Critical Security Fixes Applied

#### 1. Subprocess Security (HIGH PRIORITY)
- **Fixed**: Eliminated all `shell=True` usage in subprocess calls
- **Applied**: Secure command parsing using `shlex.split()`
- **Added**: Command timeouts to prevent DoS attacks
- **Location**: All script files in `scripts/` directory

#### 2. Input Validation (HIGH PRIORITY)  
- **Added**: Comprehensive input validation for all API endpoints
- **Implemented**: XSS prevention for string inputs
- **Added**: JSON depth validation to prevent DoS attacks
- **Added**: Numeric range validation
- **Location**: `app/main.py` validation functions

#### 3. Environment Security
- **Updated**: `env.template` with security best practices
- **Added**: Production security configuration examples
- **Documented**: Secrets management using AWS SSM
- **Added**: Database SSL and connection pooling guidance

#### 4. Exception Handling
- **Fixed**: Removed dangerous `try/except/pass` blocks
- **Added**: Proper error logging instead of silent failures
- **Improved**: Error messages for debugging without information leakage

#### 5. Cryptographic Security
- **Fixed**: Replaced `random` module with `secrets` for cryptographic operations
- **Added**: Secure random selection for load testing

#### 6. Testing Security
- **Fixed**: Replaced `assert` statements with proper validation
- **Added**: Timeout handling for subprocess operations

### 🛡️ Security Monitoring & Alerting

#### Prometheus/Grafana Security Alerts
- **Created**: `configs/security-alerts.yml` with comprehensive security monitoring
- **Added**: DoS attack detection (CPU/Memory spikes)
- **Added**: Anomalous request volume alerts
- **Added**: Authentication failure monitoring
- **Added**: Database attack detection
- **Added**: Disk space monitoring (log flooding attacks)

#### Key Security Metrics
```yaml
- High CPU usage (>90% for 5+ minutes)
- High memory usage (>95% for 3+ minutes) 
- High error rate (>10 errors/sec)
- Unusual request volume (>100 req/sec)
- Multiple remediation failures
- ML anomaly spikes
- Database connection failures
- Authentication failures
```

### 🔧 Production Deployment Security

#### 1. Environment Configuration
```bash
# Production security settings
FLASK_ENV=production
FLASK_DEBUG=false
REQUIRE_APPROVAL=true
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_MINUTE=100
ENABLE_CSRF_PROTECTION=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

#### 2. Database Security
```bash
# Secure database configuration
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
```

#### 3. AWS Security Best Practices
- ✅ Use IAM roles instead of access keys
- ✅ Store secrets in AWS SSM Parameter Store
- ✅ Enable VPC security groups
- ✅ Use SSL/TLS for all communications
- ✅ Enable CloudTrail for audit logging

### 🚨 Incident Response

#### Immediate Response Actions
1. **High Security Alert**: Scale down affected services
2. **Authentication Failures**: Block suspicious IPs
3. **DoS Attacks**: Enable rate limiting and traffic shaping
4. **Database Attacks**: Review connection logs and lock accounts
5. **Anomaly Spikes**: Review ML model predictions and retrain if needed

#### Security Contact Information
- **Primary**: `security@smartcloudops.ai`
- **Emergency**: Slack channel `#security-alerts`
- **Escalation**: AWS Support (Business/Enterprise)

### 📋 Developer Security Guidelines

#### Code Security Requirements
1. **Never use `shell=True`** in subprocess calls
2. **Always validate user input** before processing
3. **Use environment variables** for secrets, never hardcode
4. **Implement rate limiting** on all public endpoints
5. **Log security events** but not sensitive data
6. **Use HTTPS** for all API communications
7. **Sanitize log output** to prevent log injection

#### Input Validation Rules
```python
# Always validate string inputs
query = validate_string_input(request.json.get('query'), max_length=5000)

# Always validate numeric inputs  
hours = validate_numeric_input(request.args.get('hours'), min_val=1, max_val=720)

# Always validate JSON structure
data = validate_json_input(request.get_json())
```

#### Security Testing
```bash
# Run security scan
bandit -r app/ scripts/ ml_models/

# Check for secrets in code
git secrets --scan

# Dependency vulnerability scan  
safety check

# Container security scan
trivy image smartcloudops-ai:latest
```

### 🔍 Security Monitoring Tools

#### Integrated Security Tools
- **Bandit**: Static security analysis for Python
- **Trivy**: Container vulnerability scanning
- **Safety**: Python dependency vulnerability checking
- **Prometheus**: Real-time security metrics
- **Grafana**: Security dashboard and alerting

#### Security Metrics Dashboard
- Request rate and error rate
- Authentication success/failure rates
- ML anomaly detection trends
- Resource usage patterns
- Failed remediation attempts
- Database connection health

### 📚 Security Training Resources

#### Required Reading
1. [OWASP Top 10](https://owasp.org/www-project-top-ten/)
2. [AWS Security Best Practices](https://aws.amazon.com/security/security-learning/)
3. [Python Security Guidelines](https://python-security.readthedocs.io/)
4. [Container Security](https://kubernetes.io/docs/concepts/security/)

#### Internal Security Policies
- Code review requirements (2 approvers for security-sensitive changes)
- Vulnerability disclosure process
- Incident response procedures
- Access control and privilege management

### 🔄 Security Update Process

#### Regular Security Maintenance
1. **Weekly**: Dependency vulnerability scans
2. **Monthly**: Security configuration reviews
3. **Quarterly**: Penetration testing
4. **Annually**: Security architecture review

#### Security Patch Management
1. **Critical**: Apply within 24 hours
2. **High**: Apply within 7 days  
3. **Medium**: Apply within 30 days
4. **Low**: Apply in next maintenance window

### 📞 Emergency Contacts

- **Security Team**: security@smartcloudops.ai
- **DevOps Team**: devops@smartcloudops.ai  
- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **AWS Support**: https://console.aws.amazon.com/support/

---

*Last Updated: 2025-01-11*  
*Version: 1.0*  
*Classification: Internal Use*
