#!/bin/bash

# SmartCloudOps AI - Local Test Orchestration Script
# Runs backend, frontend, and e2e tests with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=${FRONTEND_PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-5000}
COVERAGE_MIN=${COVERAGE_MIN:-80}
TEST_MODE=1

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use. Killing existing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    print_status "Cleanup complete"
}

# Set up trap to cleanup on script exit
trap cleanup EXIT

# Main test execution
main() {
    print_status "Starting SmartCloudOps AI Test Suite"
    print_status "Frontend Port: $FRONTEND_PORT"
    print_status "Backend Port: $BACKEND_PORT"
    print_status "Coverage Target: ${COVERAGE_MIN}%"
    
    # Export environment variables
    export TEST_MODE=1
    export FLASK_ENV=testing
    export FLASK_PORT=$BACKEND_PORT
    export FLASK_HOST=127.0.0.1
    export NEXT_PUBLIC_API_URL=http://localhost:$BACKEND_PORT
    export AI_PROVIDER=local
    export DISABLE_AWS_SERVICES=true
    export DISABLE_ELASTICSEARCH=true
    export USE_LOCAL_STORAGE=true
    export DATABASE_URL=sqlite:///:memory:
    export OPENAI_API_KEY=test-key
    export GEMINI_API_KEY=test-key
    export REDIS_PASSWORD=test-password
    export SECRET_KEY=test-secret-key-for-testing-only-32-chars-minimum
    export JWT_SECRET_KEY=test-jwt-secret-key-for-testing-only-32-chars-minimum
    
    # Initialize exit codes
    backend_exit=0
    frontend_exit=0
    e2e_exit=0
    
    # Step 1: Backend Tests
    print_status "Running backend tests..."
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt >/dev/null 2>&1 || pip install pytest pytest-cov requests
    else
        pip install pytest pytest-cov requests
    fi
    
    # Run backend tests with coverage
    if pytest -q --maxfail=1 --disable-warnings --cov=app --cov-report=xml --cov-report=html tests/backend/; then
        print_success "Backend tests passed"
        backend_exit=0
    else
        print_error "Backend tests failed"
        backend_exit=1
    fi
    
    # Check coverage
    if [ -f "coverage.xml" ]; then
        coverage_percent=$(python -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('coverage.xml').getroot()
    line_rate = float(root.attrib.get('line-rate', 0))
    print(f'{line_rate * 100:.1f}')
except:
    print('0.0')
")
        print_status "Backend coverage: ${coverage_percent}%"
        
        if (( $(echo "$coverage_percent < $COVERAGE_MIN" | bc -l) )); then
            print_warning "Coverage below target (${COVERAGE_MIN}%)"
        else
            print_success "Coverage target met"
        fi
    fi
    
    # Step 2: Frontend Tests
    print_status "Running frontend tests..."
    cd smartcloudops-ai
    
    # Install dependencies
    if [ -f "package-lock.json" ]; then
        npm ci --silent
    elif [ -f "pnpm-lock.yaml" ]; then
        pnpm install --silent
    else
        npm install --silent
    fi
    
    # Run linting
    if npm run lint; then
        print_success "Frontend linting passed"
    else
        print_error "Frontend linting failed"
        frontend_exit=1
    fi
    
    # Run type checking
    if npm run typecheck; then
        print_success "Frontend type checking passed"
    else
        print_error "Frontend type checking failed"
        frontend_exit=1
    fi
    
    cd ..
    
    # Step 3: E2E Tests (only if backend and frontend passed)
    if [ $backend_exit -eq 0 ] && [ $frontend_exit -eq 0 ]; then
        print_status "Running E2E tests..."
        
        # Install Playwright if not already installed
        cd smartcloudops-ai
        if ! npx playwright --version >/dev/null 2>&1; then
            print_status "Installing Playwright..."
            npx playwright install --with-deps
        fi
        
        # Run E2E tests
        if npx playwright test --reporter=line; then
            print_success "E2E tests passed"
            e2e_exit=0
        else
            print_error "E2E tests failed"
            e2e_exit=1
        fi
        
        cd ..
    else
        print_warning "Skipping E2E tests due to backend or frontend failures"
        e2e_exit=1
    fi
    
    # Final summary
    echo
    print_status "=== TEST SUMMARY ==="
    print_status "Backend Tests: $([ $backend_exit -eq 0 ] && echo "PASSED" || echo "FAILED")"
    print_status "Frontend Tests: $([ $frontend_exit -eq 0 ] && echo "PASSED" || echo "FAILED")"
    print_status "E2E Tests: $([ $e2e_exit -eq 0 ] && echo "PASSED" || echo "FAILED")"
    
    if [ -f "coverage.xml" ]; then
        print_status "Backend Coverage: ${coverage_percent}% (target: ${COVERAGE_MIN}%)"
    fi
    
    print_status "Artifacts:"
    if [ -f "coverage.xml" ]; then
        print_status "  - Backend coverage: coverage.xml, htmlcov/"
    fi
    if [ -d "smartcloudops-ai/test-results" ]; then
        print_status "  - E2E results: smartcloudops-ai/test-results/"
    fi
    if [ -d "smartcloudops-ai/playwright-report" ]; then
        print_status "  - Playwright report: smartcloudops-ai/playwright-report/"
    fi
    
    # Calculate overall exit code
    overall_exit=$((backend_exit + frontend_exit + e2e_exit))
    
    if [ $overall_exit -eq 0 ]; then
        print_success "All tests passed! 🎉"
    else
        print_error "Some tests failed. Please check the output above."
    fi
    
    exit $overall_exit
}

# Run main function
main "$@"
