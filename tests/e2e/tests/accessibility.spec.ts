import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { AccessibilityUtils } from '../utils/accessibility-utils';

/**
 * Accessibility E2E Tests
 * Tests WCAG compliance, keyboard navigation, screen reader support, and mobile accessibility
 */

test.describe('Accessibility Compliance', () => {
  let accessibilityUtils: AccessibilityUtils;

  test.beforeEach(async ({ page }) => {
    accessibilityUtils = new AccessibilityUtils(page);
    
    // Login and navigate to test pages
    const loginPage = new LoginPage(page);
    await page.goto('/auth/login');
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('should pass axe-core accessibility tests on dashboard', async ({ page }) => {
    const results = await accessibilityUtils.runAxeTests();
    
    // Check for violations
    expect(results.violations).toHaveLength(0);
    
    // Log any violations for debugging
    if (results.violations.length > 0) {
      console.log('Accessibility violations:', results.violations);
    }
  });

  test('should have proper keyboard navigation', async ({ page }) => {
    const navResults = await accessibilityUtils.testKeyboardNavigation();
    
    // Should be able to navigate with keyboard
    expect(navResults.navigable).toBe(true);
    expect(navResults.focusableElements).toBeGreaterThan(0);
    expect(navResults.tabOrder.length).toBeGreaterThan(0);
    
    // Check specific navigation elements
    expect(navResults.tabOrder).toContain('user-menu');
    expect(navResults.tabOrder).toContain('nav-anomalies');
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    const headingResults = await accessibilityUtils.checkHeadingHierarchy();
    
    // Should have valid heading hierarchy
    expect(headingResults.valid).toBe(true);
    expect(headingResults.issues).toHaveLength(0);
    
    // Should have at least one H1
    expect(headingResults.hierarchy.some(h => h.startsWith('h1'))).toBe(true);
  });

  test('should have proper form labels', async ({ page }) => {
    // Navigate to a page with forms (settings or profile)
    await page.goto('/settings');
    
    const formResults = await accessibilityUtils.checkFormLabels();
    
    // All form inputs should be properly labelled
    if (formResults.totalInputs > 0) {
      expect(formResults.unlabelledInputs).toHaveLength(0);
      expect(formResults.labelledInputs).toBe(formResults.totalInputs);
    }
  });

  test('should have proper focus indicators', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    // Test focus indicators on interactive elements
    const focusResults = await accessibilityUtils.checkFocusIndicators('[data-testid="user-menu"]');
    
    expect(focusResults.hasFocusStyle).toBe(true);
    
    // Test other interactive elements
    const navFocusResults = await accessibilityUtils.checkFocusIndicators('[data-testid="nav-anomalies"]');
    expect(navFocusResults.hasFocusStyle).toBe(true);
  });

  test('should support screen readers', async ({ page }) => {
    // Test main navigation
    const navSupport = await accessibilityUtils.testScreenReaderSupport('[data-testid="navigation-menu"]');
    expect(navSupport.hasRole || navSupport.semanticMarkup).toBe(true);
    
    // Test dashboard widgets
    const widgetSupport = await accessibilityUtils.testScreenReaderSupport('[data-testid="system-health-widget"]');
    expect(widgetSupport.hasAriaLabel || widgetSupport.semanticMarkup).toBe(true);
  });

  test('should be mobile accessible', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const mobileResults = await accessibilityUtils.checkMobileAccessibility();
    
    // Should have proper viewport meta tag
    expect(mobileResults.viewportMeta).toBe(true);
    
    // Touch targets should be large enough
    expect(mobileResults.touchTargetSize).toBe(true);
    
    // Text should be readable size
    expect(mobileResults.textSize).toBe(true);
  });

  test('should pass accessibility tests on login page', async ({ page }) => {
    await page.goto('/auth/login');
    
    const results = await accessibilityUtils.runAxeTests();
    expect(results.violations).toHaveLength(0);
    
    // Check form accessibility
    const formResults = await accessibilityUtils.checkFormLabels('[data-testid="login-form"]');
    expect(formResults.unlabelledInputs).toHaveLength(0);
  });

  test('should pass accessibility tests on anomalies page', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.navigateToAnomalies();
    
    const results = await accessibilityUtils.runAxeTests();
    expect(results.violations).toHaveLength(0);
    
    // Check table accessibility if present
    const tableElements = await page.locator('table').count();
    if (tableElements > 0) {
      const tableHeaders = await page.locator('th').count();
      expect(tableHeaders).toBeGreaterThan(0);
    }
  });

  test('should maintain accessibility during interactions', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    // Test accessibility after opening user menu
    await dashboardPage.userMenu.click();
    const menuResults = await accessibilityUtils.runAxeTests();
    expect(menuResults.violations).toHaveLength(0);
    
    // Test accessibility after navigation
    await dashboardPage.navigateToAnomalies();
    const navResults = await accessibilityUtils.runAxeTests();
    expect(navResults.violations).toHaveLength(0);
  });

  test('should handle high contrast mode', async ({ page }) => {
    // Simulate high contrast mode
    await page.emulateMedia({ colorScheme: 'dark' });
    
    // Check that content is still visible and accessible
    const results = await accessibilityUtils.runAxeTests();
    expect(results.violations.filter(v => v.id === 'color-contrast')).toHaveLength(0);
  });

  test('should support reduced motion preferences', async ({ page }) => {
    // Simulate reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    
    // Check that animations are disabled or reduced
    const animations = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      let animatedElements = 0;
      
      elements.forEach(el => {
        const styles = window.getComputedStyle(el);
        if (styles.animationDuration !== '0s' && styles.animationDuration !== '') {
          animatedElements++;
        }
      });
      
      return animatedElements;
    });
    
    // Should have minimal animations when reduced motion is preferred
    expect(animations).toBeLessThan(5);
  });

  test('should generate comprehensive accessibility report', async ({ page }) => {
    const report = await accessibilityUtils.generateAccessibilityReport('Dashboard');
    
    // Should have a good accessibility score
    expect(report.overallScore).toBeGreaterThan(80);
    
    // Should have valid structure
    expect(report.pageTitle).toBe('Dashboard');
    expect(report.timestamp).toBeTruthy();
    expect(Array.isArray(report.recommendations)).toBe(true);
    
    // Log report for review
    console.log('Accessibility Report:', JSON.stringify(report, null, 2));
  });

  test('should handle error states accessibly', async ({ page }) => {
    // Navigate to login page to test error states
    await page.goto('/auth/login');
    const loginPage = new LoginPage(page);
    
    // Trigger validation errors
    await loginPage.loginButton.click();
    
    // Check that error messages are accessible
    const errorElements = await page.locator('[role="alert"], [aria-live="polite"], [aria-live="assertive"]').count();
    expect(errorElements).toBeGreaterThan(0);
    
    // Check accessibility of error state
    const results = await accessibilityUtils.runAxeTests();
    expect(results.violations).toHaveLength(0);
  });

  test('should handle loading states accessibly', async ({ page }) => {
    // Navigate to a page that might show loading states
    await page.goto('/dashboard');
    
    // Check for proper loading indicators
    const loadingIndicators = await page.locator('[aria-live="polite"], [role="status"], [aria-label*="loading"], [aria-label*="Loading"]').count();
    
    // If there are loading states, they should be accessible
    if (loadingIndicators > 0) {
      const results = await accessibilityUtils.runAxeTests();
      expect(results.violations).toHaveLength(0);
    }
  });

  test('should support keyboard shortcuts', async ({ page }) => {
    // Test common keyboard shortcuts
    
    // Test Escape key (should close modals/dropdowns)
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.userMenu.click();
    await page.keyboard.press('Escape');
    
    // User menu should be closed
    await expect(dashboardPage.logoutButton).not.toBeVisible();
    
    // Test Enter key on focusable elements
    await dashboardPage.anomaliesNavLink.focus();
    await page.keyboard.press('Enter');
    
    // Should navigate to anomalies page
    await expect(page).toHaveURL(/.*\/anomalies/);
  });
});
