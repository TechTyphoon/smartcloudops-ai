#!/bin/bash
# Continuous Health Monitor for Smart CloudOps AI Repair Process
# Runs every 60 seconds and logs all service statuses

MONITOR_LOG="/tmp/continuous_monitor_$(date +%Y%m%d%H%M%S).log"
echo "🔍 Continuous Monitor Started: $(date)" | tee -a $MONITOR_LOG

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] === HEALTH CHECK CYCLE ===" >> $MONITOR_LOG
    
    # Test all critical endpoints
    flask_root=$(timeout 5 curl -s -o /dev/null -w '%{http_code}' http://44.253.225.44:3000/ 2>/dev/null || echo 'TIMEOUT')
    flask_health=$(timeout 5 curl -s -o /dev/null -w '%{http_code}' http://44.253.225.44:3000/health 2>/dev/null || echo 'TIMEOUT')
    flask_status=$(timeout 5 curl -s -o /dev/null -w '%{http_code}' http://44.253.225.44:3000/status 2>/dev/null || echo 'TIMEOUT')
    flask_metrics=$(timeout 5 curl -s -o /dev/null -w '%{http_code}' http://44.253.225.44:3000/metrics 2>/dev/null || echo 'TIMEOUT')
    
    prometheus=$(timeout 5 curl -s -o /dev/null -w '%{http_code}' http://54.186.188.202:9090/-/ready 2>/dev/null || echo 'TIMEOUT')
    grafana=$(timeout 5 curl -s -o /dev/null -w '%{http_code}' http://54.186.188.202:3001/api/health 2>/dev/null || echo 'TIMEOUT')
    
    # Log results
    echo "[$timestamp] Flask Root: $flask_root | Health: $flask_health | Status: $flask_status | Metrics: $flask_metrics" >> $MONITOR_LOG
    echo "[$timestamp] Prometheus: $prometheus | Grafana: $grafana" >> $MONITOR_LOG
    
    # Alert on failures (would normally send alerts in production)
    if [[ "$flask_root" != "200" ]] || [[ "$prometheus" != "200" ]]; then
        echo "[$timestamp] ⚠️  CRITICAL: Service degradation detected!" >> $MONITOR_LOG
    fi
    
    # Display last status to terminal
    echo "Monitor Status: Flask($flask_root) Prometheus($prometheus) Grafana($grafana) - Log: $MONITOR_LOG"
    
    sleep 60
done
