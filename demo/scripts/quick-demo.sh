#!/bin/bash

# SmartCloudOps AI - Quick Demo Setup Script
# Sets up a complete demo environment in 5 minutes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Demo configuration
DEMO_NAME="SmartCloudOps AI Demo"
DEMO_VERSION="1.0.0"
DEMO_PORT=3000
API_PORT=5000

echo -e "${BLUE}🎬 ${DEMO_NAME} - Quick Demo Setup${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if ports are available
if lsof -Pi :$DEMO_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $DEMO_PORT is already in use. Please stop the service using this port.${NC}"
    exit 1
fi

if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $API_PORT is already in use. Please stop the service using this port.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Start demo environment
echo -e "${YELLOW}🚀 Starting demo environment...${NC}"

# Create demo directory if it doesn't exist
mkdir -p demo/data
mkdir -p demo/logs
mkdir -p demo/config

# Start services
docker-compose -f demo/docker-compose.demo.yml up -d

echo -e "${GREEN}✅ Demo services started${NC}"
echo ""

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"

# Wait for backend API
for i in {1..30}; do
    if curl -f http://localhost:$API_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend API is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend API failed to start within 60 seconds${NC}"
        docker-compose -f demo/docker-compose.demo.yml logs backend
        exit 1
    fi
    sleep 2
done

# Wait for frontend
for i in {1..30}; do
    if curl -f http://localhost:$DEMO_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend failed to start within 60 seconds${NC}"
        docker-compose -f demo/docker-compose.demo.yml logs frontend
        exit 1
    fi
    sleep 2
done

echo ""

# Load demo data
echo -e "${YELLOW}📊 Loading demo data...${NC}"
./demo/scripts/load-demo-data.sh

echo -e "${GREEN}✅ Demo data loaded${NC}"
echo ""

# Start demo scenarios
echo -e "${YELLOW}🎭 Starting demo scenarios...${NC}"
./demo/scripts/start-demo-scenarios.sh

echo -e "${GREEN}✅ Demo scenarios started${NC}"
echo ""

# Display demo information
echo -e "${GREEN}🎉 Demo environment is ready!${NC}"
echo ""
echo -e "${BLUE}📋 Demo Access Information:${NC}"
echo -e "  🌐 Frontend URL: ${GREEN}http://localhost:$DEMO_PORT${NC}"
echo -e "  🔌 Backend API: ${GREEN}http://localhost:$API_PORT${NC}"
echo -e "  📚 API Docs:    ${GREEN}http://localhost:$API_PORT/docs${NC}"
echo ""
echo -e "${BLUE}🔐 Demo Credentials:${NC}"
echo -e "  👤 Username: ${GREEN}demo@smartcloudops.ai${NC}"
echo -e "  🔑 Password: ${GREEN}SmartCloudOpsDemo2024!${NC}"
echo ""
echo -e "${BLUE}🎬 Demo Scenarios:${NC}"
echo -e "  1️⃣  Real-time Anomaly Detection"
echo -e "  2️⃣  Automated Remediation"
echo -e "  3️⃣  ChatOps Integration"
echo -e "  4️⃣  ML Model Performance"
echo ""
echo -e "${BLUE}🎯 Quick Demo Commands:${NC}"
echo -e "  CPU Spike:     ${YELLOW}./demo/scripts/generate-cpu-spike.sh${NC}"
echo -e "  Memory Leak:   ${YELLOW}./demo/scripts/generate-memory-leak.sh${NC}"
echo -e "  Network Issue: ${YELLOW}./demo/scripts/generate-network-issues.sh${NC}"
echo -e "  Load Test:     ${YELLOW}./demo/scripts/light-load-test.sh${NC}"
echo ""
echo -e "${BLUE}🛑 Stop Demo:${NC}"
echo -e "  ${YELLOW}./demo/scripts/stop-demo.sh${NC}"
echo ""
echo -e "${GREEN}🚀 Opening demo in browser...${NC}"

# Open browser (cross-platform)
if command -v open &> /dev/null; then
    open http://localhost:$DEMO_PORT
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:$DEMO_PORT
elif command -v start &> /dev/null; then
    start http://localhost:$DEMO_PORT
else
    echo -e "${YELLOW}⚠️ Please manually open http://localhost:$DEMO_PORT in your browser${NC}"
fi

echo ""
echo -e "${GREEN}🎊 Enjoy your SmartCloudOps AI demo!${NC}"
echo -e "${BLUE}For support: demo-support@smartcloudops.ai${NC}"

# Save demo session info
cat > demo/logs/demo-session.log <<EOF
Demo Session Started: $(date)
Demo Version: $DEMO_VERSION
Frontend URL: http://localhost:$DEMO_PORT
Backend API: http://localhost:$API_PORT
Demo User: demo@smartcloudops.ai
Session ID: demo-$(date +%s)
EOF
