#!/usr/bin/env python3
"""
Beta Testing Setup Script for SmartCloudOps AI
Sets up beta testing environment and configures testers
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import boto3

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.beta_testing import BetaTestingManager, TestingScenario, UserRole

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_aws_ses():
    """Set up AWS SES for email notifications"""
    try:
        region = os.getenv("AWS_REGION", "ap-south-1")
        ses_client = boto3.client("ses", region_name=region)

        # Check if email is verified
        sender_email = os.getenv("SENDER_EMAIL", "alerts@smartcloudops.ai")

        try:
            response = ses_client.get_send_quota()
            logger.info(
                f"✅ SES quota: {response['SentLast24Hours']}/{response['Max24HourSend']} emails sent in last 24h"
            )
        except Exception as e:
            logger.warning(f"Could not get SES quota: {e}")

        # Try to verify sender email
        try:
            ses_client.verify_email_identity(EmailAddress=sender_email)
            logger.info(f"📧 Verification email sent to {sender_email}")
            logger.info("Please check your email and click the verification link")
        except Exception as e:
            logger.info(
                f"Email {sender_email} might already be verified or verification failed: {e}"
            )

        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup SES: {e}")
        return False


def setup_aws_ssm_parameters():
    """Set up AWS SSM parameters for beta testing"""
    try:
        region = os.getenv("AWS_REGION", "ap-south-1")
        ssm_client = boto3.client("ssm", region_name=region)

        # Set admin emails parameter
        admin_emails = "dileepkumarreddy12345@gmail.com"
        try:
            ssm_client.put_parameter(
                Name="/smartcloudops/dev/admin/emails",
                Value=admin_emails,
                Type="SecureString",
                Description="Admin email addresses for notifications",
                Overwrite=True,
            )
            logger.info(f"✅ Set admin emails parameter: {admin_emails}")
        except Exception as e:
            logger.warning(f"Could not set admin emails parameter: {e}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup SSM parameters: {e}")
        return False


def setup_beta_testing_manager():
    """Set up beta testing manager and create default testers"""
    try:
        beta_manager = BetaTestingManager()

        # Check if Dileep Reddy is already configured
        dileep = beta_manager.get_tester("dileepkumarreddy12345@gmail.com")
        if dileep:
            logger.info(f"✅ Beta tester already configured: {dileep.name}")
            logger.info(f"   API Key: {dileep.api_key}")
            logger.info(f"   Scenarios: {[s.value for s in dileep.testing_scenarios]}")
        else:
            logger.info("❌ Beta tester not found, this shouldn't happen")

        # Get testing summary
        summary = beta_manager.get_testing_summary()
        logger.info(f"📊 Beta Testing Summary:")
        logger.info(f"   Total Testers: {summary['total_testers']}")
        logger.info(f"   Active Testers: {summary['active_testers']}")
        logger.info(f"   Total Sessions: {summary['total_sessions']}")
        logger.info(f"   Total Feedback: {summary['total_feedback']}")

        return beta_manager

    except Exception as e:
        logger.error(f"❌ Failed to setup beta testing manager: {e}")
        return None


def create_beta_testing_guide():
    """Create beta testing guide for Dileep Reddy"""
    try:
        guide_content = """# 🧪 SmartCloudOps AI - Beta Testing Guide

## 👋 Welcome Dileep Reddy!

You've been selected as a beta tester for SmartCloudOps AI. Here's everything you need to know:

## 🔑 Your Access Details

- **Name**: Dileep Reddy
- **Email**: dileepkumarreddy12345@gmail.com
- **Role**: Beta Tester
- **Access Level**: Full Access
- **API Key**: [Will be generated automatically]

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

### 1. Get Your API Key
```bash
# The system will generate this automatically
# Check the logs or contact the admin
```

### 2. Test API Endpoints
```bash
# Health check (no auth required)
curl http://localhost:5000/api/beta/health

# Get your status (requires API key)
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/api/beta/status

# Get available scenarios
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/api/beta/scenarios
```

### 3. Start Testing Sessions
```bash
# Start a testing session
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scenario": "cpu_monitoring"}' \
  http://localhost:5000/api/beta/session/start

# End a session
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Testing completed successfully", "metrics": {"cpu_usage": "45%"}}' \
  http://localhost:5000/api/beta/session/SESSION_ID/end
```

### 4. Submit Feedback
```bash
# Submit feedback for a scenario
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scenario": "cpu_monitoring", "feedback": "Great performance!", "rating": 5}' \
  http://localhost:5000/api/beta/feedback
```

### 5. Test Notifications
```bash
# Test email notification delivery
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
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
*Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}*
""".format(
            datetime=datetime
        )

        guide_path = project_root / "docs" / "BETA_TESTING_GUIDE.md"
        guide_path.parent.mkdir(exist_ok=True)

        with open(guide_path, "w") as f:
            f.write(guide_content)

        logger.info(f"✅ Created beta testing guide: {guide_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create testing guide: {e}")
        return False


def test_beta_api_endpoints():
    """Test beta API endpoints"""
    try:
        import requests

        base_url = "http://localhost:5000"

        # Test health endpoint (no auth required)
        try:
            response = requests.get(f"{base_url}/api/beta/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Beta API health check successful")
                data = response.json()
                logger.info(f"   Service: {data['data']['service']}")
                logger.info(f"   Status: {data['data']['status']}")
            else:
                logger.warning(
                    f"⚠️ Beta API health check failed: {response.status_code}"
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not test Beta API health: {e}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to test beta API: {e}")
        return False


def main():
    """Main setup function"""
    logger.info("🚀 Setting up SmartCloudOps AI Beta Testing Environment")
    logger.info("=" * 60)

    # Check AWS credentials
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        logger.info(f"✅ AWS credentials verified: {identity['Account']}")
    except Exception as e:
        logger.error(f"❌ AWS credentials not working: {e}")
        logger.info("Please configure AWS credentials before proceeding")
        return False

    # Setup AWS services
    logger.info("\n🔧 Setting up AWS services...")
    ses_success = setup_aws_ses()
    ssm_success = setup_aws_ssm_parameters()

    # Setup beta testing
    logger.info("\n🧪 Setting up beta testing...")
    beta_manager = setup_beta_testing_manager()

    # Create testing guide
    logger.info("\n📚 Creating testing documentation...")
    guide_success = create_beta_testing_guide()

    # Test API endpoints
    logger.info("\n🌐 Testing API endpoints...")
    api_success = test_beta_api_endpoints()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 SETUP SUMMARY")
    logger.info("=" * 60)

    if beta_manager:
        summary = beta_manager.get_testing_summary()
        logger.info(f"✅ Beta Testing Manager: READY")
        logger.info(f"   Testers: {summary['total_testers']}")
        logger.info(f"   Scenarios: {len(TestingScenario)}")

        # Show Dileep's details
        dileep = beta_manager.get_tester("dileepkumarreddy12345@gmail.com")
        if dileep:
            logger.info(f"\n👤 Beta Tester Details:")
            logger.info(f"   Name: {dileep.name}")
            logger.info(f"   Email: {dileep.email}")
            logger.info(f"   API Key: {dileep.api_key}")
            logger.info(f"   Access Level: {dileep.access_level}")
    else:
        logger.error("❌ Beta Testing Manager: FAILED")

    logger.info(
        f"\n📧 Email Notifications: {'✅ READY' if ses_success else '❌ FAILED'}"
    )
    logger.info(f"🔐 SSM Parameters: {'✅ READY' if ssm_success else '❌ FAILED'}")
    logger.info(f"📚 Testing Guide: {'✅ READY' if guide_success else '❌ FAILED'}")
    logger.info(f"🌐 API Endpoints: {'✅ READY' if api_success else '❌ FAILED'}")

    logger.info("\n🎯 NEXT STEPS:")
    logger.info("1. Check your email for SES verification")
    logger.info("2. Review the beta testing guide in docs/BETA_TESTING_GUIDE.md")
    logger.info("3. Start testing with your API key")
    logger.info("4. Submit feedback through the API")

    logger.info("\n🚀 Beta testing environment setup complete!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
