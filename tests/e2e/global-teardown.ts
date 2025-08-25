import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * Global teardown for Playwright tests
 * Cleanup test environment and generate reports
 */

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up E2E test environment...');

  // Cleanup temporary files
  await cleanupTempFiles();

  // Generate test summary
  await generateTestSummary();

  console.log('✅ E2E test cleanup complete');
}

async function cleanupTempFiles() {
  console.log('🗑️ Cleaning temporary files...');

  const tempDirs = [
    'tests/e2e/auth',
    'tests/e2e/temp'
  ];

  for (const dir of tempDirs) {
    const fullPath = path.join(process.cwd(), dir);
    if (fs.existsSync(fullPath)) {
      fs.rmSync(fullPath, { recursive: true, force: true });
      console.log(`   Removed: ${dir}`);
    }
  }
}

async function generateTestSummary() {
  console.log('📊 Generating test summary...');

  const resultsPath = path.join(process.cwd(), 'test-results.json');
  
  if (fs.existsSync(resultsPath)) {
    try {
      const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));
      
      const summary = {
        timestamp: new Date().toISOString(),
        total_tests: results.stats?.total || 0,
        passed: results.stats?.passed || 0,
        failed: results.stats?.failed || 0,
        skipped: results.stats?.skipped || 0,
        flaky: results.stats?.flaky || 0,
        duration: results.stats?.duration || 0,
        projects: results.stats?.projects || [],
        environment: {
          node_version: process.version,
          platform: process.platform,
          ci: !!process.env.CI
        }
      };

      // Save summary
      fs.writeFileSync(
        path.join(process.cwd(), 'test-summary.json'),
        JSON.stringify(summary, null, 2)
      );

      // Console output
      console.log('📈 Test Results Summary:');
      console.log(`   Total Tests: ${summary.total_tests}`);
      console.log(`   ✅ Passed: ${summary.passed}`);
      console.log(`   ❌ Failed: ${summary.failed}`);
      console.log(`   ⏭️ Skipped: ${summary.skipped}`);
      console.log(`   🔄 Flaky: ${summary.flaky}`);
      console.log(`   ⏱️ Duration: ${(summary.duration / 1000).toFixed(2)}s`);

      if (summary.failed > 0) {
        console.log('❌ Some tests failed. Check the HTML report for details.');
        process.exitCode = 1;
      } else {
        console.log('✅ All tests passed!');
      }

    } catch (error) {
      console.warn('⚠️ Could not parse test results:', error);
    }
  } else {
    console.warn('⚠️ No test results found');
  }
}

export default globalTeardown;
