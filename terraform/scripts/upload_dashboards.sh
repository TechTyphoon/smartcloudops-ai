#!/bin/bash
# Smart CloudOps AI - Upload Advanced Dashboard Configurations
# This script uploads the advanced Grafana dashboards and configurations after deployment

set -e

MONITORING_IP=$1

if [ -z "$MONITORING_IP" ]; then
    echo "Usage: $0 <monitoring_ip>"
    echo "Example: $0 54.123.456.789"
    exit 1
fi

echo "🚀 Uploading advanced monitoring configurations..."

# Copy advanced configuration files to monitoring server
scp -i ~/.ssh/smartcloudops-ai-key.pem terraform/configs/grafana-dashboard-system-overview.json \
    ec2-user@$MONITORING_IP:/tmp/

scp -i ~/.ssh/smartcloudops-ai-key.pem terraform/configs/grafana-dashboard-prometheus-monitoring.json \
    ec2-user@$MONITORING_IP:/tmp/

scp -i ~/.ssh/smartcloudops-ai-key.pem terraform/configs/alert-rules.yml \
    ec2-user@$MONITORING_IP:/tmp/

# Install advanced configurations on the monitoring server
ssh -i ~/.ssh/smartcloudops-ai-key.pem ec2-user@$MONITORING_IP << 'EOF'
    # Copy advanced dashboards
    sudo cp /tmp/grafana-dashboard-*.json /opt/monitoring/grafana/dashboards/
    
    # Copy advanced alert rules
    sudo cp /tmp/alert-rules.yml /opt/monitoring/prometheus/config/
    
    # Restart monitoring stack to load new configurations
    cd /opt/monitoring
    docker-compose restart
    
    echo "✅ Advanced monitoring configurations installed!"
EOF

echo "🎉 Advanced monitoring stack configuration complete!"
echo "📊 Access your enhanced monitoring:"
echo "  Grafana: http://$MONITORING_IP:3001"
echo "  Advanced dashboards now available with CPU, RAM, disk monitoring"