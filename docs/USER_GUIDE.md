# 📖 SmartCloudOps AI - User Guide

**Complete user guide for cloud operations automation and anomaly management**

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Dashboard Overview](#dashboard-overview)
- [Anomaly Management](#anomaly-management)
- [Remediation Actions](#remediation-actions)
- [ChatOps Integration](#chatops-integration)
- [Settings & Configuration](#settings--configuration)
- [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### First Login

1. **Access the Application**
   - Open your browser and navigate to: `https://smartcloudops.ai`
   - You'll see the login page

2. **Login Process**
   - Enter your email address and password
   - Click "Sign In" or press Enter
   - If you have 2FA enabled, enter your verification code

3. **Password Reset** (if needed)
   - Click "Forgot Password?" on the login page
   - Enter your email address
   - Check your email for reset instructions
   - Follow the link to create a new password

### Initial Setup Wizard

After your first login, you'll be guided through a setup wizard:

1. **Profile Setup**
   - Upload a profile picture (optional)
   - Set your display name
   - Configure notification preferences

2. **Team Configuration**
   - Join existing teams or create new ones
   - Set team roles and permissions
   - Configure team notification channels

3. **System Integration**
   - Connect cloud provider accounts (AWS, Azure, GCP)
   - Configure monitoring data sources
   - Set up Slack/Teams integration

4. **Alert Preferences**
   - Choose which types of alerts you want to receive
   - Set severity levels for notifications
   - Configure quiet hours and escalation rules

## 📊 Dashboard Overview

### Main Dashboard

The main dashboard provides an at-a-glance view of your infrastructure health:

#### Key Widgets

1. **System Health Status**
   - Overall system health indicator (Green/Yellow/Red)
   - Shows critical issues requiring immediate attention
   - Click to drill down into specific problem areas

2. **Active Anomalies**
   - Number of currently active anomalies
   - Breakdown by severity (Critical, High, Medium, Low)
   - Trend chart showing anomalies over time

3. **Recent Remediation Actions**
   - List of latest automated actions taken
   - Success/failure status
   - Time stamps and affected resources

4. **Performance Metrics**
   - CPU, Memory, Disk, and Network utilization
   - Real-time graphs with configurable time ranges
   - Comparison with baseline performance

5. **Alert Summary**
   - Unread notifications count
   - Recent alert activity
   - Quick access to acknowledge alerts

#### Navigation Menu

- **🏠 Dashboard**: Main overview page
- **⚠️ Anomalies**: Detailed anomaly management
- **🔧 Remediation**: Remediation history and configuration
- **📊 Monitoring**: Detailed monitoring and metrics
- **📈 Reports**: Analytics and trend reports
- **⚙️ Settings**: System and user configuration

### Customizing Your Dashboard

1. **Widget Arrangement**
   - Drag and drop widgets to rearrange
   - Resize widgets by dragging corners
   - Hide/show widgets using the view menu

2. **Time Range Selection**
   - Use the time picker in the top right
   - Options: Last 1 hour, 6 hours, 24 hours, 7 days, 30 days
   - Custom range picker for specific periods

3. **Refresh Settings**
   - Auto-refresh intervals: 30s, 1m, 5m, 15m
   - Manual refresh using the refresh button
   - Real-time updates via WebSocket (when available)

## ⚠️ Anomaly Management

### Understanding Anomalies

An anomaly is detected when system metrics deviate significantly from normal patterns:

#### Severity Levels
- **🔴 Critical**: Immediate action required (system down, data loss risk)
- **🟠 High**: Urgent attention needed (performance severely impacted)
- **🟡 Medium**: Should be addressed soon (degraded performance)
- **🔵 Low**: Monitor closely (minor deviation from normal)

#### Anomaly Types
- **Performance**: CPU, memory, disk, network usage spikes
- **Application**: Error rates, response times, throughput issues
- **Infrastructure**: Service availability, connectivity problems
- **Security**: Unusual access patterns, potential threats

### Anomaly List View

The anomalies page shows all detected anomalies with filtering and sorting options:

#### Filtering Options
- **Severity**: Filter by one or more severity levels
- **Time Range**: Show anomalies from specific time periods
- **Status**: Active, Acknowledged, Resolved, Suppressed
- **Type**: Performance, Application, Infrastructure, Security
- **Source**: Which monitoring system detected the anomaly

#### Anomaly Details
Click on any anomaly to view detailed information:

- **Metric Information**
  - Metric name and current value
  - Normal range and threshold breached
  - Deviation percentage from baseline

- **Timeline**
  - When the anomaly was first detected
  - Duration and current status
  - Related events and correlations

- **Impact Assessment**
  - Affected resources and services
  - User impact estimation
  - Business criticality score

- **Root Cause Analysis**
  - Potential causes based on historical data
  - Correlated events and anomalies
  - Suggested investigation steps

### Taking Action on Anomalies

#### Acknowledge Anomaly
- Click the "Acknowledge" button to mark as reviewed
- Add optional notes about your investigation
- Acknowledged anomalies are tracked but not actively alerted

#### Suppress Anomaly
- Use "Suppress" for known issues or planned maintenance
- Set suppression duration (30 minutes to 7 days)
- Add reason for suppression for team visibility

#### Create Remediation
- Click "Create Remediation" to trigger automated fixes
- Choose from predefined remediation actions
- Review and approve actions before execution

#### Manual Investigation
- Use the "Investigate" button to gather more data
- Access related logs, metrics, and system information
- Document findings in the anomaly notes

### Bulk Operations

Select multiple anomalies using checkboxes to perform bulk actions:

- **Bulk Acknowledge**: Mark multiple anomalies as reviewed
- **Bulk Suppress**: Suppress multiple related anomalies
- **Export Data**: Download anomaly data for external analysis
- **Create Incident**: Group related anomalies into an incident

## 🔧 Remediation Actions

### Understanding Remediation

Remediation actions are automated responses to detected anomalies:

#### Types of Actions
1. **Service Management**
   - Restart services or applications
   - Reload configurations
   - Clear caches or temporary files

2. **Resource Scaling**
   - Scale up/down compute resources
   - Add/remove instances
   - Adjust resource allocations

3. **Network Actions**
   - Restart network services
   - Update routing tables
   - Reset connections

4. **Maintenance Tasks**
   - Clean up disk space
   - Archive old logs
   - Optimize databases

### Viewing Remediation History

The remediation page shows all automated actions taken:

#### Action Details
- **Action Type**: What type of remediation was performed
- **Target**: Which resources were affected
- **Trigger**: The anomaly that caused the action
- **Status**: Success, Failed, In Progress, Cancelled
- **Execution Time**: When the action was performed
- **Duration**: How long the action took
- **Results**: Outcome and any error messages

#### Filtering and Search
- Filter by action type, status, or time range
- Search by resource name or action details
- Sort by execution time, duration, or status

### Configuring Remediation Rules

#### Access Rule Configuration
1. Go to **Settings** → **Remediation Rules**
2. Click "Add New Rule" or edit existing rules
3. Configure rule parameters

#### Rule Components
1. **Trigger Conditions**
   - Anomaly type and severity
   - Affected resource types
   - Time-based conditions

2. **Safety Checks**
   - Resource health requirements
   - Maintenance windows
   - Approval requirements

3. **Action Definition**
   - Specific action to perform
   - Parameters and options
   - Rollback procedures

4. **Notifications**
   - Who to notify before/after action
   - Success and failure notifications
   - Escalation procedures

### Manual Remediation

#### Triggering Manual Actions
1. Navigate to an anomaly or use the Remediation page
2. Click "Create Remediation Action"
3. Select the appropriate action type
4. Configure action parameters
5. Review safety checks and approvals
6. Execute the action

#### Action Approval Process
For critical actions, approval may be required:
1. Action is submitted for approval
2. Designated approvers receive notifications
3. Approvers review action details and safety checks
4. Action is approved or rejected with comments
5. If approved, action executes automatically

### Safety Features

#### Pre-execution Checks
- Resource health verification
- Dependency impact analysis
- Concurrent action prevention
- Maintenance window validation

#### Rollback Capabilities
- Automatic rollback on failure
- Manual rollback options
- Rollback procedures documentation
- Impact assessment before rollback

## 💬 ChatOps Integration

### Slack Integration

#### Initial Setup
1. Go to **Settings** → **Integrations** → **Slack**
2. Click "Connect to Slack"
3. Authorize the SmartCloudOps AI bot
4. Choose which channels to monitor
5. Configure notification preferences

#### Using Slack Commands
```
# Get system status
@smartcloudops status

# List active anomalies
@smartcloudops anomalies

# Check specific service
@smartcloudops check service web-app

# Acknowledge anomaly
@smartcloudops ack anomaly-12345

# Get help
@smartcloudops help
```

#### Slack Notifications
You'll receive notifications for:
- New critical anomalies
- Remediation action results
- System status changes
- Approval requests

### Microsoft Teams Integration

#### Setup Process
1. Go to **Settings** → **Integrations** → **Teams**
2. Install the SmartCloudOps AI app from Teams store
3. Add the bot to your team channels
4. Configure notification settings

#### Teams Commands
Similar to Slack, use `@SmartCloudOps` followed by commands:
- `status` - System overview
- `anomalies` - List current issues
- `help` - Command reference

### Natural Language Queries

The AI assistant understands natural language:

```
"Show me CPU anomalies from the last hour"
"What's the status of the web-app service?"
"Restart the database service"
"Are there any critical issues right now?"
```

## ⚙️ Settings & Configuration

### User Settings

#### Profile Management
1. Go to **Settings** → **Profile**
2. Update personal information:
   - Display name and email
   - Profile picture
   - Contact preferences
   - Language and timezone

#### Notification Preferences
Configure how and when you receive notifications:

1. **Email Notifications**
   - Critical alerts: Immediate email
   - Daily summary: Morning digest
   - Weekly reports: Performance summary

2. **In-App Notifications**
   - Real-time alerts
   - Toast notifications
   - Badge counts

3. **Mobile Push** (if mobile app is installed)
   - Critical alerts only
   - All notifications
   - Disabled

#### Security Settings
- **Password Management**: Change password, password strength
- **Two-Factor Authentication**: Enable/disable 2FA
- **Session Management**: View active sessions, logout from all devices
- **API Keys**: Generate and manage personal API keys

### Team Settings

#### Team Management (Admin Only)
1. **Member Management**
   - Add/remove team members
   - Assign roles and permissions
   - Configure team hierarchy

2. **Role Configuration**
   - **Admin**: Full system access
   - **Operator**: View and manage anomalies/remediation
   - **Viewer**: Read-only access
   - **Custom**: Define specific permissions

#### Integration Settings
- **Cloud Providers**: Connect AWS, Azure, GCP accounts
- **Monitoring Tools**: Integrate Prometheus, Datadog, New Relic
- **Communication**: Setup Slack, Teams, email settings
- **Webhooks**: Configure custom webhook endpoints

### System Configuration

#### Anomaly Detection Settings
1. **Sensitivity Levels**
   - Conservative: Fewer false positives
   - Balanced: Standard detection
   - Aggressive: Catch more anomalies

2. **Custom Thresholds**
   - Define specific thresholds for metrics
   - Set baseline calculation periods
   - Configure seasonal adjustments

#### Remediation Configuration
1. **Safety Settings**
   - Require approval for critical actions
   - Define maintenance windows
   - Set concurrent action limits

2. **Default Actions**
   - Map anomaly types to remediation actions
   - Configure retry attempts and timeouts
   - Set rollback procedures

## 🔍 Troubleshooting

### Common Issues

#### Cannot Login
**Problem**: Login page shows error or won't accept credentials

**Solutions**:
1. Check if Caps Lock is on
2. Try password reset if you're unsure of password
3. Clear browser cache and cookies
4. Try incognito/private browsing mode
5. Contact your admin if account might be locked

#### Dashboard Not Loading
**Problem**: Dashboard appears blank or shows loading spinner indefinitely

**Solutions**:
1. Check internet connection
2. Refresh the page (Ctrl+F5 or Cmd+R)
3. Try a different browser
4. Disable browser extensions temporarily
5. Check if the service is down on status page

#### Notifications Not Working
**Problem**: Not receiving expected alerts or notifications

**Solutions**:
1. Check notification settings in **Settings** → **Notifications**
2. Verify email address is correct and inbox isn't full
3. Check spam/junk folder for emails
4. For Slack/Teams, verify bot is added to correct channels
5. Test notifications using the "Send Test" button

#### Anomalies Not Appearing
**Problem**: Expecting anomalies but none are shown

**Solutions**:
1. Check time range filter settings
2. Verify data sources are connected and sending data
3. Review anomaly detection sensitivity settings
4. Check if anomalies are being suppressed
5. Verify you have permissions to view anomalies

### Performance Issues

#### Slow Page Loading
1. Check your internet connection speed
2. Try using a wired connection instead of WiFi
3. Close unnecessary browser tabs
4. Clear browser cache
5. Contact support if issue persists

#### Dashboard Timing Out
1. Increase the browser timeout setting
2. Check for browser extensions blocking requests
3. Try accessing during off-peak hours
4. Use a different network if possible

### Getting Help

#### In-App Help
- Look for the "?" icon in the top navigation
- Use the help search to find specific topics
- Access guided tutorials for complex features

#### Documentation
- Complete documentation available at: `docs.smartcloudops.ai`
- API reference for developers
- Video tutorials and training materials

#### Support Channels
1. **Help Desk**: support@smartcloudops.ai
2. **Community Forum**: community.smartcloudops.ai
3. **Live Chat**: Available during business hours
4. **Emergency Support**: For critical issues (24/7)

#### Feedback and Feature Requests
- Use the feedback button in the app
- Submit feature requests through the community forum
- Vote on existing feature requests
- Contact your customer success manager

---

## 📱 Mobile App (Coming Soon)

### Features
- View critical alerts and system status
- Acknowledge anomalies on the go
- Receive push notifications
- Basic remediation actions
- Offline capability for viewing recent data

### Download
- iOS: App Store (available Q2 2024)
- Android: Google Play Store (available Q2 2024)

---

## 📚 Additional Resources

### Training Materials
- **Getting Started Video**: 15-minute overview
- **Advanced Features Webinar**: Monthly live sessions
- **Best Practices Guide**: Optimization recommendations
- **Use Case Examples**: Real-world implementation stories

### Community
- **User Community**: Share experiences and tips
- **Feature Requests**: Suggest new functionality
- **Bug Reports**: Report issues and track fixes
- **Knowledge Base**: Searchable help articles

---

*For additional support, please contact our support team at support@smartcloudops.ai or visit our help center at help.smartcloudops.ai*
