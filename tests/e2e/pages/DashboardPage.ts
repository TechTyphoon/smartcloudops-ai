import { Page, Locator } from '@playwright/test';

/**
 * Dashboard Page Object Model
 * Encapsulates dashboard page interactions and elements
 */
export class DashboardPage {
  readonly page: Page;
  readonly userMenu: Locator;
  readonly navigationMenu: Locator;
  readonly logoutButton: Locator;
  readonly searchInput: Locator;
  readonly notificationBell: Locator;
  readonly settingsLink: Locator;
  readonly profileLink: Locator;

  // Dashboard widgets
  readonly systemHealthWidget: Locator;
  readonly anomaliesWidget: Locator;
  readonly performanceWidget: Locator;
  readonly remediationWidget: Locator;
  readonly alertsWidget: Locator;

  // Navigation links
  readonly anomaliesNavLink: Locator;
  readonly remediationNavLink: Locator;
  readonly monitoringNavLink: Locator;
  readonly reportsNavLink: Locator;
  readonly settingsNavLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.userMenu = page.locator('[data-testid="user-menu"]');
    this.navigationMenu = page.locator('[data-testid="navigation-menu"]');
    this.logoutButton = page.locator('[data-testid="logout-button"]');
    this.searchInput = page.locator('[data-testid="search-input"]');
    this.notificationBell = page.locator('[data-testid="notification-bell"]');
    this.settingsLink = page.locator('[data-testid="settings-link"]');
    this.profileLink = page.locator('[data-testid="profile-link"]');

    // Dashboard widgets
    this.systemHealthWidget = page.locator('[data-testid="system-health-widget"]');
    this.anomaliesWidget = page.locator('[data-testid="anomalies-widget"]');
    this.performanceWidget = page.locator('[data-testid="performance-widget"]');
    this.remediationWidget = page.locator('[data-testid="remediation-widget"]');
    this.alertsWidget = page.locator('[data-testid="alerts-widget"]');

    // Navigation links
    this.anomaliesNavLink = page.locator('[data-testid="nav-anomalies"]');
    this.remediationNavLink = page.locator('[data-testid="nav-remediation"]');
    this.monitoringNavLink = page.locator('[data-testid="nav-monitoring"]');
    this.reportsNavLink = page.locator('[data-testid="nav-reports"]');
    this.settingsNavLink = page.locator('[data-testid="nav-settings"]');
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.waitFor({ state: 'visible' });
    await this.logoutButton.click();
  }

  async navigateToAnomalies() {
    await this.anomaliesNavLink.click();
    await this.page.waitForURL('**/anomalies');
  }

  async navigateToRemediation() {
    await this.remediationNavLink.click();
    await this.page.waitForURL('**/remediation');
  }

  async navigateToMonitoring() {
    await this.monitoringNavLink.click();
    await this.page.waitForURL('**/monitoring');
  }

  async navigateToReports() {
    await this.reportsNavLink.click();
    await this.page.waitForURL('**/reports');
  }

  async navigateToSettings() {
    await this.settingsNavLink.click();
    await this.page.waitForURL('**/settings');
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async getDashboardMetrics() {
    const metrics = {
      systemHealth: await this.getSystemHealthStatus(),
      anomaliesCount: await this.getAnomaliesCount(),
      activeRemediations: await this.getActiveRemediationsCount(),
      alertsCount: await this.getAlertsCount()
    };
    return metrics;
  }

  async getSystemHealthStatus() {
    const statusElement = this.systemHealthWidget.locator('[data-testid="health-status"]');
    return await statusElement.textContent();
  }

  async getAnomaliesCount() {
    const countElement = this.anomaliesWidget.locator('[data-testid="anomalies-count"]');
    const text = await countElement.textContent();
    return parseInt(text || '0');
  }

  async getActiveRemediationsCount() {
    const countElement = this.remediationWidget.locator('[data-testid="active-remediations-count"]');
    const text = await countElement.textContent();
    return parseInt(text || '0');
  }

  async getAlertsCount() {
    const countElement = this.alertsWidget.locator('[data-testid="alerts-count"]');
    const text = await countElement.textContent();
    return parseInt(text || '0');
  }

  async waitForDashboardToLoad() {
    await this.systemHealthWidget.waitFor({ state: 'visible' });
    await this.anomaliesWidget.waitFor({ state: 'visible' });
    await this.performanceWidget.waitFor({ state: 'visible' });
    await this.remediationWidget.waitFor({ state: 'visible' });
  }

  async refreshDashboard() {
    const refreshButton = this.page.locator('[data-testid="refresh-dashboard"]');
    await refreshButton.click();
    await this.waitForDashboardToLoad();
  }

  async toggleSidebar() {
    const sidebarToggle = this.page.locator('[data-testid="sidebar-toggle"]');
    await sidebarToggle.click();
  }

  async getNotificationCount() {
    const badge = this.notificationBell.locator('[data-testid="notification-badge"]');
    const isVisible = await badge.isVisible();
    if (!isVisible) return 0;
    
    const text = await badge.textContent();
    return parseInt(text || '0');
  }

  async openNotifications() {
    await this.notificationBell.click();
    await this.page.locator('[data-testid="notifications-dropdown"]').waitFor({ state: 'visible' });
  }

  async getRecentActivity() {
    const activityWidget = this.page.locator('[data-testid="recent-activity-widget"]');
    const activities = await activityWidget.locator('[data-testid="activity-item"]').all();
    
    const activityList = [];
    for (const activity of activities) {
      const title = await activity.locator('[data-testid="activity-title"]').textContent();
      const time = await activity.locator('[data-testid="activity-time"]').textContent();
      const type = await activity.locator('[data-testid="activity-type"]').textContent();
      
      activityList.push({ title, time, type });
    }
    
    return activityList;
  }
}
