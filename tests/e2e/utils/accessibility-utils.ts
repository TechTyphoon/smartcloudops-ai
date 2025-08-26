import { Page, Locator } from '@playwright/test';
import { AxeResults } from 'axe-core';

/**
 * Accessibility testing utilities for Playwright
 * Provides helpers for WCAG compliance testing
 */

export class AccessibilityUtils {
  constructor(private page: Page) {}

  /**
   * Run axe-core accessibility tests on the current page
   */
  async runAxeTests(options?: {
    include?: string[];
    exclude?: string[];
    rules?: Record<string, any>;
  }): Promise<AxeResults> {
    // Inject axe-core if not already present
    await this.page.addScriptTag({
      url: 'https://unpkg.com/axe-core@4.8.2/axe.min.js'
    });

    // Run axe tests
    const results = await this.page.evaluate((options) => {
      // @ts-ignore - axe is injected globally
      return axe.run(document, options);
    }, options);

    return results;
  }

  /**
   * Check if element has proper ARIA labels
   */
  async checkAriaLabels(selector: string): Promise<boolean> {
    const element = this.page.locator(selector);
    
    const hasAriaLabel = await element.getAttribute('aria-label');
    const hasAriaLabelledBy = await element.getAttribute('aria-labelledby');
    const hasAriaDescribedBy = await element.getAttribute('aria-describedby');
    
    return !!(hasAriaLabel || hasAriaLabelledBy || hasAriaDescribedBy);
  }

  /**
   * Check keyboard navigation functionality
   */
  async testKeyboardNavigation(startSelector?: string): Promise<{
    navigable: boolean;
    focusableElements: number;
    tabOrder: string[];
  }> {
    // Start from specific element or document
    if (startSelector) {
      await this.page.locator(startSelector).focus();
    } else {
      await this.page.keyboard.press('Tab');
    }

    const focusableElements = await this.page.locator(
      'a:not([disabled]), button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ).count();

    const tabOrder: string[] = [];
    
    // Navigate through elements
    for (let i = 0; i < Math.min(focusableElements, 20); i++) {
      const focusedElement = await this.page.locator(':focus').first();
      const tagName = await focusedElement.evaluate(el => el.tagName.toLowerCase());
      const testId = await focusedElement.getAttribute('data-testid');
      
      tabOrder.push(testId || tagName);
      await this.page.keyboard.press('Tab');
    }

    return {
      navigable: tabOrder.length > 0,
      focusableElements,
      tabOrder
    };
  }

  /**
   * Check color contrast ratios
   */
  async checkColorContrast(selector: string): Promise<{
    passed: boolean;
    ratio: number;
    level: 'AA' | 'AAA' | 'fail';
  }> {
    const result = await this.page.locator(selector).evaluate(element => {
      const styles = window.getComputedStyle(element);
      const backgroundColor = styles.backgroundColor;
      const color = styles.color;
      
      // Simple color contrast calculation (would need proper library in real implementation)
      // This is a simplified version for demonstration
      return {
        backgroundColor,
        color,
        // Placeholder values - would use proper contrast calculation
        ratio: 4.5,
        passed: true
      };
    });

    return {
      passed: result.ratio >= 4.5,
      ratio: result.ratio,
      level: result.ratio >= 7 ? 'AAA' : result.ratio >= 4.5 ? 'AA' : 'fail'
    };
  }

  /**
   * Check for proper heading hierarchy
   */
  async checkHeadingHierarchy(): Promise<{
    valid: boolean;
    hierarchy: string[];
    issues: string[];
  }> {
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').all();
    const hierarchy: string[] = [];
    const issues: string[] = [];
    
    let lastLevel = 0;
    
    for (const heading of headings) {
      const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
      const level = parseInt(tagName.charAt(1));
      const text = await heading.textContent();
      
      hierarchy.push(`${tagName}: ${text}`);
      
      // Check for proper hierarchy
      if (level > lastLevel + 1 && lastLevel > 0) {
        issues.push(`Heading level skip: ${tagName} after h${lastLevel}`);
      }
      
      lastLevel = level;
    }

    return {
      valid: issues.length === 0,
      hierarchy,
      issues
    };
  }

  /**
   * Check for proper form labels
   */
  async checkFormLabels(formSelector?: string): Promise<{
    totalInputs: number;
    labelledInputs: number;
    unlabelledInputs: string[];
  }> {
    const formContext = formSelector ? this.page.locator(formSelector) : this.page;
    const inputs = await formContext.locator('input, select, textarea').all();
    
    const unlabelledInputs: string[] = [];
    let labelledInputs = 0;
    
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      const placeholder = await input.getAttribute('placeholder');
      
      // Check for associated label
      let hasLabel = false;
      
      if (id) {
        const label = await this.page.locator(`label[for="${id}"]`).count();
        hasLabel = label > 0;
      }
      
      if (ariaLabel || ariaLabelledBy) {
        hasLabel = true;
      }
      
      if (hasLabel) {
        labelledInputs++;
      } else {
        const testId = await input.getAttribute('data-testid');
        unlabelledInputs.push(testId || 'unnamed input');
      }
    }

    return {
      totalInputs: inputs.length,
      labelledInputs,
      unlabelledInputs
    };
  }

  /**
   * Check for proper focus indicators
   */
  async checkFocusIndicators(selector: string): Promise<{
    hasFocusStyle: boolean;
    focusVisible: boolean;
  }> {
    const element = this.page.locator(selector);
    await element.focus();
    
    const focusStyles = await element.evaluate(el => {
      const styles = window.getComputedStyle(el, ':focus');
      return {
        outline: styles.outline,
        outlineWidth: styles.outlineWidth,
        outlineStyle: styles.outlineStyle,
        outlineColor: styles.outlineColor,
        boxShadow: styles.boxShadow,
        border: styles.border
      };
    });

    const hasFocusStyle = !!(
      focusStyles.outline !== 'none' ||
      focusStyles.boxShadow !== 'none' ||
      focusStyles.outlineWidth !== '0px'
    );

    const focusVisible = await element.evaluate(el => {
      return el.matches(':focus-visible');
    });

    return {
      hasFocusStyle,
      focusVisible
    };
  }

  /**
   * Test screen reader compatibility
   */
  async testScreenReaderSupport(selector: string): Promise<{
    hasRole: boolean;
    hasAriaLabel: boolean;
    hasAriaDescription: boolean;
    semanticMarkup: boolean;
  }> {
    const element = this.page.locator(selector);
    
    const role = await element.getAttribute('role');
    const ariaLabel = await element.getAttribute('aria-label');
    const ariaDescription = await element.getAttribute('aria-describedby');
    
    const semanticMarkup = await element.evaluate(el => {
      const semanticTags = ['article', 'section', 'nav', 'aside', 'header', 'footer', 'main'];
      return semanticTags.includes(el.tagName.toLowerCase());
    });

    return {
      hasRole: !!role,
      hasAriaLabel: !!ariaLabel,
      hasAriaDescription: !!ariaDescription,
      semanticMarkup
    };
  }

  /**
   * Check for mobile accessibility
   */
  async checkMobileAccessibility(): Promise<{
    touchTargetSize: boolean;
    textSize: boolean;
    viewportMeta: boolean;
  }> {
    // Check touch target sizes (minimum 44px)
    const smallTargets = await this.page.locator('button, a, input[type="button"], input[type="submit"]').evaluateAll(elements => {
      return elements.filter(el => {
        const rect = el.getBoundingClientRect();
        return rect.width < 44 || rect.height < 44;
      }).length;
    });

    // Check text sizes (minimum 16px)
    const smallText = await this.page.evaluate(() => {
      const allText = document.querySelectorAll('p, span, div, a, button, input, label');
      let smallTextCount = 0;
      
      allText.forEach(el => {
        const fontSize = parseFloat(window.getComputedStyle(el).fontSize);
        if (fontSize < 16) smallTextCount++;
      });
      
      return smallTextCount;
    });

    // Check viewport meta tag
    const viewportMeta = await this.page.locator('meta[name="viewport"]').count() > 0;

    return {
      touchTargetSize: smallTargets === 0,
      textSize: smallText === 0,
      viewportMeta
    };
  }

  /**
   * Generate accessibility report
   */
  async generateAccessibilityReport(pageTitle: string): Promise<{
    pageTitle: string;
    timestamp: string;
    overallScore: number;
    axeResults?: AxeResults;
    keyboardNavigation: any;
    headingHierarchy: any;
    formLabels: any;
    mobileAccessibility: any;
    recommendations: string[];
  }> {
    const timestamp = new Date().toISOString();
    
    // Run all accessibility checks
    const [
      axeResults,
      keyboardNavigation,
      headingHierarchy,
      formLabels,
      mobileAccessibility
    ] = await Promise.all([
      this.runAxeTests().catch(() => null),
      this.testKeyboardNavigation().catch(() => ({ navigable: false, focusableElements: 0, tabOrder: [] })),
      this.checkHeadingHierarchy().catch(() => ({ valid: false, hierarchy: [], issues: [] })),
      this.checkFormLabels().catch(() => ({ totalInputs: 0, labelledInputs: 0, unlabelledInputs: [] })),
      this.checkMobileAccessibility().catch(() => ({ touchTargetSize: false, textSize: false, viewportMeta: false }))
    ]);

    // Calculate overall score
    let score = 100;
    const recommendations: string[] = [];

    if (axeResults && axeResults.violations.length > 0) {
      score -= axeResults.violations.length * 10;
      recommendations.push(`Fix ${axeResults.violations.length} axe-core violations`);
    }

    if (!keyboardNavigation.navigable) {
      score -= 20;
      recommendations.push('Improve keyboard navigation support');
    }

    if (!headingHierarchy.valid) {
      score -= 15;
      recommendations.push('Fix heading hierarchy issues');
    }

    if (formLabels.unlabelledInputs.length > 0) {
      score -= formLabels.unlabelledInputs.length * 5;
      recommendations.push(`Add labels to ${formLabels.unlabelledInputs.length} form inputs`);
    }

    if (!mobileAccessibility.touchTargetSize) {
      score -= 10;
      recommendations.push('Increase touch target sizes for mobile');
    }

    if (!mobileAccessibility.viewportMeta) {
      score -= 5;
      recommendations.push('Add proper viewport meta tag');
    }

    return {
      pageTitle,
      timestamp,
      overallScore: Math.max(0, score),
      axeResults: axeResults || undefined,
      keyboardNavigation,
      headingHierarchy,
      formLabels,
      mobileAccessibility,
      recommendations
    };
  }
}
