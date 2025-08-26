import { defineConfig, devices } from '@playwright/test';

/**
 * SmartCloudOps AI - Playwright E2E Testing Configuration
 * Comprehensive end-to-end testing with multiple browsers and devices
 */

export default defineConfig({
  testDir: './tests',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter configuration */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit-results.xml' }],
    ['list'],
    process.env.CI ? ['github'] : ['line']
  ],
  
  /* Shared settings for all projects */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    /* Collect trace when retrying the failed test. */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
    
    /* Global timeout for each test */
    actionTimeout: 10000,
    
    /* Ignore HTTPS errors */
    ignoreHTTPSErrors: true,
    
    /* Extra HTTP headers */
    extraHTTPHeaders: {
      'X-Test-Suite': 'Playwright-E2E'
    }
  },

  /* Test timeout */
  timeout: 30000,
  
  /* Expect timeout */
  expect: {
    timeout: 5000
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* Test against branded browsers. */
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },

    /* Tablet testing */
    {
      name: 'iPad',
      use: { ...devices['iPad Pro'] },
    },

    /* Desktop variations */
    {
      name: 'Desktop 1920x1080',
      use: {
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'Desktop 1366x768',
      use: {
        viewport: { width: 1366, height: 768 },
      },
    }
  ],

  /* Global setup and teardown */
  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),

  /* Run your local dev server before starting the tests */
  webServer: [
    {
      command: 'npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      stdout: 'ignore',
      stderr: 'pipe',
    },
    {
      command: 'python -m flask run --host=0.0.0.0 --port=5000',
      port: 5000,
      cwd: './',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        FLASK_APP: 'app/main.py',
        FLASK_ENV: 'development'
      }
    }
  ],

  /* Test output directories */
  outputDir: 'test-results/',
  
  /* Metadata */
  metadata: {
    'test-suite': 'SmartCloudOps AI E2E Tests',
    'version': '1.0.0',
    'environment': process.env.NODE_ENV || 'test'
  }
});
