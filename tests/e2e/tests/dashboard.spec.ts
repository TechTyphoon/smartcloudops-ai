import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';
import { LoginPage } from '../pages/LoginPage';

/**
 * Dashboard E2E Tests
 * Tests dashboard functionality, widgets, navigation, and user interactions
 */

test.describe('Dashboard Functionality', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    // Login and navigate to dashboard
    const loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);

    await page.goto('/auth/login');
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);
    await dashboardPage.waitForDashboardToLoad();
  });

  test('should display all dashboard widgets', async ({ page }) => {
    // Check that all main widgets are visible
    await expect(dashboardPage.systemHealthWidget).toBeVisible();
    await expect(dashboardPage.anomaliesWidget).toBeVisible();
    await expect(dashboardPage.performanceWidget).toBeVisible();
    await expect(dashboardPage.remediationWidget).toBeVisible();
    await expect(dashboardPage.alertsWidget).toBeVisible();

    // Check widget titles
    await expect(dashboardPage.systemHealthWidget.locator('h3')).toContainText('System Health');
    await expect(dashboardPage.anomaliesWidget.locator('h3')).toContainText('Anomalies');
    await expect(dashboardPage.performanceWidget.locator('h3')).toContainText('Performance');
    await expect(dashboardPage.remediationWidget.locator('h3')).toContainText('Remediation');
    await expect(dashboardPage.alertsWidget.locator('h3')).toContainText('Alerts');
  });

  test('should display navigation menu correctly', async ({ page }) => {
    // Check navigation is visible
    await expect(dashboardPage.navigationMenu).toBeVisible();

    // Check all navigation links
    await expect(dashboardPage.anomaliesNavLink).toBeVisible();
    await expect(dashboardPage.remediationNavLink).toBeVisible();
    await expect(dashboardPage.monitoringNavLink).toBeVisible();
    await expect(dashboardPage.reportsNavLink).toBeVisible();
    await expect(dashboardPage.settingsNavLink).toBeVisible();

    // Check navigation link texts
    await expect(dashboardPage.anomaliesNavLink).toContainText('Anomalies');
    await expect(dashboardPage.remediationNavLink).toContainText('Remediation');
    await expect(dashboardPage.monitoringNavLink).toContainText('Monitoring');
    await expect(dashboardPage.reportsNavLink).toContainText('Reports');
    await expect(dashboardPage.settingsNavLink).toContainText('Settings');
  });

  test('should navigate to different sections', async ({ page }) => {
    // Test navigation to Anomalies
    await dashboardPage.navigateToAnomalies();
    await expect(page).toHaveURL(/.*\/anomalies/);
    await page.goBack();

    // Test navigation to Remediation
    await dashboardPage.navigateToRemediation();
    await expect(page).toHaveURL(/.*\/remediation/);
    await page.goBack();

    // Test navigation to Monitoring
    await dashboardPage.navigateToMonitoring();
    await expect(page).toHaveURL(/.*\/monitoring/);
    await page.goBack();

    // Test navigation to Reports
    await dashboardPage.navigateToReports();
    await expect(page).toHaveURL(/.*\/reports/);
    await page.goBack();

    // Test navigation to Settings
    await dashboardPage.navigateToSettings();
    await expect(page).toHaveURL(/.*\/settings/);
  });

  test('should display user menu and handle logout', async ({ page }) => {
    // Check user menu is visible
    await expect(dashboardPage.userMenu).toBeVisible();

    // Open user menu
    await dashboardPage.userMenu.click();
    await expect(dashboardPage.logoutButton).toBeVisible();
    await expect(dashboardPage.profileLink).toBeVisible();
    await expect(dashboardPage.settingsLink).toBeVisible();

    // Test logout
    await dashboardPage.logout();
    await expect(page).toHaveURL(/.*\/auth\/login/);
  });

  test('should display system metrics correctly', async ({ page }) => {
    const metrics = await dashboardPage.getDashboardMetrics();

    // Check that metrics are returned
    expect(metrics.systemHealth).toBeTruthy();
    expect(typeof metrics.anomaliesCount).toBe('number');
    expect(typeof metrics.activeRemediations).toBe('number');
    expect(typeof metrics.alertsCount).toBe('number');

    // Check reasonable values
    expect(metrics.anomaliesCount).toBeGreaterThanOrEqual(0);
    expect(metrics.activeRemediations).toBeGreaterThanOrEqual(0);
    expect(metrics.alertsCount).toBeGreaterThanOrEqual(0);
  });

  test('should handle search functionality', async ({ page }) => {
    // Test search input is visible
    await expect(dashboardPage.searchInput).toBeVisible();

    // Test search
    await dashboardPage.search('cpu anomaly');

    // Should redirect to search results or filter dashboard
    await page.waitForTimeout(1000); // Wait for search to process
    
    // Check URL contains search parameter or results are filtered
    const url = page.url();
    expect(url).toMatch(/(search|query|filter)/);
  });

  test('should handle notifications', async ({ page }) => {
    // Check notification bell is visible
    await expect(dashboardPage.notificationBell).toBeVisible();

    // Get notification count
    const notificationCount = await dashboardPage.getNotificationCount();
    expect(typeof notificationCount).toBe('number');

    // Open notifications
    await dashboardPage.openNotifications();
    
    // Check notifications dropdown is visible
    await expect(page.locator('[data-testid="notifications-dropdown"]')).toBeVisible();
  });

  test('should refresh dashboard data', async ({ page }) => {
    // Get initial metrics
    const initialMetrics = await dashboardPage.getDashboardMetrics();

    // Refresh dashboard
    await dashboardPage.refreshDashboard();

    // Verify dashboard reloaded
    await dashboardPage.waitForDashboardToLoad();

    // Get new metrics (they might be the same, but the refresh should work)
    const newMetrics = await dashboardPage.getDashboardMetrics();
    expect(typeof newMetrics.anomaliesCount).toBe('number');
  });

  test('should display recent activity', async ({ page }) => {
    const recentActivity = await dashboardPage.getRecentActivity();

    // Check that activity data is returned
    expect(Array.isArray(recentActivity)).toBe(true);

    // If there are activities, check their structure
    if (recentActivity.length > 0) {
      const firstActivity = recentActivity[0];
      expect(firstActivity).toHaveProperty('title');
      expect(firstActivity).toHaveProperty('time');
      expect(firstActivity).toHaveProperty('type');
    }
  });

  test('should work on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Check dashboard is responsive
    await expect(dashboardPage.systemHealthWidget).toBeVisible();
    
    // Test sidebar toggle on mobile
    await dashboardPage.toggleSidebar();
    
    // Navigation should be collapsible on mobile
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toHaveClass(/.*collapsed.*|.*mobile.*/);
  });

  test('should handle real-time updates', async ({ page }) => {
    // Get initial metrics
    const initialMetrics = await dashboardPage.getDashboardMetrics();

    // Wait for potential real-time updates
    await page.waitForTimeout(5000);

    // Check if any metrics have updated
    const updatedMetrics = await dashboardPage.getDashboardMetrics();
    
    // At minimum, the page should still be functional
    expect(typeof updatedMetrics.anomaliesCount).toBe('number');
    expect(typeof updatedMetrics.activeRemediations).toBe('number');
    expect(typeof updatedMetrics.alertsCount).toBe('number');
  });

  test('should handle dashboard widget interactions', async ({ page }) => {
    // Test clicking on anomalies widget
    await dashboardPage.anomaliesWidget.click();
    
    // Should either navigate or show more details
    await page.waitForTimeout(1000);
    
    // Check if modal opened or navigation occurred
    const currentUrl = page.url();
    const modalVisible = await page.locator('[data-testid="modal"]').isVisible();
    
    expect(modalVisible || currentUrl.includes('anomalies')).toBe(true);
  });

  test('should maintain state across page refresh', async ({ page }) => {
    // Get current state
    const initialUrl = page.url();
    
    // Refresh page
    await page.reload();
    
    // Should remain logged in and on dashboard
    await expect(page).toHaveURL(initialUrl);
    await dashboardPage.waitForDashboardToLoad();
    
    // Check user is still logged in
    await expect(dashboardPage.userMenu).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Test Tab navigation
    await page.keyboard.press('Tab');
    
    // Check focus moves through interactive elements
    const focusedElement = await page.locator(':focus').first();
    await expect(focusedElement).toBeVisible();

    // Test Escape key (should close any open modals/dropdowns)
    await dashboardPage.userMenu.click();
    await page.keyboard.press('Escape');
    
    // User menu dropdown should close
    await expect(dashboardPage.logoutButton).not.toBeVisible();
  });
});
