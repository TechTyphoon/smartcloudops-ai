# Personal Usage Guide - Smart CloudOps AI

**Phase 7.2**: Personal Testing & Daily Operations  
**Status**: Ready for Personal Use  
**System Health**: All Components Operational ✅  

## 🚀 Quick Start for Daily Use

### Morning Routine
```bash
# Run daily health check
./scripts/morning_check.sh

# Check system dashboard
curl -s http://localhost:3003/health | jq
```

### System Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Application** | http://localhost:3003 | Core API and health checks |
| **Grafana Dashboard** | http://localhost:3001 | System monitoring and metrics |
| **Prometheus** | http://localhost:9090 | Raw metrics and queries |
| **ML Anomaly Detection** | http://localhost:3003/api/ml/detect | AI-powered anomaly detection |

**Login Credentials**:
- **Grafana**: admin / admin (first login will prompt to change)

## � Daily Operations Workflow

### 1. System Health Check (2 minutes)
```bash
# Comprehensive morning check
./scripts/morning_check.sh

# Quick status only
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 2. Monitor Performance (5 minutes)
- Open Grafana: http://localhost:3001
- Check "Smart CloudOps AI Overview" dashboard
- Review key metrics:
  - System CPU/Memory usage
  - ML model performance
  - API response times
  - Container health

### 3. Test ML Anomaly Detection (3 minutes)
```bash
# Test normal data
curl -X POST http://localhost:3003/api/ml/detect \
  -H "Content-Type: application/json" \
  -d '{"cpu_usage": 45.0, "memory_usage": 60.0, "disk_io": 100.5}'

# Test anomalous data
curl -X POST http://localhost:3003/api/ml/detect \
  -H "Content-Type: application/json" \
## 🎯 Common Use Cases

### Use Case 1: Infrastructure Monitoring
**Scenario**: Daily infrastructure health check  
**Steps**:
1. Run `./scripts/morning_check.sh`
2. Review Grafana dashboard
3. Check for any alerts or anomalies
4. Document any issues

### Use Case 2: Anomaly Detection Testing
**Scenario**: Validate ML model accuracy  
**Steps**:
1. Send test data via API
2. Compare results with expected outcomes
3. Review model performance metrics
4. Log accuracy observations

### Use Case 3: Performance Analysis
**Scenario**: Analyze system performance trends  
**Steps**:
1. Access Prometheus: http://localhost:9090
2. Run custom queries for specific metrics
3. Export data for analysis
4. Generate performance reports

### Use Case 4: API Development Testing
**Scenario**: Test new API endpoints  
**Steps**:
1. Use `/health` endpoint for basic connectivity
2. Test `/metrics` for Prometheus integration
3. Validate `/api/ml/*` endpoints for ML features
4. Check response times and accuracy

## 📝 Feedback Collection

### Daily Feedback (5 minutes)
```bash
# Interactive feedback collection
python scripts/collect_feedback.py
# Select option 1 for daily feedback
```

### Weekly Feedback (10 minutes)
```bash
# Comprehensive weekly feedback
python scripts/collect_feedback.py
# Select option 2 for weekly feedback
```

## 🛠️ Maintenance Tasks

### Weekly Maintenance (15 minutes)
```bash
# Update system and clear logs
docker system prune -f
docker-compose down && docker-compose up -d

# Check for updates
git pull origin main
pip install -r requirements.txt --upgrade
```

### Monthly Deep Check (30 minutes)
1. Review all feedback reports
2. Analyze performance trends
3. Update ML model if needed
4. Plan system improvements
5. Document lessons learned

## 🚨 Troubleshooting Guide

### Issue: Containers Not Starting
```bash
# Check container logs
docker-compose logs

# Restart specific service
docker-compose restart smartcloudops-app

# Full system restart
docker-compose down && docker-compose up -d
```

### Issue: ML Model Not Responding
```bash
# Check ML endpoint
curl -v http://localhost:3003/api/ml/health

# Review application logs
docker logs smartcloudops-app

# Restart application
docker-compose restart smartcloudops-app
```

### Issue: Grafana Dashboard Not Loading
```bash
# Check Grafana status
docker logs smartcloudops-grafana

# Reset Grafana data (if needed)
docker-compose down
docker volume rm cloudops_grafana-data
docker-compose up -d
```

## 📈 Performance Expectations

### System Response Times
- **Health Check**: < 100ms
- **ML Anomaly Detection**: < 150ms
- **Metrics Endpoint**: < 50ms
- **Dashboard Load**: < 2 seconds

### Resource Usage (Normal Operation)
- **CPU Usage**: < 5% average
- **Memory Usage**: < 1GB total
- **Disk I/O**: < 50MB/s
- **Network**: < 10MB/s

### ML Model Performance
- **Accuracy**: > 95% for known patterns
- **False Positive Rate**: < 5%
- **Response Time**: < 100ms
- **Training Data**: 1000+ samples

## 🎓 Learning Opportunities

### Week 1: Basic Operations
- Master daily health checks
- Understand all endpoints
- Learn Grafana navigation
- Test ML anomaly detection

### Week 2: Advanced Monitoring
- Create custom Grafana dashboards
- Write Prometheus queries
- Analyze performance trends
- Optimize system settings

### Week 3: Deep Integration
- Integrate with personal infrastructure
- Develop custom monitoring scripts
- Create automated alerts
- Build performance reports

### Week 4: Optimization & Planning
- Analyze usage patterns
- Optimize ML model
- Plan feature additions
- Prepare for domain deployment

## 📋 Daily Checklist

### Morning (5 minutes)
- [ ] Run health check script
- [ ] Check all containers are running
- [ ] Review Grafana dashboard
- [ ] Test ML anomaly detection
- [ ] Note any issues

### Evening (3 minutes)
- [ ] Check system performance metrics
- [ ] Review any alerts or warnings
- [ ] Log daily usage patterns
- [ ] Plan tomorrow's testing focus

### Weekly (15 minutes)
- [ ] Complete weekly feedback collection
- [ ] Review performance trends
- [ ] Update system if needed
- [ ] Plan next week's focus areas
- [ ] Document lessons learned

## 🎯 Success Metrics

### Technical Metrics
- **Uptime**: > 99% daily
- **Response Time**: < 100ms average
- **Error Rate**: < 1%
- **ML Accuracy**: > 95%

### Personal Metrics
- **Daily Usage**: Consistent interaction
- **Satisfaction Score**: > 8/10
- **Feature Adoption**: Using all major features
- **Learning Progress**: Weekly skill advancement

---

**Remember**: This is your personal testing environment. Experiment freely, break things if needed, and learn from every interaction. The goal is to become completely comfortable with the system before domain deployment.

**Support**: All scripts and documentation are in the `/scripts/` and `/docs/` directories. Review `BETA_TESTING_REPORT.md` for technical details.

- ✅ **100% Success Rate** on all functionality tests
- ✅ **Grade A Performance** (64.51ms average ML response)
- ✅ **Stable Infrastructure** with healthy containers
- ✅ **Security Validated** with proper input handling

**Start using it today** for your DevOps tasks and infrastructure monitoring!

---

**Next Phase**: When you're ready, we can proceed with Phase 7.3 (Final Wrap-up) and prepare for domain deployment or Phase 8 (Database & Authentication) for multi-user capabilities.
