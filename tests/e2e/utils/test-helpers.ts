import { Page, Locator, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

/**
 * Common test utilities and helpers for E2E tests
 */

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Wait for element to be stable (not moving)
   */
  async waitForElementStable(locator: Locator, timeout: number = 5000): Promise<void> {
    await locator.waitFor({ state: 'visible', timeout });
    
    let previousBox = await locator.boundingBox();
    let stableCount = 0;
    const requiredStableChecks = 3;
    
    while (stableCount < requiredStableChecks) {
      await this.page.waitForTimeout(100);
      const currentBox = await locator.boundingBox();
      
      if (previousBox && currentBox && 
          previousBox.x === currentBox.x && 
          previousBox.y === currentBox.y &&
          previousBox.width === currentBox.width &&
          previousBox.height === currentBox.height) {
        stableCount++;
      } else {
        stableCount = 0;
      }
      
      previousBox = currentBox;
    }
  }

  /**
   * Take a screenshot with custom name
   */
  async takeScreenshot(name: string, fullPage: boolean = false): Promise<Buffer> {
    const screenshotPath = path.join(process.cwd(), 'screenshots', `${name}-${Date.now()}.png`);
    
    // Ensure screenshots directory exists
    const screenshotsDir = path.dirname(screenshotPath);
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
    
    return await this.page.screenshot({ 
      path: screenshotPath, 
      fullPage 
    });
  }

  /**
   * Wait for network requests to complete
   */
  async waitForNetworkIdle(timeout: number = 10000): Promise<void> {
    await this.page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Get element text content safely
   */
  async getTextContent(locator: Locator): Promise<string> {
    await locator.waitFor({ state: 'visible' });
    return await locator.textContent() || '';
  }

  /**
   * Fill input with typing simulation
   */
  async typeText(locator: Locator, text: string, delay: number = 50): Promise<void> {
    await locator.click();
    await locator.fill(''); // Clear first
    await locator.type(text, { delay });
  }

  /**
   * Wait for toast/notification message
   */
  async waitForToast(expectedText?: string, timeout: number = 5000): Promise<string> {
    const toastSelectors = [
      '[data-testid="toast"]',
      '[data-testid="notification"]',
      '[data-testid="alert"]',
      '[data-testid="success-message"]',
      '[data-testid="error-message"]',
      '.toast',
      '.notification',
      '.alert'
    ];

    for (const selector of toastSelectors) {
      try {
        const toast = this.page.locator(selector).first();
        await toast.waitFor({ state: 'visible', timeout: timeout / toastSelectors.length });
        
        const text = await toast.textContent();
        
        if (expectedText && text) {
          expect(text).toContain(expectedText);
        }
        
        return text || '';
      } catch {
        // Try next selector
        continue;
      }
    }
    
    throw new Error(`No toast message found${expectedText ? ` with text "${expectedText}"` : ''}`);
  }

  /**
   * Handle confirmation dialogs
   */
  async handleConfirmationDialog(action: 'accept' | 'dismiss' = 'accept'): Promise<void> {
    this.page.on('dialog', async dialog => {
      if (action === 'accept') {
        await dialog.accept();
      } else {
        await dialog.dismiss();
      }
    });
  }

  /**
   * Wait for loading spinner to disappear
   */
  async waitForLoadingComplete(timeout: number = 10000): Promise<void> {
    const loadingSelectors = [
      '[data-testid="loading"]',
      '[data-testid="spinner"]', 
      '[data-testid="loading-spinner"]',
      '.loading',
      '.spinner'
    ];

    for (const selector of loadingSelectors) {
      try {
        const loader = this.page.locator(selector);
        if (await loader.isVisible()) {
          await loader.waitFor({ state: 'hidden', timeout });
        }
      } catch {
        // Continue if loader not found
      }
    }
  }

  /**
   * Hover over element and wait for tooltip
   */
  async hoverAndWaitForTooltip(locator: Locator): Promise<string> {
    await locator.hover();
    
    const tooltipSelectors = [
      '[data-testid="tooltip"]',
      '[role="tooltip"]',
      '.tooltip'
    ];

    for (const selector of tooltipSelectors) {
      try {
        const tooltip = this.page.locator(selector);
        await tooltip.waitFor({ state: 'visible', timeout: 2000 });
        return await tooltip.textContent() || '';
      } catch {
        continue;
      }
    }
    
    return '';
  }

  /**
   * Scroll element into view smoothly
   */
  async scrollIntoView(locator: Locator): Promise<void> {
    await locator.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(200); // Allow scroll animation
  }

  /**
   * Get table data as array of objects
   */
  async getTableData(tableSelector: string): Promise<Array<Record<string, string>>> {
    const table = this.page.locator(tableSelector);
    await table.waitFor({ state: 'visible' });

    // Get headers
    const headers = await table.locator('thead th, tbody tr:first-child td').allTextContents();
    
    // Get rows
    const rows = await table.locator('tbody tr').all();
    const data: Array<Record<string, string>> = [];

    for (const row of rows) {
      const cells = await row.locator('td').allTextContents();
      const rowData: Record<string, string> = {};
      
      headers.forEach((header, index) => {
        rowData[header.trim()] = cells[index]?.trim() || '';
      });
      
      data.push(rowData);
    }

    return data;
  }

  /**
   * Upload file to input
   */
  async uploadFile(inputSelector: string, filePath: string): Promise<void> {
    const fileInput = this.page.locator(inputSelector);
    await fileInput.setInputFiles(filePath);
  }

  /**
   * Wait for download and return file path
   */
  async waitForDownload(triggerAction: () => Promise<void>): Promise<string> {
    const downloadPromise = this.page.waitForEvent('download');
    await triggerAction();
    const download = await downloadPromise;
    
    const filePath = path.join(process.cwd(), 'downloads', download.suggestedFilename());
    await download.saveAs(filePath);
    
    return filePath;
  }

  /**
   * Check if element is in viewport
   */
  async isInViewport(locator: Locator): Promise<boolean> {
    return await locator.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
      );
    });
  }

  /**
   * Get CSS property value
   */
  async getCSSProperty(locator: Locator, property: string): Promise<string> {
    return await locator.evaluate((element, prop) => {
      return window.getComputedStyle(element).getPropertyValue(prop);
    }, property);
  }

  /**
   * Simulate mobile swipe gesture
   */
  async swipe(startX: number, startY: number, endX: number, endY: number): Promise<void> {
    await this.page.mouse.move(startX, startY);
    await this.page.mouse.down();
    await this.page.mouse.move(endX, endY);
    await this.page.mouse.up();
  }

  /**
   * Wait for specific URL pattern
   */
  async waitForURL(pattern: string | RegExp, timeout: number = 10000): Promise<void> {
    await this.page.waitForURL(pattern, { timeout });
  }

  /**
   * Mock API response
   */
  async mockAPIResponse(url: string | RegExp, response: any, status: number = 200): Promise<void> {
    await this.page.route(url, async route => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  /**
   * Clear all mocks
   */
  async clearMocks(): Promise<void> {
    await this.page.unrouteAll();
  }

  /**
   * Get local storage value
   */
  async getLocalStorage(key: string): Promise<string | null> {
    return await this.page.evaluate((key) => {
      return localStorage.getItem(key);
    }, key);
  }

  /**
   * Set local storage value
   */
  async setLocalStorage(key: string, value: string): Promise<void> {
    await this.page.evaluate(({ key, value }) => {
      localStorage.setItem(key, value);
    }, { key, value });
  }

  /**
   * Clear all local storage
   */
  async clearLocalStorage(): Promise<void> {
    await this.page.evaluate(() => {
      localStorage.clear();
    });
  }

  /**
   * Get performance metrics
   */
  async getPerformanceMetrics(): Promise<Record<string, number>> {
    return await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
        totalLoadTime: navigation.loadEventEnd - navigation.fetchStart
      };
    });
  }
}

/**
 * Data generation utilities
 */
export class DataGenerator {
  static randomEmail(): string {
    return `test${Math.random().toString(36).substring(7)}@example.com`;
  }

  static randomString(length: number = 10): string {
    return Math.random().toString(36).substring(2, length + 2);
  }

  static randomNumber(min: number = 0, max: number = 100): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  static randomDate(start: Date = new Date(2020, 0, 1), end: Date = new Date()): Date {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  }

  static randomAnomaly() {
    const metrics = ['cpu_usage', 'memory_usage', 'disk_usage', 'network_latency'];
    const severities = ['low', 'medium', 'high', 'critical'];
    
    return {
      id: `anomaly-${this.randomString(8)}`,
      metric_name: metrics[Math.floor(Math.random() * metrics.length)],
      value: this.randomNumber(70, 100),
      threshold: this.randomNumber(60, 90),
      severity: severities[Math.floor(Math.random() * severities.length)],
      timestamp: this.randomDate().toISOString(),
      status: 'active'
    };
  }
}

/**
 * Custom assertions
 */
export class CustomAssertions {
  static async toBeVisibleAndStable(locator: Locator, page: Page): Promise<void> {
    const helpers = new TestHelpers(page);
    await expect(locator).toBeVisible();
    await helpers.waitForElementStable(locator);
  }

  static async toHaveTextContaining(locator: Locator, expectedText: string): Promise<void> {
    const text = await locator.textContent();
    expect(text).toContain(expectedText);
  }

  static async toBeAccessible(locator: Locator): Promise<void> {
    // Check basic accessibility requirements
    await expect(locator).toBeVisible();
    
    const tagName = await locator.evaluate(el => el.tagName.toLowerCase());
    
    if (['button', 'a', 'input'].includes(tagName)) {
      // Should be focusable
      await locator.focus();
      await expect(locator).toBeFocused();
    }
  }
}
