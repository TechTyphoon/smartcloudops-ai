#!/bin/bash
# SmartCloudOps AI - Performance Baseline Test Runner
# Comprehensive baseline measurement with multiple tools

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_URL=${APP_URL:-"http://localhost:5000"}
TEST_DURATION=${TEST_DURATION:-"300"}  # 5 minutes default
VIRTUAL_USERS=${VIRTUAL_USERS:-"50"}
RAMP_UP_TIME=${RAMP_UP_TIME:-"60"}
RESULTS_DIR="docs/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASELINE_DIR="${RESULTS_DIR}/baseline_${TIMESTAMP}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check Python and required packages
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        if ! python3 -c "import locust" 2>/dev/null; then
            missing_deps+=("locust (pip install locust)")
        fi
        if ! python3 -c "import psutil" 2>/dev/null; then
            missing_deps+=("psutil (pip install psutil)")
        fi
        if ! python3 -c "import requests" 2>/dev/null; then
            missing_deps+=("requests (pip install requests)")
        fi
    fi
    
    # Check k6
    if ! command -v k6 &> /dev/null; then
        log_warning "k6 not found - will skip k6 tests"
    fi
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "All dependencies available"
}

check_application() {
    log_info "Checking application health..."
    
    # Test basic connectivity
    if ! curl -s --connect-timeout 5 "${APP_URL}/health" >/dev/null; then
        log_error "Application not accessible at ${APP_URL}"
        log_info "Please ensure the application is running"
        exit 1
    fi
    
    # Test API endpoints
    local endpoints=("/health" "/metrics" "/observability/health")
    local failed_endpoints=()
    
    for endpoint in "${endpoints[@]}"; do
        if ! curl -s --connect-timeout 5 "${APP_URL}${endpoint}" >/dev/null; then
            failed_endpoints+=("${endpoint}")
        fi
    done
    
    if [ ${#failed_endpoints[@]} -ne 0 ]; then
        log_warning "Some endpoints not accessible: ${failed_endpoints[*]}"
    else
        log_success "Application is healthy and accessible"
    fi
}

setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create results directory
    mkdir -p "${BASELINE_DIR}"
    
    # Create test configuration file
    cat > "${BASELINE_DIR}/test_config.json" << EOF
{
    "test_name": "performance_baseline",
    "timestamp": "${TIMESTAMP}",
    "app_url": "${APP_URL}",
    "test_duration": ${TEST_DURATION},
    "virtual_users": ${VIRTUAL_USERS},
    "ramp_up_time": ${RAMP_UP_TIME},
    "test_type": "baseline",
    "environment": {
        "os": "$(uname -s)",
        "kernel": "$(uname -r)",
        "hostname": "$(hostname)",
        "cpu_cores": "$(nproc)",
        "memory_gb": "$(free -g | awk '/^Mem:/{print $2}')"
    }
}
EOF
    
    log_success "Test environment configured"
}

run_performance_monitoring() {
    log_info "Starting performance monitoring..."
    
    # Start background performance monitoring
    python3 scripts/performance/performance_analyzer.py \
        --url "${APP_URL}" \
        --duration $((TEST_DURATION + 60)) \
        --output "${BASELINE_DIR}/performance_analysis.md" \
        > "${BASELINE_DIR}/performance_monitor.log" 2>&1 &
    
    MONITOR_PID=$!
    
    # Give monitor time to start
    sleep 5
    
    log_success "Performance monitoring started (PID: ${MONITOR_PID})"
}

run_locust_test() {
    log_info "Running Locust load test..."
    
    # Run Locust test
    python3 -m locust \
        -f scripts/performance/locust_load_test.py \
        --host="${APP_URL}" \
        --users="${VIRTUAL_USERS}" \
        --spawn-rate=$((VIRTUAL_USERS / RAMP_UP_TIME * 60)) \
        --run-time="${TEST_DURATION}s" \
        --html="${BASELINE_DIR}/locust_report.html" \
        --csv="${BASELINE_DIR}/locust_results" \
        --headless \
        --loglevel=INFO \
        > "${BASELINE_DIR}/locust.log" 2>&1
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "Locust test completed successfully"
    else
        log_error "Locust test failed with exit code: $exit_code"
        return $exit_code
    fi
}

run_k6_test() {
    if ! command -v k6 &> /dev/null; then
        log_warning "k6 not available, skipping k6 test"
        return 0
    fi
    
    log_info "Running k6 load test..."
    
    # Set k6 environment variables
    export K6_OUT="json=${BASELINE_DIR}/k6_results.json"
    
    # Run k6 test
    k6 run \
        --vus="${VIRTUAL_USERS}" \
        --duration="${TEST_DURATION}s" \
        --ramp-up-time="${RAMP_UP_TIME}s" \
        --summary-export="${BASELINE_DIR}/k6_summary.json" \
        -e BASE_URL="${APP_URL}" \
        scripts/performance/k6_load_test.js \
        > "${BASELINE_DIR}/k6.log" 2>&1
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "k6 test completed successfully"
    else
        log_error "k6 test failed with exit code: $exit_code"
        return $exit_code
    fi
}

run_simple_benchmark() {
    log_info "Running simple HTTP benchmark..."
    
    # Create a simple curl benchmark
    local endpoints=(
        "/health"
        "/metrics" 
        "/observability/health"
    )
    
    echo "# Simple HTTP Benchmark Results" > "${BASELINE_DIR}/curl_benchmark.md"
    echo "Generated: $(date)" >> "${BASELINE_DIR}/curl_benchmark.md"
    echo "" >> "${BASELINE_DIR}/curl_benchmark.md"
    
    for endpoint in "${endpoints[@]}"; do
        echo "## Endpoint: ${endpoint}" >> "${BASELINE_DIR}/curl_benchmark.md"
        echo "" >> "${BASELINE_DIR}/curl_benchmark.md"
        
        # Run curl benchmark (10 requests)
        local total_time=0
        local successful_requests=0
        local failed_requests=0
        
        echo "Running 10 requests to ${endpoint}..."
        
        for i in {1..10}; do
            local start_time=$(date +%s.%N)
            
            if curl -s --connect-timeout 5 --max-time 10 "${APP_URL}${endpoint}" >/dev/null; then
                local end_time=$(date +%s.%N)
                local request_time=$(echo "$end_time - $start_time" | bc)
                total_time=$(echo "$total_time + $request_time" | bc)
                ((successful_requests++))
            else
                ((failed_requests++))
            fi
            
            sleep 0.1
        done
        
        if [ $successful_requests -gt 0 ]; then
            local avg_time=$(echo "scale=3; $total_time / $successful_requests" | bc)
            echo "- Successful requests: $successful_requests/10" >> "${BASELINE_DIR}/curl_benchmark.md"
            echo "- Failed requests: $failed_requests/10" >> "${BASELINE_DIR}/curl_benchmark.md"
            echo "- Average response time: ${avg_time}s" >> "${BASELINE_DIR}/curl_benchmark.md"
        else
            echo "- All requests failed" >> "${BASELINE_DIR}/curl_benchmark.md"
        fi
        
        echo "" >> "${BASELINE_DIR}/curl_benchmark.md"
    done
    
    log_success "Simple benchmark completed"
}

collect_system_info() {
    log_info "Collecting system information..."
    
    # Collect comprehensive system information
    cat > "${BASELINE_DIR}/system_info.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "system": {
        "os": "$(uname -s)",
        "kernel": "$(uname -r)",
        "architecture": "$(uname -m)",
        "hostname": "$(hostname)",
        "uptime": "$(uptime)"
    },
    "hardware": {
        "cpu_model": "$(grep 'model name' /proc/cpuinfo | head -1 | cut -d ':' -f2 | xargs)",
        "cpu_cores": $(nproc),
        "memory_total_gb": $(free -g | awk '/^Mem:/{print $2}'),
        "memory_available_gb": $(free -g | awk '/^Mem:/{print $7}'),
        "disk_usage": "$(df -h / | tail -1)"
    },
    "application": {
        "url": "${APP_URL}",
        "python_version": "$(python3 --version 2>&1)",
        "pip_packages": "$(pip freeze | wc -l) packages installed"
    }
}
EOF
    
    # Collect network information
    ss -tulpn > "${BASELINE_DIR}/network_connections.txt" 2>/dev/null || netstat -tulpn > "${BASELINE_DIR}/network_connections.txt" 2>/dev/null || echo "Network info not available" > "${BASELINE_DIR}/network_connections.txt"
    
    # Collect process information
    ps aux --sort=-%cpu | head -20 > "${BASELINE_DIR}/top_processes.txt"
    
    log_success "System information collected"
}

wait_for_tests() {
    log_info "Waiting for tests to complete..."
    
    # Wait for background monitor
    if [ -n "${MONITOR_PID:-}" ]; then
        wait $MONITOR_PID
        log_success "Performance monitoring completed"
    fi
    
    # Give time for final data collection
    sleep 5
}

generate_summary_report() {
    log_info "Generating summary report..."
    
    # Create summary report
    cat > "${BASELINE_DIR}/BASELINE_SUMMARY.md" << EOF
# 📊 Performance Baseline Summary

**Test Date**: $(date)  
**Test Duration**: ${TEST_DURATION} seconds  
**Virtual Users**: ${VIRTUAL_USERS}  
**Target URL**: ${APP_URL}

## 🎯 Test Configuration

- **Ramp-up Time**: ${RAMP_UP_TIME} seconds
- **Test Type**: Baseline Performance Test
- **Tools Used**: 
  - Locust (Python-based load testing)
$(if command -v k6 &> /dev/null; then echo "  - k6 (JavaScript-based load testing)"; fi)
  - Custom Performance Analyzer
  - System Resource Monitoring

## 📁 Generated Files

- \`locust_report.html\` - Interactive Locust test report
- \`locust_results_stats.csv\` - Locust statistics
- \`performance_analysis.md\` - Detailed performance analysis
$(if command -v k6 &> /dev/null; then echo "- \`k6_results.json\` - k6 test results"; echo "- \`k6_summary.json\` - k6 summary statistics"; fi)
- \`curl_benchmark.md\` - Simple HTTP benchmark
- \`system_info.json\` - System configuration
- \`test_config.json\` - Test configuration

## 🔍 Key Metrics to Review

1. **Response Times**: Check average, median, and 95th percentile
2. **Throughput**: Requests per second (RPS)
3. **Error Rate**: Percentage of failed requests
4. **Resource Usage**: CPU, memory, and I/O utilization
5. **Bottlenecks**: Identified performance constraints

## 📈 Next Steps

1. Review the detailed analysis in \`performance_analysis.md\`
2. Open \`locust_report.html\` in a browser for interactive charts
3. Compare results with future optimization tests
4. Implement recommended optimizations
5. Re-run tests to measure improvements

## 🎯 Performance Thresholds

This baseline establishes your current performance characteristics.
Future tests should aim to maintain or improve these metrics:

- **Response Time**: Target < 500ms average
- **Error Rate**: Target < 1%
- **CPU Usage**: Target < 80% average
- **Memory Usage**: Target < 85% of available

EOF

    # Add quick stats if Locust results are available
    if [ -f "${BASELINE_DIR}/locust_results_stats.csv" ]; then
        echo "" >> "${BASELINE_DIR}/BASELINE_SUMMARY.md"
        echo "## 📊 Quick Stats (Locust)" >> "${BASELINE_DIR}/BASELINE_SUMMARY.md"
        echo "" >> "${BASELINE_DIR}/BASELINE_SUMMARY.md"
        echo "\`\`\`" >> "${BASELINE_DIR}/BASELINE_SUMMARY.md"
        tail -n +2 "${BASELINE_DIR}/locust_results_stats.csv" | head -5 >> "${BASELINE_DIR}/BASELINE_SUMMARY.md"
        echo "\`\`\`" >> "${BASELINE_DIR}/BASELINE_SUMMARY.md"
    fi
    
    log_success "Summary report generated"
}

cleanup() {
    log_info "Cleaning up..."
    
    # Kill background processes if still running
    if [ -n "${MONITOR_PID:-}" ]; then
        if kill -0 $MONITOR_PID 2>/dev/null; then
            kill $MONITOR_PID
            log_info "Stopped performance monitor"
        fi
    fi
    
    # Set permissions on results
    chmod -R 644 "${BASELINE_DIR}"/* 2>/dev/null || true
    chmod 755 "${BASELINE_DIR}"
    
    log_success "Cleanup completed"
}

main() {
    echo "🚀 SmartCloudOps AI - Performance Baseline Test"
    echo "=============================================="
    echo ""
    
    # Trap for cleanup on exit
    trap cleanup EXIT
    
    # Run test phases
    check_dependencies
    check_application
    setup_test_environment
    collect_system_info
    
    echo ""
    log_info "Starting performance tests..."
    echo ""
    
    # Start monitoring
    run_performance_monitoring
    
    # Wait for monitor to initialize
    sleep 2
    
    # Run load tests
    run_locust_test
    run_k6_test
    run_simple_benchmark
    
    # Wait for everything to complete
    wait_for_tests
    
    # Generate reports
    generate_summary_report
    
    echo ""
    echo "🎉 BASELINE TEST COMPLETED!"
    echo "=========================="
    echo ""
    log_success "Results saved to: ${BASELINE_DIR}"
    log_info "Review the summary: ${BASELINE_DIR}/BASELINE_SUMMARY.md"
    log_info "Open detailed report: ${BASELINE_DIR}/locust_report.html"
    echo ""
    
    # Show quick summary
    if [ -f "${BASELINE_DIR}/locust_results_stats.csv" ]; then
        echo "📊 Quick Results:"
        echo "----------------"
        echo "$(tail -n +2 "${BASELINE_DIR}/locust_results_stats.csv" | head -1 | awk -F',' '{print "Requests: " $2 ", Failures: " $3 ", Avg Response: " $4 "ms"}')"
    fi
    
    return 0
}

# Run main function
main "$@"
