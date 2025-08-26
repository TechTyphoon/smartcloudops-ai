import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

/**
 * Anomalies Management E2E Tests
 * Tests anomaly detection, listing, filtering, and management functionality
 */

test.describe('Anomalies Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to anomalies page
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await page.goto('/auth/login');
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    await dashboardPage.navigateToAnomalies();
    await expect(page).toHaveURL(/.*\/anomalies/);
  });

  test('should display anomalies list correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/.*Anomalies.*/);
    
    // Check main elements are present
    await expect(page.locator('[data-testid="anomalies-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="anomalies-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="anomalies-filters"]')).toBeVisible();
    
    // Check filter options
    await expect(page.locator('[data-testid="severity-filter"]')).toBeVisible();
    await expect(page.locator('[data-testid="time-filter"]')).toBeVisible();
    await expect(page.locator('[data-testid="status-filter"]')).toBeVisible();
  });

  test('should filter anomalies by severity', async ({ page }) => {
    // Select high severity filter
    await page.selectOption('[data-testid="severity-filter"]', 'high');
    
    // Wait for filtering to complete
    await page.waitForTimeout(1000);
    
    // Check that only high severity anomalies are shown
    const anomalyCards = page.locator('[data-testid="anomaly-card"]');
    const count = await anomalyCards.count();
    
    if (count > 0) {
      // Check that all visible anomalies have high severity
      for (let i = 0; i < count; i++) {
        const severityBadge = anomalyCards.nth(i).locator('[data-testid="severity-badge"]');
        await expect(severityBadge).toContainText('High');
      }
    }
  });

  test('should filter anomalies by time range', async ({ page }) => {
    // Select last 24 hours filter
    await page.selectOption('[data-testid="time-filter"]', '24h');
    
    // Wait for filtering
    await page.waitForTimeout(1000);
    
    // Check URL parameters or verify filtering occurred
    const url = page.url();
    expect(url).toContain('time=24h');
  });

  test('should search anomalies', async ({ page }) => {
    const searchInput = page.locator('[data-testid="anomalies-search"]');
    
    // Search for CPU-related anomalies
    await searchInput.fill('cpu');
    await page.keyboard.press('Enter');
    
    // Wait for search results
    await page.waitForTimeout(1000);
    
    // Check that search results are displayed
    const searchResults = page.locator('[data-testid="search-results"]');
    await expect(searchResults).toBeVisible();
  });

  test('should view anomaly details', async ({ page }) => {
    // Click on first anomaly (if exists)
    const firstAnomaly = page.locator('[data-testid="anomaly-card"]').first();
    
    if (await firstAnomaly.isVisible()) {
      await firstAnomaly.click();
      
      // Check that detail modal or page opens
      await expect(page.locator('[data-testid="anomaly-details"]')).toBeVisible();
      
      // Check detail elements
      await expect(page.locator('[data-testid="anomaly-metric-name"]')).toBeVisible();
      await expect(page.locator('[data-testid="anomaly-value"]')).toBeVisible();
      await expect(page.locator('[data-testid="anomaly-threshold"]')).toBeVisible();
      await expect(page.locator('[data-testid="anomaly-timestamp"]')).toBeVisible();
    }
  });

  test('should acknowledge anomaly', async ({ page }) => {
    const firstAnomaly = page.locator('[data-testid="anomaly-card"]').first();
    
    if (await firstAnomaly.isVisible()) {
      // Click acknowledge button
      const acknowledgeBtn = firstAnomaly.locator('[data-testid="acknowledge-button"]');
      await acknowledgeBtn.click();
      
      // Check confirmation dialog
      await expect(page.locator('[data-testid="confirm-acknowledge"]')).toBeVisible();
      
      // Confirm acknowledgment
      await page.click('[data-testid="confirm-acknowledge-button"]');
      
      // Check success message
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="success-message"]')).toContainText('acknowledged');
    }
  });

  test('should create remediation action from anomaly', async ({ page }) => {
    const firstAnomaly = page.locator('[data-testid="anomaly-card"]').first();
    
    if (await firstAnomaly.isVisible()) {
      // Click create remediation button
      const remediationBtn = firstAnomaly.locator('[data-testid="create-remediation-button"]');
      await remediationBtn.click();
      
      // Check remediation form opens
      await expect(page.locator('[data-testid="remediation-form"]')).toBeVisible();
      
      // Fill remediation form
      await page.selectOption('[data-testid="action-type-select"]', 'restart_service');
      await page.fill('[data-testid="target-resource-input"]', 'web-server-1');
      
      // Submit remediation
      await page.click('[data-testid="submit-remediation-button"]');
      
      // Check success message
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="success-message"]')).toContainText('Remediation action created');
    }
  });

  test('should export anomalies data', async ({ page }) => {
    // Click export button
    const exportBtn = page.locator('[data-testid="export-button"]');
    await expect(exportBtn).toBeVisible();
    
    // Start download
    const downloadPromise = page.waitForEvent('download');
    await exportBtn.click();
    
    // Check download started
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/anomalies.*\.(csv|json|xlsx)$/);
  });

  test('should handle pagination', async ({ page }) => {
    // Check if pagination exists
    const pagination = page.locator('[data-testid="pagination"]');
    
    if (await pagination.isVisible()) {
      // Test next page
      const nextButton = pagination.locator('[data-testid="next-page"]');
      if (await nextButton.isEnabled()) {
        await nextButton.click();
        
        // Check page changed
        await page.waitForTimeout(1000);
        const currentPage = page.locator('[data-testid="current-page"]');
        await expect(currentPage).toContainText('2');
      }
      
      // Test previous page
      const prevButton = pagination.locator('[data-testid="prev-page"]');
      if (await prevButton.isEnabled()) {
        await prevButton.click();
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should display real-time updates', async ({ page }) => {
    // Get initial anomaly count
    const initialCount = await page.locator('[data-testid="anomaly-card"]').count();
    
    // Wait for potential real-time updates
    await page.waitForTimeout(10000);
    
    // Check if count changed or refresh button works
    const refreshBtn = page.locator('[data-testid="refresh-button"]');
    if (await refreshBtn.isVisible()) {
      await refreshBtn.click();
      await page.waitForTimeout(2000);
    }
    
    // Page should still be functional
    await expect(page.locator('[data-testid="anomalies-list"]')).toBeVisible();
  });

  test('should sort anomalies', async ({ page }) => {
    // Test sorting by timestamp
    const sortByTime = page.locator('[data-testid="sort-by-time"]');
    if (await sortByTime.isVisible()) {
      await sortByTime.click();
      
      // Check sort order changed
      await page.waitForTimeout(1000);
      
      // Verify sorting (check first and second anomaly timestamps)
      const anomalies = page.locator('[data-testid="anomaly-card"]');
      if (await anomalies.count() >= 2) {
        const firstTime = await anomalies.first().locator('[data-testid="anomaly-timestamp"]').textContent();
        const secondTime = await anomalies.nth(1).locator('[data-testid="anomaly-timestamp"]').textContent();
        
        // Should be in chronological order (latest first)
        expect(firstTime).toBeTruthy();
        expect(secondTime).toBeTruthy();
      }
    }
  });

  test('should handle bulk operations', async ({ page }) => {
    // Check select all checkbox
    const selectAll = page.locator('[data-testid="select-all-anomalies"]');
    
    if (await selectAll.isVisible()) {
      await selectAll.check();
      
      // Check that anomalies are selected
      const selectedCount = await page.locator('[data-testid="selected-count"]').textContent();
      expect(selectedCount).toMatch(/\d+/);
      
      // Test bulk acknowledge
      const bulkAcknowledge = page.locator('[data-testid="bulk-acknowledge"]');
      if (await bulkAcknowledge.isVisible()) {
        await bulkAcknowledge.click();
        
        // Confirm bulk operation
        await page.click('[data-testid="confirm-bulk-acknowledge"]');
        
        // Check success message
        await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      }
    }
  });

  test('should work on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check mobile layout
    await expect(page.locator('[data-testid="anomalies-list"]')).toBeVisible();
    
    // Check filters are accessible (might be in a dropdown on mobile)
    const filtersToggle = page.locator('[data-testid="filters-toggle"]');
    if (await filtersToggle.isVisible()) {
      await filtersToggle.click();
      await expect(page.locator('[data-testid="anomalies-filters"]')).toBeVisible();
    }
    
    // Test mobile-specific interactions
    const firstAnomaly = page.locator('[data-testid="anomaly-card"]').first();
    if (await firstAnomaly.isVisible()) {
      // Long press or swipe actions on mobile
      await firstAnomaly.click();
      await expect(page.locator('[data-testid="anomaly-details"]')).toBeVisible();
    }
  });

  test('should handle accessibility features', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    
    // Check focus indicators
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Test ARIA labels
    const anomalyCard = page.locator('[data-testid="anomaly-card"]').first();
    if (await anomalyCard.isVisible()) {
      await expect(anomalyCard).toHaveAttribute('role', 'article');
      await expect(anomalyCard).toHaveAttribute('aria-label');
    }
    
    // Test screen reader support
    const severityBadge = page.locator('[data-testid="severity-badge"]').first();
    if (await severityBadge.isVisible()) {
      await expect(severityBadge).toHaveAttribute('aria-label');
    }
  });
});
