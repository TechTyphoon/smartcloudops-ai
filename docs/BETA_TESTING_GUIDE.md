# 🧪 SmartCloudOps AI - Beta Testing Guide

## 👋 Welcome Dileep Reddy!

You've been selected as a beta tester for SmartCloudOps AI. Here's everything you need to know:

## 🔑 Your Access Details

- **Name**: Dileep Reddy
- **Email**: dileepkumarreddy12345@gmail.com
- **Role**: Beta Tester
- **Access Level**: Full Access
- **API Key**: `_ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM`

## 🎯 Testing Scenarios

You have access to test ALL of these scenarios:

### 1. CPU Monitoring
- Monitor CPU usage and detect anomalies
- Test alert thresholds and notifications

### 2. ML Anomaly Detection
- Test machine learning models
- Verify anomaly detection accuracy

### 3. ChatOps Queries
- Test AI-powered ChatOps interface
- Ask questions about system status

### 4. Auto-Remediation
- Test automatic problem resolution
- Verify safety mechanisms

### 5. Notification Delivery
- Test email notifications
- Verify alert delivery

### 6. Performance Load
- Test system under load
- Verify scalability

### 7. Security Features
- Test access controls
- Verify security measures

### 8. Integration Tests
- Test system workflows
- Verify component integration

## 🚀 Getting Started

### 1. Your API Key
```
_ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM
```

### 2. Test API Endpoints
```bash
# Health check (no auth required)
curl http://localhost:5000/api/beta/health

# Get your status (requires API key)
curl -H "X-API-Key: _ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM" \
  http://localhost:5000/api/beta/status

# Get available scenarios
curl -H "X-API-Key: _ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM" \
  http://localhost:5000/api/beta/scenarios
```

### 3. Start Testing Sessions
```bash
# Start a testing session
curl -X POST -H "X-API-Key: _ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM" \
  -H "Content-Type: application/json" \
  -d '{"scenario": "cpu_monitoring"}' \
  http://localhost:5000/api/beta/session/start

# End a session
curl -X POST -H "X-API-Key: _ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Testing completed successfully", "metrics": {"cpu_usage": "45%"}}' \
  http://localhost:5000/api/beta/session/SESSION_ID/end
```

### 4. Submit Feedback
```bash
# Submit feedback for a scenario
curl -X POST -H "X-API-Key: _ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM" \
  -H "Content-Type: application/json" \
  -d '{"scenario": "cpu_monitoring", "feedback": "Great performance!", "rating": 5}' \
  http://localhost:5000/api/beta/feedback
```

### 5. Test Notifications
```bash
# Test email notification delivery
curl -X POST -H "X-API-Key: _ik8pCZvU_8p2VLNhkRg5ejHC9MH6ahd8SpIqxNZtuM" \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing notification system", "level": "info"}' \
  http://localhost:5000/api/beta/test/notification
```

## 📊 Monitoring Your Progress

- **Sessions**: Track all your testing sessions
- **Feedback**: Submit ratings and comments
- **Metrics**: Record performance data
- **Activity**: Monitor your testing activity

## 🎯 Testing Goals

1. **Functionality**: Ensure all features work correctly
2. **Performance**: Test under various load conditions
3. **Usability**: Provide feedback on user experience
4. **Reliability**: Identify any bugs or issues
5. **Security**: Verify access controls work properly

## 📝 Feedback Guidelines

- **Be Specific**: Describe exactly what you tested
- **Include Context**: Mention your environment and setup
- **Rate Honestly**: Use 1-5 scale for ratings
- **Suggest Improvements**: Share ideas for enhancement
- **Report Bugs**: Document any issues you find

## 🆘 Need Help?

- Check the API documentation
- Review error messages carefully
- Contact the development team
- Check system logs for details

## 🎉 Thank You!

Your feedback is invaluable in making SmartCloudOps AI production-ready!

---
*Generated on: 2025-08-10 13:55:43 UTC* 