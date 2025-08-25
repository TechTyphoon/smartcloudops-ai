import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

/**
 * Authentication E2E Tests
 * Tests user login, logout, registration, and authentication flows
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Start from the login page
    await page.goto('/auth/login');
  });

  test('should display login form correctly', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Check page title
    await expect(page).toHaveTitle(/SmartCloudOps AI - Login/);

    // Check form elements are present
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
    await expect(loginPage.registerLink).toBeVisible();

    // Check accessibility
    await expect(loginPage.emailInput).toHaveAttribute('type', 'email');
    await expect(loginPage.passwordInput).toHaveAttribute('type', 'password');
    await expect(loginPage.emailInput).toHaveAttribute('required');
    await expect(loginPage.passwordInput).toHaveAttribute('required');
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Try to submit empty form
    await loginPage.loginButton.click();

    // Check validation messages
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Fill with invalid credentials
    await loginPage.login('invalid@example.com', 'wrongpassword');

    // Check error message
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText('Invalid credentials');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    // Login with valid credentials
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Check dashboard elements
    await expect(dashboardPage.userMenu).toBeVisible();
    await expect(dashboardPage.navigationMenu).toBeVisible();
    
    // Check user info is displayed
    await expect(page.locator('[data-testid="user-name"]')).toContainText('Test User');
  });

  test('should maintain session across page reloads', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    // Login
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Reload page
    await page.reload();

    // Should still be logged in
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(dashboardPage.userMenu).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    // Login first
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Logout
    await dashboardPage.logout();

    // Should redirect to login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
    await expect(loginPage.emailInput).toBeVisible();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Try to access dashboard without login
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/.*\/auth\/login/);
    
    // Check redirect message
    await expect(page.locator('[data-testid="redirect-message"]')).toContainText('Please log in to continue');
  });

  test('should handle password reset flow', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Click forgot password link
    await expect(loginPage.forgotPasswordLink).toBeVisible();
    await loginPage.forgotPasswordLink.click();

    // Should navigate to password reset page
    await expect(page).toHaveURL(/.*\/auth\/reset-password/);
    
    // Fill email
    await page.fill('[data-testid="reset-email-input"]', 'test@smartcloudops.ai');
    await page.click('[data-testid="reset-submit-button"]');

    // Check success message
    await expect(page.locator('[data-testid="reset-success"]')).toBeVisible();
    await expect(page.locator('[data-testid="reset-success"]')).toContainText('Password reset email sent');
  });

  test('should handle registration flow', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Navigate to registration
    await loginPage.registerLink.click();
    await expect(page).toHaveURL(/.*\/auth\/register/);

    // Fill registration form
    await page.fill('[data-testid="register-name-input"]', 'New Test User');
    await page.fill('[data-testid="register-email-input"]', 'newuser@example.com');
    await page.fill('[data-testid="register-password-input"]', 'NewPassword123!');
    await page.fill('[data-testid="register-confirm-password-input"]', 'NewPassword123!');
    
    // Accept terms
    await page.check('[data-testid="terms-checkbox"]');
    
    // Submit registration
    await page.click('[data-testid="register-button"]');

    // Check success or redirect
    await expect(page).toHaveURL(/.*\/(dashboard|auth\/verify-email)/);
  });

  test('should validate password strength', async ({ page }) => {
    await page.goto('/auth/register');

    const passwordInput = page.locator('[data-testid="register-password-input"]');
    const strengthIndicator = page.locator('[data-testid="password-strength"]');

    // Test weak password
    await passwordInput.fill('weak');
    await expect(strengthIndicator).toContainText('Weak');
    await expect(strengthIndicator).toHaveClass(/.*strength-weak.*/);

    // Test medium password
    await passwordInput.fill('Medium123');
    await expect(strengthIndicator).toContainText('Medium');
    await expect(strengthIndicator).toHaveClass(/.*strength-medium.*/);

    // Test strong password
    await passwordInput.fill('StrongPassword123!');
    await expect(strengthIndicator).toContainText('Strong');
    await expect(strengthIndicator).toHaveClass(/.*strength-strong.*/);
  });

  test('should handle rate limiting', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Make multiple failed login attempts
    for (let i = 0; i < 5; i++) {
      await loginPage.login('test@example.com', 'wrongpassword');
      await page.waitForTimeout(100);
    }

    // Should show rate limit message
    await expect(page.locator('[data-testid="rate-limit-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="rate-limit-error"]')).toContainText('Too many attempts');
  });

  test('should support keyboard navigation', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // Navigate with Tab key
    await page.keyboard.press('Tab');
    await expect(loginPage.emailInput).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(loginPage.passwordInput).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(loginPage.loginButton).toBeFocused();

    // Submit with Enter
    await loginPage.emailInput.fill('test@smartcloudops.ai');
    await loginPage.passwordInput.fill('TestPassword123!');
    await page.keyboard.press('Enter');

    // Should attempt login
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('should work on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const loginPage = new LoginPage(page);

    // Check mobile layout
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();

    // Check responsive design
    const loginForm = page.locator('[data-testid="login-form"]');
    const boundingBox = await loginForm.boundingBox();
    expect(boundingBox?.width).toBeLessThan(400);

    // Test mobile login
    await loginPage.login('test@smartcloudops.ai', 'TestPassword123!');
    await expect(page).toHaveURL(/.*\/dashboard/);
  });
});
