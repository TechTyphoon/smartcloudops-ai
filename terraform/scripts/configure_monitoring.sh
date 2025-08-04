#!/bin/bash
# Smart CloudOps AI - Post-deployment Monitoring Configuration
# This script configures the monitoring stack after EC2 instances are deployed

set -e

# Get instance IPs from Terraform outputs
MONITORING_IP=$1
APPLICATION_IP=$2

if [ -z "$MONITORING_IP" ] || [ -z "$APPLICATION_IP" ]; then
    echo "Usage: $0 <monitoring_ip> <application_ip>"
    echo "Example: $0 54.123.456.789 54.987.654.321"
    exit 1
fi

echo "Configuring monitoring stack..."
echo "Monitoring Server: $MONITORING_IP"
echo "Application Server: $APPLICATION_IP"

# Update Prometheus configuration with actual IPs
ssh -i ~/.ssh/smartcloudops-ai-key.pem ec2-user@$MONITORING_IP << EOF
    # Update Prometheus configuration
    sudo sed -i "s/APPLICATION_SERVER_IP/$APPLICATION_IP/g" /opt/monitoring/prometheus/config/prometheus.yml
    
    # Restart monitoring stack
    cd /opt/monitoring
    docker-compose down
    docker-compose up -d
    
    echo "Monitoring stack updated with application server IP: $APPLICATION_IP"
EOF

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Verify services are running
echo "Verifying services..."

# Check Prometheus
if curl -s "http://$MONITORING_IP:9090/api/v1/targets" > /dev/null; then
    echo "✅ Prometheus is running and accessible"
else
    echo "❌ Prometheus is not accessible"
fi

# Check Grafana
if curl -s "http://$MONITORING_IP:3001/api/health" > /dev/null; then
    echo "✅ Grafana is running and accessible"
else
    echo "❌ Grafana is not accessible"
fi

# Check Node Exporter on monitoring server
if curl -s "http://$MONITORING_IP:9100/metrics" > /dev/null; then
    echo "✅ Node Exporter (monitoring) is running"
else
    echo "❌ Node Exporter (monitoring) is not accessible"
fi

# Check Node Exporter on application server
if curl -s "http://$APPLICATION_IP:9100/metrics" > /dev/null; then
    echo "✅ Node Exporter (application) is running"
else
    echo "❌ Node Exporter (application) is not accessible"
fi

# Check Flask application
if curl -s "http://$APPLICATION_IP:3000/status" > /dev/null; then
    echo "✅ Flask application is running"
else
    echo "❌ Flask application is not accessible"
fi

echo ""
echo "🎉 Monitoring Configuration Complete!"
echo ""
echo "📊 Access your monitoring services:"
echo "  Prometheus: http://$MONITORING_IP:9090"
echo "  Grafana:    http://$MONITORING_IP:3001 (admin/admin)"
echo "  Flask App:  http://$APPLICATION_IP:3000"
echo ""
echo "📋 Next steps:"
echo "1. Open Grafana and verify dashboards are loaded"
echo "2. Check Prometheus targets are all 'UP'"
echo "3. Explore the pre-configured dashboards"
echo "4. Consider setting up alerting rules"