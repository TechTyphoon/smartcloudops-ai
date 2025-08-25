import { Page, Locator } from '@playwright/test';

/**
 * Login Page Object Model
 * Encapsulates login page interactions and elements
 */
export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly registerLink: Locator;
  readonly forgotPasswordLink: Locator;
  readonly rememberMeCheckbox: Locator;
  readonly loginForm: Locator;
  readonly errorMessage: Locator;
  readonly loadingSpinner: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('[data-testid="email-input"]');
    this.passwordInput = page.locator('[data-testid="password-input"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.registerLink = page.locator('[data-testid="register-link"]');
    this.forgotPasswordLink = page.locator('[data-testid="forgot-password-link"]');
    this.rememberMeCheckbox = page.locator('[data-testid="remember-me-checkbox"]');
    this.loginForm = page.locator('[data-testid="login-form"]');
    this.errorMessage = page.locator('[data-testid="login-error"]');
    this.loadingSpinner = page.locator('[data-testid="loading-spinner"]');
  }

  async login(email: string, password: string, rememberMe: boolean = false) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    
    if (rememberMe) {
      await this.rememberMeCheckbox.check();
    }
    
    await this.loginButton.click();
    
    // Wait for either success (redirect) or error
    await Promise.race([
      this.page.waitForURL('**/dashboard', { timeout: 10000 }),
      this.errorMessage.waitFor({ state: 'visible', timeout: 5000 })
    ]).catch(() => {
      // Timeout is acceptable, we'll check the result in tests
    });
  }

  async loginWithEnter(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.page.keyboard.press('Enter');
  }

  async waitForLoadingToComplete() {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 });
  }

  async getValidationErrors() {
    const errors = await this.page.locator('[data-testid*="-error"]').all();
    const errorTexts = await Promise.all(
      errors.map(error => error.textContent())
    );
    return errorTexts.filter(text => text !== null) as string[];
  }
}
