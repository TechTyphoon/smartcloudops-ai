#!/bin/bash

# SmartCloudOps AI - Demo Scenario Generator
# Creates realistic anomalies and scenarios for demonstrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="http://localhost:5000"

echo -e "${BLUE}🎭 SmartCloudOps AI - Demo Scenario Generator${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if API is available
if ! curl -f $API_URL/health > /dev/null 2>&1; then
    echo -e "${RED}❌ API is not available at $API_URL${NC}"
    echo -e "${YELLOW}Please start the demo environment first:${NC}"
    echo -e "${BLUE}  ./demo/scripts/quick-demo.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API is available${NC}"
echo ""

# Function to create anomaly
create_anomaly() {
    local metric_name=$1
    local value=$2
    local threshold=$3
    local severity=$4
    local description=$5
    
    curl -s -X POST "$API_URL/api/anomalies/" \
        -H "Content-Type: application/json" \
        -d "{
            \"metric_name\": \"$metric_name\",
            \"value\": $value,
            \"threshold\": $threshold,
            \"severity\": \"$severity\",
            \"description\": \"$description\",
            \"timestamp\": \"$(date -Iseconds)\",
            \"status\": \"active\",
            \"source\": \"demo_generator\"
        }" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ Created $severity severity anomaly: $metric_name ($value > $threshold)${NC}"
    else
        echo -e "${RED}  ❌ Failed to create anomaly: $metric_name${NC}"
    fi
}

# Function to wait with progress
wait_with_progress() {
    local seconds=$1
    local message=$2
    
    echo -e "${YELLOW}$message${NC}"
    for i in $(seq 1 $seconds); do
        echo -n "."
        sleep 1
    done
    echo ""
}

# Scenario 1: CPU Spike Simulation
echo -e "${YELLOW}🚀 Scenario 1: CPU Spike Simulation${NC}"
echo -e "Simulating a high CPU usage anomaly..."

create_anomaly "cpu_usage" 94.5 80.0 "critical" "Critical CPU spike detected on web-server-1"
create_anomaly "cpu_usage" 88.2 80.0 "high" "High CPU usage on web-server-2"
create_anomaly "load_average" 8.5 5.0 "high" "High system load average"

wait_with_progress 3 "Waiting for anomaly processing"

# Scenario 2: Memory Leak Simulation
echo -e "${YELLOW}🧠 Scenario 2: Memory Leak Simulation${NC}"
echo -e "Simulating memory exhaustion..."

create_anomaly "memory_usage" 91.8 85.0 "critical" "Memory usage critically high on app-server-1"
create_anomaly "memory_usage" 87.3 85.0 "medium" "Memory usage trending up on app-server-2"
create_anomaly "swap_usage" 45.2 30.0 "high" "High swap usage indicates memory pressure"

wait_with_progress 2 "Processing memory anomalies"

# Scenario 3: Disk Space Issues
echo -e "${YELLOW}💾 Scenario 3: Disk Space Issues${NC}"
echo -e "Simulating disk space problems..."

create_anomaly "disk_usage" 96.7 90.0 "critical" "Disk space critically low on /var/log"
create_anomaly "disk_usage" 92.1 90.0 "high" "Disk usage high on /home partition"
create_anomaly "inode_usage" 89.4 85.0 "medium" "High inode usage on filesystem"

wait_with_progress 2 "Processing disk anomalies"

# Scenario 4: Network Performance Issues
echo -e "${YELLOW}🌐 Scenario 4: Network Performance Issues${NC}"
echo -e "Simulating network problems..."

create_anomaly "network_latency" 245.7 100.0 "high" "High network latency to database server"
create_anomaly "packet_loss" 3.2 1.0 "medium" "Packet loss detected on primary interface"
create_anomaly "bandwidth_usage" 89.5 80.0 "medium" "High bandwidth utilization"

wait_with_progress 2 "Processing network anomalies"

# Scenario 5: Application Performance Degradation
echo -e "${YELLOW}📱 Scenario 5: Application Performance Issues${NC}"
echo -e "Simulating application problems..."

create_anomaly "response_time" 2847 1000 "high" "High response time on /api/users endpoint"
create_anomaly "error_rate" 8.3 5.0 "medium" "Elevated error rate on checkout service"
create_anomaly "queue_length" 1247 500 "medium" "High job queue length in background processor"

wait_with_progress 2 "Processing application anomalies"

# Scenario 6: Database Performance Issues
echo -e "${YELLOW}🗄️ Scenario 6: Database Performance Issues${NC}"
echo -e "Simulating database problems..."

create_anomaly "db_connections" 187 150 "high" "High database connection count"
create_anomaly "query_time" 3421 2000 "medium" "Slow query performance detected"
create_anomaly "deadlocks" 5 2 "medium" "Database deadlocks increasing"

wait_with_progress 2 "Processing database anomalies"

# Scenario 7: Security Anomalies
echo -e "${YELLOW}🔒 Scenario 7: Security Anomalies${NC}"
echo -e "Simulating security events..."

create_anomaly "failed_logins" 47 20 "high" "Unusual number of failed login attempts"
create_anomaly "privilege_escalation" 3 1 "critical" "Suspicious privilege escalation attempts"
create_anomaly "unusual_traffic" 156.7 100.0 "medium" "Unusual traffic pattern detected"

wait_with_progress 2 "Processing security anomalies"

# Generate some historical data points
echo -e "${YELLOW}📈 Generating Historical Data...${NC}"

# Create resolved anomalies from the past
for i in {1..5}; do
    past_time=$(date -d "$i hours ago" -Iseconds)
    create_anomaly "cpu_usage" $((70 + RANDOM % 20)) 80.0 "medium" "Historical CPU spike (resolved)"
done

wait_with_progress 2 "Processing historical data"

# Create some low-severity baseline anomalies
echo -e "${YELLOW}📊 Creating Baseline Anomalies...${NC}"

create_anomaly "cpu_usage" 72.3 70.0 "low" "Minor CPU usage increase"
create_anomaly "memory_usage" 76.8 75.0 "low" "Slight memory usage increase"
create_anomaly "response_time" 523 500 "low" "Response time slightly above normal"

# Summary
echo ""
echo -e "${GREEN}🎉 Demo Scenarios Generated Successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Summary of Generated Anomalies:${NC}"
echo -e "  🔴 Critical: 3 anomalies (CPU spike, Memory exhaustion, Disk space)"
echo -e "  🟠 High: 6 anomalies (Performance and resource issues)"
echo -e "  🟡 Medium: 8 anomalies (Various system issues)"
echo -e "  🟢 Low: 3 anomalies (Minor baseline deviations)"
echo ""
echo -e "${BLUE}🎯 Scenario Categories:${NC}"
echo -e "  ⚡ CPU & Performance: 6 anomalies"
echo -e "  🧠 Memory Issues: 3 anomalies"
echo -e "  💾 Storage Problems: 3 anomalies"
echo -e "  🌐 Network Issues: 3 anomalies"
echo -e "  📱 Application Issues: 3 anomalies"
echo -e "  🗄️ Database Issues: 3 anomalies"
echo -e "  🔒 Security Events: 3 anomalies"
echo ""
echo -e "${YELLOW}🎬 Ready for Demo!${NC}"
echo -e "Navigate to ${BLUE}http://localhost:3000${NC} to see the anomalies in action"
echo ""
echo -e "${BLUE}💡 Demo Tips:${NC}"
echo -e "  1. Start with the Dashboard to see overview"
echo -e "  2. Navigate to Anomalies page to see all generated issues"
echo -e "  3. Try acknowledging or remediating anomalies"
echo -e "  4. Use filters to focus on specific severity levels"
echo -e "  5. Check the Monitoring page for detailed metrics"
echo ""
echo -e "${GREEN}🎊 Demo environment is ready for presentation!${NC}"
