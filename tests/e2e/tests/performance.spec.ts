import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { TestHelpers } from '../utils/test-helpers';

/**
 * Performance E2E Tests
 * Tests application performance, load times, and user experience metrics
 */

test.describe('Performance Testing', () => {
  let testHelpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    testHelpers = new TestHelpers(page);
    
    // Login for performance testing
    const loginPage = new LoginPage(page);
    await page.goto('/auth/login');
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('should load dashboard within performance budget', async ({ page }) => {
    // Clear cache and reload for accurate measurement
    await page.evaluate(() => {
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        });
      }
    });
    
    const startTime = Date.now();
    await page.reload();
    
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.waitForDashboardToLoad();
    
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Get detailed performance metrics
    const metrics = await testHelpers.getPerformanceMetrics();
    
    // Performance budget assertions
    expect(metrics.domContentLoaded).toBeLessThan(2000);
    expect(metrics.firstContentfulPaint).toBeLessThan(1500);
    expect(metrics.totalLoadTime).toBeLessThan(3000);
    
    console.log('Performance metrics:', metrics);
  });

  test('should handle rapid navigation without performance degradation', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const navigationTimes: number[] = [];
    
    const routes = [
      { method: 'navigateToAnomalies', url: '/anomalies' },
      { method: 'navigateToRemediation', url: '/remediation' },
      { method: 'navigateToMonitoring', url: '/monitoring' },
      { method: 'navigateToReports', url: '/reports' }
    ];
    
    for (const route of routes) {
      const startTime = Date.now();
      
      // Navigate using dashboard method
      await (dashboardPage as any)[route.method]();
      await expect(page).toHaveURL(new RegExp(route.url));
      await testHelpers.waitForLoadingComplete();
      
      const navigationTime = Date.now() - startTime;
      navigationTimes.push(navigationTime);
      
      // Each navigation should be under 2 seconds
      expect(navigationTime).toBeLessThan(2000);
      
      // Return to dashboard
      await page.goto('/dashboard');
      await dashboardPage.waitForDashboardToLoad();
    }
    
    // Average navigation time should be reasonable
    const avgTime = navigationTimes.reduce((a, b) => a + b, 0) / navigationTimes.length;
    expect(avgTime).toBeLessThan(1500);
    
    console.log('Navigation times:', navigationTimes);
  });

  test('should handle large datasets without performance issues', async ({ page }) => {
    // Navigate to anomalies page (typically has large datasets)
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.navigateToAnomalies();
    
    const startTime = Date.now();
    
    // Wait for data to load
    await testHelpers.waitForLoadingComplete();
    await page.waitForSelector('[data-testid="anomaly-card"]', { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // Large dataset should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
    
    // Test scrolling performance with large lists
    const scrollStartTime = Date.now();
    
    for (let i = 0; i < 10; i++) {
      await page.mouse.wheel(0, 500);
      await page.waitForTimeout(100);
    }
    
    const scrollTime = Date.now() - scrollStartTime;
    
    // Scrolling should be smooth (under 2 seconds for 10 scrolls)
    expect(scrollTime).toBeLessThan(2000);
  });

  test('should maintain performance during real-time updates', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    // Get initial performance metrics
    const initialMetrics = await testHelpers.getPerformanceMetrics();
    
    // Simulate real-time updates by refreshing widgets
    const updateTimes: number[] = [];
    
    for (let i = 0; i < 5; i++) {
      const startTime = Date.now();
      
      await dashboardPage.refreshDashboard();
      await testHelpers.waitForLoadingComplete();
      
      const updateTime = Date.now() - startTime;
      updateTimes.push(updateTime);
      
      // Each update should be under 1 second
      expect(updateTime).toBeLessThan(1000);
      
      await page.waitForTimeout(500); // Brief pause between updates
    }
    
    // Performance shouldn't degrade over time
    const firstUpdate = updateTimes[0];
    const lastUpdate = updateTimes[updateTimes.length - 1];
    
    // Last update shouldn't be more than 50% slower than first
    expect(lastUpdate).toBeLessThan(firstUpdate * 1.5);
    
    console.log('Update times:', updateTimes);
  });

  test('should handle concurrent user interactions efficiently', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    // Simulate multiple concurrent interactions
    const interactions = [
      () => dashboardPage.search('cpu'),
      () => dashboardPage.openNotifications(),
      () => dashboardPage.userMenu.click(),
      () => dashboardPage.refreshDashboard()
    ];
    
    const startTime = Date.now();
    
    // Execute interactions concurrently
    await Promise.all(interactions.map(async (interaction, index) => {
      await page.waitForTimeout(index * 100); // Stagger slightly
      return interaction();
    }));
    
    const totalTime = Date.now() - startTime;
    
    // All interactions should complete within 3 seconds
    expect(totalTime).toBeLessThan(3000);
    
    // Page should remain responsive
    await expect(dashboardPage.userMenu).toBeVisible();
  });

  test('should have efficient memory usage', async ({ page }) => {
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory ? {
        used: (performance as any).memory.usedJSHeapSize,
        total: (performance as any).memory.totalJSHeapSize,
        limit: (performance as any).memory.jsHeapSizeLimit
      } : null;
    });
    
    if (initialMemory) {
      const dashboardPage = new DashboardPage(page);
      
      // Perform memory-intensive operations
      for (let i = 0; i < 10; i++) {
        await dashboardPage.navigateToAnomalies();
        await page.goBack();
        await dashboardPage.waitForDashboardToLoad();
      }
      
      // Check memory after operations
      const finalMemory = await page.evaluate(() => {
        return {
          used: (performance as any).memory.usedJSHeapSize,
          total: (performance as any).memory.totalJSHeapSize,
          limit: (performance as any).memory.jsHeapSizeLimit
        };
      });
      
      const memoryIncrease = finalMemory.used - initialMemory.used;
      const memoryIncreasePercent = (memoryIncrease / initialMemory.used) * 100;
      
      // Memory increase should be reasonable (less than 50%)
      expect(memoryIncreasePercent).toBeLessThan(50);
      
      console.log('Memory usage:', {
        initial: initialMemory.used,
        final: finalMemory.used,
        increase: memoryIncrease,
        increasePercent: memoryIncreasePercent
      });
    }
  });

  test('should maintain performance on slow networks', async ({ page }) => {
    // Simulate slow 3G network
    await page.route('**/*', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 100)); // Add 100ms delay
      await route.continue();
    });
    
    const dashboardPage = new DashboardPage(page);
    
    const startTime = Date.now();
    await page.reload();
    await dashboardPage.waitForDashboardToLoad();
    const loadTime = Date.now() - startTime;
    
    // Should still load within reasonable time on slow network (10 seconds)
    expect(loadTime).toBeLessThan(10000);
    
    // Test navigation on slow network
    const navStartTime = Date.now();
    await dashboardPage.navigateToAnomalies();
    await testHelpers.waitForLoadingComplete();
    const navTime = Date.now() - navStartTime;
    
    // Navigation should work but may take longer
    expect(navTime).toBeLessThan(8000);
    
    // Clear the route mock
    await page.unrouteAll();
  });

  test('should handle form interactions without lag', async ({ page }) => {
    // Go to a page with forms (assuming settings page has forms)
    await page.goto('/settings');
    
    const formInputs = await page.locator('input, select, textarea').all();
    
    if (formInputs.length > 0) {
      for (const input of formInputs.slice(0, 5)) { // Test first 5 inputs
        const startTime = Date.now();
        
        // Type in input
        await input.click();
        await input.fill('test value');
        
        const interactionTime = Date.now() - startTime;
        
        // Form interaction should be instant (under 100ms)
        expect(interactionTime).toBeLessThan(100);
      }
    }
  });

  test('should efficiently handle animations and transitions', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    // Test sidebar toggle animation
    const startTime = Date.now();
    
    await dashboardPage.toggleSidebar();
    
    // Wait for animation to complete
    await page.waitForTimeout(500);
    
    const animationTime = Date.now() - startTime;
    
    // Animation should complete quickly
    expect(animationTime).toBeLessThan(1000);
    
    // Test user menu animation
    await dashboardPage.userMenu.click();
    await expect(dashboardPage.logoutButton).toBeVisible();
    
    // Menu should appear quickly
    const menuVisible = await page.locator('[data-testid="user-menu-dropdown"]').isVisible();
    expect(menuVisible).toBe(true);
  });

  test('should have fast image loading and rendering', async ({ page }) => {
    // Check for images on the page
    const images = await page.locator('img').all();
    
    if (images.length > 0) {
      for (const image of images.slice(0, 3)) { // Test first 3 images
        // Check if image loaded
        const isLoaded = await image.evaluate((img: HTMLImageElement) => {
          return img.complete && img.naturalHeight !== 0;
        });
        
        expect(isLoaded).toBe(true);
        
        // Check image is visible in viewport
        const isVisible = await testHelpers.isInViewport(image);
        if (isVisible) {
          await expect(image).toBeVisible();
        }
      }
    }
  });

  test('should maintain 60fps during interactions', async ({ page }) => {
    // This test would ideally use performance observer API
    // For now, we'll test that interactions feel smooth
    
    const dashboardPage = new DashboardPage(page);
    
    // Test smooth scrolling
    const scrollTest = async () => {
      for (let i = 0; i < 20; i++) {
        await page.mouse.wheel(0, 100);
        await page.waitForTimeout(16); // ~60fps timing
      }
    };
    
    const startTime = Date.now();
    await scrollTest();
    const scrollDuration = Date.now() - startTime;
    
    // Should complete smoothly within expected timeframe
    const expectedDuration = 20 * 16; // 20 frames at 16ms each
    expect(scrollDuration).toBeLessThan(expectedDuration * 2); // Allow some tolerance
    
    // Test hover interactions
    const widgets = await page.locator('[data-testid*="widget"]').all();
    
    for (const widget of widgets.slice(0, 3)) {
      const hoverStartTime = Date.now();
      await widget.hover();
      await page.waitForTimeout(100);
      const hoverTime = Date.now() - hoverStartTime;
      
      // Hover should be instant
      expect(hoverTime).toBeLessThan(200);
    }
  });
});
