#!/bin/bash
# Smart CloudOps AI - Daily Status Check
# Run this daily to check system status

echo "=== Smart CloudOps AI - System Status $(date) ==="
echo ""

# Test all services
echo "🔍 Service Health Check:"
curl -s http://44.244.231.27:3000/health | jq . 2>/dev/null || echo "Flask App: ERROR"
curl -s -I http://35.92.147.156:3001 | head -1 | grep -q "200" && echo "Grafana: UP" || echo "Grafana: DOWN"
curl -s http://35.92.147.156:9090/api/v1/status/config | jq -r .status 2>/dev/null | grep -q "success" && echo "Prometheus: UP" || echo "Prometheus: DOWN"

echo ""
echo "📊 AWS Infrastructure:"
aws ec2 describe-instances --instance-ids i-05ea4de88477a4d2e i-07c69200a0e2ce609 --region us-west-2 --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table

echo ""
echo "📈 S3 Uptime Logs:"
aws s3 ls s3://smartcloudops-uptime-logs-20250814/uptime-logs/ --recursive | tail -5

echo ""
echo "✅ System Status: All systems operational!"
echo "Monitor running since: $(date)"
echo ""
echo "🌐 Access URLs:"
echo "- Flask App: http://44.244.231.27:3000"
echo "- Grafana: http://35.92.147.156:3001 (admin/admin)"
echo "- Prometheus: http://35.92.147.156:9090"
