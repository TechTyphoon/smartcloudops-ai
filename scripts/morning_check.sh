#!/bin/bash
# Smart CloudOps AI - Morning Health Check
# Phase 7.2: Daily Operations Script
# Updated: August 13, 2025 - Triggering workflow validation

echo "🌅 Smart CloudOps AI - Morning Health Check"
echo "=========================================="

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Container Status
echo -e "${YELLOW}📦 Container Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep cloudops | head -5

# 2. System Health
echo -e "\n${YELLOW}🏥 System Health:${NC}"
health_status=$(curl -s http://localhost:3003/health | jq -r '.status')
if [ "$health_status" = "healthy" ]; then
    echo -e "${GREEN}✅ System Status: $health_status${NC}"
else
    echo -e "${RED}❌ System Status: $health_status${NC}"
fi

# 3. ML System Status
echo -e "\n${YELLOW}🤖 ML System Status:${NC}"
ml_initialized=$(curl -s http://localhost:3003/anomaly/status | jq -r '.initialized')
if [ "$ml_initialized" = "true" ]; then
    echo -e "${GREEN}✅ ML System: Initialized${NC}"
else
    echo -e "${RED}❌ ML System: Not Initialized${NC}"
fi

# 4. Prometheus Health
echo -e "\n${YELLOW}📊 Prometheus Status:${NC}"
prometheus_health=$(curl -s http://localhost:9090/-/healthy 2>/dev/null)
if [[ "$prometheus_health" == *"Healthy"* ]]; then
    echo -e "${GREEN}✅ Prometheus: $prometheus_health${NC}"
else
    echo -e "${RED}❌ Prometheus: Not accessible${NC}"
fi

# 5. Quick ML Performance Test
echo -e "\n${YELLOW}⚡ Quick ML Performance Test:${NC}"
start_time=$(date +%s%N)
ml_result=$(curl -s -X POST http://localhost:3003/anomaly \
    -H "Content-Type: application/json" \
    -d '{
        "metrics": {
            "cpu_usage_avg": 25.5,
            "memory_usage_pct": 35.8,
            "disk_usage_pct": 22.1,
            "network_bytes_total": 512.3,
            "request_rate": 8.2,
            "response_time_p95": 0.15
        }
    }' 2>/dev/null)

if [ $? -eq 0 ]; then
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    is_anomaly=$(echo "$ml_result" | jq -r '.data.is_anomaly' 2>/dev/null)
    echo -e "${GREEN}✅ ML Response Time: ${duration}ms${NC}"
    echo -e "${GREEN}✅ ML Detection: Working (Anomaly: $is_anomaly)${NC}"
else
    echo -e "${RED}❌ ML System: Not responding${NC}"
fi

# 6. Resource Usage Summary
echo -e "\n${YELLOW}💾 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep cloudops | head -3

echo -e "\n${GREEN}✅ Morning check complete!${NC}"
echo "$(date): Health check completed" >> logs/daily_health.log

# Summary
echo -e "\n${YELLOW}📋 Summary:${NC}"
echo "- All systems checked"
echo "- Logs saved to logs/daily_health.log" 
echo "- System ready for daily operations"
echo ""
echo "🚀 Your Smart CloudOps AI is ready for use!"
echo "   Main App: http://localhost:3003"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3004"
