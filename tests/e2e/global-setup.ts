import { chromium, FullConfig } from '@playwright/test';
import path from 'path';
import fs from 'fs';

/**
 * Global setup for Playwright tests
 * Prepares test environment and authentication
 */

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up E2E test environment...');

  // Create necessary directories
  const dirs = [
    'test-results',
    'playwright-report',
    'screenshots',
    'videos',
    'trace'
  ];

  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  // Setup test data
  await setupTestData();

  // Authenticate and save session
  await setupAuthentication(config);

  console.log('✅ E2E test environment ready');
}

async function setupTestData() {
  console.log('📊 Setting up test data...');
  
  // Create test data files
  const testData = {
    users: [
      {
        id: 'test-user-1',
        email: 'test@smartcloudops.ai',
        password: 'TestPassword123!',
        role: 'admin',
        name: 'Test User'
      },
      {
        id: 'test-user-2', 
        email: 'user@smartcloudops.ai',
        password: 'UserPassword123!',
        role: 'user',
        name: 'Regular User'
      }
    ],
    anomalies: [
      {
        id: 'test-anomaly-1',
        metric_name: 'cpu_usage',
        value: 95.5,
        threshold: 80.0,
        severity: 'high',
        timestamp: new Date().toISOString()
      },
      {
        id: 'test-anomaly-2',
        metric_name: 'memory_usage', 
        value: 78.2,
        threshold: 85.0,
        severity: 'medium',
        timestamp: new Date().toISOString()
      }
    ],
    remediation_actions: [
      {
        id: 'test-action-1',
        action_type: 'restart_service',
        status: 'completed',
        target_resource: 'web-server-1'
      }
    ]
  };

  // Save test data
  fs.writeFileSync(
    path.join(process.cwd(), 'tests/e2e/fixtures/test-data.json'),
    JSON.stringify(testData, null, 2)
  );

  console.log('✅ Test data ready');
}

async function setupAuthentication(config: FullConfig) {
  console.log('🔐 Setting up authentication...');

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Navigate to login page
    await page.goto(config.projects[0].use?.baseURL + '/auth/login' || 'http://localhost:3000/auth/login');

    // Wait for login form
    await page.waitForSelector('[data-testid="login-form"]', { timeout: 10000 });

    // Fill login form
    await page.fill('[data-testid="email-input"]', 'test@smartcloudops.ai');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    
    // Submit login
    await page.click('[data-testid="login-button"]');

    // Wait for successful login
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Save authentication state
    await page.context().storageState({ 
      path: path.join(process.cwd(), 'tests/e2e/auth/admin-session.json') 
    });

    console.log('✅ Admin authentication saved');

    // Setup regular user authentication
    await page.goto(config.projects[0].use?.baseURL + '/auth/logout' || 'http://localhost:3000/auth/logout');
    await page.goto(config.projects[0].use?.baseURL + '/auth/login' || 'http://localhost:3000/auth/login');

    await page.fill('[data-testid="email-input"]', 'user@smartcloudops.ai');
    await page.fill('[data-testid="password-input"]', 'UserPassword123!');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('**/dashboard');

    await page.context().storageState({ 
      path: path.join(process.cwd(), 'tests/e2e/auth/user-session.json') 
    });

    console.log('✅ User authentication saved');

  } catch (error) {
    console.warn('⚠️ Authentication setup failed, tests will use mock data:', error);
  } finally {
    await browser.close();
  }
}

export default globalSetup;
