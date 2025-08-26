// SmartCloudOps AI - K6 Load Testing Script
// High-performance load testing with detailed metrics collection

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const apiResponseTime = new Trend('api_response_time');
const authFailures = new Counter('auth_failures');
const businessOperations = new Counter('business_operations');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 20 },   // Ramp up to 20 users
    { duration: '5m', target: 20 },   // Stay at 20 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users  
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '10m', target: 100 }, // Stay at 100 users
    { duration: '5m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests under 1s
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
    error_rate: ['rate<0.05'],         // Custom error rate under 5%
    api_response_time: ['p(90)<500'],  // 90% of API calls under 500ms
  },
  ext: {
    loadimpact: {
      projectID: 3595623,
      name: "SmartCloudOps AI Performance Test"
    }
  }
};

// Base URL - can be overridden with -e BASE_URL=...
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

// Test data
const testUsers = [
  { email: 'loadtest1@example.com', password: 'LoadTest123!' },
  { email: 'loadtest2@example.com', password: 'LoadTest123!' },
  { email: 'loadtest3@example.com', password: 'LoadTest123!' },
];

const anomalyTypes = ['cpu_usage', 'memory_usage', 'disk_usage', 'network_latency'];
const severities = ['low', 'medium', 'high', 'critical'];
const regions = ['us-west-2', 'us-east-1', 'eu-west-1', 'ap-southeast-1'];

// Global state for session management
let authToken = null;
let correlationId = null;

export function setup() {
  console.log('🚀 Starting SmartCloudOps AI Load Test');
  console.log(`📍 Target: ${BASE_URL}`);
  
  // Validate that the service is accessible
  const healthCheck = http.get(`${BASE_URL}/health`);
  check(healthCheck, {
    'Service is accessible': (r) => r.status === 200,
  });
  
  return { baseUrl: BASE_URL };
}

export default function(data) {
  correlationId = `k6-${__VU}-${__ITER}-${Date.now()}`;
  
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Correlation-ID': correlationId,
  };

  // Authentication flow
  group('Authentication', function() {
    if (!authToken) {
      authenticate(headers);
    }
  });

  // Core API operations
  group('Core Operations', function() {
    testHealthEndpoints(headers);
    testDashboardData(headers);
    testMetricsCollection(headers);
  });

  // Business operations
  group('Business Operations', function() {
    testAnomalyOperations(headers);
    testMLOperations(headers);
    testRemediationOperations(headers);
  });

  // Heavy operations (less frequent)
  if (Math.random() < 0.3) { // 30% chance
    group('Heavy Operations', function() {
      testBulkOperations(headers);
    });
  }

  sleep(randomIntBetween(1, 5));
}

function authenticate(headers) {
  const user = randomItem(testUsers);
  
  // Try to register first
  const registerPayload = {
    email: user.email,
    password: user.password,
    name: `K6 Load Test User ${__VU}`
  };

  let response = http.post(
    `${BASE_URL}/auth/register`,
    JSON.stringify(registerPayload),
    { headers }
  );

  // If registration fails, try login
  if (response.status !== 201) {
    const loginPayload = {
      email: user.email,
      password: user.password
    };

    response = http.post(
      `${BASE_URL}/auth/login`,
      JSON.stringify(loginPayload),
      { headers }
    );
  }

  const authSuccess = check(response, {
    'Authentication successful': (r) => r.status === 200 || r.status === 201,
    'Response has token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.access_token !== undefined;
      } catch {
        return false;
      }
    }
  });

  if (authSuccess && response.body) {
    try {
      const body = JSON.parse(response.body);
      authToken = body.access_token;
      headers['Authorization'] = `Bearer ${authToken}`;
    } catch (e) {
      console.error('Failed to parse auth response:', e);
      authFailures.add(1);
    }
  } else {
    authFailures.add(1);
  }

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
}

function testHealthEndpoints(headers) {
  // Basic health check
  let response = http.get(`${BASE_URL}/health`);
  check(response, {
    'Health check OK': (r) => r.status === 200,
    'Health response time < 100ms': (r) => r.timings.duration < 100,
  });

  // Observability health
  response = http.get(`${BASE_URL}/observability/health`);
  check(response, {
    'Observability health OK': (r) => r.status === 200,
  });

  // Metrics endpoint
  response = http.get(`${BASE_URL}/metrics`);
  check(response, {
    'Metrics available': (r) => r.status === 200,
    'Prometheus format': (r) => r.headers['Content-Type'].includes('text/plain'),
  });

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
}

function testDashboardData(headers) {
  if (!authToken) return;

  const response = http.get(`${BASE_URL}/api/dashboard/summary`, { headers });
  
  check(response, {
    'Dashboard data loaded': (r) => r.status === 200,
    'Dashboard response time < 500ms': (r) => r.timings.duration < 500,
  });

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  businessOperations.add(1);
}

function testMetricsCollection(headers) {
  if (!authToken) return;

  // Test monitoring status
  let response = http.get(`${BASE_URL}/api/monitoring/status`, { headers });
  check(response, {
    'Monitoring status OK': (r) => r.status === 200,
  });

  // Test metrics retrieval
  response = http.get(`${BASE_URL}/api/monitoring/metrics`, { headers });
  check(response, {
    'Metrics retrieval OK': (r) => r.status === 200 || r.status === 404, // 404 acceptable if endpoint doesn't exist
  });

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
}

function testAnomalyOperations(headers) {
  if (!authToken) return;

  // List anomalies
  let response = http.get(`${BASE_URL}/api/anomalies/`, { headers });
  check(response, {
    'Anomaly list loaded': (r) => r.status === 200,
  });

  // Create new anomaly
  const anomalyData = {
    metric_name: `${randomItem(anomalyTypes)}_${randomIntBetween(1, 100)}`,
    value: Math.random() * 100,
    threshold: randomIntBetween(70, 95),
    severity: randomItem(severities),
    source: 'k6_load_test',
    timestamp: Math.floor(Date.now() / 1000),
    metadata: {
      instance_id: `i-${randomIntBetween(100000, 999999)}`,
      region: randomItem(regions),
      test_run: correlationId
    }
  };

  response = http.post(
    `${BASE_URL}/api/anomalies/`,
    JSON.stringify(anomalyData),
    { headers }
  );

  check(response, {
    'Anomaly created': (r) => r.status === 200 || r.status === 201,
  });

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  businessOperations.add(1);
}

function testMLOperations(headers) {
  if (!authToken) return;

  // Get ML model info
  let response = http.get(`${BASE_URL}/api/ml/model/info`, { headers });
  check(response, {
    'ML model info retrieved': (r) => r.status === 200 || r.status === 404,
  });

  // Test ML prediction
  const predictionData = {
    features: Array.from({ length: 10 }, () => Math.random() * 100),
    model_name: 'anomaly_detector',
    threshold: 0.5
  };

  response = http.post(
    `${BASE_URL}/api/ml/predict`,
    JSON.stringify(predictionData),
    { headers }
  );

  check(response, {
    'ML prediction completed': (r) => r.status === 200 || r.status === 404,
  });

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  businessOperations.add(1);
}

function testRemediationOperations(headers) {
  if (!authToken) return;

  // List remediation actions
  let response = http.get(`${BASE_URL}/api/remediation/actions`, { headers });
  check(response, {
    'Remediation actions listed': (r) => r.status === 200,
  });

  // Create remediation action (occasionally)
  if (Math.random() < 0.3) {
    const actionData = {
      action_type: randomItem(['restart_service', 'scale_up', 'scale_down', 'send_alert']),
      target_resource: `instance-${randomIntBetween(1, 100)}`,
      parameters: {
        severity: randomItem(severities),
        timeout: randomIntBetween(30, 300),
        retry_count: randomIntBetween(1, 3)
      },
      require_approval: Math.random() < 0.5,
      triggered_by: 'k6_load_test'
    };

    response = http.post(
      `${BASE_URL}/api/remediation/actions`,
      JSON.stringify(actionData),
      { headers }
    );

    check(response, {
      'Remediation action created': (r) => r.status === 200 || r.status === 201,
    });
  }

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  businessOperations.add(1);
}

function testBulkOperations(headers) {
  if (!authToken) return;

  // Bulk anomaly analysis
  const bulkData = {
    metrics: Array.from({ length: 50 }, (_, i) => ({
      name: `metric_${i}`,
      value: Math.random() * 100,
      timestamp: Math.floor(Date.now() / 1000) - randomIntBetween(0, 3600)
    })),
    analysis_type: 'anomaly_detection',
    parameters: {
      threshold: 0.8,
      algorithm: 'isolation_forest'
    }
  };

  const response = http.post(
    `${BASE_URL}/api/ml/analyze/bulk`,
    JSON.stringify(bulkData),
    { 
      headers,
      timeout: '30s' // Longer timeout for bulk operations
    }
  );

  check(response, {
    'Bulk analysis completed': (r) => r.status === 200 || r.status === 404,
    'Bulk analysis under 10s': (r) => r.timings.duration < 10000,
  });

  if (response.timings.duration > 5000) {
    console.warn(`Slow bulk operation: ${response.timings.duration}ms`);
  }

  apiResponseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  businessOperations.add(1);
}

export function teardown(data) {
  console.log('🏁 Load test completed');
  console.log(`📊 Final metrics will be available in the report`);
}

// Export for CI/CD integration
export { errorRate, apiResponseTime, authFailures, businessOperations };
